"""
Large Language Model interfaces for AI Modular Blocks

This module contains all LLM-related interfaces:
- Basic LLM provider interface
- Enhanced LLM provider with function calling support
- Streaming capabilities

Following the "Do One Thing Well" philosophy.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, List, Optional

from ..types import EnhancedLLMResponse, LLMResponse, MessageList, ToolList


class LLMProvider(ABC):
    """
    Abstract base class for Large Language Model providers.

    This interface defines the standard operations that all LLM providers
    must implement, ensuring consistency across different provider implementations.
    """

    @abstractmethod
    async def chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a chat completion response.

        Args:
            messages: List of chat messages in the conversation
            model: Model identifier to use for generation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse containing the generated content and metadata

        Raises:
            ProviderException: When provider-specific errors occur
            ValidationException: When input validation fails
        """
        pass

    @abstractmethod
    async def stream_chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[LLMResponse, None]:
        """
        Generate a streaming chat completion response.

        Args:
            messages: List of chat messages in the conversation
            model: Model identifier to use for generation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters

        Yields:
            LLMResponse objects containing incremental content

        Raises:
            ProviderException: When provider-specific errors occur
            ValidationException: When input validation fails
        """
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models from the provider.

        Returns:
            List of model identifiers

        Raises:
            ProviderException: When unable to fetch models
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass


class EnhancedLLMProvider(LLMProvider):
    """
    Enhanced LLM Provider with function calling capabilities.
    
    Extends the base LLMProvider to support tool/function calling,
    which is essential for modern AI applications.
    """

    @abstractmethod
    async def chat_completion_with_tools(
        self,
        messages: MessageList,
        tools: Optional[ToolList] = None,
        tool_choice: str = "auto",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> EnhancedLLMResponse:
        """
        Generate chat completion with tool calling support.

        Args:
            messages: List of chat messages in the conversation
            tools: Available tools for the model to use
            tool_choice: How the model should choose tools ("auto", "none", or specific tool)
            model: Model identifier to use for generation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters

        Returns:
            EnhancedLLMResponse with potential tool calls
        """
        pass

    @abstractmethod
    async def stream_chat_completion_with_tools(
        self,
        messages: MessageList,
        tools: Optional[ToolList] = None,
        tool_choice: str = "auto",
        model: str = "gpt-3.5-turbo",
        **kwargs: Any,
    ) -> AsyncGenerator[EnhancedLLMResponse, None]:
        """
        Stream chat completion with tool calling support.

        Args:
            messages: List of chat messages in the conversation
            tools: Available tools for the model to use
            tool_choice: How the model should choose tools
            model: Model identifier to use for generation
            **kwargs: Provider-specific parameters

        Yields:
            Streaming EnhancedLLMResponse chunks
        """
        pass
