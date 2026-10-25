"""
Database management for JARVIS continuous memory system using SQLite.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DatabaseManager:
    """Manages SQLite database for facts, episodes, lessons, and dynamic skills."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        """Create tables, FTS virtual tables, and synchronization triggers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Semantic Facts Table (User preferences, hardware info, project context, habits)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,       -- 'preference', 'user_fact', 'project_context', 'system', 'habit'
                    key TEXT NOT NULL,            -- e.g. 'preferred_editor', 'coding_style'
                    value TEXT NOT NULL,          -- e.g. 'neovim', 'type hints with google docstrings'
                    confidence REAL DEFAULT 1.0,  -- 0.0 to 1.0
                    source TEXT DEFAULT 'direct', -- 'direct', 'inferred', 'reflection'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                )
            """)

            # 2. Episodic Memory Table (Past interactions, actions taken, outcomes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_prompt TEXT NOT NULL,
                    plan TEXT,
                    steps_json TEXT,              -- JSON list of actions/tools executed
                    result TEXT,                  -- Final response or output
                    success INTEGER DEFAULT 1,    -- 1 if succeeded, 0 if failed
                    feedback TEXT,                -- User feedback or correction if any
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Lessons Learned Table (Continuous self-correction & rule evolution)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons_learned (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_pattern TEXT NOT NULL,-- Keywords or context where this rule applies
                    mistake TEXT NOT NULL,        -- What was done wrong previously
                    lesson TEXT NOT NULL,         -- Rule to adhere to in the future
                    solution TEXT,                -- Suggested correct action or approach
                    tags TEXT,                    -- Comma-separated tags (e.g. 'bash,docker,formatting')
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Skills Index Table (Dynamic Python tools generated and maintained by JARVIS)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    code_path TEXT NOT NULL,
                    code_content TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """)

            # 5. Full text search (FTS5) virtual tables
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                    category, key, value,
                    content='semantic_facts',
                    content_rowid='id'
                )
            """)

            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
                    trigger_pattern, mistake, lesson, solution, tags,
                    content='lessons_learned',
                    content_rowid='id'
                )
            """)

            # 6. Automatic Triggers for FTS5 Synchronization
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON semantic_facts BEGIN
                    INSERT INTO facts_fts(rowid, category, key, value) VALUES (new.id, new.category, new.key, new.value);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON semantic_facts BEGIN
                    INSERT INTO facts_fts(facts_fts, rowid, category, key, value) VALUES('delete', old.id, old.category, old.key, old.value);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON semantic_facts BEGIN
                    INSERT INTO facts_fts(facts_fts, rowid, category, key, value) VALUES('delete', old.id, old.category, old.key, old.value);
                    INSERT INTO facts_fts(rowid, category, key, value) VALUES (new.id, new.category, new.key, new.value);
                END;
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons_learned BEGIN
                    INSERT INTO lessons_fts(rowid, trigger_pattern, mistake, lesson, solution, tags) VALUES (new.id, new.trigger_pattern, new.mistake, new.lesson, new.solution, new.tags);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons_learned BEGIN
                    INSERT INTO lessons_fts(lessons_fts, rowid, trigger_pattern, mistake, lesson, solution, tags) VALUES('delete', old.id, old.trigger_pattern, old.mistake, old.lesson, old.solution, old.tags);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons_learned BEGIN
                    INSERT INTO lessons_fts(lessons_fts, rowid, trigger_pattern, mistake, lesson, solution, tags) VALUES('delete', old.id, old.trigger_pattern, old.mistake, old.lesson, old.solution, old.tags);
                    INSERT INTO lessons_fts(rowid, trigger_pattern, mistake, lesson, solution, tags) VALUES (new.id, new.trigger_pattern, new.mistake, new.lesson, new.solution, new.tags);
                END;
            """)

            conn.commit()

    # --- Semantic Facts Methods ---

    def upsert_fact(self, category: str, key: str, value: str, confidence: float = 1.0, source: str = "direct") -> int:
        """Insert or update a semantic fact/preference."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO semantic_facts (category, key, value, confidence, source, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(category, key) DO UPDATE SET
                    value = excluded.value,
                    confidence = excluded.confidence,
                    source = excluded.source,
                    updated_at = CURRENT_TIMESTAMP
            """, (category, key, value, confidence, source))
            row_id = cursor.lastrowid
            conn.commit()
            return row_id

    def get_facts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retrieve all facts belonging to a specific category."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM semantic_facts WHERE category = ? ORDER BY updated_at DESC", (category,))
            return [dict(row) for row in cursor.fetchall()]

    def search_facts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search facts using FTS or keyword matching."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            clean_query = "".join([c if c.isalnum() or c.isspace() else " " for c in query]).strip()
            if not clean_query:
                cursor.execute("SELECT * FROM semantic_facts ORDER BY updated_at DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]

            fts_tokens = " OR ".join(clean_query.split())
            try:
                cursor.execute("""
                    SELECT f.* FROM semantic_facts f
                    JOIN facts_fts ON facts_fts.rowid = f.id
                    WHERE facts_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (fts_tokens, limit))
                results = [dict(row) for row in cursor.fetchall()]
                if results:
                    return results
            except sqlite3.OperationalError:
                pass

            # Fallback to LIKE query
            cursor.execute("""
                SELECT * FROM semantic_facts
                WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
                ORDER BY updated_at DESC LIMIT ?
            """, (f"%{clean_query}%", f"%{clean_query}%", f"%{clean_query}%", limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Get all stored semantic facts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM semantic_facts ORDER BY category, key")
            return [dict(row) for row in cursor.fetchall()]

    def delete_fact(self, category: str, key: str) -> bool:
        """Delete a fact."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM semantic_facts WHERE category = ? AND key = ?", (category, key))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    # --- Episodic Memory Methods ---

    def log_episode(self, session_id: str, user_prompt: str, plan: Optional[str],
                    steps: List[Dict[str, Any]], result: str, success: bool = True,
                    feedback: Optional[str] = None) -> int:
        """Store an episode into episodic memory."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_memory (session_id, user_prompt, plan, steps_json, result, success, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_prompt,
                plan or "",
                json.dumps(steps, default=str),
                result,
                1 if success else 0,
                feedback or ""
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_episodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch the most recent episodes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM episodic_memory ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            episodes = []
            for r in rows:
                item = dict(r)
                item["steps"] = json.loads(item.get("steps_json") or "[]")
                episodes.append(item)
            return episodes

    # --- Lessons Learned Methods ---

    def add_lesson(self, trigger_pattern: str, mistake: str, lesson: str,
                   solution: Optional[str] = None, tags: str = "") -> int:
        """Add a newly learned self-correction lesson/rule."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lessons_learned (trigger_pattern, mistake, lesson, solution, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (trigger_pattern, mistake, lesson, solution or "", tags))
            row_id = cursor.lastrowid
            conn.commit()
            return row_id

    def search_lessons(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search relevant lessons for a given prompt or task context."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            clean_query = "".join([c if c.isalnum() or c.isspace() else " " for c in query]).strip()
            if not clean_query:
                cursor.execute("SELECT * FROM lessons_learned ORDER BY updated_at DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]

            fts_tokens = " OR ".join(clean_query.split())
            try:
                cursor.execute("""
                    SELECT l.* FROM lessons_learned l
                    JOIN lessons_fts ON lessons_fts.rowid = l.id
                    WHERE lessons_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (fts_tokens, limit))
                results = [dict(row) for row in cursor.fetchall()]
                if results:
                    return results
            except sqlite3.OperationalError:
                pass

            # Fallback
            cursor.execute("""
                SELECT * FROM lessons_learned
                WHERE trigger_pattern LIKE ? OR mistake LIKE ? OR lesson LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC LIMIT ?
            """, (f"%{clean_query}%", f"%{clean_query}%", f"%{clean_query}%", f"%{clean_query}%", limit))
            return [dict(row) for row in cursor.fetchall()]

    def record_lesson_applied(self, lesson_id: int, was_successful: bool = True) -> None:
        """Update usage and success stats for a lesson."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lessons_learned
                SET usage_count = usage_count + 1,
                    success_count = success_count + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (1 if was_successful else 0, lesson_id))
            conn.commit()

    def get_all_lessons(self) -> List[Dict[str, Any]]:
        """Retrieve all learned lessons."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lessons_learned ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    # --- Dynamic Skills Index Methods ---

    def register_skill(self, name: str, description: str, parameters: Dict[str, Any],
                       code_path: str, code_content: str) -> int:
        """Register a newly synthesized dynamic skill."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO skills_index (name, description, parameters_json, code_path, code_content)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description,
                    parameters_json = excluded.parameters_json,
                    code_path = excluded.code_path,
                    code_content = excluded.code_content
            """, (name, description, json.dumps(parameters), code_path, code_content))
            conn.commit()
            return cursor.lastrowid

    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Retrieve all dynamic skills."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills_index ORDER BY name")
            rows = cursor.fetchall()
            skills = []
            for r in rows:
                item = dict(r)
                item["parameters"] = json.loads(item.get("parameters_json") or "{}")
                skills.append(item)
            return skills

    def increment_skill_usage(self, name: str) -> None:
        """Increment usage count for a dynamic skill."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE skills_index SET usage_count = usage_count + 1 WHERE name = ?", (name,))
            conn.commit()
