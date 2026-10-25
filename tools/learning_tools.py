"""
Explicit continuous learning and self-evolution tools for JARVIS.
These allow JARVIS to consciously update its own memory and write new tools during task execution.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from memory.memory_manager import MemoryManager


class LearningToolProvider:
    """Provides explicit learning tools linked to the active MemoryManager."""

    def __init__(self, memory_mgr: 'MemoryManager'):
        self.memory_mgr = memory_mgr

    def learn_user_fact(self, key: str, value: str, category: str = "preference") -> str:
        """
        Record a permanent user preference, habit, system specification, or project detail into long-term memory.
        
        Args:
            key: Concise snake_case identifier (e.g. 'favorite_language', 'dark_mode_preference').
            value: The detailed preference or fact.
            category: Category: 'preference', 'user_fact', 'project_context', 'system', or 'habit'.
        """
        self.memory_mgr.semantic.add_or_update_fact(
            category=category,
            key=key,
            value=value,
            confidence=1.0,
            source="direct"
        )
        return f"Successfully committed to Long-Term Memory: [{category}] {key} = '{value}'"

    def learn_lesson_rule(self, trigger_condition: str, mistake_to_avoid: str, rule_or_lesson: str, solution: str = "") -> str:
        """
        Record a permanent rule or lesson learned from a mistake or user correction so JARVIS will not repeat it.
        
        Args:
            trigger_condition: When or in what context does this rule apply (e.g. 'writing bash scripts on Linux Mint', 'handling json parsing').
            mistake_to_avoid: What action failed or was incorrect previously.
            rule_or_lesson: The rule to follow going forward.
            solution: Optional recommended snippet or pattern.
        """
        lesson_id = self.memory_mgr.learn_lesson(
            trigger=trigger_condition,
            mistake=mistake_to_avoid,
            lesson=rule_or_lesson,
            solution=solution
        )
        return f"Successfully saved Lesson #{lesson_id}: When '{trigger_condition}', remember '{rule_or_lesson}'"

    def synthesize_custom_skill(self, skill_name: str, python_code: str, description: str) -> str:
        """
        Synthesize, test, and permanently register a new Python tool for yourself to use in future tasks.
        
        Args:
            skill_name: Valid python function name (e.g. 'convert_markdown_to_pdf', 'calculate_subnet_ips').
            python_code: Self-contained Python script defining the function with docstring and type annotations.
            description: Clear explanation of what the new tool does and its parameters.
        """
        success, message = self.memory_mgr.skills.register_new_skill(
            name=skill_name,
            code_content=python_code,
            description=description
        )
        return message
