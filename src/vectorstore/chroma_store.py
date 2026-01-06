import logging
import os
import shutil
import time
from pathlib import Path

import chromadb
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
                            logging.info("Cleaned up old session directory (%.1f days old): %s", age/86400, item)
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


__all__ = [
    "get_chroma_settings",
    "get_session_store_dir",
    "reset_embedding_store",
    "get_vector_store",
]
