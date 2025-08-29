"""
Interface definitions for AI Modular Blocks

This module re-exports all interfaces to maintain backward compatibility
while organizing code according to single responsibility principle.
"""

# LLM interfaces
from .llm import (
    EnhancedLLMProvider,
    LLMProvider,
)

# MCP interfaces
from .mcp import (
    MCPProvider,
)

# Storage interfaces
from .storage import (
    EmbeddingProvider,
    VectorStore,
)

# Tool interfaces
from .tools import (
    ToolProvider,
)

# Utility interfaces
from .utilities import (
    CacheProvider,
    DocumentProcessor,
    Middleware,
    Plugin,
)

__all__ = [
    # LLM interfaces
    "LLMProvider",
    "EnhancedLLMProvider",
    
    # Storage interfaces
    "VectorStore",
    "EmbeddingProvider",
    
    # Tool interfaces
    "ToolProvider",
    
    # MCP interfaces
    "MCPProvider",
    
    # Utility interfaces
    "DocumentProcessor",
    "CacheProvider",
    "Middleware",
    "Plugin",
]
