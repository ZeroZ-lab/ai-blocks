"""
Utility interfaces for AI Modular Blocks

This module contains interfaces for utility components:
- Document processors
- Cache providers
- Middleware components
- Plugin systems

Following the "Do One Thing Well" philosophy.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..types import DocumentList


class DocumentProcessor(ABC):
    """
    Abstract base class for document processors.

    Document processors transform documents through various operations
    like loading, splitting, filtering, or enriching with metadata.
    """

    @abstractmethod
    async def process(self, documents: DocumentList) -> DocumentList:
        """
        Process a list of documents.

        Args:
            documents: List of documents to process

        Returns:
            List of processed documents

        Raises:
            ProcessorException: When processing fails
        """
        pass

    @abstractmethod
    def get_processor_name(self) -> str:
        """
        Get the name of this processor.

        Returns:
            Processor name identifier
        """
        pass


class CacheProvider(ABC):
    """
    Abstract base class for cache providers.

    This interface defines standard caching operations with TTL support
    and different cache strategies.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False if key didn't exist
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all values from the cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        pass


class Middleware(ABC):
    """
    Abstract base class for middleware components.

    Middleware components can intercept and modify requests/responses
    in the processing pipeline.
    """

    @abstractmethod
    async def process(
        self,
        request: Any,
        call_next: Any,
    ) -> Any:
        """
        Process a request through the middleware.

        Args:
            request: The incoming request
            call_next: Function to call the next middleware in chain

        Returns:
            The processed response
        """
        pass

    @abstractmethod
    def get_middleware_name(self) -> str:
        """
        Get the name of this middleware.

        Returns:
            Middleware name identifier
        """
        pass


class Plugin(ABC):
    """
    Abstract base class for plugin components.

    Plugins extend the functionality of the system with custom features.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name identifier."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string."""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration dictionary
        """
        pass

    @abstractmethod
    async def finalize(self) -> None:
        """Cleanup plugin resources."""
        pass

    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Get list of plugin dependencies.

        Returns:
            List of required plugin names
        """
        pass
