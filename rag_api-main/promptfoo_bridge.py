#!/usr/bin/env python3
"""
Promptfoo Python Provider Bridge for RAG API

This script acts as a bridge between Promptfoo and your RAG API.
Promptfoo will call this script with prompts, and it returns responses.

Usage:
  Promptfoo calls this automatically based on promptfooconfig.yaml

  Provider config in YAML:
    providers:
      - id: python:promptfoo_bridge.py
        config:
          api_url: "http://localhost:8000/query"
          file_id: "security-manual-001"
"""

import sys
import json
import os
import requests
from typing import Dict, Any, Optional


def call_api(
    prompt: str,
    options: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Call the RAG API with the given prompt.

    This function signature matches Promptfoo's Python provider interface:
    https://www.promptfoo.dev/docs/providers/python

    Args:
        prompt: The input text/query from Promptfoo
        options: Provider configuration from promptfooconfig.yaml
        context: Additional context from Promptfoo (test metadata, etc.)

    Returns:
        Dict with 'output' key containing the response
        or 'error' key if something went wrong
    """
    # Get configuration from options or environment
    if options is None:
        options = {}

    api_url = options.get('api_url', os.getenv('RAG_API_URL', 'http://localhost:8000/query'))
    file_id = options.get('file_id', os.getenv('RAG_FILE_ID', 'security-manual-001'))
    k = options.get('k', 4)
    timeout = options.get('timeout', 30)

    # Prepare request payload
    payload = {
        "query": prompt,
        "file_id": file_id,
        "k": k
    }

    try:
        # Call RAG API
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )

        # Handle response
        if response.status_code == 200:
            data = response.json()

            # Parse different response formats
            if isinstance(data, list):
                # List of documents
                result_text = []
                for item in data:
                    if isinstance(item, dict):
                        content = item.get("page_content", item.get("text", str(item)))
                        result_text.append(content)
                    else:
                        result_text.append(str(item))
                output = "\n\n".join(result_text) if result_text else "No content found"

            elif isinstance(data, dict):
                # Dictionary response
                if "response" in data:
                    output = data["response"]
                elif "answer" in data:
                    output = data["answer"]
                elif "page_content" in data:
                    output = data["page_content"]
                else:
                    output = json.dumps(data)
            else:
                # String or other type
                output = str(data)

            return {
                "output": output,
                "tokenUsage": {
                    "total": len(output.split()),
                    "prompt": len(prompt.split()),
                    "completion": len(output.split())
                }
            }
        else:
            # API error
            return {
                "error": f"API returned status {response.status_code}: {response.text}"
            }

    except requests.exceptions.Timeout:
        return {
            "error": f"Request timeout after {timeout}s"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "error": f"Connection error: {e}. Is the RAG API running?"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {type(e).__name__}: {e}"
        }


def main():
    """
    Main entry point for Promptfoo Python provider.

    Promptfoo communicates via stdin/stdout using JSON.
    """
    # Read input from stdin (Promptfoo sends JSON)
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    # Extract prompt and options
    prompt = input_data.get("prompt", "")
    options = input_data.get("config", {})
    context = input_data.get("context", {})

    # Call the API
    result = call_api(prompt, options, context)

    # Return result as JSON to stdout
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    # Check if running standalone for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode: demonstrate functionality
        print("🧪 Testing RAG API Bridge\n")

        test_prompt = "What is the company's security policy?"
        print(f"Test prompt: {test_prompt}\n")

        result = call_api(
            prompt=test_prompt,
            options={
                "api_url": "http://localhost:8000/query",
                "file_id": "security-manual-001",
                "k": 4
            }
        )

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success!")
            print(f"\nResponse:\n{result['output'][:500]}...")
            print(f"\nToken usage: {result.get('tokenUsage', {})}")
    else:
        # Normal mode: used by Promptfoo
        main()
