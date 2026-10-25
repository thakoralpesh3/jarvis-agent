"""
Tests for Self-Learning and Reflection parsing.
"""

import tempfile
from pathlib import Path
import pytest

from memory.database import DatabaseManager
from memory.semantic_memory import SemanticMemory


def test_fact_json_parsing():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = DatabaseManager(Path(tmpdir) / "test.db")
        semantic = SemanticMemory(db)

        raw_json = """
        [
            {
                "category": "preference",
                "key": "preferred_language",
                "value": "Python 3.12",
                "confidence": 0.95
            },
            {
                "category": "project_context",
                "key": "current_project",
                "value": "JARVIS assistant",
                "confidence": 0.9
            }
        ]
        """
        parsed = semantic.parse_and_store_facts_json(raw_json)
        assert len(parsed) == 2

        fact = semantic.get_fact("preference", "preferred_language")
        assert fact is not None
        assert fact["value"] == "Python 3.12"
