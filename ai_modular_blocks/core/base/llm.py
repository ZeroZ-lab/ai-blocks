"""
LLM base provider class for AI Modular Blocks

This module provides the BaseLLMProvider class that LLM providers
can inherit from to get common functionality like input validation,
error handling, response formatting, and configuration validation.

Following the "Do One Thing Well" philosophy.
"""

from datetime import datetime
from typing import Any, List, Optional

from .provider import BaseProvider
from ..exceptions import ConfigurationException, ProviderException, ValidationException
from ..interfaces import LLMProvider
from ..types import LLMConfig, LLMResponse, MessageList
from ..validators import InputValidator


class BaseLLMProvider(BaseProvider, LLMProvider):
    """
    Base implementation for LLM providers.

    Provides common functionality like input validation,
    error handling, and response formatting.
    """

    def __init__(self, config: LLMConfig):
        super().__init__(config, "llm")
        self.config: LLMConfig = config
        self._available_models: Optional[List[str]] = None
        self._models_cache_time: Optional[datetime] = None
        
        # 让每个provider自己验证配置
        self._validate_provider_config(config)

    async def chat_completion(
        self,
        messages: MessageList,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate chat completion with validation and error handling."""
        # Input validation
        validated_messages = InputValidator.validate_message_list(messages)
        validated_model = InputValidator.validate_model_name(model)
        validated_temperature = InputValidator.validate_temperature(temperature)

        # Log operation start
        context = self._log_operation_start(
            "chat_completion",
            model=validated_model,
            message_count=len(validated_messages),
            temperature=validated_temperature,
            max_tokens=max_tokens,
        )

        try:
            # Call provider-specific implementation
            response = await self._chat_completion_impl(
                validated_messages,
                validated_model,
                validated_temperature,
                max_tokens,
                **kwargs,
            )

            self._log_operation_end(context, success=True)
            return response

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            if isinstance(e, (ProviderException, ValidationException)):
                raise
            else:
                raise ProviderException(
                    f"Chat completion failed: {str(e)}",
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                ) from e

    async def _chat_completion_impl(
        self,
        messages: MessageList,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs: Any,
    ) -> LLMResponse:
        """Subclasses must implement this method."""
        raise NotImplementedError("Subclasses must implement _chat_completion_impl")

    async def get_available_models(self) -> List[str]:
        """Get available models with caching."""
        # Check cache validity (5 minutes)
        now = datetime.utcnow()
        if (
            self._available_models
            and self._models_cache_time
            and (now - self._models_cache_time).seconds < 300
        ):
            return self._available_models

        context = self._log_operation_start("get_available_models")

        try:
            models = await self._get_available_models_impl()
            self._available_models = models
            self._models_cache_time = now

            self._log_operation_end(context, success=True)
            return models

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"Failed to get available models: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _get_available_models_impl(self) -> List[str]:
        """Subclasses must implement this method."""
        raise NotImplementedError(
            "Subclasses must implement _get_available_models_impl"
        )
    
    def _validate_provider_config(self, config: LLMConfig) -> None:
        """
        Validate provider-specific configuration.
        
        Each provider should implement this method to validate its own
        configuration requirements (API key format, required fields, etc.).
        Base class provides common validation, subclasses can override
        for provider-specific checks.
        
        Args:
            config: LLM configuration to validate
            
        Raises:
            ConfigurationException: If configuration is invalid
        """
        # 基础验证 - 所有provider都需要API key
        if not config.api_key:
            raise ConfigurationException(
                f"API key is required for {self.provider_name}",
                config_key="api_key",
                details={"provider": self.provider_name},
            )
        
        # 基础超时验证
        if config.timeout <= 0:
            raise ConfigurationException(
                "Timeout must be positive",
                config_key="timeout",
                config_value=config.timeout,
                details={"provider": self.provider_name},
            )
