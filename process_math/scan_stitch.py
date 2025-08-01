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
#
import pandas as pd
import inspect

# Import debug_print from utils
from utils.utils_instrument_control import debug_print
from ref.frequency_bands import MHZ_TO_HZ # Import for frequency conversion

def process_and_stitch_scan_data(raw_data, overall_start_freq_hz, overall_stop_freq_hz, console_print_func=None):
    """
    Processes raw scan data (frequency and amplitude pairs) collected from multiple
    segments/bands to remove duplicates, sort by frequency, and ensure a contiguous range.
    This function is responsible for stitching together the individual scan segments.

    Inputs:
        raw_data (list): A list of (frequency_hz, amplitude_dbm) tuples collected
                         across all scan segments.
        overall_start_freq_hz (float): The absolute start frequency (in Hz) of the
                                       entire desired scan range.
        overall_stop_freq_hz (float): The absolute stop frequency (in Hz) of the
                                      entire desired scan range.
        console_print_func (function, optional): Function to use for console output.

    Returns:
        pandas.DataFrame: A DataFrame with 'Frequency (MHz)' and 'Amplitude (dBm)'
                          columns, representing the stitched and processed scan data.
                          Returns an empty DataFrame if no valid data is provided.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function} function. Processing {len(raw_data)} points.", file=current_file, function=current_function, console_print_func=console_print_func)

    if not raw_data:
        if console_print_func:
            console_print_func("ℹ️ No raw data provided for stitching.")
        debug_print("No raw data to process and stitch.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} function. Result: Empty DataFrame", file=current_file, function=current_function, console_print_func=console_print_func)
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(raw_data, columns=['Frequency (Hz)', 'Amplitude (dBm)'])

    # Remove duplicates based on Frequency (keeping the last one which is often from the end of a segment)
    # This is crucial for stitching overlapping segments
    initial_rows = df.shape[0]
    df.drop_duplicates(subset=['Frequency (Hz)'], keep='last', inplace=True)
    if console_print_func and initial_rows > df.shape[0]:
        console_print_func(f"🧹 Removed {initial_rows - df.shape[0]} duplicate frequency points.")
    debug_print(f"Removed duplicates. New shape: {df.shape}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Sort by frequency to ensure a continuous trace
    df.sort_values(by='Frequency (Hz)', inplace=True)
    debug_print("Data sorted by frequency.", file=current_file, function=current_function, console_print_func=console_print_func)

    # Filter to the overall scan range to remove any stray points outside
    # This ensures the final data matches the requested scan boundaries
    df = df[(df['Frequency (Hz)'] >= overall_start_freq_hz) & (df['Frequency (Hz)'] <= overall_stop_freq_hz)]
    if console_print_func:
        console_print_func(f"✂️ Filtered data to overall range: {overall_start_freq_hz/MHZ_TO_HZ:.3f} MHz to {overall_stop_freq_hz/MHZ_TO_HZ:.3f} MHz.")
    debug_print(f"Filtered to overall range. New shape: {df.shape}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Convert Frequency to MHz for consistency in output/plotting
    df['Frequency (MHz)'] = df['Frequency (Hz)'] / MHZ_TO_HZ
    
    # Reorder columns to have MHz first
    df = df[['Frequency (MHz)', 'Amplitude (dBm)']]

    if console_print_func:
        console_print_func(f"✅ Stitched and processed {df.shape[0]} data points.")
    debug_print(f"Processed data shape: {df.shape}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function} function. Result: DataFrame with {df.shape[0]} rows.", file=current_file, function=current_function, console_print_func=console_print_func)
    return df

