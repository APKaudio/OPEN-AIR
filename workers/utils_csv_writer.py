# csv_utils.py
#
# This module provides utility functions for writing spectrum scan data to CSV files.
# It encapsulates the logic for handling file paths, directory creation, and data formatting
# for CSV output, ensuring consistent data storage for analysis and historical tracking.
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
# Version 20250810.134500.1 (FIXED: Added app_instance_ref parameter and wrapped console calls with after() to prevent GIL errors.)

current_version = "20250810.134500.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250810 * 134500 * 1 # Example hash, adjust as needed

import csv
import os
import inspect # Import inspect module

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

def write_scan_data_to_csv(file_path, header, data, app_instance_ref, append_mode=False, console_print_func=None):
    """
    Writes scan data to a CSV file. This function is designed to write raw frequency
    and amplitude data collected from the spectrum analyzer. It handles creating
    the necessary directory structure if it doesn't exist and conditionally writes
    the header.

    Inputs:
        file_path (str): The full path to the CSV file where the data will be written.
        header (list or None): A list of strings representing the CSV header row.
                               If None, no header will be written.
        data (list): A list of lists or tuples, where each inner list/tuple represents
                     a row of data (e.g., [frequency_mhz, level_dbm]).
        app_instance_ref (object): A reference to the main application instance.
        append_mode (bool): If True, data will be appended to the file if it exists.
                            If False, the file will be overwritten.
        console_print_func (function, optional): Function to use for console output.
                                                  Defaults to console_log if None.
    Raises:
        IOError: If there is an issue writing to the file.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to write scan data to CSV: {file_path}, append_mode={append_mode}. Let's save this data!",
                file=__file__,
                version=current_version,
                function=current_function)

    # Ensure the directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            debug_log(f"Created directory: {output_dir}. Path cleared!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except OSError as e:
            error_msg = f"❌ Error creating directory '{output_dir}': {e}. This is a disaster!"
            # WRAPPED WITH after() to prevent cross-thread access
            app_instance_ref.after(0, lambda: console_print_func(error_msg))
            debug_log(error_msg,
                        file=__file__,
                        version=current_version,
                        function=current_function)
            raise IOError(f"Failed to create directory {output_dir}") from e

    try:
        # Determine the mode and if header needs to be written
        file_exists = os.path.exists(file_path)
        
        # If not in append_mode, or if in append_mode but file doesn't exist, open in write mode.
        # Otherwise, open in append mode.
        mode = 'a' if append_mode and file_exists else 'w'
        
        # Flag to indicate if header needs to be written
        # Write header ONLY if header is not None and we are creating a new file or overwriting
        write_header = (header is not None) and (mode == 'w')

        with open(file_path, mode, newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            if write_header:
                csv_writer.writerow(header)
                debug_log(f"Wrote header to CSV file: {file_path}. Header added!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            
            # Write data rows
            for freq_mhz, level_dbm in data:
                csv_writer.writerow([f"{freq_mhz:.3f}", f"{level_dbm:.3f}"])
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func(f"✅ Scan data written to CSV: {file_path}. Data saved!"))
        debug_log(f"Scan data written to CSV: {file_path}. Mission accomplished!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    except IOError as e:
        error_msg = f"❌ I/O Error writing to CSV file {file_path}: {e}. This is a disaster!"
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to allow higher-level error handling
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while writing to CSV file {file_path}: {e}. What a mess!"
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func(error_msg))
        debug_log(error_msg,
                    file=__file__,
                    version=current_version,
                    function=current_function)
        raise # Re-raise to allow higher-level error handling
