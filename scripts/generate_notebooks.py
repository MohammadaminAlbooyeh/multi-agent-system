"""Generate all 10 MARES Jupyter notebooks with executable code cells."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat as nbf

NOTEBOOKS_DIR = Path(__file__).resolve().parents[1] / "notebooks"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "source": source, "outputs": []}


def raw(source: str) -> dict:
    return {"cell_type": "raw", "metadata": {}, "source": source}


META = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11",
    },
}


def make_notebook(cells: list[dict]) -> str:
    nb = nbf.v4.new_notebook(metadata=META)
    nb.cells = [nbf.v4.new_markdown_cell(c["source"]) if c["cell_type"] == "markdown"
                else nbf.v4.new_code_cell(c["source"]) if c["cell_type"] == "code"
                else nbf.v4.new_raw_cell(c["source"])
                for c in cells]
    nb.metadata["kernelspec"] = META["kernelspec"]
    nb.metadata["language_info"] = META["language_info"]
    return nbformat_writes(nb)


def nbformat_writes(nb) -> str:
    """Minimal writes without validation to avoid schema quirks."""
    return json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": nb.metadata,
            "cells": [
                {
                    "cell_type": c.cell_type,
                    "metadata": c.metadata,
                    "source": c.source if isinstance(c.source, str) else "".join(c.source),
                }
                | ({"outputs": c.outputs, "execution_count": None} if c.cell_type == "code" else {})
                for c in nb.cells
            ],
        },
        indent=2,
        ensure_ascii=False,
    )


# =============================================================================
# 1. MARES Introduction
# =============================================================================
NOTEBOOK_1 = make_notebook([
    md("""# 1. MARES Introduction

An interactive walkthrough of the **Multi-Agent Research & Execution System**.

MARES uses 5 specialized LLM agents that collaborate via a DAG-based pipeline:
- **Planner** — decomposes a task into sub-tasks with dependencies
- **Research** — gathers information for each sub-task
- **Execution** — generates and runs Python code
- **Critic** — validates outputs and flags errors
- **Synthesizer** — combines everything into a final Markdown report

Let's explore the system. First, we import the core components."""),

    code("""# Core imports
from mares.orchestrator.orchestrator import Orchestrator
from mares.graph.dag import DAG
from mares.models.sub_task import SubTask
from mares.utils.logger import get_logger

logger = get_logger(__name__)
print("MARES imports OK — version", __import__("mares").__version__)"""),

    md("""## Pipeline Overview

The MARES pipeline works in stages:

```
USER TASK → Planner → DAG of sub-tasks → Research/Execution → Critic → Synthesizer → Final Report
```

In the next notebooks we'll explore each component in detail. For a quick demo, create an orchestrator:"""),

    code("""# Create an orchestrator (uses mock LLM config for demonstration)
orch = Orchestrator()
print(f"Orchestrator ready: Planner={orch.planner.name}, Critic={orch.critic.name}")"""),

    md("""## System Architecture

MARES is built on 4 pillars:
1. **DAG-based execution** — dependency resolution, topological sort, parallel waves
2. **Multi-LLM support** — OpenAI, Anthropic, Groq, Ollama
3. **Real tool use** — web search, Python sandbox, file I/O, HTTP APIs
4. **Self-correction** — critic-driven retry loop

Continue to Notebook 2 to learn about DAG execution."""),
])


