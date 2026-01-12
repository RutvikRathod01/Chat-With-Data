"""Handles file ingestion, validation, and storage for uploaded documents."""

import os
import re
import shutil
import gradio as gr
from pathlib import Path
from typing import List, Tuple
from config.settings import DATA_DIR, IST


def get_clean_filename(filepath: str) -> str:
    """Extract clean filename without extension and special characters."""
    filename = Path(filepath).stem
    # Remove special characters and replace spaces with underscores
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
    # Remove multiple underscores
    clean_name = re.sub(r'_+', '_', clean_name)
    # Trim underscores from ends
    clean_name = clean_name.strip('_')
    return clean_name or "document"


def get_original_filename(filepath: str) -> str:
    """Extract the original filename with extension."""
    return Path(filepath).name


def get_unique_document_name(uploaded_files) -> str:
    """Generate a unique document name based on uploaded file names."""
    if not uploaded_files:
        return "document"

    # Get base name from first file
    first_file = uploaded_files[0]
    base_name = get_clean_filename(first_file.name)

    # If multiple files, append count
    if len(uploaded_files) > 1:
        base_name = f"{base_name}_and_{len(uploaded_files) - 1}_more"

    # Check for existing sessions with same name
    from models.chat_storage import get_chat_storage
    storage = get_chat_storage()
    existing_sessions = storage.get_all_active_sessions()
    existing_names = {s['document_name'] for s in existing_sessions}

    # Handle duplicates
    final_name = base_name
    counter = 1
    while final_name in existing_names:
        final_name = f"{base_name}_{counter}"
        counter += 1

    return final_name


def validate_and_save_files(uploaded_files) -> Tuple[List[str], str, str, List[str]]:
    """Validate and save uploaded files to the data directory.

    Returns:
        Tuple of (saved_files, collection_name, document_name, original_filenames)
        - saved_files: List of paths to saved files
        - collection_name: Name for the vector store collection
        - document_name: Display name for the session
        - original_filenames: List of original document filenames (for source tracking)
    """
    if not uploaded_files:
        raise gr.Error("⚠️ Please upload at least one file.")

    # Generate clean document name and collection name
    document_name = get_unique_document_name(uploaded_files)
    collection_name = document_name  # Use same name for collection

    saved_files = []
    original_filenames = []  # Track original filenames for source references

    for idx, file in enumerate(uploaded_files, start=1):
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in [".pdf", ".docx", ".xlsx"]:
            raise gr.Error(f"❌ Unsupported file type: {ext}. Only PDF, DOCX, XLSX are allowed.")

        # Get original filename
        original_name = get_original_filename(file.name)
        original_filenames.append(original_name)

        # Use collection name for saving files
        save_path = DATA_DIR / f"{collection_name}-{idx}{ext}"
        try:
            shutil.copyfile(file.name, str(save_path))
            saved_files.append(str(save_path))
        except Exception as exc:  # pylint: disable=broad-except
            raise gr.Error(f"❌ Error saving file: {str(exc)}") from exc

    return saved_files, collection_name, document_name, original_filenames


__all__ = [
    "get_clean_filename",
    "get_original_filename",
    "get_unique_document_name",
    "validate_and_save_files"
]
