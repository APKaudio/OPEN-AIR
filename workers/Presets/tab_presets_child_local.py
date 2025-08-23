# tabs/Presets/tab_presets_child_local.py
#
# This file defines the LocalPresetsTab, a Tkinter Frame that provides
# functionality for displaying and loading user-defined presets stored
# locally in a CSV file. It does NOT include direct editing capabilities;
# editing is handled in the separate PresetEditorTab.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.173331.1
# UPDATED: Refactored logic to break circular dependencies by using a shared load preset logic
#          file and importing push_preset_logic lazily.

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import functions from preset utility modules
from Presets.utils_preset_csv_process import load_user_presets_from_csv
from src.program_style import COLOR_PALETTE
from settings_and_config.config_manager_save import save_program_config 
from ref.ref_file_paths import CONFIG_FILE_PATH, PRESETS_FILE_PATH
from Presets.utils_preset_query_and_load import load_selected_preset_logic

# --- Versioning ---
w = 20250821
x_str = '173331'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


class LocalPresetsTab(ttk.Frame):
    """
    A Tkinter Frame for displaying and loading user-defined local presets.
    It lists presets from PRESETS.CSV as a grid of buttons and allows the user
    to load them, which updates the main application's instrument settings
    and pushes them to the connected instrument.
    """

    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing LocalPresetsTab. Version: {current_version}. Setting up local preset display! 💾", file=current_file,
                    version=current_version,
                    function=current_function)

        self.user_presets_data = []
        self.last_clicked_button = None
        
        self.selected_preset_nickname_var = tk.StringVar(self, value="N/A")
        self.selected_preset_start_var = tk.StringVar(self, value="N/A")
        self.selected_preset_stop_var = tk.StringVar(self, value="N/A")
        self.selected_preset_center_var = tk.StringVar(self, value="N/A")
        self.selected_preset_span_var = tk.StringVar(self, value="N/A")
        self.selected_preset_rbw_var = tk.StringVar(self, value="N/A")
        self.selected_preset_vbw_var = tk.StringVar(self, value="N/A")
        self.selected_preset_reflevel_var = tk.StringVar(self, value="N/A")
        self.selected_preset_attenuation_var = tk.StringVar(self, value="N/A")
        self.selected_preset_maxhold_var = tk.StringVar(self, value="N/A")
        self.selected_preset_highsens_var = tk.StringVar(self, value="N/A")
        self.selected_preset_preamp_var = tk.StringVar(self, value="N/A")
        self.selected_preset_trace1_var = tk.StringVar(self, value="N/A")
        self.selected_preset_trace2_var = tk.StringVar(self, value="N/A")
        self.selected_preset_trace3_var = tk.StringVar(self, value="N/A")
        self.selected_preset_trace4_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker1_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker2_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker3_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker4_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker5_var = tk.StringVar(self, value="N/A")
        self.selected_preset_marker6_var = tk.StringVar(self, value="N/A")
        
        self.display_variables_map = {
            'NickName': self.selected_preset_nickname_var,
            'Start': self.selected_preset_start_var,
            'Stop': self.selected_preset_stop_var,
            'Center': self.selected_preset_center_var,
            'Span': self.selected_preset_span_var,
            'RBW': self.selected_preset_rbw_var,
            'VBW': self.selected_preset_vbw_var,
            'RefLevel': self.selected_preset_reflevel_var,
            'Attenuation': self.selected_preset_attenuation_var,
            'MaxHold': self.selected_preset_maxhold_var,
            'HighSens': self.selected_preset_highsens_var,
            'PreAmp': self.selected_preset_preamp_var,
            'Trace1Mode': self.selected_preset_trace1_var,
            'Trace2Mode': self.selected_preset_trace2_var,
            'Trace3Mode': self.selected_preset_trace3_var,
            'Trace4Mode': self.selected_preset_trace4_var,
            'Marker1Max': self.selected_preset_marker1_var,
            'Marker2Max': self.selected_preset_marker2_var,
            'Marker3Max': self.selected_preset_marker3_var,
            'Marker4Max': self.selected_preset_marker4_var,
            'Marker5Max': self.selected_preset_marker5_var,
            'Marker6Max': self.selected_preset_marker6_var,
        }

        self._create_widgets()
        self.populate_local_presets_list()

        debug_log(f"LocalPresetsTab initialized. Version: {current_version}. Local presets ready! ✅", file=current_file,
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating LocalPresetsTab widgets...", file=current_file,
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.canvas = tk.Canvas(self, bg=COLOR_PALETTE.get('background'), highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.max_cols = 5
        for i in range(self.max_cols):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)

        selected_preset_box = ttk.LabelFrame(self, text="Selected Preset Details", style='Dark.TLabelframe')
        selected_preset_box.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        details_grid_frame = ttk.Frame(selected_preset_box)
        details_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        details_grid_frame.grid_columnconfigure(1, weight=1)

        details_grid_frame.grid_columnconfigure(0, weight=1)
        details_grid_frame.grid_columnconfigure(1, weight=1)
        details_grid_frame.grid_columnconfigure(2, weight=1)
        details_grid_frame.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(details_grid_frame, text="Nickname:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_nickname_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew", columnspan=3)

        row_idx += 1
        ttk.Separator(details_grid_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=5)
        row_idx += 1
        ttk.Label(details_grid_frame, text="Frequency Settings", style='Dark.TLabel.Value').grid(row=row_idx, column=0, columnspan=4, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="Start (MHz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_start_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="Stop (MHz):", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_stop_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        
        row_idx += 1
        ttk.Label(details_grid_frame, text="Center (MHz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_center_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="Span (MHz):", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_span_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        
        row_idx += 1
        ttk.Separator(details_grid_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=5)
        row_idx += 1
        ttk.Label(details_grid_frame, text="Bandwidth Settings", style='Dark.TLabel.Value').grid(row=row_idx, column=0, columnspan=4, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="RBW (Hz):", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_rbw_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="VBW (Hz):", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_vbw_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        row_idx += 1
        ttk.Separator(details_grid_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=5)
        row_idx += 1
        ttk.Label(details_grid_frame, text="Amplitude Settings", style='Dark.TLabel.Value').grid(row=row_idx, column=0, columnspan=4, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="Ref Level:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_reflevel_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="Attenuation:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_attenuation_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="Max Hold:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_maxhold_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="High Sens.:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_highsens_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        
        row_idx += 1
        ttk.Label(details_grid_frame, text="PreAmp:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_preamp_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        
        row_idx += 1
        ttk.Separator(details_grid_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=5)
        row_idx += 1
        ttk.Label(details_grid_frame, text="Trace Modes", style='Dark.TLabel.Value').grid(row=row_idx, column=0, columnspan=4, sticky="ew")
        
        row_idx += 1
        ttk.Label(details_grid_frame, text="T1 Mode:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_trace1_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="T2 Mode:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_trace2_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")
        
        row_idx += 1
        ttk.Label(details_grid_frame, text="T3 Mode:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_trace3_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="T4 Mode:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_trace4_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        row_idx += 1
        ttk.Separator(details_grid_frame, orient=tk.HORIZONTAL).grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=5)
        row_idx += 1
        ttk.Label(details_grid_frame, text="Marker Settings", style='Dark.TLabel.Value').grid(row=row_idx, column=0, columnspan=4, sticky="ew")
        
        row_idx += 1
        ttk.Label(details_grid_frame, text="M1 Max:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker1_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="M2 Max:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker2_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="M3 Max:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker3_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="M4 Max:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker4_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        row_idx += 1
        ttk.Label(details_grid_frame, text="M5 Max:", style='TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker5_var, style='Dark.TLabel.Value').grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(details_grid_frame, text="M6 Max:", style='TLabel').grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(details_grid_frame, textvariable=self.selected_preset_marker6_var, style='Dark.TLabel.Value').grid(row=row_idx, column=3, padx=5, pady=2, sticky="ew")

        debug_log("LocalPresetsTab widgets created. Scrollable button container and details box ready! 🖼️", file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        debug_log(f"Mouse wheel scrolled by {event.delta} units. Adjusting canvas view.", file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def populate_local_presets_list(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets buttons...", file=current_file,
                    version=current_version,
                    function=current_function)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.last_clicked_button = None
        for var in self.display_variables_map.values():
            var.set("N/A")

        self.user_presets_data = load_user_presets_from_csv(PRESETS_FILE_PATH, self.console_print_func)

        if not self.user_presets_data:
            ttk.Label(self.scrollable_frame, text="No local presets found.", style='TLabel').grid(row=0, column=0, columnspan=self.max_cols, padx=10, pady=10)
            self.console_print_func("ℹ️ No local presets found in PRESETS.CSV.")
            debug_log("No local presets found. 🤷‍♂️", file=current_file,
                        version=current_version,
                        function=current_function)
            return

        row_idx = 0
        col_idx = 0
        
        for preset in self.user_presets_data:
            nickname = preset.get('NickName', preset.get('Filename', 'Unnamed Preset'))
            
            start_freq_mhz_display = "N/A"
            stop_freq_mhz_display = "N/A"
            try:
                if preset.get('Start', '').strip():
                    start_freq_mhz_display = f"{float(preset.get('Start')):.3f}"
                if preset.get('Stop', '').strip():
                    stop_freq_mhz_display = f"{float(preset.get('Stop')):.3f}"
            except ValueError:
                debug_log(f"Warning: Could not convert Start/Stop for button text for preset '{nickname}'. What a mess!", file=current_file,
                            version=current_version,
                            function=current_function)

            button_text = f"{nickname}\nStart: {start_freq_mhz_display} MHz\nStop: {stop_freq_mhz_display} MHz"

            preset_button = ttk.Button(self.scrollable_frame,
                                       text=button_text,
                                       command=lambda p=preset, b=None: self._on_preset_button_click(p, b),
                                       style='LocalPreset.TButton')
            
            preset_button.configure(command=lambda p=preset, b=preset_button: self._on_preset_button_click(p, b))

            preset_button.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

            col_idx += 1
            if col_idx >= self.max_cols:
                col_idx = 0
                row_idx += 1
        
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.console_print_func(f"✅ Displayed {len(self.user_presets_data)} local presets as buttons.")
        debug_log(f"Local presets buttons populated with {len(self.user_presets_data)} entries. Looking good! 👍", file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_preset_button_click(self, preset_data, clicked_button):
        current_function = inspect.currentframe().f_code.co_name
        display_name = preset_data.get('NickName', preset_data.get('Filename', 'Unnamed Preset'))
        self.console_print_func(f"Attempting to load and apply preset: {display_name}...")
        debug_log(f"Preset button clicked for: {display_name}. Applying settings to GUI and instrument. 🖱️", file=current_file,
                    version=current_version,
                    function=current_function)

        if self.last_clicked_button and self.last_clicked_button != clicked_button:
            self.last_clicked_button.config(style='LocalPreset.TButton')
            debug_log(f"Reset style of previous button: {self.last_clicked_button.cget('text').splitlines()[0]}", file=current_file,
                        version=current_version,
                        function=current_function)

        clicked_button.config(style='SelectedPreset.Orange.TButton')
        self.last_clicked_button = clicked_button
        debug_log(f"Set style of current button to orange: {display_name}", file=current_file,
                    version=current_version,
                    function=current_function)

        self.app_instance.defer_config_save = True
        debug_log("Config saving deferred. GUI updates won't trigger saves yet. 🛑", file=current_file,
                    version=current_version,
                    function=current_function)

        success_push_to_instrument = False
        if not self.app_instance.inst:
            self.console_print_func("⚠️ Instrument not connected. Settings will be applied to GUI only.")
            debug_log("Instrument not connected. Skipping SCPI commands. GUI only update. 🖥️", file=current_file,
                        version=current_version,
                        function=current_function)
            self._update_gui_from_preset_data(preset_data)
        else:
            self._update_gui_from_preset_data(preset_data)
            debug_log(f"Instrument is connected ({self.app_instance.inst}). Attempting to push preset to device. ⚡", file=current_file,
                        version=current_version,
                        function=current_function)
            
            # LAZY IMPORT: Imports moved here to break circular dependency
            from Presets.utils_push_preset import push_preset_logic
            
            success_push_to_instrument = push_preset_logic(self.app_instance, self.console_print_func, preset_data)
        
        if success_push_to_instrument:
            self.console_print_func(f"✅ Preset '{display_name}' applied to instrument and GUI. Fantastic!")
            debug_log(f"Preset '{display_name}' applied to instrument and GUI successfully. 🎉", file=current_file,
                        version=current_version,
                        function=current_function)
        elif self.app_instance.inst:
             self.console_print_func(f"❌ Failed to apply preset '{display_name}' to instrument. GUI updated only.")
             debug_log(f"Failed to apply preset '{display_name}' to instrument. GUI updated only. 🤦‍♂️", file=current_file,
                         version=current_version,
                         function=current_function)

        try:
            if hasattr(self.app_instance, 'instrument_parent_tab') and \
               hasattr(self.app_instance.instrument_parent_tab, 'settings_tab') and \
               hasattr(self.app_instance.instrument_parent_tab.settings_tab, 'refresh_all_child_tabs'):
                self.app_instance.instrument_parent_tab.settings_tab.refresh_all_child_tabs()
        finally:
            self.app_instance.defer_config_save = False
            debug_log("Config saving re-enabled. Triggering final save. ✅", file=current_file,
                        version=current_version,
                        function=current_function)
            
            try:
                save_program_config (self.app_instance.program_config, self.console_print_func, self.app_instance)
            except Exception as e:
                debug_log(f"CRITICAL ERROR: Could not save config after preset load: {e}. Config not saved!", file=current_file,
                            version=current_version,
                            function=current_function)
                self.console_print_func("❌ CRITICAL ERROR: Application config could not be saved! See debug log.")

    def _update_gui_from_preset_data(self, preset_data):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating GUI from preset data: {preset_data.get('NickName', 'Unnamed')}. 🔄", file=current_file,
                    version=current_version,
                    function=current_function)

        self.selected_preset_nickname_var.set(preset_data.get('NickName', 'N/A'))
        
        for var in self.display_variables_map.values():
            var.set("N/A")

        def set_display_var(tk_var, key, format_str="{}", conversion_func=str, default_val="N/A"):
            value_str = preset_data.get(key, '').strip()
            if not value_str:
                tk_var.set(default_val)
                debug_log(f"Preset '{key}' is empty for display. Setting display to '{default_val}'.", file=current_file,
                            version=current_version,
                            function=current_function)
                return

            try:
                converted_value = conversion_func(value_str)
                tk_var.set(format_str.format(converted_value))
                debug_log(f"Preset '{key}' value '{value_str}' converted to '{converted_value}' and displayed as '{tk_var.get()}'.", file=current_file,
                            version=current_version,
                            function=current_function)
            except ValueError as e:
                tk_var.set("Invalid Value")
                debug_log(f"Error converting preset '{key}' value '{value_str}' to {conversion_func.__name__}: {e}. Displaying 'Invalid Value'. 💥", file=current_file,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                tk_var.set("Error")
                debug_log(f"Unexpected error processing preset '{key}' value '{value_str}': {e}. Displaying 'Error'. 🤯", file=current_file,
                            version=current_version,
                            function=current_function)

        set_display_var(self.selected_preset_start_var, 'Start', "{:.3f}", float)
        set_display_var(self.selected_preset_stop_var, 'Stop', "{:.3f}", float)
        set_display_var(self.selected_preset_center_var, 'Center', "{:.3f}", float)
        set_display_var(self.selected_preset_span_var, 'Span', "{:.3f}", float)
        set_display_var(self.selected_preset_rbw_var, 'RBW', "{:.0f}", float)
        set_display_var(self.selected_preset_vbw_var, 'VBW', "{:.0f}", float)
        set_display_var(self.selected_preset_reflevel_var, 'RefLevel', "{:.1f}", float)
        set_display_var(self.selected_preset_attenuation_var, 'Attenuation', "{:.0f}", float)
        set_display_var(self.selected_preset_maxhold_var, 'MaxHold')
        set_display_var(self.selected_preset_highsens_var, 'HighSens')
        set_display_var(self.selected_preset_preamp_var, 'PreAmp')
        set_display_var(self.selected_preset_trace1_var, 'Trace1Mode')
        set_display_var(self.selected_preset_trace2_var, 'Trace2Mode')
        set_display_var(self.selected_preset_trace3_var, 'Trace3Mode')
        set_display_var(self.selected_preset_trace4_var, 'Trace4Mode')
        set_display_var(self.selected_preset_marker1_var, 'Marker1Max')
        set_display_var(self.selected_preset_marker2_var, 'Marker2Max')
        set_display_var(self.selected_preset_marker3_var, 'Marker3Max')
        set_display_var(self.selected_preset_marker4_var, 'Marker4Max')
        set_display_var(self.selected_preset_marker5_var, 'Marker5Max')
        set_display_var(self.selected_preset_marker6_var, 'Marker6Max')

        def get_and_set_app_var(preset_key, app_attr_name, conversion_func=str, scale_factor=1.0):
            value_str = preset_data.get(preset_key, '').strip()
            app_tk_var = getattr(self.app_instance, app_attr_name, None)

            if app_tk_var is None:
                debug_log(f"WARNING: app_instance does not have attribute '{app_attr_name}'. Cannot update. ⚠️", file=current_file,
                            version=current_version,
                            function=current_function)
                return
            
            if not value_str:
                debug_log(f"Preset '{preset_key}' is empty. Skipping update for app_instance.{app_attr_name}. 🤷‍♀️", file=current_file,
                            version=current_version,
                            function=current_function)
                return

            try:
                converted_value = conversion_func(value_str) * scale_factor
                app_tk_var.set(converted_value)
                debug_log(f"App var '{app_attr_name}' (from '{preset_key}') updated to '{converted_value}'.", file=current_file,
                            version=current_version,
                            function=current_function)
            except ValueError as e:
                debug_log(f"Error converting preset '{preset_key}' value '{value_str}' to {conversion_func.__name__}: {e}. Skipping update. 💥", file=current_file,
                            version=current_version,
                            function=current_function)
            except Exception as e:
                debug_log(f"Unexpected error processing preset '{preset_key}' value '{value_str}': {e}. Skipping update. 🤯", file=current_file,
                            version=current_version,
                            function=current_function)

        get_and_set_app_var('Center', 'center_freq_mhz_var', float, self.app_instance.MHZ_TO_HZ)
        get_and_set_app_var('Span', 'span_freq_mhz_var', float, self.app_instance.MHZ_TO_HZ)
        get_and_set_app_var('RBW', 'rbw_hz_var', float)
        get_and_set_app_var('VBW', 'vbw_hz_var', float)
        get_and_set_app_var('RefLevel', 'reference_level_dbm_var', float)
        get_and_set_app_var('Attenuation', 'attenuation_db_var', int)
        get_and_set_app_var('FreqShift', 'freq_shift_hz_var', float)

        def get_and_set_bool_app_var(preset_key, app_attr_name):
            value_str = preset_data.get(preset_key, '').strip().upper()
            app_tk_var = getattr(self.app_instance, app_attr_name, None)

            if app_tk_var is None:
                debug_log(f"WARNING: app_instance does not have attribute '{app_attr_name}'. Cannot update. ⚠️", file=current_file,
                            version=current_version,
                            function=current_function)
                return

            if value_str in ['ON', 'TRUE', 'WRITE']:
                app_tk_var.set(True)
            elif value_str in ['OFF', 'FALSE', '']:
                app_tk_var.set(False)
            else:
                debug_log(f"Warning: Unexpected boolean value for '{preset_key}': '{value_str}'. Not updating app_instance.{app_attr_name}. ⚠️", file=current_file,
                            version=current_version,
                            function=current_function)

        get_and_set_bool_app_var('MaxHold', 'maxhold_enabled_var')
        get_and_set_bool_app_var('HighSens', 'high_sensitivity_var')
        get_and_set_bool_app_var('PreAmp', 'preamp_on_var')

        get_and_set_app_var('Trace1Mode', 'trace1_mode_var')
        get_and_set_app_var('Trace2Mode', 'trace2_mode_var')
        get_and_set_app_var('Trace3Mode', 'trace3_mode_var')
        get_and_set_app_var('Trace4Mode', 'trace4_mode_var')

        get_and_set_bool_app_var('Marker1Max', 'marker1_calculate_max_var')
        get_and_set_bool_app_var('Marker2Max', 'marker2_calculate_max_var')
        get_and_set_bool_app_var('Marker3Max', 'marker3_calculate_max_var')
        get_and_set_bool_app_var('Marker4Max', 'marker4_calculate_max_var')
        get_and_set_bool_app_var('Marker5Max', 'marker5_calculate_max_var')
        get_and_set_bool_app_var('Marker6Max', 'marker6_calculate_max_var')


        self.app_instance.last_selected_preset_name_var.set(preset_data.get('NickName', preset_data.get('Filename', '')))
        
        set_display_var(self.app_instance.last_loaded_preset_center_freq_mhz_var, 'Center', "{:.3f}", float)
        set_display_var(self.app_instance.last_loaded_preset_span_mhz_var, 'Span', "{:.3f}", float)
        set_display_var(self.app_instance.last_loaded_preset_rbw_hz_var, 'RBW', "{:.0f}", float)


        self.console_print_func(f"✅ GUI settings updated from local preset '{preset_data.get('NickName', 'Unnamed')}'.")
        debug_log("GUI settings updated from local preset. Done! ✅", file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Local Presets tab selected. Refreshing buttons instantly. ✅", file=current_file,
                    version=current_version,
                    function=current_function)
        self.populate_local_presets_list()
        debug_log(f"Local Presets tab refreshed after selection. 👍", file=current_file,
                    version=current_version,
                    function=current_function)