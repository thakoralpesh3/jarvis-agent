"""
Screen capture and desktop vision tools for JARVIS.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime


def capture_screen(output_path: Optional[str] = None) -> str:
    """
    Capture a screenshot of the user's primary monitor to observe what is currently on the screen.
    
    Args:
        output_path: Optional path to save the screenshot image. If not specified, saves to /tmp/jarvis_screenshot.png.
    """
    try:
        import mss
        
        target = Path(output_path) if output_path else Path(f"/tmp/jarvis_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        target.parent.mkdir(parents=True, exist_ok=True)

        with mss.mss() as sct:
            # Capture the primary monitor
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=str(target))

        return f"Screenshot successfully saved to '{str(target)}' ({monitor['width']}x{monitor['height']})."
    except Exception as e:
        return f"Error capturing screen: {str(e)}"