# =============================================================================
# 2. DAG Execution
# =============================================================================
NOTEBOOK_2 = make_notebook([
    md("""# 2. DAG Execution

The **DAG** (Directed Acyclic Graph) is the backbone of MARES. It models sub-tasks as nodes and their dependencies as edges.

Key capabilities:
- Cycle detection (add_edge raises if it would create a cycle)
- Topological sort (Kahn's algorithm)
- Level grouping — independent nodes run in parallel "waves"
"""),

    code("""from mares.graph.dag import DAG

# Build a small DAG
dag = DAG()
for n in (1, 2, 3, 4, 5):
    dag.add_node(n, data=f"task-{n}")

dag.add_edge(1, 3)  # 3 depends on 1
dag.add_edge(2, 3)  # 3 depends on 2
dag.add_edge(3, 4)  # 4 depends on 3
dag.add_edge(4, 5)  # 5 depends on 4

print(f"Nodes: {dag.node_count()}, Edges: {dag.edge_count()}")
print(f"Topological order: {dag.topological_sort()}")
print(f"Levels (waves): {dag.levels()}")
# Level 0: [1, 2] — independent, run in parallel
# Level 1: [3]    — waits for 1,2
# Level 2: [4]    — waits for 3
# Level 3: [5]    — waits for 4"""),

    md("""## Cycle Detection

The DAG rejects any edge that would create a cycle:"""),

    code("""from mares.utils.exceptions import PlanningError

dag2 = DAG()
for n in (1, 2, 3):
    dag2.add_node(n)

dag2.add_edge(1, 2)
dag2.add_edge(2, 3)

try:
    dag2.add_edge(3, 1)  # Would create 1→2→3→1 cycle
    print("ERROR: cycle not detected!")
except PlanningError as e:
    print(f"Cycle correctly rejected: {e}")"""),

    md("""## Dependency Resolver

The `DependencyResolver` converts a DAG into execution waves for the parallel runner."""),

    code("""from mares.graph.dependency_resolver import DependencyResolver
from mares.models.sub_task import SubTask

# Create sub-tasks with dependencies
sub_tasks = [
    SubTask(id=1, task="Research API design", depends_on=[]),
    SubTask(id=2, task="Research database schema", depends_on=[]),
    SubTask(id=3, task="Write API code", depends_on=[1]),
    SubTask(id=4, task="Write DB code", depends_on=[2]),
    SubTask(id=5, task="Integration test", depends_on=[3, 4]),
]

# Build DAG from sub-tasks
dag3 = DAG()
for st in sub_tasks:
    dag3.add_node(st.id, data=st)
    for dep in st.depends_on:
        dag3.add_edge(dep, st.id)

resolver = DependencyResolver(dag3)
waves = resolver.execution_waves()

for i, wave in enumerate(waves):
    print(f"Wave {i}: {[st.task[:30] for st in wave]}")"""),
])


# =============================================================================
# 3. Planner Agent
# =============================================================================
NOTEBOOK_3 = make_notebook([
    md("""# 3. Planner Agent

The **PlannerAgent** receives a high-level user task and decomposes it into a DAG of sub-tasks with explicit dependencies.

It uses an LLM to produce structured JSON describing the task breakdown."""),

    code("""from unittest.mock import AsyncMock, MagicMock
import json

from mares.agents.planner_agent import PlannerAgent

# Create a mock LLM factory (no real API key needed)
mock_factory = MagicMock()
mock_factory.generate = AsyncMock()
mock_factory.generate.return_value = json.dumps({
    "tasks": [
        {"id": 1, "task": "Research Celery architecture", "depends_on": []},
        {"id": 2, "task": "Identify common failure modes", "depends_on": []},
        {"id": 3, "task": "Analyze logs for patterns", "depends_on": [1, 2]},
        {"id": 4, "task": "Propose and implement fix", "depends_on": [3]},
    ]
})

agent = PlannerAgent(llm_factory=mock_factory)
plan = await agent.run("Analyze Celery task failures in distributed systems")

print(f"Task: {plan.description}")
for st in plan.sub_tasks:
    print(f"  #{st.id}: {st.task} (depends on: {st.depends_on})")"""),

    md("""## How the Prompt Works

The planner is guided by a strict system prompt that demands:
- Valid JSON output only
- 1-indexed integer IDs
- Explicit dependency lists
- Small, independent, collectively exhaustive sub-tasks

This structure ensures the DAG executor can process the output reliably."""),

    code("""# Inspect the system prompt
print(agent.system_prompt[:300] + "...")"""),

    md("""## Error Handling

The planner raises `PlanningError` for:
- Empty input
- Invalid JSON from the LLM
- Missing required fields"""),

    code("""# Test error handling
from mares.utils.exceptions import PlanningError

# Invalid JSON
mock_factory.generate.return_value = "not valid json"
try:
    await agent.run("test")
except PlanningError as e:
    print(f"Correctly caught: {e}")

# Reset
mock_factory.generate.return_value = json.dumps({
    "tasks": [{"id": 1, "task": "Valid task", "depends_on": []}]
})"""),
])


