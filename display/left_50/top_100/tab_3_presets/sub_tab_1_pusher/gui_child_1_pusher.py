# display/left_50/top_100/tab_3_presets/sub_tab_1_pusher/gui_child_1_pusher.py
#
# A GUI frame with a button to manually load presets from a CSV file.
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
# Version 20251014.220800.4
#
# MODIFIED: Simplified load logic to read the new, unified, normalized CSV structure 
#           (Presets as Rows, Attributes as Columns) directly for stability.

import os
import inspect
import tkinter as tk
from tkinter import ttk, filedialog
import csv
import pathlib
import json 

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.worker_mqtt_controller_util import MqttControllerUtility
from workers.worker_preset_pusher import PresetPusherWorker
import workers.worker_project_paths 

# --- Global Scope Variables ---
current_version = "20251014.220800.4"
current_version_hash = (20251014 * 220800 * 4)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
BUTTON_GRID_COLUMNS = 4
ALL_ATTRIBUTES = [
    "Active", "FileName", "NickName", "Start", "Stop", 
    "Center", "Span", "RBW", "VBW", "RefLevel", "Attenuation", 
    "MaxHold", "HighSens", "PreAmp", "Trace1Mode", "Trace2Mode", 
    "Trace3Mode", "Trace4Mode"
]

