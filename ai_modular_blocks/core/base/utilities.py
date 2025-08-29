"""
Utility base provider classes for AI Modular Blocks

This module provides base classes for utility components:
- BaseDocumentProcessor for document processing operations

Following the "Do One Thing Well" philosophy.
"""

import logging
import time

from ..interfaces import DocumentProcessor
from ..types import DocumentList
from ..validators import InputValidator


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
