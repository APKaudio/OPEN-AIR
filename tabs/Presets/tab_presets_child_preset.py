# tabs/Presets/tab_presets_child_preset.py
#
# This file defines the PresetFilesTab, a Tkinter Frame that provides
# functionality for managing instrument and user-defined presets.
# It allows querying presets from the connected instrument, loading
# selected presets, and saving/loading user presets to/from a CSV file.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
# Version 20250801.1920.1 (Reconstructed file to fix circular import, implemented PresetFilesTab logic.)

current_version = "20250801.1920.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime # For timestamping user presets

from utils.utils_instrument_control import debug_print
from tabs.Presets.utils_preset import (
    load_user_presets_from_csv, save_user_preset_to_csv,
    query_device_presets_logic, load_selected_preset_logic
)

class PresetFilesTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for managing instrument and
    user-defined presets. It includes sections for querying presets from the
    connected instrument, loading selected presets, and saving/loading
    user presets to/from a CSV file.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the PresetFilesTab.

        Inputs:
            master (tk.Widget): The parent widget (the ttk.Notebook).
            app_instance (App): The main application instance, used for accessing
                                shared state like instrument connection, Tkinter variables,
                                and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"🚫🐛 [DEBUG] Initializing PresetFilesTab. Version: {current_version}",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self.console_print_func)

        self._create_widgets()
        self.instrument_presets = [] # To store names of presets from the instrument
        self.user_presets = []       # To store details of user-saved presets

        # Initial population of user presets from CSV
        self.populate_user_preset_buttons()

        debug_print(f"🚫🐛 [DEBUG] PresetFilesTab initialized. Version: {current_version}",
                    file=f"{current_file} - {current_version}",
                    function=current_function,
                    console_print_func=self.console_print_func)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Preset Files tab.
        This includes sections for Instrument Presets and User Presets.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Creating PresetFilesTab widgets...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Configure grid for the main frame of this tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Instrument Presets Section ---
        instrument_preset_frame = ttk.LabelFrame(self, text="Instrument Presets (from Device)", style='Dark.TLabelframe')
        instrument_preset_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        instrument_preset_frame.grid_columnconfigure(0, weight=1)
        instrument_preset_frame.grid_rowconfigure(0, weight=0) # Button row
        instrument_preset_frame.grid_rowconfigure(1, weight=1) # Listbox row

        ttk.Button(instrument_preset_frame, text="Query Device Presets", command=self._query_device_presets).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.instrument_preset_listbox = tk.Listbox(instrument_preset_frame, bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a", selectforeground="white")
        self.instrument_preset_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.instrument_preset_listbox.bind("<<ListboxSelect>>", self._on_instrument_preset_selected)

        instrument_preset_scrollbar = ttk.Scrollbar(instrument_preset_frame, orient="vertical", command=self.instrument_preset_listbox.yview)
        instrument_preset_scrollbar.grid(row=1, column=1, sticky="ns")
        self.instrument_preset_listbox.config(yscrollcommand=instrument_preset_scrollbar.set)

        # --- User Presets Section ---
        user_preset_frame = ttk.LabelFrame(self, text="User Presets (Saved Locally)", style='Dark.TLabelframe')
        user_preset_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        user_preset_frame.grid_columnconfigure(0, weight=1)
        user_preset_frame.grid_rowconfigure(0, weight=0) # Button row
        user_preset_frame.grid_rowconfigure(1, weight=1) # Listbox row

        user_preset_button_frame = ttk.Frame(user_preset_frame)
        user_preset_button_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        user_preset_button_frame.grid_columnconfigure(0, weight=1)
        user_preset_button_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(user_preset_button_frame, text="Save Current Settings as Preset", command=self._save_current_settings_as_user_preset).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(user_preset_button_frame, text="Reload User Presets", command=self.populate_user_preset_buttons).grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        self.user_preset_listbox = tk.Listbox(user_preset_frame, bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a", selectforeground="white")
        self.user_preset_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.user_preset_listbox.bind("<<ListboxSelect>>", self._on_user_preset_selected)

        user_preset_scrollbar = ttk.Scrollbar(user_preset_frame, orient="vertical", command=self.user_preset_listbox.yview)
        user_preset_scrollbar.grid(row=1, column=1, sticky="ns")
        self.user_preset_listbox.config(yscrollcommand=user_preset_scrollbar.set)

        debug_print("PresetFilesTab widgets created.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def populate_instrument_preset_buttons(self, presets):
        """
        Populates the instrument preset listbox with names of presets found on the device.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"Populating instrument preset buttons with {len(presets)} presets.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        self.instrument_preset_listbox.delete(0, tk.END)
        self.instrument_presets = presets # Store the actual list
        for preset_name in presets:
            self.instrument_preset_listbox.insert(tk.END, preset_name)
        debug_print("Instrument preset buttons populated.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def populate_user_preset_buttons(self):
        """
        Loads user presets from the CSV file and populates the user preset listbox.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Populating user preset buttons...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        self.user_preset_listbox.delete(0, tk.END)
        self.user_presets = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        for preset in self.user_presets:
            display_name = preset.get('NickName', preset.get('Filename', 'Unnamed Preset'))
            self.user_preset_listbox.insert(tk.END, display_name)
        debug_print(f"Populated {len(self.user_presets)} user preset buttons.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _query_device_presets(self):
        """
        Initiates the process of querying available presets from the connected instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Calling query_device_presets_logic...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        query_device_presets_logic(self.app_instance, self.console_print_func)


    def _on_instrument_preset_selected(self, event):
        """
        Handles selection of an instrument preset from the listbox.
        Loads the selected preset onto the instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_indices = self.instrument_preset_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_preset_name = self.instrument_preset_listbox.get(index)
            self.console_print_func(f"Selected instrument preset: {selected_preset_name}")
            debug_print(f"Instrument preset selected: {selected_preset_name}", file=current_file, function=current_function, console_print_func=self.console_print_func)

            # Update the app_instance's last selected preset name
            self.app_instance.last_selected_preset_name_var.set(selected_preset_name)

            # Call the logic to load the preset and update GUI settings
            success, center_freq, span, rbw = load_selected_preset_logic(self.app_instance, selected_preset_name, self.console_print_func)
            if success:
                self.console_print_func(f"✅ Instrument preset '{selected_preset_name}' loaded.")
                debug_print(f"Instrument preset '{selected_preset_name}' loaded successfully.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                
                # Update the app_instance's loaded preset details
                self.app_instance.last_loaded_preset_center_freq_mhz_var.set(f"{center_freq / self.app_instance.MHZ_TO_HZ:.3f}")
                self.app_instance.last_loaded_preset_span_mhz_var.set(f"{span / self.app_instance.MHZ_TO_HZ:.3f}")
                self.app_instance.last_loaded_preset_rbw_hz_var.set(f"{rbw:.0f}")

                # Ensure the Instrument tab's display updates
                if hasattr(self.app_instance, 'instrument_parent_tab') and hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab'):
                    self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()
            else:
                self.console_print_func(f"❌ Failed to load instrument preset '{selected_preset_name}'.")
                debug_print(f"Failed to load instrument preset '{selected_preset_name}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_user_preset_selected(self, event):
        """
        Handles selection of a user-defined preset from the listbox.
        Loads the selected preset onto the instrument and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        selected_indices = self.user_preset_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_preset_data = self.user_presets[index]
            preset_filename = selected_preset_data.get('Filename')
            display_name = selected_preset_data.get('NickName', preset_filename)

            self.console_print_func(f"Selected user preset: {display_name}")
            debug_print(f"User preset selected: {display_name} (Filename: {preset_filename})", file=current_file, function=current_function, console_print_func=self.console_print_func)

            # Update the app_instance's last selected preset name
            self.app_instance.last_selected_preset_name_var.set(display_name)


            if self.app_instance.inst:
                # Load the preset onto the instrument using its filename
                success, center_freq, span, rbw = load_selected_preset_logic(self.app_instance, preset_filename, self.console_print_func)
                if success:
                    self.console_print_func(f"✅ User preset '{display_name}' loaded to instrument.")
                    debug_print(f"User preset '{display_name}' loaded to instrument successfully.", file=current_file, function=current_function, console_print_func=self.console_print_func)

                    # Update the app_instance's loaded preset details
                    self.app_instance.last_loaded_preset_center_freq_mhz_var.set(f"{center_freq / self.app_instance.MHZ_TO_HZ:.3f}")
                    self.app_instance.last_loaded_preset_span_mhz_var.set(f"{span / self.app_instance.MHZ_TO_HZ:.3f}")
                    self.app_instance.last_loaded_preset_rbw_hz_var.set(f"{rbw:.0f}")

                    # Also update relevant Tkinter variables in the main app to reflect the loaded settings
                    # This assumes the preset data contains the values to set
                    # Note: This is a simplified example. A real implementation would map preset data fields
                    # to the correct Tkinter variables and handle type conversions.
                    if 'Center' in selected_preset_data:
                        self.app_instance.current_center_freq_var.set(f"{float(selected_preset_data['Center']) / self.app_instance.MHZ_TO_HZ:.3f}")
                    if 'Span' in selected_preset_data:
                        self.app_instance.current_span_var.set(f"{float(selected_preset_data['Span']) / self.app_instance.MHZ_TO_HZ:.3f}")
                    if 'RBW' in selected_preset_data:
                        self.app_instance.current_rbw_var.set(f"{float(selected_preset_data['RBW']):.0f}")
                    
                    # Ensure the Instrument tab's display updates
                    if hasattr(self.app_instance, 'instrument_parent_tab') and hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab'):
                        self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()

                else:
                    self.console_print_func(f"❌ Failed to load user preset '{display_name}' to instrument.")
                    debug_print(f"Failed to load user preset '{display_name}' to instrument.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            else:
                self.console_print_func("⚠️ No instrument connected. Cannot load user preset to device. Updating GUI only.")
                debug_print("No instrument connected. Loading user preset to GUI only.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                # If no instrument, just update GUI based on saved preset values
                if 'Center' in selected_preset_data:
                    self.app_instance.current_center_freq_var.set(f"{float(selected_preset_data['Center']) / self.app_instance.MHZ_TO_HZ:.3f}")
                if 'Span' in selected_preset_data:
                    self.app_instance.current_span_var.set(f"{float(selected_preset_data['Span']) / self.app_instance.MHZ_TO_HZ:.3f}")
                if 'RBW' in selected_preset_data:
                    self.app_instance.current_rbw_var.set(f"{float(selected_preset_data['RBW']):.0f}")
                
                # Ensure the Instrument tab's display updates
                if hasattr(self.app_instance, 'instrument_parent_tab') and hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab'):
                    # Call query_current_settings to refresh the display, but it won't query hardware
                    self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()


    def _save_current_settings_as_user_preset(self):
        """
        Prompts the user for a preset name and saves the current instrument settings
        (Center Freq, Span, RBW) as a new user-defined preset to the CSV file.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Attempting to save current settings as user preset...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # First, query the current instrument settings
        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument connected. Cannot save current settings as preset.")
            debug_print("No instrument connected, cannot save current settings as preset.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        # Use query_current_instrument_settings_logic to get all settings from the instrument
        # This will also update the app_instance's Tkinter variables for current display
        center_freq_hz, span_hz, rbw_hz, ref_level_dbm, freq_shift_hz, high_sensitivity, preamp_on = \
            self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()

        if center_freq_hz is None: # If query failed
            self.console_print_func("❌ Failed to query current instrument settings. Cannot save preset.")
            debug_print("Failed to query current instrument settings for saving preset.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        # Prompt for a nickname for the preset
        nickname = simpledialog.askstring("Save User Preset", "Enter a nickname for this preset:",
                                          parent=self.app_instance)
        if nickname is None: # User cancelled
            self.console_print_func("ℹ️ Preset save cancelled.")
            debug_print("Preset save cancelled by user.", file=current_file, function=current_function, console_print_func=self.console_print_func)
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
            # Add other settings if desired, e.g., 'RefLevel': ref_level_dbm, etc.
        }

        save_user_preset_to_csv(preset_data, self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        self.populate_user_preset_buttons() # Refresh the user presets list
        self.console_print_func(f"✅ Current settings saved as user preset: '{nickname}'")
        debug_print(f"Current settings saved as user preset: '{nickname}'", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the user presets table and queries device presets.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("PresetFilesTab selected. Refreshing data...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        self.populate_user_preset_buttons() # Always refresh user presets
        self._query_device_presets() # Query device presets when tab is selected
