"""
Storage interfaces for AI Modular Blocks

This module contains all storage-related interfaces:
- Vector store operations
- Embedding provider operations
- Document storage and retrieval

Following the "Do One Thing Well" philosophy.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..types import DocumentList, EmbeddingVector, MetadataDict, SearchResult


class VectorStore(ABC):
    """
    Abstract base class for vector storage providers.

    This interface defines standard operations for storing and retrieving
    vector embeddings with associated metadata.
    """

    @abstractmethod
    async def upsert(
        self,
        documents: DocumentList,
        namespace: Optional[str] = None,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Insert or update documents in the vector store.

        Args:
            documents: List of documents to upsert
            namespace: Optional namespace for isolation
            batch_size: Number of documents to process in each batch

        Returns:
            Dictionary with operation metadata (e.g., processed_count, errors)

        Raises:
            ProviderException: When upsert operation fails
            ValidationException: When document validation fails
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: EmbeddingVector,
        top_k: int = 5,
        filter_dict: Optional[MetadataDict] = None,
        namespace: Optional[str] = None,
        include_metadata: bool = True,
        include_values: bool = False,
    ) -> List[SearchResult]:
        """
        Search for similar vectors in the store.

        Args:
            query_vector: Vector to search for similarities
            top_k: Number of top results to return
            filter_dict: Metadata filters to apply
            namespace: Optional namespace to search within
            include_metadata: Whether to include document metadata
            include_values: Whether to include vector values

        Returns:
            List of search results ordered by similarity score

        Raises:
            ProviderException: When search operation fails
            ValidationException: When search parameters are invalid
        """
        pass

    @abstractmethod
    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete
            namespace: Optional namespace to delete from

        Returns:
            Dictionary with deletion metadata (e.g., deleted_count)

        Raises:
            ProviderException: When deletion fails
        """
        pass

    @abstractmethod
    async def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Args:
            namespace: Optional namespace to get stats for

        Returns:
            Dictionary containing store statistics
        """
        pass


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding model providers.

    This interface defines operations for generating vector embeddings
    from text and other content types.
    """

    @abstractmethod
    async def embed_text(
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> List[EmbeddingVector]:
        """
        Generate embeddings for text content.

        Args:
            texts: List of text strings to embed
            model: Optional model identifier
            **kwargs: Provider-specific parameters

        Returns:
            List of embedding vectors corresponding to input texts

        Raises:
            ProviderException: When embedding generation fails
            ValidationException: When input validation fails
        """
        pass

    @abstractmethod
    async def embed_documents(
        self,
        documents: DocumentList,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> DocumentList:
        """
        Generate embeddings for documents and update them in-place.

        Args:
            documents: List of documents to embed
            model: Optional model identifier
            **kwargs: Provider-specific parameters

        Returns:
            List of documents with updated embedding fields

        Raises:
            ProviderException: When embedding generation fails
            ValidationException: When document validation fails
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self, model: Optional[str] = None) -> int:
        """
        Get the dimension of embeddings for a given model.

        Args:
            model: Optional model identifier

        Returns:
            Embedding vector dimension
        """
        pass
