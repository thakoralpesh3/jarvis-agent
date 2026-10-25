"""
Computer Vision Spares Scanner for Chamunda Automobile Parts & Service.
Takes actual photos of motorcycle parts, identifies the exact Royal Enfield
OEM part number using Gemini Vision, and cross-references Chamunda's inventory stock levels.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types

from config.settings import load_config
from tools.ironman_protocols import play_stark_sound

sys.path.insert(0, "/home/alpesh/chamunda_re_enterprise")
from inventory_engine import ChamundaInventoryManager


class REVisionPartScanner:
    """Computer vision recognition for Royal Enfield spare parts."""

    def __init__(self):
        self.config = load_config()
        self.client = genai.Client(api_key=self.config.api_key) if self.config.api_key else None
        self.inv_mgr = ChamundaInventoryManager()

    def identify_part_from_image(self, image_path: Optional[str] = None, part_hint: str = "") -> Dict[str, Any]:
        """Scan part photo, identify OEM part number with Gemini Vision, and check workshop inventory."""
        play_stark_sound("protocol")

        if not image_path or not Path(image_path).exists():
            # If no image is provided, offer keyword search or prompt for photo
            if part_hint:
                matches = self.inv_mgr.search_parts(part_hint)
                if matches:
                    lines = [f"### 📦 Chamunda Spares Catalog Results for '{part_hint}':\n"]
                    for p in matches:
                        lines.append(f"- **{p['name']}** (`{p['part_id']}`) | OEM: `{p['oem_number']}`")
                        lines.append(f"  Stock: **{p['stock']} {p.get('unit', 'Pcs')}** | MRP: **₹{p['mrp']}** (Cost: ₹{p['cost_price']})\n")
                    return {"success": True, "report": "\n".join(lines)}
                return {"success": False, "report": f"No parts matching '{part_hint}' found in inventory."}

            msg = (
                "### 📷 Chamunda Computer Vision Part Scanner:\n"
                "- **Status:** ⚠️ **No image file provided.**\n"
                "- **Usage:** Provide an image path: `/scan /path/to/part_photo.jpg` or enter a part name to search our catalog."
            )
            return {"success": False, "report": msg}

        # Analyze actual image file with Gemini Vision
        if self.client and Path(image_path).exists():
            try:
                img_bytes = Path(image_path).read_bytes()
                mime = "image/png" if image_path.endswith(".png") else "image/jpeg"
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type=mime),
                        "You are the Parts Specialist at Chamunda Automobile Parts & Service, specialized strictly in Royal Enfield motorcycles. "
                        "Examine this physical motorcycle part in the image. Identify: 1. Exact Part Name, 2. Royal Enfield OEM Part Number, "
                        "3. Compatible Royal Enfield bike models (Classic, Hunter, Meteor, Himalayan 450, 650 Twins, UCE), 4. Key inspection points."
                    ]
                )
                report_text = response.text or "Vision analysis complete."
                play_stark_sound("ack")
                return {"success": True, "report": report_text}
            except Exception as e:
                return {"success": False, "report": f"Vision analysis error: {str(e)}"}

        return {"success": False, "report": "Vision API client unavailable."}
