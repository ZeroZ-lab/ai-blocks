"""
Input validation utilities for AI Modular Blocks

This module provides comprehensive validation functions for various types
of inputs including API keys, messages, documents, and configuration values.
"""

import re
from typing import List, Optional

from .exceptions import ValidationException
from .types import ChatMessage, DocumentList, MessageList, VectorDocument


class InputValidator:
    """
    Comprehensive input validation utility class.

    Provides static methods for validating various types of inputs
    with detailed error messages and security considerations.
    """

    # Regular expressions for validation
    API_KEY_PATTERNS = {
        "openai": re.compile(r"^sk-[a-zA-Z0-9]{48}$"),
        "anthropic": re.compile(r"^sk-[a-zA-Z0-9\-]{10,100}$"),
        "generic": re.compile(r"^[a-zA-Z0-9\-_]{10,200}$"),
    }

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
    NAMESPACE_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]{1,50}$")
    MODEL_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\-_.]{1,100}$")

    @staticmethod
    def validate_api_key(
        api_key: str,
        provider: Optional[str] = None,
        required: bool = True,
    ) -> str:
        """
        Validate API key format and security.

        Args:
            api_key: The API key to validate
            provider: Optional provider name for specific validation
            required: Whether the API key is required

        Returns:
            The validated API key

        Raises:
            ValidationException: If validation fails
        """
        if not api_key and required:
            raise ValidationException(
                "API key is required",
                field_name="api_key",
                field_value=None,
            )

        if not api_key:
            return ""

        if not isinstance(api_key, str):
            raise ValidationException(
                "API key must be a string",
                field_name="api_key",
                expected_type="str",
                field_value=type(api_key).__name__,
            )

        # Check for obviously invalid keys
        if len(api_key.strip()) < 10:
            raise ValidationException(
                "API key too short (minimum 10 characters)",
                field_name="api_key",
                field_value=f"length={len(api_key)}",
            )

        if len(api_key) > 200:
            raise ValidationException(
                "API key too long (maximum 200 characters)",
                field_name="api_key",
                field_value=f"length={len(api_key)}",
            )

        # Provider-specific validation
        if provider:
            pattern = InputValidator.API_KEY_PATTERNS.get(
                provider.lower(), InputValidator.API_KEY_PATTERNS["generic"]
            )
            if not pattern.match(api_key):
                raise ValidationException(
                    f"Invalid API key format for provider '{provider}'",
                    field_name="api_key",
                    field_value="[REDACTED]",
                    details={"provider": provider},
                )

        return api_key.strip()

    @staticmethod
    def validate_chat_message(message: ChatMessage) -> ChatMessage:
        """
        Validate a chat message object.

        Args:
            message: The chat message to validate

        Returns:
            The validated chat message

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(message, ChatMessage):
            raise ValidationException(
                "Message must be a ChatMessage instance",
                field_name="message",
                expected_type="ChatMessage",
                field_value=type(message).__name__,
            )

        # Validate role
        valid_roles = {"user", "assistant", "system", "function", "tool"}
        if message.role not in valid_roles:
            raise ValidationException(
                f"Invalid message role. Must be one of: {', '.join(valid_roles)}",
                field_name="role",
                field_value=message.role,
                details={"valid_roles": list(valid_roles)},
            )

        # Validate content
        if not isinstance(message.content, str):
            raise ValidationException(
                "Message content must be a string",
                field_name="content",
                expected_type="str",
                field_value=type(message.content).__name__,
            )

        if len(message.content.strip()) == 0:
            raise ValidationException(
                "Message content cannot be empty",
                field_name="content",
                field_value="empty string",
            )

        # Check for excessively long content
        if len(message.content) > 100000:  # 100KB limit
            raise ValidationException(
                "Message content too long (maximum 100,000 characters)",
                field_name="content",
                field_value=f"length={len(message.content)}",
            )

        return message

    @staticmethod
    def validate_message_list(messages: MessageList) -> MessageList:
        """
        Validate a list of chat messages.

        Args:
            messages: List of chat messages to validate

        Returns:
            The validated message list

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(messages, list):
            raise ValidationException(
                "Messages must be a list",
                field_name="messages",
                expected_type="list",
                field_value=type(messages).__name__,
            )

        if len(messages) == 0:
            raise ValidationException(
                "Message list cannot be empty",
                field_name="messages",
                field_value="empty list",
            )

        if len(messages) > 1000:  # Reasonable limit
            raise ValidationException(
                "Too many messages (maximum 1000)",
                field_name="messages",
                field_value=f"length={len(messages)}",
            )

        # Validate each message
        validated_messages = []
        for i, message in enumerate(messages):
            try:
                validated_message = InputValidator.validate_chat_message(message)
                validated_messages.append(validated_message)
            except ValidationException as e:
                raise ValidationException(
                    f"Invalid message at index {i}: {e.message}",
                    field_name=f"messages[{i}]",
                    details={"index": i, "original_error": e.message},
                ) from e

        return validated_messages

    @staticmethod
    def validate_vector_document(document: VectorDocument) -> VectorDocument:
        """
        Validate a vector document object.

        Args:
            document: The vector document to validate

        Returns:
            The validated document

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(document, VectorDocument):
            raise ValidationException(
                "Document must be a VectorDocument instance",
                field_name="document",
                expected_type="VectorDocument",
                field_value=type(document).__name__,
            )

        # Validate ID
        if not document.id or not isinstance(document.id, str):
            raise ValidationException(
                "Document ID must be a non-empty string",
                field_name="id",
                field_value=document.id,
            )

        if len(document.id) > 100:
            raise ValidationException(
                "Document ID too long (maximum 100 characters)",
                field_name="id",
                field_value=f"length={len(document.id)}",
            )

        # Validate content
        if not isinstance(document.content, str):
            raise ValidationException(
                "Document content must be a string",
                field_name="content",
                expected_type="str",
                field_value=type(document.content).__name__,
            )

        if len(document.content.strip()) == 0:
            raise ValidationException(
                "Document content cannot be empty",
                field_name="content",
                field_value="empty string",
            )

        # Validate metadata
        if document.metadata is not None:
            if not isinstance(document.metadata, dict):
                raise ValidationException(
                    "Document metadata must be a dictionary",
                    field_name="metadata",
                    expected_type="dict",
                    field_value=type(document.metadata).__name__,
                )

        # Validate embedding if present
        if document.embedding is not None:
            if not isinstance(document.embedding, list):
                raise ValidationException(
                    "Document embedding must be a list",
                    field_name="embedding",
                    expected_type="list",
                    field_value=type(document.embedding).__name__,
                )

            if not all(isinstance(x, (int, float)) for x in document.embedding):
                raise ValidationException(
                    "Document embedding must contain only numbers",
                    field_name="embedding",
                    field_value="contains non-numeric values",
                )

        return document

    @staticmethod
    def validate_document_list(documents: DocumentList) -> DocumentList:
        """
        Validate a list of vector documents.

        Args:
            documents: List of documents to validate

        Returns:
            The validated document list

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(documents, list):
            raise ValidationException(
                "Documents must be a list",
                field_name="documents",
                expected_type="list",
                field_value=type(documents).__name__,
            )

        if len(documents) == 0:
            raise ValidationException(
                "Document list cannot be empty",
                field_name="documents",
                field_value="empty list",
            )

        if len(documents) > 10000:  # Reasonable limit
            raise ValidationException(
                "Too many documents (maximum 10,000)",
                field_name="documents",
                field_value=f"length={len(documents)}",
            )

        # Validate each document
        validated_documents = []
        document_ids = set()

        for i, document in enumerate(documents):
            try:
                validated_doc = InputValidator.validate_vector_document(document)

                # Check for duplicate IDs
                if validated_doc.id in document_ids:
                    raise ValidationException(
                        f"Duplicate document ID: {validated_doc.id}",
                        field_name=f"documents[{i}].id",
                        field_value=validated_doc.id,
                        details={"index": i},
                    )

                document_ids.add(validated_doc.id)
                validated_documents.append(validated_doc)

            except ValidationException as e:
                raise ValidationException(
                    f"Invalid document at index {i}: {e.message}",
                    field_name=f"documents[{i}]",
                    details={"index": i, "original_error": e.message},
                ) from e

        return validated_documents

    @staticmethod
    def validate_model_name(model: str) -> str:
        """
        Validate a model name.

        Args:
            model: The model name to validate

        Returns:
            The validated model name

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(model, str):
            raise ValidationException(
                "Model name must be a string",
                field_name="model",
                expected_type="str",
                field_value=type(model).__name__,
            )

        if len(model.strip()) == 0:
            raise ValidationException(
                "Model name cannot be empty",
                field_name="model",
                field_value="empty string",
            )

        model = model.strip()

        if not InputValidator.MODEL_NAME_PATTERN.match(model):
            raise ValidationException(
                "Invalid model name format (alphanumeric, hyphens, underscores, dots only)",
                field_name="model",
                field_value=model,
            )

        return model

    @staticmethod
    def validate_temperature(temperature: float) -> float:
        """
        Validate temperature parameter.

        Args:
            temperature: The temperature value to validate

        Returns:
            The validated temperature

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(temperature, (int, float)):
            raise ValidationException(
                "Temperature must be a number",
                field_name="temperature",
                expected_type="float",
                field_value=type(temperature).__name__,
            )

        if temperature < 0.0 or temperature > 2.0:
            raise ValidationException(
                "Temperature must be between 0.0 and 2.0",
                field_name="temperature",
                field_value=temperature,
                details={"valid_range": "0.0 to 2.0"},
            )

        return float(temperature)

    @staticmethod
    def validate_top_k(top_k: int) -> int:
        """
        Validate top_k parameter.

        Args:
            top_k: The top_k value to validate

        Returns:
            The validated top_k

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(top_k, int):
            raise ValidationException(
                "top_k must be an integer",
                field_name="top_k",
                expected_type="int",
                field_value=type(top_k).__name__,
            )

        if top_k <= 0:
            raise ValidationException(
                "top_k must be positive",
                field_name="top_k",
                field_value=top_k,
            )

        if top_k > 1000:
            raise ValidationException(
                "top_k too large (maximum 1000)",
                field_name="top_k",
                field_value=top_k,
            )

        return top_k

    @staticmethod
    def validate_namespace(namespace: Optional[str]) -> Optional[str]:
        """
        Validate namespace parameter.

        Args:
            namespace: The namespace to validate

        Returns:
            The validated namespace

        Raises:
            ValidationException: If validation fails
        """
        if namespace is None:
            return None

        if not isinstance(namespace, str):
            raise ValidationException(
                "Namespace must be a string",
                field_name="namespace",
                expected_type="str",
                field_value=type(namespace).__name__,
            )

        namespace = namespace.strip()

        if len(namespace) == 0:
            return None

        if not InputValidator.NAMESPACE_PATTERN.match(namespace):
            raise ValidationException(
                "Invalid namespace format (alphanumeric, hyphens, underscores only, 1-50 chars)",
                field_name="namespace",
                field_value=namespace,
            )

        return namespace

    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize user input text.

        Args:
            text: The text to sanitize
            max_length: Maximum allowed length

        Returns:
            The sanitized text

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(text, str):
            raise ValidationException(
                "Input text must be a string",
                field_name="text",
                expected_type="str",
                field_value=type(text).__name__,
            )

        # Remove potential security threats
        text = text.strip()

        # Check length
        if len(text) > max_length:
            raise ValidationException(
                f"Input text too long (maximum {max_length} characters)",
                field_name="text",
                field_value=f"length={len(text)}",
            )

        # Remove null bytes and other control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

        return text

    @staticmethod
    def validate_embedding_vector(
        vector: List[float], expected_dim: Optional[int] = None
    ) -> List[float]:
        """
        Validate an embedding vector.

        Args:
            vector: The embedding vector to validate
            expected_dim: Expected dimension (optional)

        Returns:
            The validated vector

        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(vector, list):
            raise ValidationException(
                "Embedding vector must be a list",
                field_name="vector",
                expected_type="list",
                field_value=type(vector).__name__,
            )

        if len(vector) == 0:
            raise ValidationException(
                "Embedding vector cannot be empty",
                field_name="vector",
                field_value="empty list",
            )

        if not all(isinstance(x, (int, float)) for x in vector):
            raise ValidationException(
                "Embedding vector must contain only numbers",
                field_name="vector",
                field_value="contains non-numeric values",
            )

        if expected_dim and len(vector) != expected_dim:
            raise ValidationException(
                f"Embedding vector dimension mismatch (expected {expected_dim}, got {len(vector)})",
                field_name="vector",
                field_value=f"dimension={len(vector)}",
                details={
                    "expected_dimension": expected_dim,
                    "actual_dimension": len(vector),
                },
            )

        return vector
