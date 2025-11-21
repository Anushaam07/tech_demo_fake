import asyncio
import requests
from promptfoo_integration import PromptfooConfig, RedTeamRunner
from promptfoo_integration.core.types import TargetConfig, PluginType, StrategyType

async def main():
    # Custom query function for Docker RAG API
    def query_docker_rag(prompt: str, **kwargs) -> str:
        """
        Query the RAG API running in Docker container.
        The API is accessible at localhost:8000 from host machine.
        """
        try:
            response = requests.post(
                "http://localhost:8000/query",
                json={
                    "query": prompt,
                    "file_id": "security-manual-001",
                    "k": 4
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            # Handle response
            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                if isinstance(data, list):
                    # Response is a list of documents
                    result_text = []
                    for item in data:
                        if isinstance(item, dict):
                            # Extract page_content if it exists
                            content = item.get("page_content", item.get("text", str(item)))
                            result_text.append(content)
                        else:
                            result_text.append(str(item))
                    return "\n\n".join(result_text) if result_text else "No content returned"
                elif isinstance(data, dict):
                    # Response is a dictionary
                    if "page_content" in data:
                        return data["page_content"]
                    elif "text" in data:
                        return data["text"]
                    else:
                        return str(data)
                else:
                    # Response is string or other type
                    return str(data)
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"

        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to RAG API. Is Docker running?"
        except Exception as e:
            return f"Error: {str(e)}"

    # Configure target
    target = TargetConfig(
        name="docker-rag-api",
        type="custom",
        config={
            "query_fn": query_docker_rag
        }
    )

    # Configure red team assessment
    config = PromptfooConfig(
        purpose="RAG-based document QA system running in Docker",
        target=target,
        plugins=[
            PluginType.PROMPT_INJECTION,
            PluginType.PII,
            PluginType.HARMFUL_CONTENT,
            PluginType.SQL_INJECTION,
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
        ],
        num_tests=3,  # Start small
        output_dir="./docker_red_team_results"
    )

    print("=" * 70)
    print("🔍 RED TEAM ASSESSMENT - Docker RAG API")
    print("=" * 70)
    print(f"Target: Docker container at http://localhost:8000")
    print(f"Plugins: {len(config.plugins)}")
    print(f"Strategies: {len(config.strategies)}")
    print("=" * 70)
    print()

    # Test connection first
    print("Testing connection to Docker RAG API...")
    test_response = query_docker_rag("Hello, can you help me?")

    if "Error" in test_response or "No content" in test_response:
        print(f"❌ {test_response}")
        print("\n⚠️  The document may not be uploaded yet.")
        print("\nPlease upload the document first:")
        print("  curl -X POST http://localhost:8000/embed-upload \\")
        print("    -F \"uploaded_file=@comprehensive_test_document.txt\" \\")
        print("    -F \"file_id=security-manual-001\"")
        print("\nThen run this script again.")
        return
    else:
        print("✓ Connection successful!")
        print(f"Sample response: {test_response[:100]}...")
        print()

    # Run assessment
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=2)

    # Generate reports
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)

    print("\n📊 Generating reports...")
    generator.save_report(format="html", file_path="docker_red_team_report.html")
    generator.save_report(format="json", file_path="docker_red_team_report.json")
    generator.save_report(format="text", file_path="docker_red_team_report.txt")

    print("\n" + "=" * 70)
    print("✅ ASSESSMENT COMPLETE")
    print("=" * 70)
    generator.print_summary()

    print("\n📁 Reports saved:")
    print("  🌐 HTML: docker_red_team_report.html")
    print("  📄 JSON: docker_red_team_report.json")
    print("  📝 Text: docker_red_team_report.txt")
    print("\nOpen the HTML report to see detailed results:")
    print("  open docker_red_team_report.html")  # Mac
    print("  xdg-open docker_red_team_report.html")  # Linux

if __name__ == "__main__":
    asyncio.run(main())
