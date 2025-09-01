"""
Minimal AI Modular Blocks - Just the essentials

This module provides the absolute minimum needed.
Everything else is optional convenience.
"""

from typing import Any, Dict, Optional

# Import only the minimal interfaces
from .core.interfaces.minimal import LLMProvider, ToolProvider
from .providers.llm.factory import LLMProviderFactory
from .core.types.config import LLMConfig


def create_llm(provider: str, **config) -> LLMProvider:
    """
    Create an LLM provider. That's it.
    
    Usage:
        llm = create_llm("openai", api_key="sk-...")
        response = await llm.generate("Hello")
        print(response["content"])
    """
    llm_config = LLMConfig(**config)
    return LLMProviderFactory.create_provider(provider, llm_config)


# Users implement their own agents however they want:
# 
# class MyAgent:
#     def __init__(self, llm):
#         self.llm = llm
#     
#     async def chat(self, message):
#         response = await self.llm.generate(message)
#         return response["content"]
#
# That's pure Python. No framework abstractions needed.