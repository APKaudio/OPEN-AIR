# OPEN-AIR/display/left_40/top_100/tab_2_markers/sub_tab_1_showtime/gui_child_1_showtime.py
#
# This file dynamically generates buttons for each marker in the MARKERS.csv file.
# It reloads and recreates the buttons every time the tab is made active.
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
# Version 20250922.145500.10
import tkinter as tk
from tkinter import ttk
import os
import csv
import sys
import inspect
import datetime
import pathlib
from collections import defaultdict
import re

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_marker_file_handling import maker_file_check_for_markers_file
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
current_version = "20250922.145500.10"
current_version_hash = (20250922 * 145500 * 10)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[5]
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

class ShowtimeTab(ttk.Frame):
    """
    A Tkinter Frame that dynamically creates buttons for each marker in the MARKERS.csv file.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🟢 Initializing ShowtimeTab. Ready for showtime!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.buttons = []
        self.marker_data = []
        self.column_headers = []
        self.grouped_markers = {}
        self.selected_zone = None
        self.selected_group = None
        self.selected_device_button = None

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()
        
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
            
        self._load_marker_data()
        self._process_and_sort_markers()
        self._create_zone_buttons()
        self._create_group_buttons()
        self._create_device_buttons()
        console_log("✅ Filters reset. All markers displayed.")

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        
        if event is None or event.widget.tab(event.widget.select(), "text") == "Showtime":
            debug_log(
                message="🛠️🟢 'Showtime' tab activated. Reloading marker data and buttons.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
            self._load_marker_data()
            self._process_and_sort_markers()
            self._create_zone_buttons()
            self._create_group_buttons()
            self._create_device_buttons()
            
    def _load_marker_data(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🟢 Loading raw marker data from file.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        
        raw_headers, raw_data = maker_file_check_for_markers_file()
        
        if not raw_data:
            self.marker_data = []
            self.column_headers = []
            console_log("🟡 No marker data found in MARKERS.csv. No buttons will be created.")
            return

        self.marker_data = [dict(zip(raw_headers, row)) for row in raw_data if len(row) == len(raw_headers)]
        self.column_headers = raw_headers

        debug_log(
            message=f"✅ Loaded {len(self.marker_data)} rows. Converted to dictionaries for sorting and display.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
            
    def _process_and_sort_markers(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🔵 Processing and sorting marker data by Zone, Group, and Device.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

        self.grouped_markers = defaultdict(lambda: defaultdict(list))
        
        for row in self.marker_data:
            zone = row.get('ZONE', 'N/A')
            group = row.get('GROUP', 'N/A')
            self.grouped_markers[zone][group].append(row)
        
        for zone, groups in self.grouped_markers.items():
            for group, devices in groups.items():
                devices.sort(key=lambda x: x.get('NAME', ''))
        
        debug_log(
            message="✅ Markers grouped and sorted successfully.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

    def _create_zone_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
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
            button = ttk.Button(
                self.zone_frame,
                text=zone_name,
                command=lambda z=zone_name: self._on_zone_toggle(z),
                style='Custom.TButton' if not is_selected else 'Custom.Selected.TButton'
            )
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        for i in range(4):
            self.zone_frame.grid_columnconfigure(i, weight=1)
        
        debug_log(
            message=f"✅ Zone buttons created for {len(sorted_zones)} zones.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        
    def _create_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🟢 Creating Group filter buttons.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        
        for widget in self.group_frame.winfo_children():
            widget.destroy()
        
        if self.selected_zone:
            self.group_frame.configure(text=f"GROUPS")
            self.group_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
            
            sorted_groups = sorted(self.grouped_markers[self.selected_zone].keys())
            for i, group_name in enumerate(sorted_groups):
                is_selected = self.selected_group == group_name
                button = ttk.Button(
                    self.group_frame,
                    text=group_name,
                    command=lambda g=group_name: self._on_group_toggle(g),
                    style='Custom.TButton' if not is_selected else 'Custom.Selected.TButton'
                )
                row = i // 4
                col = i % 4
                button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        else:
            self.group_frame.grid_remove()
            
        debug_log(
            message=f"✅ Group buttons updated for selected zone.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

    def _create_device_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🟢 Creating Device buttons.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        
        self.selected_device_button = None

        for widget in self.device_frame.winfo_children():
            widget.destroy()
        
        filtered_devices = []
        if self.selected_zone and self.selected_group:
            filtered_devices = self.grouped_markers[self.selected_zone][self.selected_group]
            debug_log(
                message=f"🔍 Showing devices for Zone: {self.selected_zone} and Group: {self.selected_group}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        elif self.selected_zone:
            for group_name in self.grouped_markers[self.selected_zone]:
                filtered_devices.extend(self.grouped_markers[self.selected_zone][group_name])
            debug_log(
                message=f"🔍 Showing all devices for selected Zone: {self.selected_zone}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        else:
            filtered_devices = self.marker_data
            debug_log(
                message="🔍 Showing all devices from MARKERS.csv.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )

        for i, row_data in enumerate(filtered_devices):
            button_text = (f"{row_data.get('NAME', 'N/A')}\n"
                           f"{row_data.get('DEVICE', 'N/A')}\n"
                           f"{row_data.get('FREQ (MHZ)', 'N/A')} MHz\n"
                           f"PEAK: [*************]")
            
            button = ttk.Button(
                self.device_frame,
                text=button_text,
                style='Custom.TButton'
            )
            button.configure(command=lambda data=row_data, b=button: self._on_marker_button_click(data, b))
            
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        debug_log(
            message=f"✅ Created {len(filtered_devices)} device buttons.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
            
    def _on_zone_toggle(self, zone_name):
        current_function = inspect.currentframe().f_code.co_name
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
            debug_log(
                message=f"🛠️🟢 Selected new Zone: {self.selected_zone}. Clearing Group selection.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        
        self._create_zone_buttons()
        self._create_group_buttons()
        self._create_device_buttons()
        
    def _on_group_toggle(self, group_name):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🔵 Group toggle clicked for: {group_name}. Current selection: {self.selected_group}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        if self.selected_group == group_name:
            self.selected_group = None
            debug_log(
                message="🛠️🟡 Deselected Group. Showing all devices for the current Zone.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        else:
            self.selected_group = group_name
            debug_log(
                message=f"🛠️🟢 Selected new Group: {self.selected_group}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
            
        self._create_group_buttons()
        self._create_device_buttons()
        
    def _clear_group_buttons(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🔵 Clearing group buttons.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        for widget in self.group_frame.winfo_children():
            widget.destroy()

    def _on_marker_button_click(self, marker_data, button):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🔵 Device button clicked. Toggling selection.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        
        if self.selected_device_button == button:
            self.selected_device_button.config(style='Custom.TButton')
            self.selected_device_button = None
            console_log(f"🟡 Deselected device: {marker_data.get('NAME', 'N/A')}.")
        else:
            if self.selected_device_button:
                self.selected_device_button.config(style='Custom.TButton')
            
            self.selected_device_button = button
            self.selected_device_button.config(style='Custom.Selected.TButton')
            console_log(f"✅ Selected device: {marker_data.get('NAME', 'N/A')} at {marker_data.get('FREQ (MHZ)', 'N/A')} MHz.")