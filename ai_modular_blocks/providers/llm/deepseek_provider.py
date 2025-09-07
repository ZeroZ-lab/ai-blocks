"""
DeepSeek LLM provider implementation

This module provides integration with DeepSeek's API for chat completions
and other language model operations. DeepSeek API is compatible with OpenAI format.
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_CLIENT_AVAILABLE = True
except ImportError:
    OPENAI_CLIENT_AVAILABLE = False
    openai = None
    AsyncOpenAI = None

from ...core.base import BaseLLMProvider
from ...core.exceptions import (
    AuthenticationException,
    ConfigurationException,
    DependencyException,
    NetworkException,
    ProviderException,
    QuotaExceededException,
    RateLimitException,
    TimeoutException,
)
from ...core.types import LLMConfig, LLMResponse, MessageList


class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek LLM provider implementation.

    Provides integration with DeepSeek's API including DeepSeek-V3, DeepSeek-Coder,
    and other DeepSeek models with full support for streaming responses.
    
    DeepSeek API is compatible with OpenAI format, making integration straightforward.
    """

    # DeepSeek API endpoint
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
    
    # Supported models
    SUPPORTED_MODELS = [
        "deepseek-chat",
        "deepseek-coder", 
        "deepseek-v3",
        "deepseek-reasoner",
    ]

    def __init__(self, config: LLMConfig):
        if not OPENAI_CLIENT_AVAILABLE:
            raise DependencyException(
                "OpenAI package not available. Install with: pip install openai",
                dependency_name="openai",
                required_version=">=1.0.0",
            )

        super().__init__(config)
        self.client: Optional[AsyncOpenAI] = None

        # Normalize base URL to include /v1
        base_url = config.base_url or self.DEFAULT_BASE_URL
        if base_url and not base_url.rstrip('/').endswith('/v1'):
            base_url = base_url.rstrip('/') + '/v1'
        self.base_url = base_url

        # Ensure a valid default model for DeepSeek
        if not getattr(self.config, 'model', None) or self.config.model == 'gpt-3.5-turbo':
            self.config.model = 'deepseek-chat'

    @classmethod
    def is_available(cls) -> bool:
        """Check if DeepSeek provider is available."""
        return OPENAI_CLIENT_AVAILABLE

    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get list of supported DeepSeek models."""
        return cls.SUPPORTED_MODELS.copy()

    async def _initialize_provider(self) -> None:
        """Initialize the DeepSeek client."""
        try:
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.base_url,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )
            
            # Test connection with a simple request
            await self._test_connection()
            
        except Exception as e:
            raise ProviderException(
                f"Failed to initialize DeepSeek provider: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _test_connection(self) -> None:
        """Test the connection to DeepSeek API."""
        try:
            # Try to get available models to test the connection
            models = await self.client.models.list()
            self.logger.debug(f"DeepSeek connection test successful. Found {len(models.data)} models")
        except Exception as e:
            if "authentication" in str(e).lower():
                raise AuthenticationException(
                    "DeepSeek API authentication failed. Please check your API key.",
                    provider_name=self.provider_name,
                )
            else:
                raise NetworkException(
                    f"Failed to connect to DeepSeek API: {str(e)}",
                    provider_name=self.provider_name,
                )

    async def _chat_completion_impl(
        self,
        messages: MessageList,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs: Any,
    ) -> LLMResponse:
        """Implement chat completion using DeepSeek API."""
        # 自动初始化（如果尚未初始化）
        if not self.client:
            await self.initialize()

        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages_to_openai_format(messages)

            # Make API request
            response = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Convert response to our format
            return self._convert_openai_response_to_llm_response(response)

        except Exception as e:
            self._handle_api_error(e)

    async def stream_chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[LLMResponse, None]:
        """Generate streaming chat completion."""
        # 自动初始化（如果尚未初始化）
        if not self.client:
            await self.initialize()

        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages_to_openai_format(messages)

            # Create streaming request
            stream = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )

            # Yield streaming responses
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield LLMResponse(
                        content=chunk.choices[0].delta.content,
                        model=model,
                        usage={},  # Usage info comes in the last chunk
                        created_at=datetime.now(),
                        finish_reason=chunk.choices[0].finish_reason or "streaming",
                    )

        except Exception as e:
            self._handle_api_error(e)

    async def _get_available_models_impl(self) -> List[str]:
        """Get available models from DeepSeek API."""
        # 自动初始化（如果尚未初始化）
        if not self.client:
            await self.initialize()

        try:
            response = await self.client.models.list()
            return [model.id for model in response.data]
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch models from API: {e}")
            # Return default supported models if API call fails
            return self.SUPPORTED_MODELS.copy()

    def _convert_messages_to_openai_format(self, messages: MessageList) -> List[Dict[str, Any]]:
        """Convert our message format to OpenAI API format."""
        openai_messages = []
        
        for message in messages:
            openai_message = {
                "role": message.role,
                "content": message.content,
            }
            
            # Add metadata if available
            if message.metadata:
                # DeepSeek might support additional parameters
                openai_message.update(message.metadata)
            
            openai_messages.append(openai_message)
        
        return openai_messages

    def _convert_openai_response_to_llm_response(self, response) -> LLMResponse:
        """Convert OpenAI API response to our LLMResponse format."""
        choice = response.choices[0]
        
        # Extract usage information
        usage = {}
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage=usage,
            created_at=datetime.fromtimestamp(response.created),
            finish_reason=choice.finish_reason or "stop",
            metadata={
                "id": response.id,
                "object": response.object,
                "system_fingerprint": getattr(response, "system_fingerprint", None),
            },
        )

    def _handle_api_error(self, error: Exception) -> None:
        """Handle and convert API errors to our exception types."""
        error_str = str(error).lower()

        if "authentication" in error_str or "unauthorized" in error_str:
            raise AuthenticationException(
                f"DeepSeek API authentication failed: {error}",
                provider_name=self.provider_name,
            ) from error

        elif "rate limit" in error_str or "too many requests" in error_str:
            raise RateLimitException(
                f"DeepSeek API rate limit exceeded: {error}",
                provider_name=self.provider_name,
                retry_after=60,  # Default retry after 60 seconds
            ) from error

        elif "quota" in error_str or "billing" in error_str:
            raise QuotaExceededException(
                f"DeepSeek API quota exceeded: {error}",
                provider_name=self.provider_name,
                quota_type="api_calls",
            ) from error

        elif "timeout" in error_str:
            raise TimeoutException(
                f"DeepSeek API request timeout: {error}",
                provider_name=self.provider_name,
                timeout_duration=self.config.timeout,
            ) from error

        elif "network" in error_str or "connection" in error_str:
            raise NetworkException(
                f"DeepSeek API network error: {error}",
                provider_name=self.provider_name,
            ) from error

        else:
            raise ProviderException(
                f"DeepSeek API error: {error}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from error

    async def _cleanup_provider(self) -> None:
        """Cleanup DeepSeek provider resources."""
        if self.client:
            # Close HTTP connections
            await self.client.close()
            self.client = None

    async def _perform_health_check(self) -> bool:
        """Perform health check for DeepSeek provider."""
        try:
            if not self.client:
                return False

            # Try to list models as a health check
            await self.client.models.list()
            return True

        except Exception as e:
            self.logger.warning(f"DeepSeek health check failed: {e}")
            return False

    def _validate_provider_config(self, config: LLMConfig) -> None:
        """Validate DeepSeek-specific configuration."""
        # 先调用基类的基础验证
        super()._validate_provider_config(config)
        
        # DeepSeek特定验证 - API key格式
        if not config.api_key.startswith("sk-"):
            raise ConfigurationException(
                "DeepSeek API key must start with 'sk-'",
                config_key="api_key",
                details={"provider": "deepseek"},
            )
        
        # 验证base URL如果提供了的话
        if hasattr(config, 'base_url') and config.base_url:
            if not config.base_url.startswith(("http://", "https://")):
                raise ConfigurationException(
                    "Base URL must be a valid HTTP/HTTPS URL",
                    config_key="base_url",
                    config_value=config.base_url,
                    details={"provider": "deepseek"},
                )

    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider-specific information."""
        return {
            "provider_name": "deepseek",
            "provider_type": "llm",
            "base_url": self.base_url,
            "supported_models": self.SUPPORTED_MODELS,
            "supports_streaming": True,
            "supports_function_calling": False,  # Update when DeepSeek adds support
            "max_tokens_limit": 32768,  # DeepSeek-V3 context limit
            "api_format": "openai_compatible",
        }
