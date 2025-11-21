"""
Example: Using Promptfoo Built-in Plugins with RAG Application

This example demonstrates how to use Promptfoo's official built-in plugins
alongside custom plugins to test your RAG application comprehensively.

Promptfoo built-in plugins follow official specifications from:
https://www.promptfoo.dev/docs/red-team/plugins
"""

import asyncio
import requests
from promptfoo_integration import PromptfooConfig, RedTeamRunner
from promptfoo_integration.core.types import TargetConfig, PluginType, StrategyType
from promptfoo_integration.red_team.plugins import PluginManager


def query_docker_rag(prompt: str, **kwargs) -> str:
    """
    Query function for Docker RAG API.

    Args:
        prompt: The user query/prompt
        **kwargs: Additional parameters (file_id, k, etc.)

    Returns:
        Response from RAG API
    """
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json={
                "query": prompt,
                "file_id": kwargs.get("file_id", "security-manual-001"),
                "k": kwargs.get("k", 4)
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                result_text = []
                for item in data:
                    if isinstance(item, dict):
                        content = item.get("page_content", item.get("text", str(item)))
                        result_text.append(content)
                    else:
                        result_text.append(str(item))
                return "\n\n".join(result_text) if result_text else "No content found"

            elif isinstance(data, dict):
                if "response" in data:
                    return data["response"]
                elif "answer" in data:
                    return data["answer"]
                return str(data)

            return str(data)
        else:
            return f"Error: HTTP {response.status_code}"

    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


async def example_1_builtin_pii_plugins():
    """
    Example 1: Using Promptfoo's Built-in PII Plugins

    Tests PII leakage using official Promptfoo plugins:
    - pii:direct - Direct PII requests
    - pii:api-db - Database/API PII exposure
    - pii:session - Cross-session leakage
    - pii:social - Social engineering
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Promptfoo Built-in PII Plugins")
    print("=" * 70)

    # Register Promptfoo built-in plugins
    print("\n📦 Loading Promptfoo built-in plugins...")
    success = PluginManager.register_promptfoo_builtin_plugins()
    if not success:
        print("❌ Failed to load built-in plugins")
        return

    print("✅ Loaded Promptfoo built-in plugins successfully!")
    print(f"   Total plugins available: {len(PluginManager.PLUGIN_REGISTRY)}")

    # Configure target
    target = TargetConfig(
        name="docker-rag-api-pii-test",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    # Configure test with Promptfoo built-in PII plugins
    config = PromptfooConfig(
        purpose="RAG system PII compliance testing",
        target=target,
        plugins=[
            # Promptfoo built-in PII plugins (use string names)
            "pii:direct",
            "pii:api-db",
            "pii:session",
            "pii:social",
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
        ],
        num_tests=3,  # 3 tests per plugin for quick demo
        output_dir="./builtin_pii_results"
    )

    print(f"\n🎯 Test Configuration:")
    print(f"  Target: {target.name}")
    print(f"  Plugins: {len(config.plugins)} (all Promptfoo built-in)")
    print(f"  Strategies: {len(config.strategies)}")
    print(f"  Tests per plugin: {config.num_tests}")
    print(f"  Total tests: ~{len(config.plugins) * config.num_tests}")

    # Run assessment
    print("\n🚀 Running PII security assessment...")
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    # Generate reports
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)

    print("\n📊 Generating reports...")
    generator.save_report(format="html", file_path="builtin_pii_report.html")
    generator.save_report(format="json", file_path="builtin_pii_report.json")

    print("\n" + "=" * 70)
    print("✅ PII ASSESSMENT COMPLETE")
    print("=" * 70)
    generator.print_summary()

    print("\n📁 Reports saved:")
    print("  🌐 HTML: builtin_pii_report.html")
    print("  📄 JSON: builtin_pii_report.json")


async def example_2_builtin_harmful_plugins():
    """
    Example 2: Using Promptfoo's Built-in Harmful Content Plugins

    Tests harmful content generation using official Promptfoo plugins:
    - harmful:hate - Hate speech
    - harmful:harassment-bullying - Harassment
    - harmful:violent-crime - Violence
    - harmful:privacy - Privacy violations
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Promptfoo Built-in Harmful Content Plugins")
    print("=" * 70)

    # Register built-in plugins
    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="docker-rag-api-harmful-test",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="RAG system harmful content testing",
        target=target,
        plugins=[
            # Promptfoo built-in harmful content plugins
            "harmful:hate",
            "harmful:harassment-bullying",
            "harmful:violent-crime",
            "harmful:privacy",
        ],
        strategies=[StrategyType.JAILBREAK],
        num_tests=3,
        output_dir="./builtin_harmful_results"
    )

    print(f"\n🎯 Testing harmful content generation...")
    print(f"  Plugins: {len(config.plugins)}")

    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="builtin_harmful_report.html")

    print("\n✅ Harmful content assessment complete")
    print("📁 Report: builtin_harmful_report.html")


