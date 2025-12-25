import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog
from collections import defaultdict
from workers.mqtt.setup.config_reader import Config # Import the Config class
app_constants = Config.get_instance() # Get the singleton instance

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
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.importers.worker_marker_file_import_handling import maker_file_check_for_markers_file
# FIXED: Importing tuning functions from the correct location.
# from workers.active.worker_active_marker_tune_and_collect import Push_Marker_to_Center_Freq, Push_Marker_to_Start_Stop_Freq
# NEW: Import the refactored logic function
from workers.markers.worker_marker_logic import calculate_frequency_range
from workers.styling.style import THEMES, DEFAULT_THEME
from workers.Showtime.worker_showtime_read import load_marker_data
from workers.Showtime.worker_showtime_group import process_and_sort_markers
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection
from workers.Showtime.worker_showtime_on_marker_button_click import on_marker_button_click
from workers.Showtime.worker_showtime_clear_group_buttons import clear_group_buttons
from workers.Showtime.worker_showtime_on_zone_toggle import on_zone_toggle
from workers.Showtime.worker_showtime_on_group_toggle import on_group_toggle


LOCAL_DEBUG_ENABLE = False

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"

class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame that dynamically creates buttons for each marker in the MARKERS.csv file.
    """
    def __init__(self, parent, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)
        
        self.current_file = current_file
        self.current_version = current_version
        self.LOCAL_DEBUG_ENABLE = LOCAL_DEBUG_ENABLE
        
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

        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🟢️️️🟢 Initialized ShowtimeTab.",
**_get_log_args()
                


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
        style.configure('Custom.TButton', background="#FF8C00", foreground=colors["text"])
        style.configure('Custom.Selected.TButton', background="#FFA500", foreground=colors["text"], relief="sunken")

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
          **_get_log_args()
            


        )

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        
        if event is None or event.widget.tab(event.widget.select(), "text") == "Showtime":
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message="🟢️️️🟢 'Showtime' tab activated. Reloading marker data and buttons.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    


                )
            load_marker_data(self)
            process_and_sort_markers(self)
            self._create_zone_buttons()
            self._create_group_buttons()
            self._create_device_buttons()
    
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message="✅ 'Showtime' tab setup complete.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    


                )

    # --- BUTTON CREATION METHODS ---

    def _create_zone_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        if self.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="🟢️️️🟢 Creating Zone buttons.",
        **_get_log_args()
                


            )
        
        # Clear existing zone buttons
        for widget in self.zones_frame.winfo_children():
            widget.destroy()

        zone_buttons_frame = ttk.Frame(self.zones_frame)
        zone_buttons_frame.pack(fill=tk.X, padx=5, pady=2)

        for zone_name in sorted(self.grouped_markers.keys()):
            zone_button = ttk.Button(
                zone_buttons_frame,
                text=zone_name,
                command=lambda zn=zone_name: self._on_zone_toggle(zn),
                style='Custom.TButton'
            )
            zone_button.pack(side=tk.LEFT, padx=2, pady=2)
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ Created button for Zone: {zone_name}.",
               **_get_log_args()

                )

    def _create_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        if self.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="🟢️️️🟢 Creating Group filter buttons.",
**_get_log_args()
                


            )
        
        for widget in self.group_frame.winfo_children():
            widget.destroy()
        
        if self.selected_zone:
            self.group_frame.configure(text=f"GROUPS")
            self.group_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
            
            sorted_groups = sorted(self.grouped_markers[self.selected_zone].keys())
            for i, group_name in enumerate(sorted_groups):
                is_selected = self.selected_group == group_name

                group_devices = self.grouped_markers[self.selected_zone][group_name]
                # UPDATED: Use the imported utility function
                min_freq, max_freq = calculate_frequency_range(group_devices)
                
                freq_range_text = ""
                if min_freq is not None and max_freq is not None:
                    freq_range_text = f"\\n{min_freq} MHz - {max_freq} MHz"
                
                button_text = f"{group_name}{freq_range_text}"
                
                button = ttk.Button(
                    self.group_frame,
                    text=button_text,
                    command=lambda g=group_name: self._on_group_toggle(g),
                    style='Custom.TButton' if not is_selected else 'Custom.Selected.TButton'
                )
                row = i // 4
                col = i % 4
                button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        else:
            self.group_frame.grid_remove()
            
        if self.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"✅ Group buttons updated for selected zone.",
**_get_log_args()
                


            )

    def _create_device_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        if self.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="🟢️️️🟢 Creating Device buttons.",
**_get_log_args()
                


            )
        
        if self.selected_device_button:
            self.selected_device_button.config(style='Custom.TButton')
        self.selected_device_button = None

        for widget in self.device_frame.winfo_children():
            widget.destroy()
        
        filtered_devices = []
        if self.selected_zone and self.selected_group:
            filtered_devices = self.grouped_markers[self.selected_zone][self.selected_group]
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🔍 Showing devices for Zone: {self.selected_zone} and Group: {self.selected_group}.",
**_get_log_args()               


                )
        elif self.selected_zone:
            for group_name in self.grouped_markers[self.selected_zone]:
                filtered_devices.extend(self.grouped_markers[self.selected_zone][group_name])
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🔍 Showing all devices for selected Zone: {self.selected_zone}.",
**_get_log_args()               


                )
        else:
            filtered_devices = self.marker_data
            if self.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message="🔍 Showing all devices from MARKERS.csv.",
**_get_log_args()               


                )

        for i, row_data in enumerate(filtered_devices):
            button_text = (
                           f"{row_data.get('NAME', 'N/A')}\\n"
                           f"{row_data.get('DEVICE', 'N/A')}\\n"
                           f"{row_data.get('FREQ_MHZ', 'N/A')} MHz\\n"
                           f"[********************]"
                          )
            
            button = ttk.Button(
                self.device_frame,
                text=button_text,
                style='Custom.TButton'
            )
            # Store data directly on the button object
            button.marker_data = row_data
            button.configure(command=lambda b=button: self._on_marker_button_click(b))
            
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        if self.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"✅ Created {len(filtered_devices)} device buttons.",
**_get_log_args()
                


            )

    # --- WRAPPER METHODS ---

    def _on_zone_toggle(self, zone_name):
        """Wrapper to call the imported on_zone_toggle function."""
        on_zone_toggle(self, zone_name)

    def _on_group_toggle(self, group_name):
        """Wrapper to call the imported on_group_toggle function."""
        on_group_toggle(self, group_name)

    def _on_marker_button_click(self, button):
        """Wrapper to call the imported on_marker_button_click function."""
        on_marker_button_click(self, button)