# =============================================================================
# 4. Research Agent
# =============================================================================
NOTEBOOK_4 = make_notebook([
    md("""# 4. Research Agent

The **ResearchAgent** takes a single sub-task and produces structured findings. It has access to tools (web search, file I/O, HTTP APIs) to gather information.

Output is a `ResearchFinding` with a summary, facts list, and sources."""),

    code("""from unittest.mock import AsyncMock, MagicMock
import json

from mares.agents.research_agent import ResearchAgent
from mares.models.sub_task import SubTask

mock_factory = MagicMock()
mock_factory.generate = AsyncMock()
mock_factory.generate.return_value = json.dumps({
    "summary": "Celery uses Redis/RabbitMQ as broker. Failures often stem from connection timeouts or worker crashes.",
    "facts": [
        "Celery supports Redis, RabbitMQ, and SQS brokers",
        "Worker prefetch can cause uneven load distribution",
        "Late acknowledgement can mask failures"
    ],
    "sources": ["https://docs.celeryq.dev"]
})

agent = ResearchAgent(llm_factory=mock_factory)
subtask = SubTask(id=1, task="Research Celery architecture")

finding = await agent.run(subtask)
print(f"Summary: {finding.summary[:80]}...")
print(f"Facts ({len(finding.facts)}):")
for f in finding.facts:
    print(f"  • {f}")
print(f"Sources: {finding.sources}")"""),

    md("""## Tool Integration

The research agent has a `ToolExecutor` that can run web searches, read files, and make HTTP requests. Tools are registered centrally and dispatched by name."""),

    code("""# Show available tools
from mares.tools.tool_registry import default_registry

for tool in default_registry.describe():
    print(f"  {tool['name']}: {tool.get('description', '')[:60]}")"""),

    md("""## Research Finding Schema

Each research result includes:
- **summary** — one-paragraph synthesis
- **facts** — bullet-point list of specific findings
- **sources** — URLs or references"""),

    code("""from mares.models.research_finding import ResearchFinding

print("ResearchFinding fields:")
for name, field in ResearchFinding.model_fields.items():
    print(f"  {name}: {field.annotation}")"""),
])


# =============================================================================
# 5. Execution Agent
# =============================================================================
NOTEBOOK_5 = make_notebook([
    md("""# 5. Execution Agent

The **ExecutionAgent** generates Python code for sub-tasks that require implementation and runs it in a sandboxed subprocess.

Workflow:
1. LLM generates code based on the sub-task description
2. Code is executed in a subprocess sandbox
3. stdout, stderr, and return code are captured
4. An `ExecutionResult` is returned with success/failure status
"""),

    code("""from unittest.mock import AsyncMock, MagicMock
import json

from mares.agents.execution_agent import ExecutionAgent
from mares.models.sub_task import SubTask

mock_factory = MagicMock()
mock_factory.generate = AsyncMock()
mock_factory.generate.return_value = json.dumps({
    "language": "python",
    "code": "print(sum(range(1, 101)))"
})

agent = ExecutionAgent(llm_factory=mock_factory)
subtask = SubTask(id=1, task="Write a script to sum 1 to 100")

result = await agent.run(subtask)
print(f"Success: {result.success}")
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"Language: {result.language}")
print(f"Return code: {result.return_code}")"""),

    md("""## Execution Result Fields

The `ExecutionResult` model captures full output:"""),

    code("""from mares.models.execution_result import ExecutionResult

print("ExecutionResult fields:")
for name, field in ExecutionResult.model_fields.items():
    print(f"  {name}: {field.annotation}")"""),

    md("""## Sandbox Safety

The Python sandbox (`PythonExecutorTool`) runs code in an isolated subprocess with:
- Configurable timeout (default 10s)
- Resource limits to prevent abuse
- No access to the host filesystem beyond a temp directory"""),

    code("""from mares.tools.python_executor_tool import PythonExecutorTool

sandbox = PythonExecutorTool(timeout=5)

# Safe execution
result = await sandbox.run(code="print('hello from sandbox')")
print(f"stdout: {result.get('stdout', '')}")

# Dangerous operation is blocked by timeout
result = await sandbox.run(code="import time; time.sleep(60)")
print(f"Timed out? success={result.get('success')}, stderr={result.get('stderr', '')[:50]}")"""),
])


