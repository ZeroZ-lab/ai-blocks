"""
Vector Store Provider Factory

This module provides a factory for creating vector store provider instances
with automatic provider discovery and registration.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from ...core.exceptions import (
    ConfigurationException,
    DependencyException,
    ProviderException,
)
from ...core.interfaces import VectorStore
from ...core.types import VectorStoreConfig

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """
    Factory for creating vector store provider instances.

    Supports automatic discovery of available providers and provides
    a unified interface for creating provider instances with proper
    configuration validation.
    """

    _providers: Dict[str, Type[VectorStore]] = {}
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the factory by discovering available providers."""
        if cls._initialized:
            return

        cls._discover_providers()
        cls._initialized = True
        logger.info(
            f"Vector store factory initialized with {len(cls._providers)} providers"
        )

    @classmethod
    def _discover_providers(cls) -> None:
        """Discover and register available vector store providers."""
        # Register Pinecone provider if available
        try:
            from .pinecone_store import PineconeVectorStore

            if PineconeVectorStore.is_available():
                cls.register_provider("pinecone", PineconeVectorStore)
                logger.debug("Registered Pinecone provider")
            else:
                logger.debug("Pinecone provider not available (missing dependencies)")
        except ImportError as e:
            logger.debug(f"Pinecone provider not available: {e}")

        # Register ChromaDB provider if available
        try:
            from .chroma_store import ChromaVectorStore

            if ChromaVectorStore.is_available():
                cls.register_provider("chroma", ChromaVectorStore)
                cls.register_provider("chromadb", ChromaVectorStore)  # Alternative name
                logger.debug("Registered ChromaDB provider")
            else:
                logger.debug("ChromaDB provider not available (missing dependencies)")
        except ImportError as e:
            logger.debug(f"ChromaDB provider not available: {e}")

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[VectorStore]) -> None:
        """
        Register a new vector store provider.

        Args:
            name: Provider name identifier
            provider_class: Provider class that implements VectorStore interface

        Raises:
            ConfigurationException: If provider registration fails
        """
        if not issubclass(provider_class, VectorStore):
            raise ConfigurationException(
                "Provider class must implement VectorStore interface",
                details={
                    "provider_name": name,
                    "provider_class": provider_class.__name__,
                },
            )

        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered vector store provider: {name}")

    @classmethod
    def unregister_provider(cls, name: str) -> None:
        """
        Unregister a vector store provider.

        Args:
            name: Provider name identifier
        """
        name_lower = name.lower()
        if name_lower in cls._providers:
            del cls._providers[name_lower]
            logger.info(f"Unregistered vector store provider: {name}")

    @classmethod
    def create_provider(cls, name: str, config: VectorStoreConfig) -> VectorStore:
        """
        Create a vector store provider instance.

        Args:
            name: Provider name identifier
            config: Provider configuration

        Returns:
            Configured vector store provider instance

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
                f"Unknown vector store provider: {name}",
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
            logger.info(f"Created vector store provider instance: {name}")
            return provider

        except Exception as e:
            if isinstance(e, (ConfigurationException, DependencyException)):
                raise
            else:
                raise ProviderException(
                    f"Failed to create provider '{name}': {str(e)}",
                    provider_name=name,
                    provider_type="vector_store",
                ) from e

    @classmethod
    def _validate_config_for_provider(
        cls, provider_name: str, config: VectorStoreConfig
    ) -> None:
        """Validate configuration for a specific provider."""
        # Basic validation
        if not config.index_name:
            raise ConfigurationException(
                f"Index name is required for provider '{provider_name}'",
                config_key="index_name",
                details={"provider": provider_name},
            )

        # Provider-specific validation
        if provider_name == "pinecone":
            cls._validate_pinecone_config(config)
        elif provider_name in ["chroma", "chromadb"]:
            cls._validate_chroma_config(config)

    @classmethod
    def _validate_pinecone_config(cls, config: VectorStoreConfig) -> None:
        """Validate Pinecone-specific configuration."""
        # Validate API key
        if not config.api_key:
            raise ConfigurationException(
                "API key is required for Pinecone",
                config_key="api_key",
                details={"provider": "pinecone"},
            )

        # Validate dimension
        dimension = getattr(config, "dimension", None)
        if dimension and (dimension < 1 or dimension > 20000):
            raise ConfigurationException(
                "Dimension must be between 1 and 20000 for Pinecone",
                config_key="dimension",
                config_value=dimension,
                details={"provider": "pinecone"},
            )

        # Validate metric
        metric = getattr(config, "metric", "cosine")
        valid_metrics = ["cosine", "euclidean", "dotproduct"]
        if metric not in valid_metrics:
            raise ConfigurationException(
                f"Invalid metric for Pinecone. Must be one of: {valid_metrics}",
                config_key="metric",
                config_value=metric,
                details={"provider": "pinecone", "valid_metrics": valid_metrics},
            )

    @classmethod
    def _validate_chroma_config(cls, config: VectorStoreConfig) -> None:
        """Validate ChromaDB-specific configuration."""
        # Validate dimension if specified
        dimension = getattr(config, "dimension", None)
        if dimension and dimension < 1:
            raise ConfigurationException(
                "Dimension must be positive for ChromaDB",
                config_key="dimension",
                config_value=dimension,
                details={"provider": "chroma"},
            )

        # Validate metric
        metric = getattr(config, "metric", "cosine")
        valid_metrics = ["cosine", "euclidean", "manhattan", "dot"]
        if metric not in valid_metrics:
            raise ConfigurationException(
                f"Invalid metric for ChromaDB. Must be one of: {valid_metrics}",
                config_key="metric",
                config_value=metric,
                details={"provider": "chroma", "valid_metrics": valid_metrics},
            )

        # Validate port if specified
        port = getattr(config, "port", 8000)
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ConfigurationException(
                "Port must be a valid port number (1-65535)",
                config_key="port",
                config_value=port,
                details={"provider": "chroma"},
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
                f"Unknown vector store provider: {name}",
                details={"requested_provider": name},
            )

        provider_class = cls._providers[name_lower]

        info = {
            "name": name,
            "class_name": provider_class.__name__,
            "module": provider_class.__module__,
            "available": True,
        }

        # Add provider-specific information if available
        if hasattr(provider_class, "is_available"):
            info["available"] = provider_class.is_available()

        # Add supported features
        if name_lower == "pinecone":
            info.update(
                {
                    "supports_namespaces": True,
                    "supports_metadata_filtering": True,
                    "supports_batch_operations": True,
                    "cloud_hosted": True,
                }
            )
        elif name_lower in ["chroma", "chromadb"]:
            info.update(
                {
                    "supports_namespaces": True,
                    "supports_metadata_filtering": True,
                    "supports_batch_operations": True,
                    "cloud_hosted": False,
                    "local_storage": True,
                }
            )

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
    def get_recommended_provider(cls, use_case: str = "general") -> Optional[str]:
        """
        Get recommended provider for a specific use case.

        Args:
            use_case: Use case identifier ("general", "local", "production", "testing")

        Returns:
            Recommended provider name or None if no providers available
        """
        if not cls._initialized:
            cls.initialize()

        available_providers = cls.get_available_providers()

        if not available_providers:
            return None

        recommendations = {
            "production": ["pinecone", "chroma"],
            "local": ["chroma", "chromadb"],
            "testing": ["chroma", "chromadb"],
            "general": ["pinecone", "chroma"],
        }

        preferred_providers = recommendations.get(use_case, ["pinecone", "chroma"])

        # Return first available preferred provider
        for provider in preferred_providers:
            if provider in available_providers:
                return provider

        # Return any available provider
        return available_providers[0] if available_providers else None

    @classmethod
    def reset(cls) -> None:
        """Reset the factory (mainly for testing purposes)."""
        cls._providers.clear()
        cls._initialized = False
        logger.debug("Vector store factory reset")
