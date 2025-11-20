"""
Custom Target Example

This example demonstrates how to red team a custom LLM application
using custom query functions.
"""

import asyncio
from promptfoo_integration import PromptfooConfig, RedTeamRunner
from promptfoo_integration.core.types import TargetConfig, PluginType
from promptfoo_integration.core.client import CustomTargetClient


# Define your custom query function
def my_custom_query(prompt: str, **kwargs) -> str:
    """
    Custom function to query your LLM application.

    Replace this with your actual application logic.
    """
    # Example: Call your custom LLM service
    # response = my_llm_service.query(prompt)

    # For demonstration:
    return f"Response to: {prompt}"


# You can also define an async version
async def my_custom_async_query(prompt: str, **kwargs) -> str:
    """Async version of custom query."""
    # Example async call
    await asyncio.sleep(0.1)  # Simulate async operation
    return f"Async response to: {prompt}"


async def main():
    """Run red team assessment with custom target."""

    # Create target configuration with custom functions
    target = TargetConfig(
        name="my-custom-llm",
        type="custom",
        config={
            "query_fn": my_custom_query,
            "async_query_fn": my_custom_async_query
        }
    )

    # Configure assessment
    config = PromptfooConfig(
        purpose="Custom LLM application",
        target=target,
        plugins=[
            PluginType.PROMPT_INJECTION,
            PluginType.SQL_INJECTION,
            PluginType.HARMFUL_CONTENT,
            PluginType.HALLUCINATION,
        ],
        num_tests=3,
        output_dir="./custom_red_team_results"
    )

    # Run assessment
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=5)

    # Generate reports
    from promptfoo_integration.red_team.report import ReportGenerator

    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="custom_red_team_report.html")
    generator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
