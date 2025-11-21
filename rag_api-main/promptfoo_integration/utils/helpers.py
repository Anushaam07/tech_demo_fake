"""
Helper utilities for the Promptfoo integration.
"""

from typing import Any, Dict


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_test_output(output: str, max_lines: int = 5) -> str:
    """
    Format test output for display.

    Args:
        output: Raw output text
        max_lines: Maximum number of lines to display

    Returns:
        Formatted output
    """
    lines = output.split('\n')
    if len(lines) <= max_lines:
        return output

    return '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"


def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage safely.

    Args:
        part: Part value
        total: Total value

    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (part / total) * 100
