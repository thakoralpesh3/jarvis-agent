"""
Episodic memory and Lessons Learned (Self-Correction) management for JARVIS.
"""

from typing import Any, Dict, List, Optional
from .database import DatabaseManager


class EpisodicMemory:
    """Manages past episodes and continuous self-correction rules (Lessons Learned)."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def record_episode(self, session_id: str, user_prompt: str, plan: Optional[str],
                       steps: List[Dict[str, Any]], result: str, success: bool = True,
                       feedback: Optional[str] = None) -> int:
        """Record an episode in the database."""
        return self.db.log_episode(
            session_id=session_id,
            user_prompt=user_prompt,
            plan=plan,
            steps=steps,
            result=result,
            success=success,
            feedback=feedback
        )

    def get_recent_episodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent interaction episodes."""
        return self.db.get_recent_episodes(limit=limit)

    def add_lesson(self, trigger_pattern: str, mistake: str, lesson: str,
                   solution: Optional[str] = None, tags: str = "") -> int:
        """Store a new self-correction lesson/rule."""
        return self.db.add_lesson(
            trigger_pattern=trigger_pattern,
            mistake=mistake,
            lesson=lesson,
            solution=solution,
            tags=tags
        )

    def find_relevant_lessons(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve lessons that match the user's intent or upcoming task."""
        return self.db.search_lessons(query=query, limit=limit)

    def get_all_lessons(self) -> List[Dict[str, Any]]:
        """Get all learned lessons."""
        return self.db.get_all_lessons()

    def format_lessons_for_prompt(self, query: str = "", limit: int = 5) -> str:
        """Format learned lessons and rules of thumb to avoid repeating mistakes."""
        lessons = self.find_relevant_lessons(query=query, limit=limit)
        if not lessons:
            return ""

        lines = ["### [Continuous Learning: Past Lessons & Error Avoidance Rules]"]
        lines.append("You have previously encountered mistakes on similar tasks. Adhere strictly to these rules:")
        for idx, l in enumerate(lessons, 1):
            rule_str = f"{idx}. **When dealing with '{l['trigger_pattern']}'**:"
            rule_str += f"\n   - *Mistake to avoid*: {l['mistake']}"
            rule_str += f"\n   - *Rule/Lesson*: {l['lesson']}"
            if l.get("solution"):
                rule_str += f"\n   - *Recommended Approach*: {l['solution']}"
            lines.append(rule_str)

        return "\n".join(lines)
