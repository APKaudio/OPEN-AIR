import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog
from collections import defaultdict


# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[5]
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")
Current_Date = 20251213
Current_Time = 120000
Current_iteration = 44





# --- Graceful Dependency Importing ---
try:
    import pandas as pd
    import numpy as np
    PANDAS_NUMPY_AVAILABLE = True
except ImportError:
    pd = None
    np = None
    PANDAS_NUMPY_AVAILABLE = False

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from workers.importers.worker_marker_file_import_handling import maker_file_check_for_markers_file
# FIXED: Importing tuning functions from the correct location.
from workers.active.worker_active_marker_tune_and_collect import Push_Marker_to_Center_Freq, Push_Marker_to_Start_Stop_Freq
# NEW: Import the refactored logic function
from workers.markers.worker_marker_logic import calculate_frequency_range
from display.styling.style import THEMES, DEFAULT_THEME
from workers.Showtime.worker_showtime_read import load_marker_data
from workers.Showtime.worker_showtime_group import process_and_sort_markers
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection
from workers.Showtime.worker_showtime_create_group_buttons import create_group_buttons
from workers.Showtime.worker_showtime_create_device_buttons import create_device_buttons
from workers.Showtime.worker_showtime_create_zone_buttons import create_zone_buttons # NEW IMPORT
from workers.Showtime.worker_showtime_on_marker_button_click import on_marker_button_click
from workers.Showtime.worker_showtime_clear_group_buttons import clear_group_buttons
from workers.Showtime.worker_showtime_on_zone_toggle import on_zone_toggle
from workers.Showtime.worker_showtime_on_group_toggle import on_group_toggle


Local_Debug_Enable = True

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"

class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame that dynamically creates buttons for each marker in the MARKERS.csv file.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)
        
        self.mqtt_util = mqtt_util
        self.current_file = current_file
        self.current_version = current_version
        self.Local_Debug_Enable = Local_Debug_Enable
        
        # State variables
        self.marker_data = []
        self.grouped_markers = defaultdict(lambda: defaultdict(list))
        self.column_headers = []
        
        # Selection state
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_button = None # Track the currently selected button widget
        
        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Initialized ShowtimeTab.",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name):
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe.Label', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"])
        
        # Custom button styles for toggle states
        style.configure('Custom.TButton', background=colors["accent"], foreground=colors["text"])
        style.configure('Custom.Selected.TButton', background=colors["secondary"], foreground=colors["text"], relief="sunken")

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        
        # Main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zones section
        self.zones_frame = ttk.LabelFrame(main_frame, text="Zones")
        self.zones_frame.pack(fill=tk.X, padx=5, pady=2)
        # Create zone buttons will go here.

        # Groups section
        self.group_frame = ttk.LabelFrame(main_frame, text="Groups")
        self.group_frame.pack(fill=tk.X, padx=5, pady=2)
        # Create group buttons will go here.

        # Devices section
        self.device_frame = ttk.LabelFrame(main_frame, text="Devices")
        self.device_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        # Create device buttons will go here.

        # Tune button
        tune_frame = ttk.Frame(main_frame)
        tune_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tune_button = ttk.Button(tune_frame, text="Tune", command=lambda: on_tune_request_from_selection(self))
        tune_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        debug_log(
            message=f"✅ Widgets created for ShowtimeTab.",
            file=self.current_file,
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        
        if event is None or event.widget.tab(event.widget.select(), "text") == "Showtime":
            if Local_Debug_Enable:
                debug_log(
                    message="🛠️🟢 'Showtime' tab activated. Reloading marker data and buttons.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )
            load_marker_data(self)
            process_and_sort_markers(self)
            create_zone_buttons(self)
            create_group_buttons(self)
            create_device_buttons(self)
    
            if Local_Debug_Enable:
                debug_log(
                    message="✅ 'Showtime' tab setup complete.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )

    # --- MISSING METHODS ADDED BELOW ---

    def _on_group_toggle(self, group_name):
        """Wrapper to call the imported on_group_toggle function."""
        on_group_toggle(self, group_name)

    def _on_marker_button_click(self, button):
        """Wrapper to call the imported on_marker_button_click function."""
        on_marker_button_click(self, button)