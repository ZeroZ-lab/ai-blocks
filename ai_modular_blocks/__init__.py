"""
AI Modular Blocks - Minimal AI development framework

Like React, minimal framework syntax that relies on Python language features.
"""

__version__ = "0.1.0"
__author__ = "AI Modular Blocks Team"
__email__ = "team@ai-modular-blocks.com"

# Essential types only
from .core.types.basic import (
    LLMResponse, Message, ToolCall, ToolResult, ToolDefinition,
    MessageList, ToolCallList, ToolResultList, ToolList
)
from .core.types.config import LLMConfig, ToolConfig

# Essential interfaces (protocols)
from .core.interfaces.minimal import LLMProvider, ToolProvider

# Essential providers
from .providers.llm.factory import LLMProviderFactory

# Essential exceptions
from .core.exceptions import AIBlocksException

# Minimal exports - users import what they need
__all__ = [
    # Types
    "LLMResponse", 
    "Message", 
    "ToolCall", 
    "ToolResult",
    "ToolDefinition",
    "LLMConfig",
    "ToolConfig",
    
    # Interfaces  
    "LLMProvider",
    "ToolProvider", 
    
    # Providers
    "LLMProviderFactory",
    
    # Exceptions
    "AIBlocksException",
]

# Single convenience function - everything else is user freedom
def create_llm(provider: str, **config) -> LLMProvider:
    """
    The only convenience function you need.
    
    Usage:
        llm = create_llm("openai", api_key="sk-...")
        response = await llm.generate("Hello")
        print(response["content"])
    """
    llm_config = LLMConfig(**config)
    return LLMProviderFactory.create_provider(provider, llm_config)


# Everything else is user freedom:
# 
# class MyAgent:  # No inheritance required!
#     def __init__(self):
#         self.llm = create_llm("openai", api_key="...")
#     
#     async def chat(self, message: str) -> str:
#         response = await self.llm.generate(message)
#         return response["content"]
