"""
Cloud Synchronization & 24/7 Mobile Access Tools for Aradhya.
Allows checking cloud status, syncing offline tasks, and transmitting Wake-on-LAN packets.
"""

from typing import Dict, Any, Optional
from config.settings import load_config


_sync_manager: Optional[Any] = None


def _get_sync_manager() -> Any:
    global _sync_manager
    if _sync_manager is None:
        from core.cloud_sync import CloudSyncManager
        cfg = load_config()
        _sync_manager = CloudSyncManager(cfg)
    return _sync_manager


def check_cloud_sentinel_status() -> str:
    """
    Check the connectivity, heartbeat, and pending offline task mailbox of the 24/7 Aradhya Cloud Sentinel.
    """
    mgr = _get_sync_manager()
    status_data = mgr._http_request("/api/status", method="GET")
    if not status_data:
        return (
            f"Aradhya Cloud Sentinel: [UNREACHABLE at {mgr.cloud_url}]\n"
            f"- Note: If running locally or on Render, ensure the cloud container is deployed or run 'python3 cloud_mobile_bridge/mobile_agent_server.py'."
        )

    tasks_count = status_data.get("pending_tasks_count", 0)
    laptop_state = status_data.get("laptop_status", "UNKNOWN")
    return (
        f"Aradhya 24/7 Cloud Sentinel Status: [ONLINE / ACTIVE]\n"
        f"- Cloud URL: {mgr.cloud_url}\n"
        f"- Cloud View of Laptop: {laptop_state}\n"
        f"- Pending Offline Tasks in Mailbox: {tasks_count}\n"
        f"- Mobile Web Portal: Active at {mgr.cloud_url}/"
    )


def sync_cloud_task_queue() -> str:
    """
    Fetch and immediately execute all directives queued by Alpesh Sir from his mobile phone
    or web portal while this laptop was turned off or asleep.
    """
    mgr = _get_sync_manager()
    executed = mgr.fetch_and_execute_pending_cloud_tasks()
    if not executed:
        return "Cloud Task Mailbox: Synchronized. No pending offline directives found."

    lines = [f"Successfully synchronized and executed {len(executed)} offline cloud directive(s):"]
    for item in executed:
        lines.append(f"- [{item['id']}] '{item['command']}': {item['result'][:80]}")
    return "\n".join(lines)


def send_wake_on_lan_signal(mac_address: str, broadcast_ip: str = "255.255.255.255") -> str:
    """
    Transmit a Wake-on-LAN (WoL) magic packet to remotely wake or power on a computer or laptop.
    
    Args:
        mac_address: Target network interface MAC address (e.g., '00:11:22:33:44:55').
        broadcast_ip: Network broadcast address (default: 255.255.255.255).
    """
    res = CloudSyncManager.send_wake_on_lan(mac_address, broadcast_ip=broadcast_ip)
    return res["message"]
