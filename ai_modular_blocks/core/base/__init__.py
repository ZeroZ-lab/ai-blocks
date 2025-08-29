"""
Base implementations for AI Modular Blocks

This module provides base classes that concrete providers can inherit from
to get common functionality like error handling, logging, metrics collection,
and configuration management.

Following the "Do One Thing Well" philosophy - each file focuses on one provider type.
"""

from .llm import BaseLLMProvider
from .provider import BaseProvider
from .storage import BaseEmbeddingProvider, BaseVectorStore
from .utilities import BaseDocumentProcessor

__all__ = [
    # Core base class
    "BaseProvider",
    
    # LLM base classes  
    "BaseLLMProvider",
    
    # Storage base classes
    "BaseVectorStore",
    "BaseEmbeddingProvider",
    
    # Utility base classes
    "BaseDocumentProcessor",
]
