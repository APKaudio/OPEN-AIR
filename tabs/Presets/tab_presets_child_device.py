# tabs/Presets/tab_presets_child_device.py
#
# This file defines the DevicePresetsTab, a Tkinter Frame that provides
# functionality for managing instrument-defined presets. It allows querying
# presets from the connected instrument and loading selected presets.
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
# Version 20250802.1800.1 (New file for Device Presets, migrated from old tab_presets_child_preset.py)
# Version 20250802.2235.0 (Updated import and call for saving presets to use overwrite_user_presets_csv.)
# Version 20250802.2238.0 (Corrected import and call for query_device_presets_logic.)
# Version 20250802.2245.1 (Updated to use COLOR_PALETTE from style.py for Listbox styling.)

current_version = "20250802.2245.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 2245 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime # For timestamping user presets

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log
# Import the COLOR_PALETTE from style.py
from src.program_style import COLOR_PALETTE

# Import functions from preset utility modules
from tabs.Presets.utils_preset_query_and_load import load_selected_preset_logic, query_device_presets_logic
from tabs.Presets.utils_preset_process import load_user_presets_from_csv, overwrite_user_presets_csv

# Import instrument-related utilities
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings

class DevicePresetsTab(ttk.Frame):
    def __init__(self, parent, app_instance, console_print_func, style_obj, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj # Store the style object (though we'll use COLOR_PALETTE directly for Listbox)
        self.cached_user_presets = {} # To store user presets for nickname lookup

        self.create_widgets()
        self.setup_layout()
        self.bind_events()

        # Initial check for connection status
        is_connected = self.app_instance.inst is not None
        instrument_model = self.app_instance.connected_instrument_model.get() if hasattr(self.app_instance, 'connected_instrument_model') else ""
        self.on_connection_status_changed(is_connected, instrument_model)

        debug_log(f"DevicePresetsTab initialized. Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def create_widgets(self):
        # Frame for Device Presets controls
        self.device_presets_frame = ttk.LabelFrame(self, text="Device Presets", style='Custom.TLabelframe')
        self.device_presets_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Query Device Presets Button
        self.query_device_presets_button = ttk.Button(self.device_presets_frame,
                                                    text="Query Device Presets",
                                                    command=self.query_and_populate_device_presets,
                                                    style='TButton')
        self.query_device_presets_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.query_device_presets_button.config(state=tk.DISABLED) # Start disabled

        # Device Presets Listbox
        self.device_preset_listbox_label = ttk.Label(self.device_presets_frame, text="Available Device Presets:")
        self.device_preset_listbox_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.device_preset_listbox_frame = ttk.Frame(self.device_presets_frame, style='TFrame')
        self.device_preset_listbox_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.device_preset_listbox = tk.Listbox(self.device_preset_listbox_frame, height=10, width=50,
                                                selectmode=tk.SINGLE, exportselection=False,
                                                bg=COLOR_PALETTE.get('input_bg'), # Use COLOR_PALETTE
                                                fg=COLOR_PALETTE.get('input_fg'), # Use COLOR_PALETTE
                                                selectbackground=COLOR_PALETTE.get('select_bg'), # Use COLOR_PALETTE
                                                selectforeground=COLOR_PALETTE.get('select_fg')) # Use COLOR_PALETTE
        self.device_preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.device_preset_scrollbar = ttk.Scrollbar(self.device_preset_listbox_frame, orient="vertical", command=self.device_preset_listbox.yview)
        self.device_preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_preset_listbox.config(yscrollcommand=self.device_preset_scrollbar.set)

        # Load Device Preset Button
        self.load_device_preset_button = ttk.Button(self.device_presets_frame,
                                                    text="Load Selected Device Preset",
                                                    command=self.load_selected_device_preset,
                                                    style='TButton')
        self.load_device_preset_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.load_device_preset_button.config(state=tk.DISABLED) # Start disabled

        # --- Save Current Settings as User Preset ---
        self.save_current_frame = ttk.LabelFrame(self, text="Save Current Instrument Settings as User Preset", style='Custom.TLabelframe')
        self.save_current_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.filename_label = ttk.Label(self.save_current_frame, text="Filename (e.g., MY_PRESET.STA):")
        self.filename_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.filename_entry = ttk.Entry(self.save_current_frame, style='TEntry')
        self.filename_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.nickname_label = ttk.Label(self.save_current_frame, text="Nickname (optional):")
        self.nickname_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.nickname_entry = ttk.Entry(self.save_current_frame, style='TEntry')
        self.nickname_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.save_current_button = ttk.Button(self.save_current_frame,
                                            text="Save Current Settings to PRESETS.CSV",
                                            command=self.save_current_settings_as_user_preset,
                                            style='TButton')
        self.save_current_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.save_current_button.config(state=tk.DISABLED) # Start disabled

    def setup_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.device_presets_frame.grid_columnconfigure(0, weight=1)
        self.device_preset_listbox_frame.grid_columnconfigure(0, weight=1)
        self.save_current_frame.grid_columnconfigure(1, weight=1)

    def bind_events(self):
        self.device_preset_listbox.bind("<<ListboxSelect>>", self.on_device_preset_select)
        # Bind the connection status change event
        self.app_instance.bind("<<ConnectionStatusChanged>>", self._handle_connection_status_change_event)

    def _handle_connection_status_change_event(self, event=None):
        """
        Internal handler for the custom <<ConnectionStatusChanged>> event.
        Extracts status and model from the event and calls on_connection_status_changed.
        """
        is_connected = self.app_instance.inst is not None
        instrument_model = self.app_instance.connected_instrument_model.get() if hasattr(self.app_instance, 'connected_instrument_model') else ""
        self.on_connection_status_changed(is_connected, instrument_model)

    def on_connection_status_changed(self, is_connected, instrument_model):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connection status changed event received in DevicePresetsTab: Connected={is_connected}, Model={instrument_model}. Updating UI state.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Enable/disable "Query Device Presets" and "Load Selected Device Preset" buttons
        if is_connected and "N9342CN" in instrument_model:
            self.query_device_presets_button.config(state=tk.NORMAL)
            self.load_device_preset_button.config(state=tk.NORMAL)
            self.save_current_button.config(state=tk.NORMAL) # Enable Save button
            if not self.device_preset_listbox.get(0, tk.END): # Only auto-query if list is empty
                self.query_and_populate_device_presets() # Auto-query when connected to N9342CN
        else:
            self.query_device_presets_button.config(state=tk.DISABLED)
            self.load_device_preset_button.config(state=tk.DISABLED)
            self.save_current_button.config(state=tk.DISABLED) # Disable Save button
            self.populate_device_preset_listboxes([]) # Clear displayed presets
            self.console_print_func("⚠️ Query Device Presets button disabled (not connected or not N9342CN).")

    def query_and_populate_device_presets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Querying device presets. Getting the list of presets from the instrument. Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.app_instance.inst:
            presets = query_device_presets_logic(self.app_instance, self.console_print_func)
            self.populate_device_preset_listboxes(presets)
            if presets:
                self.console_print_func(f"✅ Found {len(presets)} device presets.")
            else:
                self.console_print_func("ℹ️ No device presets found or instrument does not support preset querying.")
        else:
            self.console_print_func("❌ Instrument not connected. Cannot query device presets.")
            debug_log("Instrument not connected. Cannot query device presets. What a mess!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def populate_device_preset_listboxes(self, presets):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating device preset listbox with {len(presets)} entries. Filling up the display!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self.device_preset_listbox.delete(0, tk.END)
        for preset in presets:
            self.device_preset_listbox.insert(tk.END, preset)
        debug_log("Device preset listbox populated.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def on_device_preset_select(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Device preset selected event triggered. Let's see what's chosen! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # Enable/disable Load button based on selection
        if self.device_preset_listbox.curselection():
            self.load_device_preset_button.config(state=tk.NORMAL)
        else:
            self.load_device_preset_button.config(state=tk.DISABLED)
        debug_log("Device preset selection handled.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def load_selected_device_preset(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading selected device preset. Applying the magic! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        selected_index = self.device_preset_listbox.curselection()
        if selected_index:
            selected_preset_name = self.device_preset_listbox.get(selected_index[0])
            self.console_print_func(f"Attempting to load device preset: {selected_preset_name}...")
            # For device presets, load_selected_preset_logic will directly use the name
            success, center, span, rbw = load_selected_preset_logic(
                self.app_instance,
                self.console_print_func,
                selected_preset_name,
                preset_type='device' # Indicate that this is a device preset
            )
            if success:
                self.console_print_func(f"✅ Successfully loaded device preset: {selected_preset_name}.")
                debug_log(f"Device preset '{selected_preset_name}' loaded successfully. Good job!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func(f"❌ Failed to load device preset: {selected_preset_name}. Something went wrong!")
                debug_log(f"Failed to load device preset '{selected_preset_name}'. This is a disaster!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("⚠️ No device preset selected to load. Pick one!")
            debug_log("No device preset selected to load.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def save_current_settings_as_user_preset(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Saving current settings as user preset. Getting all the goodies! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        filename = self.filename_entry.get().strip()
        nickname = self.nickname_entry.get().strip()

        if not filename:
            self.console_print_func("❌ Filename cannot be empty. Please enter a filename.")
            debug_log("Filename for new preset was empty. User needs to provide one.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        if not filename.endswith(".STA"):
            filename += ".STA"

        # Query current instrument settings
        current_settings = query_current_instrument_settings(self.app_instance, self.console_print_func)
        if not current_settings:
            self.console_print_func("❌ Could not retrieve current instrument settings to save.")
            debug_log("Failed to retrieve current instrument settings. Cannot save preset.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Prepare the new preset dictionary, ensuring all fields are present
        new_preset = {
            'Filename': filename,
            'NickName': nickname,
            'Center': str(current_settings.get('center_freq_hz', 0.0)),
            'Span': str(current_settings.get('span_freq_hz', 0.0)),
            'RBW': str(current_settings.get('rbw_hz', 0.0)),
            'VBW': str(current_settings.get('vbw_hz', '')),
            'RefLevel': str(current_settings.get('ref_level_dbm', '')),
            'Attenuation': str(current_settings.get('attenuation_db', '')),
            'MaxHold': current_settings.get('max_hold_enabled', 'OFF'), # Stored as ON/OFF, not boolean
            'HighSens': current_settings.get('high_sensitivity_enabled', 'OFF'), # Stored as ON/OFF
            'PreAmp': current_settings.get('preamp_enabled', 'OFF'), # Stored as ON/OFF
            'Trace1Mode': current_settings.get('trace1_mode', ''),
            'Trace2Mode': current_settings.get('trace2_mode', ''),
            'Trace3Mode': current_settings.get('trace3_mode', ''),
            'Trace4Mode': current_settings.get('trace4_mode', ''),
            'Marker1Max': str(current_settings.get('marker1_max', '')),
            'Marker2Max': str(current_settings.get('marker2_max', '')),
            'Marker3Max': str(current_settings.get('marker3_max', '')),
            'Marker4Max': str(current_settings.get('marker4_max', '')),
            'Marker5Max': str(current_settings.get('marker5_max', '')),
            'Marker6Max': str(current_settings.get('marker6_max', ''))
        }

        # Load existing presets
        all_presets = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        # Check if a preset with the same filename already exists and ask for overwrite
        existing_index = -1
        for i, preset in enumerate(all_presets):
            if preset.get('Filename') == filename:
                existing_index = i
                break

        if existing_index != -1:
            if tk.messagebox.askyesno("Overwrite Preset",
                                    f"A preset with filename '{filename}' already exists. Do you want to overwrite it?",
                                    parent=self): # Add parent for better dialog focus
                all_presets[existing_index] = new_preset
                self.console_print_func(f"ℹ️ Overwriting existing preset: {filename}.")
                debug_log(f"User confirmed overwrite for preset: {filename}",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func("ℹ️ Preset save cancelled by user.")
                debug_log("User cancelled preset overwrite.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return
        else:
            all_presets.append(new_preset)
            self.console_print_func(f"ℹ️ Adding new preset: {filename}.")
            debug_log(f"Adding new preset: {filename}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Save the updated list of presets back to the CSV
        if overwrite_user_presets_csv(self.app_instance.CONFIG_FILE_PATH, all_presets, self.console_print_func):
            self.console_print_func(f"✅ Preset '{filename}' saved successfully to PRESETS.CSV!")
            debug_log(f"Preset '{filename}' saved to CSV. All good!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            # Clear the entry fields after successful save
            self.filename_entry.delete(0, tk.END)
            self.nickname_entry.delete(0, tk.END)
        else:
            self.console_print_func(f"❌ Failed to save preset '{filename}'. Check console for errors.")
            debug_log(f"Failed to save preset '{filename}'. This is a nightmare!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the device presets list and updates button states.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("DevicePresetsTab selected. Refreshing data... Let's get this updated!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Ensure the connection status is checked and buttons are enabled/disabled correctly
        is_connected = self.app_instance.inst is not None
        instrument_model = self.app_instance.connected_instrument_model.get() if hasattr(self.app_instance, 'connected_instrument_model') else ""
        self.on_connection_status_changed(is_connected, instrument_model)

        # Reload cached user presets for nickname lookup when saving current settings
        # This part might not be strictly necessary for this tab's direct functionality
        # but is good practice if this tab also interacts with user presets beyond just saving.
        # self.cached_user_presets = {
        #     p['Filename']: p for p in load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        # }