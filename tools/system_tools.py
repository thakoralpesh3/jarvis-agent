"""
System and OS automation tools for JARVIS.
"""

import os
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Any


def execute_shell_command(command: str, timeout_seconds: int = 30) -> str:
    """
    Execute a shell command on the host operating system and return the stdout and stderr output.
    
    Args:
        command: The bash command line string to run.
        timeout_seconds: Maximum time in seconds before terminating the process.
    """
    try:
        # Run command
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            executable="/bin/bash"
        )
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        code = proc.returncode

        output_parts = []
        if stdout:
            output_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_parts.append(f"STDERR:\n{stderr}")
        if not stdout and not stderr:
            output_parts.append("(Command produced no output)")
        
        output_parts.append(f"Exit Code: {code}")
        return "\n\n".join(output_parts)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout_seconds} seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"


def read_file_content(filepath: str, max_lines: int = 500) -> str:
    """
    Read the contents of a local file.
    
    Args:
        filepath: Absolute or relative path to the file.
        max_lines: Maximum number of lines to return.
    """
    path = Path(filepath).expanduser().resolve()
    if not path.exists():
        return f"Error: File '{filepath}' does not exist."
    if not path.is_file():
        return f"Error: Path '{filepath}' is not a regular file."

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            content = "".join(lines)
            if f.readline():
                content += f"\n... (File truncated at {max_lines} lines)"
            return content
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


def write_file_content(filepath: str, content: str, append: bool = False) -> str:
    """
    Write or append text content to a file. Parent directories will be created automatically.
    
    Args:
        filepath: Target file path.
        content: Text content to write.
        append: If True, append to existing content instead of overwriting.
    """
    path = Path(filepath).expanduser().resolve()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        action = "Appended to" if append else "Wrote"
        return f"Success: {action} '{filepath}' ({len(content)} characters)."
    except Exception as e:
        return f"Error writing to '{filepath}': {str(e)}"


def list_directory_files(directory_path: str = ".") -> str:
    """
    List contents of a directory with file types and sizes.
    
    Args:
        directory_path: Path to the directory.
    """
    path = Path(directory_path).expanduser().resolve()
    if not path.exists():
        return f"Error: Directory '{directory_path}' does not exist."
    if not path.is_dir():
        return f"Error: '{directory_path}' is not a directory."

    try:
        entries = []
        for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith("."):
                continue
            kind = "DIR " if item.is_dir() else "FILE"
            size = f"{item.stat().st_size / 1024:.1f} KB" if item.is_file() else "-"
            entries.append(f"{kind:4} | {size:>10} | {item.name}")
        
        header = f"Contents of {path} ({len(entries)} items):\n"
        header += f"{'TYPE':4} | {'SIZE':>10} | NAME\n" + "-" * 40
        return header + "\n" + "\n".join(entries[:100])
    except Exception as e:
        return f"Error listing directory '{directory_path}': {str(e)}"


def get_system_metrics() -> str:
    """
    Get real-time system performance metrics (CPU, RAM, Disk, Uptime, Top Processes).
    """
    try:
        cpu_pct = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Top 5 CPU processes
        procs = []
        for p in sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']), 
                        key=lambda x: x.info.get('cpu_percent', 0) or 0, reverse=True)[:5]:
            procs.append(f"- {p.info.get('name')}: CPU {p.info.get('cpu_percent')}% | RAM {p.info.get('memory_percent', 0):.1f}%")

        return (
            f"System Metrics:\n"
            f"- CPU Usage: {cpu_pct}%\n"
            f"- RAM Usage: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)\n"
            f"- Disk Usage: {disk.percent}% ({disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB)\n\n"
            f"Top Active Processes:\n" + "\n".join(procs)
        )
    except Exception as e:
        return f"Error gathering metrics: {str(e)}"


def launch_desktop_app(app_name: str) -> str:
    """
    Launch an application on the Linux desktop in background.
    
    Args:
        app_name: Name or executable of the application (e.g., 'firefox', 'vlc', 'gedit').
    """
    try:
        subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return f"Launched application '{app_name}' successfully."
    except FileNotFoundError:
        return f"Error: Application executable '{app_name}' not found in system PATH."
    except Exception as e:
        return f"Error launching application '{app_name}': {str(e)}"