async def example_3_builtin_security_plugins():
    """
    Example 3: Using Promptfoo's Built-in Security Plugins

    Tests security vulnerabilities using official Promptfoo plugins:
    - shell-injection - Command injection
    - debug-access - Debug mode access
    - rbac - Role-based access control
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Promptfoo Built-in Security Plugins")
    print("=" * 70)

    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="docker-rag-api-security-test",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="RAG system security testing",
        target=target,
        plugins=[
            # Promptfoo built-in security plugins
            "shell-injection",
            "debug-access",
            "rbac",
        ],
        strategies=[StrategyType.BASE64, StrategyType.ROT13],
        num_tests=3,
        output_dir="./builtin_security_results"
    )

    print(f"\n🎯 Testing security vulnerabilities...")

    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="builtin_security_report.html")

    print("\n✅ Security assessment complete")
    print("📁 Report: builtin_security_report.html")


async def example_4_mixed_custom_and_builtin():
    """
    Example 4: Mixing Custom and Built-in Plugins

    Demonstrates using both:
    - Custom plugins (SQLInjectionPlugin, PromptInjectionPlugin)
    - Built-in Promptfoo plugins (pii:direct, harmful:hate)

    This is the recommended approach for comprehensive testing.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Mixed Custom and Built-in Plugins")
    print("=" * 70)

    # Register built-in plugins
    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="docker-rag-api-comprehensive",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="Comprehensive RAG security testing",
        target=target,
        plugins=[
            # Custom plugins (use enum)
            PluginType.PROMPT_INJECTION,
            PluginType.SQL_INJECTION,
            PluginType.HALLUCINATION,

            # Promptfoo built-in plugins (use string names)
            "pii:direct",
            "harmful:hate",
            "rbac",
            "excessive-agency",
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
            StrategyType.MULTILINGUAL,
        ],
        num_tests=3,
        output_dir="./mixed_results"
    )

    print(f"\n🎯 Test Configuration:")
    print(f"  Custom plugins: 3 (PROMPT_INJECTION, SQL_INJECTION, HALLUCINATION)")
    print(f"  Built-in plugins: 4 (pii:direct, harmful:hate, rbac, excessive-agency)")
    print(f"  Total plugins: {len(config.plugins)}")
    print(f"  Strategies: {len(config.strategies)}")

    print("\n🚀 Running comprehensive assessment...")
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="mixed_comprehensive_report.html")
    generator.save_report(format="json", file_path="mixed_comprehensive_report.json")

    print("\n✅ Comprehensive assessment complete")
    generator.print_summary()

    print("\n📁 Reports saved:")
    print("  🌐 HTML: mixed_comprehensive_report.html")
    print("  📄 JSON: mixed_comprehensive_report.json")

    # Analyze results by plugin type
    custom_vulns = [r for r in results.test_results
                    if r.is_vulnerable and not r.metadata.get("promptfoo_builtin")]
    builtin_vulns = [r for r in results.test_results
                     if r.is_vulnerable and r.metadata.get("promptfoo_builtin")]

    print(f"\n🔍 Vulnerability Breakdown:")
    print(f"  Custom plugin vulnerabilities: {len(custom_vulns)}")
    print(f"  Built-in plugin vulnerabilities: {len(builtin_vulns)}")


