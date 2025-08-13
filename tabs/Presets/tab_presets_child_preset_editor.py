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
#
# Version 20250814.162500.1 (REBUILT: Refactored the GUI to use the new PresetEditorLogic class, decoupling presentation from data management.)

current_version = "20250814.162500.1"
current_version_hash = 20250814 * 162500 * 1

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import inspect
import os
from datetime import datetime
import pandas as pd
import numpy as np

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import the new utility file
from tabs.Presets.utils_presets_editor import PresetEditorLogic

from tabs.Instrument.instrument_logic import query_current_settings_logic
from src.program_style import COLOR_PALETTE


class PresetEditorTab(ttk.Frame):
    """
    A Tkinter Frame that provides comprehensive functionality for managing
    user-defined presets stored locally in a CSV file. It allows displaying,
    editing (cell-by-cell), saving, importing, exporting, and adding new presets
    (including current instrument settings).
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log
        self.style_obj = style_obj

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing PresetEditorTab. Version: {current_version}. Get ready to edit presets!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.columns = [
            'Filename', 'NickName', 'Start (MHz)', 'Stop (MHz)', 'Center (MHz)', 'Span (MHz)', 'RBW (Hz)', 'VBW (Hz)',
            'RefLevel (dBm)', 'Attenuation (dB)', 'MaxHold', 'HighSens', 'PreAmp',
            'Trace1Mode', 'Trace2Mode', 'Trace3Mode', 'Trace4Mode',
            'Marker1Max', 'Marker2Max', 'Marker3Max', 'Marker4Max',
            'Marker5Max', 'Marker6Max'
        ]
        self.column_widths = {'Filename': 120, 'NickName': 120, 'Start (MHz)': 100, 'Stop (MHz)': 100, 'Center (MHz)': 100, 'Span (MHz)': 100, 'RBW (Hz)': 80, 'VBW (Hz)': 80,
            'RefLevel (dBm)': 80, 'Attenuation (dB)': 90, 'MaxHold': 80, 'HighSens': 80, 'PreAmp': 80,
            'Trace1Mode': 90, 'Trace2Mode': 90, 'Trace3Mode': 90, 'Trace4Mode': 90,
            'Marker1Max': 90, 'Marker2Max': 90, 'Marker3Max': 90, 'Marker4Max': 90,
            'Marker5Max': 90, 'Marker6Max': 90
        }

        # NEW: Instantiate the logic class
        self.logic = PresetEditorLogic(self.app_instance, self.console_print_func, self.columns)
        self.logic.load_presets()

        self.current_edit_cell = None
        self.is_editing_cell = False

        self._create_widgets()
        self.populate_presets_table()
        
        # Bind to main app window focus-in event for refresh when app gains focus
        self.app_instance.bind("<FocusIn>", self._on_window_focus_in)

        debug_log(f"PresetEditorTab initialized. Version: {current_version}. Preset editor is live!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _on_window_focus_in(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Main window gained focus. Refreshing presets. 🔄", file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)
        if self.master.winfo_exists() and self.master.select() == str(self):
            self.logic.load_presets()
            self.populate_presets_table()

    def _create_widgets(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Creating PresetEditorTab widgets...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)

        top_button_frame = ttk.Frame(self, style='Dark.TFrame')
        top_button_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        top_button_frame.grid_columnconfigure(0, weight=1)
        top_button_frame.grid_columnconfigure(1, weight=1)
        top_button_frame.grid_columnconfigure(2, weight=1)

        add_current_button = ttk.Button(top_button_frame, text="Add Current Settings", command=self._add_current_settings, style='Green.TButton')
        add_current_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        add_empty_row_button = ttk.Button(top_button_frame, text="Add New Empty Row", command=self._add_new_empty_row, style='Blue.TButton')
        add_empty_row_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        delete_button = ttk.Button(top_button_frame, text="Delete Selected", command=self._delete_selected_preset, style='Red.TButton')
        delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        move_button_frame = ttk.Frame(self, style='Dark.TFrame')
        move_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        move_button_frame.grid_columnconfigure(0, weight=1)
        move_button_frame.grid_columnconfigure(1, weight=1)

        move_up_button = ttk.Button(move_button_frame, text="Move Preset UP (CTRL+UP)", command=self._move_preset_up, style='Orange.TButton')
        move_up_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        move_down_button = ttk.Button(move_button_frame, text="Move Preset DOWN (CTRL+DOWN)", command=self._move_preset_down, style='Orange.TButton')
        move_down_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.presets_tree = ttk.Treeview(self, columns=self.columns, show='headings', style='Treeview')
        self.presets_tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        for col in self.columns:
            self.presets_tree.heading(col, text=col, anchor=tk.W)
            self.presets_tree.column(col, width=self.column_widths.get(col, 100), anchor=tk.W, stretch=tk.NO)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.presets_tree.yview)
        vsb.grid(row=2, column=1, sticky='ns')
        self.presets_tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.presets_tree.xview)
        hsb.grid(row=3, column=0, sticky='ew')
        self.presets_tree.configure(xscrollcommand=hsb.set)

        self.presets_tree.bind("<Double-1>", self._on_double_click)
        self.presets_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.presets_tree.bind("<Control-Up>", lambda event: self._move_preset_up())
        self.presets_tree.bind("<Control-Down>", lambda event: self._move_preset_down())

        file_ops_button_frame = ttk.Frame(self, style='Dark.TFrame')
        file_ops_button_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        file_ops_button_frame.grid_columnconfigure(0, weight=1)
        file_ops_button_frame.grid_columnconfigure(1, weight=1)
        file_ops_button_frame.grid_columnconfigure(2, weight=1)

        import_button = ttk.Button(file_ops_button_frame, text="Import Presets", command=self._import_presets, style='Orange.TButton')
        import_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        export_button = ttk.Button(file_ops_button_frame, text="Export Presets", command=self._export_presets, style='Purple.TButton')
        export_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        debug_log("PresetEditorTab widgets created. Treeview and buttons are ready for action!",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

    def populate_presets_table(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Populating local presets table from internal data...",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

        for item in self.presets_tree.get_children():
            self.presets_tree.delete(item)

        if not self.logic.presets_data:
            self.console_print_func("ℹ️ No user presets in memory to display in editor.")
            return

        for preset in self.logic.presets_data:
            row_values = []
            for col_key in self.columns:
                clean_col_key = col_key.split(' ')[0]
                value = preset.get(clean_col_key, '')
                
                if isinstance(value, float) and np.isnan(value):
                    value = ''
                
                row_values.append(value)
            
            self.presets_tree.insert('', 'end', values=row_values)
        
        self.console_print_func(f"✅ Displayed {len(self.logic.presets_data)} user presets in the editor.")
        debug_log(f"Local presets table populated with {len(self.logic.presets_data)} entries from internal data.",
                    file=f"{os.path.basename(__file__)}",
                    version=current_version,
                    function=current_function)

    def _add_current_settings(self):
        if self.logic.add_current_settings():
            self.populate_presets_table()
            self.logic.save_presets()

    def _add_new_empty_row(self):
        if self.logic.add_new_empty_row():
            self.populate_presets_table()
            self.logic.save_presets()

    def _save_presets_to_csv(self):
        if self.logic.save_presets():
            self.console_print_func(f"✅ Presets saved successfully to: {self.app_instance.PRESETS_FILE_PATH}")

    def _import_presets(self):
        file_path = filedialog.askopenfilename(
            parent=self.app_instance,
            title="Select CSV file to import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path and self.logic.import_presets(file_path):
            self.populate_presets_table()
            self.logic.save_presets()

    def _export_presets(self):
        file_path = filedialog.asksaveasfilename(
            parent=self.app_instance,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"exported_presets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
        if file_path:
            self.logic.export_presets(file_path)

    def _delete_selected_preset(self):
        selected_items = self.presets_tree.selection()
        if not selected_items:
            self.console_print_func("⚠️ No preset selected for deletion. Pick one, genius!")
            return

        filenames_to_delete = [self.presets_tree.item(item, 'values')[0] for item in selected_items]
        if self.logic.delete_presets(filenames_to_delete):
            self.populate_presets_table()
            self.logic.save_presets()

    def _on_double_click(self, event):
        region = self.presets_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.presets_tree.identify_column(event.x)
            item = self.presets_tree.identify_row(event.y)
            if item and self.columns[int(col[1:]) - 1] != 'Filename':
                col_index = int(col[1:]) - 1
                self._start_edit(item, col_index)

    def _start_edit(self, item_id, col_index):
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            self._end_edit()

        x, y, width, height = self.presets_tree.bbox(item_id, f"#{col_index + 1}")
        current_values_in_tree = self.presets_tree.item(item_id, "values")
        current_value = current_values_in_tree[col_index]
        filename_of_edited_row = current_values_in_tree[0]

        self.edit_entry = ttk.Entry(self.presets_tree, style='TEntry')
        self.edit_entry.place(x=x, y=y, width=width, height=height, anchor="nw")
        self.edit_entry.insert(0, current_value)
        self.edit_entry.focus_set()

        self.current_edit_cell = (item_id, col_index, filename_of_edited_row)
        self.is_editing_cell = True

        self.edit_entry.bind("<FocusOut>", self._end_edit)
        self.edit_entry.bind("<Return>", self._on_edit_return)
        self.edit_entry.bind("<Escape>", self._on_edit_escape)

    def _on_edit_return(self, event):
        self._end_edit()
        return "break"

    def _on_edit_escape(self, event):
        if hasattr(self, 'edit_entry') and self.edit_entry.winfo_exists():
            self.edit_entry.destroy()
            self.current_edit_cell = None
            self.is_editing_cell = False
        return "break"

    def _end_edit(self, event=None):
        if not hasattr(self, 'edit_entry') or not self.edit_entry.winfo_exists():
            return

        if self.current_edit_cell:
            item_id_from_edit, col_index, filename_of_edited_row = self.current_edit_cell
            new_value = self.edit_entry.get()
            original_col_name = self.columns[col_index].split(' ')[0]
            
            if self.logic.update_preset_value(filename_of_edited_row, original_col_name, new_value):
                self.logic.save_presets()
            
            self.populate_presets_table()
            self.current_edit_cell = None

        self.edit_entry.destroy()
        self.is_editing_cell = False

    def _on_tab_selected(self, event):
        if self.logic.has_unsaved_changes:
            self.logic.save_presets()
        self.logic.load_presets()
        self.populate_presets_table()
        
    def _on_tree_select(self, event):
        pass

    def _move_preset_up(self):
        selected_items = self.presets_tree.selection()
        if not selected_items:
            self.console_print_func("⚠️ No preset selected to move up. Select one, genius!")
            return
        
        filenames_to_move = [self.presets_tree.item(item, 'values')[0] for item in selected_items]
        
        for filename in filenames_to_move:
            self.logic.move_preset_up(filename)
        
        self.populate_presets_table()
        self.presets_tree.selection_set(self.presets_tree.get_children()[:len(filenames_to_move)])
        self.logic.save_presets()

    def _move_preset_down(self):
        selected_items = self.presets_tree.selection()
        if not selected_items:
            self.console_print_func("⚠️ No preset selected to move down. Select one, buddy!")
            return
            
        filenames_to_move = [self.presets_tree.item(item, 'values')[0] for item in selected_items]
        
        for filename in reversed(filenames_to_move):
            self.logic.move_preset_down(filename)

        self.populate_presets_table()
        self.presets_tree.selection_set(self.presets_tree.get_children()[-len(filenames_to_move):])
        self.logic.save_presets()
