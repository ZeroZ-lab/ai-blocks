"""
Exception hierarchy for AI Modular Blocks

This module defines a comprehensive exception hierarchy that provides
clear error categorization and helpful error handling capabilities.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class AIBlocksException(Exception):
    """
    Base exception class for all AI Modular Blocks errors.

    Provides a standardized structure for error information including
    error codes, details, and timestamps.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            base_msg += f" (Details: {details_str})"
        return base_msg


class ConfigurationException(AIBlocksException):
    """
    Exception raised for configuration-related errors.

    This includes missing configuration values, invalid configuration
    formats, or configuration validation failures.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = str(config_value)

        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details,
            **kwargs,
        )


class ValidationException(AIBlocksException):
    """
    Exception raised for input validation errors.

    This includes invalid parameter values, malformed data,
    or constraint violations.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if field_name:
            details["field_name"] = field_name
        if field_value is not None:
            details["field_value"] = str(field_value)
        if expected_type:
            details["expected_type"] = expected_type

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs,
        )


class ProviderException(AIBlocksException):
    """
    Base exception for provider-related errors.

    This serves as the parent class for all provider-specific
    exceptions and includes provider identification.
    """

    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        provider_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if provider_name:
            details["provider_name"] = provider_name
        if provider_type:
            details["provider_type"] = provider_type

        super().__init__(
            message=message,
            error_code="PROVIDER_ERROR",
            details=details,
            **kwargs,
        )


class AuthenticationException(ProviderException):
    """
    Exception raised for authentication failures.

    This includes invalid API keys, expired tokens,
    or insufficient permissions.
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            **kwargs,
        )


class RateLimitException(ProviderException):
    """
    Exception raised when provider rate limits are exceeded.

    Includes information about retry timing and limits.
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if retry_after:
            details["retry_after_seconds"] = retry_after
        if limit_type:
            details["limit_type"] = limit_type

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **kwargs,
        )


class TimeoutException(ProviderException):
    """
    Exception raised when operations timeout.

    Includes information about the timeout duration and operation type.
    """

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if timeout_duration:
            details["timeout_duration_seconds"] = timeout_duration
        if operation_type:
            details["operation_type"] = operation_type

        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
            **kwargs,
        )


class QuotaExceededException(ProviderException):
    """
    Exception raised when usage quotas are exceeded.

    Includes information about quota limits and current usage.
    """

    def __init__(
        self,
        message: str,
        quota_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if quota_type:
            details["quota_type"] = quota_type
        if current_usage is not None:
            details["current_usage"] = current_usage
        if quota_limit is not None:
            details["quota_limit"] = quota_limit

        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            details=details,
            **kwargs,
        )


class ProcessorException(AIBlocksException):
    """
    Exception raised during document processing operations.

    Includes information about the processing stage and document details.
    """

    def __init__(
        self,
        message: str,
        processor_name: Optional[str] = None,
        document_id: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if processor_name:
            details["processor_name"] = processor_name
        if document_id:
            details["document_id"] = document_id
        if processing_stage:
            details["processing_stage"] = processing_stage

        super().__init__(
            message=message,
            error_code="PROCESSOR_ERROR",
            details=details,
            **kwargs,
        )


class CacheException(AIBlocksException):
    """
    Exception raised during cache operations.

    Includes information about the cache operation and key details.
    """

    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if cache_key:
            details["cache_key"] = cache_key
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details,
            **kwargs,
        )


class PluginException(AIBlocksException):
    """
    Exception raised during plugin operations.

    Includes information about the plugin and operation details.
    """

    def __init__(
        self,
        message: str,
        plugin_name: Optional[str] = None,
        plugin_version: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if plugin_name:
            details["plugin_name"] = plugin_name
        if plugin_version:
            details["plugin_version"] = plugin_version
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="PLUGIN_ERROR",
            details=details,
            **kwargs,
        )


class DependencyException(AIBlocksException):
    """
    Exception raised when dependencies are missing or incompatible.

    Includes information about the missing dependency and requirements.
    """

    def __init__(
        self,
        message: str,
        dependency_name: Optional[str] = None,
        required_version: Optional[str] = None,
        available_version: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if dependency_name:
            details["dependency_name"] = dependency_name
        if required_version:
            details["required_version"] = required_version
        if available_version:
            details["available_version"] = available_version

        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            details=details,
            **kwargs,
        )


class NetworkException(ProviderException):
    """
    Exception raised for network-related errors.

    Includes information about the network operation and connection details.
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code

        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            details=details,
            **kwargs,
        )


class SerializationException(AIBlocksException):
    """
    Exception raised during serialization/deserialization operations.

    Includes information about the data and format details.
    """

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        format_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if data_type:
            details["data_type"] = data_type
        if format_type:
            details["format_type"] = format_type

        super().__init__(
            message=message,
            error_code="SERIALIZATION_ERROR",
            details=details,
            **kwargs,
        )


# Error code mappings for quick reference
ERROR_CODES = {
    "CONFIG_ERROR": ConfigurationException,
    "VALIDATION_ERROR": ValidationException,
    "PROVIDER_ERROR": ProviderException,
    "AUTH_ERROR": AuthenticationException,
    "RATE_LIMIT_ERROR": RateLimitException,
    "TIMEOUT_ERROR": TimeoutException,
    "QUOTA_EXCEEDED": QuotaExceededException,
    "PROCESSOR_ERROR": ProcessorException,
    "CACHE_ERROR": CacheException,
    "PLUGIN_ERROR": PluginException,
    "DEPENDENCY_ERROR": DependencyException,
    "NETWORK_ERROR": NetworkException,
    "SERIALIZATION_ERROR": SerializationException,
}
