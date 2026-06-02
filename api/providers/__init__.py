"""
Thin re-export shim so that code can import from either
    from providers.ai import run_ai_task
or
    from ai_providers import run_ai_task
"""
from ai_providers import AIProvider, AIProviderError, run_ai_task  # noqa: F401

__all__ = ["AIProvider", "AIProviderError", "run_ai_task"]
