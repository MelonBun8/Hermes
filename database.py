import sqlite3
from datetime import datetime
import threading

class DatabaseManager:
    def __init__(self, db_name='research_chat.db'):
        self.db_name = db_name
        self._local = threading.local()
        self._initialize_db()
    
    def get_conversation_by_id(self, conv_id):
        """Get conversation by ID"""
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT id, query, response FROM conversations WHERE id = ?",
                (conv_id,)
            ).fetchone()

    def _get_connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_name)
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn
        
    def _initialize_db(self):
        """Initialize database with schema migration support"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Check for missing columns
                cursor.execute("PRAGMA table_info(conversations)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'model_used' not in columns:
                    cursor.execute("ALTER TABLE conversations ADD COLUMN model_used TEXT")
                    conn.commit()
            else:
                # Create new table
                cursor.execute('''
                    CREATE TABLE conversations (
                        id INTEGER PRIMARY KEY,
                        query TEXT,
                        response TEXT,
                        timestamp DATETIME,
                        likes INTEGER DEFAULT 0,
                        model_used TEXT
                    )
                ''')
                conn.commit()
                    
    def save_conversation(self, query, response, model_used):
        """Save conversation to database"""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO conversations (query, response, timestamp, model_used) VALUES (?, ?, ?, ?)",
                (query, response, datetime.now(), model_used)
            )
            conn.commit()
            return cur.lastrowid
    
    def get_recent_conversations(self, limit=5):
        """Get recent conversations"""
        with self._get_connection() as conn:
            return conn.execute(
                "SELECT id, query, response FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
    
    def update_likes(self, conv_id):
        """Increment like count"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE conversations SET likes = likes + 1 WHERE id = ?",
                (conv_id,)
            )
            conn.commit()
    
    def delete_conversation(self, conv_id):
        """Delete conversation"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
            conn.commit()
    
    def close_all(self):
        """Close all connections"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()