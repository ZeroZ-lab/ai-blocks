"""
Model Context Protocol (MCP) interfaces for AI Modular Blocks

This module contains MCP protocol interfaces:
- MCP provider for protocol implementation
- Resource management and access
- Tool execution via MCP
- Change subscription capabilities

Following the "Do One Thing Well" philosophy.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from ..types import MCPContext, MCPResource, ToolCall, ToolList, ToolResult


class MCPProvider(ABC):
    """
    Abstract base class for Model Context Protocol providers.
    
    MCP providers implement the Model Context Protocol for standardized
    communication between AI models and external tools/data sources.
    """

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to MCP server.

        Returns:
            True if connection was successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from MCP server.
        """
        pass

    @abstractmethod
    async def get_resources(self) -> List[MCPResource]:
        """
        Get available MCP resources.

        Returns:
            List of available resources
        """
        pass

    @abstractmethod
    async def get_tools(self) -> ToolList:
        """
        Get available MCP tools.

        Returns:
            List of available tools from MCP server
        """
        pass

    @abstractmethod
    async def read_resource(self, resource_uri: str) -> str:
        """
        Read content from an MCP resource.

        Args:
            resource_uri: URI of the resource to read

        Returns:
            Content of the resource
        """
        pass

    @abstractmethod
    async def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call via MCP.

        Args:
            tool_call: Tool call request

        Returns:
            Result of tool execution
        """
        pass

    @abstractmethod
    async def get_context(self) -> MCPContext:
        """
        Get full MCP context (resources + tools).

        Returns:
            Complete MCP context information
        """
        pass

    @abstractmethod
    async def subscribe_to_changes(self, resource_uri: str) -> AsyncGenerator[str, None]:
        """
        Subscribe to changes in an MCP resource.

        Args:
            resource_uri: URI of the resource to monitor

        Yields:
            Updated resource content when changes occur
        """
        pass
