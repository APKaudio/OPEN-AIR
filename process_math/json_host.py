# process_math/json_host.py
#
# This module provides a simple Flask-based JSON API to serve scan data
# from CSV files located in the 'scan_data' directory. It is designed
# to be queried by external applications, such as an Electron-based GUI.
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
# Version 20250802.0110.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0110.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 110 * 1 # Example hash, adjust as needed

import sys
import os
import csv
import inspect
from flask import Flask, jsonify, send_from_directory, request

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log # Added for console_print_func

# --- Path Configuration for Imports and Data Folder ---
# This block ensures that the project root is in sys.path, allowing imports
# from 'utils' or other top-level packages to resolve correctly,
# especially when this script is run directly.

# Get the directory of the current script (json_host.py)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to the project root.
# From process_math/json_host.py, it's two levels up:
# current_script_dir (process_math) -> parent (src) -> parent (project_root)
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    debug_log(f"Added project root to sys.path: {project_root}. Path configured!",
                file=__file__, version=current_version, function="sys_path_config")

# Now import the debug_log function correctly
# from utils.utils_instrument_control import debug_log # Old import
# from src.debug_logic import debug_log # Already imported above

# Define the base directory for scan data relative to the project root
SCAN_DATA_DIR = os.path.join(project_root, 'scan_data')
MARKERS_FILE = os.path.join(project_root, 'ref', 'MARKERS.CSV') # Path to MARKERS.CSV

app = Flask(__name__)

# --- Helper Functions ---

def _get_scan_files():
    """
    Function Description:
    Lists all CSV files in the SCAN_DATA_DIR.

    Inputs:
    - None.

    Process of this function:
    1. Checks if `SCAN_DATA_DIR` exists.
    2. If it exists, uses `os.listdir` to get all files.
    3. Filters for files ending with '.csv'.
    4. Logs the discovered files.

    Outputs of this function:
    - list: A list of CSV filenames found in `SCAN_DATA_DIR`.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Listing scan files in {SCAN_DATA_DIR}. Searching for data!",
                file=__file__, version=current_version, function=current_function)
    if not os.path.exists(SCAN_DATA_DIR):
        debug_log(f"Scan data directory not found: {SCAN_DATA_DIR}. No scans here!",
                    file=__file__, version=current_version, function=current_function)
        return []
    files = [f for f in os.listdir(SCAN_DATA_DIR) if f.endswith('.csv')]
    debug_log(f"Found {len(files)} CSV scan files. Files discovered!",
                file=__file__, version=current_version, function=current_function)
    return files

def _read_scan_data(filename):
    """
    Function Description:
    Reads data from a specified CSV scan file.

    Inputs:
    - filename (str): The name of the CSV file to read.

    Process of this function:
    1. Constructs the full path to the file.
    2. Opens and reads the CSV file.
    3. Parses each row into a dictionary with 'frequency_mhz' and 'power_dbm'.
    4. Logs the reading process.

    Outputs of this function:
    - list: A list of dictionaries, each representing a data point.
            Returns an empty list if the file is not found or an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    file_path = os.path.join(SCAN_DATA_DIR, filename)
    debug_log(f"Entering {current_function}. Reading scan data from: {file_path}. Loading data!",
                file=__file__, version=current_version, function=current_function)
    data = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Assuming the first row is header, skip it if necessary or handle it
            # For simplicity, assuming no header or handling it implicitly
            for i, row in enumerate(reader):
                if len(row) >= 2:
                    try:
                        freq = float(row[0])
                        power = float(row[1])
                        data.append({"frequency_mhz": freq, "power_dbm": power})
                    except ValueError:
                        debug_log(f"Skipping row {i+1} in {filename}: Non-numeric data found. Bad row!",
                                    file=__file__, version=current_version, function=current_function)
                        continue
        debug_log(f"Successfully read {len(data)} data points from {filename}. Data loaded!",
                    file=__file__, version=current_version, function=current_function)
    except FileNotFoundError:
        debug_log(f"File not found: {file_path}. Can't find it!",
                    file=__file__, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"Error reading {file_path}: {e}. File problem!",
                    file=__file__, version=current_version, function=current_function)
    return data

