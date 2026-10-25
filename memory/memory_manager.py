"""
Unified Memory Manager coordinating Semantic, Episodic, and Procedural (Skill) memory for JARVIS.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from config.settings import JarvisConfig
from .database import DatabaseManager
from .semantic_memory import SemanticMemory
from .episodic_memory import EpisodicMemory
from .skill_store import SkillStore


class MemoryManager:
    """Central interface coordinating all memory tiers for JARVIS."""

    def __init__(self, config: JarvisConfig):
        self.config = config
        self.db = DatabaseManager(config.db_path)
        self.semantic = SemanticMemory(self.db)
        self.episodic = EpisodicMemory(self.db)
        self.skills = SkillStore(config.dynamic_tools_dir, self.db)

    def assemble_system_learning_context(self, current_prompt: str = "") -> str:
        """
        Assemble the continuous learning prompt block containing:
        1. User profile and facts
        2. Relevant self-correction lessons
        3. Available synthesized dynamic tools
        """
        sections = []

        # 1. User & System Semantic Facts
        facts_context = self.semantic.format_context_for_prompt(
            query=current_prompt,
            limit=self.config.max_relevant_facts
        )
        if facts_context:
            sections.append(facts_context)

        # 2. Lessons Learned (Error avoidance)
        lessons_context = self.episodic.format_lessons_for_prompt(
            query=current_prompt,
            limit=self.config.max_relevant_lessons
        )
        if lessons_context:
            sections.append(lessons_context)

        # 3. Dynamic Skills
        skills_context = self.skills.format_skills_for_prompt()
        if skills_context:
            sections.append(skills_context)

        if not sections:
            return ""

        return "\n\n".join(sections)

    def record_interaction(self, session_id: str, user_prompt: str, plan: Optional[str],
                           steps: List[Dict[str, Any]], result: str, success: bool = True,
                           feedback: Optional[str] = None) -> int:
        """Store the complete turn into episodic memory."""
        return self.episodic.record_episode(
            session_id=session_id,
            user_prompt=user_prompt,
            plan=plan,
            steps=steps,
            result=result,
            success=success,
            feedback=feedback
        )

    def learn_lesson(self, trigger: str, mistake: str, lesson: str,
                     solution: Optional[str] = None, tags: str = "") -> int:
        """Directly record a new lesson learned."""
        return self.episodic.add_lesson(
            trigger_pattern=trigger,
            mistake=mistake,
            lesson=lesson,
            solution=solution,
            tags=tags
        )

    def get_summary_stats(self) -> Dict[str, int]:
        """Return counts of learned items for UI dashboard."""
        facts_count = len(self.semantic.get_all_facts())
        lessons_count = len(self.episodic.get_all_lessons())
        episodes_count = len(self.episodic.get_recent_episodes(1000))
        skills_count = len(self.skills.loaded_tools)
        return {
            "facts": facts_count,
            "lessons": lessons_count,
            "episodes": episodes_count,
            "skills": skills_count,
        }
