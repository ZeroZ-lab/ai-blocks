"""
Vector store providers for AI Modular Blocks

This module contains implementations for various vector storage providers.
"""

from .factory import VectorStoreFactory

__all__ = ["VectorStoreFactory"]

# Import providers only if their dependencies are available
try:
    from .pinecone_store import PineconeVectorStore

    __all__.append("PineconeVectorStore")
except ImportError:
    PineconeVectorStore = None

try:
    from .chroma_store import ChromaVectorStore

    __all__.append("ChromaVectorStore")
except ImportError:
    ChromaVectorStore = None
