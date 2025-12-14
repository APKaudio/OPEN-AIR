import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog
from collections import defaultdict

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


Local_Debug_Enable = True


def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)


# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[5]
current_file = str(current_file_path.relative_to(project_root)).replace("/", "/")

class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame that dynamically creates buttons for each marker in the MARKERS.csv file.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🟢 Initializing ShowtimeTab. Ready for showtime!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(parent, *args, **kwargs)

        self.mqtt_util = mqtt_util
        self.buttons = []
        self.marker_data = []
        self.column_headers = []
        self.grouped_markers = {}
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_button = None
        self.Local_Debug_Enable = Local_Debug_Enable
        self.current_file = current_file
        self.current_version = current_version


        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

        if not PANDAS_NUMPY_AVAILABLE:
            console_log_switch("❌ Critical dependencies 'pandas' or 'numpy' not found. Showtime tab will be disabled.")
            for widget in self.winfo_children():
                widget.destroy()
            error_label = ttk.Label(self, text="Error: NumPy and Pandas libraries are required for this tab.", foreground="red")
            error_label.pack(pady=20)
            return
        
        parent_notebook = parent.master
        parent_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)
        
        self._on_tab_selected(None)

    def _apply_styles(self, theme_name: str):
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        # FIXED: Apply wraplength to the base button style for consistent wrapping.
        style.configure('Custom.TButton',
                        background=colors["button_style_toggle"]["background"],
                        foreground=colors["button_style_toggle"]["foreground"],
                        padding=10, relief=colors["relief"],
                        wraplength=150,
                        borderwidth=colors["border_width"])
        style.map('Custom.TButton',
                  background=[('pressed', colors["accent"]), 
                              ('active', colors["hover_blue"])])
    
        style.configure('Group.TLabel',
                        background=colors["primary"],
                        foreground=colors["accent"],
                        font=('Helvetica', 12, 'bold'))

        style.configure('Zone.TLabel',
                        background=colors["primary"],
                        foreground=colors["fg"],
                        font=('Helvetica', 14, 'bold'))

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🟢 Creating the three-pane filter layout.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_scroll_frame = ttk.Frame(self, padding=(5,5,5,5))
        self.main_scroll_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.canvas = tk.Canvas(self.main_scroll_frame, bg=THEMES[DEFAULT_THEME]["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.filter_frame = ttk.Frame(self.scrollable_frame)
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)
        self.filter_frame.grid_columnconfigure(0, weight=1)
        
        reset_button = ttk.Button(self.filter_frame, text="Reset All Filters", command=self._reset_filters)
        reset_button.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.zone_frame = ttk.LabelFrame(self.filter_frame, text="ZONES")
        self.zone_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.zone_frame.grid_columnconfigure(0, weight=1)
        self.zone_frame.grid_columnconfigure(1, weight=1)
        self.zone_frame.grid_columnconfigure(2, weight=1)
        self.zone_frame.grid_columnconfigure(3, weight=1)
        
        self.group_frame = ttk.LabelFrame(self.filter_frame, text="GROUPS")
        self.group_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.group_frame.grid_columnconfigure(0, weight=1)
        self.group_frame.grid_columnconfigure(1, weight=1)
        self.group_frame.grid_columnconfigure(2, weight=1)
        self.group_frame.grid_columnconfigure(3, weight=1)

        self.device_frame = ttk.LabelFrame(self.filter_frame, text="DEVICES")
        self.device_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.device_frame.grid_columnconfigure(0, weight=1)
        self.device_frame.grid_columnconfigure(1, weight=1)
        self.device_frame.grid_columnconfigure(2, weight=1)
        self.device_frame.grid_columnconfigure(3, weight=1)
        
    def _reset_filters(self):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🔵 Resetting all filters and rebuilding the UI.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        self.selected_zone = None
        self.selected_group = None
        if self.selected_device_button:
            self.selected_device_button.config(style='Custom.TButton')
            self.selected_device_button = None
            
        load_marker_data(self)
        process_and_sort_markers(self)
        self._create_zone_buttons()
        create_group_buttons(self)
        create_device_buttons(self)
        console_log_switch("✅ Filters reset. All markers displayed.")

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
            self._create_zone_buttons()
            create_group_buttons(self)
            create_device_buttons(self)

    def _create_zone_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🟢 Creating Zone filter buttons.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        for widget in self.zone_frame.winfo_children():
            widget.destroy()

        sorted_zones = sorted(self.grouped_markers.keys())
        for i, zone_name in enumerate(sorted_zones):
            is_selected = self.selected_zone == zone_name
            
            all_zone_devices = []
            for group in self.grouped_markers[zone_name].values():
                all_zone_devices.extend(group)
            # UPDATED: Use the imported utility function
            min_freq, max_freq = calculate_frequency_range(all_zone_devices)
            
            freq_range_text = ""
            if min_freq is not None and max_freq is not None:
                freq_range_text = f"\n{min_freq} MHz - {max_freq} MHz"

            button_text = f"{zone_name}{freq_range_text}"

            button = ttk.Button(
                self.zone_frame,
                text=button_text,
                command=lambda z=zone_name: self._on_zone_toggle(z),
                style='Custom.TButton' if not is_selected else 'Custom.Selected.TButton'
            )
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        for i in range(4):
            self.zone_frame.grid_columnconfigure(i, weight=1)
        
        if Local_Debug_Enable:
            debug_log(
                message=f"✅ Zone buttons created for {len(sorted_zones)} zones.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        



            
    def _on_zone_toggle(self, zone_name):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🔵 Zone toggle clicked for: {zone_name}. Current selection: {self.selected_zone}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        if self.selected_zone == zone_name:
            self.selected_zone = None
            self.selected_group = None
            if Local_Debug_Enable:
                debug_log(
                    message="🛠️🟡 Deselected Zone. Clearing Group selection.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )
        else:
            self.selected_zone = zone_name
            self.selected_group = None
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🟢 Selected new Zone: {self.selected_zone}. Clearing Group selection.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )
        
        self._create_zone_buttons()
        create_group_buttons(self)
        create_device_buttons(self)
        
        on_tune_request_from_selection(self)
        
    def _on_group_toggle(self, group_name):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🔵 Group toggle clicked for: {group_name}. Current selection: {self.selected_group}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        if self.selected_group == group_name:
            self.selected_group = None
            if Local_Debug_Enable:
                debug_log(
                    message="🛠️🟡 Deselected Group. Showing all devices for the current Zone.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )
        else:
            self.selected_group = group_name
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🟢 Selected new Group: {self.selected_group}.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function}",
                    console_print_func=console_log
                )
            
        create_group_buttons(self)
        create_device_buttons(self)
        
        on_tune_request_from_selection(self)
        
    def _clear_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🔵 Clearing group buttons.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        for widget in self.group_frame.winfo_children():
            widget.destroy()

    def _on_marker_button_click(self, button):
        current_function = inspect.currentframe().f_code.co_name
        if Local_Debug_Enable:
            debug_log(
                message="🛠️🔵 Device button clicked. Toggling selection.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        marker_data = button.marker_data
        
        if self.selected_device_button == button:
            self.selected_device_button.config(style='Custom.TButton')
            self.selected_device_button = None
            console_log_switch(f"🟡 Deselected device: {marker_data.get('NAME', 'N/A')}.")
        else:
            if self.selected_device_button:
                self.selected_device_button.config(style='Custom.TButton')
            
            self.selected_device_button = button
            self.selected_device_button.config(style='Custom.Selected.TButton')
            console_log_switch(f"✅ Selected device: {marker_data.get('NAME', 'N/A')} at {marker_data.get('FREQ_MHZ', 'N/A')} MHz.")
        
        on_tune_request_from_selection(self)