# workers/Showtime/worker_showtime_create_zone_buttons.py
#
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213
Current_Time = 120000
Current_iteration = 44

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#

import inspect
import tkinter as tk
from tkinter import ttk
from display.logger import debug_log, console_log
from workers.Showtime.worker_showtime_on_zone_toggle import on_zone_toggle

Local_Debug_Enable = True

def create_zone_buttons(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message="🛠️🟢 Creating Zone buttons.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
    
    # Clear existing zone buttons
    for widget in showtime_tab_instance.zones_frame.winfo_children():
        widget.destroy()

    zone_buttons_frame = ttk.Frame(showtime_tab_instance.zones_frame)
    zone_buttons_frame.pack(fill=tk.X, padx=5, pady=2)

    for zone_name in sorted(showtime_tab_instance.grouped_markers.keys()):
        zone_button = ttk.Button(
            zone_buttons_frame,
            text=zone_name,
            command=lambda zn=zone_name: on_zone_toggle(showtime_tab_instance, zn),
            style='Custom.TButton'
        )
        zone_button.pack(side=tk.LEFT, padx=2, pady=2)
        if Local_Debug_Enable:
            debug_log(
                message=f"✅ Created button for Zone: {zone_name}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
