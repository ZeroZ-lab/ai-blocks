"""
Configuration management system for AI Modular Blocks

This module provides a flexible and hierarchical configuration system
that supports environment-specific configurations, validation, and
dynamic configuration updates.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .exceptions import ConfigurationException
from .types import EmbeddingConfig, LLMConfig, VectorStoreConfig

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """System-level configuration settings."""

    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    max_workers: int = 10
    enable_monitoring: bool = True
    enable_caching: bool = True


@dataclass
class SecurityConfig:
    """Security-related configuration settings."""

    encrypt_api_keys: bool = True
    mask_sensitive_logs: bool = True
    enable_ssl_verification: bool = True
    max_request_size_mb: int = 100


@dataclass
class PerformanceConfig:
    """Performance-related configuration settings."""

    connection_timeout: float = 30.0
    read_timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 100
    enable_connection_pooling: bool = True


@dataclass
class CacheConfig:
    """Cache configuration settings."""

    cache_type: str = "memory"  # memory, redis, filesystem
    default_ttl: int = 3600  # seconds
    max_cache_size_mb: int = 100
    cache_key_prefix: str = "ai_blocks"
    redis_url: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""

    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 9090
    log_requests: bool = True
    log_responses: bool = False
    sample_rate: float = 1.0


@dataclass
class ProvidersConfig:
    """Configuration for all providers."""

    llm_providers: Dict[str, LLMConfig] = field(default_factory=dict)
    vector_stores: Dict[str, VectorStoreConfig] = field(default_factory=dict)
    embedding_providers: Dict[str, EmbeddingConfig] = field(default_factory=dict)
    default_llm: Optional[str] = None
    default_vector_store: Optional[str] = None
    default_embedding: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration container."""

    system: SystemConfig = field(default_factory=SystemConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    providers: ProvidersConfig = field(default_factory=ProvidersConfig)


class ConfigManager:
    """
    Configuration manager that handles loading, validation, and access
    to configuration settings from multiple sources.
    """

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        environment: Optional[str] = None,
    ):
        self.config_dir = (
            Path(config_dir) if config_dir else self._get_default_config_dir()
        )
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self._config: Optional[AppConfig] = None
        self._config_files: List[Path] = []

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        # Look for config directory relative to the package
        package_root = Path(__file__).parent.parent.parent
        config_dir = package_root / "config"

        if not config_dir.exists():
            # Create default config directory
            config_dir.mkdir(exist_ok=True)

        return config_dir

    def load_config(self) -> AppConfig:
        """
        Load configuration from multiple sources in order of precedence:
        1. Base configuration
        2. Environment-specific configuration
        3. Local overrides
        4. Environment variables
        """
        try:
            # Start with default configuration
            config_dict = self._load_default_config()

            # Load base configuration
            base_config = self._load_config_file("base.yaml")
            if base_config:
                config_dict = self._merge_configs(config_dict, base_config)

            # Load environment-specific configuration
            env_config = self._load_config_file(f"{self.environment}.yaml")
            if env_config:
                config_dict = self._merge_configs(config_dict, env_config)

            # Load local overrides
            local_config = self._load_config_file("local.yaml")
            if local_config:
                config_dict = self._merge_configs(config_dict, local_config)

            # Apply environment variable overrides
            config_dict = self._apply_env_overrides(config_dict)

            # Create and validate configuration object
            self._config = self._create_config_object(config_dict)
            self._validate_config(self._config)

            logger.info(
                f"Configuration loaded successfully for environment: {self.environment}"
            )
            return self._config

        except Exception as e:
            raise ConfigurationException(
                f"Failed to load configuration: {str(e)}",
                details={
                    "environment": self.environment,
                    "config_dir": str(self.config_dir),
                },
            ) from e

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "system": {
                "environment": self.environment,
                "debug": self.environment in ("development", "testing"),
                "log_level": "DEBUG" if self.environment == "development" else "INFO",
            }
        }

    def _load_config_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration from a YAML file."""
        config_file = self.config_dir / filename

        if not config_file.exists():
            logger.debug(f"Config file not found: {config_file}")
            return None

        try:
            with open(config_file, encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            self._config_files.append(config_file)
            logger.debug(f"Loaded config file: {config_file}")
            return config_data

        except yaml.YAMLError as e:
            raise ConfigurationException(
                f"Invalid YAML in config file: {config_file}",
                details={"file": str(config_file), "yaml_error": str(e)},
            ) from e
        except Exception as e:
            raise ConfigurationException(
                f"Failed to read config file: {config_file}",
                details={"file": str(config_file)},
            ) from e

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Define environment variable mappings
        env_mappings = {
            "AI_BLOCKS_DEBUG": ("system", "debug"),
            "AI_BLOCKS_LOG_LEVEL": ("system", "log_level"),
            "AI_BLOCKS_MAX_WORKERS": ("system", "max_workers"),
            "AI_BLOCKS_CACHE_TYPE": ("cache", "cache_type"),
            "AI_BLOCKS_REDIS_URL": ("cache", "redis_url"),
            "AI_BLOCKS_ENABLE_MONITORING": ("monitoring", "enable_metrics"),
        }

        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)

                if section not in config:
                    config[section] = {}
                config[section][key] = converted_value

        return config

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass

        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _create_config_object(self, config_dict: Dict[str, Any]) -> AppConfig:
        """Create AppConfig object from configuration dictionary."""
        try:
            # Create provider configurations
            providers_config = ProvidersConfig()

            if "providers" in config_dict:
                provider_data = config_dict["providers"]

                # Create LLM provider configurations
                if "llm_providers" in provider_data:
                    for name, llm_config in provider_data["llm_providers"].items():
                        providers_config.llm_providers[name] = LLMConfig(**llm_config)

                # Create vector store configurations
                if "vector_stores" in provider_data:
                    for name, vs_config in provider_data["vector_stores"].items():
                        providers_config.vector_stores[name] = VectorStoreConfig(
                            **vs_config
                        )

                # Create embedding provider configurations
                if "embedding_providers" in provider_data:
                    for name, emb_config in provider_data[
                        "embedding_providers"
                    ].items():
                        providers_config.embedding_providers[name] = EmbeddingConfig(
                            **emb_config
                        )

                # Set defaults
                providers_config.default_llm = provider_data.get("default_llm")
                providers_config.default_vector_store = provider_data.get(
                    "default_vector_store"
                )
                providers_config.default_embedding = provider_data.get(
                    "default_embedding"
                )

            # Create main configuration object
            app_config = AppConfig(
                system=SystemConfig(**config_dict.get("system", {})),
                security=SecurityConfig(**config_dict.get("security", {})),
                performance=PerformanceConfig(**config_dict.get("performance", {})),
                cache=CacheConfig(**config_dict.get("cache", {})),
                monitoring=MonitoringConfig(**config_dict.get("monitoring", {})),
                providers=providers_config,
            )

            return app_config

        except Exception as e:
            raise ConfigurationException(
                f"Failed to create configuration object: {str(e)}",
                details={"config_keys": list(config_dict.keys())},
            ) from e

    def _validate_config(self, config: AppConfig) -> None:
        """Validate the configuration object."""
        validations = [
            (config.system.max_workers > 0, "max_workers must be positive"),
            (
                config.performance.connection_timeout > 0,
                "connection_timeout must be positive",
            ),
            (config.performance.read_timeout > 0, "read_timeout must be positive"),
            (config.performance.max_retries >= 0, "max_retries must be non-negative"),
            (config.cache.default_ttl > 0, "default_ttl must be positive"),
            (config.cache.max_cache_size_mb > 0, "max_cache_size_mb must be positive"),
        ]

        for condition, message in validations:
            if not condition:
                raise ConfigurationException(
                    f"Configuration validation failed: {message}"
                )

        # Validate provider configurations
        self._validate_providers(config.providers)

    def _validate_providers(self, providers: ProvidersConfig) -> None:
        """Validate provider configurations."""
        # Validate default providers exist
        if (
            providers.default_llm
            and providers.default_llm not in providers.llm_providers
        ):
            raise ConfigurationException(
                f"Default LLM provider '{providers.default_llm}' not found in configuration"
            )

        if (
            providers.default_vector_store
            and providers.default_vector_store not in providers.vector_stores
        ):
            raise ConfigurationException(
                f"Default vector store '{providers.default_vector_store}' not found in configuration"
            )

        if (
            providers.default_embedding
            and providers.default_embedding not in providers.embedding_providers
        ):
            raise ConfigurationException(
                f"Default embedding provider '{providers.default_embedding}' not found in configuration"
            )

    def get_config(self) -> AppConfig:
        """Get the current configuration, loading it if necessary."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def reload_config(self) -> AppConfig:
        """Reload configuration from files."""
        self._config = None
        self._config_files.clear()
        return self.load_config()

    def get_loaded_files(self) -> List[Path]:
        """Get list of configuration files that were loaded."""
        return self._config_files.copy()


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return get_config_manager().get_config()


def init_config(
    config_dir: Optional[Union[str, Path]] = None,
    environment: Optional[str] = None,
) -> AppConfig:
    """Initialize the global configuration manager."""
    global _config_manager
    _config_manager = ConfigManager(config_dir=config_dir, environment=environment)
    return _config_manager.load_config()
