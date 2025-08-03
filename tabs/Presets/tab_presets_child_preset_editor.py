# tabs/Presets/tab_presets_child_preset_editor.py
#
# This file defines the PresetEditorTab, a Tkinter Frame that provides
# comprehensive functionality for managing user-defined presets stored locally
# in a CSV file. It allows displaying, editing (cell-by-cell), saving, importing,
# exporting, and adding new presets (including current instrument settings).
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
# Version 20250802.1900.0 (Added Trace Mode columns and reordered NickName column.)
# Version 20250802.2215.0 (Implemented flexible column matching for import, new export filename,
#                         added 'Add New Empty Row' button, excluded SweepTime and FreqShift.)
# Version 20250802.2225.0 (Handled 'nan' values, refined UI grouping for buttons.)
# Version 20250802.2230.0 (Added debug logging to _export_presets for header/blank file issue.)
# Version 20250803.0030.0 (Updated Treeview column headers to include units for Center, Span, RBW, VBW.)

current_version = "20250803.0030.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 30 * 0 # Example hash, adjust as needed.

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime
import shutil # For file operations like copy
import pandas as pd # For CSV import/export with flexible column handling
import numpy as np # For handling NaN values

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import functions from preset utility modules
from tabs.Presets.utils_preset_process import (
    get_presets_csv_path,
    load_user_presets_from_csv,
    overwrite_user_presets_csv # NEW: For saving changes back to CSV
)
from tabs.Instrument.instrument_logic import query_current_settings_logic # For 'Add Current Settings'
from src.style import COLOR_PALETTE # For styling

