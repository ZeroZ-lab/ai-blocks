"""
Interface definitions for AI Modular Blocks

Minimal interface exports for essential functionality.
"""

# Minimal interfaces
from .minimal import LLMProvider, ToolProvider

# Optional interfaces (if they exist)
try:
    from .llm import LLMProvider as DetailedLLMProvider
except ImportError:
    DetailedLLMProvider = LLMProvider

try:
    from .tools import ToolProvider as DetailedToolProvider  
except ImportError:
    DetailedToolProvider = ToolProvider

__all__ = [
    "LLMProvider",
    "ToolProvider",
]