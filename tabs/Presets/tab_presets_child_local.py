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
# Version 20250803.1110.0 (FIXED: Reverted import path for push_preset_logic to original correct path.)
# Version 20250803.235902.0 (MODIFIED: Applied 3-column layout and new button styles for local presets. Added explicit online check.)
# Version 20250804.000003.0 (FIXED: Mapped preset CSV keys to correct app_instance attribute names (e.g., 'Center' -> 'center_freq_hz_var').)
# Version 20250804.000006.0 (MODIFIED: Confirmed 3-column layout and ensured consistent behavior.)
# Version 20250804.000007.0 (MODIFIED: Changed preset button layout to 4 columns and enabled mouse scroll wheel for canvas.)
# Version 20250804.000008.0 (MODIFIED: Changed preset button layout to 5 columns as requested.)
# Version 20250804.000009.0 (ADDED: _on_tab_selected and _on_window_focus_in to ensure instant button refresh.)
# Version 20250804.000010.0 (FIXED: AttributeError by moving _on_window_focus_in definition before __init__ bind.)

current_version = "20250804.000010.0" # Incremented version
current_version_hash = 20250803 * 1110 * 0 # Example hash, adjust as needed.

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import functions from preset utility modules
from tabs.Presets.utils_preset_process import load_user_presets_from_csv
# Reverted Import push_preset_logic to original correct path
from tabs.Presets.utils_push_preset import push_preset_logic
from src.program_style import COLOR_PALETTE # NEW: Import COLOR_PALETTE directly
from src.settings_and_config.config_manager import save_config # Explicit import of save_config

