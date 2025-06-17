
import os
import sqlite3
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional

class EvidenceLinker:
    """
    Professional evidence linking system for legal timeline builder.
    Manages document storage, metadata tracking, and evidence chain of custody.
    """

    def __init__(self, storage_dir: str = "evidence_storage"):
        """
        Initialize evidence linker with storage directory and database.

        Args:
            storage_dir: Directory to store evidence files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize database
        self.db_path = self.storage_dir / "evidence.db"
        self._init_database()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize SQLite database for evidence tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Evidence files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_path TEXT,
                stored_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                upload_time TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Evidence links table (links timeline events to evidence)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                page_number INTEGER,
                text_snippet TEXT,
                confidence REAL,
                created_time TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES evidence_files (id)
            )
        """)

        conn.commit()
        conn.close()

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def store_file(self, uploaded_file, temp_path: str) -> str:
        """
        Store uploaded file securely and track in database.

        Args:
            uploaded_file: Streamlit uploaded file object
            temp_path: Temporary file path

        Returns:
            Stored file path
        """
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(uploaded_file.name).suffix
            safe_filename = f"{timestamp}_{uploaded_file.name.replace(' ', '_')}"
            stored_path = self.storage_dir / safe_filename

            # Copy file to storage directory
            shutil.copy2(temp_path, stored_path)

            # Calculate file hash
            file_hash = self._calculate_file_hash(str(stored_path))
            file_size = stored_path.stat().st_size

            # Store metadata in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO evidence_files 
                (filename, stored_path, file_hash, file_size, mime_type, upload_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                uploaded_file.name,
                str(stored_path),
                file_hash,
                file_size,
                uploaded_file.type or "application/octet-stream",
                datetime.now().isoformat(),
                "{}"  # JSON metadata placeholder
            ))

            conn.commit()
            conn.close()

            self.logger.info(f"File stored successfully: {safe_filename}")
            return str(stored_path)

        except Exception as e:
            self.logger.error(f"Error storing file: {e}")
            raise

    def link_evidence(self, event_id: str, filename: str, page_number: Optional[int] = None, 
                     text_snippet: Optional[str] = None, confidence: float = 1.0) -> str:
        """
        Create evidence link between timeline event and source document.

        Args:
            event_id: Unique identifier for timeline event
            filename: Source filename
            page_number: Page number in document (for PDFs)
            text_snippet: Relevant text snippet
            confidence: Confidence score (0.0 to 1.0)

        Returns:
            Evidence link ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Find file ID
            cursor.execute("SELECT id FROM evidence_files WHERE filename = ?", (filename,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"File not found: {filename}")

            file_id = result[0]

            # Create evidence link
            cursor.execute("""
                INSERT INTO evidence_links 
                (event_id, file_id, page_number, text_snippet, confidence, created_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                file_id,
                page_number,
                text_snippet,
                confidence,
                datetime.now().isoformat()
            ))

            link_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return str(link_id)

        except Exception as e:
            self.logger.error(f"Error creating evidence link: {e}")
            raise

    def get_evidence_for_event(self, event_id: str) -> List[Dict]:
        """
        Get all evidence linked to a specific timeline event.

        Args:
            event_id: Timeline event ID

        Returns:
            List of evidence records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ef.filename, ef.stored_path, ef.file_hash, ef.mime_type,
                       el.page_number, el.text_snippet, el.confidence
                FROM evidence_links el
                JOIN evidence_files ef ON el.file_id = ef.id
                WHERE el.event_id = ?
                ORDER BY el.created_time
            """, (event_id,))

            results = cursor.fetchall()
            conn.close()

            evidence_list = []
            for row in results:
                evidence_list.append({
                    "filename": row[0],
                    "stored_path": row[1],
                    "file_hash": row[2],
                    "mime_type": row[3],
                    "page_number": row[4],
                    "text_snippet": row[5],
                    "confidence": row[6]
                })

            return evidence_list

        except Exception as e:
            self.logger.error(f"Error retrieving evidence: {e}")
            return []

    def get_file_info(self, filename: str) -> Optional[Dict]:
        """
        Get file information from database.

        Args:
            filename: Original filename

        Returns:
            File information dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT filename, stored_path, file_hash, file_size, 
                       mime_type, upload_time, metadata
                FROM evidence_files 
                WHERE filename = ?
            """, (filename,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "filename": result[0],
                    "stored_path": result[1],
                    "file_hash": result[2],
                    "file_size": result[3],
                    "mime_type": result[4],
                    "upload_time": result[5],
                    "metadata": result[6]
                }

            return None

        except Exception as e:
            self.logger.error(f"Error retrieving file info: {e}")
            return None

    def generate_evidence_citation(self, event_id: str) -> str:
        """
        Generate professional evidence citation for timeline event.

        Args:
            event_id: Timeline event ID

        Returns:
            Formatted evidence citation
        """
        evidence_list = self.get_evidence_for_event(event_id)

        if not evidence_list:
            return "No evidence linked"

        citations = []
        for evidence in evidence_list:
            citation = f"[Source: {evidence['filename']}"
            if evidence['page_number']:
                citation += f", Page {evidence['page_number']}"
            citation += f"] (Confidence: {evidence['confidence']:.1%})"
            citations.append(citation)

        return "; ".join(citations)

    def cleanup_storage(self, days_old: int = 30):
        """
        Clean up old evidence files.

        Args:
            days_old: Remove files older than this many days
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Find old files
            cursor.execute("""
                SELECT stored_path FROM evidence_files 
                WHERE upload_time < ?
            """, (cutoff_date.isoformat(),))

            old_files = cursor.fetchall()

            # Delete files and database records
            for file_path in old_files:
                path = Path(file_path[0])
                if path.exists():
                    path.unlink()

            cursor.execute("DELETE FROM evidence_files WHERE upload_time < ?", 
                         (cutoff_date.isoformat(),))

            conn.commit()
            conn.close()

            self.logger.info(f"Cleaned up {len(old_files)} old evidence files")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def verify_file_integrity(self, filename: str) -> bool:
        """
        Verify file integrity using stored hash.

        Args:
            filename: Original filename

        Returns:
            True if file is intact, False otherwise
        """
        try:
            file_info = self.get_file_info(filename)
            if not file_info:
                return False

            stored_path = file_info["stored_path"]
            if not Path(stored_path).exists():
                return False

            current_hash = self._calculate_file_hash(stored_path)
            return current_hash == file_info["file_hash"]

        except Exception as e:
            self.logger.error(f"Error verifying file integrity: {e}")
            return False
