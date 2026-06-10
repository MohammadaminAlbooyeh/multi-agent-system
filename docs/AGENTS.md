# Agents

MARES has five core agents. Each is an `async` Python class inheriting from
`mares.agents.base_agent.BaseAgent`.

| Agent | File | Input | Output | Notes |
|-------|------|-------|--------|-------|
| **Planner** | `planner_agent.py` | Task string | `Task` (sub-tasks + deps) | Produces a strict-JSON DAG. |
| **Research** | `research_agent.py` | `SubTask` | `ResearchFinding` | Uses tools (search, file, api). |
| **Execution** | `execution_agent.py` | `SubTask` | `ExecutionResult` | Runs Python in a subprocess sandbox. |
| **Critic** | `critic_agent.py` | `list[AgentOutput]` | `CriticReport` | Flags hallucinations / errors. |
| **Synthesizer** | `synthesizer_agent.py` | `list[AgentOutput]` | `FinalReport` | Markdown final report. |

## Prompts

The system prompt for each agent is defined as a module-level constant:

- `PLANNER_SYSTEM_PROMPT` — instructs the model to return JSON only.
- `RESEARCH_SYSTEM_PROMPT` — structured `summary/facts/sources` output.
- `EXECUTION_SYSTEM_PROMPT` — returns `{language, code}`.
- `CRITIC_SYSTEM_PROMPT` — returns `{passed, issues, summary}`.
- `SYNTHESIZER_SYSTEM_PROMPT` — returns pure Markdown.

## Memory

Each agent owns an `AgentMemory` instance for its private conversation
history. Agents can also read from the global `SharedMemory`.
