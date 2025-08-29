"""
Base classes for AI Modular Blocks

This module provides base implementations that concrete providers
can inherit from to get common functionality like error handling,
logging, metrics collection, and configuration management.
"""

import logging
import time
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional

from .exceptions import (
    ConfigurationException,
    ProviderException,
    ValidationException,
)
from .interfaces import (
    DocumentProcessor,
    EmbeddingProvider,
    LLMProvider,
    VectorStore,
)
from .types import (
    DocumentList,
    EmbeddingConfig,
    EmbeddingVector,
    LLMConfig,
    LLMResponse,
    MessageList,
    MetadataDict,
    ProviderConfig,
    SearchResult,
    VectorDocument,
    VectorStoreConfig,
)
from .validators import InputValidator

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


class BaseVectorStore(BaseProvider, VectorStore):
    """
    Base implementation for vector stores.

    Provides common functionality like document validation,
    batch processing, and error handling.
    """

    def __init__(self, config: VectorStoreConfig):
        super().__init__(config, "vector_store")
        self.config: VectorStoreConfig = config

    async def upsert(
        self,
        documents: DocumentList,
        namespace: Optional[str] = None,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """Upsert documents with validation and batch processing."""
        # Input validation
        validated_documents = InputValidator.validate_document_list(documents)
        validated_namespace = InputValidator.validate_namespace(namespace)

        if batch_size <= 0:
            raise ValidationException(
                "batch_size must be positive",
                field_name="batch_size",
                field_value=batch_size,
            )

        context = self._log_operation_start(
            "upsert",
            document_count=len(validated_documents),
            namespace=validated_namespace,
            batch_size=batch_size,
        )

        try:
            # Process in batches
            total_processed = 0
            errors = []

            for i in range(0, len(validated_documents), batch_size):
                batch = validated_documents[i : i + batch_size]

                try:
                    result = await self._upsert_batch_impl(batch, validated_namespace)
                    total_processed += len(batch)

                except Exception as e:
                    error_info = {
                        "batch_start": i,
                        "batch_size": len(batch),
                        "error": str(e),
                    }
                    errors.append(error_info)
                    self.logger.error(f"Batch upsert failed: {e}", extra=error_info)

            result = {
                "total_documents": len(validated_documents),
                "processed_count": total_processed,
                "error_count": len(errors),
                "errors": errors,
            }

            self._log_operation_end(context, success=len(errors) == 0)
            return result

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"Document upsert failed: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _upsert_batch_impl(
        self,
        documents: DocumentList,
        namespace: Optional[str],
    ) -> Dict[str, Any]:
        """Subclasses must implement this method."""
        raise NotImplementedError("Subclasses must implement _upsert_batch_impl")

    async def search(
        self,
        query_vector: EmbeddingVector,
        top_k: int = 5,
        filter_dict: Optional[MetadataDict] = None,
        namespace: Optional[str] = None,
        include_metadata: bool = True,
        include_values: bool = False,
    ) -> List[SearchResult]:
        """Search with validation and error handling."""
        # Input validation
        validated_vector = InputValidator.validate_embedding_vector(query_vector)
        validated_top_k = InputValidator.validate_top_k(top_k)
        validated_namespace = InputValidator.validate_namespace(namespace)

        context = self._log_operation_start(
            "search",
            vector_dim=len(validated_vector),
            top_k=validated_top_k,
            namespace=validated_namespace,
            has_filter=filter_dict is not None,
        )

        try:
            results = await self._search_impl(
                validated_vector,
                validated_top_k,
                filter_dict,
                validated_namespace,
                include_metadata,
                include_values,
            )

            self._log_operation_end(context, success=True)
            return results

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"Vector search failed: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _search_impl(
        self,
        query_vector: EmbeddingVector,
        top_k: int,
        filter_dict: Optional[MetadataDict],
        namespace: Optional[str],
        include_metadata: bool,
        include_values: bool,
    ) -> List[SearchResult]:
        """Subclasses must implement this method."""
        raise NotImplementedError("Subclasses must implement _search_impl")


