"""
Tool type definitions for AI Modular Blocks

Simple re-exports from basic.py to avoid duplication.
"""

# Re-export tool types from basic.py to avoid duplication
from .basic import (
    ToolCall, ToolResult, ToolDefinition,
    ToolCallList, ToolResultList, ToolList
)

__all__ = [
    "ToolCall", "ToolResult", "ToolDefinition",
    "ToolCallList", "ToolResultList", "ToolList"
]