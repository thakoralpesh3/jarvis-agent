"""
Daily Briefing Tool for JARVIS.
"""


def get_daily_briefing() -> str:
    """
    Generate and deliver the Stark Industries daily morning/startup briefing,
    including system health, battery, and daily YouTube Shorts agent status.
    """
    from core.briefing import DailyBriefingEngine
    engine = DailyBriefingEngine()
    return engine.deliver_briefing(play_voice=True)
