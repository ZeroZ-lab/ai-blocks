"""
Storage base provider classes for AI Modular Blocks

This module provides base classes for storage-related providers:
- BaseVectorStore for vector storage operations
- BaseEmbeddingProvider for embedding generation

Following the "Do One Thing Well" philosophy.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .provider import BaseProvider
from ..exceptions import ProviderException, ValidationException
from ..interfaces import EmbeddingProvider, VectorStore
from ..types import (
    DocumentList,
    EmbeddingConfig,
    EmbeddingVector,
    MetadataDict,
    SearchResult,
    VectorDocument,
    VectorStoreConfig,
)
from ..validators import InputValidator


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