# =============================================================================
# 6. Critic Agent
# =============================================================================
NOTEBOOK_6 = make_notebook([
    md("""# 6. Critic Agent

The **CriticAgent** reviews outputs from Research and Execution agents. It checks for hallucinations, inconsistencies, and errors.

Output is a `CriticReport` with a pass/fail status and a list of issues per sub-task."""),

    code("""from unittest.mock import AsyncMock, MagicMock
import json

from mares.agents.critic_agent import CriticAgent
from mares.models.agent_output import AgentOutput

mock_factory = MagicMock()
mock_factory.generate = AsyncMock()
mock_factory.generate.return_value = json.dumps({
    "passed": True,
    "issues": [],
    "summary": "All outputs look correct and well-sourced."
})

agent = CriticAgent(llm_factory=mock_factory)

# Create sample outputs to review
outputs = [
    AgentOutput(
        agent="research_agent",
        sub_task_id=1,
        content={"summary": "Python asyncio is great for I/O", "facts": ["async/await syntax"]},
        metadata={"sources": ["https://docs.python.org"]}
    ),
    AgentOutput(
        agent="execution_agent",
        sub_task_id=2,
        content={"language": "python", "code": "print('ok')", "success": True},
    ),
]

report = await agent.run(outputs)
print(f"Passed: {report.passed}")
print(f"Issues: {report.issues}")
print(f"Summary: {report.summary}")"""),

    md("""## Failure Detection

When the critic finds issues, it lists them with severity levels:"""),

    code("""# Simulate a critic finding problems
mock_factory.generate.return_value = json.dumps({
    "passed": False,
    "issues": [
        {"sub_task_id": 1, "severity": "high", "description": "Claim lacks supporting source"},
        {"sub_task_id": 2, "severity": "medium", "description": "Code doesn't handle edge case"}
    ],
    "summary": "Two issues found that need correction."
})

report2 = await agent.run(outputs)
print(f"Passed: {report2.passed}")
for issue in report2.issues:
    print(f"  [{issue['severity']}] Task #{issue['sub_task_id']}: {issue['description']}")
print(f"Failed sub-tasks: {report2.failed_subtask_ids()}")"""),
])


