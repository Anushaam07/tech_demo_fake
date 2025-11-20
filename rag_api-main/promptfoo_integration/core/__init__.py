"""
Core module for Promptfoo integration.

This module provides the fundamental building blocks for the Promptfoo integration,
including configuration management, client interfaces, and type definitions.
"""

from promptfoo_integration.core.config import PromptfooConfig
from promptfoo_integration.core.client import PromptfooClient
from promptfoo_integration.core.types import (
    PluginType,
    StrategyType,
    RedTeamResult,
    TestCase,
    CompliancePreset,
)

__all__ = [
    "PromptfooConfig",
    "PromptfooClient",
    "PluginType",
    "StrategyType",
    "RedTeamResult",
    "TestCase",
    "CompliancePreset",
]
