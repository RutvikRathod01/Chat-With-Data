from dataclasses import dataclass, field
from typing import Optional

from langchain_chroma import Chroma


@dataclass
class RagSession:
    rag_chain: object
    vectorstore: Chroma
    sparse_index: "SparseIndex"
    session_id: Optional[str] = None
    document_name: Optional[str] = None
    collection_name: Optional[str] = None


__all__ = ["RagSession"]
