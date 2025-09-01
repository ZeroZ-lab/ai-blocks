"""
Base classes for AI Modular Blocks providers

Provides concrete base implementations that work with the minimal Protocol interfaces.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

from .exceptions import (
    ConfigurationException,
    DependencyException,
    ProviderException,
)
from .types import LLMConfig, LLMResponse, MessageList

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """
    Base implementation for LLM providers.
    
    Provides common functionality and enforces the minimal LLMProvider protocol.
    All concrete providers should inherit from this class.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider configuration
            
        Raises:
            ConfigurationException: If configuration is invalid
            DependencyException: If required dependencies are missing
        """
        self.config = config
        self._initialized = False
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.provider_type = "llm"
        self.logger = logging.getLogger(f"{self.__module__}.{self.__class__.__name__}")
        self._validate_provider_config(config)
        self._setup_client()
        
    def _validate_provider_config(self, config: LLMConfig) -> None:
        """
        Validate provider-specific configuration.
        
        Subclasses should override this to add provider-specific validation.
        
        Args:
            config: Provider configuration to validate
            
        Raises:
            ConfigurationException: If configuration is invalid
        """
        if not config.api_key:
            raise ConfigurationException(
                "API key is required",
                config_key="api_key",
                details={"provider": self.__class__.__name__}
            )
    
    def _setup_client(self) -> None:
        """
        Setup the client connection.
        
        Subclasses should override this to initialize their specific clients.
        """
        pass
    
    async def initialize(self) -> None:
        """
        Initialize the provider.
        
        This method calls the provider-specific _initialize_provider method.
        All providers expect this method to be available.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        await self._initialize_provider()
        self._initialized = True
    
    @abstractmethod
    async def _initialize_provider(self) -> None:
        """
        Provider-specific initialization.
        
        Subclasses must implement this method to set up their clients,
        test connections, etc.
        """
        pass
    
    async def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from a prompt.
        
        This implements the minimal LLMProvider protocol by calling
        the provider's internal _chat_completion_impl method.
        
        Args:
            prompt: Text prompt or list of messages
            **kwargs: Additional provider-specific parameters
            
        Returns:
            dict with at least 'content' key containing the response
            
        Raises:
            ProviderException: If generation fails
        """
        try:
            # Convert prompt to messages if needed
            if isinstance(prompt, str):
                from .types.basic import Message
                messages = [Message(role="user", content=prompt)]
            else:
                # Assume it's already a message list
                messages = prompt
            
            # Get default parameters
            model = kwargs.get('model') or getattr(self.config, 'model', None)
            temperature = kwargs.get('temperature') or getattr(self.config, 'temperature', 0.7)
            max_tokens = kwargs.get('max_tokens') or getattr(self.config, 'max_tokens', None)
            
            # Call provider's implementation
            response = await self._chat_completion_impl(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Standardize response format - handle any return type
            return self._standardize_response(response, model)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise ProviderException(
                f"Failed to generate response: {str(e)}",
                provider_name=getattr(self, 'provider_name', self.__class__.__name__),
                provider_type="llm",
            ) from e
    
    def _standardize_response(self, response: Any, model: str) -> Dict[str, Any]:
        """
        Standardize any response type to the minimal protocol format.
        
        Handles LLMResponse objects, dicts, strings, and error cases.
        """
        try:
            # Case 1: Already a proper LLMResponse object
            if hasattr(response, 'content') and hasattr(response, 'model'):
                return {
                    "content": str(response.content) if response.content else "",
                    "model": getattr(response, 'model', model) or model,
                    "usage": getattr(response, 'usage', {}) or {},
                    "finish_reason": getattr(response, 'finish_reason', 'stop') or 'stop',
                }
            
            # Case 2: Dictionary response (some providers return dict)
            elif isinstance(response, dict):
                return {
                    "content": str(response.get('content', '')),
                    "model": response.get('model', model),
                    "usage": response.get('usage', {}),
                    "finish_reason": response.get('finish_reason', 'stop'),
                }
            
            # Case 3: String response (error case or simple response)
            elif isinstance(response, str):
                return {
                    "content": response,
                    "model": model,
                    "usage": {},
                    "finish_reason": 'stop',
                }
            
            # Case 4: Unexpected type - log and provide fallback
            else:
                logger.warning(f"Unexpected response type {type(response)} from {self.provider_name}")
                return {
                    "content": str(response) if response else "",
                    "model": model,
                    "usage": {},
                    "finish_reason": 'error',
                }
                
        except Exception as e:
            logger.error(f"Failed to standardize response: {e}")
            return {
                "content": f"Response standardization failed: {str(e)}",
                "model": model,
                "usage": {},
                "finish_reason": 'error',
            }
    
    @abstractmethod
    async def _chat_completion_impl(
        self,
        messages: MessageList,
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """
        Provider-specific chat completion implementation.
        
        This is the method that concrete providers must implement.
        
        Args:
            messages: List of chat messages
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object with the completion
        """
        pass
    
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Check if this provider is available (dependencies installed, etc.).
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """
        Get list of supported models for this provider.
        
        Returns:
            List of model names
        """
        return []


class BaseToolProvider(ABC):
    """
    Base implementation for tool providers.
    
    Provides common functionality for tool execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the tool provider."""
        self.config = config or {}
        
    @abstractmethod
    async def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        pass