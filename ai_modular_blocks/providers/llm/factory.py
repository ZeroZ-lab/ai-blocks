"""
LLM Provider Factory

This module provides a factory for creating LLM provider instances
with automatic provider discovery and registration.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from ...core.exceptions import (
    ConfigurationException,
    DependencyException,
    ProviderException,
)
from ...core.interfaces import LLMProvider
from ...core.types import LLMConfig

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.

    Supports automatic discovery of available providers and provides
    a unified interface for creating provider instances with proper
    configuration validation.
    """

    _providers: Dict[str, Type[LLMProvider]] = {}
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the factory by discovering available providers."""
        if cls._initialized:
            return

        cls._discover_providers()
        cls._initialized = True
        logger.info(f"LLM factory initialized with {len(cls._providers)} providers")

    @classmethod
    def _discover_providers(cls) -> None:
        """Discover and register available LLM providers."""
        # Register OpenAI provider if available
        try:
            from .openai_provider import OpenAIProvider

            if OpenAIProvider.is_available():
                cls.register_provider("openai", OpenAIProvider)
                logger.debug("Registered OpenAI provider")
            else:
                logger.debug("OpenAI provider not available (missing dependencies)")
        except ImportError as e:
            logger.debug(f"OpenAI provider not available: {e}")

        # Register Anthropic provider if available
        try:
            from .anthropic_provider import AnthropicProvider

            if AnthropicProvider.is_available():
                cls.register_provider("anthropic", AnthropicProvider)
                logger.debug("Registered Anthropic provider")
            else:
                logger.debug("Anthropic provider not available (missing dependencies)")
        except ImportError as e:
            logger.debug(f"Anthropic provider not available: {e}")

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Register a new LLM provider.

        Args:
            name: Provider name identifier
            provider_class: Provider class that implements LLMProvider interface

        Raises:
            ConfigurationException: If provider registration fails
        """
        if not issubclass(provider_class, LLMProvider):
            raise ConfigurationException(
                "Provider class must implement LLMProvider interface",
                details={
                    "provider_name": name,
                    "provider_class": provider_class.__name__,
                },
            )

        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered LLM provider: {name}")

    @classmethod
    def unregister_provider(cls, name: str) -> None:
        """
        Unregister an LLM provider.

        Args:
            name: Provider name identifier
        """
        name_lower = name.lower()
        if name_lower in cls._providers:
            del cls._providers[name_lower]
            logger.info(f"Unregistered LLM provider: {name}")

    @classmethod
    def create_provider(cls, name: str, config: LLMConfig) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            name: Provider name identifier
            config: Provider configuration

        Returns:
            Configured LLM provider instance

        Raises:
            ConfigurationException: If provider is not found or configuration is invalid
            DependencyException: If provider dependencies are missing
        """
        if not cls._initialized:
            cls.initialize()

        name_lower = name.lower()

        if name_lower not in cls._providers:
            available_providers = list(cls._providers.keys())
            raise ConfigurationException(
                f"Unknown LLM provider: {name}",
                details={
                    "requested_provider": name,
                    "available_providers": available_providers,
                },
            )

        provider_class = cls._providers[name_lower]

        try:
            # Validate configuration for this provider
            cls._validate_config_for_provider(name_lower, config)

            # Create provider instance
            provider = provider_class(config)
            logger.info(f"Created LLM provider instance: {name}")
            return provider

        except Exception as e:
            if isinstance(e, (ConfigurationException, DependencyException)):
                raise
            else:
                raise ProviderException(
                    f"Failed to create provider '{name}': {str(e)}",
                    provider_name=name,
                    provider_type="llm",
                ) from e

    @classmethod
    def _validate_config_for_provider(
        cls, provider_name: str, config: LLMConfig
    ) -> None:
        """Validate configuration for a specific provider."""
        # Basic validation
        if not config.api_key:
            raise ConfigurationException(
                f"API key is required for provider '{provider_name}'",
                config_key="api_key",
                details={"provider": provider_name},
            )

        # Provider-specific validation
        if provider_name == "openai":
            cls._validate_openai_config(config)
        elif provider_name == "anthropic":
            cls._validate_anthropic_config(config)

    @classmethod
    def _validate_openai_config(cls, config: LLMConfig) -> None:
        """Validate OpenAI-specific configuration."""
        # Validate API key format (basic check)
        if not config.api_key.startswith("sk-"):
            raise ConfigurationException(
                "OpenAI API key must start with 'sk-'",
                config_key="api_key",
                details={"provider": "openai"},
            )

        # Validate timeout settings
        if config.timeout <= 0:
            raise ConfigurationException(
                "Timeout must be positive",
                config_key="timeout",
                config_value=config.timeout,
                details={"provider": "openai"},
            )

    @classmethod
    def _validate_anthropic_config(cls, config: LLMConfig) -> None:
        """Validate Anthropic-specific configuration."""
        # Validate API key format (basic check)
        if not config.api_key.startswith("sk-"):
            raise ConfigurationException(
                "Anthropic API key must start with 'sk-'",
                config_key="api_key",
                details={"provider": "anthropic"},
            )

        # Validate timeout settings
        if config.timeout <= 0:
            raise ConfigurationException(
                "Timeout must be positive",
                config_key="timeout",
                config_value=config.timeout,
                details={"provider": "anthropic"},
            )

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider names.

        Returns:
            List of registered provider names
        """
        if not cls._initialized:
            cls.initialize()

        return list(cls._providers.keys())

    @classmethod
    def is_provider_available(cls, name: str) -> bool:
        """
        Check if a provider is available.

        Args:
            name: Provider name identifier

        Returns:
            True if provider is available, False otherwise
        """
        if not cls._initialized:
            cls.initialize()

        return name.lower() in cls._providers

    @classmethod
    def get_provider_info(cls, name: str) -> Dict[str, Any]:
        """
        Get information about a specific provider.

        Args:
            name: Provider name identifier

        Returns:
            Dictionary containing provider information

        Raises:
            ConfigurationException: If provider is not found
        """
        if not cls._initialized:
            cls.initialize()

        name_lower = name.lower()

        if name_lower not in cls._providers:
            raise ConfigurationException(
                f"Unknown LLM provider: {name}", details={"requested_provider": name}
            )

        provider_class = cls._providers[name_lower]

        info = {
            "name": name,
            "class_name": provider_class.__name__,
            "module": provider_class.__module__,
            "available": True,
        }

        # Add provider-specific information if available
        if hasattr(provider_class, "get_supported_models"):
            info["supported_models"] = provider_class.get_supported_models()

        if hasattr(provider_class, "is_available"):
            info["available"] = provider_class.is_available()

        return info

    @classmethod
    def get_all_provider_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available providers.

        Returns:
            Dictionary mapping provider names to their information
        """
        if not cls._initialized:
            cls.initialize()

        provider_info = {}
        for name in cls._providers:
            try:
                provider_info[name] = cls.get_provider_info(name)
            except Exception as e:
                logger.warning(f"Failed to get info for provider {name}: {e}")
                provider_info[name] = {
                    "name": name,
                    "available": False,
                    "error": str(e),
                }

        return provider_info

    @classmethod
    def get_supported_models(
        cls, provider_name: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get supported models for providers.

        Args:
            provider_name: Optional specific provider name

        Returns:
            Dictionary mapping provider names to their supported models
        """
        if not cls._initialized:
            cls.initialize()

        if provider_name:
            provider_name = provider_name.lower()
            if provider_name not in cls._providers:
                raise ConfigurationException(
                    f"Unknown LLM provider: {provider_name}",
                    details={"requested_provider": provider_name},
                )
            providers_to_check = {provider_name: cls._providers[provider_name]}
        else:
            providers_to_check = cls._providers

        models_by_provider = {}

        for name, provider_class in providers_to_check.items():
            try:
                if hasattr(provider_class, "get_supported_models"):
                    models_by_provider[name] = provider_class.get_supported_models()
                else:
                    models_by_provider[name] = []
            except Exception as e:
                logger.warning(f"Failed to get models for provider {name}: {e}")
                models_by_provider[name] = []

        return models_by_provider

    @classmethod
    def reset(cls) -> None:
        """Reset the factory (mainly for testing purposes)."""
        cls._providers.clear()
        cls._initialized = False
        logger.debug("LLM factory reset")