# =============================================================================
# 7. Self-Correction Loop
# =============================================================================
NOTEBOOK_7 = make_notebook([
    md("""# 7. Self-Correction Loop

The **SelfCorrectionLoop** wraps the DAG executor and critic. If the critic rejects any outputs, the loop re-runs just the failed sub-tasks (up to `max_retries` times).

This makes the system resilient to transient LLM failures and hallucination."""),

    code("""from unittest.mock import AsyncMock, MagicMock
from mares.orchestrator.self_correction_loop import SelfCorrectionLoop
from mares.models.task import Task
from mares.models.sub_task import SubTask
from mares.models.agent_output import AgentOutput

# Mock the DAG executor and critic
mock_dag = MagicMock()
mock_critic = MagicMock()

# First call returns failed outputs, second call returns passing
call_count = [0]
async def mock_dag_run(task):
    return [
        AgentOutput(agent="research_agent", sub_task_id=1, content="ok"),
        AgentOutput(agent="execution_agent", sub_task_id=2, content="ok", metadata={"success": True}),
    ]

mock_dag.run = mock_dag_run

async def mock_critic_run(outputs):
    call_count[0] += 1
    from mares.models.critic_report import CriticReport
    if call_count[0] == 1:
        # First run fails
        return CriticReport(
            passed=False,
            issues=[{"sub_task_id": 1, "severity": "high", "description": "Missing source"}],
            summary="Retry needed"
        )
    return CriticReport(passed=True, issues=[], summary="All good")

mock_critic.run = mock_critic_run

loop = SelfCorrectionLoop(dag_executor=mock_dag, critic=mock_critic, max_retries=2)
task = Task(description="Test", sub_tasks=[
    SubTask(id=1, task="Research topic", depends_on=[]),
    SubTask(id=2, task="Write code", depends_on=[1]),
])

outputs = await loop.run(task)
print(f"Final outputs: {len(outputs)}")
print(f"Critic called {call_count[0]} times")"""),

    md("""## Retry Strategy

The self-correction loop:
1. Executes the full DAG
2. Runs the critic on all outputs
3. If failed, identifies which sub-task IDs failed
4. Re-runs only those sub-tasks (not the entire DAG)
5. Merges new results with the passing ones
6. Repeats up to `max_retries` times"""),

    code("""# Show the retry configuration
print(f"Default max_retries: {loop.max_retries}")

# Simulate exhaustion of retries
call_count2 = [0]
async def always_fail(outputs):
    call_count2[0] += 1
    from mares.models.critic_report import CriticReport
    return CriticReport(passed=False, issues=[], summary="Always fails")

mock_critic2 = MagicMock()
mock_critic2.run = always_fail

loop2 = SelfCorrectionLoop(dag_executor=mock_dag, critic=mock_critic2, max_retries=3)
outputs2 = await loop2.run(task)
print(f"Critic called {call_count2[0]} times (should be 4 = 3 retries + 1 final)")
print(f"Returns all outputs even when correction is exhausted")"""),
])


# =============================================================================
# 8. Async Parallel Execution
# =============================================================================
NOTEBOOK_8 = make_notebook([
    md("""# 8. Async Parallel Execution

MARES uses Python's `asyncio` to run independent sub-tasks concurrently. The **ParallelRunner** manages concurrency with a configurable cap.

This maximizes throughput while respecting LLM API rate limits."""),

    code("""import asyncio
import time

from mares.orchestrator.parallel_runner import ParallelRunner
from mares.models.sub_task import SubTask
from mares.models.agent_output import AgentOutput

runner = ParallelRunner(max_concurrency=3)
print(f"Max concurrency: {runner.max_concurrency}")"""),

    md("""## Simulating Parallel Work

Let's simulate sub-tasks that take varying amounts of time to see how parallel execution works:"""),

    code("""import asyncio

async def simulate_work(sub_task: SubTask) -> AgentOutput:
    delay = {1: 0.3, 2: 0.5, 3: 0.2, 4: 0.4, 5: 0.1}.get(sub_task.id, 0.2)
    await asyncio.sleep(delay)
    return AgentOutput(
        agent="research_agent",
        sub_task_id=sub_task.id,
        content={"summary": f"Result for task {sub_task.id}"}
    )

# Run a wave in parallel
sub_tasks = [
    SubTask(id=i, task=f"Task {i}", depends_on=[])
    for i in range(1, 6)
]

start = time.perf_counter()
results = await runner.run_wave(sub_tasks, simulate_work)
elapsed = time.perf_counter() - start

print(f"Ran {len(results)} tasks in parallel in {elapsed:.2f}s")
print(f"(Sequential would take ~{0.3+0.5+0.2+0.4+0.1:.1f}s)")"""),

    md("""## Gather with Concurrency

The `gather_with_concurrency` utility limits how many coroutines run at once:"""),

    code("""from mares.utils.async_utils import gather_with_concurrency

async def slow_task(n: int) -> str:
    await asyncio.sleep(0.1)
    return f"Task {n} done"

# Run 20 tasks with max 5 concurrent
start = time.perf_counter()
results = await gather_with_concurrency(5, *(slow_task(i) for i in range(20)))
elapsed = time.perf_counter() - start

print(f"20 tasks at concurrency 5: {elapsed:.2f}s (expected ~0.4s)")
print(f"Results: {len(results)}")"""),
])


