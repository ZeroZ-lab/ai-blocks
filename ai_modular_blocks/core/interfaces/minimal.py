"""
Minimal core interfaces for AI Modular Blocks

Only the absolutely essential interfaces that enable interoperability.
Everything else is optional and can be implemented by users.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """
    Minimal LLM provider interface.
    
    This is the ONLY required interface. Everything else is optional.
    """
    
    async def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from a prompt.
        
        Returns:
            dict with at least 'content' key
        """
        ...


@runtime_checkable  
class ToolProvider(Protocol):
    """
    Optional tool provider interface.
    
    Users can implement this or create their own tool system.
    """
    
    async def execute_tool(
        self, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        ...


# That's it! Everything else is user-defined.
# No required base classes, no complex abstractions.
# Just protocols for interoperability.