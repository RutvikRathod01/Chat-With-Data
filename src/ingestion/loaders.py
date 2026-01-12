"""Handles document loading based on file types and enriches metadata."""

import os
import logging
import gradio as gr
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
)


def get_short_source_name(filepath: str) -> str:
    """Get a short display name for the source document.

    Extracts just the filename without the collection prefix.
    e.g., 'doc_collection-1.pdf' -> 'document1.pdf' or original filename if available.
    """
    path = Path(filepath)
    return path.name


def load_docs(files: List[str], original_filenames: Optional[List[str]] = None) -> List[Document]:
    """Auto-detect loader based on file extension and load documents.

    Args:
        files: List of file paths to load
        original_filenames: Optional list of original filenames for source tracking

    Returns:
        List of loaded documents with source metadata
    """
    logging.info("Loading documents")

    loaders = {
        ".pdf": PyPDFLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".docx": UnstructuredWordDocumentLoader,
    }

    docs = []
    for idx, file in enumerate(files):
        ext = os.path.splitext(file)[1].lower()
        if ext not in loaders:
            raise gr.Error(f"❌ Unsupported file extension: {ext}")

        # Determine the source name to use
        if original_filenames and idx < len(original_filenames):
            source_name = original_filenames[idx]
        else:
            source_name = get_short_source_name(file)

        try:
            loader = loaders[ext](file)
            loaded_docs = loader.load()

            # Enhance metadata with document source information
            for doc in loaded_docs:
                if doc.metadata is None:
                    doc.metadata = {}

                # Add original document filename for source tracking
                doc.metadata["document_name"] = source_name
                doc.metadata["document_path"] = file

                # Keep the source field but ensure it points to the readable name
                if "source" not in doc.metadata:
                    doc.metadata["source"] = source_name

            docs.extend(loaded_docs)
            logging.info(
                "Loaded %s pages/sheets from %s (source: %s)",
                len(loaded_docs), file, source_name
            )
        except Exception as exc:  # pylint: disable=broad-except
            logging.error("Error loading %s: %s", file, str(exc))
            raise gr.Error(f"❌ Error loading {os.path.basename(file)}: {str(exc)}") from exc

    return docs


__all__ = ["load_docs", "get_short_source_name"]
