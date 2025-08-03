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
# Version 20250803.0050.0 (FIXED: populate_presets_table to only refresh Treeview from internal data.
#                         FIXED: _add_new_empty_row to use default values for Center, Span, RBW.)
# Version 20250803.0055.0 (Added window focus event to reload presets; clarified tab change save behavior.)
# Version 20250803.0100.0 (FIXED: AttributeError: '_tkinter.tkapp' object has no attribute 'root' by binding to app_instance directly.)
# Version 20250803.0115.0 (FIXED: Delete bug by adding existence check and explicit _end_edit call.
#                         FIXED: UI layout for Add buttons.
#                         CLARIFIED: Save/Load behavior on tab/window changes.)
# Version 20250803.0130.0 (CRITICAL FIX: Removed automatic CSV reload on tab select/window focus to prevent data loss.
#                         Ensured Save/Export/Delete operate on in-memory data.
#                         Added more debug logging for data consistency.)
# Version 20250803.0145.0 (FIXED: PresetEditorTab not displaying CSV content by re-introducing CSV load on tab select/window focus,
#                         with a prompt for unsaved changes. Added self.has_unsaved_changes flag.)
# Version 20250803.0200.0 (CRITICAL FIX: Removed all messagebox calls, replaced with simpledialog for confirmation where needed.
#                         CRITICAL FIX: Changed _import_presets to REPLACE existing data, not extend.
#                         Modified tab/window focus logic to auto-save unsaved changes before reloading.)
# Version 20250803.0215.0 (CRITICAL FIX: Removed all simpledialog prompts for save/delete confirmations.
#                         Auto-saves after import and delete. Console messages provide feedback.)
# Version 20250803.0230.0 (FIXED: _end_edit to ensure Treeview update.
#                         UPDATED: _add_current_settings to use query_current_instrument_settings_for_preset and populate all columns.
#                         UPDATED: Nickname and Filename format for 'Add Current Settings'.
#                         CLARIFIED: Save button message.)
# Version 20250803.0245.0 (IMPLEMENTED: Instant save on cell edit.
#                         IMPLEMENTED: Enter/Tab/Shift+Tab navigation in edit mode.
#                         REMOVED: Redundant 'Save Changes' button.
#                         MOVED: 'Delete Selected' button to top right.
#                         FIXED: AttributeError in _add_current_settings by safely accessing instrument model.)
# Version 20250803.0940.0 (FIXED: Data not saving on cell edit due to race condition with window/tab focus.
#                         Ensured _end_edit completes and saves before table repopulation on focus/tab change.
#                         Refined focus/tab change logic to prevent unnecessary saves.)
# Version 20250803.0945.0 (FIXED: Double-clicking cell causes table to go blank due to Treeview item_id invalidation.
#                         Modified _start_edit to store filename for robust data update.
#                         Modified _end_edit to update internal data first, then Treeview if item_id still valid.)
# Version 20250803.0948.0 (FIXED: CSV being cleared on double click due to save logic.
#                         Changed _end_edit to NOT trigger immediate save.
#                         Modified _on_tab_selected and _on_window_focus_in to only save if has_unsaved_changes is True.)
# Version 20250803.1000.0 (REBUILD: Cell editing logic.
#                         _end_edit now triggers immediate save to CSV.
#                         _on_edit_return, _on_edit_tab, _on_edit_shift_tab, _on_edit_escape all call _end_edit or destroy entry.
#                         Removed automatic cell navigation on Enter/Tab. Only Enter saves and exits.)
# Version 20250803.1005.0 (FIXED: "Kicking out" of edit mode due to _on_window_focus_in.
#                         Introduced self.is_editing_cell flag to suppress focus-in events during active edit.
#                         Added more debug logging for focus and edit states.)
# Version 20250803.1006.0 (FIXED: TclError: unknown option "-xyscrollcommand" by changing to xscrollcommand.)
# Version 20250803.1012.0 (ADDED: Move Preset UP/DOWN buttons and functionality.)
# Version 20250803.1018.0 (REFINED: _on_window_focus_in to prevent unnecessary table reloads and preserve selection.
#                         ADDED: Debug logging for selection state in move functions.)
# Version 20250803.1020.0 (REFINED: _on_window_focus_in to be less disruptive.
#                         ADDED: _on_tree_select method and bind to <<TreeviewSelect>> for selection debugging.
#                         ADDED: Explicit console message for save path in _save_presets_to_csv.)

