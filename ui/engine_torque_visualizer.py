"""
Interactive Engine Blueprint & Factory Torque Visualizer for Royal Enfield.
Provides precise factory tightening torques (Nm), bolt sequence patterns, and lubrication requirements.
"""

from typing import Any, Dict, List, Optional
from tools.ironman_protocols import play_stark_sound


RE_TORQUE_SPECIFICATIONS = {
    "J-Series 350 (Classic, Hunter, Meteor, Bullet)": [
        {"component": "Cylinder Head Main Stud Nuts (M10)", "torque_nm": "40 Nm", "sequence": "Criss-Cross in 3 stages (15Nm -> 28Nm -> 40Nm)", "notes": "Engine oil on threads"},
        {"component": "Cylinder Head Perimeter Flange Bolts (M6)", "torque_nm": "10 Nm", "sequence": "Opposite diagonal", "notes": "Dry"},
        {"component": "Tappet Rocker Cover Bolts", "torque_nm": "10 Nm", "sequence": "Even diagonal", "notes": "Do not overtighten; check rubber gasket"},
        {"component": "Clutch Hub Center Nut (Left-Hand Thread)", "torque_nm": "75 Nm", "sequence": "Direct lock with clutch holder tool", "notes": "Use medium-strength threadlocker"},
        {"component": "Stator Magneto Rotor Center Bolt", "torque_nm": "85 Nm", "sequence": "Direct with flywheel holder", "notes": "Clean taper dry"},
        {"component": "Engine Oil Drain Bolt & Strainer Cover", "torque_nm": "24 Nm / 10 Nm", "sequence": "Single", "notes": "Replace copper washer"},
        {"component": "Spark Plug (M12)", "torque_nm": "14 Nm", "sequence": "Hand tight + 1/2 turn", "notes": "Never cross-thread cold head"},
        {"component": "Front Axle Spindle / Rear Axle Nut", "torque_nm": "70 Nm / 100 Nm", "sequence": "Torque wrench on axle nut only", "notes": "Grease spindle shaft"}
    ],
    "650 Twins (Continental GT, Interceptor, Super Meteor)": [
        {"component": "Cylinder Head Main Bolts (M10)", "torque_nm": "45 Nm", "sequence": "Spiral outward from center bolts", "notes": "Engine oil on threads & washers"},
        {"component": "Camshaft Bearing Carrier Caps", "torque_nm": "10 Nm", "sequence": "Even progressive 2-stage", "notes": "Crucial: do not tilt caps"},
        {"component": "Slipper Clutch Center Nut", "torque_nm": "80 Nm", "sequence": "Locked", "notes": "Blue Loctite 243"},
        {"component": "Exhaust Header Pipe Flange Nuts", "torque_nm": "18 Nm", "sequence": "Even pair tightening", "notes": "New copper crush washers"}
    ]
}


class EngineTorqueVisualizer:
    """Delivers precise factory torque tightening charts and bolt sequences."""

    def get_torque_spec_sheet(self, platform: str = "J-Series 350") -> Dict[str, Any]:
        """Retrieve factory torque specifications and sequence guidelines."""
        play_stark_sound("protocol")
        
        target_key = next((k for k in RE_TORQUE_SPECIFICATIONS if platform.lower() in k.lower()), list(RE_TORQUE_SPECIFICATIONS.keys())[0])
        specs = RE_TORQUE_SPECIFICATIONS[target_key]

        lines = [f"### 🧩 Royal Enfield Factory Torque & Bolt Sequence ({target_key}):\n"]
        for s in specs:
            lines.append(f"- **{s['component']}:** **`{s['torque_nm']}`**")
            lines.append(f"  Sequence: _{s['sequence']}_ | Note: {s['notes']}\n")

        return {
            "platform": target_key,
            "specs": specs,
            "report": "\n".join(lines)
        }
