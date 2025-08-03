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
# Version 20250802.1800.4 (New file for Local Presets, simplified for display and loading only.)
# Version 20250802.2300.1 (Replaced Listbox with a grid of buttons for local presets and integrated push_preset_logic.)
# Version 20250802.2305.0 (Fixed AttributeError: 'Style' object has no attribute 'colors' by importing COLOR_PALETTE.)
# Version 20250802.2310.0 (Fixed incorrect import path for push_preset_logic from src.utils_push_preset.)
# Version 20250802.2315.0 (CRITICAL FIX: Corrected MHz/Hz conversion for Center/Span in preset loading and display.)
# Version 20250803.0005.0 (Added selected preset details box, dynamic button styling, and adjusted button font size.)
# Version 20250803.0015.0 (FIXED: SyntaxError: leading zeros in decimal integer literals by correcting current_version_hash.)
# Version 20250803.0025.0 (Adjusted display units and labels for Center, Span (MHz) and RBW, VBW (Hz).)
# Version 20250803.0035.0 (Removed 'Nickname: ' prefix from preset buttons.)

current_version = "20250803.0035.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 35 * 0 # Example hash, adjust as needed.

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import functions from preset utility modules
from tabs.Presets.utils_preset_process import load_user_presets_from_csv
# Import push_preset_logic directly for button commands
from tabs.Presets.utils_push_preset import push_preset_logic # CORRECTED: Import path from src.utils_push_preset
from src.style import COLOR_PALETTE # NEW: Import COLOR_PALETTE directly

