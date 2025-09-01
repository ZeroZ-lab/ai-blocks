"""
Core module for AI Modular Blocks

Minimal core exports for the framework.
Users can import what they need, or ignore this entirely.
"""

# Essential types
from .types.basic import (
    LLMResponse, Message, ToolCall, ToolResult, ToolDefinition,
    MessageList, ToolCallList, ToolResultList, ToolList
)
from .types.config import LLMConfig, ToolConfig

# Essential interfaces
from .interfaces.minimal import LLMProvider, ToolProvider

# Essential exceptions
from .exceptions import AIBlocksException

# Minimal exports
__all__ = [
    # Types
    "LLMResponse", "Message", "ToolCall", "ToolResult", "ToolDefinition",
    "MessageList", "ToolCallList", "ToolResultList", "ToolList",
    "LLMConfig", "ToolConfig",
    
    # Interfaces
    "LLMProvider", "ToolProvider",
    
    # Exceptions
    "AIBlocksException",
]