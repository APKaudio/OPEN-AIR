# display/left_50/top_100/3_markers/2_peak_hunter/gui_peak_hunter.py
#
# This file (gui_peak_hunter.py) provides the MarkerPeakHunterGUI component for the Peak Hunter tab, displaying marker data and tuning instruments based on selections.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251215  ##Update on the day the change was made
Current_Time = 195000  ## update at the time it was edited and compiled
Current_iteration = 3 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import pathlib
from tkinter import filedialog

# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.exporters.worker_file_csv_export import CsvExportUtility
from display.styling.style import THEMES, DEFAULT_THEME
import workers.setup.app_constants as app_constants

LOCAL_DEBUG_ENABLE = False

# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("/", "/")

# --- No Magic Numbers (as per your instructions) ---


class MarkerPeakHunterGUI(ttk.Frame):
    """
    A GUI component for displaying marker data in a table and exporting it.
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the GUI, sets up the layout, and subscribes to the MQTT topic.
        
        Args:
            parent (tk.Widget): The parent widget for this frame.
        """
        current_function_name = inspect.currentframe().f_code.co_name

        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🟢 Initializing the {self.__class__.__name__}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
            )

        try:
            if 'config' in kwargs:
                kwargs.pop('config')
            super().__init__(parent, *args, **kwargs)

            self.current_file = current_file
            self.current_version = current_version
            self.current_version_hash = current_version_hash
            self.csv_export_util = CsvExportUtility(print_to_gui_func=print)
            self.current_class_name = self.__class__.__name__

            self._apply_styles(theme_name=DEFAULT_THEME)

            # --- MQTT Message Log Table ---
            self.table_frame = ttk.Frame(self)
            self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            horizontal_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
            self.commands_table = ttk.Treeview(self.table_frame, xscrollcommand=horizontal_scrollbar.set, show="headings", style="Custom.Treeview")
            horizontal_scrollbar.config(command=self.commands_table.xview)
            
            vertical_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.commands_table.yview)
            self.commands_table.config(yscrollcommand=vertical_scrollbar.set)

            horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.commands_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # --- File Controls Section ---
            file_frame = ttk.LabelFrame(self, text="File")
            file_frame.pack(fill=tk.X, padx=10, pady=5)
           
            # Button: Export to CSV
            self.export_button = ttk.Button(
                file_frame,
                text="Export to CSV",
                command=self._export_table_data
            )
            self.export_button.pack(side=tk.LEFT, padx=5, pady=5)


            # --- Status Bar at the bottom ---
            status_bar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

            file_parts = self.current_file.rsplit('/', 1)
            file_folder = file_parts[0] if len(file_parts) > 1 else ""
            file_name = file_parts[-1]

            status_text = f"Version: {self.current_version} | Folder: {file_folder} | File: {file_name}"
            status_label = ttk.Label(status_bar, text=status_text, anchor='w')
            status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        except Exception as e:
            debug_log(
                message=f"❌ Error in {current_function_name}: {e}",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
            )
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=self.current_file,
                    version=self.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                )
    
    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the GUI elements using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure('TFrame', background=colors["bg"])
        style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
        style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
        style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=colors["padding"] * 5, relief=colors["relief"], borderwidth=colors["border_width"] * 2)
        style.map('TButton', background=[('active', colors["secondary"])])
        
        style.configure('Custom.Treeview',
                        background=colors["table_bg"],
                        foreground=colors["table_fg"],
                        fieldbackground=colors["table_bg"],
                        bordercolor=colors["table_border"],
                        borderwidth=colors["border_width"])

        style.configure('Custom.Treeview.Heading',
                        background=colors["table_heading_bg"],
                        foreground=colors["fg"],
                        relief=colors["relief"],
                        borderwidth=colors["border_width"])

    def _export_table_data(self):
        """
        Opens a file dialog and exports the current data from the table to a CSV file.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🔵 Preparing to export table data to CSV.",
                file=self.current_file,
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
            )

        try:
            file_path = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                title="Save Table Data as CSV",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                defaultextension=".csv"
            )
            
            if file_path:
                data = []
                headers = self.commands_table["columns"]
                for item_id in self.commands_table.get_children():
                    row_values = self.commands_table.item(item_id, 'values')
                    row_dict = dict(zip(headers, row_values))
                    data.append(row_dict)
                    
                self.csv_export_util.export_data_to_csv(data=data, file_path=file_path)
               
            

        except Exception as e:
            debug_log(message=f"❌ Error in {current_function_name}: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                    file=self.current_file,
                    version=self.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )