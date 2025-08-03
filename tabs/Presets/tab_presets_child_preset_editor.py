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

current_version = "20250802.2215.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 2215 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
import csv
from datetime import datetime
import shutil # For file operations like copy

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import functions from the newly refactored preset utility modules
from tabs.Presets.utils_preset_process import load_user_presets_from_csv, save_user_preset_to_csv, get_presets_csv_path, overwrite_user_presets_csv

class PresetEditorTab(ttk.Frame):
    """
    A Tkinter Frame that provides comprehensive functionality for managing
    user-defined presets stored locally in a CSV file. It includes a table
    for displaying and editing presets, along with buttons for saving,
    improving, exporting, and adding new presets.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        """
        Initializes the PresetEditorTab.

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
        self.style_obj = style_obj

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing PresetEditorTab. Version: {current_version}. Let's manage and edit presets!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.presets_data = [] # Stores the loaded CSV data
        self.current_edit_cell = None # To track the currently edited cell (item, column)
        self.edit_entry = None # Reference to the Entry widget used for editing

        self._create_widgets()
        self.populate_presets_table() # Initial population

        debug_log(f"PresetEditorTab initialized. Version: {current_version}. Ready for preset editing!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Preset Editor tab.
        This includes buttons for file operations and a Treeview for displaying
        and editing the CSV data.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating PresetEditorTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Buttons row
        self.grid_rowconfigure(1, weight=1) # Treeview row

        # --- Buttons Frame ---
        button_frame = ttk.Frame(self, style='Dark.TFrame')
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=1)
        button_frame.grid_columnconfigure(5, weight=1) # For new "Add Row" button


        ttk.Button(button_frame, text="Reload Presets", command=self.populate_presets_table, style='Blue.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Save Presets", command=self._save_presets_to_csv, style='Green.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Import Presets", command=self._import_presets, style='Orange.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Export Presets", command=self._export_presets, style='Purple.TButton').grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Add Current Settings as New Preset", command=self._add_current_settings_as_new_preset, style='Green.TButton').grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Add New Empty Row", command=self._add_new_empty_row, style='Blue.TButton').grid(row=0, column=5, padx=5, pady=5, sticky="ew")


        # --- Presets Table (Treeview) ---
        table_frame = ttk.LabelFrame(self, text="Local Presets Data (PRESETS.CSV)", style='Dark.TLabelframe')
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Updated columns and order, with NickName after Filename and new Trace Modes
        # Removed SweepTime and FreqShift
        columns = ("Filename", "NickName", "Center", "Span", "RBW", "VBW", "RefLevel", "Attenuation", "MaxHold", "HighSens", "PreAmp", "Trace1Mode", "Trace2Mode", "Trace3Mode", "Trace4Mode", "Marker1Max", "Marker2Max", "Marker3Max", "Marker4Max", "Marker5Max", "Marker6Max")
        self.presets_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.presets_tree.heading(col, text=col, anchor="w")
            # Set default widths for better visibility of new columns
            if "Mode" in col or "Max" in col:
                self.presets_tree.column(col, width=80, stretch=False)
            elif col == "Filename" or col == "NickName":
                self.presets_tree.column(col, width=120, stretch=True)
            else:
                self.presets_tree.column(col, width=100, stretch=True)

        self.presets_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        tree_scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.presets_tree.yview)
        tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.presets_tree.configure(yscrollcommand=tree_scrollbar_y.set)

        tree_scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.presets_tree.xview)
        tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.presets_tree.configure(xscrollcommand=tree_scrollbar_x.set)

        # Bindings for editing
        self.presets_tree.bind("<Double-1>", self._on_double_click_edit)
        self.presets_tree.bind("<Return>", self._on_edit_return)
        self.presets_tree.bind("<Tab>", self._on_edit_tab)
        self.presets_tree.bind("<Shift-Tab>", self._on_edit_shift_tab)
        self.presets_tree.bind("<Escape>", self._on_edit_escape)

        debug_log("PresetEditorTab widgets created. Table and buttons are ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def populate_presets_table(self):
        """
        Loads presets from the PRESETS.CSV file and populates the Treeview.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets table...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Clear existing data
        for item in self.presets_tree.get_children():
            self.presets_tree.delete(item)

        self.presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        for row_data in self.presets_data:
            # Ensure all columns are present, even if empty in CSV, and in the new order
            # Removed SweepTime and FreqShift
            values = [
                row_data.get("Filename", ""),
                row_data.get("NickName", ""), # Reordered
                row_data.get("Center", ""),
                row_data.get("Span", ""),
                row_data.get("RBW", ""),
                row_data.get("VBW", ""),
                row_data.get("RefLevel", ""),
                row_data.get("Attenuation", ""),
                row_data.get("MaxHold", ""),
                row_data.get("HighSens", ""),
                row_data.get("PreAmp", ""),
                row_data.get("Trace1Mode", ""),
                row_data.get("Trace2Mode", ""),
                row_data.get("Trace3Mode", ""),
                row_data.get("Trace4Mode", ""),
                row_data.get("Marker1Max", ""),
                row_data.get("Marker2Max", ""),
                row_data.get("Marker3Max", ""),
                row_data.get("Marker4Max", ""),
                row_data.get("Marker5Max", ""),
                row_data.get("Marker6Max", ""),
            ]
            self.presets_tree.insert("", "end", values=values)
        
        self.console_print_func(f"✅ Loaded {len(self.presets_data)} local presets from CSV.")
        debug_log(f"Local presets table populated with {len(self.presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _save_presets_to_csv(self):
        """
        Saves the current data in the Treeview back to the PRESETS.CSV file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Saving current presets data to CSV...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Ensure any active editing is finalized before saving
        self._end_edit(event=None)

        # Get data from Treeview
        updated_presets = []
        for item_id in self.presets_tree.get_children():
            values = self.presets_tree.item(item_id, "values")
            # Convert tuple of values back to dictionary, matching new order and columns
            # Removed SweepTime and FreqShift
            row_data = {
                "Filename": values[0],
                "NickName": values[1],
                "Center": values[2],
                "Span": values[3],
                "RBW": values[4],
                "VBW": values[5],
                "RefLevel": values[6],
                "Attenuation": values[7],
                "MaxHold": values[8],
                "HighSens": values[9],
                "PreAmp": values[10],
                "Trace1Mode": values[11],
                "Trace2Mode": values[12],
                "Trace3Mode": values[13],
                "Trace4Mode": values[14],
                "Marker1Max": values[15],
                "Marker2Max": values[16],
                "Marker3Max": values[17],
                "Marker4Max": values[18],
                "Marker5Max": values[19],
                "Marker6Max": values[20],
            }
            updated_presets.append(row_data)

        # Overwrite the CSV file with the updated data
        overwrite_user_presets_csv(updated_presets, self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        self.console_print_func("✅ Local presets saved successfully.")
        debug_log("Local presets saved to CSV.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _import_presets(self):
        """
        Allows the user to select a CSV file to import presets from.
        The imported presets are appended to the current local presets.
        It uses a flexible column matching logic (first 4 letters).
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Initiating preset import...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV file to Import"
        )
        if file_path:
            try:
                imported_data = []
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    
                    # Define expected headers in their correct order
                    expected_headers = [
                        "Filename", "NickName", "Center", "Span", "RBW", "VBW",
                        "RefLevel", "Attenuation", "MaxHold", "HighSens", "PreAmp",
                        "Trace1Mode", "Trace2Mode", "Trace3Mode", "Trace4Mode",
                        "Marker1Max", "Marker2Max", "Marker3Max", "Marker4Max", "Marker5Max", "Marker6Max"
                    ]

                    # Create a mapping from actual CSV headers to expected headers
                    # based on the "first 4 letters" rule
                    header_map = {}
                    for csv_header in reader.fieldnames:
                        matched = False
                        for expected_header in expected_headers:
                            if csv_header[:4].lower() == expected_header[:4].lower():
                                header_map[csv_header] = expected_header
                                matched = True
                                break
                        if not matched:
                            debug_log(f"CSV header '{csv_header}' did not match any expected header by first 4 letters. It will be ignored.",
                                        file=f"{os.path.basename(__file__)} - {current_version}",
                                        version=current_version,
                                        function=current_function)

                    for row in reader:
                        processed_row = {}
                        for expected_header in expected_headers:
                            # Find the corresponding CSV header using the map, or default to empty string
                            found_value = ""
                            for csv_header, mapped_header in header_map.items():
                                if mapped_header == expected_header:
                                    found_value = row.get(csv_header, "")
                                    break
                            processed_row[expected_header] = found_value
                        
                        imported_data.append(processed_row)

                # Append imported data to current presets
                self.presets_data.extend(imported_data)
                self._save_presets_to_csv() # Save the combined data
                self.populate_presets_table() # Refresh the table display

                self.console_print_func(f"✅ Successfully imported {len(imported_data)} presets from {os.path.basename(file_path)}.")
                debug_log(f"Imported {len(imported_data)} presets from {file_path}.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Error importing presets: {e}. This is a disaster!")
                debug_log(f"Error importing presets from {file_path}: {e}. Fucking hell!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("ℹ️ Import cancelled. Fine, be that way!")
            debug_log("Preset import cancelled by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _export_presets(self):
        """
        Allows the user to select a location to export the current local presets to a CSV file.
        The filename will be in the format: exported_presets_YYYYMMDD_HHSS.csv
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Initiating preset export...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Generate the dynamic filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M") # YYYYMMDD_HHMM
        initial_filename = f"exported_presets_{timestamp}.csv"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Presets As",
            initialfile=initial_filename
        )
        if file_path:
            try:
                # Ensure any active editing is finalized before exporting
                self._end_edit(event=None)

                # Get data directly from the Treeview for export
                data_to_export = []
                for item_id in self.presets_tree.get_children():
                    values = self.presets_tree.item(item_id, "values")
                    # Removed SweepTime and FreqShift
                    data_to_export.append({
                        "Filename": values[0],
                        "NickName": values[1],
                        "Center": values[2],
                        "Span": values[3],
                        "RBW": values[4],
                        "VBW": values[5],
                        "RefLevel": values[6],
                        "Attenuation": values[7],
                        "MaxHold": values[8],
                        "HighSens": values[9],
                        "PreAmp": values[10],
                        "Trace1Mode": values[11],
                        "Trace2Mode": values[12],
                        "Trace3Mode": values[13],
                        "Trace4Mode": values[14],
                        "Marker1Max": values[15],
                        "Marker2Max": values[16],
                        "Marker3Max": values[17],
                        "Marker4Max": values[18],
                        "Marker5Max": values[19],
                        "Marker6Max": values[20],
                    })

                # Updated fieldnames to match new column order and exclusions
                fieldnames = ["Filename", "NickName", "Center", "Span", "RBW", "VBW", "RefLevel", "Attenuation", "MaxHold", "HighSens", "PreAmp", "Trace1Mode", "Trace2Mode", "Trace3Mode", "Trace4Mode", "Marker1Max", "Marker2Max", "Marker3Max", "Marker4Max", "Marker5Max", "Marker6Max"]
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_to_export)

                self.console_print_func(f"✅ Successfully exported {len(data_to_export)} presets to {os.path.basename(file_path)}.")
                debug_log(f"Exported {len(data_to_export)} presets to {file_path}.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Error exporting presets: {e}. This is a disaster!")
                debug_log(f"Error exporting presets to {file_path}: {e}. Fucking hell!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            self.console_print_func("ℹ️ Export cancelled. Fine, be that way!")
            debug_log("Preset export cancelled by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _add_current_settings_as_new_preset(self):
        """
        Prompts the user for a preset name and adds the current instrument settings
        as a new row to the local presets table.
        It then saves the updated table to the CSV file.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to add current settings as a new local preset... Let's make this happen!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # First, query the current instrument settings from the app_instance's Tkinter variables
        center_freq_hz = self.app_instance.center_freq_hz_var.get()
        span_hz = self.app_instance.span_hz_var.get()
        rbw_hz = self.app_instance.rbw_hz_var.get()
        vbw_hz = self.app_instance.vbw_hz_var.get() if hasattr(self.app_instance, 'vbw_hz_var') else ""
        # sweep_time_s = self.app_instance.sweep_time_s_var.get() if hasattr(self.app_instance, 'sweep_time_s_var') else "" # Excluded
        ref_level_dbm = self.app_instance.reference_level_dbm_var.get() if hasattr(self.app_instance, 'reference_level_dbm_var') else ""
        attenuation_db = self.app_instance.attenuation_var.get() if hasattr(self.app_instance, 'attenuation_var') else ""
        # freq_shift_hz = self.app_instance.freq_shift_var.get() if hasattr(self.app_instance, 'freq_shift_var') else "" # Excluded
        maxhold_enabled = self.app_instance.maxhold_enabled_var.get() if hasattr(self.app_instance, 'maxhold_enabled_var') else ""
        high_sensitivity_enabled = self.app_instance.high_sensitivity_var.get() if hasattr(self.app_instance, 'high_sensitivity_var') else ""
        preamp_on = self.app_instance.preamp_on_var.get() if hasattr(self.app_instance, 'preamp_on_var') else ""

        # New Trace Mode variables
        trace1_mode = self.app_instance.trace1_mode_var.get() if hasattr(self.app_instance, 'trace1_mode_var') else ""
        trace2_mode = self.app_instance.trace2_mode_var.get() if hasattr(self.app_instance, 'trace2_mode_var') else ""
        trace3_mode = self.app_instance.trace3_mode_var.get() if hasattr(self.app_instance, 'trace3_mode_var') else ""
        trace4_mode = self.app_instance.trace4_mode_var.get() if hasattr(self.app_instance, 'trace4_mode_var') else ""

        # New Marker Calculate Max variables
        marker1_max = self.app_instance.marker1_calculate_max_var.get() if hasattr(self.app_instance, 'marker1_calculate_max_var') else ""
        marker2_max = self.app_instance.marker2_calculate_max_var.get() if hasattr(self.app_instance, 'marker2_calculate_max_var') else ""
        marker3_max = self.app_instance.marker3_calculate_max_var.get() if hasattr(self.app_instance, 'marker3_calculate_max_var') else ""
        marker4_max = self.app_instance.marker4_calculate_max_var.get() if hasattr(self.app_instance, 'marker4_calculate_max_var') else ""
        marker5_max = self.app_instance.marker5_calculate_max_var.get() if hasattr(self.app_instance, 'marker5_calculate_max_var') else ""
        marker6_max = self.app_instance.marker6_calculate_max_var.get() if hasattr(self.app_instance, 'marker6_calculate_max_var') else ""

        # Check if basic settings are meaningful, otherwise prompt user
        if center_freq_hz == 0.0 and span_hz == 0.0 and rbw_hz == 0.0:
            self.console_print_func("⚠️ Current instrument settings are all zero. Please connect to an instrument and query settings first.")
            debug_log("Current instrument settings are zero. Aborting 'add current settings'.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Prompt for a nickname for the preset
        nickname = simpledialog.askstring("Add New Local Preset", "Enter a nickname for this new preset:",
                                          parent=self.app_instance)
        if nickname is None: # User cancelled
            self.console_print_func("ℹ️ New preset addition cancelled. Fine, be that way!")
            debug_log("New preset addition cancelled by user.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Generate a unique filename (e.g., based on timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"USER_{timestamp}.STA" # Use .STA extension for consistency

        new_preset_data = {
            'Filename': filename,
            'NickName': nickname, # Reordered
            'Center': f"{center_freq_hz}", # Store as string to match CSV format
            'Span': f"{span_hz}",
            'RBW': f"{rbw_hz}",
            'VBW': f"{vbw_hz}",
            'RefLevel': f"{ref_level_dbm}",
            'Attenuation': f"{attenuation_db}",
            'MaxHold': f"{maxhold_enabled}",
            'HighSens': f"{high_sensitivity_enabled}",
            'PreAmp': f"{preamp_on}",
            'Trace1Mode': f"{trace1_mode}",
            'Trace2Mode': f"{trace2_mode}",
            'Trace3Mode': f"{trace3_mode}",
            'Trace4Mode': f"{trace4_mode}",
            'Marker1Max': f"{marker1_max}",
            'Marker2Max': f"{marker2_max}",
            'Marker3Max': f"{marker3_max}",
            'Marker4Max': f"{marker4_max}",
            'Marker5Max': f"{marker5_max}",
            'Marker6Max': f"{marker6_max}",
        }

        # Add to the in-memory data and refresh the table
        self.presets_data.append(new_preset_data)
        self.populate_presets_table() # Re-populate to show the new entry

        # Save the updated data to CSV
        self._save_presets_to_csv() # This will now save the entire updated table

        self.console_print_func(f"✅ Current settings added as new local preset: '{nickname}'. Success!")
        debug_log(f"Current settings added as new local preset: '{nickname}'. BOOM!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _add_new_empty_row(self):
        """
        Adds a new empty row to the presets table with default values.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Adding a new empty row to presets table...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Define a default empty row with all expected columns
        new_empty_row = {
            "Filename": "",
            "NickName": "",
            "Center": "",
            "Span": "",
            "RBW": "",
            "VBW": "",
            "RefLevel": "",
            "Attenuation": "",
            "MaxHold": "",
            "HighSens": "",
            "PreAmp": "",
            "Trace1Mode": "",
            "Trace2Mode": "",
            "Trace3Mode": "",
            "Trace4Mode": "",
            "Marker1Max": "",
            "Marker2Max": "",
            "Marker3Max": "",
            "Marker4Max": "",
            "Marker5Max": "",
            "Marker6Max": "",
        }

        self.presets_data.append(new_empty_row)
        self.populate_presets_table() # Refresh the table display
        self._save_presets_to_csv() # Save the updated data to CSV

        self.console_print_func("✅ New empty row added to presets table. Fill it up!")
        debug_log("New empty row added and saved.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_double_click_edit(self, event):
        """
        Initiates cell editing when a cell in the Treeview is double-clicked.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Double-click detected. Attempting to edit cell...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if self.edit_entry: # If another cell is being edited, finalize it first
            self._end_edit(event=None)

        item_id = self.presets_tree.identify_row(event.y)
        column_id = self.presets_tree.identify_column(event.x)

        if not item_id or not column_id:
            debug_log("No item or column identified for editing.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Get column index (e.g., #1, #2, etc.)
        col_index = int(column_id.replace('#', '')) - 1
        
        # Get the current value of the cell
        current_value = self.presets_tree.item(item_id, "values")[col_index]

        # Get the bounding box of the cell
        x, y, width, height = self.presets_tree.bbox(item_id, column_id)

        # Create an Entry widget for editing
        self.edit_entry = ttk.Entry(self.presets_tree, style='TEntry')
        self.edit_entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()

        self.current_edit_cell = (item_id, col_index)

        # Bind events to the entry widget
        self.edit_entry.bind("<FocusOut>", self._end_edit)
        self.edit_entry.bind("<Return>", self._on_edit_return)
        self.edit_entry.bind("<Tab>", self._on_edit_tab)
        self.edit_entry.bind("<Shift-Tab>", self._on_edit_shift_tab)
        self.edit_entry.bind("<Escape>", self._on_edit_escape)

        debug_log(f"Started editing cell: Item={item_id}, Column={col_index}, Value='{current_value}'",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _end_edit(self, event):
        """
        Finalizes the cell editing process, updates the Treeview, and destroys the Entry widget.
        """
        current_function = inspect.currentframe().f_code.co_name
        if self.edit_entry and self.current_edit_cell:
            item_id, col_index = self.current_edit_cell
            new_value = self.edit_entry.get()
            
            # Destroy the entry widget
            self.edit_entry.destroy()
            self.edit_entry = None
            self.current_edit_cell = None

            # Update the Treeview cell
            current_values = list(self.presets_tree.item(item_id, "values"))
            old_value = current_values[col_index]

            if new_value != old_value:
                current_values[col_index] = new_value
                self.presets_tree.item(item_id, values=current_values)
                self.console_print_func(f"✅ Cell updated: {self.presets_tree.heading(f'#{col_index+1}')['text']} = '{new_value}'")
                debug_log(f"Cell updated: Item={item_id}, Column={col_index}, New Value='{new_value}'",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log("Cell value not changed. No update needed.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        debug_log("Edit finalized.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_edit_return(self, event):
        """
        Handles the Return key press during cell editing.
        Moves the edit focus to the cell directly below the current one.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Return key pressed during edit. Moving to next row...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.edit_entry and self.current_edit_cell:
            item_id, col_index = self.current_edit_cell
            self._end_edit(event=None) # Finalize current edit

            # Find the next item
            next_item_id = self.presets_tree.next(item_id)
            if next_item_id:
                # Trigger edit on the same column in the next row
                self.presets_tree.focus(next_item_id)
                self.presets_tree.selection_set(next_item_id)
                self._start_edit_on_cell(next_item_id, col_index)
            else:
                self.console_print_func("ℹ️ No next row to edit. End of table.")
                debug_log("End of table reached after Return key.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        # Prevent default Tkinter behavior (e.g., submitting a form if this were a form)
        return "break"

    def _on_edit_tab(self, event):
        """
        Handles the Tab key press during cell editing.
        Moves the edit focus to the next cell to the right, or to the first cell
        of the next row if at the end of the current row.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Tab key pressed during edit. Moving to next column/row...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.edit_entry and self.current_edit_cell:
            item_id, col_index = self.current_edit_cell
            self._end_edit(event=None) # Finalize current edit

            columns = self.presets_tree["columns"]
            next_col_index = col_index + 1

            if next_col_index < len(columns):
                # Move to the next column in the same row
                self.presets_tree.focus(item_id)
                self.presets_tree.selection_set(item_id)
                self._start_edit_on_cell(item_id, next_col_index)
            else:
                # Move to the first column of the next row
                next_item_id = self.presets_tree.next(item_id)
                if next_item_id:
                    self.presets_tree.focus(next_item_id)
                    self.presets_tree.selection_set(next_item_id)
                    self._start_edit_on_cell(next_item_id, 0)
                else:
                    self.console_print_func("ℹ️ No next cell to edit. End of table.")
                    debug_log("End of table reached after Tab key.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
        return "break" # Prevent default Tkinter behavior

    def _on_edit_shift_tab(self, event):
        """
        Handles the Shift+Tab key press during cell editing.
        Moves the edit focus to the previous cell to the left, or to the last cell
        of the previous row if at the beginning of the current row.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Shift+Tab key pressed during edit. Moving to previous column/row...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.edit_entry and self.current_edit_cell:
            item_id, col_index = self.current_edit_cell
            self._end_edit(event=None) # Finalize current edit

            columns = self.presets_tree["columns"]
            prev_col_index = col_index - 1

            if prev_col_index >= 0:
                # Move to the previous column in the same row
                self.presets_tree.focus(item_id)
                self.presets_tree.selection_set(item_id)
                self._start_edit_on_cell(item_id, prev_col_index)
            else:
                # Move to the last column of the previous row
                prev_item_id = self.presets_tree.prev(item_id)
                if prev_item_id:
                    self.presets_tree.focus(prev_item_id)
                    self.presets_tree.selection_set(prev_item_id)
                    self._start_edit_on_cell(prev_item_id, len(columns) - 1)
                else:
                    self.console_print_func("ℹ️ No previous cell to edit. Beginning of table.")
                    debug_log("Beginning of table reached after Shift+Tab key.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
        return "break" # Prevent default Tkinter behavior

    def _on_edit_escape(self, event):
        """
        Handles the Escape key press during cell editing.
        Discards changes and exits edit mode.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Escape key pressed during edit. Discarding changes and exiting edit mode.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
            self.current_edit_cell = None
        return "break" # Prevent default Tkinter behavior

    def _start_edit_on_cell(self, item_id, col_index):
        """Helper to start editing a specific cell."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting edit on cell: Item={item_id}, Column={col_index}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.presets_tree.focus(item_id)
        self.presets_tree.selection_set(item_id)
        
        # Get the bounding box of the cell
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

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the local presets table to show the most current values.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Preset Editor Tab selected. Refreshing table... Let's get this updated!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        self.populate_presets_table()