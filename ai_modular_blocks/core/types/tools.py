"""
Tool and Function Calling type definitions for AI Modular Blocks

This module contains all tool and function calling related types:
- Tool definitions and parameters
- Tool calls and results
- Enhanced LLM responses with tool support
- Function calling message formats

Following the "Do One Thing Well" philosophy.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .basic import ChatMessage, LLMResponse


class ToolParameterType(str, Enum):
    """Parameter types for tool definitions"""
    
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Parameter definition for a tool"""
    
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


@dataclass
class ToolDefinition:
    """Tool definition following OpenAI function calling format"""
    
    name: str
    description: str
    parameters: List[ToolParameter]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolCall:
    """A tool call request from the LLM"""
    
    id: str
    name: str
    arguments: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolResult:
    """Result of a tool execution"""
    
    tool_call_id: str
    content: str
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FunctionCallMessage(ChatMessage):
    """Chat message with function call support"""
    
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


@dataclass
class EnhancedLLMResponse(LLMResponse):
    """LLM response with tool calling support"""
    
    tool_calls: Optional[List[ToolCall]] = None
    requires_tool_response: bool = False


# =============================================================================
# Type aliases for tool-related collections
# =============================================================================

ToolList = List[ToolDefinition]
ToolCallList = List[ToolCall]
ToolResultList = List[ToolResult]
