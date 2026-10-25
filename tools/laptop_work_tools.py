"""
Advanced Laptop Work & Operating System tools for JARVIS.
Includes file manipulation, notifications, process management, archive handling, and network inspection.
"""

import os
import shutil
import zipfile
import tarfile
import subprocess
import socket
import psutil
from pathlib import Path
from typing import Any, Dict, List, Optional


def send_desktop_notification(title: str, message: str, details: Optional[str] = None, urgency: str = "normal", user_commanded: bool = True) -> str:
    """
    Send an interactive native Linux desktop notification banner/popup to alert the user.
    When the user clicks the notification, it automatically displays the complete related details.
    
    Args:
        title: Header/title of notification.
        message: Brief body summary of notification.
        details: Optional comprehensive multi-line details, logs, diagnostics, or file paths.
        urgency: 'low', 'normal', or 'critical'.
        user_commanded: Set True when explicitly triggered by user command.
    """
    try:
        from core.notification_manager import get_notification_manager
        mgr = get_notification_manager()
        return mgr.send_interactive_notification(
            title=title,
            message=message,
            details=details,
            urgency=urgency,
            user_commanded=user_commanded
        )
    except Exception as e:
        return f"Error sending notification: {str(e)}"
def view_recent_notifications(limit: int = 10) -> str:
    """
    View the history of recent desktop notifications sent by JARVIS with their timestamps and full details.
    
    Args:
        limit: Number of recent notifications to retrieve.
    """
    try:
        from core.notification_manager import get_notification_manager
        mgr = get_notification_manager()
        items = mgr.get_history(limit=limit)
        if not items:
            return "No notification history recorded yet."

        lines = ["### 📬 Recent Desktop Notifications:"]
        for idx, n in enumerate(items, 1):
            lines.append(f"{idx}. **{n.get('title')}** `[{n.get('timestamp')}]`")
            lines.append(f"   Summary: {n.get('message')}")
            lines.append(f"   Details: {n.get('details')[:200]}...")
            lines.append(f"   ID: `{n.get('id')}`\n")
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving notifications: {str(e)}"


def open_notification_details(notification_id: str) -> str:
    """
    Open the full graphical details modal for a specific notification ID on the desktop.
    
    Args:
        notification_id: Unique ID of the notification (e.g. 'notif_1725123456_a1b2c3').
    """
    try:
        from core.notification_manager import get_notification_manager
        mgr = get_notification_manager()
        items = mgr.get_history(limit=50)
        for n in items:
            if n.get("id") == notification_id or notification_id in n.get("id", ""):
                mgr.show_details_dialog(n.get("title", "Notification"), n.get("details", ""), Path(n.get("details_file", "")))
                return f"Details modal opened for notification: {n.get('title')}"
        return f"Notification ID '{notification_id}' not found."
    except Exception as e:
        return f"Error opening notification details: {str(e)}"


def search_files_by_pattern(directory_path: str = "/home/alpesh", pattern: str = "*", max_results: int = 30) -> str:
    """
    Search recursively for files and folders matching a glob pattern (e.g. '*.pdf', '*invoice*', '*.py').
    
    Args:
        directory_path: Root folder to begin search. Defaults to /home/alpesh.
        pattern: Wildcard search pattern (e.g. '*.py', '*.docx', 'config*').
        max_results: Max items to return.
    """
    root = Path(directory_path).expanduser().resolve()
    if not root.exists():
        return f"Error: Directory '{directory_path}' does not exist."

    matches = []
    try:
        for p in root.rglob(pattern):
            # Ignore hidden cache/virtualenv dirs
            parts = p.parts
            if any(part.startswith(".") and part not in [".", ".."] for part in parts):
                continue
            if "node_modules" in parts or "__pycache__" in parts or ".venv" in parts:
                continue

            size_str = f"{p.stat().st_size / 1024:.1f} KB" if p.is_file() else "DIR"
            matches.append(f"- {p} ({size_str})")
            if len(matches) >= max_results:
                break

        if not matches:
            return f"No files matching '{pattern}' found in '{directory_path}'."
        return f"Found {len(matches)} matches for '{pattern}' in {directory_path}:\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching files: {str(e)}"