async def example_5_all_builtin_plugins():
    """
    Example 5: Testing with ALL Promptfoo Built-in Plugins

    Comprehensive test using all 16 Promptfoo built-in plugins:

    PII (4):
    - pii:direct, pii:api-db, pii:session, pii:social

    Harmful (5):
    - harmful:hate, harmful:harassment-bullying, harmful:violent-crime,
      harmful:privacy, harmful:specialized-advice

    Security (3):
    - shell-injection, debug-access, rbac

    Brand & Trust (4):
    - competitors, contracts, excessive-agency, overreliance
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: ALL Promptfoo Built-in Plugins")
    print("=" * 70)

    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="docker-rag-api-full-builtin",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="Complete Promptfoo built-in plugin testing",
        target=target,
        plugins=[
            # All 16 Promptfoo built-in plugins
            # PII
            "pii:direct",
            "pii:api-db",
            "pii:session",
            "pii:social",
            # Harmful
            "harmful:hate",
            "harmful:harassment-bullying",
            "harmful:violent-crime",
            "harmful:privacy",
            "harmful:specialized-advice",
            # Security
            "shell-injection",
            "debug-access",
            "rbac",
            # Brand & Trust
            "competitors",
            "contracts",
            "excessive-agency",
            "overreliance",
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
            StrategyType.ROT13,
            StrategyType.MULTILINGUAL,
        ],
        num_tests=3,
        output_dir="./all_builtin_results"
    )

    print(f"\n🎯 Test Configuration:")
    print(f"  All Promptfoo built-in plugins: {len(config.plugins)}")
    print(f"  - PII plugins: 4")
    print(f"  - Harmful content plugins: 5")
    print(f"  - Security plugins: 3")
    print(f"  - Brand & Trust plugins: 4")
    print(f"  Strategies: {len(config.strategies)}")
    print(f"  Tests per plugin: {config.num_tests}")
    print(f"  Total tests: ~{len(config.plugins) * config.num_tests}")

    print("\n🚀 Running comprehensive built-in plugin assessment...")
    print("⏱️  This may take several minutes...")

    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=3)

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="all_builtin_report.html")
    generator.save_report(format="json", file_path="all_builtin_report.json")

    print("\n" + "=" * 70)
    print("✅ COMPREHENSIVE BUILT-IN ASSESSMENT COMPLETE")
    print("=" * 70)
    generator.print_summary()

    # Category breakdown
    categories = {}
    for result in results.test_results:
        if result.is_vulnerable:
            plugin = result.metadata.get("plugin", "unknown")
            category = plugin.split(":")[0] if ":" in plugin else plugin.split("-")[0]
            categories[category] = categories.get(category, 0) + 1

    print(f"\n🔍 Vulnerabilities by Category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")

    print("\n📁 Reports saved:")
    print("  🌐 HTML: all_builtin_report.html")
    print("  📄 JSON: all_builtin_report.json")


async def main():
    """Run the selected example."""
    import sys

    # Check API connectivity
    print("🔌 Checking RAG API connectivity...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ RAG API is running\n")
        else:
            print(f"⚠️  API returned status {response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot connect to RAG API: {e}")
        print("\n📋 Prerequisites:")
        print("  1. Start Docker: docker compose up -d")
        print("  2. Upload document: see run_complete_test.sh")
        return

    # Menu
    print("=" * 70)
    print("Promptfoo Built-in Plugins Examples")
    print("=" * 70)
    print("\nSelect an example to run:")
    print("  1. Built-in PII plugins only")
    print("  2. Built-in harmful content plugins only")
    print("  3. Built-in security plugins only")
    print("  4. Mixed custom + built-in plugins (recommended)")
    print("  5. ALL 16 built-in plugins (comprehensive)")
    print("  0. Run all examples sequentially")

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter your choice (0-5): ").strip()

    print()

    if choice == "1":
        await example_1_builtin_pii_plugins()
    elif choice == "2":
        await example_2_builtin_harmful_plugins()
    elif choice == "3":
        await example_3_builtin_security_plugins()
    elif choice == "4":
        await example_4_mixed_custom_and_builtin()
    elif choice == "5":
        await example_5_all_builtin_plugins()
    elif choice == "0":
        await example_1_builtin_pii_plugins()
        await example_2_builtin_harmful_plugins()
        await example_3_builtin_security_plugins()
        await example_4_mixed_custom_and_builtin()
        await example_5_all_builtin_plugins()
    else:
        print("❌ Invalid choice. Please run again with a number 0-5.")
        return

    print("\n" + "=" * 70)
    print("🎉 EXAMPLES COMPLETE!")
    print("=" * 70)
    print("\n💡 Next Steps:")
    print("  - Review HTML reports in your browser")
    print("  - Analyze JSON results programmatically")
    print("  - Fix vulnerabilities found")
    print("  - Re-run tests to verify fixes")


if __name__ == "__main__":
    asyncio.run(main())
