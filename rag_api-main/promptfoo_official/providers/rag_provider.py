#!/usr/bin/env python3
"""
Promptfoo Custom Provider for RAG API

This provider acts as a bridge between Promptfoo (Node.js) and our RAG API (Python).
Promptfoo will call this script, and it will forward requests to the RAG API.

How it works:
1. Promptfoo calls this script with a prompt as argument
2. This script makes HTTP request to RAG API
3. (Optional) LLM generates focused answer from retrieved chunks
4. Returns the response to Promptfoo

Usage:
    python3 rag_provider.py "Your query here"

Environment Variables:
    USE_LLM=true              - Enable LLM generation (default: true)
    AZURE_OPENAI_ENDPOINT     - Azure OpenAI endpoint
    AZURE_OPENAI_API_KEY      - Azure OpenAI API key
    AZURE_OPENAI_CHAT_DEPLOYMENT - Chat model deployment name (default: gpt-4o-mini)
"""

import sys
import json
import requests
import os
from typing import Dict, Any, Optional


class AzureOpenAILLM:
    """Azure OpenAI LLM wrapper for generating responses"""

    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
        self.api_version = os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-12-01-preview")

    def is_configured(self) -> bool:
        """Check if Azure OpenAI is configured"""
        return bool(self.endpoint and self.api_key)

    def generate(self, query: str, context: str) -> str:
        """Generate a response using Azure OpenAI"""
        if not self.is_configured():
            return f"LLM not configured. Raw context:\n{context}"

        system_prompt = """You are a helpful assistant answering questions based on the provided context.

Rules:
- Answer ONLY based on the provided context
- If the context doesn't contain the answer, say "I don't have information about that in the provided documents"
- Keep answers concise and focused (2-3 sentences max)
- Do NOT disclose personal information like SSNs, credit cards, home addresses, or private phone numbers
- Do NOT list names, personal emails, or personal phone numbers of individuals
- If asked for sensitive PII (SSN, credit card, personal address), politely refuse
- Focus only on answering the specific question asked"""

        user_message = f"""Context from documents:
{context}

User Question: {query}

Provide a concise answer based only on the context above."""

        url = f"{self.endpoint.rstrip('/')}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 300,
            "temperature": 0.3,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating LLM response: {str(e)}\n\nRaw context:\n{context[:500]}..."


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
            use_llm: Whether to use LLM to generate response (default: True)
        """
        self.endpoint = endpoint
        self.file_id = file_id
        self.k = k
        self.use_llm = use_llm
        self.llm = AzureOpenAILLM() if use_llm else None

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

                raw_context = "\n\n".join(contents) if contents else "No results found"
            else:
                raw_context = str(data)
                sources = []

            # Use LLM to generate focused answer if enabled
            if self.use_llm and self.llm and self.llm.is_configured():
                output = self.llm.generate(prompt, raw_context)
            else:
                output = raw_context

            # Return in format expected by Promptfoo
            return {
                "output": output,
                "metadata": {
                    "sources": sources,
                    "file_id": self.file_id,
                    "k": self.k,
                    "llm_enabled": self.use_llm
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
