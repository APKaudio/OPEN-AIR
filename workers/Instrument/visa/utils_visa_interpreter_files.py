# utils/utils_visa_interpreter_files.py
#
# This file contains all the core logic for handling file I/O operations related to the
# VISA Interpreter Tab. This includes creating the default data file if it doesn't exist,
# loading the data from the file, and saving the data back to it. This module ensures
# that the file handling is a separate, modular concern, as per project standards.
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
# Version 20250821.175500.1
# UPDATED: This file now uses the definitive source of truth for default commands,
#          `ref_visa_commands.py`, and correctly handles the full 7-column data structure.

import os
import csv
import inspect
from datetime import datetime

from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.ref_file_paths import VISA_COMMANDS_FILE_PATH, DATA_FOLDER_PATH
from .ref_visa_commands import get_default_visa_commands

# --- Versioning ---
w = 20250821
x_str = '175500'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"{w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = f"{os.path.basename(__file__)}"


def create_default_data_file(data_file):
    """
    Creates a new CSV file with default VISA command entries from the ref file.

    Inputs:
        data_file (str): The full path to the data file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Creating default VISA commands CSV file at '{data_file}'. 📝",
                file=current_file,
                version=current_version,
                function=current_function)
    
    # Use the definitive source of truth for headers and data
    default_headers = ["Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated"]
    default_data = get_default_visa_commands()

    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    with open(data_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(default_headers)
        writer.writerows(default_data)
    console_log(f"✅ Created new default file: {os.path.basename(data_file)}")
    debug_log("Default VISA commands CSV created.",
                file=current_file,
                version=current_version,
                function=current_function)

def load_visa_commands_data(data_file):
    """
    Loads data from the CSV file into a list of lists.
    This function is designed to handle the 7-column data from the `ref` file.

    Inputs:
        data_file (str): The full path to the data file.

    Outputs:
        list: A list of lists representing the CSV data.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Loading data from CSV... 💾",
                file=current_file,
                version=current_version,
                function=current_function)
    
    data = []
    try:
        with open(data_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                # Ensure the data has the correct number of columns
                if len(row) == 7:
                    data.append(row)
                else:
                    debug_log(f"⚠️ Row has incorrect number of columns: {row}. Skipping.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
        console_log(f"✅ Loaded {len(data)} entries from {os.path.basename(data_file)}.")
        debug_log(f"Loaded {len(data)} entries from CSV.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return data
    except FileNotFoundError:
        console_log(f"❌ Error: {os.path.basename(data_file)} not found. This is a disaster!")
        debug_log("CSV file not found during load.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return []
    except Exception as e:
        console_log(f"❌ Error loading data: {e}. This is a disaster!")
        debug_log(f"Error loading CSV data: {e}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        return []

def save_visa_commands_data(data_file, data):
    """
    Saves the provided data to the CSV file.
    This function is designed to handle the 7-column data.

    Inputs:
        data_file (str): The full path to the data file.
        data (list): A list of lists containing the data to save.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Saving data to CSV file. Committing the changes to memory! 💾",
                file=current_file,
                version=current_version,
                function=current_function)
    
    headers = ["Manufacturer", "Model", "Command Type", "Action", "VISA Command", "Variable", "Validated"]
    try:
        with open(data_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        console_log(f"✅ Saved data to {os.path.basename(data_file)} successfully.")
        debug_log("Data saved successfully.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
    except Exception as e:
        console_log(f"❌ Error saving data: {e}. Oh no, the data is lost!")
        debug_log(f"Error saving data to CSV: {e}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

def initialize_data_file_and_load():
    """
    Ensures the VISA commands CSV file exists, populates it if it doesn't,
    and then loads its content.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Initializing data file and loading content... 💾",
                file=current_file,
                version=current_version,
                function=current_function)
    
    data_file_path = VISA_COMMANDS_FILE_PATH
    
    if not os.path.exists(data_file_path):
        console_log(f"ℹ️ {os.path.basename(data_file_path)} not found. Creating a new file with default entries.")
        debug_log(f"File '{os.path.basename(data_file_path)}' not found. Creating new file with defaults.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        create_default_data_file(data_file_path)
    
    data = load_visa_commands_data(data_file_path)
    debug_log("Data file check and load completed. Ready to go! ✅",
                file=current_file,
                version=current_version,
                function=current_function)
    return data