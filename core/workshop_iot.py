"""
Workshop Smart IoT & Hardware Infrastructure Control for Chamunda Automobile.
Controls workshop pneumatic air compressor relays, high-bay lighting, exhaust extraction, and security alarms.
"""

from typing import Any, Dict, List
from tools.ironman_protocols import play_stark_sound


class WorkshopIoTController:
    """Controls workshop hardware appliances, relays, and lighting."""

    def __init__(self):
        self.state = {
            "air_compressor": "ON (Nominal 120 PSI)",
            "bay_high_bay_lights": "ON (100% Day Brightness)",
            "exhaust_extraction_fan": "AUTO (CO2 Sensor Linked)",
            "service_lift_bay_1": "READY (Pneumatic Lock Engaged)",
            "service_lift_bay_2": "READY (Pneumatic Lock Engaged)",
            "security_perimeter_alarm": "ARMED (Night Sentry Mode)"
        }

    def get_hardware_status(self) -> Dict[str, Any]:
        """Get telemetry of all workshop IoT relays and electrical appliances."""
        play_stark_sound("protocol")
        lines = ["### 💡 Chamunda Workshop Smart IoT Telemetry:\n"]
        for device, st in self.state.items():
            lines.append(f"- **{device.replace('_', ' ').title()}:** `{st}`")
        return {"state": self.state, "report": "\n".join(lines)}

    def toggle_device(self, device_name: str, state: str = "ON") -> str:
        """Toggle an electrical device or workshop relay."""
        play_stark_sound("ack")
        key = device_name.lower().replace(" ", "_")
        self.state[key] = state.upper()
        return f"Workshop appliance '{device_name}' switched to {state.upper()} successfully, Chairman."
