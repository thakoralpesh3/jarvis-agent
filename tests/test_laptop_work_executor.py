"""
Unit tests for Full Laptop Access and LaptopWorkExecutor.
"""

import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock

from tools.laptop_work_tools import (
    open_file_or_folder_with_default_app,
    get_detailed_disk_usage,
    find_files_across_laptop,
    manage_software_package,
    inspect_desktop_state,
)
from core.laptop_work_executor import LaptopWorkExecutor, execute_autonomous_laptop_work


def test_get_detailed_disk_usage():
    res = get_detailed_disk_usage()
    assert isinstance(res, str)
    assert "Laptop Storage" in res or "df" in res


def test_find_files_across_laptop():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "jarvis_sample_test_doc.txt"
        test_file.write_text("JARVIS test sample file content")

        res = find_files_across_laptop("sample_test_doc", start_dir=tmpdir)
        assert "jarvis_sample_test_doc.txt" in res


def test_open_file_with_default_app_not_found():
    res = open_file_or_folder_with_default_app("/nonexistent_path/random_file_1234.xyz")
    assert "does not exist" in res


def test_open_file_with_default_app_success():
    with tempfile.NamedTemporaryFile(suffix=".txt") as tf:
        res = open_file_or_folder_with_default_app(tf.name)
        assert "Successfully opened" in res or "xdg-open" in res


def test_manage_software_package():
    # 'python3' should be detected in PATH
    res = manage_software_package(action="check", package_name="python3")
    assert "is installed" in res

    # Random non-existent tool
    res_fake = manage_software_package(action="check", package_name="totally_nonexistent_cli_tool_999")
    assert "NOT currently found" in res_fake


def test_inspect_desktop_state():
    res = inspect_desktop_state()
    assert isinstance(res, str)
    assert "Active Desktop State" in res
    assert "CPU Usage" in res


def test_laptop_work_executor_mock_agent():
    mock_agent = MagicMock()
    mock_agent.client = MagicMock()
    mock_agent.config = MagicMock()
    mock_agent.config.language = "gujarati"
    mock_agent.config.enable_voice_response = False
    mock_agent.voice = MagicMock()
    mock_agent.run_turn = MagicMock(return_value="All 4 task steps executed and verified on laptop.")

    executor = LaptopWorkExecutor(agent=mock_agent)
    res = executor.execute_mission("Clean temporary files and verify disk space")

    assert res["status"] == "completed"
    assert "All 4 task steps executed" in res["summary"]
    assert mock_agent.run_turn.called


def test_dispatch_background_laptop_work():
    from core.laptop_work_executor import dispatch_background_laptop_work
    res = dispatch_background_laptop_work("Test background task for Aradhya")
    assert "Aradhya has dispatched your laptop mission to the background" in res
    assert "Test background task for Aradhya" in res
