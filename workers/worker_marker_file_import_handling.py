# workers/worker_marker_file_handling.py
#
# This worker module handles all file I/O and data processing logic for marker files,
# separating it from the GUI's presentation layer.
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
# Version 20251005.220127.1

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
from tkinter import filedialog, messagebox

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from workers.worker_marker_file_import_converter import (
    Marker_convert_IAShtml_report_to_csv,
    Marker_convert_SB_PDF_File_report_to_csv,
    Marker_convert_WWB_SHW_File_report_to_csv,
    Marker_convert_csv_unknow_report_to_csv
)

# --- Global Scope Variables ---
current_version = "20251005.220127.1"
current_version_hash = (20251005 * 220127 * 1)
current_file_path = pathlib.Path(__file__).resolve()
# FIX: The project root is one level up from the 'workers' folder.
project_root = current_file_path.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
# NEW CONSTANT: Define the canonical headers
CANONICAL_HEADERS = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ_MHZ", "PEAK"]

def maker_file_check_for_markers_file():
    # Checks for the MARKERS.csv file in the DATA directory and loads it if it exists.
    current_function = inspect.currentframe().f_code.co_name
    
    # ANCHOR FIX: Use the stable project_root calculated above.
    target_path = project_root / 'DATA' / 'MARKERS.csv'
    
    debug_log(
        message=f"🛠️🕵️‍♂️ Checking for existing markers file at: {target_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    
    if target_path.is_file():
        debug_log(
            message=f"✅ Found an existing MARKERS.csv file. Attempting to load.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        try:
            with open(target_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                # Use canonical headers if the file is empty or headers are bad
                try:
                    headers = next(reader)
                except StopIteration:
                    headers = CANONICAL_HEADERS
                data = list(reader)
            
            debug_log(
                message="✅ Successfully loaded MARKERS.csv on startup.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            return headers, data
        except Exception as e:
            debug_log(
                message=f"❌ Error loading existing MARKERS.csv on startup: {e}",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            console_log(f"Error: Failed to load existing MARKERS.csv. {e}")
    else:
        debug_log(
            message="🛠️🟡 No existing MARKERS.csv found. Starting with a blank table.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
    return CANONICAL_HEADERS, []

def maker_file_load_markers_file():
    # Opens a file dialog, loads a generic CSV file, and returns its headers and data.
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load CSV Marker Set' action cancelled by user.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return [], []

    debug_log(
        message=f"🛠️🟢 'Load CSV Marker Set' button clicked. Opening file: {file_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    console_log(f"Action: Load CSV Marker Set from {os.path.basename(file_path)}.")
    
    try:
        # Pass the desired headers to the converter for consistency
        headers, data = Marker_convert_csv_unknow_report_to_csv(file_path)

        if not data:
            console_log("❌ Failed to process CSV file or no data found.")
            return [], []

        debug_log(
            message=f"🔍🔵 Received Headers: {headers}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        debug_log(
            message=f"🔍🔵 Received first {min(len(data), 5)} data points: {data[:5]}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        
        debug_log(
            message="✅ CSV file loaded successfully.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        # Ensure we return canonical headers so the GUI knows what columns to show.
        return CANONICAL_HEADERS, data
    except Exception as e:
        debug_log(
            message=f"❌ Error loading CSV file: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"Error: Failed to process CSV file. {e}")
        return [], []

def maker_file_load_ias_html():
    # Opens a file dialog, loads an IAS HTML file, converts it, and returns the data.
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".html",
        filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load IAS HTML' action cancelled by user.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return [], []
        
    debug_log(
        message=f"🛠️🟢 'Load IAS HTML' button clicked. Opening file: {file_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    console_log(f"Action: Load IAS HTML from {os.path.basename(file_path)}.")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        headers, data = Marker_convert_IAShtml_report_to_csv(html_content)

        debug_log(
            message=f"🔍🔵 Received Headers: {headers}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        debug_log(
            message=f"🔍🔵 Received first {min(len(data), 5)} data points: {data[:5]}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )

        debug_log(
            message="✅ HTML report converted successfully.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return CANONICAL_HEADERS, data
    except Exception as e:
        debug_log(
            message=f"❌ Error converting HTML report: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"Error: Failed to convert HTML file. {e}")
        return [], []

def maker_file_load_wwb_shw():
    # Opens a file dialog, loads a WWB .shw file, converts it, and returns the data.
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".shw",
        filetypes=[("Shure Wireless Workbench files", "*.shw"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load WWB.shw' action cancelled by user.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return [], []
        
    debug_log(
        message=f"🛠️🟢 'Load WWB.shw' button clicked. Opening file: {file_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    console_log(f"Action: Load WWB.shw from {os.path.basename(file_path)}.")
    
    try:
        headers, data = Marker_convert_WWB_SHW_File_report_to_csv(file_path)

        debug_log(
            message=f"🔍🔵 Received Headers: {headers}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        debug_log(
            message=f"🔍🔵 Received first {min(len(data), 5)} data points: {data[:5]}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        
        debug_log(
            message="✅ SHW file converted successfully.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return CANONICAL_HEADERS, data
    except Exception as e:
        debug_log(
            message=f"❌ Error converting SHW file: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"Error: Failed to convert SHW file. {e}")
        return [], []

def maker_file_load_sb_pdf():
    # Opens a file dialog, loads a Soundbase PDF file, converts it, and returns the data.
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load SB PDF' action cancelled by user.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return [], []
        
    debug_log(
        message=f"🛠️🟢 'Load SB PDF' button clicked. Opening file: {file_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    console_log(f"Action: Load SB PDF from {os.path.basename(file_path)}.")

    try:
        headers, data = Marker_convert_SB_PDF_File_report_to_csv(file_path)

        debug_log(
            message=f"🔍🔵 Received Headers: {headers}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        debug_log(
            message=f"🔍🔵 Received first {min(len(data), 5)} data points: {data[:5]}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )

        debug_log(
            message="✅ PDF report converted successfully.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return CANONICAL_HEADERS, data
    except Exception as e:
        debug_log(
            message=f"❌ Error converting PDF report: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"Error: Failed to convert PDF file. {e}")
        return [], []
    
def maker_file_save_intermediate_file(tree_headers, tree_data):
    # Saves the current tree data to a file named 'MARKERS.csv' in the DATA directory at the project root level.
    current_function = inspect.currentframe().f_code.co_name
    # ANCHOR FIX: Use the stable project_root calculated above.
    target_path = project_root / 'DATA' / 'MARKERS.csv'
    
    debug_log(
        message=f"💾🟢 Saving data to intermediate file: {target_path}. Headers: {tree_headers}, first row: {tree_data[0] if tree_data else 'N/A'}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    
    try:
        with open(target_path, 'w', newline='') as csvfile:
            # Use DictWriter to ensure only rows that match the headers are written
            writer = csv.DictWriter(csvfile, fieldnames=CANONICAL_HEADERS) 
            
            # Use CANONICAL_HEADERS to ensure consistent output file
            writer.writeheader()
            writer.writerows(tree_data)
            
        console_log(f"Intermediate file saved as {target_path}")
    except Exception as e:
        console_log(f"Error: Failed to save intermediate MARKERS.csv file. {e}")
        
def maker_file_save_open_air_file(tree_headers, tree_data):
    # Saves the current tree data to a file named 'OpenAir.csv' in the DATA directory.
    current_function = inspect.currentframe().f_code.co_name
    
    if not tree_headers or not tree_data:
        debug_log(
            message="🛠️🟡 'Save Open Air' action aborted: no data in treeview.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log("Action: Save Markers as Open Air.csv. No data to save.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile="OpenAir.csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Save Open Air' action cancelled by user.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return

    debug_log(
        message=f"🛠️🟢 'Save Open Air' button clicked. Saving to: {file_path}",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )
    console_log(f"Action: Saving Markers as Open Air.csv to {os.path.basename(file_path)}.")
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=tree_headers)
            writer.writeheader()
            writer.writerows(tree_data)
        
        console_log(f"File saved successfully to {file_path}")
        debug_log(
            message="✅ File saved successfully.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
    except Exception as e:
        debug_log(
            message=f"❌ Error saving Open Air CSV file: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"Error: Failed to save file. {e}")
