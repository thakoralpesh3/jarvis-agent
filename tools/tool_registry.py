"""
Tool Registry and Dispatcher for JARVIS using Gemini function-calling specifications.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional
from google.genai import types


class ToolRegistry:
    """Manages built-in and dynamic tools, converting them into Gemini function call declarations."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, func: Optional[Callable] = None, *, name: Optional[str] = None, description: Optional[str] = None):
        """Decorator or method to register a tool."""
        def decorator(f: Callable):
            tool_name = name or f.__name__
            tool_desc = description or inspect.getdoc(f) or f"Execute {tool_name}"
            self._tools[tool_name] = f
            self._descriptions[tool_name] = tool_desc
            return f

        if func is None:
            return decorator
        return decorator(func)

    def register_function(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        """Direct method to register a callable function."""
        tool_name = name or func.__name__
        tool_desc = description or inspect.getdoc(func) or f"Execute {tool_name}"
        self._tools[tool_name] = func
        self._descriptions[tool_name] = tool_desc

    def unregister(self, name: str) -> None:
        """Remove a tool by name."""
        self._tools.pop(name, None)
        self._descriptions.pop(name, None)

    @property
    def tools(self) -> Dict[str, Callable]:
        return self._tools

    def get_tool_callables(self) -> List[Callable]:
        """Return list of Python callable functions for Google GenAI client."""
        return list(self._tools.values())

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool safely by name."""
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found. Available tools: {list(self._tools.keys())}"

        func = self._tools[tool_name]
        try:
            return func(**kwargs)
        except TypeError as e:
            return f"Argument Error calling '{tool_name}': {str(e)}"
        except Exception as e:
            return f"Runtime Error executing '{tool_name}': {str(e)}"
