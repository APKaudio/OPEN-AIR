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

current_version = "20250802.1800.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1800 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime # For timestamping user presets

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import functions from the newly refactored preset utility modules
from tabs.Presets.utils_preset_query_and_load import query_device_presets_logic, load_selected_preset_logic
from tabs.Presets.utils_preset_process import save_user_preset_to_csv, load_user_presets_from_csv # Need this for saving current settings as user preset

class DevicePresetsTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for managing instrument-defined presets.
    It includes sections for querying presets from the connected instrument and
    loading selected presets.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        """
        Initializes the DevicePresetsTab.

        Inputs:
            master (tk.Widget): The parent widget (the ttk.Notebook).
            app_instance (App): The main application instance, used for accessing
                                shared state like instrument connection, Tkinter variables,
                                and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            style_obj (ttk.Style): The ttk.Style object for applying custom styles.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing DevicePresetsTab. Version: {current_version}. Let's get these device presets organized!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self._create_widgets()
        self.instrument_presets = [] # To store names of presets from the instrument
        self.cached_user_presets = {} # To store user presets for nickname lookup

        # Initial population of device presets (if connected)
        self._query_device_presets()

        debug_log(f"DevicePresetsTab initialized. Version: {current_version}. Ready to rock and roll with device presets!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Device Presets tab.
        This includes sections for Instrument Presets and a button to save current settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating DevicePresetsTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1) # Listboxes row
        self.grid_rowconfigure(1, weight=0) # Save button row

        # --- Instrument Presets Section ---
        instrument_preset_frame = ttk.LabelFrame(self, text="Instrument Presets (from Device)", style='Dark.TLabelframe')
        instrument_preset_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        instrument_preset_frame.grid_columnconfigure(0, weight=1)
        instrument_preset_frame.grid_rowconfigure(0, weight=0) # Button row
        instrument_preset_frame.grid_rowconfigure(1, weight=1) # Listbox row

        self.query_device_presets_button = ttk.Button(instrument_preset_frame, text="Query Device Presets", command=self._query_device_presets, style='Blue.TButton')
        self.query_device_presets_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Inner frame for MON and Other presets listboxes
        listbox_container_frame = ttk.Frame(instrument_preset_frame, style='Dark.TFrame')
        listbox_container_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        listbox_container_frame.grid_columnconfigure(0, weight=1)
        listbox_container_frame.grid_columnconfigure(1, weight=1)
        listbox_container_frame.grid_rowconfigure(0, weight=1)

        # MON Presets Listbox
        mon_frame = ttk.LabelFrame(listbox_container_frame, text="MON Presets", style='Dark.TLabelframe')
        mon_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        mon_frame.grid_columnconfigure(0, weight=1)
        mon_frame.grid_rowconfigure(0, weight=1)
        self.mon_preset_listbox = tk.Listbox(mon_frame, bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a", selectforeground="white")
        self.mon_preset_listbox.grid(row=0, column=0, sticky="nsew")
        self.mon_preset_listbox.bind("<<ListboxSelect>>", self._on_instrument_preset_selected)
        mon_scrollbar = ttk.Scrollbar(mon_frame, orient="vertical", command=self.mon_preset_listbox.yview)
        mon_scrollbar.grid(row=0, column=1, sticky="ns")
        self.mon_preset_listbox.config(yscrollcommand=mon_scrollbar.set)

        # Other Presets Listbox
        other_frame = ttk.LabelFrame(listbox_container_frame, text="Other Presets", style='Dark.TLabelframe')
        other_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        other_frame.grid_columnconfigure(0, weight=1)
        other_frame.grid_rowconfigure(0, weight=1)
        self.other_preset_listbox = tk.Listbox(other_frame, bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a", selectforeground="white")
        self.other_preset_listbox.grid(row=0, column=0, sticky="nsew")
        self.other_preset_listbox.bind("<<ListboxSelect>>", self._on_instrument_preset_selected)
        other_scrollbar = ttk.Scrollbar(other_frame, orient="vertical", command=self.other_preset_listbox.yview)
        other_scrollbar.grid(row=0, column=1, sticky="ns")
        self.other_preset_listbox.config(yscrollcommand=other_scrollbar.set)


        # --- Save Current Settings as User Preset Button ---
        ttk.Button(self, text="Save Current Instrument Settings as Local User Preset", command=self._save_current_settings_as_user_preset, style='Green.TButton').grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        debug_log("DevicePresetsTab widgets created. Ready to interact with the device!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def populate_device_preset_listboxes(self, presets):
        """
        Populates the MON and Other preset listboxes with names of presets found on the device.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating device preset listboxes with {len(presets)} presets. Get ready for some data!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.mon_preset_listbox.delete(0, tk.END)
        self.other_preset_listbox.delete(0, tk.END)
        self.instrument_presets = presets # Store the actual list

        mon_presets = sorted([p for p in presets if "MON" in p.upper()])
        other_presets = sorted([p for p in presets if "MON" not in p.upper()])

        for preset_name in mon_presets:
            self.mon_preset_listbox.insert(tk.END, preset_name)
        for preset_name in other_presets:
            self.other_preset_listbox.insert(tk.END, preset_name)

        debug_log("Device preset listboxes populated. Mission accomplished!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _query_device_presets(self):
        """
        Initiates the process of querying available presets from the connected instrument.
        This button is only active if the connected device is "N9342CN".
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Calling query_device_presets_logic... Time to talk to the instrument!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("⚠️ Not connected to an instrument. Cannot query device presets.")
            debug_log("No instrument connected for querying device presets. Aborting.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self.query_device_presets_button.config(state=tk.DISABLED)
            return

        # Check if the connected device is N9342CN
        if hasattr(self.app_instance, 'connected_instrument_model') and \
           self.app_instance.connected_instrument_model.get() == "N9342CN":
            self.query_device_presets_button.config(state=tk.NORMAL)
            self.instrument_presets = query_device_presets_logic(self.app_instance, self.console_print_func)
            self.populate_device_preset_listboxes(self.instrument_presets)
        else:
            self.console_print_func("⚠️ Device is not N9342CN. Cannot query device presets (feature limited to N9342CN).")
            debug_log("Device is not N9342CN. Disabling query device presets button.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self.query_device_presets_button.config(state=tk.DISABLED)
            self.populate_device_preset_listboxes([]) # Clear displayed presets if not N9342CN

    def _on_instrument_preset_selected(self, event):
        """
        Handles selection of an instrument preset from either listbox.
        Loads the selected preset onto the instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        # Determine which listbox was clicked
        if event.widget == self.mon_preset_listbox:
            selected_indices = self.mon_preset_listbox.curselection()
            listbox_type = "MON"
        elif event.widget == self.other_preset_listbox:
            selected_indices = self.other_preset_listbox.curselection()
            listbox_type = "Other"
        else:
            return # Not a listbox we care about

        if selected_indices:
            index = selected_indices[0]
            selected_preset_name = event.widget.get(index)
            self.console_print_func(f"Selected {listbox_type} instrument preset: {selected_preset_name}")
            debug_log(f"Instrument preset selected: {selected_preset_name}. Let's load this bad boy!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

            # Update the app_instance's last selected preset name
            self.app_instance.last_selected_preset_name_var.set(selected_preset_name)

            # Call the logic to load the preset and update GUI settings
            success, center_freq, span, rbw = load_selected_preset_logic(self.app_instance, selected_preset_name, self.console_print_func)
            if success:
                self.console_print_func(f"✅ Instrument preset '{selected_preset_name}' loaded. Success!")
                debug_log(f"Instrument preset '{selected_preset_name}' loaded successfully. BOOM!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

                # Update the app_instance's loaded preset details for display in other tabs
                self.app_instance.last_loaded_preset_center_freq_mhz_var.set(f"{center_freq / self.app_instance.MHZ_TO_HZ:.3f}")
                self.app_instance.last_loaded_preset_span_mhz_var.set(f"{span / self.app_instance.MHZ_TO_HZ:.3f}")
                self.app_instance.last_loaded_preset_rbw_hz_var.set(f"{rbw:.0f}")

                # Ensure the Instrument tab's display updates
                if hasattr(self.app_instance, 'instrument_parent_tab') and \
                   hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab') and \
                   hasattr(self.app_instance.instrument_parent_tab.instrument_connection_tab, '_query_current_settings'):
                    self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()
            else:
                self.console_print_func(f"❌ Failed to load instrument preset '{selected_preset_name}'. This is a nightmare!")
                debug_log(f"Failed to load instrument preset '{selected_preset_name}'. What the hell happened?!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

    def _save_current_settings_as_user_preset(self):
        """
        Prompts the user for a preset name and saves the current instrument settings
        (Center Freq, Span, RBW, Markers) as a new user-defined preset to the CSV file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to save current settings as user preset... Let's make this happen!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # First, query the current instrument settings
        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument connected. Cannot save current settings as preset. Connect the damn thing first!")
            debug_log("No instrument connected, cannot save current settings as preset. Fucking useless!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Use the _query_current_settings method from the Instrument Connection tab
        # This method is expected to query the instrument and update the app_instance's Tkinter variables
        # and also return the queried values.
        if hasattr(self.app_instance, 'instrument_parent_tab') and \
           hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab') and \
           hasattr(self.app_instance.instrument_parent_tab.instrument_connection_tab, '_query_current_settings'):
            # Call the _query_current_settings method which now returns the queried values
            center_freq_mhz, span_mhz, rbw_hz, ref_level_dbm, preamp_on, high_sensitivity = \
                self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()

            # Convert MHz back to Hz for saving if necessary, or ensure query returns Hz
            center_freq_hz = center_freq_mhz * self.app_instance.MHZ_TO_HZ
            span_hz = span_mhz * self.app_instance.MHZ_TO_HZ

            # Placeholder for Markers - in a real scenario, you'd query these from the instrument
            # For now, let's assume no markers are set or a default value
            markers_data = "N/A" # You would query this from the instrument if available

            if center_freq_hz is None: # If query failed
                self.console_print_func("❌ Failed to query current instrument settings. Cannot save preset. This is a disaster!")
                debug_log("Failed to query current instrument settings for saving preset. What a mess!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return
        else:
            self.console_print_func("❌ Instrument connection tab or _query_current_settings method not found. Cannot save preset. This is a critical error!")
            debug_log("Instrument connection tab or _query_current_settings method not found. Fucking hell!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Prompt for a nickname for the preset
        nickname = simpledialog.askstring("Save User Preset", "Enter a nickname for this preset:",
                                          parent=self.app_instance)
        if nickname is None: # User cancelled
            self.console_print_func("ℹ️ Preset save cancelled. Fine, be that way!")
            debug_log("Preset save cancelled by user. What a waste!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Generate a unique filename (e.g., based on timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"USER_{timestamp}.STA" # Use .STA extension for consistency with device presets

        preset_data = {
            'Filename': filename,
            'Center': center_freq_hz,
            'Span': span_hz,
            'RBW': rbw_hz,
            'NickName': nickname,
            'Markers': markers_data # New Markers column
            # Add other settings if desired, e.g., 'RefLevel': ref_level_dbm, etc.
        }

        save_user_preset_to_csv(preset_data, self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        self.console_print_func(f"✅ Current settings saved as user preset: '{nickname}'. Success!")
        debug_log(f"Current settings saved as user preset: '{nickname}'. BOOM!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # After saving, refresh the Local Presets tab to show the new entry
        if hasattr(self.app_instance, 'presets_parent_tab') and \
           hasattr(self.app_instance.presets_parent_tab, 'local_presets_tab') and \
           hasattr(self.app_instance.presets_parent_tab.local_presets_tab, 'populate_presets_table'):
            self.app_instance.presets_parent_tab.local_presets_tab.populate_presets_table()


    def on_connection_status_changed(self, is_connected, instrument_model):
        """
        Called by the main application when the instrument connection status changes.
        This method updates the state of the query presets button based on connection
        and instrument model.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"DevicePresetsTab received connection status update: Connected={is_connected}, Model={instrument_model}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if is_connected and instrument_model == "N9342CN":
            self.query_device_presets_button.config(state=tk.NORMAL)
            self._query_device_presets() # Auto-query when connected to N9342CN
        else:
            self.query_device_presets_button.config(state=tk.DISABLED)
            self.populate_device_preset_listboxes([]) # Clear displayed presets
            self.console_print_func("⚠️ Query Device Presets button disabled (not connected or not N9342CN).")


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
        self.cached_user_presets = {
            p['Filename']: p for p in load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        }

