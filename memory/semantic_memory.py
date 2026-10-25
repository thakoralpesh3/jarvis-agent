"""
Semantic memory subsystem for storing and extracting user profile, facts, and preferences.
"""

import json
from typing import Any, Dict, List, Optional
from .database import DatabaseManager


FACT_EXTRACTION_PROMPT = """You are a sub-module of JARVIS responsible for learning and maintaining a profile of the user and their environment.
Analyze the recent interaction between the user and JARVIS. Extract any new, durable facts, preferences, constraints, project details, or habits.

Categories:
- 'preference': Tool preferences, code style, UI themes, communication style (e.g., 'prefers concise answers', 'uses Python 3.12').
- 'user_fact': Role, occupation, location, name, background (e.g., 'name is Alpesh', 'backend engineer').
- 'project_context': Active projects, repository paths, tech stacks (e.g., 'working on jarvis-agent').
- 'system': OS, shell, hardware, installed tools (e.g., 'running Linux Mint', 'uses bash').
- 'habit': Daily routines, recurring workflows.

Return ONLY a JSON list of objects matching this schema (if no new durable facts are found, return []):
[
  {
    "category": "preference" | "user_fact" | "project_context" | "system" | "habit",
    "key": "snake_case_descriptive_key",
    "value": "clear description of the fact or preference",
    "confidence": 0.8 to 1.0
  }
]

Interaction:
User: {user_input}
Assistant: {assistant_response}
"""


class SemanticMemory:
    """Handles semantic user profiling, facts, and preference learning."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def add_or_update_fact(self, category: str, key: str, value: str, confidence: float = 1.0, source: str = "direct") -> int:
        """Store or update a specific fact."""
        return self.db.upsert_fact(category=category, key=key, value=value, confidence=confidence, source=source)

    def get_fact(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific fact by category and key."""
        facts = self.db.get_facts_by_category(category)
        for f in facts:
            if f["key"] == key:
                return f
        return None

    def search_relevant_facts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find facts relevant to a given query or context."""
        return self.db.search_facts(query, limit=limit)

    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Retrieve all known facts."""
        return self.db.get_all_facts()

    def delete_fact(self, category: str, key: str) -> bool:
        """Remove a fact."""
        return self.db.delete_fact(category, key)

    def format_context_for_prompt(self, query: str = "", limit: int = 10) -> str:
        """Format known facts and preferences into a system prompt section."""
        facts = []
        if query:
            facts = self.search_relevant_facts(query, limit=limit)

        # Supplement with general facts if below limit
        if len(facts) < limit:
            all_facts = self.get_all_facts()
            existing_ids = {f["id"] for f in facts if "id" in f}
            for f in all_facts:
                if f.get("id") not in existing_ids:
                    facts.append(f)
                    if len(facts) >= limit:
                        break

        if not facts:
            return ""

        grouped: Dict[str, List[str]] = {}
        for f in facts:
            cat = f["category"].replace("_", " ").title()
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(f"- **{f['key']}**: {f['value']}")

        lines = ["### [Continuous Memory: User & System Profile]"]
        for cat, items in grouped.items():
            lines.append(f"**{cat}**:")
            lines.extend(items)

        return "\n".join(lines)

    def parse_and_store_facts_json(self, raw_json_str: str) -> List[Dict[str, Any]]:
        """Parse LLM JSON response and upsert extracted facts."""
        try:
            # Clean possible markdown wrapping
            cleaned = raw_json_str.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("\n", 1)[0]
            cleaned = cleaned.strip()

            facts_list = json.loads(cleaned)
            if not isinstance(facts_list, list):
                return []

            saved_facts = []
            for item in facts_list:
                cat = item.get("category", "user_fact")
                key = item.get("key")
                val = item.get("value")
                conf = float(item.get("confidence", 1.0))
                if key and val:
                    self.add_or_update_fact(category=cat, key=key, value=val, confidence=conf, source="inferred")
                    saved_facts.append(item)
            return saved_facts
        except Exception:
            return []
