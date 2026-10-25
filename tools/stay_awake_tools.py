"""
Work StayAwake Sentry Tools for Aradhya.
Allows inspecting and controlling sleep and lockscreen inhibition during active work.
"""

from typing import Dict, Any, Optional
from config.settings import load_config


_sentry_instance: Optional[Any] = None


def _get_sentry() -> Any:
    global _sentry_instance
    if _sentry_instance is None:
        from core.stay_awake_sentry import StayAwakeSentry
        cfg = load_config()
        _sentry_instance = StayAwakeSentry(cfg)
    return _sentry_instance


def inspect_stay_awake_status() -> str:
    """
    Inspect whether the laptop is currently protected from sleep and lockscreen due to active work.
    Lists any detected active work applications (e.g. Antigravity, LibreOffice, terminals, IDEs)
    and the status of FreeDesktop ScreenSaver and systemd inhibitors.
    """
    sentry = _get_sentry()
    status = sentry.get_status_report()

    inhibited_badge = "🛡️ ACTIVE (Sleep & Lockscreen Inhibited)" if status["is_inhibited"] else "🌙 STANDBY (Normal Sleep Allowed)"
    work_badge = "💼 ACTIVE WORK IN PROGRESS" if status["is_work_active"] else "☕ NO ACTIVE WORK APPS"

    apps_lines = [f"  - `{app}`" for app in status["active_work_apps"]]

    gujarati_msg = (
        f"જી સાહેબ! હાલમાં લેપટોપ પર કામ ચાલુ હોવાથી સ્લીપ અને લોકસ્ક્રીન બંધ રાખવામાં આવેલ છે. "
        f"સક્રિય એપ્લિકેશન્સ: {', '.join(status['active_work_apps']) if status['active_work_apps'] else 'કોઈ નથી'}."
        if status["is_inhibited"] else
        "જી સાહેબ, હાલમાં કોઈ સક્રિય કામ ચાલી રહ્યું નથી, તેથી સામાન્ય પાવર સેવિંગ મોડ ચાલુ છે."
    )

    english_msg = (
        f"Sir, sleep and lockscreen are actively inhibited while you work. "
        f"Active applications: {', '.join(status['active_work_apps']) if status['active_work_apps'] else 'None'}."
        if status["is_inhibited"] else
        "Sir, no active work applications are currently detected. Standard power saving is active."
    )

    return f"""### 🛡️ Aradhya Work StayAwake Sentry Status (સ્ટે અવેક સેન્ટ્રી સ્થિતિ)

> **ગુજરાતી:** {gujarati_msg}
>
> **English:** {english_msg}

---
- **Protection State:** **{inhibited_badge}**
- **Work State:** **{work_badge}**
- **D-Bus ScreenSaver Inhibit:** `{'Engaged (Cookie: ' + str(status['dbus_cookie']) + ')' if status['dbus_cookie'] else 'Inactive'}`
- **Systemd Sleep Inhibit:** `{'Engaged' if status['systemd_inhibit_active'] else 'Inactive'}`
- **Force Keep-Awake Mode:** `{'Enabled' if status['force_mode'] else 'Disabled (Auto-Detection Active)'}`
- **Current Status Reason:** *{status['status_reason']}*

**Detected Active Work Applications ({len(status['active_work_apps'])}):**
{chr(10).join(apps_lines) if apps_lines else '  - None'}
"""


def toggle_force_stay_awake(enable: bool = True, duration_minutes: int = 0) -> str:
    """
    Manually force the laptop to stay awake and prevent sleep/lockscreen, or restore automatic detection.

    Args:
        enable: Set to True to force the laptop awake, False to return to automatic work detection.
        duration_minutes: Optional duration in minutes (0 = indefinitely until turned off).
    """
    sentry = _get_sentry()
    res = sentry.set_force_mode(enable=enable, duration_minutes=duration_minutes)

    if enable:
        dur_text = f"આગામી {duration_minutes} મિનિટ માટે" if duration_minutes > 0 else "જ્યાં સુધી આપ બંધ ન કરો ત્યાં સુધી"
        gu_text = f"જી સાહેબ! લેપટોપને {dur_text} સ્લીપ કે લૉક થવાથી રોકી રાખવામાં આવ્યું છે."
    else:
        gu_text = "જી સાહેબ! ઓટોમેટિક વર્ક ડિટેક્શન પુનઃસ્થાપિત કરવામાં આવ્યું છે. જ્યારે કામ ચાલુ હશે ત્યારે જ સ્લીપ રોકાશે."

    return f"""### ⚡ Aradhya StayAwake Mode Updated
> **ગુજરાતી:** {gu_text}
>
> **English:** {res}
"""
