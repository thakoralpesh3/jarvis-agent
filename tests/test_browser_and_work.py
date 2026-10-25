"""
Tests for Laptop Work Tools and Browser Controller.
"""

import tempfile
from pathlib import Path
import pytest

from tools.laptop_work_tools import (
    search_files_by_pattern,
    move_or_rename_file,
    copy_file_or_folder,
    delete_file_or_folder,
    compress_to_archive,
    extract_archive,
    find_running_processes,
    get_network_and_wifi_status,
    send_desktop_notification,
)
from tools.browser_controller import (
    desktop_browser_new_tab,
    desktop_browser_switch_tab,
    desktop_browser_reload_page,
)


def test_file_operations_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        test_file = base / "project_report.txt"
        test_file.write_text("JARVIS test content")

        # Search
        search_res = search_files_by_pattern(str(base), "*.txt")
        assert "project_report.txt" in search_res

        # Copy
        copy_dst = base / "backup_report.txt"
        copy_res = copy_file_or_folder(str(test_file), str(copy_dst))
        assert "Successfully copied" in copy_res
        assert copy_dst.exists()

        # Move / Rename
        renamed_dst = base / "renamed_report.txt"
        move_res = move_or_rename_file(str(copy_dst), str(renamed_dst))
        assert "Successfully moved" in move_res
        assert renamed_dst.exists()
        assert not copy_dst.exists()

        # Delete
        del_res = delete_file_or_folder(str(renamed_dst))
        assert "Successfully deleted" in del_res
        assert not renamed_dst.exists()


def test_archive_compress_and_extract():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        source_dir = base / "my_data"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("Hello 1")
        (source_dir / "file2.txt").write_text("Hello 2")

        # Compress to zip
        zip_path = base / "archive.zip"
        comp_res = compress_to_archive(str(source_dir), str(zip_path))
        assert "Successfully created archive" in comp_res
        assert zip_path.exists()

        # Extract
        extract_dir = base / "extracted"
        ext_res = extract_archive(str(zip_path), str(extract_dir))
        assert "Successfully extracted" in ext_res
        assert (extract_dir / "my_data" / "file1.txt").exists()


def test_processes_and_network():
    # Process listing
    procs = find_running_processes("python")
    assert isinstance(procs, str)

    # Network diagnostics
    net = get_network_and_wifi_status()
    assert "Diagnostics" in net
    assert "Hostname" in net


def test_desktop_notification():
    notif_res = send_desktop_notification("Test Alert", "JARVIS automated test message")
    assert "notification" in notif_res.lower()