def _read_markers_data():
    """
    Function Description:
    Reads marker data from MARKERS.CSV.

    Inputs:
    - None.

    Process of this function:
    1. Checks if `MARKERS_FILE` exists.
    2. Opens and reads the CSV file, assuming a header row.
    3. Parses each row into a dictionary.
    4. Logs the reading process.

    Outputs of this function:
    - list: A list of dictionaries, each representing a marker.
            Returns an empty list if the file is not found or an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Reading markers data from: {MARKERS_FILE}. Loading markers!",
                file=__file__, version=current_version, function=current_function)
    markers = []
    if not os.path.exists(MARKERS_FILE):
        debug_log(f"Markers file not found: {MARKERS_FILE}. No markers here!",
                    file=__file__, version=current_version, function=current_function)
        return []
    try:
        with open(MARKERS_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert frequency to float, handle potential errors
                try:
                    row['Frequency'] = float(row['Frequency'])
                except (ValueError, KeyError):
                    row['Frequency'] = None # Or handle as appropriate
                    debug_log(f"Skipping marker row due to invalid frequency: {row}. Bad marker!",
                                file=__file__, version=current_version, function=current_function)
                    continue
                markers.append(row)
        debug_log(f"Successfully read {len(markers)} markers from {MARKERS_FILE}. Markers loaded!",
                    file=__file__, version=current_version, function=current_function)
    except Exception as e:
        debug_log(f"Error reading markers file {MARKERS_FILE}: {e}. Markers problem!",
                    file=__file__, version=current_version, function=current_function)
    return markers

# --- Flask API Endpoints ---

@app.route('/api/list_scans', methods=['GET'])
def list_scans():
    """
    Function Description:
    API endpoint to list all available scan CSV files.

    Inputs:
    - None. (Accessed via HTTP GET request)

    Process of this function:
    1. Calls `_get_scan_files` to retrieve the list of files.
    2. Returns the list as a JSON response.

    Outputs of this function:
    - flask.Response: JSON response containing the list of scan files.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"API endpoint '/api/list_scans' hit. Listing available scans! Version: {current_version}",
                file=__file__, version=current_version, function=current_function)
    scan_files = _get_scan_files()
    return jsonify(scan_files), 200

