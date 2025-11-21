"""
Guardrails Module

Runtime protection for LLM applications including:
- Input validation (prompt injection, jailbreak detection)
- Output filtering (PII, harmful content)
- Logging and monitoring
"""

from guardrails.middleware.guardrails_middleware import (
    GuardrailsMiddleware,
    GuardrailConfig,
    GuardrailResult,
    GuardrailType,
    Action,
    create_guardrails
)

__version__ = "1.0.0"

__all__ = [
    'GuardrailsMiddleware',
    'GuardrailConfig',
    'GuardrailResult',
    'GuardrailType',
    'Action',
    'create_guardrails',
]
