"""Execution Agent — generates Python code and runs it safely in a sandbox."""

from __future__ import annotations

from typing import Any, ClassVar

from mares.agents.base_agent import BaseAgent
from mares.models.execution_result import ExecutionResult
from mares.models.sub_task import SubTask
from mares.tools.python_executor_tool import PythonExecutorTool
from mares.utils.exceptions import ResearchError
from mares.utils.json_utils import safe_json_loads
from mares.utils.logger import get_logger

logger = get_logger(__name__)


EXECUTION_SYSTEM_PROMPT = """You are the MARES Execution Agent.
You receive a sub-task that requires running code. Produce JSON:
{
  "language": "python",
  "code": "print('hello world')"
}

Return ONLY the JSON. Keep code minimal, self-contained, and side-effect free
where possible.
"""


class ExecutionAgent(BaseAgent):
    """Generates code for a sub-task and runs it via the Python sandbox."""

    name: ClassVar[str] = "execution_agent"
    description: ClassVar[str] = "Generates Python code and runs it safely."

    def __init__(
        self,
        executor: PythonExecutorTool | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(system_prompt=EXECUTION_SYSTEM_PROMPT, **kwargs)
        self.executor = executor or PythonExecutorTool()

    async def run(self, input_data: SubTask) -> ExecutionResult:
        if not isinstance(input_data, SubTask):
            raise ResearchError("ExecutionAgent requires a SubTask instance.")

        self.remember("user", input_data.task)
        logger.info("execution.start", sub_task_id=input_data.id)

        raw = await self.llm_factory.generate(
            system=self.system_prompt,
            user=f"Write code that accomplishes: {input_data.task}",
        )
        self.remember("assistant", raw)

        try:
            payload = safe_json_loads(raw)
            language = payload.get("language", "python")
            code = payload.get("code", "")
        except (ValueError, TypeError) as exc:
            raise ResearchError(f"Execution agent produced invalid JSON: {exc}") from exc

        if language != "python":
            return ExecutionResult(
                sub_task_id=input_data.id,
                language=language,
                code=code,
                stdout="",
                stderr=f"Unsupported language: {language}",
                return_code=-1,
                success=False,
            )

        run_output = await self.executor.run(code=code)
        result = ExecutionResult(
            sub_task_id=input_data.id,
            language=language,
            code=code,
            stdout=run_output.get("stdout", ""),
            stderr=run_output.get("stderr", ""),
            return_code=int(run_output.get("return_code", -1)),
            success=bool(run_output.get("success", False)),
        )
        self.validate_output(result)
        logger.info(
            "execution.done",
            sub_task_id=input_data.id,
            success=result.success,
        )
        return result


__all__ = ["ExecutionAgent", "EXECUTION_SYSTEM_PROMPT"]
