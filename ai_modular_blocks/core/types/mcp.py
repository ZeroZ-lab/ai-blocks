"""
Model Context Protocol (MCP) type definitions for AI Modular Blocks

This module contains all MCP protocol related types:
- MCP resource definitions
- MCP context and protocol structures
- MCP-specific enums and data classes

Following the "Do One Thing Well" philosophy.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .tools import ToolDefinition


class MCPResourceType(str, Enum):
    """MCP resource types"""
    
    FILE = "file"
    DIRECTORY = "directory"
    DATABASE = "database"
    API_ENDPOINT = "api_endpoint"
    CUSTOM = "custom"


@dataclass
class MCPResource:
    """MCP resource definition"""
    
    uri: str
    name: str
    type: MCPResourceType
    description: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MCPContext:
    """MCP context information"""
    
    resources: List[MCPResource]
    tools: List[ToolDefinition]
    metadata: Optional[Dict[str, Any]] = None
