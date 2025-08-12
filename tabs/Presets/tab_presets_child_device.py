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
# Version 20250811.223500.1 (FIXED: Corrected an AttributeError by changing the call to the private method `_on_connection_status_changed` in the __init__ method and event handler.)

current_version = "20250811.223500.1"
current_version_hash = 20250811 * 223500 * 1

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime # For timestamping user presets

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log
# Import the COLOR_PALETTE from style.py
from src.program_style import COLOR_PALETTE

# Import functions from preset utility modules
from tabs.Presets.utils_preset_process import load_user_presets_from_csv, overwrite_user_presets_csv
from tabs.Presets.utils_push_preset import push_preset_logic
# Import instrument-related utilities
from tabs.Instrument.instrument_logic import query_current_settings_logic
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe

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
        self._on_connection_status_changed(is_connected, instrument_model)

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
                                                    command=self._query_and_populate_device_presets,
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
                                                    command=self._load_selected_device_preset,
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
        self.device_preset_listbox.bind("<<ListboxSelect>>", self._on_device_preset_select)
        # Bind the connection status change event
        self.app_instance.bind("<<ConnectionStatusChanged>>", self._handle_connection_status_change_event)

    def _handle_connection_status_change_event(self, event=None):
        """
        Internal handler for the custom <<ConnectionStatusChanged>> event.
        Extracts status and model from the event and calls on_connection_status_changed.
        """
        is_connected = self.app_instance.inst is not None
        instrument_model = self.app_instance.connected_instrument_model.get() if hasattr(self.app_instance, 'connected_instrument_model') else ""
        self._on_connection_status_changed(is_connected, instrument_model)

    def _on_connection_status_changed(self, is_connected, instrument_model):
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
                self._query_and_populate_device_presets() # Auto-query when connected to N9342CN
        else:
            self.query_device_presets_button.config(state=tk.DISABLED)
            self.load_device_preset_button.config(state=tk.DISABLED)
            self.save_current_button.config(state=tk.DISABLED) # Disable Save button
            self._populate_device_preset_listboxes([]) # Clear displayed presets
            self.console_print_func("⚠️ Query Device Presets button disabled (not connected or not N9342CN).")

    def _query_and_populate_device_presets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Querying device presets. Getting the list of presets from the instrument. Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.app_instance.inst:
            presets = self._query_device_presets_logic()
            self._populate_device_preset_listboxes(presets)
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

    def _populate_device_preset_listboxes(self, presets):
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

    def _on_device_preset_select(self, event):
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

    def _load_selected_device_preset(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading selected device preset. Applying the magic! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        selected_index = self.device_preset_listbox.curselection()
        if selected_index:
            selected_preset_name = self.device_preset_listbox.get(selected_index[0])
            self.console_print_func(f"Attempting to load device preset: {selected_preset_name}...")
            # For device presets, _load_selected_preset_logic will directly use the name
            success = self.__load_selected_preset_logic(
                selected_preset_name,
                is_device_preset=True, # Indicate that this is a device preset
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
        current_settings = query_current_settings_logic(self.app_instance, self.console_print_func)
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

    def __load_selected_preset_logic(self, selected_preset_name, is_device_preset=True, preset_data_dict=None):
        """
        Loads a selected preset (either from device or local CSV) onto the instrument
        and updates the GUI's settings variables.

        This is a modified version of the original, now a private method within the class.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to load preset: '{selected_preset_name}'. Is Device Preset: {is_device_preset}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        try:
            if is_device_preset:
                if not self.app_instance.inst:
                    self.console_print_func("❌ No instrument connected. Cannot load device preset.")
                    debug_log("No instrument connected. Aborting device preset load.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False

                # Check if the connected device is N9342CN for loading device presets
                if hasattr(self.app_instance, 'connected_instrument_model') and \
                   self.app_instance.connected_instrument_model.get() != "N9342CN":
                    self.console_print_func("⚠️ Device is not N9342CN. Cannot load device presets (feature limited to N9342CN).")
                    debug_log("Device is not N9342CN. Aborting device preset load.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False

                load_command = f":MMEMory:LOAD:STATe \"{selected_preset_name}\""
                if write_safe(self.app_instance.inst, load_command, self.app_instance, self.console_print_func):
                    self.console_print_func(f"✅ Device preset '{selected_preset_name}' loaded to instrument.")
                    debug_log(f"Device preset '{selected_preset_name}' loaded to instrument.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    
                    # After loading, query the instrument for its current settings to update GUI
                    settings = query_current_settings_logic(self.app_instance, self.console_print_func)
                    
                    if settings:
                        center_freq_hz = settings.get('center_freq_hz') if settings.get('center_freq_hz') is not None else 0.0
                        span_hz = settings.get('span_hz') if settings.get('span_hz') is not None else 0.0
                        rbw_hz = settings.get('rbw_hz') if settings.get('rbw_hz') is not None else 0.0

                        # Update Tkinter variables in the app instance
                        self.app_instance.center_freq_hz_var.set(center_freq_hz)
                        self.app_instance.span_hz_var.set(span_hz)
                        self.app_instance.rbw_hz_var.set(rbw_hz)
                        self.app_instance.reference_level_dbm_var.set(settings.get('ref_level_dbm'))
                        self.app_instance.preamp_on_var.set(settings.get('preamp_on'))
                        self.app_instance.high_sensitivity_var.set(settings.get('high_sensitivity_on'))

                        self.console_print_func(f"GUI settings updated from device preset: Center Freq={center_freq_hz / self.app_instance.MHZ_TO_HZ:.3f} MHz, Span={span_hz / self.app_instance.MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz / 1000:.1f} kHz. Looking good!")
                        debug_log(f"GUI settings updated from loaded device preset.",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                        return True
                    else:
                        self.console_print_func("❌ Failed to query settings after loading device preset. This is frustrating!")
                        debug_log("Failed to query settings after loading device preset. What a pain!",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                        return False
                else:
                    self.console_print_func(f"❌ Failed to load device preset '{selected_preset_name}'. This is frustrating!")
                    debug_log(f"Failed to load device preset '{selected_preset_name}'. What a pain!",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False
            else: # It's a local user preset
                if preset_data_dict:
                    # Update Tkinter variables directly from the provided dictionary
                    center_freq_hz = float(preset_data_dict.get('Center', 0.0))
                    span_hz = float(preset_data_dict.get('Span', 0.0))
                    rbw_hz = float(preset_data_dict.get('RBW', 0.0))

                    self.app_instance.center_freq_hz_var.set(center_freq_hz)
                    self.app_instance.span_hz_var.set(span_hz)
                    self.app_instance.rbw_hz_var.set(rbw_hz)

                    self.console_print_func(f"GUI settings updated from preset: Center Freq={center_freq_hz / self.app_instance.MHZ_TO_HZ:.3f} MHz, Span={span_hz / self.app_instance.MHZ_TO_HZ:.3f} MHz, RBW={rbw_hz:.0f} Hz. Looking good!")
                    debug_log(f"GUI settings updated from loaded local preset.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return True
                else:
                    self.console_print_func(f"❌ Failed to load local preset '{selected_preset_name}'. Preset data not provided.")
                    debug_log(f"Failed to load local preset '{selected_preset_name}'. Preset data dictionary is missing.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    return False

        except Exception as e:
            self.console_print_func(f"❌ An unexpected error occurred in __load_selected_preset_logic: {e}. This is a disaster!")
            debug_log(f"An unexpected error occurred in __load_selected_preset_logic: {e}. Fucking hell!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False