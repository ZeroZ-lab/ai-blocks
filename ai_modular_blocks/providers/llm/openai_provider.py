"""
OpenAI LLM provider implementation

This module provides integration with OpenAI's API for chat completions
and other language model operations.
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    import openai
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    AsyncOpenAI = None

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


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider implementation.

    Provides integration with OpenAI's API including GPT-3.5, GPT-4,
    and other language models with full support for streaming responses.
    """

    def __init__(self, config: LLMConfig):
        if not OPENAI_AVAILABLE:
            raise DependencyException(
                "OpenAI package not available. Install with: pip install openai",
                dependency_name="openai",
            )

        super().__init__(config)
        self.client: Optional[AsyncOpenAI] = None
        self._rate_limit_status = {
            "requests_remaining": None,
            "tokens_remaining": None,
            "reset_time": None,
        }

    async def _initialize_provider(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=getattr(self.config, "base_url", None),
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )

            # Test the connection
            await self._perform_health_check()

        except Exception as e:
            raise ProviderException(
                f"Failed to initialize OpenAI client: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _cleanup_provider(self) -> None:
        """Cleanup OpenAI client resources."""
        if self.client:
            await self.client.close()
            self.client = None

    async def _perform_health_check(self) -> bool:
        """Perform health check by listing available models."""
        if not self.client:
            return False

        try:
            models = await self.client.models.list()
            return len(models.data) > 0

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
        """Implementation of chat completion for OpenAI."""
        if not self.client:
            await self.initialize()

        # Convert messages to OpenAI format
        openai_messages = self._convert_messages_to_openai(messages)

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens

        try:
            response = await self.client.chat.completions.create(**request_params)
            return self._convert_openai_response(response)

        except openai.AuthenticationError as e:
            raise AuthenticationException(
                f"OpenAI authentication failed: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except openai.RateLimitError as e:
            # Extract retry information if available
            retry_after = getattr(e, "retry_after", None)
            raise RateLimitException(
                f"OpenAI rate limit exceeded: {str(e)}",
                provider_name=self.provider_name,
                retry_after=retry_after,
            ) from e

        except openai.APITimeoutError as e:
            raise TimeoutException(
                f"OpenAI request timeout: {str(e)}",
                provider_name=self.provider_name,
                timeout_duration=self.config.timeout,
                operation_type="chat_completion",
            ) from e

        except openai.InternalServerError as e:
            raise ProviderException(
                f"OpenAI internal server error: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except openai.APIConnectionError as e:
            raise NetworkException(
                f"OpenAI connection error: {str(e)}",
                provider_name=self.provider_name,
            ) from e

        except Exception as e:
            # Handle quota exceeded errors
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                raise QuotaExceededException(
                    f"OpenAI quota exceeded: {str(e)}",
                    provider_name=self.provider_name,
                ) from e

            raise ProviderException(
                f"OpenAI API error: {str(e)}",
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
        """Implementation of streaming chat completion for OpenAI."""
        if not self.client:
            await self.initialize()

        # Input validation (handled by base class)
        validated_messages = self._convert_messages_to_openai(messages)

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": validated_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }

        if max_tokens is not None:
            request_params["max_tokens"] = max_tokens

        try:
            stream = await self.client.chat.completions.create(**request_params)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield self._convert_openai_streaming_chunk(chunk)

        except Exception as e:
            # Use the same error handling as chat_completion
            self.logger.error(f"Streaming completion error: {e}")
            raise

    async def _get_available_models_impl(self) -> List[str]:
        """Get available models from OpenAI."""
        if not self.client:
            await self.initialize()

        try:
            models_response = await self.client.models.list()
            models = [model.id for model in models_response.data]

            # Filter to only chat models (GPT models)
            chat_models = [
                model
                for model in models
                if any(prefix in model for prefix in ["gpt-", "text-davinci-", "code-"])
            ]

            return sorted(chat_models)

        except Exception as e:
            raise ProviderException(
                f"Failed to fetch OpenAI models: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    def _convert_messages_to_openai(
        self, messages: MessageList
    ) -> List[Dict[str, Any]]:
        """Convert internal message format to OpenAI format."""
        openai_messages = []

        for message in messages:
            openai_message = {
                "role": message.role,
                "content": message.content,
            }

            # Add metadata if available and relevant
            if message.metadata:
                # OpenAI supports function calls and tool calls in metadata
                if "function_call" in message.metadata:
                    openai_message["function_call"] = message.metadata["function_call"]
                if "tool_calls" in message.metadata:
                    openai_message["tool_calls"] = message.metadata["tool_calls"]
                if "name" in message.metadata:
                    openai_message["name"] = message.metadata["name"]

            openai_messages.append(openai_message)

        return openai_messages

    def _convert_openai_response(self, response) -> LLMResponse:
        """Convert OpenAI response to internal format."""
        # Defensive check: ensure response is an object, not string
        if isinstance(response, str):
            self.logger.warning(f"OpenAI returned string instead of response object: {response}")
            return LLMResponse(
                content=response,
                model="unknown",
                usage={},
                finish_reason="error",
                metadata={"error": "String response received"}
            )
        
        # Ensure response has expected attributes
        if not hasattr(response, 'choices'):
            self.logger.warning(f"OpenAI response missing 'choices' attribute: {type(response)}")
            return LLMResponse(
                content=str(response),
                model="unknown", 
                usage={},
                finish_reason="error",
                metadata={"error": "Invalid response structure"}
            )
        
        # Extract the main content
        content = ""
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content or ""

        # Extract usage information
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        # Extract finish reason
        finish_reason = ""
        if response.choices and response.choices[0].finish_reason:
            finish_reason = response.choices[0].finish_reason

        # Build metadata
        metadata = {
            "response_id": response.id,
            "created": response.created,
            "system_fingerprint": getattr(response, "system_fingerprint", None),
        }

        # Add function call information if present
        if (
            response.choices
            and response.choices[0].message
            and hasattr(response.choices[0].message, "function_call")
            and response.choices[0].message.function_call
        ):
            metadata["function_call"] = response.choices[0].message.function_call

        # Add tool calls if present
        if (
            response.choices
            and response.choices[0].message
            and hasattr(response.choices[0].message, "tool_calls")
            and response.choices[0].message.tool_calls
        ):
            metadata["tool_calls"] = response.choices[0].message.tool_calls

        return LLMResponse(
            content=content,
            model=response.model,
            usage=usage,
            created_at=datetime.fromtimestamp(response.created),
            finish_reason=finish_reason,
            metadata=metadata,
        )

    def _convert_openai_streaming_chunk(self, chunk) -> LLMResponse:
        """Convert OpenAI streaming chunk to internal format."""
        # Defensive check for streaming chunks
        if isinstance(chunk, str):
            return LLMResponse(
                content=chunk,
                model="unknown",
                usage={},
                finish_reason="streaming",
                metadata={"is_chunk": True, "error": "String chunk received"}
            )
        
        content = ""
        if hasattr(chunk, 'choices') and chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content

        finish_reason = ""
        if chunk.choices and chunk.choices[0].finish_reason:
            finish_reason = chunk.choices[0].finish_reason

        metadata = {
            "chunk_id": chunk.id,
            "created": chunk.created,
            "is_chunk": True,
        }

        return LLMResponse(
            content=content,
            model=chunk.model,
            usage={},  # Usage is typically only in the final chunk
            created_at=datetime.fromtimestamp(chunk.created),
            finish_reason=finish_reason,
            metadata=metadata,
        )

    def _update_rate_limit_status(self, response_headers: Dict[str, str]) -> None:
        """Update rate limit status from response headers."""
        try:
            if "x-ratelimit-remaining-requests" in response_headers:
                self._rate_limit_status["requests_remaining"] = int(
                    response_headers["x-ratelimit-remaining-requests"]
                )

            if "x-ratelimit-remaining-tokens" in response_headers:
                self._rate_limit_status["tokens_remaining"] = int(
                    response_headers["x-ratelimit-remaining-tokens"]
                )

            if "x-ratelimit-reset-requests" in response_headers:
                self._rate_limit_status["reset_time"] = response_headers[
                    "x-ratelimit-reset-requests"
                ]

        except (ValueError, KeyError) as e:
            self.logger.debug(f"Could not parse rate limit headers: {e}")

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self._rate_limit_status.copy()

    def estimate_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Estimate token count for text.

        Note: This is a rough estimation. For exact counts, use OpenAI's
        tiktoken library or the actual API response.
        """
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4

    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get list of models supported by this provider."""
        return [
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-4-32k-0613",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-1106",
        ]

    @classmethod
    def is_available(cls) -> bool:
        """Check if OpenAI provider is available."""
        return OPENAI_AVAILABLE
