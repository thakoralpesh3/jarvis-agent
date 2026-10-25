"""
Chamunda Riders Club & WhatsApp Event Concierge for Royal Enfield Owners.
Manages customer community rides, monsoon checkup camps, and automated broadcast campaigns.
"""

import json
import time
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import DEFAULT_CONFIG_DIR


EVENTS_FILE = DEFAULT_CONFIG_DIR / "chamunda_riders_events.json"


class ChamundaRidersClubManager:
    """Manages Royal Enfield community rides, camps, and customer retention campaigns."""

    def __init__(self, events_file: Path = EVENTS_FILE):
        self.events_file = events_file
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.events_file.exists():
            self.events_file.write_text("[]", encoding="utf-8")

    def get_all_events(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.events_file.read_text(encoding="utf-8") or "[]")
        except Exception:
            return []

    def create_event(self, title: str, date: str, destination: str, perks: str) -> Dict[str, Any]:
        """Create a new ride event and generate WhatsApp broadcast copy."""
        today_ym = datetime.datetime.now().strftime('%Y%m')
        events = self.get_all_events()
        event_id = f"RIDE-{today_ym}-{len(events) + 1:03d}"
        
        wa_text = (
            f"🏍️ *CHAMUNDA RIDERS CLUB: {title.upper()}* 🏍️\n\n"
            f"📅 *Date:* {date}\n"
            f"🛣️ *Destination:* {destination}\n"
            f"★ *Rider Perks:* {perks}\n\n"
            f"📍 *Organized by:* Chamunda Automobile Parts & Service\n"
            f"Reply 'RIDE' to reserve your spot!"
        )

        event = {
            "event_id": event_id,
            "title": title,
            "date": date,
            "destination": destination,
            "perks": perks,
            "whatsapp_broadcast": wa_text
        }

        events.insert(0, event)
        self.events_file.write_text(json.dumps(events, indent=2), encoding="utf-8")
        return event
