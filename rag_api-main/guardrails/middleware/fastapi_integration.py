#!/usr/bin/env python3
"""
FastAPI Integration for Guardrails

This module provides easy integration of guardrails with FastAPI applications.

Usage:
    from guardrails.middleware.fastapi_integration import GuardrailsMiddlewareAPI
    from fastapi import FastAPI

    app = FastAPI()
    guardrails = GuardrailsMiddlewareAPI()

    @app.post("/query")
    async def query(request: QueryRequest):
        # Check input
        input_check = guardrails.check_input(request.query)
        if input_check.blocked:
            return {"error": input_check.message, "blocked": True}

        # Process with LLM...
        response = await process_query(request.query)

        # Check output
        output_check = guardrails.check_output(response)
        if output_check.blocked:
            return {"answer": output_check.safe_response, "filtered": True}

        return {"answer": response}
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import functools

from guardrails.middleware.guardrails_middleware import (
    GuardrailsMiddleware,
    GuardrailConfig,
    GuardrailResult,
    Action,
    create_guardrails
)


class GuardrailsMiddlewareAPI:
    """
    FastAPI-specific guardrails middleware.

    Provides decorators and middleware for FastAPI endpoints.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize FastAPI guardrails.

        Args:
            config_path: Path to guardrails config YAML file
        """
        self.guardrails = create_guardrails(config_path)

    def check_input(self, text: str) -> GuardrailResult:
        """Check user input"""
        return self.guardrails.check_input(text)

    def check_output(self, text: str) -> GuardrailResult:
        """Check LLM output"""
        return self.guardrails.check_output(text)

    def redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        return self.guardrails.redact_pii(text)

    def protect_endpoint(self, check_input: bool = True, check_output: bool = True):
        """
        Decorator to protect FastAPI endpoints with guardrails.

        Args:
            check_input: Whether to check input
            check_output: Whether to check output

        Usage:
            @app.post("/query")
            @guardrails.protect_endpoint(check_input=True, check_output=True)
            async def query(request: QueryRequest):
                return {"answer": "..."}
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract input from request
                request = kwargs.get('request') or (args[0] if args else None)

                if check_input and request:
                    input_text = self._extract_input(request)
                    if input_text:
                        result = self.check_input(input_text)
                        if result.blocked:
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": result.message,
                                    "blocked": True,
                                    "guardrail_type": result.guardrail_type
                                }
                            )

                # Call the original function
                response = await func(*args, **kwargs)

                if check_output and isinstance(response, dict):
                    output_text = response.get('answer') or response.get('output') or response.get('response')
                    if output_text:
                        result = self.check_output(str(output_text))
                        if result.blocked:
                            response['answer'] = result.safe_response
                            response['filtered'] = True
                            response['guardrail_type'] = result.guardrail_type

                return response

            return wrapper
        return decorator

    def _extract_input(self, request) -> Optional[str]:
        """Extract input text from request"""
        if hasattr(request, 'query'):
            return request.query
        if hasattr(request, 'question'):
            return request.question
        if hasattr(request, 'prompt'):
            return request.prompt
        if hasattr(request, 'text'):
            return request.text
        return None


def add_guardrails_middleware(app: FastAPI, config_path: Optional[str] = None):
    """
    Add guardrails as FastAPI middleware.

    This will check ALL requests/responses automatically.

    Args:
        app: FastAPI application
        config_path: Path to guardrails config

    Usage:
        app = FastAPI()
        add_guardrails_middleware(app, "guardrails/configs/guardrails_config.yaml")
    """
    guardrails = create_guardrails(config_path)

    @app.middleware("http")
    async def guardrails_middleware(request: Request, call_next):
        # Check input for POST requests
        if request.method == "POST":
            try:
                body = await request.body()
                body_text = body.decode('utf-8')

                result = guardrails.check_input(body_text)
                if result.blocked:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": result.message,
                            "blocked": True,
                            "guardrail_type": result.guardrail_type
                        }
                    )
            except Exception:
                pass  # If we can't parse body, continue

        # Process request
        response = await call_next(request)

        return response

    return guardrails


# Example usage with RAG API
def example_rag_integration():
    """
    Example showing how to integrate guardrails with RAG API.
    """
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()

    # Initialize guardrails
    guardrails = GuardrailsMiddlewareAPI("guardrails/configs/guardrails_config.yaml")

    class QueryRequest(BaseModel):
        query: str
        file_id: str = "test-doc-006"
        k: int = 4

    @app.post("/query")
    async def query_with_guardrails(request: QueryRequest):
        # Step 1: Check input
        input_result = guardrails.check_input(request.query)
        if input_result.blocked:
            return {
                "error": input_result.message,
                "blocked": True,
                "guardrail_type": input_result.guardrail_type
            }

        # Step 2: Process query (your existing RAG logic)
        # response = await rag_query(request.query, request.file_id, request.k)
        response = "This is the RAG response..."  # Placeholder

        # Step 3: Check output
        output_result = guardrails.check_output(response)
        if output_result.blocked:
            return {
                "answer": output_result.safe_response,
                "filtered": True,
                "guardrail_type": output_result.guardrail_type
            }

        return {"answer": response}

    return app
