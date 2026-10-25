"""
Dynamic Procedural Skill Store: Manages runtime-synthesized Python tools created by JARVIS.
"""

import ast
import importlib.util
import inspect
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from .database import DatabaseManager


class SkillStore:
    """Manages creation, validation, storage, and dynamic loading of generated tools."""

    def __init__(self, skills_dir: Path | str, db: DatabaseManager):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.db = db
        self._loaded_tools: Dict[str, Callable] = {}
        self.reload_all_skills()

    @property
    def loaded_tools(self) -> Dict[str, Callable]:
        """Dictionary of loaded callable dynamic tools."""
        return self._loaded_tools

    def validate_code_syntax(self, code_str: str) -> Tuple[bool, Optional[str]]:
        """Check if Python code parses cleanly."""
        try:
            ast.parse(code_str)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax Error on line {e.lineno}: {e.msg}"

    def register_new_skill(self, name: str, code_content: str, description: Optional[str] = None) -> Tuple[bool, str]:
        """Validate, save, and dynamically load a new Python skill."""
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in name).strip("_").lower()
        if not clean_name:
            return False, "Invalid skill name."

        # Validate syntax
        is_valid, err = self.validate_code_syntax(code_content)
        if not is_valid:
            return False, f"Code failed validation: {err}"

        file_path = self.skills_dir / f"{clean_name}.py"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_content)

            # Load dynamically
            loaded_fn = self._load_module_function(file_path, clean_name)
            if not loaded_fn:
                # If function name doesn't match clean_name, find the first public function
                mod = self._load_module(file_path, clean_name)
                funcs = [obj for n, obj in inspect.getmembers(mod, inspect.isfunction) if not n.startswith("_")]
                if funcs:
                    loaded_fn = funcs[0]
                    clean_name = loaded_fn.__name__
                else:
                    return False, f"No valid function found in {file_path.name}"

            fn_doc = inspect.getdoc(loaded_fn) or description or f"Dynamic skill: {clean_name}"
            sig = inspect.signature(loaded_fn)
            params = {
                k: str(v.annotation) if v.annotation != inspect.Parameter.empty else "Any"
                for k, v in sig.parameters.items()
            }

            self._loaded_tools[clean_name] = loaded_fn
            self.db.register_skill(
                name=clean_name,
                description=fn_doc,
                parameters=params,
                code_path=str(file_path),
                code_content=code_content
            )
            return True, f"Skill '{clean_name}' successfully created, loaded, and registered."
        except Exception as e:
            return False, f"Failed to load skill: {str(e)}"

    def _load_module(self, file_path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(f"jarvis_dynamic_{module_name}", file_path)
        if not spec or not spec.loader:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _load_module_function(self, file_path: Path, func_name: str) -> Optional[Callable]:
        try:
            module = self._load_module(file_path, func_name)
            if module and hasattr(module, func_name):
                fn = getattr(module, func_name)
                if callable(fn):
                    return fn
            return None
        except Exception:
            return None

    def reload_all_skills(self) -> None:
        """Scan skills directory and load all valid python scripts."""
        self._loaded_tools.clear()
        for py_file in self.skills_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            skill_name = py_file.stem
            try:
                mod = self._load_module(py_file, skill_name)
                if not mod:
                    continue
                # Register all top-level public functions
                for name, fn in inspect.getmembers(mod, inspect.isfunction):
                    if not name.startswith("_"):
                        self._loaded_tools[name] = fn
            except Exception:
                continue

    def get_skill_descriptions(self) -> List[Dict[str, Any]]:
        """Get summary of all available dynamic skills."""
        return self.db.get_all_skills()

    def format_skills_for_prompt(self) -> str:
        """Format dynamic skills for system prompt context."""
        skills = self.get_skill_descriptions()
        if not skills:
            return ""

        lines = ["### [Continuous Learning: Dynamic Tools Synthesized by JARVIS]"]
        lines.append("The following custom tools were previously synthesized and are available for use:")
        for s in skills:
            lines.append(f"- **{s['name']}**: {s['description']}")

        return "\n".join(lines)