# =============================================================================
# 9. Memory System
# =============================================================================
NOTEBOOK_9 = make_notebook([
    md("""# 9. Memory System

MARES has a two-tier memory system:
1. **AgentMemory** — per-agent conversation history (bounded deque)
2. **SharedMemory** — cross-agent key/value store with output indexing
3. **MemoryStore** — optional persistent backend (in-memory or Redis)
"""),

    code("""from mares.memory.agent_memory import AgentMemory

# Per-agent memory with bounded history
memory = AgentMemory(agent_name="planner_agent", capacity=100)

memory.add("user", "Analyze Celery failures")
memory.add("assistant", '{"tasks": [...]}')
memory.add("user", "Focus on Redis broker issues")
memory.add("assistant", "OK, diving deeper into Redis")

print(f"History ({len(memory)} messages):")
for msg in memory.history():
    print(f"  [{msg['role']}] {msg['content'][:60]}...")"""),

    md("""## Shared Memory

`SharedMemory` allows agents to share data during a run:"""),

    code("""from mares.memory.shared_memory import SharedMemory
from mares.models.agent_output import AgentOutput

shared = SharedMemory()

# Store outputs by sub-task ID
await shared.store_output(
    AgentOutput(agent="research_agent", sub_task_id=1, content="finding-1")
)
await shared.store_output(
    AgentOutput(agent="execution_agent", sub_task_id=2, content="code-output")
)

# Retrieve individual outputs
out1 = await shared.get_output(1)
out2 = await shared.get_output(2)
print(f"Output 1: agent={out1.agent}, content={out1.content}")
print(f"Output 2: agent={out2.agent}, content={out2.content}")

# Key/value storage
await shared.set("task_description", "Analyze Celery")
val = await shared.get("task_description")
print(f"KV store: {val}")"""),

    md("""## Persistent Storage

`MemoryStore` provides an optional Redis backend with automatic fallback to in-memory:"""),

    code("""from mares.memory.memory_store import MemoryStore

# In-memory store (default)
store = MemoryStore(backend="memory")
await store.set("key1", {"nested": "value", "count": 42})
value = await store.get("key1")
print(f"Stored value: {value}")

# Redis store (if REDIS_URL is set)
import os
redis_url = os.getenv("REDIS_URL")
if redis_url:
    redis_store = MemoryStore(backend="redis", redis_url=redis_url)
    await redis_store.set("test_key", "working")
    val = await redis_store.get("test_key")
    print(f"Redis store works: {val}")
    await redis_store.delete("test_key")
else:
    print("No REDIS_URL set — skipping Redis test")"""),
])


