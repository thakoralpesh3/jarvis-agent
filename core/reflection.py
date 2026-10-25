"""
Continuous Reflection & Learning Engine for JARVIS.
Analyzes interactions, user corrections, errors, and outcomes to synthesize long-term memory and lessons.
"""

import json
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from config.settings import JarvisConfig
from memory.memory_manager import MemoryManager


REFLECTION_PROMPT = """You are the self-learning reflection module of JARVIS.
Your objective is to inspect a completed interaction between the user and JARVIS to extract:
1. Durable User Facts / Preferences / Project Info (if any was disclosed).
2. Lessons Learned & Self-Corrections (especially if there was a mistake, an error in command execution, a tool failure, or the user corrected JARVIS).

Interaction History:
User Prompt: {user_prompt}
Tools Executed & Outputs: {tool_trace}
Final Assistant Response: {assistant_response}
User Feedback / Follow-up: {user_feedback}

Return a valid JSON object matching this schema:
{{
  "facts": [
    {{
      "category": "preference" | "user_fact" | "project_context" | "system" | "habit",
      "key": "snake_case_key",
      "value": "Description of fact or preference",
      "confidence": 0.9
    }}
  ],
  "lessons": [
    {{
      "trigger_pattern": "Context or keywords when this rule applies",
      "mistake": "What went wrong or was mistaken",
      "lesson": "Actionable rule to follow in the future to avoid this mistake",
      "solution": "Recommended technique or syntax (optional)",
      "tags": "comma,separated,tags"
    }}
  ]
}}

If nothing new was learned, return {{"facts": [], "lessons": []}}.
"""


class ReflectionEngine:
    """Performs post-turn reflection to extract facts and error-avoidance rules."""

    def __init__(self, config: JarvisConfig, memory_mgr: MemoryManager):
        self.config = config
        self.memory_mgr = memory_mgr
        self.client = genai.Client(api_key=config.api_key) if config.api_key else None

    def reflect_on_interaction(self, user_prompt: str, tool_trace: List[Dict[str, Any]],
                               assistant_response: str, user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Run reflection and commit extracted learnings directly into persistent storage."""
        if not self.config.auto_reflection:
            return {"facts": [], "lessons": []}

        if not self.client:
            return {"facts": [], "lessons": []}

        prompt = REFLECTION_PROMPT.format(
            user_prompt=user_prompt,
            tool_trace=json.dumps(tool_trace, default=str),
            assistant_response=assistant_response,
            user_feedback=user_feedback or "(None)"
        )

        from core.network_resilience import execute_with_network_resume, is_network_error

        candidate_models = [self.config.model_name, "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        def _call_reflection():
            last_err = None
            for model_id in models_to_try:
                try:
                    return self.client.models.generate_content(
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            response_mime_type="application/json"
                        )
                    )
                except Exception as e:
                    last_err = e
                    if is_network_error(e) and model_id == models_to_try[-1]:
                        raise e
                    continue
            if last_err:
                raise last_err
            return None

        try:
            response = execute_with_network_resume(_call_reflection)
        except Exception:
            response = None

        if not response:
            return {"facts": [], "lessons": []}

        try:

            raw_text = response.text or "{}"
            data = json.loads(raw_text)

            learned_facts = []
            for f in data.get("facts", []):
                cat = f.get("category", "user_fact")
                k = f.get("key")
                v = f.get("value")
                conf = float(f.get("confidence", 1.0))
                if k and v:
                    self.memory_mgr.semantic.add_or_update_fact(category=cat, key=k, value=v, confidence=conf, source="reflection")
                    learned_facts.append(f)

            learned_lessons = []
            for l in data.get("lessons", []):
                trigger = l.get("trigger_pattern")
                mistake = l.get("mistake")
                lesson = l.get("lesson")
                sol = l.get("solution")
                tags = l.get("tags", "")
                if trigger and lesson:
                    self.memory_mgr.learn_lesson(trigger=trigger, mistake=mistake or "", lesson=lesson, solution=sol, tags=tags)
                    learned_lessons.append(l)

            return {
                "facts": learned_facts,
                "lessons": learned_lessons
            }
        except Exception:
            return {"facts": [], "lessons": []}
