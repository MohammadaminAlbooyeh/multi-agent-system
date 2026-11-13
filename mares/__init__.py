"""MARES — Multi-Agent Research & Execution System.

A production-grade multi-agent orchestration framework where specialized LLM
agents collaborate to analyze, decompose, research, execute, and synthesize
complex tasks.
"""

from dotenv import load_dotenv

# Load `.env` once, early, so every module that reads os.getenv() sees it.
# Existing environment variables always win over values from the file.
load_dotenv(override=False)

__version__ = "0.1.0"
__author__ = "Mohammadamin Albooyeh"

__all__ = [
    "__version__",
    "__author__",
]
