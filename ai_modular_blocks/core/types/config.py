"""
Configuration type definitions for AI Modular Blocks

This module contains all configuration-related types:
- Base provider configurations
- LLM, Vector Store, and Embedding configurations
- Tool and MCP configurations

Following the "Do One Thing Well" philosophy.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class ProviderConfig:
    """Base configuration for providers"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


class LLMConfig(ProviderConfig):
    """Configuration for LLM providers"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )


class VectorStoreConfig(ProviderConfig):
    """Configuration for vector store providers"""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        metric: str = "cosine",
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            index_name=index_name,
            dimension=dimension,
            metric=metric,
            **kwargs,
        )


class EmbeddingConfig(ProviderConfig):
    """Configuration for embedding providers"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002",
        dimension: int = 1536,
        **kwargs,
    ):
        super().__init__(api_key=api_key, model=model, dimension=dimension, **kwargs)


@dataclass
class ToolConfig:
    """Configuration for tool providers"""
    
    enabled_tools: List[str]
    tool_timeout: float = 30.0
    max_tool_calls: int = 5
    allow_parallel_calls: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MCPConfig:
    """Configuration for MCP providers"""
    
    server_url: str
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    supported_protocols: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
