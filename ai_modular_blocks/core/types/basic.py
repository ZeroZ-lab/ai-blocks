"""
Basic type definitions for AI Modular Blocks

Only the essential types needed for interoperability.
Everything else is optional.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMResponse:
    """Standard LLM response format."""
    
    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access for backward compatibility."""
        if key == "content":
            return self.content
        elif hasattr(self, key):
            return getattr(self, key)
        elif self.metadata and key in self.metadata:
            return self.metadata[key]
        raise KeyError(f"Key '{key}' not found")


@dataclass  
class Message:
    """Simple message format."""
    
    role: str  # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ToolCall:
    """Tool call request."""
    
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Tool execution result."""
    
    tool_call_id: str
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None
    success: bool = True


@dataclass
class ToolDefinition:
    """Tool definition for LLM function calling."""
    
    name: str
    description: str
    parameters: Dict[str, Any]


# Type aliases for convenience
MessageList = List[Message]
ToolCallList = List[ToolCall] 
ToolResultList = List[ToolResult]
ToolList = List[ToolDefinition]

# Legacy alias for compatibility
VectorDocument = Dict[str, Any]  # Users can define their own format