def move_or_rename_file(source_path: str, destination_path: str) -> str:
    """
    Move or rename a file or directory.
    
    Args:
        source_path: Path to current file/directory.
        destination_path: New path or destination folder.
    """
    src = Path(source_path).expanduser().resolve()
    dst = Path(destination_path).expanduser().resolve()
    if not src.exists():
        return f"Error: Source '{source_path}' does not exist."

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return f"Successfully moved '{source_path}' to '{destination_path}'."
    except Exception as e:
        return f"Error moving file: {str(e)}"


def copy_file_or_folder(source_path: str, destination_path: str) -> str:
    """
    Copy a file or directory to a new location.
    
    Args:
        source_path: Source file or folder.
        destination_path: Target destination path.
    """
    src = Path(source_path).expanduser().resolve()
    dst = Path(destination_path).expanduser().resolve()
    if not src.exists():
        return f"Error: Source '{source_path}' does not exist."

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
        else:
            shutil.copy2(str(src), str(dst))
        return f"Successfully copied '{source_path}' to '{destination_path}'."
    except Exception as e:
        return f"Error copying: {str(e)}"


def delete_file_or_folder(path: str) -> str:
    """
    Delete a file or folder.
    
    Args:
        path: Path to file or folder to delete.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: Path '{path}' does not exist."

    try:
        if target.is_dir():
            shutil.rmtree(str(target))
        else:
            target.unlink()
        return f"Successfully deleted '{path}'."
    except Exception as e:
        return f"Error deleting '{path}': {str(e)}"


def compress_to_archive(source_path: str, output_archive_path: str) -> str:
    """
    Compress a file or directory into a .zip or .tar.gz archive.
    
    Args:
        source_path: File or folder to compress.
        output_archive_path: Output archive path (e.g. 'backup.zip' or 'project.tar.gz').
    """
    src = Path(source_path).expanduser().resolve()
    out = Path(output_archive_path).expanduser().resolve()
    if not src.exists():
        return f"Error: Source '{source_path}' does not exist."

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.name.endswith(".zip"):
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zipf:
                if src.is_file():
                    zipf.write(src, arcname=src.name)
                else:
                    for root, _, files in os.walk(src):
                        for f in files:
                            full_p = Path(root) / f
                            zipf.write(full_p, arcname=full_p.relative_to(src.parent))
        else:
            mode = "w:gz" if out.name.endswith(".gz") else "w"
            with tarfile.open(out, mode) as tar:
                tar.add(src, arcname=src.name)

        size_kb = out.stat().st_size / 1024
        return f"Successfully created archive '{output_archive_path}' ({size_kb:.1f} KB)."
    except Exception as e:
        return f"Error compressing: {str(e)}"


def extract_archive(archive_path: str, extract_to_dir: str = ".") -> str:
    """
    Extract a .zip, .tar, .tar.gz, or .tgz archive into a target directory.
    
    Args:
        archive_path: Path to archive file.
        extract_to_dir: Destination folder.
    """
    arch = Path(archive_path).expanduser().resolve()
    out = Path(extract_to_dir).expanduser().resolve()
    if not arch.exists():
        return f"Error: Archive '{archive_path}' does not exist."

    try:
        out.mkdir(parents=True, exist_ok=True)
        if arch.name.endswith(".zip"):
            with zipfile.ZipFile(arch, "r") as zipf:
                zipf.extractall(out)
        else:
            with tarfile.open(arch, "r:*") as tar:
                tar.extractall(out)
        return f"Successfully extracted '{archive_path}' to '{extract_to_dir}'."
    except Exception as e:
        return f"Error extracting archive: {str(e)}"


def kill_process_by_name(process_name: str) -> str:
    """
    Terminate/kill running processes by name (e.g. 'chrome', 'firefox', 'vlc', 'spotify').
    
    Args:
        process_name: Executable or process name.
    """
    killed = 0
    clean_name = process_name.lower().strip()
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if clean_name in p.info['name'].lower():
                p.terminate()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed > 0:
        return f"Terminated {killed} process(es) matching '{process_name}'."
    return f"No running processes found matching '{process_name}'."


def find_running_processes(search_keyword: str = "") -> str:
    """
    List active system processes filtered by keyword with PID, CPU %, and Memory %.
    
    Args:
        search_keyword: Optional keyword to filter process names.
    """
    matches = []
    kw = search_keyword.lower().strip()
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            name = p.info.get('name') or ""
            if not kw or kw in name.lower():
                cpu = p.info.get('cpu_percent', 0.0) or 0.0
                mem = p.info.get('memory_percent', 0.0) or 0.0
                pid = p.info.get('pid')
                matches.append(f"PID {pid:6} | CPU: {cpu:4.1f}% | RAM: {mem:4.1f}% | {name}")
                if len(matches) >= 25:
                    break
        except Exception:
            continue

    if not matches:
        return f"No processes matching '{search_keyword}'."
    return f"Active Processes ({len(matches)}):\n" + "\n".join(matches)


def get_network_and_wifi_status() -> str:
    """
    Get IP addresses, network interface statistics, WiFi SSID, and internet connectivity ping.
    """
    info = []
    # Hostname and local IP
    hostname = socket.gethostname()
    info.append(f"Hostname: {hostname}")

    # Check internet ping
    try:
        res = subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"], capture_output=True, text=True)
        online = "Connected to Internet" if res.returncode == 0 else "Offline / No Internet"
        info.append(f"Internet Status: {online}")
    except Exception:
        info.append("Internet Status: Unknown")

    # WiFi SSID via nmcli or iwgetid
    if shutil.which("nmcli"):
        try:
            res = subprocess.run("nmcli -t -f active,ssid dev wifi | grep '^yes:'", shell=True, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                ssid = res.stdout.strip().replace("yes:", "")
                info.append(f"Connected Wi-Fi Network: {ssid}")
        except Exception:
            pass

    # Network Interfaces
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        if iface == "lo":
            continue
        for a in addr_list:
            if a.family == socket.AF_INET:
                info.append(f"Interface {iface}: IP {a.address}")

    return "Network & Connectivity Diagnostics:\n" + "\n".join(info)


def open_file_or_folder_with_default_app(path: str) -> str:
    """
    Open any file, document, image, video, code, or folder on the laptop using its default system desktop application (xdg-open).
    
    Args:
        path: Absolute or relative path to the file or directory on the laptop.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return f"Error: Path '{path}' does not exist on this laptop."

    try:
        env = os.environ.copy()
        if "DISPLAY" not in env or not env["DISPLAY"]:
            env["DISPLAY"] = ":0"
        subprocess.Popen(["xdg-open", str(target)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return f"Successfully opened '{target.name}' with default system application."
    except Exception as e:
        return f"Error opening '{path}': {str(e)}"


def get_detailed_disk_usage() -> str:
    """
    Inspect comprehensive storage metrics, free space, and mount points across all disks and partitions on the laptop.
    """
    try:
        res = subprocess.run(["df", "-h", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs"], capture_output=True, text=True)
        if res.returncode == 0:
            return f"### 💾 Laptop Storage & Disk Partitions:\n```\n{res.stdout.strip()}\n```"
        return "Could not retrieve disk metrics via df."
    except Exception as e:
        return f"Error checking disk usage: {str(e)}"


def find_files_across_laptop(query: str, start_dir: str = "/home/alpesh", file_extension: Optional[str] = None, max_results: int = 40) -> str:
    """
    Search high-speed for files or directories matching a query anywhere on the laptop.
    
    Args:
        query: Search term or pattern (e.g. 'report', 'invoice', 'test').
        start_dir: Root directory to search from. Defaults to '/home/alpesh'.
        file_extension: Optional extension filter without dot (e.g. 'pdf', 'py', 'png', 'docx').
        max_results: Max results to return.
    """
    root = Path(start_dir).expanduser().resolve()
    if not root.exists():
        return f"Error: Directory '{start_dir}' does not exist."

    matches = []
    pattern = f"*{query}*"
    if file_extension:
        ext = file_extension.lstrip(".")
        pattern = f"*{query}*.{ext}"

    try:
        for p in root.rglob(pattern):
            parts = p.parts
            if any(part.startswith(".") and part not in [".", ".."] for part in parts):
                continue
            if any(x in parts for x in ["node_modules", "__pycache__", ".venv", ".git", ".cache"]):
                continue

            size_str = f"{p.stat().st_size / 1024:.1f} KB" if p.is_file() else "DIR"
            matches.append(f"- `{p}` ({size_str})")
            if len(matches) >= max_results:
                break

        if not matches:
            return f"No files matching '{query}' (ext: {file_extension or 'any'}) found under '{start_dir}'."
        return f"### 🔍 Found {len(matches)} item(s) matching '{query}' under {start_dir}:\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching across laptop: {str(e)}"


def manage_software_package(action: str = "check", package_name: str = "") -> str:
    """
    Inspect or manage software packages and CLI tools on the laptop (apt/pip).
    
    Args:
        action: 'check' (verify if tool is installed), 'install_pip' (install Python package), 'check_which' (find binary in PATH).
        package_name: Name of tool or package (e.g. 'ffmpeg', 'git', 'pandas', 'ripgrep').
    """
    pkg = package_name.strip()
    if not pkg:
        return "Error: package_name must be specified."

    if action in ("check", "check_which"):
        path = shutil.which(pkg)
        if path:
            return f"✓ Tool '{pkg}' is installed at: `{path}`"
        # Check python package
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "show", pkg], capture_output=True, text=True)
            if res.returncode == 0:
                return f"✓ Python package '{pkg}' is installed:\n{res.stdout.splitlines()[0]}"
        except Exception:
            pass
        return f"✗ Tool/package '{pkg}' is NOT currently found in system PATH or python environment."

    elif action == "install_pip":
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True, timeout=120)
            if res.returncode == 0:
                return f"✓ Successfully installed Python package '{pkg}'."
            return f"Error installing '{pkg}':\n{res.stderr.strip()}"
        except Exception as e:
            return f"Installation error: {str(e)}"

    return f"Unsupported action: '{action}'. Use 'check' or 'install_pip'."


def inspect_desktop_state() -> str:
    """
    Inspect the current active desktop state, including screen resolution, focused window, and active applications.
    """
    state_lines = ["### 🖥️ Active Desktop State:"]
    # Resolution
    if shutil.which("xrandr"):
        try:
            res = subprocess.run("xrandr --current | grep '*' | awk '{print $1}'", shell=True, capture_output=True, text=True)
            if res.stdout.strip():
                state_lines.append(f"- **Screen Resolution:** {res.stdout.strip()}")
        except Exception:
            pass

    # Active Window
    if shutil.which("xdotool"):
        try:
            res = subprocess.run("xdotool getactivewindow getwindowname", shell=True, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                state_lines.append(f"- **Currently Focused Window:** \"{res.stdout.strip()}\"")
        except Exception:
            pass

    # Battery & System Metrics
    battery = psutil.sensors_battery()
    if battery:
        plug = "Plugged in" if battery.power_plugged else "On Battery"
        state_lines.append(f"- **Power:** {battery.percent}% ({plug})")

    state_lines.append(f"- **CPU Usage:** {psutil.cpu_percent(interval=0.1)}%")
    state_lines.append(f"- **RAM Usage:** {psutil.virtual_memory().percent}%")

    return "\n".join(state_lines)


def dispatch_background_laptop_work(mission_directive: str) -> str:
    """
    Dispatch a laptop mission or command to execute asynchronously in the background.
    Aradhya will run the task to full completion and send a native desktop notification when finished.
    
    Args:
        mission_directive: Detailed command or task for Aradhya to execute in the background.
    """
    from core.laptop_work_executor import dispatch_background_laptop_work as _dispatch
    return _dispatch(mission_directive)