class BaseEmbeddingProvider(BaseProvider, EmbeddingProvider):
    """
    Base implementation for embedding providers.

    Provides common functionality like input validation,
    batch processing, and error handling.
    """

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config, "embedding")
        self.config: EmbeddingConfig = config

    async def embed_text(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[EmbeddingVector]:
        """Generate text embeddings with validation."""
        # Input validation
        if not isinstance(texts, list):
            raise ValidationException(
                "texts must be a list",
                field_name="texts",
                expected_type="list",
                field_value=type(texts).__name__,
            )

        if len(texts) == 0:
            raise ValidationException(
                "texts list cannot be empty",
                field_name="texts",
                field_value="empty list",
            )

        # Sanitize text inputs
        validated_texts = []
        for i, text in enumerate(texts):
            try:
                sanitized_text = InputValidator.sanitize_user_input(text)
                validated_texts.append(sanitized_text)
            except ValidationException as e:
                raise ValidationException(
                    f"Invalid text at index {i}: {e.message}",
                    field_name=f"texts[{i}]",
                    details={"index": i, "original_error": e.message},
                ) from e

        validated_model = model or self.config.model
        if validated_model:
            validated_model = InputValidator.validate_model_name(validated_model)

        context = self._log_operation_start(
            "embed_text",
            text_count=len(validated_texts),
            model=validated_model,
        )

        try:
            embeddings = await self._embed_text_impl(
                validated_texts, validated_model, **kwargs
            )

            self._log_operation_end(context, success=True)
            return embeddings

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"Text embedding failed: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _embed_text_impl(
        self,
        texts: List[str],
        model: Optional[str],
        **kwargs: Any,
    ) -> List[EmbeddingVector]:
        """Subclasses must implement this method."""
        raise NotImplementedError("Subclasses must implement _embed_text_impl")

    async def embed_documents(
        self,
        documents: DocumentList,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> DocumentList:
        """Generate embeddings for documents."""
        # Input validation
        validated_documents = InputValidator.validate_document_list(documents)

        # Extract text content
        texts = [doc.content for doc in validated_documents]

        # Generate embeddings
        embeddings = await self.embed_text(texts, model, **kwargs)

        # Update documents with embeddings
        updated_documents = []
        for doc, embedding in zip(validated_documents, embeddings):
            updated_doc = VectorDocument(
                id=doc.id,
                content=doc.content,
                metadata=doc.metadata,
                embedding=embedding,
                content_type=doc.content_type,
                created_at=doc.created_at,
                updated_at=datetime.utcnow(),
            )
            updated_documents.append(updated_doc)

        return updated_documents


class BaseDocumentProcessor(DocumentProcessor):
    """
    Base implementation for document processors.

    Provides common functionality like logging and error handling.
    """

    def __init__(self, processor_name: str):
        self.processor_name = processor_name
        self.logger = logging.getLogger(f"{__name__}.{processor_name}")

    async def process(self, documents: DocumentList) -> DocumentList:
        """Process documents with validation and error handling."""
        # Input validation
        validated_documents = InputValidator.validate_document_list(documents)

        context = {
            "processor": self.processor_name,
            "document_count": len(validated_documents),
            "start_time": time.time(),
        }

        self.logger.debug(
            f"Processing {len(validated_documents)} documents", extra=context
        )

        try:
            processed_documents = await self._process_impl(validated_documents)

            duration = time.time() - context["start_time"]
            self.logger.debug(
                f"Processed {len(processed_documents)} documents ({duration:.3f}s)",
                extra={
                    **context,
                    "duration": duration,
                    "output_count": len(processed_documents),
                },
            )

            return processed_documents

        except Exception as e:
            duration = time.time() - context["start_time"]
            self.logger.error(
                f"Document processing failed ({duration:.3f}s): {e}",
                extra={**context, "duration": duration, "error": str(e)},
            )
            raise

    async def _process_impl(self, documents: DocumentList) -> DocumentList:
        """Subclasses must implement this method."""
        raise NotImplementedError("Subclasses must implement _process_impl")

    def get_processor_name(self) -> str:
        """Get the processor name."""
        return self.processor_name
