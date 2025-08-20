# tabs/Markers/showtime/storage_showtime_shared.py
#
# [This file defines a centralized class for managing shared state variables
# used across the Showtime tab and its child components.]
#
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
#
# Version 20250820.115620.1
# FIXED: Updated versioning to adhere to project standards.

import tkinter as tk
import os
from datetime import datetime

# --- Versioning ---
w = 20250820
x_str = '115620'
x = 115620
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

class ShowtimeSharedState:
    """
    A centralized storage class for all state variables shared across the
    Showtime tab's various frames and utilities. This ensures a single source
    of truth for UI state and selections.
    """
    def __init__(self):
        # [Initializes all shared state variables for the Showtime tab.]
        
        # --- UI Element References ---
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        self.device_buttons = {}
        self.zone_zoom_buttons = {}

        # --- Tkinter State Variables ---
        self.span_var = tk.StringVar(value="50M")
        self.rbw_var = tk.StringVar(value="300k")
        self.poke_freq_var = tk.StringVar(value="")
        self.follow_zone_span_var = tk.BooleanVar(value=False)
        
        # Labels for the Zone Zoom functionality
        self.zone_zoom_label_left_var = tk.StringVar(value="Select Zone/Group/Device")
        self.zone_zoom_label_center_var = tk.StringVar(value="N/A")
        self.zone_zoom_label_right_var = tk.StringVar(value="N/A")

        # Toggles for trace modes
        self.toggle_get_all_traces = tk.BooleanVar(value=False)
        self.toggle_get_live_trace = tk.BooleanVar(value=True)
        self.toggle_get_max_traces = tk.BooleanVar(value=False)
        
        self.trace_modes = {
            'live': self.toggle_get_live_trace,
            'max': self.toggle_get_max_traces,
            'all': self.toggle_get_all_traces
        }

        # --- Selection State ---
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_info = None
        self.last_selected_button = None
        self.active_device_button = None