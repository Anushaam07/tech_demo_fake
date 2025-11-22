# app/models.py
import hashlib
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List


class DocumentResponse(BaseModel):
    page_content: str
    metadata: dict


class DocumentModel(BaseModel):
    page_content: str
    metadata: Optional[dict] = {}

    def generate_digest(self):
        hash_obj = hashlib.md5(self.page_content.encode())
        return hash_obj.hexdigest()


class StoreDocument(BaseModel):
    filepath: str
    filename: str
    file_content_type: str
    file_id: str


class QueryRequestBody(BaseModel):
    query: str
    file_id: str
    k: int = 4
    entity_id: Optional[str] = None
    use_llm: Optional[bool] = None  # If None, uses USE_LLM env var


class QueryResponse(BaseModel):
    """Response model for /query endpoint with LLM generation"""
    answer: Optional[str] = None  # LLM-generated answer (if enabled)
    sources: Optional[List[dict]] = None  # Source documents with metadata
    llm_generated: bool = False  # Whether answer was LLM-generated
    raw_documents: Optional[List] = None  # Raw document chunks (for backward compat)


class CleanupMethod(str, Enum):
    incremental = "incremental"
    full = "full"


class QueryMultipleBody(BaseModel):
    query: str
    file_ids: List[str]
    k: int = 4
