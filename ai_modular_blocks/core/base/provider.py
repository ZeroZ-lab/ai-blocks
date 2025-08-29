"""
Base provider class for AI Modular Blocks

This module provides the foundation BaseProvider class that all providers
can inherit from to get common functionality like error handling,
logging, metrics collection, and configuration management.

Following the "Do One Thing Well" philosophy.
"""

import logging
import time
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional

from ..exceptions import ConfigurationException
from ..types import ProviderConfig

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Base class for all providers with common functionality.

    Provides standard implementations for configuration management,
    logging, error handling, and health checking.
    """

    def __init__(self, config: ProviderConfig, provider_type: str = "unknown"):
        self.config = config
        self.provider_type = provider_type
        self.provider_name = self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self.provider_name}")
        self._initialized = False
        self._health_status = True
        self._last_health_check = None

    async def initialize(self) -> None:
        """Initialize the provider."""
        if self._initialized:
            return

        try:
            await self._initialize_provider()
            self._initialized = True
            self.logger.info(f"Provider {self.provider_name} initialized successfully")

        except Exception as e:
            self.logger.error(
                f"Failed to initialize provider {self.provider_name}: {e}"
            )
            raise ConfigurationException(
                f"Provider initialization failed: {str(e)}",
                details={
                    "provider_name": self.provider_name,
                    "provider_type": self.provider_type,
                },
            ) from e

    async def _initialize_provider(self) -> None:
        """Subclasses should override this for specific initialization."""
        pass

    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        try:
            await self._cleanup_provider()
            self._initialized = False
            self.logger.info(f"Provider {self.provider_name} cleaned up successfully")

        except Exception as e:
            self.logger.error(f"Error during provider cleanup: {e}")

    async def _cleanup_provider(self) -> None:
        """Subclasses should override this for specific cleanup."""
        pass

    def _log_operation_start(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Log the start of an operation and return context."""
        context = {
            "operation": operation,
            "provider": self.provider_name,
            "start_time": time.time(),
            "kwargs": kwargs,
        }
        self.logger.debug(f"Starting operation: {operation}", extra=context)
        return context

    def _log_operation_end(
        self,
        context: Dict[str, Any],
        success: bool = True,
        error: Optional[Exception] = None,
    ) -> None:
        """Log the end of an operation."""
        duration = time.time() - context["start_time"]
        context.update(
            {
                "duration": duration,
                "success": success,
                "error": str(error) if error else None,
            }
        )

        if success:
            self.logger.debug(
                f"Operation completed: {context['operation']} ({duration:.3f}s)",
                extra=context,
            )
        else:
            self.logger.error(
                f"Operation failed: {context['operation']} ({duration:.3f}s): {error}",
                extra=context,
            )

    async def health_check(self) -> bool:
        """Check provider health status."""
        try:
            start_time = time.time()
            health_status = await self._perform_health_check()
            duration = time.time() - start_time

            self._health_status = health_status
            self._last_health_check = datetime.utcnow()

            self.logger.debug(
                f"Health check completed: {health_status} ({duration:.3f}s)",
                extra={
                    "provider": self.provider_name,
                    "health_status": health_status,
                    "duration": duration,
                },
            )

            return health_status

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self._health_status = False
            self._last_health_check = datetime.utcnow()
            return False

    async def _perform_health_check(self) -> bool:
        """Subclasses should override this for specific health checks."""
        return True

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status information."""
        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "healthy": self._health_status,
            "last_check": self._last_health_check.isoformat()
            if self._last_health_check
            else None,
            "initialized": self._initialized,
        }
