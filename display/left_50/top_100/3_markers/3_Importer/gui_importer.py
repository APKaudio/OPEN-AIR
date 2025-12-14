# display/left_40/top_100/tab_2_markers/sub_tab_3_Importer/gui_child_1_marker_importer.py
#
# This file provides a basic GUI component with buttons for importing marker data.
# It now serves as the presentation layer, with all file handling logic moved
# to a dedicated worker file.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20251127.000000.1

import tkinter as tk
from tkinter import filedialog, ttk
import os
import csv
import xml.etree.ElementTree as ET
import sys
import inspect
import threading
import json
import datetime
import re
import pathlib
from tkinter import TclError

# --- Graceful Dependency Importing ---
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    np = None
    PANDAS_AVAILABLE = False

# --- Module Imports ---
from display.logger import debug_log, console_log, log_visa_command
from workers.importers.worker_marker_file_import_handling import (
    maker_file_check_for_markers_file,
    maker_file_load_markers_file,
    maker_file_load_ias_html,
    maker_file_load_wwb_shw,
    maker_file_load_sb_pdf,
    maker_file_save_intermediate_file,
    maker_file_save_open_air_file
)
from workers.importers.worker_marker_file_import_converter import (
    Marker_convert_wwb_zip_report_to_csv,
    Marker_convert_SB_v2_PDF_File_report_to_csv
)
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = (20251127 * 0 * 1)
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parents[5]
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class MarkerImporterTab(ttk.Frame):
    """
    A stripped-down Tkinter Frame focused on displaying marker data and triggering
    actions via a separate worker module.
    """
    def __init__(self, master=None, app_instance=None, mqtt_util=None, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message="🛠️🟢 Initializing MarkerImporterTab. The GUI is now lean and mean! 🎉",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
        if 'config' in kwargs:
            kwargs.pop('config')
        super().__init__(master, **kwargs)

        self.app_instance = app_instance
        self.mqtt_util = mqtt_util
        self.tree_headers = []
        self.tree_data = []
        self.sort_column = None
        self.sort_direction = False

        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()

        if not PANDAS_AVAILABLE:
            console_log("❌ Critical dependency 'pandas' or 'numpy' not found. Marker Importer will have limited functionality.")
            # Optionally, disable the whole tab or show an error message
            error_label = ttk.Label(self, text="Error: NumPy and Pandas libraries are required for this tab.", foreground="red")
            error_label.pack(pady=20)
            return

        # Call the worker to check for an existing file on startup
        self.tree_headers, self.tree_data = maker_file_check_for_markers_file()
        self._update_treeview()

        debug_log(
            message="🛠️🟢 MarkerImporterTab has been fully instantiated. Now creating widgets!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

    def _apply_styles(self, theme_name: str):
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")

        # General widget styling
        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])

        # Table (Treeview) styling
        style.configure('Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

        style.configure('Treeview.Heading',
                        background=colors["table_heading_bg"],
                        foreground=colors["fg"],
                        relief=colors["relief"],
                        borderwidth=colors["border_width"])

        style.configure('Markers.TEntry',
                        fieldbackground=colors["entry_bg"],
                        foreground=colors["entry_fg"],
                        insertbackground=colors["fg"],
                        selectbackground=colors["hover_blue"],
                        selectforeground=colors["text"])
        
        style.configure('TButton',
                        background=colors["secondary"],
                        foreground=colors["text"],
                        padding=10, relief=colors["relief"],
                        borderwidth=colors["border_width"])
        style.map('TButton',
                  background=[('pressed', colors["accent"]),
                              ('active', colors["hover_blue"])])
        
        style.configure('Green.TButton', background='#6a9955', foreground='#ffffff')
        style.map('Green.TButton',
                  background=[('pressed', '!disabled', '#4a6f3b'),
                              ('active', '#8ab97c')],
                  foreground=[('pressed', '!disabled', '#ffffff'),
                              ('active', '#ffffff')])
        
        style.configure('Blue.TButton', 
                        background=colors["button_style_toggle"]["background"], 
                        foreground=colors["button_style_toggle"]["foreground"])
        style.map('Blue.TButton',
                  background=[('pressed', '!disabled', colors["button_style_toggle"]["Button_Pressed_Bg"]),
                              ('active', colors["button_style_toggle"]["Button_Hover_Bg"])],
                  foreground=[('pressed', '!disabled', colors["button_style_toggle"]["foreground"]),
                              ('active', colors["button_style_toggle"]["foreground"])])

        style.configure('Orange.TButton', 
                        background=colors["button_style_toggle"]["background"], 
                        foreground=colors["button_style_toggle"]["foreground"])
        style.map('Orange.TButton',
                  background=[('pressed', '!disabled', colors["button_style_toggle"]["Button_Pressed_Bg"]),
                              ('active', colors["button_style_toggle"]["Button_Hover_Bg"])],
                  foreground=[('pressed', '!disabled', colors["button_style_toggle"]["foreground"]),
                              ('active', colors["button_style_toggle"]["foreground"])])
        
        style.configure('Red.TButton', 
                        background=colors["button_style_toggle"]["background"], 
                        foreground=colors["button_style_toggle"]["foreground"])
        style.map('Red.TButton',
                  background=[('pressed', '!disabled', colors["button_style_toggle"]["Button_Pressed_Bg"]),
                              ('active', colors["button_style_toggle"]["Button_Hover_Bg"])],
                  foreground=[('pressed', '!disabled', colors["button_style_toggle"]["foreground"]),
                              ('active', colors["button_style_toggle"]["foreground"])])

    def _create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)
        
        load_markers_frame = ttk.LabelFrame(self, text="Load Markers", padding=(5,5,5,5))
        load_markers_frame.pack(fill=tk.X, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
        
        self.load_csv_button = ttk.Button(load_markers_frame, text="Load CSV Marker Set", style='Action.TButton', command=self._load_markers_file_action)
        self.load_csv_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.load_ias_html_button = ttk.Button(load_markers_frame, text="Load IAS HTML", style='Action.TButton', command=self._load_ias_html_action)
        self.load_ias_html_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.load_wwb_shw_button = ttk.Button(load_markers_frame, text="Load WWB.shw", style='Action.TButton', command=self._load_wwb_shw_action)
        self.load_wwb_shw_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.load_wwb_zip_button = ttk.Button(load_markers_frame, text="Load WWB.zip", style='Action.TButton', command=self._load_wwb_zip_action)
        self.load_wwb_zip_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.load_sb_pdf_button = ttk.Button(load_markers_frame, text="Load SB PDF", style='Action.TButton', command=self._load_sb_pdf_action)
        self.load_sb_pdf_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.load_sb_v2_pdf_button = ttk.Button(load_markers_frame, text="Load SB V2.pdf", style='Action.TButton', command=self._load_sb_v2_pdf_action)
        self.load_sb_v2_pdf_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        marker_table_frame = ttk.LabelFrame(self, text="Marker Editor", padding=(5,5,5,5))
        marker_table_frame.pack(fill=tk.BOTH, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
        
        self.marker_tree = ttk.Treeview(marker_table_frame, show=("headings", "tree"))
        self.marker_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
        self.marker_tree.column("#0", width=0, stretch=tk.NO)
        
        tree_yscroll = ttk.Scrollbar(marker_table_frame, orient="vertical", command=self.marker_tree.yview)
        tree_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.marker_tree.configure(yscrollcommand=tree_yscroll.set)
        
        tree_xscroll = ttk.Scrollbar(marker_table_frame, orient="horizontal", command=self.marker_tree.xview)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.marker_tree.configure(xscrollcommand=tree_xscroll.set)

        self.marker_tree.bind("<Double-1>", self._on_tree_double_click)
        self.marker_tree.bind("<Button-1>", self._on_tree_header_click, add="+")
        self.marker_tree.bind("<Delete>", self._delete_selected_row)

        append_markers_frame = ttk.LabelFrame(self, text="Append Markers", padding=(5,5,5,5))
        append_markers_frame.pack(fill=tk.X, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
        
        self.append_csv_button = ttk.Button(append_markers_frame, text="Append CSV Marker Set", style='Action.TButton', command=self._append_markers_file_action)
        self.append_csv_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.append_ias_html_button = ttk.Button(append_markers_frame, text="Append IAS HTML", style='Action.TButton', command=self._append_ias_html_action)
        self.append_ias_html_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.append_wwb_shw_button = ttk.Button(append_markers_frame, text="Append WWB.shw", style='Action.TButton', command=self._append_wwb_shw_action)
        self.append_wwb_shw_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.append_wwb_zip_button = ttk.Button(append_markers_frame, text="Append WWB.zip", style='Action.TButton', command=self._append_wwb_zip_action)
        self.append_wwb_zip_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.append_sb_pdf_button = ttk.Button(append_markers_frame, text="Append SB PDF", style='Action.TButton', command=self._append_sb_pdf_action)
        self.append_sb_pdf_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        
        self.append_sb_v2_pdf_button = ttk.Button(append_markers_frame, text="Append SB V2.pdf", style='Action.TButton', command=self._append_sb_v2_pdf_action)
        self.append_sb_v2_pdf_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        self.save_open_air_button = ttk.Button(self, text="Save Markers as Open Air.csv", style='Orange.TButton', command=self._save_open_air_file_action)
        self.save_open_air_button.pack(fill=tk.X, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    def _update_treeview(self):
        self.marker_tree.delete(*self.marker_tree.get_children())
        standardized_headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ_MHZ", "PEAK"]
        self.marker_tree["columns"] = standardized_headers
        debug_log(
            message=f"🔁🔵 Now adding {len(self.tree_data)} rows to the Treeview. Headers: {standardized_headers}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}",
            console_print_func=console_log
        )
        for col in standardized_headers:
            self.marker_tree.heading(col, text=col, command=lambda c=col: self._sort_treeview(c, False))
            self.marker_tree.column(col, width=100)

        for row in self.tree_data:
            if isinstance(row, dict):
                values = [row.get(raw_header, '') for raw_header in standardized_headers]
                self.marker_tree.insert("", "end", values=values)
            else:
                self.marker_tree.insert("", "end", values=row)

    def _check_for_markers_file(self):
        headers, data = maker_file_check_for_markers_file()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()

    def _load_markers_file_action(self):
        headers, data = maker_file_load_markers_file()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _load_ias_html_action(self):
        headers, data = maker_file_load_ias_html()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _load_wwb_shw_action(self):
        headers, data = maker_file_load_wwb_shw()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _load_wwb_zip_action(self):
        current_function = inspect.currentframe().f_code.co_name
        file_path = filedialog.askopenfilename(
            defaultextension=".zip",
            filetypes=[("Shure Wireless Workbench files", "*.zip"), ("All files", "*.*")]
        )
        if not file_path:
            debug_log(
                message="🛠️🟡 'Load WWB.zip' action cancelled by user.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            return
        headers, data = Marker_convert_wwb_zip_report_to_csv(file_path=file_path)
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _load_sb_pdf_action(self):
        headers, data = maker_file_load_sb_pdf()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _load_sb_v2_pdf_action(self):
        current_function = inspect.currentframe().f_code.co_name
        file_path = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("Sound Base V2 PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not file_path:
            debug_log(
                message="🛠️🟡 'Load SB V2.pdf' action cancelled by user.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            return
        headers, data = Marker_convert_SB_v2_PDF_File_report_to_csv(pdf_file_path=file_path)
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_markers_file_action(self):
        headers, new_data = maker_file_load_markers_file()
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_ias_html_action(self):
        headers, new_data = maker_file_load_ias_html()
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_wwb_shw_action(self):
        headers, new_data = maker_file_load_wwb_shw()
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_wwb_zip_action(self):
        current_function = inspect.currentframe().f_code.co_name
        file_path = filedialog.askopenfilename(
            defaultextension=".zip",
            filetypes=[("Shure Wireless Workbench files", "*.zip"), ("All files", "*.*")]
        )
        if not file_path:
            debug_log(
                message="🛠️🟡 'Append WWB.zip' action cancelled by user.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            return
        headers, new_data = Marker_convert_wwb_zip_report_to_csv(file_path=file_path)
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_sb_pdf_action(self):
        headers, new_data = maker_file_load_sb_pdf()
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _append_sb_v2_pdf_action(self):
        current_function = inspect.currentframe().f_code.co_name
        file_path = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("Sound Base V2 PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not file_path:
            debug_log(
                message="🛠️🟡 'Append SB V2.pdf' action cancelled by user.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            return
        headers, new_data = Marker_convert_SB_v2_PDF_File_report_to_csv(pdf_file_path=file_path)
        if headers and new_data:
            self.tree_headers = headers
            self.tree_data.extend(new_data)
            self._update_treeview()
            self._save_markers_file_internally()

    def _save_open_air_file_action(self):
        maker_file_save_open_air_file(self.tree_headers, self.tree_data)
        if self.mqtt_util:
            self._publish_markers_to_mqtt()

    def _delete_selected_row(self, event):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{current_file} - {current_function}] Delete key pressed.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
        selected_items = self.marker_tree.selection()
        if not selected_items:
            console_log("🟡 No row selected to delete.")
            return
        for item in selected_items:
            index_in_tree = self.marker_tree.index(item)
            if index_in_tree < len(self.tree_data):
                self.marker_tree.delete(item)
                del self.tree_data[index_in_tree]
                console_log(f"✅ Deleted row {index_in_tree + 1}.")
            else:
                console_log(f"❌ Error: Row {index_in_tree + 1} not found in data.")
        self._save_markers_file_internally()

    def _on_tree_double_click(self, event):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"[{current_file} - {current_function}] Treeview double-clicked for editing.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
        if not self.marker_tree.identify_region(event.x, event.y) == "cell":
            return
        column_id = self.marker_tree.identify_column(event.x)
        item_id = self.marker_tree.identify_row(event.y)
        if not item_id or not column_id:
            return
        col_index = int(column_id[1:]) - 1
        if col_index < 0 or col_index >= len(self.tree_headers):
            debug_log(f"[{current_file} - {current_function}] Invalid column index {col_index} for editing.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
            return
        current_value = self.marker_tree.item(item_id, 'values')[col_index]
        self._start_editing_cell(item_id, col_index, initial_value=current_value)

    def _start_editing_cell(self, item, col_index, initial_value=""):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        for widget in self.marker_tree.winfo_children():
            if isinstance(widget, ttk.Entry) and widget.winfo_name() == "cell_editor":
                widget.destroy()
        entry_editor = ttk.Entry(self.marker_tree, style="Markers.TEntry", name="cell_editor")
        entry_editor.insert(0, initial_value)
        entry_editor.focus_force()
        x, y, width, height = self.marker_tree.bbox(item, self.marker_tree["columns"][col_index])
        entry_editor.place(x=x, y=y, width=width, height=height)
        entry_editor.current_item = item
        entry_editor.current_col_index = col_index
        def on_edit_complete_and_navigate(event, navigate_direction=None):
            new_value = entry_editor.get()
            entry_editor.destroy()
            current_values = list(self.marker_tree.item(item, 'values'))
            current_values[col_index] = new_value
            self.marker_tree.item(item, values=current_values)
            row_idx = self.marker_tree.index(item)
            if row_idx < len(self.tree_data) and isinstance(self.tree_data[row_idx], dict):
                self.tree_data[row_idx][self.tree_headers[col_index]] = new_value
                console_log(f"Updated cell: Row {row_idx+1}, Column '{self.tree_headers[col_index]}' to '{new_value}'")
                debug_log(f"[{current_file} - {current_function}] Updated tree_data[{row_idx}]['{self.tree_headers[col_index]}'] to '{new_value}'.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
                self._save_markers_file_internally()
            else:
                debug_log(f"[{current_file} - {current_function}] Error: Row index {row_idx} out of bounds or data not a dictionary for self.tree_data.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
            if navigate_direction:
                self._navigate_cells(item, col_index, navigate_direction)
        entry_editor.bind("<Return>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Tab>", lambda e: on_edit_complete_and_navigate(e, "right"))
        entry_editor.bind("<Shift-Tab>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Control-Return>", lambda e: on_edit_complete_and_navigate(e, "ctrl_down"))
        entry_editor.bind("<FocusOut>", lambda e: on_edit_complete_and_navigate(e, None))
        entry_editor.bind("<Up>", lambda e: on_edit_complete_and_navigate(e, "up"))
        entry_editor.bind("<Down>", lambda e: on_edit_complete_and_navigate(e, "down"))
        entry_editor.bind("<Left>", lambda e: on_edit_complete_and_navigate(e, "left"))
        entry_editor.bind("<Right>", lambda e: on_edit_complete_and_navigate(e, "right"))

    def _navigate_cells(self, current_item, current_col_index, direction):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"[{current_file} - {current_function}] Navigating cells.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
        items = self.marker_tree.get_children()
        num_rows = len(items)
        num_cols = len(self.tree_headers)
        current_row_idx = items.index(current_item) if current_item in items else -1
        next_item = None
        next_col_index = -1
        initial_value_for_next_cell = ""
        if current_row_idx == -1:
            debug_log(f"[{current_file} - {current_function}] Current item not found in tree for navigation.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
            return
        if direction == "down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
        elif direction == "up":
            next_row_idx = current_row_idx - 1
            next_col_index = current_col_index
            if next_row_idx >= 0:
                next_item = items[next_row_idx]
        elif direction == "right":
            next_col_index = current_col_index + 1
            if next_col_index < num_cols:
                next_item = current_item
            else:
                next_row_idx = current_row_idx + 1
                if next_row_idx < num_rows:
                    next_item = items[next_row_idx]
                    next_col_index = 0
        elif direction == "left":
            next_col_index = current_col_index - 1
            if next_col_index >= 0:
                next_item = current_item
            else:
                next_row_idx = current_row_idx - 1
                if next_row_idx >= 0:
                    next_item = items[next_row_idx]
                    next_col_index = num_cols - 1
        elif direction == "ctrl_down":
            next_row_idx = current_row_idx + 1
            next_col_index = current_col_index
            if next_row_idx < num_rows:
                next_item = items[next_row_idx]
                prev_cell_value = self.marker_tree.item(current_item, 'values')[current_col_index]
                initial_value_for_next_cell = self._increment_string_with_trailing_digits(prev_cell_value)
                new_values = list(self.marker_tree.item(next_item, 'values'))
                new_values[next_col_index] = initial_value_for_next_cell
                self.marker_tree.item(next_item, values=new_values)
                if next_row_idx < len(self.tree_data) and isinstance(self.tree_data[next_row_idx], dict):
                    self.tree_data[next_row_idx][self.tree_headers[next_col_index]] = initial_value_for_next_cell
                else:
                    debug_log(f"[{current_file} - {current_function}] Cannot Ctrl+Enter: No row below.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
                    return
        if next_item is not None and next_col_index != -1:
            if direction != "ctrl_down":
                try:
                    next_item_values = self.marker_tree.item(next_item, 'values')
                    if 0 <= next_col_index < len(next_item_values):
                        initial_value_for_next_cell = next_item_values[next_col_index]
                    else:
                        debug_log(f"[{current_file} - {current_function}] Next column index {next_col_index} out of bounds for next item values. Setting empty.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
                        initial_value_for_next_cell = ""
                except Exception as e:
                    debug_log(f"[{current_file} - {current_function}] Error getting initial value for next cell: {e}. Setting empty.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
                    initial_value_for_next_cell = ""
            self.marker_tree.focus(next_item)
            self.marker_tree.selection_set(next_item)
            self.after(10, lambda: self._start_editing_cell(next_item, next_col_index, initial_value_for_next_cell))
        else:
            debug_log(f"[{current_file} - {current_function}] No cell to navigate to in direction: {direction}", file=current_file, version=current_version, function=current_function, console_print_func=console_log)

    def _increment_string_with_trailing_digits(self, text):
        match = re.search(r'(\d+)$', text)
        if match:
            num_str = match.group(1)
            num_int = int(num_str)
            incremented_num = num_int + 1
            new_num_str = str(incremented_num).zfill(len(num_str))
            return text[:-len(num_str)] + new_num_str
        return text

    def _on_tree_header_click(self, event):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"[{current_file} - {current_function}] Treeview header clicked for sorting.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
        region = self.marker_tree.identify_region(event.x, event.y)
        if region == "heading":
            column_id = self.marker_tree.identify_column(event.x)
            col_index = int(column_id[1:]) - 1
            if col_index < 0 or col_index >= len(self.tree_headers):
                debug_log(f"[{current_file} - {current_function}] Invalid column index {col_index} for sorting.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
                return
            column_name = self.tree_headers[col_index]
            if self.sort_column == column_name:
                self.sort_direction = not self.sort_direction
            else:
                self.sort_column = column_name
                self.sort_direction = True
            self._sort_treeview(column_name, self.sort_direction)

    def _sort_treeview(self, column_name, ascending):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"[{current_file} - {current_function}] Sorting treeview by '{column_name}', ascending: {ascending}.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)
        def get_sort_key(item):
            value = item.get(column_name, "")
            try:
                return float(value)
            except (ValueError, TypeError):
                return str(value)
        self.tree_data.sort(key=get_sort_key, reverse=not ascending)
        self._populate_marker_tree()
        console_log(f"Sorted by '{column_name}' {'Ascending' if ascending else 'Descending'}.")

    def _populate_marker_tree(self):
        """Re-populates the treeview from the internal data model."""
        self.marker_tree.delete(*self.marker_tree.get_children())
        standardized_headers = self.tree_headers if self.tree_headers else ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ_MHZ", "PEAK"]
        self.marker_tree["columns"] = standardized_headers
        for col in standardized_headers:
            self.marker_tree.heading(col, text=col, command=lambda c=col: self._sort_treeview(c, self.sort_column != c or not self.sort_direction))
            self.marker_tree.column(col, width=100)
        for row in self.tree_data:
            values = [row.get(raw_header, '') for raw_header in standardized_headers]
            self.marker_tree.insert("", "end", values=values)

    def _update_markers_display_tab_data(self):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"[{current_file} - {current_function}] Notifying display tab of data change.", file=current_file, version=current_version, function=current_function, console_print_func=console_log)

    def _save_markers_file_internally(self):
        maker_file_save_intermediate_file(self.tree_headers, self.tree_data)
        if self.mqtt_util:
            self._publish_markers_to_mqtt()

    def _publish_markers_to_mqtt(self):
        from workers.importers.worker_marker_csv_to_json_mqtt import csv_to_json_and_publish
        csv_to_json_and_publish(mqtt_util=self.mqtt_util)