class PresetEditorTab(ttk.Frame):
    """
    A Tkinter Frame that provides comprehensive functionality for managing
    user-defined presets stored locally in a CSV file. It allows displaying,
    editing (cell-by-cell), saving, importing, exporting, and adding new presets
    (including current instrument settings).
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        """
        Initializes the PresetEditorTab.

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
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing PresetEditorTab. Version: {current_version}. Get ready to edit presets!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.presets_data = [] # List of dictionaries to hold preset data
        self.current_edit_cell = None # (item_id, col_index) of the cell being edited

        self._create_widgets()
        self.populate_presets_table() # Initial population

        debug_log(f"PresetEditorTab initialized. Version: {current_version}. Preset editor is live!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Preset Editor tab.
        Includes the Treeview for displaying presets, and buttons for actions.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating PresetEditorTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Treeview
        self.grid_rowconfigure(1, weight=0) # Buttons

        # --- Treeview for Presets ---
        # Define columns with units
        self.columns = [
            'Filename', 'NickName', 'Center (MHz)', 'Span (MHz)', 'RBW (Hz)', 'VBW (Hz)',
            'RefLevel', 'Attenuation', 'MaxHold', 'HighSens', 'PreAmp',
            'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
            'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
            'Marker5Max', 'Marker6Max'
        ]
        self.column_widths = {
            'Filename': 120, 'NickName': 120, 'Center (MHz)': 100, 'Span (MHz)': 100, 'RBW (Hz)': 80, 'VBW (Hz)': 80,
            'RefLevel': 80, 'Attenuation': 90, 'MaxHold': 80, 'HighSens': 80, 'PreAmp': 80,
            'Trace1Mode': 90, 'Trace2Mode': 90, 'Trace3Mode': 90, 'Trace4Mode': 90,
            'Marker1Max': 90, 'Marker2Max': 90, 'Marker3Max': 90, 'Marker4Max': 90,
            'Marker5Max': 90, 'Marker6Max': 90
        }

        self.presets_tree = ttk.Treeview(self, columns=self.columns, show='headings', style='Treeview')
        self.presets_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure columns and headings
        for col in self.columns:
            self.presets_tree.heading(col, text=col, anchor=tk.W)
            self.presets_tree.column(col, width=self.column_widths.get(col, 100), anchor=tk.W, stretch=tk.NO) # Default width 100

        # Add scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.presets_tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.presets_tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.presets_tree.xview)
        hsb.grid(row=1, column=0, sticky='ew')
        self.presets_tree.configure(xscrollcommand=hsb.set)

        # Bind double-click event for editing
        self.presets_tree.bind("<Double-1>", self._on_double_click)

        # --- Button Frame ---
        button_frame = ttk.Frame(self, style='Dark.TFrame')
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1) # Allow buttons to spread out
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=1)
        button_frame.grid_columnconfigure(5, weight=1)


        # Grouping for "Add" buttons
        add_button_frame = ttk.Frame(button_frame, style='Dark.TFrame')
        add_button_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        add_button_frame.grid_columnconfigure(0, weight=1)
        add_button_frame.grid_columnconfigure(1, weight=1)

        # Add Current Settings Button
        add_current_button = ttk.Button(add_button_frame, text="Add Current Settings", command=self._add_current_settings, style='Green.TButton')
        add_current_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Add New Empty Row Button
        add_empty_row_button = ttk.Button(add_button_frame, text="Add New Empty Row", command=self._add_new_empty_row, style='Blue.TButton')
        add_empty_row_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # Grouping for "File Operations" buttons
        file_ops_button_frame = ttk.Frame(button_frame, style='Dark.TFrame')
        file_ops_button_frame.grid(row=0, column=2, columnspan=4, sticky="ew", padx=5, pady=5)
        file_ops_button_frame.grid_columnconfigure(0, weight=1)
        file_ops_button_frame.grid_columnconfigure(1, weight=1)
        file_ops_button_frame.grid_columnconfigure(2, weight=1)
        file_ops_button_frame.grid_columnconfigure(3, weight=1)


        # Save Button
        save_button = ttk.Button(file_ops_button_frame, text="Save Changes", command=self._save_presets_to_csv, style='Green.TButton')
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Import Button
        import_button = ttk.Button(file_ops_button_frame, text="Import Presets", command=self._import_presets, style='Orange.TButton')
        import_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Export Button
        export_button = ttk.Button(file_ops_button_frame, text="Export Presets", command=self._export_presets, style='Purple.TButton')
        export_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Delete Selected Button
        delete_button = ttk.Button(file_ops_button_frame, text="Delete Selected", command=self._delete_selected_preset, style='Red.TButton')
        delete_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")


        debug_log("PresetEditorTab widgets created. Treeview and buttons are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def populate_presets_table(self):
        """
        Loads user presets from the CSV file and populates the Treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets table...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Clear existing entries
        for item in self.presets_tree.get_children():
            self.presets_tree.delete(item)

        self.presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        if not self.presets_data:
            self.console_print_func("ℹ️ No user presets found in PRESETS.CSV to display in editor.")
            debug_log("No user presets found for editor.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        for preset in self.presets_data:
            # Prepare values for insertion, ensuring all columns are present and handling NaN/None
            row_values = []
            for col_key in self.columns:
                # Remove units from column key for dictionary lookup
                clean_col_key = col_key.split(' ')[0] # e.g., "Center (MHz)" -> "Center"
                value = preset.get(clean_col_key, '')
                
                # Handle NaN values explicitly, convert to empty string for display
                if isinstance(value, float) and np.isnan(value):
                    value = ''
                
                row_values.append(value)
            
            self.presets_tree.insert('', 'end', values=row_values)
        
        self.console_print_func(f"✅ Loaded {len(self.presets_data)} user presets into the editor.")
        debug_log(f"Local presets table populated with {len(self.presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _add_current_settings(self):
        """
        Queries current instrument settings and adds them as a new row to the Treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Adding current instrument settings to presets...")
        debug_log("Attempting to add current settings.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot get current settings. Connect first!")
            debug_log("No instrument connected to get current settings.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Query current settings using the instrument_logic function
        # This function updates the app_instance's Tkinter variables
        success = query_current_settings_logic(
            self.app_instance.inst,
            self.app_instance.center_freq_hz_var,
            self.app_instance.span_hz_var,
            self.app_instance.rbw_hz_var,
            self.app_instance.vbw_hz_var,
            self.app_instance.reference_level_dbm_var,
            self.app_instance.attenuation_var,
            self.app_instance.maxhold_enabled_var,
            self.app_instance.high_sensitivity_var,
            self.app_instance.preamp_on_var,
            self.app_instance.trace1_mode_var,
            self.app_instance.trace2_mode_var,
            self.app_instance.trace3_mode_var,
            self.app_instance.trace4_mode_var,
            self.app_instance.marker1_calculate_max_var,
            self.app_instance.marker2_calculate_max_var,
            self.app_instance.marker3_calculate_max_var,
            self.app_instance.marker4_calculate_max_var,
            self.app_instance.marker5_calculate_max_var,
            self.app_instance.marker6_calculate_max_var,
            self.app_instance.connected_instrument_model, # Pass the model var
            self.console_print_func
        )

        if success:
            # Create a new preset dictionary from current GUI values
            new_preset = {
                'Filename': f"USER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.STA",
                'NickName': simpledialog.askstring("Nickname", "Enter a nickname for this preset:",
                                                  parent=self.app_instance.root),
                'Center': f"{self.app_instance.center_freq_hz_var.get() / self.app_instance.MHZ_TO_HZ:.3f}", # Convert Hz to MHz for CSV
                'Span': f"{self.app_instance.span_hz_var.get() / self.app_instance.MHZ_TO_HZ:.3f}",         # Convert Hz to MHz for CSV
                'RBW': f"{self.app_instance.rbw_hz_var.get():.0f}",
                'VBW': f"{self.app_instance.vbw_hz_var.get():.0f}",
                'RefLevel': f"{self.app_instance.reference_level_dbm_var.get():.1f}",
                'Attenuation': f"{self.app_instance.attenuation_var.get()}",
                'MaxHold': 'ON' if self.app_instance.maxhold_enabled_var.get() else 'OFF',
                'HighSens': 'ON' if self.app_instance.high_sensitivity_var.get() else 'OFF',
                'PreAmp': 'ON' if self.app_instance.preamp_on_var.get() else 'OFF',
                'Trace1Mode': self.app_instance.trace1_mode_var.get(),
                'Trace2Mode': self.app_instance.trace2_mode_var.get(),
                'Trace3Mode': self.app_instance.trace3_mode_var.get(),
                'Trace4Mode': self.app_instance.trace4_mode_var.get(),
                'Marker1Max': 'WRITE' if self.app_instance.marker1_calculate_max_var.get() else '',
                'Marker2Max': 'WRITE' if self.app_instance.marker2_calculate_max_var.get() else '',
                'Marker3Max': 'WRITE' if self.app_instance.marker3_calculate_max_var.get() else '',
                'Marker4Max': 'WRITE' if self.app_instance.marker4_calculate_max_var.get() else '',
                'Marker5Max': 'WRITE' if self.app_instance.marker5_calculate_max_var.get() else '',
                'Marker6Max': 'WRITE' if self.app_instance.marker6_calculate_max_var.get() else '',
            }
            if new_preset['NickName'] is None: # User cancelled nickname input
                self.console_print_func("ℹ️ Adding current settings cancelled by user.")
                debug_log("Adding current settings cancelled (nickname input).",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return

            self.presets_data.append(new_preset)
            self.populate_presets_table() # Refresh table to show new entry
            self.console_print_func("✅ Current settings added as a new preset.")
            debug_log("Current settings added as new preset.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to query current settings from instrument.")
            debug_log("Failed to query current settings.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _add_new_empty_row(self):
        """
        Adds a new empty row to the Treeview and the internal presets_data list.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Adding a new empty row to the presets table...")
        debug_log("Adding new empty row.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        new_empty_preset = {col.split(' ')[0]: '' for col in self.columns} # Initialize with empty strings
        new_empty_preset['Filename'] = f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}.STA"
        new_empty_preset['NickName'] = "New Preset" # Default nickname

        self.presets_data.append(new_empty_preset)
        self.populate_presets_table() # Refresh table to show new entry
        self.console_print_func("✅ New empty row added. Remember to save your changes!")
        debug_log("New empty row added.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _save_presets_to_csv(self):
        """
        Saves the current state of the presets_data (from the Treeview) back to the CSV file.
        Uses overwrite_user_presets_csv from utils_preset_process.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Saving all presets to PRESETS.CSV...")
        debug_log("Saving presets to CSV.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Ensure that self.presets_data reflects the current Treeview content
        # This is crucial if edits were made directly in the Treeview via the entry widget
        # but not yet committed back to self.presets_data.
        # For this implementation, edits are committed to self.presets_data in _end_edit.
        # So, we can directly use self.presets_data.

        if overwrite_user_presets_csv(self.app_instance.CONFIG_FILE_PATH, self.presets_data, self.console_print_func):
            self.console_print_func("✅ Presets saved successfully to PRESETS.CSV.")
            debug_log("Presets saved to CSV successfully.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            # After saving, refresh the local presets tab to reflect changes
            if hasattr(self.app_instance, 'presets_parent_tab') and \
               hasattr(self.app_instance.presets_parent_tab, 'local_presets_tab') and \
               hasattr(self.app_instance.presets_parent_tab.local_presets_tab, 'populate_local_presets_list'):
                self.app_instance.presets_parent_tab.local_presets_tab.populate_local_presets_list()
                debug_log("Refreshed Local Presets tab after saving.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("❌ Failed to save presets to PRESETS.CSV.")
            debug_log("Failed to save presets to CSV.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _import_presets(self):
        """
        Opens a file dialog to select a CSV file and imports its contents
        into the current presets table, merging with existing data.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Initiating preset import...")
        debug_log("Initiating preset import...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        file_path = filedialog.askopenfilename(
            parent=self.app_instance.root,
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            self.console_print_func("ℹ️ Preset import cancelled.")
            debug_log("Preset import cancelled.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        try:
            # Use pandas to read CSV, handling missing columns gracefully
            df_imported = pd.read_csv(file_path)
            imported_presets = df_imported.to_dict(orient='records')

            # Clean up NaN values and convert to strings
            for preset in imported_presets:
                for key, value in preset.items():
                    if pd.isna(value):
                        preset[key] = '' # Replace NaN with empty string
                    elif isinstance(value, (float, np.float_)): # Convert floats to string, but keep original if not NaN
                        # Check if it's an integer value represented as float (e.g., 50.0)
                        if value.is_integer():
                            preset[key] = str(int(value))
                        else:
                            preset[key] = str(value)
                    else:
                        preset[key] = str(value) # Ensure all values are strings

            # Merge imported presets with existing ones (simple append for now, can add more complex merge logic if needed)
            self.presets_data.extend(imported_presets)
            self.populate_presets_table() # Refresh the display

            self.console_print_func(f"✅ Successfully imported {len(imported_presets)} presets from {os.path.basename(file_path)}.")
            debug_log(f"Imported {len(imported_presets)} presets from {file_path}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

            # Prompt to save changes
            if simpledialog.askstring("Save Changes", "Imported presets. Do you want to save these changes to your main PRESETS.CSV now? (yes/no)",
                                      parent=self.app_instance.root).lower() == 'yes':
                self._save_presets_to_csv()
            else:
                self.console_print_func("ℹ️ Imported presets not saved to main PRESETS.CSV. They are only in memory.")
                debug_log("Imported presets not saved to main CSV.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ Error importing presets: {e}. Check file format.")
            debug_log(f"Error importing presets from {file_path}: {e}. This is a disaster!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _export_presets(self):
        """
        Exports the current presets data from the Treeview to a new CSV file,
        including all columns.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Exporting presets to CSV...")
        debug_log("Exporting presets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not self.presets_data:
            self.console_print_func("⚠️ No presets to export. Add some first!")
            debug_log("No presets to export.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        default_filename = f"exported_presets_{timestamp}.csv"

        file_path = filedialog.asksaveasfilename(
            parent=self.app_instance.root,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if not file_path:
            self.console_print_func("ℹ️ Preset export cancelled.")
            debug_log("Preset export cancelled.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        try:
            # Use the defined columns as fieldnames to ensure correct order and all columns
            fieldnames = [col.split(' ')[0] for col in self.columns] # Remove units for actual CSV header

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                debug_log("Export - Header written successfully. Attempting to write rows...",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                for preset in self.presets_data:
                    # Create a dictionary with only the keys that match the fieldnames
                    # and ensure values are converted to strings, handling NaN
                    row_to_write = {}
                    for field in fieldnames:
                        value = preset.get(field, '')
                        if isinstance(value, float) and np.isnan(value):
                            row_to_write[field] = '' # Replace NaN with empty string
                        elif isinstance(value, (float, np.float_)) and value.is_integer():
                            row_to_write[field] = str(int(value))
                        else:
                            row_to_write[field] = str(value) # Ensure all values are strings
                    writer.writerow(row_to_write)
                debug_log("Export - Rows written successfully.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

            self.console_print_func(f"✅ Successfully exported {len(self.presets_data)} presets to {os.path.basename(file_path)}.")
            debug_log(f"Exported {len(self.presets_data)} presets to {file_path}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        except Exception as e:
            self.console_print_func(f"❌ Error exporting presets: {e}. This is a disaster!")
            debug_log(f"Error exporting presets to {file_path}: {e}. Fucking hell!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _delete_selected_preset(self):
        """
        Deletes the selected preset(s) from the Treeview and the internal data list.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_items = self.presets_tree.selection()
        if not selected_items:
            self.console_print_func("⚠️ No preset selected for deletion. Pick one, genius!")
            debug_log("No preset selected for deletion.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        if not simpledialog.askstring("Confirm Deletion", "Are you sure you want to delete the selected preset(s)? Type 'yes' to confirm.",
                                      parent=self.app_instance.root).lower() == 'yes':
            self.console_print_func("ℹ️ Deletion cancelled.")
            debug_log("Deletion cancelled by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        deleted_count = 0
        # Iterate in reverse to avoid issues with index changes during deletion
        for item_id in reversed(selected_items):
            # Get the values of the item to be deleted
            values = self.presets_tree.item(item_id, 'values')
            if values:
                # Assuming 'Filename' is the first column and unique identifier
                filename_to_delete = values[0]
                
                # Find and remove from self.presets_data
                self.presets_data = [p for p in self.presets_data if p.get('Filename') != filename_to_delete]
                
                # Delete from Treeview
                self.presets_tree.delete(item_id)
                deleted_count += 1
                debug_log(f"Deleted preset with Filename: {filename_to_delete}.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        self.console_print_func(f"✅ Deleted {deleted_count} preset(s). Remember to save your changes!")
        debug_log(f"Deleted {deleted_count} presets. Prompting to save.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Prompt to save changes after deletion
        if simpledialog.askstring("Save Changes", "Changes made. Do you want to save these changes to your main PRESETS.CSV now? (yes/no)",
                                  parent=self.app_instance.root).lower() == 'yes':
            self._save_presets_to_csv()
        else:
            self.console_print_func("ℹ️ Deleted presets not saved to main PRESETS.CSV. They are only in memory.")
            debug_log("Deleted presets not saved to main CSV.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _on_double_click(self, event):
        """
        Handles double-click events on the Treeview to enable cell editing.
        """
        current_function = inspect.currentframe().f_code.co_name
        region = self.presets_tree.identify("region", event.x, event.y)

        if region == "heading":
            debug_log("Double-clicked on heading. Skipping edit.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return # Do not edit headings

        if region == "cell":
            col = self.presets_tree.identify_column(event.x)
            item = self.presets_tree.identify_row(event.y)

            if not item:
                debug_log("Double-clicked on empty row. Skipping edit.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return # Do not edit empty rows

            col_index = int(col.replace('#', '')) - 1 # Column index (0-based)
            column_name = self.columns[col_index]

            # Prevent editing of 'Filename' column
            if column_name == 'Filename':
                self.console_print_func("⚠️ Filename column cannot be edited directly.")
                debug_log("Attempted to edit 'Filename' column, which is disallowed.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return

            self._start_edit(item, col_index)
        else:
            debug_log(f"Double-clicked on region: {region}. Skipping edit.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _start_edit(self, item_id, col_index):
        """
        Creates an Entry widget to allow inline editing of a Treeview cell.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting edit for item_id: {item_id}, col_index: {col_index}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Destroy existing editor if any
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            self._end_edit()

        # Get bounding box of the cell
        x, y, width, height = self.presets_tree.bbox(item_id, f"#{col_index + 1}")

        # Get the current value of the cell
        current_value = self.presets_tree.item(item_id, "values")[col_index]

        # Create an Entry widget for editing
        self.edit_entry = ttk.Entry(self.presets_tree, style='TEntry')
        self.edit_entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()

        self.current_edit_cell = (item_id, col_index)

        # Re-bind events to the new entry widget
        self.edit_entry.bind("<FocusOut>", self._end_edit)
        self.edit_entry.bind("<Return>", self._on_edit_return)
        self.edit_entry.bind("<Tab>", self._on_edit_tab)
        self.edit_entry.bind("<Shift-Tab>", self._on_edit_shift_tab)
        self.edit_entry.bind("<Escape>", self._on_edit_escape)

    def _on_edit_return(self, event):
        """Handles Enter key press during editing."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Enter key pressed during edit. Ending edit.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self._end_edit()
        # Prevent default Tkinter behavior (e.g., moving focus)
        return "break"

    def _on_edit_tab(self, event):
        """Handles Tab key press during editing to move to the next editable cell."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Tab key pressed during edit. Moving to next cell.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self._end_edit() # Commit current edit

        item_id, col_index = self.current_edit_cell
        next_col_index = col_index + 1
        
        # Find the next editable column
        while next_col_index < len(self.columns) and self.columns[next_col_index] == 'Filename':
            next_col_index += 1

        if next_col_index < len(self.columns):
            self._start_edit(item_id, next_col_index)
        else:
            # If at the end of the row, move to the first editable column of the next row
            next_item_id = self.presets_tree.next(item_id)
            if next_item_id:
                first_editable_col_index = 0
                while first_editable_col_index < len(self.columns) and self.columns[first_editable_col_index] == 'Filename':
                    first_editable_col_index += 1
                self._start_edit(next_item_id, first_editable_col_index)
            else:
                self.console_print_func("ℹ️ Reached end of table. No more cells to tab to.")
                debug_log("Reached end of table via Tab key.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        return "break" # Prevent default Tkinter behavior

    def _on_edit_shift_tab(self, event):
        """Handles Shift-Tab key press during editing to move to the previous editable cell."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Shift-Tab key pressed during edit. Moving to previous cell.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self._end_edit() # Commit current edit

        item_id, col_index = self.current_edit_cell
        prev_col_index = col_index - 1

        # Find the previous editable column
        while prev_col_index >= 0 and self.columns[prev_col_index] == 'Filename':
            prev_col_index -= 1

        if prev_col_index >= 0:
            self._start_edit(item_id, prev_col_index)
        else:
            # If at the beginning of the row, move to the last editable column of the previous row
            prev_item_id = self.presets_tree.prev(item_id)
            if prev_item_id:
                last_editable_col_index = len(self.columns) - 1
                while last_editable_col_index >= 0 and self.columns[last_editable_col_index] == 'Filename':
                    last_editable_col_index -= 1
                self._start_edit(prev_item_id, last_editable_col_index)
            else:
                self.console_print_func("ℹ️ Reached beginning of table. No more cells to shift-tab to.")
                debug_log("Reached beginning of table via Shift-Tab key.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        return "break" # Prevent default Tkinter behavior

    def _on_edit_escape(self, event):
        """Handles Escape key press during editing to cancel the edit."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Escape key pressed during edit. Cancelling edit.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # Just destroy the entry without saving changes
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            self.edit_entry.destroy()
            self.current_edit_cell = None
        return "break" # Prevent default Tkinter behavior


    def _end_edit(self, event=None):
        """
        Commits the changes from the Entry widget back to the Treeview and
        the internal presets_data list, then destroys the Entry widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Ending edit...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not hasattr(self, 'edit_entry') or not self.edit_entry.winfo_exists():
            debug_log("No active edit entry found. Skipping _end_edit.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        if self.current_edit_cell:
            item_id, col_index = self.current_edit_cell
            new_value = self.edit_entry.get()

            # Get current values of the row
            current_values = list(self.presets_tree.item(item_id, "values"))
            
            # Update the specific column's value
            current_values[col_index] = new_value
            self.presets_tree.item(item_id, values=current_values)

            # Update the internal presets_data list
            # Find the corresponding preset dictionary using Filename (first column)
            filename = current_values[0] # Filename is always the first column
            
            # Get the original column name (without units) for the dictionary key
            original_col_name = self.columns[col_index].split(' ')[0]

            for preset in self.presets_data:
                if preset.get('Filename') == filename:
                    preset[original_col_name] = new_value
                    self.console_print_func(f"✅ Updated '{original_col_name}' for '{preset.get('NickName', filename)}' to '{new_value}'. Remember to save!")
                    debug_log(f"Internal data updated for {filename}: {original_col_name} = {new_value}.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                    break
            
            self.current_edit_cell = None # Clear the editing state

        self.edit_entry.destroy()
        debug_log("Edit ended. Entry widget destroyed.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the local presets table to show the most current values.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("PresetEditorTab selected. Refreshing table... Let's get this updated!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self.populate_presets_table()
