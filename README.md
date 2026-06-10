# MARES — Multi-Agent Research & Execution System

> A production-grade multi-agent orchestration system where specialized LLM agents collaborate to analyze, decompose, research, execute, and synthesize complex tasks — powered by async workflows, DAG-based dependency resolution, and real tool use.

## ✨ Features

- 🤖 **5 specialized agents** (Planner, Research, Execution, Critic, Synthesizer)
- 🔁 **DAG-based execution** with topological sort and parallel task scheduling
- ⚡ **Async parallel execution** with `asyncio` for independent tasks
- 🛠️ **Real tool use** (web search, Python sandbox, file I/O, HTTP APIs)
- 🧠 **Two-tier memory** (per-agent + shared cross-agent memory)
- 🔄 **Self-correction loop** with critic-driven retries
- 🌐 **FastAPI** REST + WebSocket API
- 🐳 **Docker** + docker-compose deployment
- 🧪 **40+ test cases** (unit + integration)
- 📓 **10 Jupyter notebooks** for interactive learning

## 📁 Project Structure

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a deep dive.

```
mares-multi-agent-system/
├── mares/                  # Core library
│   ├── agents/             # 5 specialized agents
│   ├── orchestrator/       # DAG execution + parallel runner
│   ├── tools/              # Tool registry + executors
│   ├── memory/             # Agent + shared memory
│   ├── graph/              # DAG + dependency resolution
│   ├── llm/                # Multi-LLM factory
│   ├── communication/      # Message queue + event bus
│   ├── evaluation/         # Hallucination + consistency checks
│   ├── models/             # Pydantic data models
│   └── utils/              # Config, logger, retry, timeout
├── api/                    # FastAPI app
├── tests/                  # Unit + integration tests
├── examples/               # Runnable examples
├── notebooks/              # 10 interactive notebooks
├── docs/                   # Project documentation
├── config/                 # App configuration
└── .github/workflows/      # CI/CD pipelines
```

## 🚀 Quickstart

```bash
# Clone
git clone https://github.com/MohammadaminAlbooyeh/mares-multi-agent-system
cd mares-multi-agent-system

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

# Run an example
python -m examples.run_celery_analysis

# Or start the API server
uvicorn api.main:app --reload
```

## 🤖 Agents

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Planner** | Break task into sub-tasks + build DAG | Main task (string) | JSON task graph |
| **Research** | Research each sub-task using tools | Sub-task | Structured findings |
| **Execution** | Generate + run Python code | Code task | Execution result |
| **Critic** | Review + validate all outputs | Agent outputs | Error report |
| **Synthesizer** | Combine all into final report | All outputs | Final report (Markdown) |

## 🔁 System Flow

```
USER INPUT
   │
   ▼
┌─────────────────────┐
│   PLANNER AGENT     │  ← Breaks task into sub-tasks
│   + DAG Builder     │  ← Builds dependency graph
└─────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│         DAG EXECUTOR               │
│  (Topological Sort + Scheduling)   │
└────────────────────────────────────┘
         │
         ▼
   Independent tasks run in PARALLEL
         │
         ▼
┌─────────────────────┐
│   CRITIC AGENT      │  ← Validate all outputs
└─────────────────────┘
         │
    ┌────┴────────────┐
  PASS ✅          FAIL ❌
    │                 │
    │         ┌───────────────────┐
    │         │ SELF-CORRECTION   │
    │         │ LOOP (re-run)     │
    │         └───────────────────┘
    ▼
┌─────────────────────┐
│ SYNTHESIZER AGENT   │  ← Final report
└─────────────────────┘
    │
    ▼
📄 FINAL REPORT
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11+ |
| **Async** | asyncio, aiohttp |
| **LLM** | OpenAI GPT-4, Claude, Groq, Ollama |
| **API** | FastAPI |
| **Graph** | Custom DAG (no external lib) |
| **Memory** | Redis + In-memory |
| **Database** | PostgreSQL |
| **Testing** | Pytest + pytest-asyncio |
| **Deployment** | Docker + docker-compose |

## 📓 Notebooks

Start with `notebooks/1_MARES_Introduction.ipynb` and walk through the 10 notebooks to learn the system end-to-end.

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Agents](docs/AGENTS.md)
- [DAG Execution](docs/DAG_EXECUTION.md)
- [Tools](docs/TOOLS.md)
- [Memory](docs/MEMORY.md)
- [Async Guide](docs/ASYNC_GUIDE.md)
- [Self-Correction](docs/SELF_CORRECTION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment](docs/DEPLOYMENT.md)

## 📜 License

See [LICENSE](LICENSE).

---

> **GitHub:** `https://github.com/MohammadaminAlbooyeh/mares-multi-agent-system`
