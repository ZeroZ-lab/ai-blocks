"""
Configuration types for AI Modular Blocks

Minimal configuration classes for LLM providers.
Users can extend or replace these as needed.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LLMConfig:
    """Basic LLM provider configuration."""
    
    api_key: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: float = 30.0
    max_retries: int = 3
    base_url: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)
    
    # Users can add any custom parameters
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ToolConfig:
    """Basic tool configuration."""
    
    enabled: bool = True
    timeout: float = 30.0
    retry_count: int = 3
    
    # Users can add any custom parameters  
    extra_params: Dict[str, Any] = field(default_factory=dict)


# Legacy aliases for backward compatibility
VectorStoreConfig = Dict[str, Any]  # Users define their own
EmbeddingConfig = Dict[str, Any]    # Users define their own