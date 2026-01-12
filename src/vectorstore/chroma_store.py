"""Chroma vector store management for document embeddings."""

import os
import time
import shutil
import logging
import chromadb
from pathlib import Path
from langchain_chroma import Chroma
from config.settings import EMBEDDING_STORE_DIR, embedding_model

_CHROMA_SETTINGS = None
_CURRENT_STORE_DIR: Path | None = None


def get_chroma_settings():
    """Get consistent Chroma settings to avoid 'different settings' errors."""
    global _CHROMA_SETTINGS
    if _CHROMA_SETTINGS is None:
        from chromadb.config import Settings

        _CHROMA_SETTINGS = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
        )
    return _CHROMA_SETTINGS


def get_session_store_dir(file_group_name):
    """Get a unique directory for this session to avoid database conflicts."""
    global _CURRENT_STORE_DIR

    # Just set the session directory without deleting previous ones
    session_dir = EMBEDDING_STORE_DIR / file_group_name

    # Only create if it doesn't exist (reuse existing for same collection)
    if not session_dir.exists():
        session_dir.mkdir(parents=True, exist_ok=True)
        try:
            import stat
            os.chmod(session_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except Exception:
            pass
        logging.info("Created session store directory: %s", session_dir)
    else:
        logging.info("Reusing existing session store directory: %s", session_dir)

    _CURRENT_STORE_DIR = session_dir
    return session_dir


def reset_embedding_store(max_age_hours=168):  # 7 days default
    """Clean up very old session directories (optional cleanup)."""
    if EMBEDDING_STORE_DIR.exists():
        try:
            import gc

            current_time = time.time()
            max_age = max_age_hours * 3600  # Convert hours to seconds
            cleaned_count = 0
            for item in EMBEDDING_STORE_DIR.iterdir():
                if item.is_dir():
                    try:
                        age = current_time - item.stat().st_mtime
                        if age > max_age:
                            gc.collect()
                            time.sleep(0.1)
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned_count += 1
                            logging.info("Cleaned up old session directory (%.1f days old): %s", age / 86400, item)
                    except Exception as exc:  # pylint: disable=broad-except
                        logging.warning("Error cleaning up directory %s: %s", item, str(exc))
            if cleaned_count > 0:
                logging.info("Cleaned up %d old session directories", cleaned_count)
        except Exception as exc:  # pylint: disable=broad-except
            logging.warning("Error in reset_embedding_store: %s", str(exc))


def get_vector_store(splits, collection_name):
    """Create a fresh vector store tied to the current upload."""
    session_store_dir = get_session_store_dir(collection_name)
    client = chromadb.PersistentClient(
        path=str(session_store_dir),
        settings=get_chroma_settings(),
    )

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        client=client,
        collection_name=collection_name,
    )
    logging.info("Vectorstore created for collection: %s in directory: %s", collection_name, session_store_dir)
    return vectorstore


def get_all_chunks_by_metadata(vectorstore, metadata_filter=None, document_filter=None):
    """
    Retrieve all chunks matching metadata filter without TopK limits.
    Used for exhaustive retrieval in counting/enumeration queries.

    Args:
        vectorstore: Chroma vector store instance
        metadata_filter: Dict of metadata filters (e.g., {"contains_projects": True})
        document_filter: Specific document name to filter by (handled in post-processing)

    Returns:
        List of documents with scores (score set to 1.0 for exhaustive retrieval)
    """
    from langchain_core.documents import Document

    try:
        # Use metadata_filter only - document filtering done in post-processing
        filter_to_use = {}
        if metadata_filter:
            filter_to_use.update(metadata_filter)

        logging.info("Exhaustive retrieval with metadata_filter: %s, document_filter: %s",
                     metadata_filter, document_filter)

        # Get all matching documents without k limit
        if filter_to_use:
            results = vectorstore.get(where=filter_to_use)
        else:
            # No metadata filter - get all documents
            results = vectorstore.get()

        # Convert to (Document, score) tuples
        docs_with_scores = []

        if results and 'documents' in results:
            # Log available document names for debugging
            available_docs = set()
            for i, doc_text in enumerate(results['documents']):
                metadata = results['metadatas'][i] if 'metadatas' in results else {}
                doc_name = metadata.get('document_name', 'unknown')
                available_docs.add(doc_name)

                doc = Document(page_content=doc_text, metadata=metadata)
                docs_with_scores.append((doc, 1.0))

            logging.info("Exhaustive retrieval found %d chunks from documents: %s",
                         len(docs_with_scores), list(available_docs)[:10])
        else:
            logging.warning("Exhaustive retrieval got empty results from vectorstore.get()")

        return docs_with_scores

    except Exception as exc:
        logging.error("Error in exhaustive retrieval: %s", str(exc))
        # Fall back to empty list
        return []


__all__ = [
    "get_chroma_settings",
    "get_session_store_dir",
    "reset_embedding_store",
    "get_all_chunks_by_metadata",
    "get_vector_store",
]
