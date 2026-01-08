"""
Chat storage module for persisting conversation history across sessions.
"""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class ChatStorage:
    """Manages persistent storage of chat sessions and messages."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize chat storage with SQLite database."""
        if db_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            db_path = project_root / "src" / "logs" / "chat_history.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logging.info("ChatStorage initialized at %s", self.db_path)

    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table with documents column for multi-doc tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    document_name TEXT NOT NULL,
                    collection_name TEXT NOT NULL,
                    documents TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Add documents column if it doesn't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE sessions ADD COLUMN documents TEXT DEFAULT '[]'")
                logging.info("Added documents column to sessions table")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages 
                ON messages(session_id, timestamp)
            """)
            
            conn.commit()
            logging.info("Database initialized successfully")

    def create_session(
        self, 
        session_id: str, 
        document_name: str, 
        collection_name: str,
        documents: List[str] = None
    ) -> bool:
        """Create a new chat session with document tracking.
        
        Args:
            session_id: Unique session identifier
            document_name: Display name for the session
            collection_name: Vector store collection name
            documents: List of original document filenames
        """
        try:
            documents_json = json.dumps(documents or [])
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, document_name, collection_name, documents)
                    VALUES (?, ?, ?, ?)
                """, (session_id, document_name, collection_name, documents_json))
                conn.commit()
                logging.info(
                    "Created session: %s for document: %s with %d documents", 
                    session_id, document_name, len(documents or [])
                )
                return True
        except sqlite3.IntegrityError:
            logging.warning("Session %s already exists", session_id)
            return False
        except Exception as e:
            logging.error("Error creating session: %s", e)
            return False

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session details by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, document_name, collection_name, documents, created_at, last_updated
                    FROM sessions
                    WHERE session_id = ? AND is_active = 1
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    # Parse documents JSON
                    try:
                        documents = json.loads(row[3]) if row[3] else []
                    except (json.JSONDecodeError, TypeError):
                        documents = []
                    
                    return {
                        "session_id": row[0],
                        "document_name": row[1],
                        "collection_name": row[2],
                        "documents": documents,
                        "created_at": row[4],
                        "last_updated": row[5]
                    }
                return None
        except Exception as e:
            logging.error("Error fetching session: %s", e)
            return None

    def get_all_active_sessions(self) -> List[dict]:
        """Get all active sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, document_name, collection_name, created_at, last_updated
                    FROM sessions
                    WHERE is_active = 1
                    ORDER BY last_updated DESC
                """)
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        "session_id": row[0],
                        "document_name": row[1],
                        "collection_name": row[2],
                        "created_at": row[3],
                        "last_updated": row[4]
                    })
                return sessions
        except Exception as e:
            logging.error("Error fetching sessions: %s", e)
            return []

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Add message
                cursor.execute("""
                    INSERT INTO messages (session_id, role, content)
                    VALUES (?, ?, ?)
                """, (session_id, role, content))
                
                # Update session's last_updated timestamp
                cursor.execute("""
                    UPDATE sessions
                    SET last_updated = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                return True
        except Exception as e:
            logging.error("Error adding message: %s", e)
            return False

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[dict]:
        """Get all messages for a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT role, content, timestamp
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, (session_id,))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2]
                    })
                return messages
        except Exception as e:
            logging.error("Error fetching messages: %s", e)
            return []

    def clear_session_messages(self, session_id: str) -> bool:
        """Clear all messages for a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM messages
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
                logging.info("Cleared messages for session: %s", session_id)
                return True
        except Exception as e:
            logging.error("Error clearing messages: %s", e)
            return False

    def delete_session(self, session_id: str) -> bool:
        """Soft delete a session (mark as inactive)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions
                    SET is_active = 0
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
                logging.info("Deleted session: %s", session_id)
                return True
        except Exception as e:
            logging.error("Error deleting session: %s", e)
            return False

    def update_session_timestamp(self, session_id: str) -> bool:
        """Update the last_updated timestamp for a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions
                    SET last_updated = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (session_id,))
                conn.commit()
                return True
        except Exception as e:
            logging.error("Error updating session timestamp: %s", e)
            return False


# Global instance
_chat_storage = None


def get_chat_storage() -> ChatStorage:
    """Get or create the global chat storage instance."""
    global _chat_storage
    if _chat_storage is None:
        _chat_storage = ChatStorage()
    return _chat_storage


__all__ = ["ChatStorage", "get_chat_storage"]