class PresetPusherGui(ttk.Frame):
    """
    A GUI frame that dynamically creates a grid of buttons for presets.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        """
        Initializes the Presets pusher GUI, loading data from CSV and creating buttons.
        """
        super().__init__(parent, *args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.mqtt_util = mqtt_util
        self.preset_worker = PresetPusherWorker(mqtt_controller=self.mqtt_util)
        self.presets_data = []
        self.selected_preset_index = None
        self.buttons = []
        
        # UI Elements
        self.presets_frame = None
        self.info_frame = None
        self.info_labels = {}
        self.button_frame = None

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

        # Load data immediately
        self._load_presets_from_repo()
        
        console_log("✅ Celebration of success! The PresetPusherGui did initialize and load presets.")

    def _load_presets_from_repo(self):
        """
        Loads presets directly from the normalized CSV structure (Presets as Rows).
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 1. Resolve Path (Using getattr for safe access)
        filepath = getattr(workers.worker_project_paths, 'PRESET_REPO_PATH', None)
        
        if not filepath or not pathlib.Path(filepath).is_file():
            console_log("❌ Preset repository file not found. Starting with no presets.")
            return

        debug_log(
            message=f"🛠️🟢 Automatically loading normalized preset data from repository: {filepath}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        self.presets_data = []
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as csv_file:
                # Assuming the file is now in the normalized format (Preset rows, Attribute columns)
                csv_reader = csv.DictReader(csv_file)

                for row_dict in csv_reader:
                    
                    # Ensure row has the minimal required keys (Parameter/Preset_Key and Active)
                    if 'Parameter' in row_dict:
                        row_dict['Preset_Key'] = row_dict.pop('Parameter')
                    
                    # We treat the row dictionary as the monolithic preset dictionary
                    if str(row_dict.get('Active', 'false')).lower() == 'true':
                        self.presets_data.append(row_dict)
                    
            
            # Sort data by NickName numerically if possible, otherwise alphabetically
            self.presets_data.sort(key=lambda x: (x.get('NickName', '').isdigit(), int(x.get('NickName', '')) if x.get('NickName', '').isdigit() else x.get('NickName', '')))

            console_log(f"✅ Loaded {len(self.presets_data)} active presets from repository.")
            
            self._rebuild_gui()
            
        except Exception as e:
            console_log(f"❌ Error loading presets from repository: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! Failed to load presets! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _create_widgets(self):
        """
        Creates the main widgets, now removing the manual Load Button.
        """
        # Frame for the Preset Buttons
        self.presets_frame = ttk.LabelFrame(self, text="Available Presets")
        self.presets_frame.pack(fill=tk.X, padx=10, pady=5, side=tk.TOP)

        self.button_frame = ttk.Frame(self.presets_frame)
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for the Preset Details
        self.info_frame = ttk.LabelFrame(self, text="Selected Preset Details")
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.BOTTOM)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        
        self._setup_info_labels()


    def _rebuild_gui(self):
        """
        Clears existing buttons and recreates them based on the newly loaded data.
        """
        # Clear existing buttons
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

        # Create new buttons
        for i, preset in enumerate(self.presets_data):
            # Pass the monolithic dictionary for processing
            button_text = self._format_button_text(preset)
            button = ttk.Button(
                self.button_frame,
                text=button_text,
                style='Custom.TButton',
                command=lambda p=preset: self.select_preset(p)
            )
            row = i // BUTTON_GRID_COLUMNS
            col = i % BUTTON_GRID_COLUMNS
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.buttons.append(button)

        for i in range(BUTTON_GRID_COLUMNS):
            self.button_frame.grid_columnconfigure(i, weight=1)

        # Clear info labels
        for value_var in self.info_labels.values():
            value_var.set("")

    def _setup_info_labels(self):
        """
        Initializes the StringVar objects for the info labels.
        """
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        row_count = 0
        for key in self._get_info_keys():
            label_text = f"{key}:"
            value_var = tk.StringVar(value="")
            
            label_widget = ttk.Label(self.info_frame, text=label_text)
            label_widget.grid(row=row_count, column=0, sticky="w", padx=5, pady=2)
            
            value_label = ttk.Label(self.info_frame, textvariable=value_var)
            value_label.grid(row=row_count, column=1, sticky="w", padx=5, pady=2)
            
            self.info_labels[key] = value_var
            row_count += 1
            
    def _get_info_keys(self):
        """Returns the list of keys to display in the info box, sorted by importance."""
        return ALL_ATTRIBUTES 

    def _format_button_text(self, preset):
        """
        Formats the text for each preset button.
        """
        nickname = preset.get("NickName", "N/A")
        start = preset.get("Start", "N/A")
        stop = preset.get("Stop", "N/A")
        center = preset.get("Center", "N/A")
        span = preset.get("Span", "N/A")

        return (
            f"{nickname}\n"
            f"ST: {start} / STP: {stop}\n"
            f"C: {center} / SP: {span}"
        )

    def select_preset(self, selected_preset):
        """
        This function is called when a preset button is clicked. It updates the
        displayed information and triggers the `selected_preset` function.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Reset previous selection style
        for button in self.buttons:
            button.config(style='Custom.TButton')
            
        # Find and apply new selection style
        for i, preset in enumerate(self.presets_data):
            if preset == selected_preset:
                self.buttons[i].config(style='Custom.Selected.TButton')
                break

        self._update_info_labels(selected_preset)
        
        # Build the ordered values list as required by the worker's API
        # The worker expects the preset key + all attributes.
        ordered_values = [selected_preset.get('Preset_Key', '')] 
        ordered_values.extend([selected_preset.get(key, '') for key in self._get_info_keys()]) 
        
        self.preset_worker.Tune_to_preset(ordered_values)
        
    def _update_info_labels(self, preset):
        """
        Updates the labels in the info box with the selected preset's details.
        """
        for key, value_var in self.info_labels.items():
            value_var.set(preset.get(key, "N/A"))

    def selected_preset(self, preset_values):
        """
        This is the core function called when a preset is selected.
        It prints the full list of values to the console.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 The 'selected_preset' function has been called!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        console_log("--- Selected Preset Values ---")
        console_log(str(preset_values))
        console_log("------------------------------")
        
    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        
        style.configure('Custom.TButton',
                        background=colors["button_style_actuator"]["background"],
                        foreground=colors["button_style_actuator"]["foreground"],
                        padding=colors["padding"] * 5,
                        relief=colors["relief"],
                        borderwidth=colors["border_width"] * 2)

        style.map('Custom.TButton',
                  background=[('pressed', colors["button_style_actuator"]["Button_Pressed_Bg"]),
                              ('active', colors["button_style_actuator"]["Button_Hover_Bg"])],
                  foreground=[('pressed', colors["button_style_actuator"]["foreground"])])

        style.configure('Custom.Selected.TButton',
                        background=colors["button_style_toggle"]["Button_Selected_Bg"],
                        foreground=colors["button_style_toggle"]["Button_Selected_Fg"],
                        padding=colors["padding"] * 5,
                        relief=tk.SUNKEN,
                        borderwidth=colors["border_width"] * 2)
        
        style.map('Custom.Selected.TButton',
                  background=[('pressed', colors["button_style_toggle"]["Button_Pressed_Bg"]),
                              ('active', colors["button_style_toggle"]["Button_Hover_Bg"])],
                  foreground=[('pressed', colors["button_style_toggle"]["Button_Selected_Fg"])])