@app.route('/api/scan_data/<filename>', methods=['GET'])
def get_scan_data(filename):
    """
    Function Description:
    API endpoint to retrieve data for a specific scan CSV file.

    Inputs:
    - filename (str): The name of the CSV file requested in the URL.

    Process of this function:
    1. Calls `_read_scan_data` to get data for the specified file.
    2. If data is found, returns it as a JSON response.
    3. If no data (file not found or empty), returns a 404 error.

    Outputs of this function:
    - flask.Response: JSON response with scan data or an error message.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"API endpoint '/api/scan_data/<filename>' hit for filename: {filename}. Fetching scan data! Version: {current_version}",
                file=__file__, version=current_version, function=current_function)
    scan_data = _read_scan_data(filename)
    if scan_data:
        debug_log(f"Returning {len(scan_data)} data points for {filename}. Data sent!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify(scan_data), 200
    else:
        debug_log(f"No data found for {filename} or error reading file. File problem!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify({"error": "Scan data not found or an error occurred."}), 404

@app.route('/api/scan_in_progress_data', methods=['GET'])
def get_scan_in_progress_data():
    """
    Function Description:
    API endpoint to retrieve data for the currently active scan-in-progress file.
    This endpoint is designed to serve the latest data from a specific, known file
    that the main application is actively writing to.

    Inputs:
    - None. (Accessed via HTTP GET request)

    Process of this function:
    1. Retrieves the `current_scan_file_path` from Flask's `request.args` (or a global/app context).
       NOTE: In a real application, `current_scan_file_path` would be managed by the main app
       and passed/shared securely, e.g., via a shared memory segment or a more robust IPC.
       For this Flask app, we'll assume it's passed as a query parameter for demonstration.
       Alternatively, it could be a hardcoded path if only one scan-in-progress file exists.
    2. If a path is provided, reads data from that file.
    3. Returns the data as a JSON response or a 404 if not found/error.

    Outputs of this function:
    - flask.Response: JSON response with scan-in-progress data or an error message.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"API endpoint '/api/scan_in_progress_data' hit. Fetching live scan data! Version: {current_version}",
                file=__file__, version=current_version, function=current_function)
    
    # In a real scenario, this path would be dynamically set by the main app
    # For now, let's assume the main app passes it as a query parameter or it's a known fixed file.
    # Example: /api/scan_in_progress_data?path=/path/to/live_scan.csv
    current_scan_file_path = request.args.get('path')
    
    if not current_scan_file_path:
        # Fallback to a common or expected live scan file if no path is provided
        # This assumes the main app writes to a predictable location for live updates
        # For instance, the last created scan file in SCAN_DATA_DIR.
        # This is a simplification; a more robust solution would involve explicit IPC.
        all_scans = _get_scan_files()
        if all_scans:
            # Sort by modification time to get the most recent file
            all_scans.sort(key=lambda f: os.path.getmtime(os.path.join(SCAN_DATA_DIR, f)), reverse=True)
            current_scan_file_path = os.path.join(SCAN_DATA_DIR, all_scans[0])
            debug_log(f"No explicit path provided for scan_in_progress_data. Using most recent scan file: {current_scan_file_path}. Assuming live file!",
                        file=__file__, version=current_version, function=current_function)
        else:
            debug_log("No current_scan_file_path provided and no scan files found. Cannot provide scan in progress data!",
                        file=__file__, version=current_version, function=current_function)
            return jsonify({"error": "No scan in progress file specified or found."}), 400

    debug_log(f"Attempting to read scan in progress data from: {current_scan_file_path}.",
                file=__file__, version=current_version, function=current_function)
    
    # Read data directly from the specified path
    data = []
    try:
        with open(current_scan_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if len(row) >= 2:
                    try:
                        freq = float(row[0])
                        power = float(row[1])
                        data.append({"frequency_mhz": freq, "power_dbm": power})
                    except ValueError:
                        debug_log(f"Skipping row {i+1} in {current_scan_file_path}: Non-numeric data found. Bad row!",
                                    file=__file__, version=current_version, function=current_function)
                        continue
        debug_log(f"Successfully read {len(data)} data points from scan in progress file. Live data loaded!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify(data), 200
    except FileNotFoundError:
        debug_log(f"Scan in progress file not found: {current_scan_file_path}. Can't find it!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify({"error": "Scan in progress data not found."}), 404
    except Exception as e:
        debug_log(f"Error reading scan in progress file {current_scan_file_path}: {e}. File problem!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify({"error": f"Error reading scan in progress data: {e}"}), 500


@app.route('/api/markers_data', methods=['GET'])
def get_markers_data():
    """
    Function Description:
    API endpoint to retrieve marker data from MARKERS.CSV.

    Inputs:
    - None. (Accessed via HTTP GET request)

    Process of this function:
    1. Calls `_read_markers_data` to get marker data.
    2. If data is found, returns it as a JSON response.
    3. If no data (file not found or empty), returns a 404 error.

    Outputs of this function:
    - flask.Response: JSON response with marker data or an error message.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"API endpoint '/api/markers_data' hit. Request for markers data! Version: {current_version}",
                file=__file__, version=current_version, function=current_function)
    
    markers_data = _read_markers_data()
    if markers_data:
        debug_log(f"Returning {len(markers_data)} markers. Data sent!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify(markers_data), 200
    else:
        debug_log("No markers data found or error reading markers file. Markers problem!",
                    file=__file__, version=current_version, function=current_function)
        return jsonify({"error": "No markers data found or an error occurred."}), 404


@app.route('/')
def index():
    """
    Function Description:
    Basic endpoint to confirm the API is running.

    Inputs:
    - None. (Accessed via HTTP GET request)

    Process of this function:
    1. Returns a simple string message.

    Outputs of this function:
    - str: A confirmation message.
    """
    return "Scan Data API is running. Use /api/scan_data/<filename> to get data or /api/list_scans to list files."

# --- Running the Flask Application ---
if __name__ == '__main__':
    # This block allows you to run the Flask application directly for testing.
    # In a real Electron application, you would typically start this Python script
    # as a subprocess and communicate with it (e.g., using child_process in Node.js).
    
    # For development, set debug=True to enable Flask's debugger and auto-reloader.
    # For production deployment, always set debug=False for security and performance.
    debug_log(f"Starting JSON API server from {current_script_dir}. Version: {current_version}",
                file=__file__, version=current_version, function="main")
    debug_log(f"Serving files from SCAN_DATA_DIR: {SCAN_DATA_DIR}. Data source set!",
                file=__file__, version=current_version, function="main")
    debug_log(f"Serving markers from MARKERS_FILE: {MARKERS_FILE}. Marker source set!",
                file=__file__, version=current_version, function="main")
    
    # You might want to make the host configurable (e.g., '0.0.0.0' for external access)
    # and the port configurable.
    app.run(host='127.0.0.1', port=5000, debug=False) # Set debug=False for production
