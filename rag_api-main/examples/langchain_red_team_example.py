"""
LangChain Red Team Example

This example demonstrates how to red team a LangChain-based RAG application.
"""

import asyncio
from promptfoo_integration import PromptfooConfig, RedTeamRunner, PromptfooClient
from promptfoo_integration.core.types import TargetConfig, PluginType, CompliancePreset


async def main():
    """Run red team assessment on LangChain application."""

    # Example: Create a simple LangChain RAG chain
    # You would replace this with your actual chain
    try:
        from langchain.chains import RetrievalQA
        from langchain_openai import ChatOpenAI
        from langchain_openai import OpenAIEmbeddings
        from langchain.vectorstores import Chroma

        # This is just an example - use your actual chain
        llm = ChatOpenAI(temperature=0)
        embeddings = OpenAIEmbeddings()

        # Assuming you have a vectorstore
        # vectorstore = Chroma(embedding_function=embeddings)
        # chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

        # For demonstration, we'll use a simple mock
        class MockChain:
            def invoke(self, inputs):
                return {"output": "This is a mock response"}

        chain = MockChain()

    except ImportError:
        print("LangChain not installed. Install with: pip install langchain langchain-openai")
        return

    # Create target configuration for LangChain
    target = TargetConfig(
        name="my-langchain-rag",
        type="langchain",
        config={
            "chain": chain,
            "invoke_method": "invoke"  # or "run", depending on your chain
        }
    )

    # Use OWASP LLM Top 10 compliance preset
    config = PromptfooConfig.with_compliance_preset(
        preset=CompliancePreset.OWASP_LLM_TOP_10,
        target=target,
        purpose="LangChain RAG application for document retrieval",
        num_tests=5
    )

    # Run assessment
    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=5)

    # Generate report
    from promptfoo_integration.red_team.report import ReportGenerator

    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="langchain_red_team_report.html")
    generator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