class LocalPresetsTab(ttk.Frame):
    """
    A Tkinter Frame for displaying and loading user-defined local presets.
    It lists presets from PRESETS.CSV as a grid of buttons and allows the user
    to load them, which updates the main application's instrument settings
    and pushes them to the connected instrument.
    """
    def _on_window_focus_in(self, event):
        """
        Called when the main application window gains focus.
        This will trigger a refresh of the displayed presets to ensure they are up-to-date.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Main window gained focus. Refreshing Local Presets. 🔄",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # Check if this tab is the active one in its notebook
        if self.master.winfo_exists() and self.master.select() == str(self):
            self.populate_local_presets_list()
            debug_log(f"Local Presets tab active and window focused. Buttons refreshed. ✅",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Window focused, but Local Presets tab not active. Skipping refresh. 😴",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Ensures the presets are reloaded and buttons are refreshed instantly.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Local Presets tab selected. Refreshing buttons instantly. 🚀",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self.populate_local_presets_list()
        debug_log(f"Local Presets tab refreshed after selection. 👍",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

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
        debug_log(f"Initializing LocalPresetsTab. Version: {current_version}. Setting up local preset display! 💾",
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
        self.selected_preset_vbw_var = tk.StringVar(self, value="N/A")

        self._create_widgets()
        self.populate_local_presets_list() # Initial population

        # Bind to main app window focus-in event for refresh when app gains focus
        # This binding needs to be after _on_window_focus_in is defined.
        self.app_instance.bind("<FocusIn>", self._on_window_focus_in)

        debug_log(f"LocalPresetsTab initialized. Version: {current_version}. Local presets ready! ✅",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_function)

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

        # Bind mouse scroll wheel to canvas
        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Configure the scrollable frame to expand with 5 columns
        self.max_cols = 5 # Changed to 5 as requested
        for i in range(self.max_cols):
            self.scrollable_frame.grid_columnconfigure(i, weight=1)


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

        # VBW (Hz)
        ttk.Label(selected_preset_box, text="VBW (Hz):", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(selected_preset_box, textvariable=self.selected_preset_vbw_var, style='Dark.TLabel.Value').grid(row=4, column=1, padx=5, pady=2, sticky="ew")


        debug_log("LocalPresetsTab widgets created. Scrollable button container and details box ready! 🖼️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling for the canvas."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        debug_log(f"Mouse wheel scrolled by {event.delta} units. Adjusting canvas view.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

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
        # Clear selected preset details when repopulating
        self.selected_preset_nickname_var.set("N/A")
        self.selected_preset_center_var.set("N/A")
        self.selected_preset_span_var.set("N/A")
        self.selected_preset_rbw_var.set("N/A")
        self.selected_preset_vbw_var.set("N/A")


        self.user_presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        if not self.user_presets_data:
            ttk.Label(self.scrollable_frame, text="No local presets found.", style='TLabel').grid(row=0, column=0, columnspan=self.max_cols, padx=10, pady=10)
            self.console_print_func("ℹ️ No local presets found in PRESETS.CSV.")
            debug_log("No local presets found. 🤷‍♂️",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        row_idx = 0
        col_idx = 0
        
        for preset in self.user_presets_data:
            nickname = preset.get('NickName', preset.get('Filename', 'Unnamed Preset'))
            
            # Safely get and format Center and Span for button display
            center_freq_mhz_display = "N/A"
            span_mhz_display = "N/A"
            try:
                if preset.get('Center', '').strip():
                    center_freq_mhz_display = f"{float(preset.get('Center')):.3f}"
                if preset.get('Span', '').strip():
                    span_mhz_display = f"{float(preset.get('Span')):.3f}"
            except ValueError:
                debug_log(f"Warning: Could not convert Center/Span for button text for preset '{nickname}'. What a mess!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                # Keep "N/A" or previous value if conversion fails

            # Removed "Nickname: " from the button text
            button_text = f"{nickname}\nC: {center_freq_mhz_display} MHz\nSP: {span_mhz_display} MHz"

            # Use lambda to capture the current preset_data for each button
            preset_button = ttk.Button(self.scrollable_frame,
                                       text=button_text,
                                       command=lambda p=preset, b=None: self._on_preset_button_click(p, b), # Pass button reference
                                       style='LocalPreset.TButton') # Use the new style
            
            # Update the lambda to pass the button itself once it's created
            # This is a common pattern for Tkinter buttons in loops
            preset_button.configure(command=lambda p=preset, b=preset_button: self._on_preset_button_click(p, b))

            preset_button.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

            col_idx += 1
            if col_idx >= self.max_cols: # Use self.max_cols here
                col_idx = 0
                row_idx += 1
        
        # Adjust canvas scroll region after adding all buttons
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.console_print_func(f"✅ Displayed {len(self.user_presets_data)} local presets as buttons.")
        debug_log(f"Local presets buttons populated with {len(self.user_presets_data)} entries. Looking good! 👍",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_preset_button_click(self, preset_data, clicked_button):
        """
        Handles the click event for a preset button.
        Updates GUI variables, pushes the preset settings to the connected instrument,
        and updates the button's visual style.
        """
        current_function = inspect.currentframe().f_code.co_name
        display_name = preset_data.get('NickName', preset_data.get('Filename', 'Unnamed Preset'))
        self.console_print_func(f"Attempting to load and apply preset: {display_name}...")
        debug_log(f"Preset button clicked for: {display_name}. Applying settings to GUI and instrument. 🖱️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Reset style of previously clicked button
        if self.last_clicked_button and self.last_clicked_button != clicked_button:
            self.last_clicked_button.config(style='LocalPreset.TButton') # Use the new default style
            debug_log(f"Reset style of previous button: {self.last_clicked_button.cget('text').splitlines()[0]}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Set style of current button to orange
        clicked_button.config(style='SelectedPreset.Orange.TButton') # Use the new selected style
        self.last_clicked_button = clicked_button
        debug_log(f"Set style of current button to orange: {display_name}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # 1. Defer config saving while updating multiple GUI variables
        self.app_instance.defer_config_save = True
        debug_log("Config saving deferred. GUI updates won't trigger saves yet. 🛑",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # --- Explicit check for instrument connection ---
        success_push_to_instrument = False
        if not self.app_instance.inst:
            self.console_print_func("⚠️ Instrument not connected. Settings will be applied to GUI only.")
            debug_log("Instrument not connected. Skipping SCPI commands. GUI only update. 🖥️",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            # Proceed to update GUI from preset_data even if not connected
            self._update_gui_from_preset_data(preset_data)
        else:
            # If connected, update GUI first, then attempt to push to instrument
            self._update_gui_from_preset_data(preset_data)
            debug_log(f"Instrument is connected ({self.app_instance.inst}). Attempting to push preset to device. ⚡",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            success_push_to_instrument = push_preset_logic(self.app_instance, self.console_print_func, preset_data)
        
        if success_push_to_instrument:
            self.console_print_func(f"✅ Preset '{display_name}' applied to instrument and GUI. Fantastic!")
            debug_log(f"Preset '{display_name}' applied to instrument and GUI successfully. 🎉",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        elif self.app_instance.inst: # If app.inst exists but push_preset_logic returned False
             self.console_print_func(f"❌ Failed to apply preset '{display_name}' to instrument. GUI updated only.")
             debug_log(f"Failed to apply preset '{display_name}' to instrument. GUI updated only. 🤦‍♂️",
                         file=f"{os.path.basename(__file__)} - {current_version}",
                         version=current_version,
                         function=current_function)
        # else (if not connected): message already shown above

        # Wrap config save and following code in a try-finally block
        try:
            # Ensure the Instrument tab's display updates after loading
            if hasattr(self.app_instance, 'instrument_parent_tab') and \
               hasattr(self.app_instance.instrument_parent_tab, 'instrument_settings_tab') and \
               hasattr(self.app_instance.instrument_parent_tab.instrument_settings_tab, '_query_current_settings'):
                # Call query_current_settings to refresh the display, but it won't query hardware if not connected
                self.app_instance.instrument_parent_tab.instrument_settings_tab._query_current_settings()
        finally:
            # Re-enable config saving and trigger a single save
            self.app_instance.defer_config_save = False
            debug_log("Config saving re-enabled. Triggering final save. ✅",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            
            # Assuming config_manager is a module or an instance with a save_config method
            # The save_config function from src.settings_and_config.config_manager
            # expects: (config_parser_object, config_file_path, console_print_func, app_instance_ref)
            try:
                save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
            except Exception as e:
                debug_log(f"CRITICAL ERROR: Could not save config after preset load: {e}. Config not saved!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                self.console_print_func("❌ CRITICAL ERROR: Application config could not be saved! See debug log.")


    def _update_gui_from_preset_data(self, preset_data):
        """
        Updates the main application's Tkinter variables based on the provided preset data.
        This function ensures that the GUI elements reflect the loaded preset.
        It also updates the new selected preset details.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating GUI from preset data: {preset_data.get('NickName', 'Unnamed')}. 🔄",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Update the new display variables for selected preset details box first
        self.selected_preset_nickname_var.set(preset_data.get('NickName', 'N/A'))

        # Helper to safely get and convert value for display variables (these are local to this tab)
        def set_display_var(tk_var, key, format_str="{}", conversion_func=str, default_val="N/A"):
            value_str = preset_data.get(key, '').strip()
            if not value_str:
                tk_var.set(default_val)
                debug_log(f"Preset '{key}' is empty for display. Setting display to '{default_val}'.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return

            try:
                converted_value = conversion_func(value_str)
                tk_var.set(format_str.format(converted_value))
                debug_log(f"Preset '{key}' value '{value_str}' converted to '{converted_value}' and displayed as '{tk_var.get()}'.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except ValueError as e:
                tk_var.set("Invalid Value")
                debug_log(f"Error converting preset '{key}' value '{value_str}' to {conversion_func.__name__}: {e}. Displaying 'Invalid Value'. 💥",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except Exception as e:
                tk_var.set("Error")
                debug_log(f"Unexpected error processing preset '{key}' value '{value_str}': {e}. Displaying 'Error'. 🤯",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        set_display_var(self.selected_preset_center_var, 'Center', "{:.3f}", float)
        set_display_var(self.selected_preset_span_var, 'Span', "{:.3f}", float)
        set_display_var(self.selected_preset_rbw_var, 'RBW', "{:.0f}", float)
        set_display_var(self.selected_preset_vbw_var, 'VBW', "{:.0f}", float)

        # Now, update the main application's instrument control variables
        
        # Helper to safely get and convert value for app_instance variables
        def get_and_set_app_var(preset_key, app_attr_name, conversion_func=str, scale_factor=1.0):
            # preset_key: key from the preset_data dict (e.g., 'Center', 'RBW')
            # app_attr_name: name of the attribute on app_instance (e.g., 'center_freq_hz_var', 'rbw_hz_var')
            
            value_str = preset_data.get(preset_key, '').strip()
            app_tk_var = getattr(self.app_instance, app_attr_name, None) # Get the Tkinter var by its attribute name

            if app_tk_var is None:
                debug_log(f"WARNING: app_instance does not have attribute '{app_attr_name}'. Cannot update. ⚠️",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return
            
            if not value_str:
                debug_log(f"Preset '{preset_key}' is empty. Skipping update for app_instance.{app_attr_name}. 🤷‍♀️",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return

            try:
                converted_value = conversion_func(value_str) * scale_factor
                app_tk_var.set(converted_value)
                debug_log(f"App var '{app_attr_name}' (from '{preset_key}') updated to '{converted_value}'.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except ValueError as e:
                debug_log(f"Error converting preset '{preset_key}' value '{value_str}' to {conversion_func.__name__} for app_instance.{app_attr_name}: {e}. Skipping update. 💥",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except Exception as e:
                debug_log(f"Unexpected error processing preset '{preset_key}' value '{value_str}' for app_instance.{app_attr_name}: {e}. Skipping update. 🤯",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)


        # Apply preset values to app_instance's Tkinter variables
        # Map preset_data keys (from CSV) to app_instance's variable attribute names (from DEFAULT_CONFIG)
        
        # Frequencies (from MHz in CSV to Hz in app_instance)
        get_and_set_app_var('Center', 'center_freq_hz_var', float, self.app_instance.MHZ_TO_HZ)
        get_and_set_app_var('Span', 'span_hz_var', float, self.app_instance.MHZ_TO_HZ)

        # RBW and VBW are already in Hz in the CSV, map to app_instance's rbw_hz_var and vbw_hz_var
        get_and_set_app_var('RBW', 'rbw_hz_var', float)
        get_and_set_app_var('VBW', 'vbw_hz_var', float)
        
        # Other instrument settings
        get_and_set_app_var('RefLevel', 'reference_level_dbm_var', float)
        get_and_set_app_var('Attenuation', 'attenuation_db_var', int)
        get_and_set_app_var('FreqShift', 'freq_shift_hz_var', float)

        # For boolean values, ensure they are correctly interpreted
        def get_and_set_bool_app_var(preset_key, app_attr_name):
            value_str = preset_data.get(preset_key, '').strip().upper()
            app_tk_var = getattr(self.app_instance, app_attr_name, None)

            if app_tk_var is None:
                debug_log(f"WARNING: app_instance does not have attribute '{app_attr_name}'. Cannot update. ⚠️",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return

            if value_str in ['ON', 'TRUE', 'WRITE']: # 'WRITE' used for MarkerMax state in CSV
                app_tk_var.set(True)
            elif value_str in ['OFF', 'FALSE', '']:
                app_tk_var.set(False)
            else:
                debug_log(f"Warning: Unexpected boolean value for '{preset_key}': '{value_str}'. Not updating app_instance.{app_attr_name}. ⚠️",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        get_and_set_bool_app_var('MaxHold', 'maxhold_enabled_var')
        get_and_set_bool_app_var('HighSens', 'high_sensitivity_var')
        get_and_set_bool_app_var('PreAmp', 'preamp_on_var')

        # Trace Modes (StringVars)
        get_and_set_app_var('Trace1Mode', 'trace1_mode_var')
        get_and_set_app_var('Trace2Mode', 'trace2_mode_var')
        get_and_set_app_var('Trace3Mode', 'trace3_mode_var')
        get_and_set_app_var('Trace4Mode', 'trace4_mode_var')

        # Marker Max (BooleanVars, assuming 'WRITE' means True in CSV)
        get_and_set_bool_app_var('Marker1Max', 'marker1_calculate_max_var')
        get_and_set_bool_app_var('Marker2Max', 'marker2_calculate_max_var')
        get_and_set_bool_app_var('Marker3Max', 'marker3_calculate_max_var')
        get_and_set_bool_app_var('Marker4Max', 'marker4_calculate_max_var')
        get_and_set_bool_app_var('Marker5Max', 'marker5_calculate_max_var')
        get_and_set_bool_app_var('Marker6Max', 'marker6_calculate_max_var')


        # Update the app_instance's last selected preset name and loaded values (these are already for display in MHz)
        self.app_instance.last_selected_preset_name_var.set(preset_data.get('NickName', preset_data.get('Filename', '')))
        
        # These are *additional* display variables on app_instance (not part of instrument control)
        # They need to be explicitly initialized in program_shared_values.py
        set_display_var(self.app_instance.last_loaded_preset_center_freq_mhz_var, 'Center', "{:.3f}", float)
        set_display_var(self.app_instance.last_loaded_preset_span_mhz_var, 'Span', "{:.3f}", float)
        set_display_var(self.app_instance.last_loaded_preset_rbw_hz_var, 'RBW', "{:.0f}", float)


        self.console_print_func(f"✅ GUI settings updated from local preset '{preset_data.get('NickName', 'Unnamed')}'.")
        debug_log("GUI settings updated from local preset. Done! ✅",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)