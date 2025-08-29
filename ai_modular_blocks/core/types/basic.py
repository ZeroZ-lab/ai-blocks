"""
Basic type definitions for AI Modular Blocks

This module contains fundamental types used throughout the system:
- Content types and message formats
- LLM responses and document structures
- Search results and basic data structures

Following the "Do One Thing Well" philosophy.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentType(str, Enum):
    """Content types supported by the system"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


@dataclass
class ChatMessage:
    """Chat message format"""

    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


@dataclass
class LLMResponse:
    """Standard response format for LLM providers"""

    content: str
    model: str
    usage: Dict[str, int]
    created_at: datetime
    finish_reason: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VectorDocument:
    """Document representation for vector storage"""

    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    content_type: ContentType = ContentType.TEXT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """Vector search result"""

    document: VectorDocument
    score: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProcessingConfig:
    """Configuration for processing operations"""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_k: int = 5
    filter_metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# Type aliases for common use cases
# =============================================================================

MessageList = List[ChatMessage]
DocumentList = List[VectorDocument]
EmbeddingVector = List[float]
MetadataDict = Dict[str, Any]
