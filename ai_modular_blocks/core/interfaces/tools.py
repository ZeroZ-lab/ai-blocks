"""
Tool interfaces for AI Modular Blocks

This module contains tool-related interfaces:
- Tool provider for registration and execution
- Tool management and validation
- Parallel tool execution capabilities

Following the "Do One Thing Well" philosophy.
"""

from abc import ABC, abstractmethod

from ..types import ToolCall, ToolCallList, ToolDefinition, ToolList, ToolResult, ToolResultList


class ToolProvider(ABC):
    """
    Abstract base class for tool providers.
    
    Tool providers manage the registration, discovery, and execution
    of tools that can be called by LLMs.
    """

    @abstractmethod
    async def register_tool(self, tool: ToolDefinition) -> bool:
        """
        Register a new tool.

        Args:
            tool: Tool definition to register

        Returns:
            True if registration was successful
        """
        pass

    @abstractmethod
    async def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if unregistration was successful
        """
        pass

    @abstractmethod
    async def get_available_tools(self) -> ToolList:
        """
        Get list of all available tools.

        Returns:
            List of registered tool definitions
        """
        pass

    @abstractmethod
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call.

        Args:
            tool_call: Tool call request from LLM

        Returns:
            Result of tool execution
        """
        pass

    @abstractmethod
    async def execute_tools_parallel(self, tool_calls: ToolCallList) -> ToolResultList:
        """
        Execute multiple tool calls in parallel.

        Args:
            tool_calls: List of tool call requests

        Returns:
            List of tool execution results
        """
        pass

    @abstractmethod
    async def validate_tool_call(self, tool_call: ToolCall) -> bool:
        """
        Validate a tool call request.

        Args:
            tool_call: Tool call to validate

        Returns:
            True if the tool call is valid
        """
        pass