current_version = "20250803.1020.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1020 * 0 # Example hash, adjust as needed.

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog # simpledialog kept only for nickname input
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
# Specific import for querying instrument settings
from tabs.Presets.utils_preset_query_and_load import query_current_instrument_settings_for_preset
from tabs.Instrument.utils_instrument_read_and_write import query_safe # For additional queries

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

        # Load presets initially from CSV. This is the primary load point.
        self.presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        debug_log(f"Initial load of presets_data in PresetEditorTab __init__: {len(self.presets_data)} entries.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.current_edit_cell = None # (item_id, col_index, filename) of the cell being edited
        self.has_unsaved_changes = False # Flag to track if data has been modified
        self.is_editing_cell = False # NEW: Flag to indicate if a cell is currently being edited

        self._create_widgets()
        self.populate_presets_table() # Initial population of Treeview from loaded data

        # Bind to the main application window's FocusIn event
        # This ensures that if the window loses and gains focus, presets are reloaded
        self.app_instance.bind("<FocusIn>", self._on_window_focus_in)


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
        # Adjusted row weights for new button placement
        self.grid_rowconfigure(0, weight=0) # Add/Delete buttons
        self.grid_rowconfigure(1, weight=0) # Move buttons (NEW)
        self.grid_rowconfigure(2, weight=1) # Treeview (shifted from row 1 to row 2)
        self.grid_rowconfigure(3, weight=0) # Scrollbar for Treeview (shifted from row 2 to row 3)
        self.grid_rowconfigure(4, weight=0) # File Ops buttons (shifted from row 3 to row 4)

        # --- Grouping for "Add" and "Delete" buttons (Moved to top) ---
        top_button_frame = ttk.Frame(self, style='Dark.TFrame')
        top_button_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        top_button_frame.grid_columnconfigure(0, weight=1)
        top_button_frame.grid_columnconfigure(1, weight=1)
        top_button_frame.grid_columnconfigure(2, weight=1) # For Delete button

        # Add Current Settings Button
        add_current_button = ttk.Button(top_button_frame, text="Add Current Settings", command=self._add_current_settings, style='Green.TButton')
        add_current_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Add New Empty Row Button
        add_empty_row_button = ttk.Button(top_button_frame, text="Add New Empty Row", command=self._add_new_empty_row, style='Blue.TButton')
        add_empty_row_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Delete Selected Button (Moved)
        delete_button = ttk.Button(top_button_frame, text="Delete Selected", command=self._delete_selected_preset, style='Red.TButton')
        delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # --- NEW: Grouping for "Move" buttons ---
        move_button_frame = ttk.Frame(self, style='Dark.TFrame')
        move_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5) # New row for move buttons
        move_button_frame.grid_columnconfigure(0, weight=1)
        move_button_frame.grid_columnconfigure(1, weight=1)

        # Move Preset UP Button
        move_up_button = ttk.Button(move_button_frame, text="Move Preset UP", command=self._move_preset_up, style='Orange.TButton')
        move_up_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Move Preset DOWN Button
        move_down_button = ttk.Button(move_button_frame, text="Move Preset DOWN", command=self._move_preset_down, style='Orange.TButton')
        move_down_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


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
        self.presets_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10) # Moved to row 2

        # Configure columns and headings
        for col in self.columns:
            self.presets_tree.heading(col, text=col, anchor=tk.W)
            self.presets_tree.column(col, width=self.column_widths.get(col, 100), anchor=tk.W, stretch=tk.NO) # Default width 100

        # Add scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.presets_tree.yview)
        vsb.grid(row=2, column=1, sticky='ns') # Moved to row 2
        self.presets_tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.presets_tree.xview)
        hsb.grid(row=3, column=0, sticky='ew') # Moved to row 3
        self.presets_tree.configure(xscrollcommand=hsb.set)

        # Bind double-click event for editing
        self.presets_tree.bind("<Double-1>", self._on_double_click)
        # NEW: Bind to TreeviewSelect event for debugging selection
        self.presets_tree.bind("<<TreeviewSelect>>", self._on_tree_select)


        # --- Button Frame for File Operations (excluding Save) ---
        file_ops_button_frame = ttk.Frame(self, style='Dark.TFrame')
        file_ops_button_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew") # Moved to row 4
        file_ops_button_frame.grid_columnconfigure(0, weight=1)
        file_ops_button_frame.grid_columnconfigure(1, weight=1)
        file_ops_button_frame.grid_columnconfigure(2, weight=1)


        # Import Button
        import_button = ttk.Button(file_ops_button_frame, text="Import Presets", command=self._import_presets, style='Orange.TButton')
        import_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Export Button
        export_button = ttk.Button(file_ops_button_frame, text="Export Presets", command=self._export_presets, style='Purple.TButton')
        export_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        debug_log("PresetEditorTab widgets created. Treeview and buttons are ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def populate_presets_table(self):
        """
        Populates the Treeview with the current data from self.presets_data.
        This function should NOT reload from CSV; it only refreshes the display.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets table from internal data...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Clear existing entries in the Treeview
        for item in self.presets_tree.get_children():
            self.presets_tree.delete(item)

        if not self.presets_data:
            self.console_print_func("ℹ️ No user presets in memory to display in editor.")
            debug_log("No user presets in memory for editor.",
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
        
        self.console_print_func(f"✅ Displayed {len(self.presets_data)} user presets in the editor.")
        debug_log(f"Local presets table populated with {len(self.presets_data)} entries from internal data.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _add_current_settings(self):
        """
        Queries current instrument settings and adds them as a new row to the Treeview
        and the internal presets_data list.
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

        # Safely get the instrument model string
        instrument_model = ""
        if hasattr(self.app_instance, 'connected_instrument_model') and \
           isinstance(self.app_instance.connected_instrument_model, tk.StringVar):
            instrument_model = self.app_instance.connected_instrument_model.get()
        debug_log(f"Instrument model for query: '{instrument_model}'.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


        # Query all current settings from the instrument
        (center_freq_mhz, span_mhz, rbw_hz_val, vbw_hz_val,
         ref_level_dbm, attenuation_db, maxhold_on, high_sensitivity_on, preamp_on,
         trace1_mode, trace2_mode, trace3_mode, trace4_mode,
         marker1_calc_max, marker2_calc_max, marker3_calc_max,
         marker4_calc_max, marker5_calc_max, marker6_calc_max) = \
            query_current_instrument_settings_for_preset(self.app_instance.inst, self.console_print_func, instrument_model)

        # Check if all critical values were successfully retrieved
        if all(x is not None for x in [center_freq_mhz, span_mhz, rbw_hz_val, vbw_hz_val,
                                       ref_level_dbm, attenuation_db, maxhold_on, high_sensitivity_on, preamp_on,
                                       trace1_mode, trace2_mode, trace3_mode, trace4_mode,
                                       marker1_calc_max, marker2_calc_max, marker3_calc_max,
                                       marker4_calc_max, marker5_calc_max, marker6_calc_max]):
            
            # Generate Filename and NickName based on current timestamp
            timestamp_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamp_nickname = datetime.now().strftime('%Y%m%d %H%M')
            
            new_preset = {
                'Filename': f"USER_{timestamp_filename}.STA",
                'NickName': f"Device {timestamp_nickname}",
                'Center': f"{center_freq_mhz:.3f}",
                'Span': f"{span_mhz:.3f}",
                'RBW': f"{rbw_hz_val:.0f}",
                'VBW': f"{vbw_hz_val:.0f}",
                'RefLevel': f"{ref_level_dbm:.1f}",
                'Attenuation': f"{attenuation_db:.0f}", # Assuming attenuation is an integer value
                'MaxHold': 'ON' if maxhold_on else 'OFF',
                'HighSens': 'ON' if high_sensitivity_on else 'OFF',
                'PreAmp': 'ON' if preamp_on else 'OFF',
                'Trace1Mode': trace1_mode,
                'Trace2Mode': trace2_mode,
                'Trace3Mode': trace3_mode,
                'Trace4Mode': trace4_mode,
                'Marker1Max': 'WRITE' if marker1_calc_max else '',
                'Marker2Max': 'WRITE' if marker2_calc_max else '',
                'Marker3Max': 'WRITE' if marker3_calc_max else '',
                'Marker4Max': 'WRITE' if marker4_calc_max else '',
                'Marker5Max': 'WRITE' if marker5_calc_max else '',
                'Marker6Max': 'WRITE' if marker6_calc_max else '',
            }

            self.presets_data.append(new_preset)
            self.populate_presets_table() # Refresh table to show new entry from internal data
            self.has_unsaved_changes = True # Mark as unsaved
            self.console_print_func("✅ Current instrument settings added as a new preset. Remember to save your changes!")
            debug_log(f"Current settings added as new preset. Current presets_data count: {len(self.presets_data)}. Unsaved changes: {self.has_unsaved_changes}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to query all current settings from instrument. Some values were missing.")
            debug_log("Failed to query all current settings. Some values were None.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _add_new_empty_row(self):
        """
        Adds a new empty row to the Treeview and the internal presets_data list.
        Initializes with default values for common settings.
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
        new_empty_preset['Center'] = "100.0" # Default Center in MHz
        new_empty_preset['Span'] = "100.0"   # Default Span in MHz
        new_empty_preset['RBW'] = "100000.0" # Default RBW in Hz
        new_empty_preset['VBW'] = "" # Keep VBW empty or set a default if desired, e.g., "30000.0"

        self.presets_data.append(new_empty_preset)
        self.populate_presets_table() # Refresh table to show new entry from internal data
        self.has_unsaved_changes = True # Mark as unsaved
        self.console_print_func("✅ New empty row added. Remember to save your changes!")
        debug_log(f"New empty row added. Current presets_data count: {len(self.presets_data)}. Unsaved changes: {self.has_unsaved_changes}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _save_presets_to_csv(self):
        """
        Saves the current state of the presets_data (from the Treeview) back to the CSV file.
        Uses overwrite_user_presets_csv from utils_preset_process.
        This function is called automatically on cell edit, tab change, and window focus.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Saving all presets to PRESETS.CSV...")
        debug_log("Saving presets to CSV.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # self.presets_data is the source of truth for saving, as _end_edit updates it.
        # Pass the column headers explicitly to overwrite_user_presets_csv to ensure consistency
        fieldnames_for_save = [col.split(' ')[0] for col in self.columns]
        
        # Get the full path for logging
        presets_csv_full_path = get_presets_csv_path(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)

        if overwrite_user_presets_csv(self.app_instance.CONFIG_FILE_PATH, self.presets_data, self.console_print_func, fieldnames=fieldnames_for_save):
            self.console_print_func(f"✅ Presets saved successfully to: {presets_csv_full_path}")
            debug_log(f"Presets saved to CSV successfully. Total entries: {len(self.presets_data)}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self.has_unsaved_changes = False # No unsaved changes after saving

            # After saving, refresh the local presets tab to reflect changes
            if hasattr(self.app_instance, 'presets_parent_tab') and \
               hasattr(self.app_instance.presets_parent_tab, 'local_presets_tab') and \
               hasattr(self.app_instance.presets_parent_tab.local_presets_tab, 'populate_local_presets_list'):
                self.app_instance.presets_parent_tab.local_presets_tab.populate_local_presets_list()
                debug_log("Refreshed Local Presets tab after saving.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            return True # Indicate success
        else:
            self.console_print_func("❌ Failed to save presets to PRESETS.CSV.")
            debug_log("Failed to save presets to CSV.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False # Indicate failure


    def _import_presets(self):
        """
        Opens a file dialog to select a CSV file and imports its contents
        into the current presets table, REPLACING existing data.
        Automatically saves changes after import.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("💬 Initiating preset import...")
        debug_log("Initiating preset import...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        file_path = filedialog.askopenfilename(
            parent=self.app_instance, # Use app_instance as parent
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
                    elif isinstance(value, (float, np.float64)): # Use np.float64 for NumPy 2.0 compatibility
                        # Check if it's an integer value represented as float (e.g., 50.0)
                        if value.is_integer():
                            preset[key] = str(int(value))
                        else:
                            preset[key] = str(value)
                    else:
                        preset[key] = str(value) # Ensure all values are strings

            # CRITICAL CHANGE: Replace existing presets_data with imported data
            self.presets_data = imported_presets
            self.populate_presets_table() # Refresh the display from updated internal data
            self.has_unsaved_changes = True # Mark as unsaved after import

            self.console_print_func(f"✅ Successfully imported {len(imported_presets)} presets from {os.path.basename(file_path)}. Existing data replaced. Automatically saving changes...")
            debug_log(f"Imported {len(imported_presets)} presets from {file_path}. Existing data replaced. Current presets_data count: {len(self.presets_data)}. Unsaved changes: {self.has_unsaved_changes}.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

            # Automatically save changes after import
            self._save_presets_to_csv()

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
        debug_log(f"Exporting presets. Current presets_data count: {len(self.presets_data)}.",
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
            parent=self.app_instance, # Use app_instance as parent
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
                        elif isinstance(value, (float, np.float64)) and value.is_integer(): # Use np.float64
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
        Automatically saves changes after deletion.
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

        # No confirmation dialog, proceed directly with deletion
        self.console_print_func("💬 Deleting selected preset(s)...")
        debug_log("Proceeding with deletion of selected presets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        deleted_count = 0
        # Iterate in reverse to avoid issues with index changes during deletion
        for item_id in reversed(selected_items):
            # Check if the item being deleted is currently being edited
            if self.current_edit_cell and self.current_edit_cell[0] == item_id:
                self._end_edit() # Gracefully end the edit before deleting the item
                debug_log(f"Ending active edit on item {item_id} before deletion.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

            # Get the values of the item to be deleted
            values = self.presets_tree.item(item_id, 'values')
            if values:
                # Assuming 'Filename' is the first column and unique identifier
                filename_to_delete = values[0]
                
                # Find and remove from self.presets_data
                initial_len = len(self.presets_data)
                self.presets_data = [p for p in self.presets_data if p.get('Filename') != filename_to_delete]
                if len(self.presets_data) < initial_len:
                    # Only increment deleted_count if an item was actually removed from the list
                    deleted_count += 1
                    debug_log(f"Removed preset with Filename: {filename_to_delete} from internal data.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                else:
                    debug_log(f"Preset with Filename: {filename_to_delete} not found in internal data for deletion.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                
                # Delete from Treeview
                self.presets_tree.delete(item_id)
                debug_log(f"Deleted item {item_id} from Treeview.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        if deleted_count > 0:
            self.has_unsaved_changes = True # Mark as unsaved
            self.console_print_func(f"✅ Deleted {deleted_count} preset(s). Automatically saving changes...")
            debug_log(f"Deleted {deleted_count} presets. Current presets_data count: {len(self.presets_data)}. Unsaved changes: {self.has_unsaved_changes}. Automatically saving.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

            # Automatically save changes after deletion
            self._save_presets_to_csv()
        else:
            self.console_print_func("ℹ️ No presets were deleted.")
            debug_log("No presets deleted.",
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
        Stores the item_id, column index, and the filename of the row being edited
        for robust saving. Sets self.is_editing_cell to True.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting edit for item_id: {item_id}, col_index: {col_index}. Setting is_editing_cell=True.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Destroy existing editor if any
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            self._end_edit()

        # Get bounding box of the cell
        x, y, width, height = self.presets_tree.bbox(item_id, f"#{col_index + 1}")

        # Get the current value of the cell
        current_values_in_tree = self.presets_tree.item(item_id, "values")
        current_value = current_values_in_tree[col_index]
        
        # CRITICAL CHANGE: Store the filename for robust lookup in presets_data
        filename_of_edited_row = current_values_in_tree[0] # Filename is always the first column

        # Create an Entry widget for editing
        self.edit_entry = ttk.Entry(self.presets_tree, style='TEntry')
        self.edit_entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()

        self.current_edit_cell = (item_id, col_index, filename_of_edited_row) # Store filename here
        self.is_editing_cell = True # Set the flag to indicate active editing

        # Bind events to the new entry widget
        self.edit_entry.bind("<FocusOut>", self._end_edit)
        self.edit_entry.bind("<Return>", self._on_edit_return)
        self.edit_entry.bind("<Escape>", self._on_edit_escape)


    def _on_edit_return(self, event):
        """
        Handles Enter key press during editing. Saves the current edit and exits the cell.
        No automatic navigation to the next cell/row.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Enter key pressed during edit. Ending edit.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self._end_edit() # This will save and destroy the current entry
        return "break" # Prevent default Tkinter behavior (like inserting newline or moving focus)

    def _on_edit_tab(self, event):
        """
        Handles Tab key press during editing. Saves the current edit and exits the cell.
        No automatic navigation to the next cell.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Tab key pressed during edit. Ending edit.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self._end_edit() # This will save and destroy the current entry
        return "break" # Prevent default Tkinter behavior (like moving focus)

    def _on_edit_shift_tab(self, event):
        """
        Handles Shift-Tab key press during editing. Saves the current edit and exits the cell.
        No automatic navigation to the previous cell.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Shift-Tab key pressed during edit. Ending edit.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self._end_edit() # This will save and destroy the current entry
        return "break" # Prevent default Tkinter behavior (like moving focus)

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
            self.is_editing_cell = False # Reset flag even on escape
        return "break" # Prevent default Tkinter behavior


    def _end_edit(self, event=None):
        """
        Commits the changes from the Entry widget back to the internal presets_data list,
        then updates the Treeview (if the item_id is still valid) and destroys the Entry widget.
        Triggers an immediate save to CSV. Resets self.is_editing_cell to False.
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
            self.is_editing_cell = False # Ensure flag is reset if no entry exists
            return

        if self.current_edit_cell:
            item_id_from_edit, col_index, filename_of_edited_row = self.current_edit_cell
            new_value = self.edit_entry.get()

            # Update the internal presets_data list first (most important)
            edited_preset = None
            for preset in self.presets_data:
                if preset.get('Filename') == filename_of_edited_row:
                    edited_preset = preset
                    # Get the original column name (without units) for the dictionary key
                    original_col_name = self.columns[col_index].split(' ')[0]
                    
                    # Only update if the value has actually changed
                    if str(preset.get(original_col_name, '')) != new_value:
                        preset[original_col_name] = new_value
                        self.console_print_func(f"✅ Updated '{original_col_name}' for '{preset.get('NickName', filename_of_edited_row)}' to '{new_value}'. Automatically saving changes!")
                        debug_log(f"Internal data updated for {filename_of_edited_row}: {original_col_name} = {new_value}. Unsaved changes: True. Triggering auto-save.",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                        self.has_unsaved_changes = True # Mark as unsaved
                        # CRITICAL CHANGE: Re-introducing immediate save here as per user's request
                        self._save_presets_to_csv()
                    else:
                        debug_log("Value unchanged. No update to internal data or unsaved changes flag.",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                    break
            
            # Now, update the Treeview item, but only if it still exists
            if self.presets_tree.exists(item_id_from_edit):
                # Get current values from the *updated* presets_data, not the Treeview directly
                # This ensures consistency if the Treeview was not updated by the edit_entry directly
                updated_values_for_treeview = []
                if edited_preset: # Use the updated dictionary if found
                    for col_key in self.columns:
                        clean_col_key = col_key.split(' ')[0]
                        value = edited_preset.get(clean_col_key, '')
                        if isinstance(value, float) and np.isnan(value):
                            value = ''
                        updated_values_for_treeview.append(value)
                else: # Fallback: if edited_preset wasn't found (shouldn't happen if filename is unique),
                      # try to get from Treeview and apply new value directly
                    try:
                        updated_values_for_treeview = list(self.presets_tree.item(item_id_from_edit, "values"))
                        updated_values_for_treeview[col_index] = new_value # Apply new value directly
                    except tk.TclError:
                        debug_log(f"Could not retrieve values from Treeview for item {item_id_from_edit}. Skipping Treeview update.",
                                    file=f"{os.path.basename(__file__)} - {current_version}",
                                    version=current_version,
                                    function=current_function)
                        updated_values_for_treeview = None # Indicate failure to get values

                if updated_values_for_treeview is not None:
                    self.presets_tree.item(item_id_from_edit, values=updated_values_for_treeview)
                    debug_log(f"Treeview item {item_id_from_edit} updated with new values: {updated_values_for_treeview}.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
            else:
                debug_log(f"Treeview item {item_id_from_edit} no longer exists. Skipping Treeview visual update.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                # The data is already saved to self.presets_data and CSV by this point.
                # The next populate_presets_table() will refresh the view correctly.

            self.current_edit_cell = None # Clear the editing state

        self.edit_entry.destroy()
        self.is_editing_cell = False # Reset the flag after destroying the entry
        debug_log("Edit ended. Entry widget destroyed. is_editing_cell set to False.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the local presets table to show the most current values.
        This now automatically saves unsaved changes before reloading from CSV.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("PresetEditorTab selected. Checking for unsaved changes before refreshing...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # First, ensure any active edit is committed (without saving to CSV yet)
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            debug_log("Active edit detected on tab selection. Ending edit before reload.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self._end_edit() # This will update internal data and set has_unsaved_changes if needed

        if self.has_unsaved_changes:
            self.console_print_func("💬 Unsaved changes detected. Attempting to auto-save before reloading presets from file.")
            debug_log("Unsaved changes detected. Attempting auto-save.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            self._save_presets_to_csv() # Attempt to save automatically

        # Always reload from CSV to ensure the latest disk version is displayed
        self.presets_data = load_user_presets_from_csv(self.app_instance.CONFIG_FILE_PATH, self.console_print_func)
        self.populate_presets_table()
        debug_log(f"PresetEditorTab refreshed from CSV. Current presets_data count: {len(self.presets_data)}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_window_focus_in(self, event):
        """
        Called when the main application window gains focus.
        Performs an auto-save if unsaved changes exist and no cell is being edited.
        Does NOT automatically reload the table to preserve selection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Main window gained focus. Checking if PresetEditorTab is active.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        # Check if this tab is currently the selected tab in the notebook
        if hasattr(self.master, 'select') and self.master.select() == str(self):
            # Only proceed if not currently in an active cell edit
            if self.is_editing_cell:
                debug_log("Window focused, but a cell is currently being edited. Skipping auto-save/reload to avoid interruption.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                return # Skip everything if an edit is active

            # If there are unsaved changes, attempt to auto-save
            if self.has_unsaved_changes:
                self.console_print_func("💬 Window focused and Preset Editor tab active. Unsaved changes detected. Attempting auto-save.")
                debug_log("Window focused and Preset Editor tab active. Unsaved changes detected. Attempting auto-save.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                self._save_presets_to_csv() # Attempt to save automatically
                # NOTE: We do NOT call populate_presets_table() here to preserve selection.
                # The _on_tab_selected will handle the refresh when the tab is explicitly selected.
            else:
                debug_log("Window focused, Preset Editor tab active, but no unsaved changes. Skipping auto-save.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
        else:
            debug_log("Window focused, but PresetEditorTab is not the active tab. Skipping auto-save.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

    def _on_tree_select(self, event):
        """
        Handles selection events on the Treeview. Logs the selected items.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_items = self.presets_tree.selection()
        if selected_items:
            # For debugging, log the filenames of selected items
            selected_filenames = [self.presets_tree.item(item, 'values')[0] for item in selected_items]
            debug_log(f"Treeview selection changed. Selected items: {selected_filenames}",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            debug_log("Treeview selection cleared (no items selected).",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _move_preset_up(self):
        """
        Moves the selected preset(s) one position up in the table and internal data.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_items = self.presets_tree.selection()
        debug_log(f"Move Preset UP clicked. Selected items: {selected_items}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not selected_items:
            self.console_print_func("⚠️ No preset selected to move up. Select one, genius!")
            debug_log("No preset selected for move up.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Ensure active edit is ended before moving
        if self.is_editing_cell:
            self._end_edit()

        # Sort selected items by their current position (topmost first)
        sorted_selected_items = sorted(selected_items, key=lambda x: self.presets_tree.index(x))

        moved_count = 0
        original_filenames_to_reselect = [] # Store filenames to re-select after repopulation

        for item_id in sorted_selected_items:
            current_index = self.presets_tree.index(item_id)
            if current_index > 0: # Can only move up if not the first item
                # Get the filename of the item to move
                filename_to_move = self.presets_tree.item(item_id, 'values')[0]
                original_filenames_to_reselect.append(filename_to_move) # Add to list for re-selection
                
                # Find the corresponding preset in self.presets_data
                preset_to_move = None
                for i, p in enumerate(self.presets_data):
                    if p.get('Filename') == filename_to_move:
                        preset_to_move = p
                        break
                
                if preset_to_move:
                    # Remove from current position and insert at new position in data list
                    self.presets_data.pop(i)
                    self.presets_data.insert(current_index - 1, preset_to_move)
                    moved_count += 1
                    debug_log(f"Moved preset '{filename_to_move}' from index {current_index} to {current_index - 1} in internal data.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                else:
                    debug_log(f"Preset with filename '{filename_to_move}' not found in internal data for move up.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
            else:
                self.console_print_func(f"⚠️ Preset '{self.presets_tree.item(item_id, 'values')[1]}' is already at the top. Cannot move up.")
                debug_log(f"Attempted to move top preset '{self.presets_tree.item(item_id, 'values')[1]}' up.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        if moved_count > 0:
            self.has_unsaved_changes = True
            self.populate_presets_table() # Refresh Treeview from updated data
            
            # Re-select the moved items based on their original filenames
            new_selection_ids = []
            for filename in original_filenames_to_reselect:
                for new_item_id in self.presets_tree.get_children():
                    if self.presets_tree.item(new_item_id, 'values')[0] == filename:
                        new_selection_ids.append(new_item_id)
                        break
            self.presets_tree.selection_set(new_selection_ids)
            if new_selection_ids: # Ensure there's something to focus
                self.presets_tree.focus(new_selection_ids[0]) # Focus the first moved item
            
            self.console_print_func(f"✅ Moved {moved_count} preset(s) up. Automatically saving changes...")
            self._save_presets_to_csv()
        else:
            self.console_print_func("ℹ️ No presets were moved up.")


    def _move_preset_down(self):
        """
        Moves the selected preset(s) one position down in the table and internal data.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_items = self.presets_tree.selection()
        debug_log(f"Move Preset DOWN clicked. Selected items: {selected_items}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not selected_items:
            self.console_print_func("⚠️ No preset selected to move down. Select one, buddy!")
            debug_log("No preset selected for move down.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return

        # Ensure active edit is ended before moving
        if self.is_editing_cell:
            self._end_edit()

        # Sort selected items by their current position (bottommost first for down movement)
        sorted_selected_items = sorted(selected_items, key=lambda x: self.presets_tree.index(x), reverse=True)

        moved_count = 0
        original_filenames_to_reselect = [] # Store filenames to re-select after repopulation

        for item_id in sorted_selected_items:
            current_index = self.presets_tree.index(item_id)
            if current_index < len(self.presets_data) - 1: # Can only move down if not the last item
                # Get the filename of the item to move
                filename_to_move = self.presets_tree.item(item_id, 'values')[0]
                original_filenames_to_reselect.append(filename_to_move) # Add to list for re-selection
                
                # Find the corresponding preset in self.presets_data
                preset_to_move = None
                for i, p in enumerate(self.presets_data):
                    if p.get('Filename') == filename_to_move:
                        preset_to_move = p
                        break
                
                if preset_to_move:
                    # Remove from current position and insert at new position in data list
                    self.presets_data.pop(i)
                    self.presets_data.insert(current_index + 1, preset_to_move)
                    moved_count += 1
                    debug_log(f"Moved preset '{filename_to_move}' from index {current_index} to {current_index + 1} in internal data.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
                else:
                    debug_log(f"Preset with filename '{filename_to_move}' not found in internal data for move down.",
                                file=f"{os.path.basename(__file__)} - {current_version}",
                                version=current_version,
                                function=current_function)
            else:
                self.console_print_func(f"⚠️ Preset '{self.presets_tree.item(item_id, 'values')[1]}' is already at the bottom. Cannot move down.")
                debug_log(f"Attempted to move bottom preset '{self.presets_tree.item(item_id, 'values')[1]}' down.",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)

        if moved_count > 0:
            self.has_unsaved_changes = True
            self.populate_presets_table() # Refresh Treeview from updated data
            
            # Re-select the moved items based on their original filenames
            new_selection_ids = []
            for filename in original_filenames_to_reselect:
                for new_item_id in self.presets_tree.get_children():
                    if self.presets_tree.item(new_item_id, 'values')[0] == filename:
                        new_selection_ids.append(new_item_id)
                        break
            self.presets_tree.selection_set(new_selection_ids)
            if new_selection_ids: # Ensure there's something to focus
                self.presets_tree.focus(new_selection_ids[0]) # Focus the first moved item
            
            self.console_print_func(f"✅ Moved {moved_count} preset(s) down. Automatically saving changes...")
            self._save_presets_to_csv()
        else:
            self.console_print_func("ℹ️ No presets were moved down.")

