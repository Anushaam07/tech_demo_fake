#!/usr/bin/env python3
"""
Async Promptfoo Custom Provider for RAG API

Advanced provider with async support for better performance when Promptfoo
runs concurrent tests.

Usage:
    python3 rag_provider_async.py "Your query here"
"""

import sys
import json
import asyncio
import aiohttp
import os
from typing import Dict, Any, List


class AsyncRAGProvider:
    """Async custom provider for Promptfoo to query RAG API"""

    def __init__(
        self,
        endpoint: str = "http://localhost:8000/query",
        file_id: str = "test-doc-006",
        k: int = 4,
        timeout: int = 30
    ):
        self.endpoint = endpoint
        self.file_id = file_id
        self.k = k
        self.timeout = timeout

    async def query(self, prompt: str) -> Dict[str, Any]:
        """
        Query the RAG API asynchronously

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

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.endpoint, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # API returns list of [document, score] pairs
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
                    else:
                        output = str(data)
                        sources = []

                    return {
                        "output": output,
                        "metadata": {
                            "sources": sources,
                            "file_id": self.file_id,
                            "k": self.k,
                            "prompt": prompt
                        }
                    }

        except aiohttp.ClientError as e:
            return {
                "output": f"Error querying RAG API: {str(e)}",
                "error": str(e)
            }
        except asyncio.TimeoutError:
            return {
                "output": f"Request timed out after {self.timeout} seconds",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "output": f"Unexpected error: {str(e)}",
                "error": str(e)
            }

    async def batch_query(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """
        Query multiple prompts concurrently

        Args:
            prompts: List of prompts to query

        Returns:
            List of responses
        """
        tasks = [self.query(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)


async def main_async():
    """Async main entry point"""
    endpoint = os.getenv("RAG_API_ENDPOINT", "http://localhost:8000/query")
    file_id = os.getenv("RAG_FILE_ID", "test-doc-006")
    k = int(os.getenv("RAG_K", "4"))
    timeout = int(os.getenv("RAG_TIMEOUT", "30"))

    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No prompt provided. Usage: python3 rag_provider_async.py 'Your prompt here'"
        }))
        sys.exit(1)

    prompt = sys.argv[1]

    provider = AsyncRAGProvider(
        endpoint=endpoint,
        file_id=file_id,
        k=k,
        timeout=timeout
    )
    result = await provider.query(prompt)

    print(json.dumps(result))


def main():
    """Sync wrapper for async main"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
