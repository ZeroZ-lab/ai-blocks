"""
AI Modular Blocks - Minimal AI development framework

Like React, minimal framework syntax that relies on Python language features.

The only thing you need to know:
    llm = create_llm("openai", api_key="sk-...")
    response = await llm.generate("Hello")
    
Everything else is pure Python - your freedom to implement however you want.
"""

__version__ = "0.1.0"
__author__ = "AI Modular Blocks Team"
__email__ = "team@ai-modular-blocks.com"

# Essential types
from .core.types.basic import (
    LLMResponse, Message, ToolCall, ToolResult, ToolDefinition,
    MessageList, ToolCallList, ToolResultList, ToolList
)
from .core.types.config import LLMConfig, ToolConfig

# Essential interfaces
from .core.interfaces.minimal import LLMProvider, ToolProvider

# Essential providers
from .providers.llm.factory import LLMProviderFactory

# Essential exceptions
from .core.exceptions import AIBlocksException

# Exports
__all__ = [
    # The one function you need
    "create_llm",
    
    # Types (if you want type hints)
    "LLMResponse", "Message", "ToolCall", "ToolResult", "ToolDefinition",
    "LLMConfig", "ToolConfig",
    
    # Interfaces (if you want protocols)  
    "LLMProvider", "ToolProvider",
    
    # Advanced (if you need them)
    "LLMProviderFactory", "AIBlocksException",
]


def create_llm(provider: str, **config) -> LLMProvider:
    """
    The only function you need to know.
    
    Everything else is pure Python - implement however you want.
    
    Usage:
        llm = create_llm("openai", api_key="sk-...")
        response = await llm.generate("Hello")
        print(response["content"])
        
    Supported providers:
        - "openai"
        - "anthropic" 
        - "deepseek"
    """
    # Friendly defaults for examples: if requested provider has no API key but
    # DEEPSEEK_API_KEY is present, fallback to DeepSeek.
    import os
    requested = provider.lower()

    # Auto-fill API keys from environment if not provided
    if "api_key" not in config or not config.get("api_key"):
        env_key = os.getenv(f"{requested.upper()}_API_KEY")
        if env_key:
            config["api_key"] = env_key

    # Fallback to DeepSeek when no key for requested provider but DeepSeek is available
    if ("api_key" not in config or not config.get("api_key")) and os.getenv("DEEPSEEK_API_KEY"):
        provider = "deepseek"
        config["api_key"] = os.getenv("DEEPSEEK_API_KEY")

    # Set a conservative default max_tokens to improve responsiveness in examples
    if provider.lower() == "deepseek" and "max_tokens" not in config:
        config["max_tokens"] = 256

    llm_config = LLMConfig(**config)
    return LLMProviderFactory.create_provider(provider, llm_config)


# Example of user freedom - no framework classes needed:
#
# class MyAgent:  # Pure Python class
#     def __init__(self):
#         self.llm = create_llm("openai", api_key="...")
#         self.memory = []  # Your own data structure
#     
#     async def chat(self, message: str) -> str:
#         self.memory.append({"user": message})  # Your own logic
#         response = await self.llm.generate(message)
#         self.memory.append({"bot": response["content"]})
#         return response["content"]
#
# agent = MyAgent()  # No inheritance, no framework abstractions
# reply = await agent.chat("Hello!")  # Just Python
