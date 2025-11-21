#!/usr/bin/env python3
"""
Promptfoo Custom Provider for RAG API

This provider acts as a bridge between Promptfoo (Node.js) and our RAG API (Python).
Promptfoo will call this script, and it will forward requests to the RAG API.

How it works:
1. Promptfoo calls this script with a prompt as argument
2. This script makes HTTP request to RAG API
3. Returns the response to Promptfoo

Usage:
    python3 rag_provider.py "Your query here"
"""

import sys
import json
import requests
import os
from typing import Dict, Any, Optional


class RAGProvider:
    """Custom provider for Promptfoo to query RAG API"""

    def __init__(
        self,
        endpoint: str = "http://localhost:8000/query",
        file_id: str = "test-doc-006",
        k: int = 4
    ):
        """
        Initialize RAG provider

        Args:
            endpoint: RAG API endpoint
            file_id: Document file ID to query
            k: Number of results to return
        """
        self.endpoint = endpoint
        self.file_id = file_id
        self.k = k

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
                "k": self.k
            }

            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # API returns list of [document, score] pairs
            # Extract page_content from results
            if isinstance(data, list) and len(data) > 0:
                # Combine all page_content from results
                contents = []
                sources = []
                for item in data:
                    if isinstance(item, list) and len(item) >= 1:
                        doc = item[0]
                        if isinstance(doc, dict):
                            contents.append(doc.get("page_content", ""))
                            sources.append(doc.get("metadata", {}))

                output = "\n\n".join(contents) if contents else "No results found"
            else:
                output = str(data)
                sources = []

            # Return in format expected by Promptfoo
            return {
                "output": output,
                "metadata": {
                    "sources": sources,
                    "file_id": self.file_id,
                    "k": self.k
                }
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

    # Get prompt from command line argument
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No prompt provided. Usage: python3 rag_provider.py 'Your prompt here'"
        }))
        sys.exit(1)

    prompt = sys.argv[1]

    # Create provider and query
    provider = RAGProvider(endpoint=endpoint, file_id=file_id, k=k)
    result = provider.query(prompt)

    # Output JSON for Promptfoo to parse
    print(json.dumps(result))


if __name__ == "__main__":
    main()


def call_api(prompt: str, options: dict = None, context: dict = None) -> dict:
    """
    Promptfoo provider interface function.

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

    provider = RAGProvider(endpoint=endpoint, file_id=file_id, k=k)
    return provider.query(prompt)