# =============================================================================
# 10. Full Pipeline Example
# =============================================================================
NOTEBOOK_10 = make_notebook([
    md("""# 10. Full Pipeline Example

This notebook demonstrates the complete MARES pipeline end-to-end. Since real LLM calls require API keys, we'll use mock agents to show the flow without dependencies.

In production, set `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) in your `.env` file."""),

    code("""# Check for API keys
import os

api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
if api_key and api_key != "test-key":
    print("API key found — you can run with a real LLM!")
else:
    print("No real API key set. Using mock/demo mode (no actual LLM calls).")"""),

    md("""## End-to-End with Mock Agents"""),

    code("""from unittest.mock import AsyncMock, MagicMock
import json

from mares.orchestrator.orchestrator import Orchestrator

# Create mock LLM factory
mock_factory = MagicMock()
mock_factory.generate = AsyncMock()

# Cycle through JSON responses for each agent
responses = [
    # Planner
    json.dumps({
        "tasks": [
            {"id": 1, "task": "Research task scheduling", "depends_on": []},
            {"id": 2, "task": "Analyze failure patterns", "depends_on": [1]},
            {"id": 3, "task": "Synthesize findings", "depends_on": [2]},
        ]
    }),
    # Research for task 1
    json.dumps({
        "summary": "Task scheduling in distributed systems uses queues.",
        "facts": ["Celery uses Redis/RabbitMQ"], "sources": []
    }),
    # Research for task 2
    json.dumps({
        "summary": "Failures often stem from worker crashes.",
        "facts": ["Prefetch can cause issues"], "sources": []
    }),
    # Research for task 3
    json.dumps({
        "summary": "Synthesis complete.", "facts": ["Key insight"],
        "sources": []
    }),
    # Critic
    json.dumps({
        "passed": True, "issues": [], "summary": "All outputs look good."
    }),
    # Synthesizer
    "# MARES Final Report\\n\\nAll tasks completed successfully."
]

mock_factory.generate.side_effect = responses

# Override agents with our mock
from mares.agents.planner_agent import PlannerAgent
from mares.agents.research_agent import ResearchAgent
from mares.agents.critic_agent import CriticAgent
from mares.agents.synthesizer_agent import SynthesizerAgent

# Run with mock
orch = Orchestrator(
    planner=PlannerAgent(llm_factory=mock_factory),
    research=ResearchAgent(llm_factory=mock_factory),
    critic=CriticAgent(llm_factory=mock_factory),
    synthesizer=SynthesizerAgent(llm_factory=mock_factory),
)

print("Pipeline ready. Run with: await orch.run('Your task here')")"""),

    md("""## Running Real Examples

To run with real LLMs, use the provided example scripts:"""),

    code('print("""\nExample commands:\n\n  # Basic task\n  python -m examples.run_basic_task\n\n  # Research deep-dive\n  python -m examples.run_research_task\n\n  # Data pipeline with code\n  python -m examples.run_data_pipeline_task\n\n  # Algorithm implementation\n  python -m examples.run_algorithm_task\n\n  # Celery failure analysis (canonical demo)\n  python -m examples.run_celery_analysis\n\n  # Start the API server\n  uvicorn api.main:app --reload\n""")'),

    md("""## Next Steps

1. Copy `.env.example` to `.env` and add your API keys
2. Run examples with `python -m examples.run_basic_task`
3. Start the API: `uvicorn api.main:app --reload`
4. Read the docs in the `docs/` directory
5. Explore the source code in `mares/`

Happy multi-agent orchestrating! 🚀"""),
])


# =============================================================================
# Write all notebooks
# =============================================================================
NOTEBOOKS = [
    ("1_MARES_Introduction.ipynb", NOTEBOOK_1),
    ("2_DAG_Execution.ipynb", NOTEBOOK_2),
    ("3_Planner_Agent.ipynb", NOTEBOOK_3),
    ("4_Research_Agent.ipynb", NOTEBOOK_4),
    ("5_Execution_Agent.ipynb", NOTEBOOK_5),
    ("6_Critic_Agent.ipynb", NOTEBOOK_6),
    ("7_Self_Correction_Loop.ipynb", NOTEBOOK_7),
    ("8_Async_Parallel_Execution.ipynb", NOTEBOOK_8),
    ("9_Memory_System.ipynb", NOTEBOOK_9),
    ("10_Full_Pipeline_Example.ipynb", NOTEBOOK_10),
]

if __name__ == "__main__":
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in NOTEBOOKS:
        path = NOTEBOOKS_DIR / filename
        path.write_text(content, encoding="utf-8")
        print(f"  ✓ {filename} ({len(content)} bytes)")
    print(f"\nAll {len(NOTEBOOKS)} notebooks generated in {NOTEBOOKS_DIR}")