class LocalPresetsTab(ttk.Frame):
    """
    A Tkinter Frame for displaying and loading user-defined local presets.
    It lists presets from PRESETS.CSV as a grid of buttons and allows the user
    to load them, which updates the main application's instrument settings
    and pushes them to the connected instrument.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        """
        Initializes the LocalPresetsTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance.
            console_print_func (function): Function to print messages to the GUI console.
            style_obj (ttk.Style): The ttk.Style object for applying custom styles.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing LocalPresetsTab. Version: {current_version}. Setting up local preset display!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.user_presets_data = [] # To store the loaded local preset dictionaries
        self.last_clicked_button = None # To keep track of the last button clicked for styling

        # Tkinter StringVars for displaying selected preset details
        self.selected_preset_nickname_var = tk.StringVar(self, value="N/A")
        self.selected_preset_center_var = tk.StringVar(self, value="N/A")
        self.selected_preset_span_var = tk.StringVar(self, value="N/A")
        self.selected_preset_rbw_var = tk.StringVar(self, value="N/A")
        self.selected_preset_vbw_var = tk.StringVar(self, value="N/A") # NEW: VBW display variable

        self._create_widgets()
        self.populate_local_presets_list() # Initial population

        debug_log(f"LocalPresetsTab initialized. Version: {current_version}. Local presets ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Local Presets tab.
        This now includes a scrollable frame to hold the preset buttons
        and a display box for selected preset details at the bottom.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating LocalPresetsTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Scrollable frame for buttons
        self.grid_rowconfigure(1, weight=0) # Selected Preset Details box

        # --- Scrollable Frame for Buttons ---
        # Create a Canvas and a Scrollbar
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

        # Configure the scrollable frame to expand
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Ensure columns within the frame expand
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)


        # --- Selected Preset Details Box ---
        selected_preset_box = ttk.LabelFrame(self, text="Selected Preset Details", style='Dark.TLabelframe')
        selected_preset_box.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        selected_preset_box.grid_columnconfigure(1, weight=1) # Allow value labels to expand

        # NickName
        ttk.Label(selected_preset_box, text="Nickname:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_nickname_var, style='Dark.TLabel.Value').grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Center Frequency (MHz)
        ttk.Label(selected_preset_box, text="Center (MHz):", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_center_var, style='Dark.TLabel.Value').grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Span (MHz)
        ttk.Label(selected_preset_box, text="Span (MHz):", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_span_var, style='Dark.TLabel.Value').grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # RBW (Hz)
        ttk.Label(selected_preset_box, text="RBW (Hz):", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_rbw_var, style='Dark.TLabel.Value').grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # NEW: VBW (Hz)
        ttk.Label(selected_preset_box, text="VBW (Hz):", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_vbw_var, style='Dark.TLabel.Value').grid(row=4, column=1, padx=5, pady=2, sticky="ew")


        debug_log("LocalPresetsTab widgets created. Scrollable button container and details box ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def populate_local_presets_list(self):
        """
        Loads user presets from the PRESETS.CSV file and populates the scrollable frame with buttons.
        Each button displays NickName, Center, and Span.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets buttons...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Clear existing buttons
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Reset last clicked button reference when repopulating
        self.last_clicked_button = None

        self.user_presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        if not self.user_presets_data:
            ttk.Label(self.scrollable_frame, text="No local presets found.", style='TLabel').grid(row=0, column=0, columnspan=3, padx=10, pady=10)
            self.console_print_func("ℹ️ No local presets found in PRESETS.CSV.")
            debug_log("No local presets found.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        row_idx = 0
        col_idx = 0
        max_cols = 3 # Three buttons per row as requested

        for preset in self.user_presets_data:
            nickname = preset.get('NickName', preset.get('Filename', 'Unnamed Preset'))
            
            # Display values as read from CSV (which are in MHz for Center/Span)
            center_freq_mhz_display = float(preset.get('Center', 0.0)) if preset.get('Center', '').strip() else "N/A"
            span_mhz_display = float(preset.get('Span', 0.0)) if preset.get('Span', '').strip() else "N/A"

            # Removed "Nickname: " from the button text
            button_text = f"{nickname}\nC: {center_freq_mhz_display:.3f} MHz\nSP: {span_mhz_display:.3f} MHz"

            # Use lambda to capture the current preset_data for each button
            preset_button = ttk.Button(self.scrollable_frame,
                                       text=button_text,
                                       command=lambda p=preset, btn=None: self._on_preset_button_click(p, btn), # Pass button reference
                                       style='LargePreset.TButton')
            
            # Update the lambda to pass the button itself once it's created
            # This is a common pattern for Tkinter buttons in loops
            preset_button.configure(command=lambda p=preset, b=preset_button: self._on_preset_button_click(p, b))

            preset_button.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

            col_idx += 1
            if col_idx >= max_cols:
                col_idx = 0
                row_idx += 1
        
        # Adjust canvas scroll region after adding all buttons
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.console_print_func(f"✅ Displayed {len(self.user_presets_data)} local presets as buttons.")
        debug_log(f"Local presets buttons populated with {len(self.user_presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_preset_button_click(self, preset_data, clicked_button):
        """
        Handles the click event for a preset button.
        Updates GUI variables, pushes the preset settings to the instrument,
        and updates the button's visual style.
        """
        current_function = inspect.currentframe().f_code.co_name
        display_name = preset_data.get('NickName', preset_data.get('Filename', 'Unnamed Preset'))
        self.console_print_func(f"Attempting to load and apply preset: {display_name}...")
        debug_log(f"Preset button clicked for: {display_name}. Applying settings to GUI and instrument.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Reset style of previously clicked button
        if self.last_clicked_button and self.last_clicked_button != clicked_button:
            self.last_clicked_button.config(style='LargePreset.TButton')
            debug_log(f"Reset style of previous button: {self.last_clicked_button.cget('text').splitlines()[0]}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Set style of current button to orange
        clicked_button.config(style='SelectedPreset.Orange.TButton')
        self.last_clicked_button = clicked_button
        debug_log(f"Set style of current button to orange: {display_name}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


        # 1. Update GUI Tkinter variables first (including the new display variables)
        self._update_gui_from_preset_data(preset_data)

        # 2. Push settings to instrument using the updated push_preset_logic
        if self.app_instance.inst:
            success = push_preset_logic(self.app_instance, self.console_print_func, preset_data)
            if success:
                self.console_print_func(f"✅ Preset '{display_name}' applied to instrument and GUI. Fantastic!")
                debug_log(f"Preset '{display_name}' applied to instrument and GUI successfully.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func(f"❌ Failed to apply preset '{display_name}' to instrument. GUI updated only.")
                debug_log(f"Failed to apply preset '{display_name}' to instrument. GUI updated only.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("⚠️ No instrument connected. GUI updated only.")
            debug_log("No instrument connected. GUI updated only.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Ensure the Instrument tab's display updates after loading
        if hasattr(self.app_instance, 'instrument_parent_tab') and \
           hasattr(self.app_instance.instrument_parent_tab, 'instrument_settings_tab') and \
           hasattr(self.app_instance.instrument_parent_tab.instrument_settings_tab, '_query_current_settings'):
            # Call query_current_settings to refresh the display, but it won't query hardware if not connected
            self.app_instance.instrument_parent_tab.instrument_settings_tab._query_current_settings()


    def _update_gui_from_preset_data(self, preset_data):
        """
        Updates the main application's Tkinter variables based on the provided preset data.
        This function ensures that the GUI elements reflect the loaded preset.
        It also updates the new selected preset details display.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating GUI from preset data: {preset_data.get('NickName', 'Unnamed')}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        try:
            # Helper to safely get and convert value, defaulting to current Tkinter var value if empty
            def get_and_set_var(key, tk_var, conversion_func=str):
                value = preset_data.get(key, '').strip()
                if value:
                    try:
                        tk_var.set(conversion_func(value))
                    except ValueError:
                        debug_log(f"Warning: Could not convert preset '{key}' value '{value}' to {conversion_func.__name__}. Skipping.",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                # If value is empty, the Tkinter variable retains its current value.

            # Convert Center and Span from MHz (CSV) to Hz (Tkinter var)
            get_and_set_var('Center', self.app_instance.center_freq_hz_var, lambda x: float(x) * self.app_instance.MHZ_TO_HZ)
            get_and_set_var('Span', self.app_instance.span_hz_var, lambda x: float(x) * self.app_instance.MHZ_TO_HZ)

            # RBW and VBW are already in Hz in the CSV, so direct conversion
            get_and_set_var('RBW', self.app_instance.rbw_hz_var, float)
            get_and_set_var('VBW', self.app_instance.vbw_hz_var, float) # VBW is also in Hz

            get_and_set_var('RefLevel', self.app_instance.reference_level_dbm_var, float)
            get_and_set_var('Attenuation', self.app_instance.attenuation_var, int)
            get_and_set_var('MaxHold', self.app_instance.maxhold_enabled_var, lambda x: x.upper() == 'ON')
            get_and_set_var('HighSens', self.app_instance.high_sensitivity_var, lambda x: x.upper() == 'ON')
            get_and_set_var('PreAmp', self.app_instance.preamp_on_var, lambda x: x.upper() == 'ON')

            # Trace Modes (StringVars)
            get_and_set_var('Trace1Mode', self.app_instance.trace1_mode_var)
            get_and_set_var('Trace2Mode', self.app_instance.trace2_mode_var)
            get_and_set_var('Trace3Mode', self.app_instance.trace3_mode_var)
            get_and_set_var('Trace4Mode', self.app_instance.trace4_mode_var)

            # Marker Max (BooleanVars, assuming 'WRITE' means True)
            get_and_set_var('Marker1Max', self.app_instance.marker1_calculate_max_var, lambda x: x.upper() == 'WRITE')
            get_and_set_var('Marker2Max', self.app_instance.marker2_calculate_max_var, lambda x: x.upper() == 'WRITE')
            get_and_set_var('Marker3Max', self.app_instance.marker3_calculate_max_var, lambda x: x.upper() == 'WRITE')
            get_and_set_var('Marker4Max', self.app_instance.marker4_calculate_max_var, lambda x: x.upper() == 'WRITE')
            get_and_set_var('Marker5Max', self.app_instance.marker5_calculate_max_var, lambda x: x.upper() == 'WRITE')
            get_and_set_var('Marker6Max', self.app_instance.marker6_calculate_max_var, lambda x: x.upper() == 'WRITE')


            # Update the app_instance's last selected preset name and loaded values (these are already for display in MHz)
            self.app_instance.last_selected_preset_name_var.set(preset_data.get('NickName', preset_data.get('Filename', '')))
            # No division needed here, as preset_data.get('Center') is already in MHz
            self.app_instance.last_loaded_preset_center_freq_mhz_var.set(f"{float(preset_data.get('Center', 0.0)):.3f}")
            self.app_instance.last_loaded_preset_span_mhz_var.set(f"{float(preset_data.get('Span', 0.0)):.3f}")
            self.app_instance.last_loaded_preset_rbw_hz_var.set(f"{float(preset_data.get('RBW', 0.0)):.0f}")


            # Update the new display variables for selected preset details box
            self.selected_preset_nickname_var.set(preset_data.get('NickName', 'N/A'))
            self.selected_preset_center_var.set(f"{float(preset_data.get('Center', 0.0)):.3f}")
            self.selected_preset_span_var.set(f"{float(preset_data.get('Span', 0.0)):.3f}")
            self.selected_preset_rbw_var.set(f"{float(preset_data.get('RBW', 0.0)):.0f}")
            self.selected_preset_vbw_var.set(f"{float(preset_data.get('VBW', 0.0)):.0f}") # NEW: Set VBW display


            self.console_print_func(f"✅ GUI settings updated from local preset '{preset_data.get('NickName', 'Unnamed')}'.")
            debug_log("GUI settings updated from local preset.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        except Exception as e:
            self.console_print_func(f"❌ An unexpected error occurred updating GUI from preset: {e}.")
            debug_log(f"Unexpected error updating GUI from preset: {e}. What a mess!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the local presets list.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Local Presets Tab selected. Refreshing list... Let's get this updated!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self.populate_local_presets_list()
