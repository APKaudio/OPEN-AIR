# src/scan_stitch.py
#
# This module handles the processing, de-duplication, and stitching of raw scan data
# collected from multiple segments or bands into a single, coherent DataFrame.
# It ensures data integrity and prepares the final dataset for plotting and analysis.
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
# Version 20250802.0125.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0125.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 125 * 1 # Example hash, adjust as needed

import pandas as pd
import inspect
import os # Added for path manipulation
from datetime import datetime # Added for timestamping
import csv # Added for writing CSV

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

from ref.frequency_bands import MHZ_TO_HZ # Import for frequency conversion


def process_and_stitch_scan_data(raw_data, overall_start_freq_hz, overall_stop_freq_hz, console_print_func=None):
    """
    Function Description:
    Processes raw scan data (frequency and amplitude pairs) collected from multiple
    segments/bands to remove duplicates, sort by frequency, and ensure a contiguous range.
    This function is responsible for stitching together the individual scan segments.

    Inputs:
        raw_data (list): A list of (frequency_hz, amplitude_dbm) tuples collected
                         across all scan segments.
        overall_start_freq_hz (float): The absolute start frequency (in Hz) of the entire scan.
        overall_stop_freq_hz (float): The absolute stop frequency (in Hz) of the entire scan.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. Defaults to console_log if None.

    Returns:
        pandas.DataFrame: A DataFrame with 'Frequency (MHz)' and 'Amplitude (dBm)' columns,
                          containing the stitched, de-duplicated, and sorted scan data.
                          Returns an empty DataFrame if no valid data is provided.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Stitching raw scan data. Let's make this coherent! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Raw data points received: {len(raw_data) if raw_data else 0}. Overall range: {overall_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz/MHZ_TO_HZ:.3f} MHz. Processing!",
                file=current_file, version=current_version, function=current_function)

    if not raw_data:
        console_print_func("⚠️ No raw scan data provided to stitch. Returning empty DataFrame. Nothing to do!")
        debug_log("No raw data provided for stitching. Returning empty DataFrame.",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (no raw data). Stitching aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return pd.DataFrame(columns=['Frequency (MHz)', 'Amplitude (dBm)'])

    df = pd.DataFrame(raw_data, columns=['Frequency (Hz)', 'Amplitude (dBm)'])
    debug_log(f"Initial DataFrame created. Shape: {df.shape}. Data loaded!",
                file=current_file, version=current_version, function=current_function)

    # Remove duplicates based on frequency, keeping the first occurrence
    initial_rows = df.shape[0]
    df.drop_duplicates(subset=['Frequency (Hz)'], keep='first', inplace=True)
    rows_removed = initial_rows - df.shape[0]
    if rows_removed > 0:
        console_print_func(f"✂️ Removed {rows_removed} duplicate frequency points. Cleaning up!")
        debug_log(f"Removed {rows_removed} duplicate frequency points. DataFrame now has {df.shape[0]} unique points.",
                    file=current_file, version=current_version, function=current_function)
    else:
        debug_log("No duplicate frequency points found. Data is pristine!",
                    file=current_file, version=current_version, function=current_function)

    # Sort by frequency to ensure a continuous trace
    df.sort_values(by='Frequency (Hz)', inplace=True)
    debug_log("Data sorted by frequency. Trace ordered!",
                file=current_file, version=current_version, function=current_function)

    # Filter to the overall scan range to remove any stray points outside
    # This ensures the final data matches the requested scan boundaries
    df = df[(df['Frequency (Hz)'] >= overall_start_freq_hz) & (df['Frequency (Hz)'] <= overall_stop_freq_hz)]
    if console_print_func:
        console_print_func(f"✂️ Filtered data to overall range: {overall_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz/MHZ_TO_HZ:.3f} MHz. Trimmed to perfection!")
    debug_log(f"Filtered to overall range. New shape: {df.shape}. Data constrained!",
                file=current_file, version=current_version, function=current_function)

    # Convert Frequency to MHz for consistency in output/plotting
    df['Frequency (MHz)'] = df['Frequency (Hz)'] / MHZ_TO_HZ
    
    # Reorder columns to have MHz first
    df = df[['Frequency (MHz)', 'Amplitude (dBm)']]

    if console_print_func:
        console_print_func(f"✅ Stitched and processed {df.shape[0]} data points. All done!")
    debug_log(f"Processed data shape: {df.shape}. Stitching complete!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Scan data stitched successfully! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return df


def stitch_and_save_scan_data(
    raw_scan_data_for_current_sweep,
    output_folder,
    scan_name,
    operator_name,
    venue_name,
    equipment_used,
    notes,
    postal_code,
    latitude,
    longitude,
    antenna_type,
    antenna_amplifier,
    console_print_func=None
):
    """
    Function Description:
    Stitches the raw scan data, adds metadata, and saves it to a CSV file
    within a timestamped subfolder.

    Inputs:
        raw_scan_data_for_current_sweep (list): List of (frequency_hz, amplitude_dbm) tuples.
        output_folder (str): Base directory for saving scan data.
        scan_name (str): Name of the scan.
        operator_name (str): Name of the operator.
        venue_name (str): Name of the venue.
        equipment_used (str): Description of equipment used.
        notes (str): General notes for the scan.
        postal_code (str): Postal code of the scan location.
        latitude (float/str): Latitude of the scan location.
        longitude (float/str): Longitude of the scan location.
        antenna_type (str): Type of antenna used.
        antenna_amplifier (str): Type of antenna amplifier used.
        console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Returns:
        tuple: (pandas.DataFrame, str) - The stitched DataFrame and the full path to the saved CSV file.
               Returns (None, None) if an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Preparing to stitch and save scan data. This is the grand finale! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)

    if not raw_scan_data_for_current_sweep:
        console_print_func("⚠️ No raw scan data available to stitch and save. Nothing to write!")
        debug_log("No raw scan data for current sweep. Cannot stitch and save.",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # Determine overall start and stop frequencies for stitching
    overall_start_freq_hz = min(f for f, _ in raw_scan_data_for_current_sweep)
    overall_stop_freq_hz = max(f for f, _ in raw_scan_data_for_current_sweep)
    debug_log(f"Determined overall scan range: {overall_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz/MHZ_TO_HZ:.3f} MHz.",
                file=current_file, version=current_version, function=current_function)

    # Process and stitch the raw data
    stitched_df = process_and_stitch_scan_data(
        raw_scan_data_for_current_sweep,
        overall_start_freq_hz,
        overall_stop_freq_hz,
        console_print_func
    )

    if stitched_df.empty:
        console_print_func("❌ Stitched DataFrame is empty after processing. Cannot save. Data vanished!")
        debug_log("Stitched DataFrame is empty. Cannot save.",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # Create a timestamped subfolder for this scan
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    scan_subfolder_name = f"{scan_name.replace(' ', '_')}_{timestamp_str}"
    full_output_dir = os.path.join(output_folder, scan_subfolder_name)

    try:
        os.makedirs(full_output_dir, exist_ok=True)
        console_print_func(f"Created scan output folder: {full_output_dir}.")
        debug_log(f"Created scan output folder: {full_output_dir}. Folder ready!",
                    file=current_file, version=current_version, function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error creating output folder '{full_output_dir}': {e}. This is a disaster!")
        debug_log(f"Error creating output folder: {e}. Folder creation failed!",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # Define the CSV file path
    csv_file_name = f"{scan_name.replace(' ', '_')}_Scan_{timestamp_str}.csv"
    output_file_path = os.path.join(full_output_dir, csv_file_name)

    # Prepare metadata for the header
    metadata = [
        f"Scan Name: {scan_name}",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Operator: {operator_name}",
        f"Venue: {venue_name}",
        f"Equipment Used: {equipment_used}",
        f"Antenna Type: {antenna_type}",
        f"Antenna Amplifier: {antenna_amplifier}",
        f"Postal Code: {postal_code}",
        f"Latitude: {latitude}",
        f"Longitude: {longitude}",
        f"Notes: {notes.replace('\n', ' ')}" # Replace newlines for single-line CSV header
    ]
    debug_log(f"Metadata prepared for CSV header. Ready to write!",
                file=current_file, version=current_version, function=current_function)

    # Write to CSV
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for item in metadata:
                writer.writerow([f"# {item}"]) # Comment out metadata lines
            writer.writerow([]) # Empty row for separation
            
            # Write column headers for data
            writer.writerow(stitched_df.columns.tolist())
            
            # Write data rows
            for index, row in stitched_df.iterrows():
                writer.writerow([f"{row['Frequency (MHz)']:.3f}", f"{row['Amplitude (dBm)']:.3f}"])
        
        console_print_func(f"✅ Scan data and metadata saved to: {output_file_path}. All done!")
        debug_log(f"Scan data and metadata saved to: {output_file_path}. File exported!",
                    file=current_file, version=current_version, function=current_function)
        return stitched_df, output_file_path
    except Exception as e:
        console_print_func(f"❌ Error saving stitched scan data to CSV: {e}. This is a disaster!")
        debug_log(f"Error saving stitched scan data to CSV: {e}. Save failed!",
                    file=current_file, version=current_version, function=current_function)
        return None, None