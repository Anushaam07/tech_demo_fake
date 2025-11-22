#!/usr/bin/env python3
"""
LLM Wrapper for Azure OpenAI

Provides LLM generation capabilities for RAG responses.
"""

import os
import requests
from typing import Optional


class AzureOpenAILLM:
    """Azure OpenAI LLM wrapper for generating responses"""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-12-01-preview")

        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set")

    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using Azure OpenAI.

        Args:
            query: User's question
            context: Retrieved context from RAG
            system_prompt: Custom system prompt (optional)
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)

        Returns:
            Generated response string
        """
        if not system_prompt:
            system_prompt = """You are a helpful assistant answering questions based on the provided context.

Rules:
- Answer ONLY based on the provided context
- If the context doesn't contain the answer, say "I don't have information about that"
- Keep answers concise and focused
- Do NOT disclose personal information like SSNs, credit cards, or private data
- Do NOT list names, emails, or phone numbers of individuals
- If asked for sensitive PII, politely refuse"""

        # Build the prompt
        user_message = f"""Context:
{context}

Question: {query}

Answer the question based only on the context above. Be concise and focused."""

        # Azure OpenAI API URL
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
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            return f"Error generating response: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Error parsing response: {str(e)}"


def generate_rag_response(query: str, context: str) -> str:
    """
    Convenience function to generate RAG response.

    Args:
        query: User's question
        context: Retrieved document chunks

    Returns:
        Generated response
    """
    llm = AzureOpenAILLM()
    return llm.generate(query, context)
