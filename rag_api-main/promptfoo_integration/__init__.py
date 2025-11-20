"""
Promptfoo Integration Module

A modular integration of Promptfoo's features for LLM security testing and evaluation.
This package provides a flexible, extensible framework for integrating Promptfoo's
red teaming, guardrails, and evaluation capabilities with any LLM application.

Current Features:
- Red Teaming: Comprehensive security testing with plugins and strategies

Future Features:
- Guardrails: Content filtering and safety controls
- Model Security: Advanced security testing
- Evaluations: Performance and quality assessments
"""

__version__ = "1.0.0"
__author__ = "RAG API Team"

from promptfoo_integration.core.client import PromptfooClient
from promptfoo_integration.core.config import PromptfooConfig
from promptfoo_integration.red_team.runner import RedTeamRunner

__all__ = [
    "PromptfooClient",
    "PromptfooConfig",
    "RedTeamRunner",
]
