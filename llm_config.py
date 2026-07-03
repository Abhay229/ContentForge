"""
ContentForge AI - LLM Configuration
-------------------------------------
Chooses a FREE LLM backend so the whole pipeline runs without any paid
API keys. Set LLM_PROVIDER in your .env to pick one:

  LLM_PROVIDER=groq        (default) -> Groq's free tier (fast, generous limits,
                                         just needs a free API key from console.groq.com)
  LLM_PROVIDER=openrouter  -> OpenRouter's free models (":free" suffix models,
                                         needs a free API key from openrouter.ai)
  LLM_PROVIDER=ollama      -> Fully local, zero API key, zero cost.
                                         Requires Ollama installed & a model pulled
                                         (e.g. `ollama pull llama3.1`)
"""

import os

from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()


def get_llm() -> LLM:
    """Return a configured, free-tier LLM instance based on LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        return LLM(
            model=os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
        )

    if provider == "openrouter":
        return LLM(
            model=os.getenv(
                "OPENROUTER_MODEL", "openrouter/meta-llama/llama-3.1-8b-instruct:free"
            ),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
        )

    if provider == "ollama":
        return LLM(
            model=os.getenv("OLLAMA_MODEL", "ollama/llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.7,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Use 'groq', 'openrouter', or 'ollama'."
    )
