"""
LLM Service for RAG Application

Provides LLM generation capabilities to transform raw document chunks
into focused, intelligent responses.

Supports:
- Azure OpenAI
- OpenAI (direct)
- Configurable via environment variables
"""

import os
import logging
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM service"""
    provider: str = "azure"  # azure, openai
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    deployment: str = "gpt-4o-mini"
    api_version: str = "2024-12-01-preview"
    max_tokens: int = 500
    temperature: float = 0.3


class LLMService:
    """
    LLM Service for generating intelligent responses from RAG context.

    This service takes retrieved document chunks and a user query,
    then generates a focused answer using an LLM.
    """

    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant answering questions based on the provided context.

Rules:
- Answer ONLY based on the provided context
- If the context doesn't contain the answer, say "I don't have information about that in the provided documents"
- Keep answers concise and focused (2-3 sentences max)
- Do NOT disclose personal information like SSNs, credit cards, home addresses, or private phone numbers
- Do NOT list names, personal emails, or personal phone numbers of individuals
- If asked for sensitive PII (SSN, credit card, personal address), politely refuse
- Focus only on answering the specific question asked"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM Service.

        Args:
            config: LLM configuration. If None, reads from environment.
        """
        if config:
            self.config = config
        else:
            self.config = self._load_config_from_env()

        self._validate_config()

    def _load_config_from_env(self) -> LLMConfig:
        """Load configuration from environment variables"""
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "azure"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("RAG_AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("RAG_AZURE_OPENAI_API_KEY"),
            deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
            api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-12-01-preview"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
        )

    def _validate_config(self):
        """Validate LLM configuration"""
        if not self.config.endpoint or not self.config.api_key:
            logger.warning(
                "LLM Service: Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. "
                "LLM generation will be disabled."
            )

    def is_configured(self) -> bool:
        """Check if LLM service is properly configured"""
        return bool(self.config.endpoint and self.config.api_key)

    def generate(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a response using the LLM.

        Args:
            query: User's question
            context: Retrieved context from RAG (document chunks)
            system_prompt: Custom system prompt (uses default if None)
            max_tokens: Override max tokens
            temperature: Override temperature

        Returns:
            Generated response string
        """
        if not self.is_configured():
            logger.warning("LLM not configured, returning raw context")
            return context

        if system_prompt is None:
            system_prompt = self.DEFAULT_SYSTEM_PROMPT

        user_message = f"""Context from documents:
{context}

User Question: {query}

Provide a concise answer based only on the context above."""

        # Azure OpenAI API URL
        url = (
            f"{self.config.endpoint.rstrip('/')}/openai/deployments/"
            f"{self.config.deployment}/chat/completions?api-version={self.config.api_version}"
        )

        headers = {
            "Content-Type": "application/json",
            "api-key": self.config.api_key,
        }

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            generated_text = data["choices"][0]["message"]["content"]

            logger.debug(f"LLM generated response for query: {query[:50]}...")
            return generated_text

        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            return f"Request timed out. Raw context:\n{context[:500]}..."
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {str(e)}")
            return f"Error generating response: {str(e)}\n\nRaw context:\n{context[:500]}..."
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return f"Error parsing response: {str(e)}\n\nRaw context:\n{context[:500]}..."

    def generate_from_documents(
        self,
        query: str,
        documents: List[Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate response from a list of document chunks.

        Args:
            query: User's question
            documents: List of (Document, score) tuples from vector search
            system_prompt: Custom system prompt

        Returns:
            Dict with 'answer' and 'sources' keys
        """
        # Extract content from documents
        contents = []
        sources = []

        for item in documents:
            if isinstance(item, (list, tuple)) and len(item) >= 1:
                doc = item[0]
                score = item[1] if len(item) > 1 else None

                # Handle Document objects
                if hasattr(doc, 'page_content'):
                    contents.append(doc.page_content)
                    metadata = getattr(doc, 'metadata', {})
                    sources.append({
                        "metadata": metadata,
                        "score": score
                    })
                elif isinstance(doc, dict):
                    contents.append(doc.get("page_content", ""))
                    sources.append({
                        "metadata": doc.get("metadata", {}),
                        "score": score
                    })

        if not contents:
            return {
                "answer": "No relevant documents found.",
                "sources": [],
                "llm_generated": False
            }

        # Combine context
        context = "\n\n---\n\n".join(contents)

        # Generate response
        if self.is_configured():
            answer = self.generate(query, context, system_prompt)
            llm_generated = True
        else:
            answer = context
            llm_generated = False

        return {
            "answer": answer,
            "sources": sources,
            "llm_generated": llm_generated
        }


# Global LLM service instance (lazy initialization)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def is_llm_enabled() -> bool:
    """Check if LLM generation is enabled via environment variable"""
    return os.getenv("USE_LLM", "false").lower() in ("true", "1", "yes")
