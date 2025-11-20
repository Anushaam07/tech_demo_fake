"""
Red Team module for LLM security testing.

This module provides comprehensive red teaming capabilities including:
- Plugin-based adversarial test generation
- Multiple attack strategies
- Test execution and grading
- Results reporting and analysis
"""

from promptfoo_integration.red_team.plugins import PluginManager
from promptfoo_integration.red_team.strategies import StrategyManager
from promptfoo_integration.red_team.runner import RedTeamRunner
from promptfoo_integration.red_team.report import ReportGenerator

__all__ = [
    "PluginManager",
    "StrategyManager",
    "RedTeamRunner",
    "ReportGenerator",
]
