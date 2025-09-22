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
# Version 20250921.232515.2
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
import pandas as pd
import numpy as np
from tkinter import TclError

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_marker_file_handling import (
    maker_file_check_for_markers_file,
    maker_file_load_markers_file,
    maker_file_load_ias_html,
    maker_file_load_wwb_shw,
    maker_file_load_sb_pdf,
    maker_file_save_intermediate_file,
    maker_file_save_open_air_file
)
from workers.worker_marker_report_converter import (
    Marker_convert_wwb_zip_report_to_csv,  # New import for the zip worker
    Marker_convert_SB_v2_PDF_File_report_to_csv # NEW: Import for the SB v2 PDF converter
)
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
current_version = "20250921.232515.2"
current_version_hash = (20250921 * 232515 * 2)
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
        super().__init__(master, **kwargs)
        
        self.app_instance = app_instance
        self.mqtt_util = mqtt_util
        self.tree_headers = []
        self.tree_data = []    
        self.sort_column = None
        self.sort_direction = False
        
        self._apply_styles(theme_name=DEFAULT_THEME)
        self._create_widgets()
        
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

        # Button styling - Refined to use central theme dictionary
        style.configure('TButton',
                        background=colors["secondary"],
                        foreground=colors["text"],
                        padding=10, relief=colors["relief"],
                        borderwidth=colors["border_width"])
        style.map('TButton',
                  background=[('pressed', colors["accent"]),
                              ('active', colors["hover_blue"])])
        
        # NOTE: Removed the redundant 'Blue', 'Orange', and 'Red' style definitions
        # to adhere to the core theme. The following `configure` and `map` calls
        # for specific button styles are now more streamlined.
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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_rowconfigure(2, weight=0) 
        
        load_markers_frame = ttk.LabelFrame(self, text="Load Markers", padding=(5,5,5,5))
        load_markers_frame.grid(row=0, column=0, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, sticky="ew")
        load_markers_frame.grid_columnconfigure(0, weight=1)
        load_markers_frame.grid_columnconfigure(1, weight=1)
        load_markers_frame.grid_columnconfigure(2, weight=1)
        load_markers_frame.grid_columnconfigure(3, weight=1) 
        
        # The button is now configured with the `Action.TButton` style
        self.load_csv_button = ttk.Button(load_markers_frame, text="Load CSV Marker Set", style='Action.TButton', command=self._load_markers_file_action)
        self.load_csv_button.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        self.load_ias_html_button = ttk.Button(load_markers_frame, text="Load IAS HTML", style='Action.TButton', command=self._load_ias_html_action)
        self.load_ias_html_button.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        
        self.load_wwb_shw_button = ttk.Button(load_markers_frame, text="Load WWB.shw", style='Action.TButton', command=self._load_wwb_shw_action)
        self.load_wwb_shw_button.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        
        # NEW: Add the button to load WWB.zip files
        self.load_wwb_zip_button = ttk.Button(load_markers_frame, text="Load WWB.zip", style='Action.TButton', command=self._load_wwb_zip_action)
        self.load_wwb_zip_button.grid(row=1, column=2, padx=2, pady=2, sticky="ew")

        self.load_sb_pdf_button = ttk.Button(load_markers_frame, text="Load SB PDF", style='Action.TButton', command=self._load_sb_pdf_action)
        self.load_sb_pdf_button.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        
        # NEW: Add the button to load the new SB V2.pdf format
        self.load_sb_v2_pdf_button = ttk.Button(load_markers_frame, text="Load SB V2.pdf", style='Action.TButton', command=self._load_sb_v2_pdf_action)
        self.load_sb_v2_pdf_button.grid(row=1, column=3, padx=2, pady=2, sticky="ew")
        
        marker_table_frame = ttk.LabelFrame(self, text="Marker Editor", padding=(5,5,5,5))
        marker_table_frame.grid(row=1, column=0, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, sticky="nsew")
        marker_table_frame.grid_columnconfigure(0, weight=1)
        marker_table_frame.grid_rowconfigure(0, weight=1)
        
        self.marker_tree = ttk.Treeview(marker_table_frame, show=("headings", "tree"))
        self.marker_tree.grid(row=0, column=0, sticky="nsew", padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
        
        self.marker_tree.column("#0", width=0, stretch=tk.NO)

        tree_yscroll = ttk.Scrollbar(marker_table_frame, orient="vertical", command=self.marker_tree.yview)
        tree_yscroll.grid(row=0, column=1, sticky="ns")
        self.marker_tree.configure(yscrollcommand=tree_yscroll.set)
        
        tree_xscroll = ttk.Scrollbar(marker_table_frame, orient="horizontal", command=self.marker_tree.xview)
        tree_xscroll.grid(row=1, column=0, sticky="ew")
        self.marker_tree.configure(xscrollcommand=tree_xscroll.set)
        
        self.save_open_air_button = ttk.Button(self, text="Save Markers as Open Air.csv", style='Orange.TButton', command=self._save_open_air_file_action)
        self.save_open_air_button.grid(row=2, column=0, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, sticky="ew")

    def _update_treeview(self):
        # The GUI is now responsible for updating the display.
        self.marker_tree.delete(*self.marker_tree.get_children())
        
        # We need to map the new column names to the old internal names for consistency.
        standardized_headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ (MHZ)", "PEAK"]
        self.marker_tree["columns"] = standardized_headers
        
        debug_log(
            message=f"🔁🔵 Now adding {len(self.tree_data)} rows to the Treeview. Headers: {standardized_headers}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}",
            console_print_func=console_log
        )
        for col in standardized_headers:
            self.marker_tree.heading(col, text=col)
            self.marker_tree.column(col, width=100)
            
        for row in self.tree_data:
            # We now assume the data coming from the worker is already a dictionary.
            if isinstance(row, dict):
                values = [row.get(raw_header, '') for raw_header in standardized_headers]
                self.marker_tree.insert("", "end", values=values)
            else:
                self.marker_tree.insert("", "end", values=row)

    # --- ACTION WRAPPERS ---
    # These functions are now simple wrappers that call the worker functions
    # and then update the GUI with the results.

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
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)

    def _load_ias_html_action(self):
        headers, data = maker_file_load_ias_html()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)

    def _load_wwb_shw_action(self):
        headers, data = maker_file_load_wwb_shw()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)
    
    def _load_wwb_zip_action(self):
        """
        Action to load a WWB.zip file via a dialog.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        # The GUI now handles the file dialog.
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
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)

    def _load_sb_pdf_action(self):
        headers, data = maker_file_load_sb_pdf()
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)

    def _load_sb_v2_pdf_action(self):
        """
        Action to load a new SB V2.pdf file via a dialog.
        This function now calls the new worker function to process the file.
        """
        current_function = inspect.currentframe().f_code.co_name
        
        # The GUI handles the file dialog to get the path.
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

        # Pass the file path to the new worker function.
        headers, data = Marker_convert_SB_v2_PDF_File_report_to_csv(pdf_file_path=file_path)
        
        # Update the GUI with the results from the worker.
        if headers and data:
            self.tree_headers = headers
            self.tree_data = data
            self._update_treeview()
            maker_file_save_intermediate_file(self.tree_headers, self.tree_data)

    def _save_open_air_file_action(self):
        # Call the worker function with the current data from the GUI
        maker_file_save_open_air_file(self.tree_headers, self.tree_data)