"""
AI Modular Blocks - Composable AI development blocks
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your-email@example.com"

from .core.exceptions import AIBlockException
from .core.interfaces import LLMProvider, VectorStore
from .core.types import LLMResponse, VectorDocument

__all__ = [
    "LLMProvider",
    "VectorStore",
    "LLMResponse",
    "VectorDocument",
    "AIBlockException",
]
