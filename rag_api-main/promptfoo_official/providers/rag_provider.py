#!/usr/bin/env python3
"""
Promptfoo Custom Provider for RAG API

This provider acts as a bridge between Promptfoo (Node.js) and the RAG API (Python).
Promptfoo will call this script, and it will forward requests to the RAG API.

The RAG API now supports LLM generation natively via the use_llm parameter.
This provider simply calls the API and returns the response.

How it works:
1. Promptfoo calls this script with a prompt as argument
2. This script makes HTTP request to RAG API with use_llm=true
3. RAG API retrieves relevant chunks AND generates focused answer via LLM
4. Returns the response to Promptfoo

Usage:
    python3 rag_provider.py "Your query here"

Environment Variables:
    RAG_API_ENDPOINT       - RAG API endpoint (default: http://localhost:8000/query)
    RAG_FILE_ID            - Document file ID to query (default: test-doc-006)
    RAG_K                  - Number of results to return (default: 4)
    USE_LLM                - Enable LLM generation in API (default: true)
"""

import sys
import json
import requests
import os
from typing import Dict, Any


class RAGProvider:
    """Custom provider for Promptfoo to query RAG API"""

    def __init__(
        self,
        endpoint: str = "http://localhost:8000/query",
        file_id: str = "test-doc-006",
        k: int = 4,
        use_llm: bool = True
    ):
        """
        Initialize RAG provider

        Args:
            endpoint: RAG API endpoint
            file_id: Document file ID to query
            k: Number of results to return
            use_llm: Whether to request LLM-generated response from API
        """
        self.endpoint = endpoint
        self.file_id = file_id
        self.k = k
        self.use_llm = use_llm

    def query(self, prompt: str) -> Dict[str, Any]:
        """
        Query the RAG API

        Args:
            prompt: User query/prompt

        Returns:
            Response from RAG API with answer and metadata
        """
        try:
            payload = {
                "query": prompt,
                "file_id": self.file_id,
                "k": self.k,
                "use_llm": self.use_llm
            }

            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=120  # Increased timeout for LLM generation
            )
            response.raise_for_status()

            data = response.json()

            # Handle new QueryResponse format (when use_llm=true)
            if isinstance(data, dict) and "answer" in data:
                return {
                    "output": data.get("answer", "No answer generated"),
                    "metadata": {
                        "sources": data.get("sources", []),
                        "llm_generated": data.get("llm_generated", False),
                        "file_id": self.file_id,
                        "k": self.k
                    }
                }

            # Handle legacy format (list of [document, score] pairs)
            # This happens when use_llm=false or API doesn't support LLM yet
            if isinstance(data, list) and len(data) > 0:
                contents = []
                sources = []
                for item in data:
                    if isinstance(item, list) and len(item) >= 1:
                        doc = item[0]
                        if isinstance(doc, dict):
                            contents.append(doc.get("page_content", ""))
                            sources.append(doc.get("metadata", {}))

                output = "\n\n".join(contents) if contents else "No results found"
                return {
                    "output": output,
                    "metadata": {
                        "sources": sources,
                        "file_id": self.file_id,
                        "k": self.k,
                        "llm_generated": False
                    }
                }

            # Fallback
            return {
                "output": str(data),
                "metadata": {"file_id": self.file_id, "k": self.k}
            }

        except requests.exceptions.RequestException as e:
            return {
                "output": f"Error querying RAG API: {str(e)}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "output": f"Unexpected error: {str(e)}",
                "error": str(e)
            }


def main():
    """
    Main entry point for Promptfoo provider

    Promptfoo will call this script with the prompt as argument
    """
    # Get configuration from environment or use defaults
    endpoint = os.getenv("RAG_API_ENDPOINT", "http://localhost:8000/query")
    file_id = os.getenv("RAG_FILE_ID", "test-doc-006")
    k = int(os.getenv("RAG_K", "4"))
    use_llm = os.getenv("USE_LLM", "true").lower() in ("true", "1", "yes")

    # Get prompt from command line argument
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No prompt provided. Usage: python3 rag_provider.py 'Your prompt here'"
        }))
        sys.exit(1)

    prompt = sys.argv[1]

    # Create provider and query
    provider = RAGProvider(endpoint=endpoint, file_id=file_id, k=k, use_llm=use_llm)
    result = provider.query(prompt)

    # Output JSON for Promptfoo to parse
    print(json.dumps(result))


if __name__ == "__main__":
    main()


def call_api(prompt: str, options: dict = None, context: dict = None) -> dict:
    """
    Promptfoo provider interface function.

    This is the function Promptfoo calls when using this as a Python provider.

    Args:
        prompt: The prompt to send to the API
        options: Provider options from config
        context: Additional context

    Returns:
        dict with 'output' key containing the response
    """
    endpoint = os.getenv("RAG_API_ENDPOINT", "http://localhost:8000/query")
    file_id = os.getenv("RAG_FILE_ID", "test-doc-006")
    k = int(os.getenv("RAG_K", "4"))
    use_llm = os.getenv("USE_LLM", "true").lower() in ("true", "1", "yes")

    provider = RAGProvider(endpoint=endpoint, file_id=file_id, k=k, use_llm=use_llm)
    return provider.query(prompt)
