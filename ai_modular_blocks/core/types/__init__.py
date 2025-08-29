"""
Type definitions for AI Modular Blocks

This module re-exports all types to maintain backward compatibility
while organizing code according to single responsibility principle.
"""

# Basic types
from .basic import (
    ChatMessage,
    ContentType,
    DocumentList,
    EmbeddingVector,
    LLMResponse,
    MessageList,
    MetadataDict,
    ProcessingConfig,
    SearchResult,
    VectorDocument,
)

# Configuration types
from .config import (
    EmbeddingConfig,
    LLMConfig,
    MCPConfig,
    ProviderConfig,
    ToolConfig,
    VectorStoreConfig,
)

# MCP types
from .mcp import (
    MCPContext,
    MCPResource,
    MCPResourceType,
)

# Tool types
from .tools import (
    EnhancedLLMResponse,
    FunctionCallMessage,
    ToolCall,
    ToolCallList,
    ToolDefinition,
    ToolList,
    ToolParameter,
    ToolParameterType,
    ToolResult,
    ToolResultList,
)

__all__ = [
    # Basic types
    "ChatMessage",
    "ContentType",
    "LLMResponse",
    "VectorDocument",
    "SearchResult",
    "ProcessingConfig",
    "MessageList",
    "DocumentList",
    "EmbeddingVector",
    "MetadataDict",
    
    # Configuration types
    "ProviderConfig",
    "LLMConfig",
    "VectorStoreConfig",
    "EmbeddingConfig",
    "ToolConfig",
    "MCPConfig",
    
    # Tool types
    "ToolParameterType",
    "ToolParameter",
    "ToolDefinition",
    "ToolCall",
    "ToolResult",
    "FunctionCallMessage",
    "EnhancedLLMResponse",
    "ToolList",
    "ToolCallList",
    "ToolResultList",
    
    # MCP types
    "MCPResourceType",
    "MCPResource",
    "MCPContext",
]
