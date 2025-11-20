"""
Basic Red Team Example

This example demonstrates how to perform a basic red team assessment
on an API endpoint.
"""

import asyncio
from promptfoo_integration import PromptfooConfig, RedTeamRunner
from promptfoo_integration.core.types import TargetConfig, PluginType, StrategyType


async def main():
    """Run a basic red team assessment."""

    # Configure the target (your LLM application)
    target = TargetConfig(
        name="my-rag-api",
        type="api",
        endpoint="http://localhost:8000/v1/query",  # Update with your endpoint
        config={
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                # Add authentication headers if needed
                # "Authorization": "Bearer YOUR_TOKEN"
            },
            "prompt_key": "query",  # Key name for the prompt in request body
            "response_key": "answer",  # Key name for response in response body
        }
    )

    # Configure the red team assessment
    config = PromptfooConfig(
        purpose="A RAG-based question answering system for documentation",
        target=target,
        plugins=[
            PluginType.PROMPT_INJECTION,
            PluginType.PII,
            PluginType.HARMFUL_CONTENT,
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
        ],
        num_tests=5,  # Generate 5 tests per plugin
        output_dir="./red_team_results"
    )

    # Run the assessment
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    # Generate reports
    from promptfoo_integration.red_team.report import ReportGenerator

    generator = ReportGenerator(results)

    # Save different report formats
    generator.save_report(format="html", file_path="red_team_report.html")
    generator.save_report(format="json", file_path="red_team_report.json")
    generator.save_report(format="text", file_path="red_team_report.txt")

    # Print summary
    generator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
