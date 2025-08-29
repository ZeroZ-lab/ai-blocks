"""
Anthropic LLM provider implementation

This module provides integration with Anthropic's Claude API for chat completions
and other language model operations.
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    import anthropic
    from anthropic import AsyncAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    AsyncAnthropic = None

from ...core.base import BaseLLMProvider
from ...core.exceptions import (
    AuthenticationException,
    DependencyException,
    NetworkException,
    ProviderException,
    QuotaExceededException,
    RateLimitException,
    TimeoutException,
)
from ...core.types import LLMConfig, LLMResponse, MessageList


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic LLM provider implementation.

    Provides integration with Anthropic's Claude API including Claude-2,
    Claude-Instant, and other models with support for streaming responses.
    """

    def __init__(self, config: LLMConfig):
        if not ANTHROPIC_AVAILABLE:
            raise DependencyException(
                "Anthropic package not available. Install with: pip install anthropic",
                dependency_name="anthropic",
            )

        super().__init__(config)
        self.client: Optional[AsyncAnthropic] = None

    async def _initialize_provider(self) -> None:
        """Initialize the Anthropic client."""
        try:
            self.client = AsyncAnthropic(
                api_key=self.config.api_key,
                base_url=getattr(self.config, "base_url", None),
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )

            # Test the connection
            await self._perform_health_check()

        except Exception as e:
            raise ProviderException(
                f"Failed to initialize Anthropic client: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _cleanup_provider(self) -> None:
        """Cleanup Anthropic client resources."""
        if self.client:
            await self.client.close()
            self.client = None

    async def _perform_health_check(self) -> bool:
        """Perform health check by making a simple API call."""
        if not self.client:
            return False

        try:
            # Make a simple completion request to test connectivity
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=test_messages,
            )
            return response is not None

        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False

    async def _chat_completion_impl(
        self,
        messages: MessageList,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs: Any,
    ) -> LLMResponse:
        """Implementation of chat completion for Anthropic."""
        if not self.client:
            await self.initialize()

        # Convert messages to Anthropic format
        anthropic_messages, system_message = self._convert_messages_to_anthropic(
            messages
        )

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens or 1000,  # Required parameter for Anthropic
            "temperature": temperature,
            **kwargs,
        }

        # Add system message if present
        if system_message:
            request_params["system"] = system_message

        try:
            response = await self.client.messages.create(**request_params)
            return self._convert_anthropic_response(response)

        except anthropic.AuthenticationError as e:
            raise AuthenticationException(
                f"Anthropic authentication failed: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except anthropic.RateLimitError as e:
            raise RateLimitException(
                f"Anthropic rate limit exceeded: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except anthropic.APITimeoutError as e:
            raise TimeoutException(
                f"Anthropic request timeout: {str(e)}",
                provider_name=self.provider_name,
                timeout_duration=self.config.timeout,
                operation_type="chat_completion",
            ) from e

        except anthropic.InternalServerError as e:
            raise ProviderException(
                f"Anthropic internal server error: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except anthropic.APIConnectionError as e:
            raise NetworkException(
                f"Anthropic connection error: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except Exception as e:
            # Handle quota exceeded errors
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                raise QuotaExceededException(
                    f"Anthropic quota exceeded: {str(e)}",
                    provider_name=self.provider_name,
                ) from e

            raise ProviderException(
                f"Anthropic API error: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    async def stream_chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[LLMResponse, None]:
        """Implementation of streaming chat completion for Anthropic."""
        if not self.client:
            await self.initialize()

        # Convert messages to Anthropic format
        anthropic_messages, system_message = self._convert_messages_to_anthropic(
            messages
        )

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens or 1000,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }

        # Add system message if present
        if system_message:
            request_params["system"] = system_message

        try:
            stream = await self.client.messages.create(**request_params)

            async for chunk in stream:
                if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                    yield self._convert_anthropic_streaming_chunk(chunk)

        except Exception as e:
            # Use the same error handling as chat_completion
            self.logger.error(f"Streaming completion error: {e}")
            raise

    async def _get_available_models_impl(self) -> List[str]:
        """Get available models from Anthropic."""
        # Anthropic doesn't have a models endpoint, so return known models
        return self.get_supported_models()

    def _convert_messages_to_anthropic(
        self, messages: MessageList
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Convert internal message format to Anthropic format."""
        anthropic_messages = []
        system_message = None

        for message in messages:
            if message.role == "system":
                # Anthropic handles system messages separately
                if system_message is None:
                    system_message = message.content
                else:
                    # Concatenate multiple system messages
                    system_message += "\n\n" + message.content
            else:
                anthropic_message = {
                    "role": message.role,
                    "content": message.content,
                }
                anthropic_messages.append(anthropic_message)

        return anthropic_messages, system_message

    def _convert_anthropic_response(self, response) -> LLMResponse:
        """Convert Anthropic response to internal format."""
        # Extract the main content
        content = ""
        if response.content:
            # Anthropic returns content as a list of content blocks
            content_parts = []
            for block in response.content:
                if hasattr(block, "text"):
                    content_parts.append(block.text)
            content = "".join(content_parts)

        # Extract usage information
        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": getattr(response.usage, "input_tokens", 0),
                "completion_tokens": getattr(response.usage, "output_tokens", 0),
                "total_tokens": getattr(response.usage, "input_tokens", 0)
                + getattr(response.usage, "output_tokens", 0),
            }

        # Extract finish reason
        finish_reason = getattr(response, "stop_reason", "")

        # Build metadata
        metadata = {
            "response_id": response.id,
            "model": response.model,
            "stop_reason": finish_reason,
        }

        return LLMResponse(
            content=content,
            model=response.model,
            usage=usage,
            created_at=datetime.utcnow(),  # Anthropic doesn't provide creation time
            finish_reason=finish_reason,
            metadata=metadata,
        )

    def _convert_anthropic_streaming_chunk(self, chunk) -> LLMResponse:
        """Convert Anthropic streaming chunk to internal format."""
        content = ""
        if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
            content = chunk.delta.text

        finish_reason = ""
        if hasattr(chunk, "delta") and hasattr(chunk.delta, "stop_reason"):
            finish_reason = chunk.delta.stop_reason or ""

        metadata = {
            "is_chunk": True,
            "event_type": getattr(chunk, "type", "unknown"),
        }

        return LLMResponse(
            content=content,
            model="",  # Model info not available in chunks
            usage={},  # Usage is typically only in the final chunk
            created_at=datetime.utcnow(),
            finish_reason=finish_reason,
            metadata=metadata,
        )

    def estimate_tokens(self, text: str, model: str = "claude-3-haiku-20240307") -> int:
        """
        Estimate token count for text.

        Note: This is a rough estimation based on Anthropic's documentation
        that suggests approximately 3.5 characters per token on average.
        """
        return len(text) // 3.5

    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get list of models supported by this provider."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ]

    @classmethod
    def is_available(cls) -> bool:
        """Check if Anthropic provider is available."""
        return ANTHROPIC_AVAILABLE

    def get_model_context_window(self, model: str) -> int:
        """Get the context window size for a specific model."""
        context_windows = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
        }
        return context_windows.get(model, 100000)  # Default to 100k

    def get_model_max_output_tokens(self, model: str) -> int:
        """Get the maximum output tokens for a specific model."""
        # Most Claude models can output up to 4000 tokens
        return 4000
