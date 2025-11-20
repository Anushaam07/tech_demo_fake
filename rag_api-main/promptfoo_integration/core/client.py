"""
Promptfoo client for interacting with target LLM applications.

This module provides a unified interface for testing different types of LLM applications,
including APIs, LangChain applications, RAG systems, and custom integrations.
"""

import asyncio
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from promptfoo_integration.core.types import TargetConfig


class BaseTargetClient(ABC):
    """
    Abstract base class for target clients.

    Subclasses must implement the query method to interact with specific LLM applications.
    """

    def __init__(self, config: TargetConfig):
        """
        Initialize the target client.

        Args:
            config: Target configuration
        """
        self.config = config
        self.name = config.name

    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Send a query to the target and get response.

        Args:
            prompt: Input prompt/query
            **kwargs: Additional parameters

        Returns:
            Response from the target
        """
        pass

    @abstractmethod
    def query_sync(self, prompt: str, **kwargs) -> str:
        """
        Synchronous version of query.

        Args:
            prompt: Input prompt/query
            **kwargs: Additional parameters

        Returns:
            Response from the target
        """
        pass


class APITargetClient(BaseTargetClient):
    """
    Client for REST API-based LLM applications.

    Supports both synchronous and asynchronous requests to HTTP endpoints.
    """

    def __init__(self, config: TargetConfig):
        """
        Initialize API client.

        Args:
            config: Target configuration with endpoint and headers
        """
        super().__init__(config)
        self.endpoint = config.endpoint
        self.headers = config.config.get("headers", {})
        self.method = config.config.get("method", "POST").upper()
        self.timeout = config.config.get("timeout", 30)

    async def query(self, prompt: str, **kwargs) -> str:
        """
        Send async query to API endpoint.

        Args:
            prompt: Input prompt
            **kwargs: Additional request parameters

        Returns:
            API response text

        Raises:
            Exception: If request fails
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query_sync, prompt, **kwargs)

    def query_sync(self, prompt: str, **kwargs) -> str:
        """
        Send synchronous query to API endpoint.

        Args:
            prompt: Input prompt
            **kwargs: Additional request parameters

        Returns:
            API response text

        Raises:
            Exception: If request fails
        """
        payload = self._build_payload(prompt, **kwargs)

        try:
            if self.method == "POST":
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )
            elif self.method == "GET":
                response = requests.get(
                    self.endpoint,
                    params=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")

            response.raise_for_status()
            return self._extract_response(response.json())

        except Exception as e:
            return f"Error: {str(e)}"

    def _build_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Build request payload from prompt and additional params."""
        payload_template = self.config.config.get("payload_template", {})
        payload = payload_template.copy()

        # Default structure
        if not payload:
            payload = {"prompt": prompt, "query": prompt}

        # Override with custom mapping
        prompt_key = self.config.config.get("prompt_key", "prompt")
        payload[prompt_key] = prompt

        # Add any additional parameters
        payload.update(kwargs)

        return payload

    def _extract_response(self, response_data: Dict[str, Any]) -> str:
        """Extract response text from API response."""
        response_key = self.config.config.get("response_key", "response")

        # Try to find response in common locations
        if response_key in response_data:
            return str(response_data[response_key])
        elif "answer" in response_data:
            return str(response_data["answer"])
        elif "text" in response_data:
            return str(response_data["text"])
        elif "output" in response_data:
            return str(response_data["output"])
        else:
            return str(response_data)


class LangChainTargetClient(BaseTargetClient):
    """
    Client for LangChain-based applications.

    Supports testing LangChain chains, agents, and RAG systems.
    """

    def __init__(self, config: TargetConfig):
        """
        Initialize LangChain client.

        Args:
            config: Target configuration with chain/agent reference
        """
        super().__init__(config)
        self.chain = config.config.get("chain")
        self.invoke_method = config.config.get("invoke_method", "invoke")

    async def query(self, prompt: str, **kwargs) -> str:
        """
        Send async query to LangChain application.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Chain/agent response
        """
        if not self.chain:
            raise ValueError("LangChain chain/agent not configured")

        try:
            # Try async invoke first
            if hasattr(self.chain, "ainvoke"):
                result = await self.chain.ainvoke({"input": prompt, **kwargs})
            else:
                # Fall back to sync
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self.query_sync, prompt, **kwargs)
                return result

            return self._extract_langchain_response(result)

        except Exception as e:
            return f"Error: {str(e)}"

    def query_sync(self, prompt: str, **kwargs) -> str:
        """
        Send synchronous query to LangChain application.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Chain/agent response
        """
        if not self.chain:
            raise ValueError("LangChain chain/agent not configured")

        try:
            invoke_fn = getattr(self.chain, self.invoke_method)
            result = invoke_fn({"input": prompt, **kwargs})
            return self._extract_langchain_response(result)

        except Exception as e:
            return f"Error: {str(e)}"

    def _extract_langchain_response(self, result: Any) -> str:
        """Extract response from LangChain result."""
        if isinstance(result, dict):
            # Try common keys
            for key in ["output", "answer", "result", "text"]:
                if key in result:
                    return str(result[key])
            return str(result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)


class CustomTargetClient(BaseTargetClient):
    """
    Client for custom LLM applications.

    Allows users to provide custom query functions for maximum flexibility.
    """

    def __init__(
        self,
        config: TargetConfig,
        query_fn: Optional[Callable] = None,
        async_query_fn: Optional[Callable] = None
    ):
        """
        Initialize custom client with user-provided query functions.

        Args:
            config: Target configuration
            query_fn: Synchronous query function
            async_query_fn: Asynchronous query function
        """
        super().__init__(config)
        self._query_fn = query_fn or config.config.get("query_fn")
        self._async_query_fn = async_query_fn or config.config.get("async_query_fn")

        if not self._query_fn and not self._async_query_fn:
            raise ValueError("At least one query function must be provided")

    async def query(self, prompt: str, **kwargs) -> str:
        """
        Send async query using custom function.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Response from custom function
        """
        try:
            if self._async_query_fn:
                result = await self._async_query_fn(prompt, **kwargs)
            elif self._query_fn:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self._query_fn, prompt, **kwargs)
            else:
                raise ValueError("No query function available")

            return str(result)

        except Exception as e:
            return f"Error: {str(e)}"

    def query_sync(self, prompt: str, **kwargs) -> str:
        """
        Send synchronous query using custom function.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Response from custom function
        """
        try:
            if self._query_fn:
                result = self._query_fn(prompt, **kwargs)
            else:
                raise ValueError("Synchronous query function not provided")

            return str(result)

        except Exception as e:
            return f"Error: {str(e)}"


class PromptfooClient:
    """
    Main client for Promptfoo integration.

    Factory class that creates appropriate target clients based on configuration.
    """

    @staticmethod
    def create_target_client(config: TargetConfig, **kwargs) -> BaseTargetClient:
        """
        Create a target client based on configuration.

        Args:
            config: Target configuration
            **kwargs: Additional arguments for client initialization

        Returns:
            Appropriate target client instance

        Raises:
            ValueError: If target type is not supported

        Example:
            >>> target_config = TargetConfig(
            ...     name="my-rag-api",
            ...     type="api",
            ...     endpoint="http://localhost:8000/query"
            ... )
            >>> client = PromptfooClient.create_target_client(target_config)
        """
        target_type = config.type.lower()

        if target_type == "api":
            return APITargetClient(config)
        elif target_type in ["langchain", "rag", "agent"]:
            return LangChainTargetClient(config)
        elif target_type == "custom":
            return CustomTargetClient(config, **kwargs)
        else:
            raise ValueError(f"Unsupported target type: {target_type}")

    @staticmethod
    def create_api_client(
        name: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **config_options
    ) -> APITargetClient:
        """
        Convenience method to create an API client.

        Args:
            name: Target name
            endpoint: API endpoint URL
            headers: HTTP headers
            **config_options: Additional configuration

        Returns:
            API target client

        Example:
            >>> client = PromptfooClient.create_api_client(
            ...     name="my-api",
            ...     endpoint="http://localhost:8000/query",
            ...     headers={"Authorization": "Bearer token"}
            ... )
        """
        config = TargetConfig(
            name=name,
            type="api",
            endpoint=endpoint,
            config={"headers": headers or {}, **config_options}
        )
        return APITargetClient(config)

    @staticmethod
    def create_langchain_client(
        name: str,
        chain: Any,
        **config_options
    ) -> LangChainTargetClient:
        """
        Convenience method to create a LangChain client.

        Args:
            name: Target name
            chain: LangChain chain/agent instance
            **config_options: Additional configuration

        Returns:
            LangChain target client

        Example:
            >>> from langchain.chains import RetrievalQA
            >>> client = PromptfooClient.create_langchain_client(
            ...     name="my-rag-chain",
            ...     chain=my_chain
            ... )
        """
        config = TargetConfig(
            name=name,
            type="langchain",
            config={"chain": chain, **config_options}
        )
        return LangChainTargetClient(config)
