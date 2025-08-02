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

current_version = "20250802.1800.4" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1800 * 4 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import functions from preset utility modules
from tabs.Presets.utils_preset_process import load_user_presets_from_csv
from tabs.Presets.utils_preset_query_and_load import load_selected_preset_logic

class LocalPresetsTab(ttk.Frame):
    """
    A Tkinter Frame for displaying and loading user-defined local presets.
    It lists presets from PRESETS.CSV and allows the user to load them,
    which updates the main application's instrument settings.
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

        self._create_widgets()
        self.populate_local_presets_list() # Initial population

        debug_log(f"LocalPresetsTab initialized. Version: {current_version}. Local presets ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Local Presets tab.
        This includes a listbox to display presets and a button to load them.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating LocalPresetsTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Listbox row
        self.grid_rowconfigure(1, weight=0) # Button row

        # --- Local Presets Listbox ---
        listbox_frame = ttk.LabelFrame(self, text="Available Local Presets", style='Dark.TLabelframe')
        listbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_rowconfigure(0, weight=1)

        self.local_presets_listbox = tk.Listbox(listbox_frame, bg="#2b2b2b", fg="#cccccc", selectbackground="#4a4a4a", selectforeground="white")
        self.local_presets_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.local_presets_listbox.bind("<<ListboxSelect>>", self._on_local_preset_selected)

        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.local_presets_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.local_presets_listbox.config(yscrollcommand=listbox_scrollbar.set)

        # --- Load Button ---
        ttk.Button(self, text="Load Selected Local Preset", command=self._load_selected_local_preset, style='Green.TButton').grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        debug_log("LocalPresetsTab widgets created. Listbox and load button are ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def populate_local_presets_list(self):
        """
        Loads user presets from the PRESETS.CSV file and populates the listbox.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets list...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.local_presets_listbox.delete(0, tk.END)
        self.user_presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        if not self.user_presets_data:
            self.local_presets_listbox.insert(tk.END, "No local presets found.")
            self.local_presets_listbox.config(state=tk.DISABLED)
            self.console_print_func("ℹ️ No local presets found in PRESETS.CSV.")
            debug_log("No local presets found.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        self.local_presets_listbox.config(state=tk.NORMAL) # Enable if presets are found
        for preset in self.user_presets_data:
            display_name = preset.get('NickName', preset.get('Filename', 'Unnamed Preset'))
            self.local_presets_listbox.insert(tk.END, display_name)
        
        self.console_print_func(f"✅ Loaded {len(self.user_presets_data)} local presets for display.")
        debug_log(f"Local presets list populated with {len(self.user_presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_local_preset_selected(self, event):
        """
        Handles selection of a local preset from the listbox.
        (Does not load automatically, just updates internal state if needed).
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_indices = self.local_presets_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_display_name = self.local_presets_listbox.get(index)
            debug_log(f"Local preset selected: {selected_display_name}. Ready to load!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        
    def _load_selected_local_preset(self):
        """
        Loads the currently selected local preset onto the instrument (if connected)
        and updates the GUI's settings variables.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_indices = self.local_presets_listbox.curselection()
        if not selected_indices:
            self.console_print_func("⚠️ No local preset selected to load. Please select one.")
            debug_log("Attempted to load local preset without selection.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        index = selected_indices[0]
        selected_preset_data = self.user_presets_data[index]
        preset_filename = selected_preset_data.get('Filename')
        display_name = selected_preset_data.get('NickName', preset_filename)

        self.console_print_func(f"Loading local preset: {display_name}...")
        debug_log(f"Loading local preset '{display_name}' (Filename: {preset_filename}).",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Update the app_instance's last selected preset name
        self.app_instance.last_selected_preset_name_var.set(display_name)

        # Attempt to load to instrument if connected
        if self.app_instance.inst:
            success, center_freq, span, rbw = load_selected_preset_logic(self.app_instance, preset_filename, self.console_print_func, is_device_preset=False, preset_data_dict=selected_preset_data)
            if success:
                self.console_print_func(f"✅ Local preset '{display_name}' loaded to instrument and GUI. Fantastic!")
                debug_log(f"Local preset '{display_name}' loaded to instrument and GUI successfully.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                self.console_print_func(f"❌ Failed to load local preset '{display_name}' to instrument. Updating GUI only.")
                debug_log(f"Failed to load local preset '{display_name}' to instrument. Updating GUI only.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                # If instrument load fails, still update GUI if data is available
                self._update_gui_from_preset_data(selected_preset_data)
        else:
            self.console_print_func("⚠️ No instrument connected. Loading local preset to GUI only.")
            debug_log("No instrument connected. Loading local preset to GUI only.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self._update_gui_from_preset_data(selected_preset_data)

        # Ensure the Instrument tab's display updates after loading
        if hasattr(self.app_instance, 'instrument_parent_tab') and \
           hasattr(self.app_instance.instrument_parent_tab, 'instrument_connection_tab') and \
           hasattr(self.app_instance.instrument_parent_tab.instrument_connection_tab, '_query_current_settings'):
            # Call query_current_settings to refresh the display, but it won't query hardware if not connected
            self.app_instance.instrument_parent_tab.instrument_connection_tab._query_current_settings()


    def _update_gui_from_preset_data(self, preset_data):
        """
        Updates the main application's Tkinter variables based on the provided preset data.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating GUI from preset data: {preset_data.get('NickName', 'Unnamed')}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        try:
            if 'Center' in preset_data:
                self.app_instance.center_freq_hz_var.set(float(preset_data['Center']))
            if 'Span' in preset_data:
                self.app_instance.span_hz_var.set(float(preset_data['Span']))
            if 'RBW' in preset_data:
                self.app_instance.rbw_hz_var.set(float(preset_data['RBW']))
            # Add other settings as needed
            # self.app_instance.reference_level_dbm_var.set(float(preset_data.get('RefLevel', self.app_instance.reference_level_dbm_var.get())))
            # self.app_instance.preamp_on_var.set(preset_data.get('Preamp', self.app_instance.preamp_on_var.get()).lower() == 'true')
            # self.app_instance.high_sensitivity_var.set(preset_data.get('HighSensitivity', self.app_instance.high_sensitivity_var.get()).lower() == 'true')

            self.console_print_func(f"✅ GUI settings updated from local preset '{preset_data.get('NickName', 'Unnamed')}'.")
            debug_log("GUI settings updated from local preset.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        except ValueError as e:
            self.console_print_func(f"❌ Error updating GUI from preset data: {e}. Data format issue!")
            debug_log(f"ValueError updating GUI from preset data: {e}. Fucking hell!",
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

