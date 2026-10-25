"""
Translucent Floating Stark Arc-Reactor Desktop HUD Widget for JARVIS & Chamunda CEO.
Displays live telemetry, CPU/RAM load, Chamunda workshop metrics, and quick executive triggers.
"""

import os
import sys
import psutil
import threading
from pathlib import Path
from typing import Optional

from tools.ironman_protocols import play_stark_sound


def launch_arc_reactor_widget():
    """Launch Tkinter-powered floating Stark Arc Reactor desktop HUD."""
    play_stark_sound("startup")
    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title("JARVIS Mark VII • Arc Reactor HUD")
        root.geometry("380x300+40+40")
        root.configure(bg="#051510")
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.92)

        # Styling
        title_lbl = tk.Label(
            root,
            text="⚡ JARVIS MARK VII • ARC REACTOR HUD",
            font=("Segoe UI", 12, "bold"),
            fg="#c5a059",
            bg="#051510"
        )
        title_lbl.pack(pady=8)

        # Core Metrics Frame
        frame = tk.Frame(root, bg="#0d2b22", bd=2, relief="groove")
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        cpu_lbl = tk.Label(frame, text="CPU Load: Scanning...", font=("Segoe UI", 10), fg="#e0e0e0", bg="#0d2b22")
        cpu_lbl.pack(anchor="w", padx=10, pady=3)

        mem_lbl = tk.Label(frame, text="RAM Usage: Scanning...", font=("Segoe UI", 10), fg="#e0e0e0", bg="#0d2b22")
        mem_lbl.pack(anchor="w", padx=10, pady=3)

        batt_lbl = tk.Label(frame, text="Power Reserve: Scanning...", font=("Segoe UI", 10), fg="#e0e0e0", bg="#0d2b22")
        batt_lbl.pack(anchor="w", padx=10, pady=3)

        chamunda_lbl = tk.Label(
            frame,
            text="🏍️ Chamunda RE: Live Enterprise Sync",
            font=("Segoe UI", 10, "bold"),
            fg="#c5a059",
            bg="#0d2b22"
        )
        chamunda_lbl.pack(anchor="w", padx=10, pady=5)

        # Update telemetry loop
        def update_stats():
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                batt = psutil.sensors_battery()
                batt_txt = f"{batt.percent}%" if batt else "AC Power"

                cpu_lbl.config(text=f"⚙️ CPU Load: {cpu}%")
                mem_lbl.config(text=f"🧠 RAM Usage: {mem}%")
                batt_lbl.config(text=f"🔋 Power Reserve: {batt_txt}")
            except Exception:
                pass
            root.after(2000, update_stats)

        update_stats()

        # Action Buttons
        btn_frame = tk.Frame(root, bg="#051510")
        btn_frame.pack(fill="x", padx=15, pady=10)

        def on_optimize():
            from tools.system_optimizer_tools import optimize_laptop_performance
            optimize_laptop_performance()

        def on_briefing():
            from tools.briefing_tools import get_daily_briefing
            get_daily_briefing()

        opt_btn = tk.Button(btn_frame, text="⚡ Optimize", bg="#1b4d3e", fg="#ffe29a", font=("Segoe UI", 9, "bold"), command=on_optimize)
        opt_btn.pack(side="left", fill="x", expand=True, padx=2)

        brief_btn = tk.Button(btn_frame, text="🌅 Briefing", bg="#1b4d3e", fg="#ffe29a", font=("Segoe UI", 9, "bold"), command=on_briefing)
        brief_btn.pack(side="left", fill="x", expand=True, padx=2)

        root.mainloop()
    except Exception as e:
        print(f"Error launching HUD: {str(e)}")


if __name__ == "__main__":
    launch_arc_reactor_widget()
