"""
ChromaDB vector store implementation

This module provides integration with ChromaDB for local and distributed
vector storage and retrieval operations.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import chromadb
    from chromadb.api.types import GetResult, QueryResult
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None
    Settings = None
    QueryResult = None
    GetResult = None

from ...core.base import BaseVectorStore
from ...core.exceptions import (
    DependencyException,
    ProviderException,
)
from ...core.types import (
    DocumentList,
    EmbeddingVector,
    MetadataDict,
    SearchResult,
    VectorDocument,
    VectorStoreConfig,
)


class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB vector store implementation.

    Provides integration with ChromaDB for local or remote vector storage
    with support for collections, metadata filtering, and similarity search.
    """

    def __init__(self, config: VectorStoreConfig):
        if not CHROMA_AVAILABLE:
            raise DependencyException(
                "ChromaDB package not available. Install with: pip install chromadb",
                dependency_name="chromadb",
            )

        super().__init__(config)
        self.client = None
        self.collection = None
        self.collection_name = config.index_name  # Using index_name as collection name
        self.dimension = getattr(config, "dimension", 1536)
        self.metric = getattr(config, "metric", "cosine")

        # ChromaDB connection settings
        self.host = getattr(config, "host", "localhost")
        self.port = getattr(config, "port", 8000)
        self.persist_directory = getattr(config, "persist_directory", None)
        self.is_persistent = getattr(config, "is_persistent", True)

    async def _initialize_provider(self) -> None:
        """Initialize the ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client
            if self.persist_directory:
                # Persistent client (local storage)
                self.client = chromadb.PersistentClient(path=self.persist_directory)
            elif hasattr(chromadb, "HttpClient") and not self._is_local_mode():
                # HTTP client (remote ChromaDB server)
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                )
            else:
                # In-memory client (for testing/development)
                self.client = chromadb.EphemeralClient()

            # Get or create collection
            await self._ensure_collection_exists()

            # Test the connection
            await self._perform_health_check()

        except Exception as e:
            raise ProviderException(
                f"Failed to initialize ChromaDB client: {str(e)}",
                provider_name=self.provider_name,
                provider_type=self.provider_type,
            ) from e

    def _is_local_mode(self) -> bool:
        """Check if we should use local mode."""
        return self.host == "localhost" and not hasattr(self.config, "api_key")

    async def _cleanup_provider(self) -> None:
        """Cleanup ChromaDB client resources."""
        self.collection = None
        self.client = None

    async def _perform_health_check(self) -> bool:
        """Perform health check by checking collection access."""
        if not self.collection:
            return False

        try:
            # Try to get collection count
            count = self.collection.count()
            return True

        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False

    async def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create if it doesn't."""
        try:
            # Check if collection exists
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                )
                self.logger.debug(f"Using existing collection: {self.collection_name}")

            except Exception:
                # Collection doesn't exist, create it
                self.logger.info(
                    f"Creating ChromaDB collection: {self.collection_name}"
                )

                # Determine distance function based on metric
                distance_function = self._get_distance_function()

                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": distance_function},
                )

        except Exception as e:
            raise ProviderException(
                f"Failed to ensure collection exists: {str(e)}",
                provider_name=self.provider_name,
                details={"collection_name": self.collection_name},
            ) from e

    def _get_distance_function(self) -> str:
        """Get ChromaDB distance function based on metric."""
        metric_mapping = {
            "cosine": "cosine",
            "euclidean": "l2",
            "manhattan": "l1",
            "dot": "ip",  # inner product
        }
        return metric_mapping.get(self.metric, "cosine")

    async def _upsert_batch_impl(
        self,
        documents: DocumentList,
        namespace: Optional[str],
    ) -> Dict[str, Any]:
        """Upsert a batch of documents to ChromaDB."""
        if not self.collection:
            await self.initialize()

        try:
            # Convert documents to ChromaDB format
            ids, embeddings, metadatas, documents_text = (
                self._convert_documents_to_chroma_format(documents, namespace)
            )

            # Perform upsert
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text,
            )

            return {
                "upserted_count": len(documents),
                "batch_size": len(documents),
            }

        except Exception as e:
            raise ProviderException(
                f"ChromaDB upsert failed: {str(e)}",
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
        """Search for similar vectors in ChromaDB."""
        if not self.collection:
            await self.initialize()

        try:
            # Prepare filter
            where_filter = self._prepare_filter(filter_dict, namespace)

            # Perform search
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
                + (["embeddings"] if include_values else []),
            )

            # Convert response to SearchResult objects
            search_results = []

            if results["ids"] and results["ids"][0]:  # Check if we have results
                ids = results["ids"][0]
                distances = results["distances"][0]
                documents_text = (
                    results["documents"][0]
                    if results["documents"]
                    else [None] * len(ids)
                )
                metadatas = (
                    results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)
                )
                embeddings = (
                    results["embeddings"][0]
                    if results.get("embeddings")
                    else [None] * len(ids)
                )

                for i, doc_id in enumerate(ids):
                    document = self._convert_chroma_result_to_document(
                        doc_id,
                        documents_text[i],
                        metadatas[i],
                        embeddings[i] if include_values else None,
                    )

                    # Convert distance to similarity score (ChromaDB returns distances)
                    score = self._distance_to_score(distances[i])

                    result = SearchResult(
                        document=document,
                        score=score,
                        metadata={"distance": distances[i]}
                        if include_metadata
                        else None,
                    )
                    search_results.append(result)

            return search_results

        except Exception as e:
            raise ProviderException(
                f"ChromaDB search failed: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    async def delete(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete documents by their IDs."""
        if not self.collection:
            await self.initialize()

        context = self._log_operation_start(
            "delete",
            id_count=len(ids),
            namespace=namespace,
        )

        try:
            # Add namespace prefix if needed
            prefixed_ids = [
                self._add_namespace_prefix(doc_id, namespace) for doc_id in ids
            ]

            # Perform deletion
            self.collection.delete(ids=prefixed_ids)

            result = {
                "deleted_count": len(ids),
                "ids": ids,
            }

            self._log_operation_end(context, success=True)
            return result

        except Exception as e:
            self._log_operation_end(context, success=False, error=e)
            raise ProviderException(
                f"ChromaDB delete failed: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    async def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.collection:
            await self.initialize()

        try:
            total_count = self.collection.count()

            result = {
                "total_vectors": total_count,
                "collection_name": self.collection_name,
            }

            # Get namespace-specific count if requested
            if namespace:
                where_filter = {"namespace": namespace}
                namespace_results = self.collection.get(
                    where=where_filter,
                    include=["metadatas"],
                )
                result["namespace_vectors"] = (
                    len(namespace_results["ids"]) if namespace_results["ids"] else 0
                )

            return result

        except Exception as e:
            raise ProviderException(
                f"Failed to get ChromaDB stats: {str(e)}",
                provider_name=self.provider_name,
            ) from e

    def _convert_documents_to_chroma_format(
        self, documents: DocumentList, namespace: Optional[str]
    ) -> tuple[List[str], List[List[float]], List[Dict[str, Any]], List[str]]:
        """Convert VectorDocument objects to ChromaDB format."""
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []

        for doc in documents:
            if not doc.embedding:
                raise ProviderException(
                    f"Document {doc.id} missing embedding vector",
                    provider_name=self.provider_name,
                    details={"document_id": doc.id},
                )

            # Add namespace prefix to ID if needed
            doc_id = self._add_namespace_prefix(doc.id, namespace)
            ids.append(doc_id)

            embeddings.append(doc.embedding)
            documents_text.append(doc.content)

            # Prepare metadata
            metadata = {
                "content_type": doc.content_type.value,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            }

            # Add namespace to metadata for filtering
            if namespace:
                metadata["namespace"] = namespace

            # Add user metadata
            if doc.metadata:
                # ChromaDB has restrictions on metadata types
                for key, value in doc.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    else:
                        # Convert complex types to JSON strings
                        metadata[key] = json.dumps(value)

            metadatas.append(metadata)

        return ids, embeddings, metadatas, documents_text

    def _convert_chroma_result_to_document(
        self,
        doc_id: str,
        document_text: Optional[str],
        metadata: Dict[str, Any],
        embedding: Optional[List[float]],
    ) -> VectorDocument:
        """Convert ChromaDB result to VectorDocument."""
        # Remove namespace prefix from ID
        original_id = self._remove_namespace_prefix(doc_id)

        # Extract core fields from metadata
        content_type_str = metadata.pop("content_type", "text")
        created_at_str = metadata.pop("created_at", None)
        updated_at_str = metadata.pop("updated_at", None)
        namespace = metadata.pop(
            "namespace", None
        )  # Remove namespace from user metadata

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

        # Parse JSON strings back to original types
        parsed_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, str) and value.startswith(("{", "[")):
                try:
                    parsed_metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    parsed_metadata[key] = value
            else:
                parsed_metadata[key] = value

        return VectorDocument(
            id=original_id,
            content=document_text or "",
            metadata=parsed_metadata,
            embedding=embedding,
            content_type=content_type,
            created_at=created_at,
            updated_at=updated_at,
        )

    def _add_namespace_prefix(self, doc_id: str, namespace: Optional[str]) -> str:
        """Add namespace prefix to document ID."""
        if namespace:
            return f"{namespace}::{doc_id}"
        return doc_id

    def _remove_namespace_prefix(self, doc_id: str) -> str:
        """Remove namespace prefix from document ID."""
        if "::" in doc_id:
            return doc_id.split("::", 1)[1]
        return doc_id

    def _prepare_filter(
        self, filter_dict: Optional[MetadataDict], namespace: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Prepare filter for ChromaDB query."""
        where_filter = {}

        # Add namespace filter
        if namespace:
            where_filter["namespace"] = namespace

        # Add user filters
        if filter_dict:
            where_filter.update(filter_dict)

        return where_filter if where_filter else None

    def _distance_to_score(self, distance: float) -> float:
        """Convert distance to similarity score."""
        # ChromaDB returns distances, we want similarity scores (higher = more similar)
        if self.metric == "cosine":
            # Cosine distance is 1 - cosine_similarity, so similarity is 1 - distance
            return max(0.0, 1.0 - distance)
        elif self.metric in ["euclidean", "l2"]:
            # For Euclidean distance, convert to similarity score
            return 1.0 / (1.0 + distance)
        else:
            # For other metrics, use inverse relationship
            return 1.0 / (1.0 + distance)

    @classmethod
    def is_available(cls) -> bool:
        """Check if ChromaDB provider is available."""
        return CHROMA_AVAILABLE

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        if not self.collection:
            raise ProviderException(
                "ChromaDB collection not initialized",
                provider_name=self.provider_name,
            )

        try:
            count = self.collection.count()
            metadata = self.collection.metadata or {}

            return {
                "name": self.collection_name,
                "count": count,
                "metadata": metadata,
            }
        except Exception as e:
            raise ProviderException(
                f"Failed to get collection info: {str(e)}",
                provider_name=self.provider_name,
            ) from e
