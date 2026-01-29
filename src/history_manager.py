"""
History Manager - SQLite based persistent storage for analysis history.
Supports semantic caching via embedding similarity.
"""
import sqlite3
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data" / "history.db"

# Semantic cache threshold (0.85 = 85% similar)
SEMANTIC_CACHE_THRESHOLD = 0.85


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class HistoryManager:
    def __init__(self):
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database table and migrate schema."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create table if not exists with all columns
        c.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id TEXT,
                user_idea TEXT,
                result_json TEXT,
                risk_level TEXT,
                score INTEGER,
                embedding_json TEXT
            )
        ''')
        
        # Migration: Check existing columns
        c.execute("PRAGMA table_info(analysis_history)")
        columns = [info[1] for info in c.fetchall()]
        
        if 'user_id' not in columns:
            logger.info("Migrating DB: Adding user_id column...")
            try:
                c.execute("ALTER TABLE analysis_history ADD COLUMN user_id TEXT")
                c.execute("UPDATE analysis_history SET user_id = 'legacy_user'")
            except Exception as e:
                logger.error(f"Migration failed: {e}")
        
        if 'embedding_json' not in columns:
            logger.info("Migrating DB: Adding embedding_json column for semantic cache...")
            try:
                c.execute("ALTER TABLE analysis_history ADD COLUMN embedding_json TEXT")
            except Exception as e:
                logger.error(f"Migration failed: {e}")
            
        conn.commit()
        conn.close()
        
    def save_analysis(self, result: Dict, user_id: str, embedding: Optional[np.ndarray] = None):
        """Save analysis result to DB with user_id and optional embedding."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            analysis = result.get('analysis', {})
            risk = analysis.get('infringement', {}).get('risk_level', 'unknown')
            score = analysis.get('similarity', {}).get('score', 0)
            
            # Serialize embedding if provided
            embedding_json = None
            if embedding is not None:
                embedding_json = json.dumps(embedding.tolist())
            
            c.execute('''
                INSERT INTO analysis_history (timestamp, user_id, user_idea, result_json, risk_level, score, embedding_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('timestamp', datetime.now().isoformat()),
                user_id,
                result.get('user_idea', ''),
                json.dumps(result, ensure_ascii=False),
                risk,
                score,
                embedding_json
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved analysis with embedding: {embedding is not None}")
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
            
    def load_recent(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Load recent analysis history for specific user."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''
                SELECT result_json FROM analysis_history 
                WHERE user_id = ?
                ORDER BY id DESC LIMIT ?
            ''', (user_id, limit))
            
            rows = c.fetchall()
            history = [json.loads(row['result_json']) for row in rows]
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    def find_cached_result(self, user_idea: str, user_id: str) -> Optional[Dict]:
        """Find the most recent identical query in history (exact match)."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''
                SELECT result_json FROM analysis_history 
                WHERE user_id = ? AND user_idea = ?
                ORDER BY id DESC LIMIT 1
            ''', (user_id, user_idea))
            
            row = c.fetchone()
            conn.close()
            
            if row:
                return json.loads(row['result_json'])
            return None
        except Exception as e:
            logger.error(f"Failed to check cache: {e}")
            return None

    def find_cached_result_semantic(
        self, 
        user_idea: str, 
        user_id: str, 
        query_embedding: np.ndarray,
        threshold: float = SEMANTIC_CACHE_THRESHOLD
    ) -> Tuple[Optional[Dict], float]:
        """
        Find semantically similar cached result using embedding similarity.
        
        Args:
            user_idea: Current query text
            user_id: User identifier
            query_embedding: Embedding vector of current query
            threshold: Minimum similarity threshold (default 0.85)
        
        Returns:
            Tuple of (cached_result, similarity_score) or (None, 0.0)
        """
        try:
            # First try exact match (fastest)
            exact_match = self.find_cached_result(user_idea, user_id)
            if exact_match:
                logger.info("Cache HIT: Exact match found")
                return exact_match, 1.0
            
            # Otherwise, search by semantic similarity
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # Load recent entries with embeddings
            c.execute('''
                SELECT result_json, embedding_json, user_idea FROM analysis_history 
                WHERE user_id = ? AND embedding_json IS NOT NULL
                ORDER BY id DESC LIMIT 50
            ''', (user_id,))
            
            rows = c.fetchall()
            conn.close()
            
            if not rows:
                logger.info("Semantic cache: No cached embeddings found")
                return None, 0.0
            
            # Find best match
            best_match = None
            best_score = 0.0
            best_idea = ""
            
            for row in rows:
                try:
                    cached_embedding = np.array(json.loads(row['embedding_json']))
                    similarity = cosine_similarity(query_embedding, cached_embedding)
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = json.loads(row['result_json'])
                        best_idea = row['user_idea']
                except Exception as e:
                    logger.warning(f"Error parsing cached embedding: {e}")
                    continue
            
            # Check threshold
            if best_score >= threshold:
                logger.info(f"Semantic cache HIT: {best_score:.2%} similar to '{best_idea[:30]}...'")
                return best_match, best_score
            else:
                logger.info(f"Semantic cache MISS: Best similarity {best_score:.2%} < threshold {threshold:.0%}")
                return None, best_score
                
        except Exception as e:
            logger.error(f"Failed to check semantic cache: {e}")
            return None, 0.0

    def clear_history(self, user_id: str):
        """Delete history for specific user."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM analysis_history WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
