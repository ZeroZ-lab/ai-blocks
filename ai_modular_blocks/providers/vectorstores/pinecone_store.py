"""
Pinecone vector store implementation

This module provides integration with Pinecone vector database for
storing and retrieving vector embeddings with metadata.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import pinecone
    from pinecone import Pinecone, PodSpec, ServerlessSpec

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None
    Pinecone = None
    PodSpec = None
    ServerlessSpec = None

from ...core.base import BaseVectorStore
from ...core.exceptions import (
    AuthenticationException,
    DependencyException,
    ProviderException,
    QuotaExceededException,
    RateLimitException,
    TimeoutException,
)
from ...core.types import (
    DocumentList,
    EmbeddingVector,
    MetadataDict,
    SearchResult,
    VectorDocument,
    VectorStoreConfig,
)


class PineconeVectorStore(BaseVectorStore):
    """
    Pinecone vector store implementation.

    Provides integration with Pinecone's vector database service for
    high-performance vector storage and similarity search operations.
    """

    def __init__(self, config: VectorStoreConfig):
        if not PINECONE_AVAILABLE:
            raise DependencyException(
                "Pinecone package not available. Install with: pip install pinecone-client",
                dependency_name="pinecone-client",
            )

        super().__init__(config)
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.index_name = config.index_name
        self.dimension = getattr(config, "dimension", 1536)
        self.metric = getattr(config, "metric", "cosine")

    async def _initialize_provider(self) -> None:
        """Initialize the Pinecone client and index."""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.config.api_key)

            # Get or create index
            await self._ensure_index_exists()

            # Connect to the index
            self.index = self.pc.Index(self.index_name)

            # Test the connection
            await self._perform_health_check()

        except Exception as e:
            raise ProviderException(
                f"Failed to initialize Pinecone client: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    async def _cleanup_provider(self) -> None:
        """Cleanup Pinecone client resources."""
        self.index = None
        self.pc = None

    async def _perform_health_check(self) -> bool:
        """Perform health check by checking index stats."""
        if not self.index:
            return False

        try:
            stats = self.index.describe_index_stats()
            return stats is not None

        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False

    async def _ensure_index_exists(self) -> None:
        """Ensure the index exists, create if it doesn't."""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]

            if self.index_name not in index_names:
                self.logger.info(f"Creating Pinecone index: {self.index_name}")

                # Determine spec based on configuration
                spec = self._get_index_spec()

                # Create the index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=spec,
                )

                # Wait for index to be ready
                await self._wait_for_index_ready()

        except Exception as e:
            raise ProviderException(
                f"Failed to ensure index exists: {str(e)}",
                provider_name=self.provider_name,
                details={"index_name": self.index_name},
            ) from e

    def _get_index_spec(self):
        """Get the appropriate index spec based on configuration."""
        # Default to serverless for simplicity
        # In production, this should be configurable
        environment = getattr(self.config, "environment", "us-east-1-aws")
        cloud = getattr(self.config, "cloud", "aws")

        return ServerlessSpec(cloud=cloud, region=environment)

    async def _wait_for_index_ready(self, timeout: int = 300) -> None:
        """Wait for index to be ready for operations."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                index_stats = self.pc.describe_index(self.index_name)
                if index_stats.status.ready:
                    self.logger.info(f"Index {self.index_name} is ready")
                    return

                self.logger.debug(f"Waiting for index {self.index_name} to be ready...")
                await asyncio.sleep(5)

            except Exception as e:
                self.logger.warning(f"Error checking index status: {e}")
                await asyncio.sleep(5)

        raise TimeoutException(
            f"Index {self.index_name} not ready within {timeout} seconds",
            provider_name=self.provider_name,
            timeout_duration=timeout,
            operation_type="index_creation",
        )

    async def _upsert_batch_impl(
        self,
        documents: DocumentList,
        namespace: Optional[str],
    ) -> Dict[str, Any]:
        """Upsert a batch of documents to Pinecone."""
        if not self.index:
            await self.initialize()

        try:
            # Convert documents to Pinecone format
            vectors = self._convert_documents_to_pinecone_vectors(documents)

            # Perform upsert
            upsert_response = self.index.upsert(
                vectors=vectors,
                namespace=namespace or "",
            )

            return {
                "upserted_count": upsert_response.upserted_count,
                "batch_size": len(documents),
            }

        except Exception as e:
            if "rate limit" in str(e).lower():
                raise RateLimitException(
                    f"Pinecone rate limit exceeded: {str(e)}",
                    provider_name=self.provider_name,
                ) from e
            elif "quota" in str(e).lower():
                raise QuotaExceededException(
                    f"Pinecone quota exceeded: {str(e)}",
                    provider_name=self.provider_name,
                ) from e
            elif "auth" in str(e).lower():
                raise AuthenticationException(
                    f"Pinecone authentication failed: {str(e)}",
                    provider_name=self.provider_name,
                ) from e
            else:
                raise ProviderException(
                    f"Pinecone upsert failed: {str(e)}",
                    provider_name=self.provider_name,
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
        """Search for similar vectors in Pinecone."""
        if not self.index:
            await self.initialize()

        try:
            # Perform search
            search_response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                namespace=namespace or "",
                include_metadata=include_metadata,
                include_values=include_values,
            )

            # Convert response to SearchResult objects
            results = []
            for match in search_response.matches:
                document = self._convert_pinecone_match_to_document(
                    match, include_values
                )
                result = SearchResult(
                    document=document,
                    score=match.score,
                    metadata={"match_id": match.id} if include_metadata else None,
                )
                results.append(result)

            return results

        except Exception as e:
            if "rate limit" in str(e).lower():
                raise RateLimitException(
                    f"Pinecone rate limit exceeded: {str(e)}",
                    provider_name=self.provider_name,
                ) from e
            elif "auth" in str(e).lower():
                raise AuthenticationException(
                    f"Pinecone authentication failed: {str(e)}",
                    provider_name=self.provider_name,
                ) from e
            else:
                raise ProviderException(
                    f"Pinecone search failed: {str(e)}",
                    provider_name=self.provider_name,
                ) from e

    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete documents by their IDs."""
        if not self.index:
            await self.initialize()

        context = self._log_operation_start(
            "delete",
            id_count=len(ids),
            namespace=namespace,
        )

        try:
            # Perform deletion
            delete_response = self.index.delete(
                ids=ids,
                namespace=namespace or "",
            )

            result = {
                "deleted_count": len(ids),
                "ids": ids,
            }

            self._log_operation_end(context, success=True)
            return result

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"Pinecone delete failed: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    async def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.index:
            await self.initialize()

        try:
            stats = self.index.describe_index_stats()

            result = {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
            }

            # Add namespace-specific stats if available
            if namespace and stats.namespaces and namespace in stats.namespaces:
                ns_stats = stats.namespaces[namespace]
                result.update(
                    {
                        "namespace_vectors": ns_stats.vector_count,
                    }
                )
            elif stats.namespaces:
                result["namespaces"] = {
                    ns: ns_stats.vector_count
                    for ns, ns_stats in stats.namespaces.items()
                }

            return result

        except Exception as e:
            raise ProviderException(
                f"Failed to get Pinecone stats: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    def _convert_documents_to_pinecone_vectors(
        self, documents: DocumentList
    ) -> List[Dict[str, Any]]:
        """Convert VectorDocument objects to Pinecone vector format."""
        vectors = []

        for doc in documents:
            if not doc.embedding:
                raise ProviderException(
                    f"Document {doc.id} missing embedding vector",
                    provider_name=self.provider_name,
                    details={"document_id": doc.id},
                )

            vector = {
                "id": doc.id,
                "values": doc.embedding,
                "metadata": {
                    "content": doc.content,
                    "content_type": doc.content_type.value,
                    "created_at": doc.created_at.isoformat()
                    if doc.created_at
                    else None,
                    "updated_at": doc.updated_at.isoformat()
                    if doc.updated_at
                    else None,
                },
            }

            # Add user metadata
            if doc.metadata:
                vector["metadata"].update(doc.metadata)

            vectors.append(vector)

        return vectors

    def _convert_pinecone_match_to_document(
        self, match, include_values: bool
    ) -> VectorDocument:
        """Convert Pinecone match to VectorDocument."""
        metadata = match.metadata or {}

        # Extract core fields from metadata
        content = metadata.pop("content", "")
        content_type_str = metadata.pop("content_type", "text")
        created_at_str = metadata.pop("created_at", None)
        updated_at_str = metadata.pop("updated_at", None)

        # Parse timestamps
        created_at = None
        updated_at = None
        try:
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
            if updated_at_str:
                updated_at = datetime.fromisoformat(updated_at_str)
        except ValueError:
            pass  # Ignore invalid timestamps

        # Parse content type
        from ...core.types import ContentType

        try:
            content_type = ContentType(content_type_str)
        except ValueError:
            content_type = ContentType.TEXT

        return VectorDocument(
            id=match.id,
            content=content,
            metadata=metadata,  # Remaining metadata
            embedding=match.values if include_values else None,
            content_type=content_type,
            created_at=created_at,
            updated_at=updated_at,
        )

    @classmethod
    def is_available(cls) -> bool:
        """Check if Pinecone provider is available."""
        return PINECONE_AVAILABLE

    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index."""
        if not self.pc:
            raise ProviderException(
                "Pinecone client not initialized",
                provider_name=self.provider_name,
            )

        try:
            index_info = self.pc.describe_index(self.index_name)
            return {
                "name": index_info.name,
                "dimension": index_info.dimension,
                "metric": index_info.metric,
                "status": index_info.status.ready,
                "spec": str(index_info.spec),
            }
        except Exception as e:
            raise ProviderException(
                f"Failed to get index info: {str(e)}",
                provider_name=self.provider_name,
            ) from e
