"""
Local Laptop Cloud Synchronization Engine for Aradhya.
Maintains continuous two-way sync between the physical laptop (Node A)
and the 24/7 Cloud Standby Sentinel (Node B).
Handles heartbeats, auto-pulling and executing directives queued while the laptop was off,
and Wake-on-LAN magic packet actuation.
"""

import os
import sys
import json
import time
import socket
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from config.settings import JarvisConfig, load_config
from tools.laptop_work_tools import send_desktop_notification
from tools.ironman_protocols import play_stark_sound


class CloudSyncManager:
    """
    Manages synchronization between local laptop and cloud sentinel.
    Keeps the cloud informed of laptop availability, and executes tasks
    commanded by Alpesh Sir from his mobile phone while the laptop was powered down.
    """

    def __init__(self, config: Optional[JarvisConfig] = None, cloud_url: Optional[str] = None):
        self.config = config or load_config()
        self.cloud_url = (cloud_url or os.getenv("ARADHYA_CLOUD_URL", os.getenv("AROHI_CLOUD_URL", "http://127.0.0.1:8080"))).rstrip("/")
        self.timeout = 2.5

    def _http_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None, method: str = "GET") -> Optional[Dict[str, Any]]:
        url = f"{self.cloud_url}{endpoint}"
        try:
            req_data = json.dumps(data).encode("utf-8") if data is not None else None
            headers = {"Content-Type": "application/json"} if req_data else {}
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            # Fallback to local shared data store if targeting localhost
            if "127.0.0.1" in self.cloud_url or "localhost" in self.cloud_url:
                data_dir = Path.home() / ".jarvis" / "cloud_data"
                hb_file = data_dir / "laptop_heartbeat.json"
                queue_file = data_dir / "cloud_tasks.json"

                if endpoint == "/api/heartbeat" and method == "POST":
                    try:
                        data_dir.mkdir(parents=True, exist_ok=True)
                        hb_data = {"timestamp": time.time(), "time_str": time.strftime("%Y-%m-%d %H:%M:%S"), "info": data or {}}
                        hb_file.write_text(json.dumps(hb_data, indent=2), encoding="utf-8")
                        return {"status": "ok", "laptop_online": True}
                    except Exception:
                        pass

                if endpoint == "/api/tasks/pending" and method == "GET":
                    if queue_file.exists():
                        try:
                            tasks = json.loads(queue_file.read_text(encoding="utf-8") or "[]")
                            pending = [t for t in tasks if t.get("status") == "pending_laptop_wake"]
                            return {"tasks": pending}
                        except Exception:
                            pass
                    return {"tasks": []}

                if endpoint == "/api/tasks/complete" and method == "POST":
                    if queue_file.exists() and data:
                        try:
                            tasks = json.loads(queue_file.read_text(encoding="utf-8") or "[]")
                            for t in tasks:
                                if t.get("id") == data.get("task_id"):
                                    t["status"] = "completed" if data.get("success", True) else "failed"
                                    t["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                                    t["result"] = data.get("result")
                                    break
                            queue_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
                            return {"status": "updated", "success": True}
                        except Exception:
                            pass

                if endpoint == "/api/status" and method == "GET":
                    is_online = False
                    if hb_file.exists():
                        try:
                            hdata = json.loads(hb_file.read_text(encoding="utf-8"))
                            is_online = (time.time() - hdata.get("timestamp", 0)) < 180
                        except Exception:
                            pass
                    pending_count = 0
                    if queue_file.exists():
                        try:
                            tasks = json.loads(queue_file.read_text(encoding="utf-8") or "[]")
                            pending_count = len([t for t in tasks if t.get("status") == "pending_laptop_wake"])
                        except Exception:
                            pass
                    return {
                        "agent_name": "Aradhya",
                        "cloud_sentinel_online": True,
                        "laptop_online": is_online,
                        "laptop_status": "ONLINE (Local Actuation Active)" if is_online else "OFFLINE / ASLEEP (Cloud Sentinel Active)",
                        "pending_tasks_count": pending_count
                    }

            return None

    # -------------------------------------------------------------------------
    # 1. Heartbeat Transmitter
    # -------------------------------------------------------------------------
    def send_heartbeat(self) -> bool:
        """Transmit telemetry ping to Cloud Sentinel to signal that laptop is online."""
        try:
            battery = psutil.sensors_battery()
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()

            payload = {
                "hostname": socket.gethostname(),
                "battery_percent": int(battery.percent) if battery else None,
                "power_plugged": bool(battery.power_plugged) if battery else True,
                "cpu_percent": round(cpu, 1),
                "ram_percent": round(mem.percent, 1),
                "agent_status": "ONLINE"
            }
            res = self._http_request("/api/heartbeat", data=payload, method="POST")
            return res is not None and res.get("status") == "ok"
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # 2. Pull and Execute Offline Cloud Tasks
    # -------------------------------------------------------------------------
    def fetch_pending_tasks(self) -> List[Dict[str, Any]]:
        """Query Cloud Sentinel for any directives queued while laptop was turned off."""
        res = self._http_request("/api/tasks/pending", method="GET")
        if res and isinstance(res.get("tasks"), list):
            return res["tasks"]
        return []

    def report_task_complete(self, task_id: str, result: Any, success: bool = True) -> bool:
        """Report completion of a cloud directive back to Cloud Sentinel."""
        payload = {
            "task_id": task_id,
            "result": str(result),
            "success": success
        }
        res = self._http_request("/api/tasks/complete", data=payload, method="POST")
        return res is not None and res.get("status") == "updated"

    def fetch_and_execute_pending_cloud_tasks(self, agent=None) -> List[Dict[str, Any]]:
        """
        Main boot & recovery routine:
        Queries Cloud Sentinel for all offline queued directives, executes them end-to-end,
        reports results back to cloud, and posts a desktop notification.
        """
        pending = self.fetch_pending_tasks()
        if not pending:
            return []

        executed = []
        from core.laptop_work_executor import LaptopWorkExecutor
        executor = LaptopWorkExecutor(agent=agent)

        for item in pending:
            task_id = item.get("id")
            cmd = item.get("command", "")
            if not cmd or not task_id:
                continue

            # Execute the directive
            try:
                exec_res = executor.execute_mission(cmd)
                success = True
                result_summary = exec_res.get("summary", "") if isinstance(exec_res, dict) else str(exec_res)
            except Exception as e:
                success = False
                result_summary = f"Error executing cloud directive: {str(e)}"

            # Report back to Cloud Sentinel
            self.report_task_complete(task_id, result_summary, success=success)
            executed.append({"id": task_id, "command": cmd, "result": result_summary, "success": success})

            # Send local notification
            send_desktop_notification(
                "Aradhya Cloud Directive Executed",
                f"Completed offline order: {cmd[:50]}",
                details=result_summary,
                urgency="normal",
                user_commanded=True
            )

        if executed:
            play_stark_sound("protocol")

        return executed

    # -------------------------------------------------------------------------
    # 3. Wake-on-LAN (WoL) Remote Power-On Magic Packet
    # -------------------------------------------------------------------------
    @staticmethod
    def send_wake_on_lan(mac_address: str, broadcast_ip: str = "255.255.255.255", port: int = 9) -> Dict[str, Any]:
        """
        Send a Wake-on-LAN (WoL) Magic Packet across UDP broadcast to remotely
        wake or power on the laptop if Wake-on-LAN is supported by NIC / BIOS.
        
        Args:
            mac_address: Hardware MAC address (e.g. '00:11:22:33:44:55' or '00-11-22-33-44-55').
            broadcast_ip: Network broadcast address (default: 255.255.255.255).
            port: UDP destination port (standard is 9 or 7).
        """
        clean_mac = mac_address.replace(":", "").replace("-", "").replace(".", "")
        if len(clean_mac) != 12:
            return {
                "success": False,
                "message": f"Invalid MAC address format: '{mac_address}'. Expected 12 hexadecimal digits."
            }

        try:
            mac_bytes = bytes.fromhex(clean_mac)
            # Magic packet: 6 bytes of 0xFF followed by MAC address repeated 16 times
            magic_packet = b"\xff" * 6 + mac_bytes * 16

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic_packet, (broadcast_ip, port))

            return {
                "success": True,
                "message": f"Wake-on-LAN magic packet successfully transmitted to {mac_address} via {broadcast_ip}:{port}."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error transmitting Wake-on-LAN packet: {str(e)}"
            }
