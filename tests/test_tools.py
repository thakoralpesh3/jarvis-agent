"""
Tests for JARVIS Tools and Tool Registry.
"""

import tempfile
from pathlib import Path
import pytest

from tools.tool_registry import ToolRegistry
from tools.system_tools import (
    execute_shell_command,
    read_file_content,
    write_file_content,
    list_directory_files,
    get_system_metrics,
)


def test_tool_registry_execution():
    registry = ToolRegistry()

    @registry.register
    def multiply(x: int, y: int) -> int:
        """Multiplies two numbers."""
        return x * y

    assert "multiply" in registry.tools
    res = registry.execute("multiply", x=6, y=7)
    assert res == 42


def test_system_tools_file_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "subfolder" / "sample.txt"
        
        # Write
        write_res = write_file_content(str(test_file), "Hello JARVIS!\nLine 2")
        assert "Success" in write_res
        assert test_file.exists()

        # Read
        read_res = read_file_content(str(test_file))
        assert "Hello JARVIS!" in read_res
        assert "Line 2" in read_res

        # List dir
        list_res = list_directory_files(str(test_file.parent))
        assert "sample.txt" in list_res


def test_execute_shell_command():
    res = execute_shell_command("echo 'JARVIS_ONLINE'")
    assert "JARVIS_ONLINE" in res
    assert "Exit Code: 0" in res


def test_system_metrics():
    metrics = get_system_metrics()
    assert "CPU Usage" in metrics
    assert "RAM Usage" in metrics
    assert "Disk Usage" in metrics
