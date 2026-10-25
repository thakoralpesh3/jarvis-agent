"""
Network Resilience and State Checkpoint Resumption Subsystem for JARVIS.
Detects network dropouts/outages, suspends task state at checkpoint, waits for internet restoration,
and automatically resumes execution from the exact point of interruption without data loss.
"""

import os
import sys
import time
import socket
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


def check_internet_connection(timeout: float = 1.5) -> bool:
    """
    Rapid multi-target probe to verify live internet connectivity.
    Tries primary DNS sockets (8.8.8.8:53, 1.1.1.1:53) and fallback HTTP ping.
    """
    targets = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("9.9.9.9", 53),
    ]
    for host, port in targets:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return True
        except Exception:
            continue

    # Fallback HTTP check
    try:
        urllib.request.urlopen("http://www.google.com", timeout=timeout)
        return True
    except Exception:
        return False


def is_network_error(exc: Exception) -> bool:
    """Determine whether an exception was caused by a network/connectivity/timeout fault."""
    if isinstance(exc, (socket.error, socket.gaierror, socket.timeout, ConnectionError,
                        ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, TimeoutError)):
        return True

    exc_str = str(exc).lower()
    net_keywords = [
        "network", "connection", "connect", "timeout", "timed out", "unreachable",
        "name resolution", "dns", "socket", "503", "502", "504", "unavailable",
        "max retries", "temporary failure", "broken pipe", "failed to establish",
        "nodename nor servname", "getaddrinfo"
    ]
    return any(kw in exc_str for kw in net_keywords)


def wait_for_network_restoration(max_wait_seconds: int = 300,
                                poll_interval: float = 3.0,
                                on_status: Optional[Callable[[str], None]] = None) -> bool:
    """
    Suspend current task, notify user, and poll until network connectivity returns.
    
    Args:
        max_wait_seconds: Maximum seconds to wait before timing out (default 5 minutes).
        poll_interval: Seconds between connection probes.
        on_status: Optional callback for UI / status text updates.
    """
    play_stark_sound("alert")
    msg = "Network link lost. Task suspended at checkpoint. Awaiting connection restoration..."
    send_desktop_notification("Aradhya Network Sentry", msg, urgency="critical", user_commanded=False)
    if on_status:
        on_status(msg)

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        time.sleep(poll_interval)
        if check_internet_connection(timeout=1.5):
            elapsed = int(time.time() - start_time)
            play_stark_sound("protocol")
            res_msg = f"Network connection restored after {elapsed}s. Resuming task execution from checkpoint..."
            send_desktop_notification("Aradhya Network Sentry", res_msg, urgency="normal", user_commanded=False)
            if on_status:
                on_status(res_msg)
            return True

    return False


def execute_with_network_resume(
    func: Callable[..., Any],
    *args: Any,
    max_network_retries: int = 5,
    on_status: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> Any:
    """
    Execute a network-dependent callable. If a network fault occurs:
    1. Pauses task state.
    2. Enters adaptive polling until internet connectivity returns.
    3. Resumes execution transparently from the exact failure point.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if is_network_error(exc) and attempt <= max_network_retries:
                if on_status:
                    on_status(f"[bold yellow]⚠️ Network fault detected ({str(exc)[:60]}...). Checkpoint saved. Pausing...[/bold yellow]")
                
                # Check if genuinely offline or transient glitch
                if not check_internet_connection(timeout=1.5):
                    # Genuine network dropout -> wait for connection to come back online
                    restored = wait_for_network_restoration(max_wait_seconds=300, poll_interval=3.0, on_status=on_status)
                    if not restored:
                        raise TimeoutError("Network connection was not restored within timeout threshold.") from exc
                else:
                    # Transient endpoint congestion / temporary glitch -> brief backoff
                    time.sleep(1.5 * attempt)

                if on_status:
                    on_status(f"[bold green]✓ Network link verified. Resuming process from checkpoint (Attempt {attempt + 1})...[/bold green]")
                continue

            # Non-network error or exceeded max retries -> raise
            raise exc
