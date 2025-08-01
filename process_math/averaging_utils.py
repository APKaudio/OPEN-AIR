# averaging_utils.py
#
# This module provides utility functions for processing and analyzing collected
# spectrum analyzer data. It includes functionalities for calculating various
# statistical measures such as average, median, range, standard deviation,
# variance, and power spectral density (PSD) from multiple scan cycles.
# It is crucial for generating insightful plots and CSV reports from the raw scan data.
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
import numpy as np # Ensure numpy is imported for std, var, and log10
import os
import csv
from datetime import datetime
import re
import platform # For opening folder cross-platform

# Import plotting functions and constants
from tabs.Plotting.utils_plotting import plot_multi_trace_data, _open_plot_in_browser
from ref.frequency_bands import (
    MHZ_TO_HZ,
    TV_PLOT_BAND_MARKERS,
    GOV_PLOT_BAND_MARKERS
)
from utils.utils_instrument_control import debug_print # Import debug_print
import inspect # Import inspect module

# --- Helper Functions for Calculations and Folder Management ---

def _create_output_subfolder(base_output_dir, prefix, timestamp_str, console_print_func):
    """
    Creates a new subfolder for scan outputs based on a prefix and timestamp.

    Inputs:
        base_output_dir (str): The base directory where the subfolder will be created.
        prefix (str): A descriptive prefix for the subfolder name (e.g., scan name, group name).
        timestamp_str (str): A timestamp string (e.g., YYYYMMDD_HHMMSS) for uniqueness.
        console_print_func (function): Function to print messages to the GUI console.

    Returns:
        str: The full path to the newly created subfolder.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)

    subfolder_name = f"{prefix}_{timestamp_str}"
    output_dir_full = os.path.join(base_output_dir, subfolder_name)
    os.makedirs(output_dir_full, exist_ok=True)
    console_print_func(f"Created output subfolder: {output_dir_full}")
    debug_print(f"Created output subfolder: {output_dir_full}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return output_dir_full

def _calculate_average(power_levels_df, console_print_func):
    """Calculates the average power levels across all traces."""
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    average_levels = power_levels_df.mean(axis=1)
    debug_print(f"Calculated Average. First 5 values: {average_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return average_levels

def _calculate_median(power_levels_df, console_print_func):
    """Calculates the median power levels across all traces."""
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    median_levels = power_levels_df.median(axis=1)
    debug_print(f"Calculated Median. First 5 values: {median_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return median_levels

def _calculate_range(power_levels_df, console_print_func):
    """Calculates the range (max - min) of power levels across all traces."""
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    range_levels = power_levels_df.max(axis=1) - power_levels_df.min(axis=1)
    debug_print(f"Calculated Range. First 5 values: {range_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return range_levels

def _calculate_std_dev(power_levels_df, console_print_func):
    """Calculates the standard deviation of power levels across all traces."""
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    std_dev_levels = power_levels_df.std(axis=1)
    debug_print(f"Calculated Std Dev. First 5 values: {std_dev_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return std_dev_levels

def _calculate_variance(power_levels_df, console_print_func):
    """Calculates the variance of power levels across all traces."""
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    variance_levels = power_levels_df.var(axis=1)
    debug_print(f"Calculated Variance. First 5 values: {variance_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return variance_levels

def _calculate_psd(power_levels_df, rbw_values, console_print_func):
    """
    Calculates the Power Spectral Density (PSD) from power levels and RBW values.
    If multiple traces, calculates PSD for each then averages.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    
    psd_levels = pd.Series([np.nan] * len(power_levels_df.index), index=power_levels_df.index) # Initialize with NaN

    if not rbw_values or all(rbw is None or rbw <= 0 for rbw in rbw_values):
        console_print_func("Warning: Resolution Bandwidth (RBW) not provided or invalid for PSD calculation. PSD will be NaN.")
        debug_print("RBW missing or invalid for PSD calculation.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (invalid RBW)", file=current_file, function=current_function, console_print_func=console_print_func)
        return psd_levels

    linear_power_mW_traces = 10**(power_levels_df / 10)
    psd_traces = []
    
    # Ensure rbw_values matches the number of columns in power_levels_df
    if len(rbw_values) != power_levels_df.shape[1]:
        console_print_func(f"Warning: Number of RBW values ({len(rbw_values)}) does not match number of power traces ({power_levels_df.shape[1]}). Using first RBW for all traces for PSD calculation.")
        debug_print(f"RBW count mismatch. Using first RBW for all traces.", file=current_file, function=current_function, console_print_func=console_print_func)
        # Fallback to using the first valid RBW for all traces if mismatch
        valid_rbw = next((rbw for rbw in rbw_values if rbw is not None and rbw > 0), None)
        if valid_rbw:
            rbw_values = [valid_rbw] * power_levels_df.shape[1]
        else:
            console_print_func("Error: No valid RBW found for PSD calculation. PSD will be NaN.")
            debug_print("No valid RBW found for PSD.", file=current_file, function=current_function, console_print_func=console_print_func)
            return psd_levels
    
    # Ensure all RBW values are valid before proceeding
    if any(rbw is None or rbw <= 0 for rbw in rbw_values):
        console_print_func("Error: One or more RBW values are invalid for PSD calculation. PSD will be NaN.")
        debug_print("Invalid RBW values detected during PSD calculation.", file=current_file, function=current_function, console_print_func=console_print_func)
        return psd_levels


    for i, col in enumerate(power_levels_df.columns):
        rbw = rbw_values[i]
        psd_trace = 10 * np.log10(linear_power_mW_traces[col] / rbw)
        psd_traces.append(psd_trace)
        debug_print(f"Calculated PSD for trace {i+1} with RBW {rbw}.", file=current_file, function=current_function, console_print_func=console_print_func)

    if psd_traces:
        combined_psd_df = pd.concat(psd_traces, axis=1)
        psd_levels = combined_psd_df.mean(axis=1)
        debug_print(f"Calculated multi-trace averaged PSD. First 5 values: {psd_levels.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    else:
        console_print_func("No valid PSD data could be calculated for any trace. PSD column will be NaN.")
        debug_print("No valid PSD data for multi-trace average.", file=current_file, function=current_function, console_print_func=console_print_func)

    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return psd_levels


def average_scan(
    file_paths,
    selected_avg_types,
    plot_title_prefix,
    output_html_path_base,
    console_print_func
):
    """
    Performs averaging and statistical calculations on a list of scan files
    and saves the results to separate CSV files in a new subfolder.

    Inputs:
        file_paths (list): A list of full paths to the CSV scan files.
        selected_avg_types (list): A list of strings indicating which average types to calculate
                                   (e.g., ["Average", "Median", "PSD (dBm/Hz)"]).
        plot_title_prefix (str): A prefix for the output folder and file names (e.g., "MyScan").
        output_html_path_base (str): The base directory where the new subfolder will be created.
        console_print_func (function): Function to print messages to the GUI console.

    Returns:
        str: The full path to the newly created output subfolder, or None if an error occurs.
        pandas.DataFrame: The aggregated DataFrame, or None if an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input file_paths ({len(file_paths)} files): {file_paths}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input selected_avg_types: {selected_avg_types}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input output_html_path_base: {output_html_path_base}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not file_paths:
        console_print_func("No file paths provided for averaging.")
        debug_print("No file paths provided for averaging.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (no file paths)", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # --- Create a new subfolder for this multi-file averaged plot's outputs ---
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir_full = _create_output_subfolder(
        output_html_path_base,
        f"{plot_title_prefix}_AppliedMath", # Prefix for applied math folder
        timestamp_str, # Timestamp for subfolder
        console_print_func
    )
    debug_print(f"Output subfolder created for applied math: {output_dir_full}", file=current_file, function=current_function, console_print_func=console_print_func)

    all_scans_dfs = []
    # Regex to extract RBW and Offset from filename for PSD calculation and frequency normalization
    filename_pattern = re.compile(
        r'.*_RBW(?P<rbw_val>\d+K?)_HOLD\d+_(?:Offset(?P<offset_val>-?\d+))?_(?P<date_time>\d{8}_\d{6})\.csv$'
    )

    all_frequencies = pd.Series(dtype=float) # To collect all unique frequencies for the master reference

    for df_idx, f_path in enumerate(file_paths):
        debug_print(f"Processing file {df_idx+1}/{len(file_paths)}: {os.path.basename(f_path)}", file=current_file, function=current_function, console_print_func=console_print_func)
        try:
            df = pd.read_csv(f_path, header=None)
            
            if df.shape[1] < 2:
                console_print_func(f"Skipping {os.path.basename(f_path)}: CSV does not contain at least two columns (Frequency, Power). Found {df.shape[1]} columns.")
                debug_print(f"Skipping {os.path.basename(f_path)}: Insufficient columns in CSV.", file=current_file, function=current_function, console_print_func=console_print_func)
                continue

            df.columns = ['Frequency (Hz)', 'Power (dBm)']
            debug_print(f"Successfully read CSV: {os.path.basename(f_path)} with implied columns: {df.columns.tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
            
            df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
            df['Power (dBm)'] = pd.to_numeric(df['Power (dBm)'], errors='coerce') # Ensure power is numeric
            df.dropna(subset=['Frequency (Hz)', 'Power (dBm)'], inplace=True) # Drop rows with NaN in either
            df.drop_duplicates(subset=['Frequency (Hz)'], keep='first', inplace=True)

            if df.empty:
                console_print_func(f"Warning: File {os.path.basename(f_path)} became empty after cleaning non-numeric or duplicate data. Skipping.")
                debug_print(f"File {os.path.basename(f_path)} empty after data cleanup.", file=current_file, function=current_function, console_print_func=console_print_func)
                continue

            file_name = os.path.basename(f_path)
            match = filename_pattern.match(file_name)
            debug_print(f"Regex match result for '{file_name}': {match}", file=current_file, function=current_function, console_print_func=console_print_func)
            
            rbw_hz = None
            current_offset_hz = 0.0

            if match:
                rbw_str = match.group('rbw_val')
                if 'K' in rbw_str:
                    rbw_hz = float(rbw_str.replace('K', '')) * 1000
                else:
                    rbw_hz = float(rbw_str)

                offset_str = match.group('offset_val')
                if offset_str:
                    current_offset_hz = float(offset_str)

                df['Frequency (Hz)'] = df['Frequency (Hz)'] - current_offset_hz
                debug_print(f"File {file_name}: Extracted RBW={rbw_hz}, Offset={current_offset_hz}. Frequency normalized.", file=current_file, function=current_function, console_print_func=console_print_func)
            else:
                debug_print(f"File {file_name}: Filename pattern mismatch. RBW and Offset not extracted. Assuming no offset and default RBW for PSD.", file=current_file, function=current_function, console_print_func=console_print_func)
                console_print_func(f"Warning: Filename '{file_name}' did not match expected pattern for RBW/Offset. PSD calculation might be inaccurate.")

            df['RBW_Hz'] = rbw_hz # Add RBW to the dataframe for later PSD calculation
            all_scans_dfs.append(df)
            all_frequencies = pd.concat([all_frequencies, df['Frequency (Hz)']]) # Collect frequencies
            debug_print(f"Added DF from {os.path.basename(f_path)} to all_scans_dfs. Current count: {len(all_scans_dfs)}", file=current_file, function=current_function, console_print_func=console_print_func)
        except Exception as e:
            console_print_func(f"Error reading {os.path.basename(f_path)}: {e}")
            debug_print(f"Error reading {os.path.basename(f_path)}: {e}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not all_scans_dfs:
        console_print_func("No valid scan data could be loaded from the selected files for averaging.")
        debug_print("No valid scan data could be loaded from the selected files for averaging.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (no valid data)", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Create a master reference frequency series from all collected frequencies
    reference_freq_series = all_frequencies.sort_values().drop_duplicates().reset_index(drop=True)
    
    # Add debug prints for reference_freq_series
    if reference_freq_series.empty or reference_freq_series.isnull().any():
        console_print_func("Error: Master reference frequency series is empty or contains NaN values. Cannot proceed.")
        debug_print("Master reference frequency series is invalid.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None
    debug_print(f"Master reference frequency axis (first few points): {reference_freq_series.head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Master reference frequency axis (last few points): {reference_freq_series.tail().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Master reference frequency axis (info):\n{reference_freq_series.info()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Master reference frequency axis (isnull sum): {reference_freq_series.isnull().sum()}", file=current_file, function=current_function, console_print_func=console_print_func)


    # Initialize aggregated_df with the master frequency axis
    aggregated_df = pd.DataFrame({'Frequency (Hz)': reference_freq_series})
    debug_print(f"Initialized aggregated_df with Frequency (Hz) column. Shape: {aggregated_df.shape}", file=current_file, function=current_function, console_print_func=console_print_func)

    power_levels_aligned_list = []
    rbw_values = [] # Collect RBW values for PSD calculation

    for df_idx, df in enumerate(all_scans_dfs):
        try:
            # Reindex the 'Power (dBm)' column to the common reference frequency
            aligned_power_series = df.set_index('Frequency (Hz)')['Power (dBm)'].reindex(reference_freq_series)

            # Interpolate NaN values introduced by reindex
            aligned_power_series = aligned_power_series.interpolate(method='linear', limit_direction='both')

            if aligned_power_series.empty or aligned_power_series.isnull().all():
                console_print_func(f"Warning: Aligned and interpolated power series for file {os.path.basename(file_paths[df_idx])} is empty or all NaNs. Skipping this file for averaging.")
                debug_print(f"Aligned and interpolated power series for file {os.path.basename(file_paths[df_idx])} is empty/NaNs.", file=current_file, function=current_function, console_print_func=console_print_func)
                continue

            power_levels_aligned_list.append(aligned_power_series)
            
            # Ensure RBW is extracted and appended for PSD calculation
            if 'RBW_Hz' in df.columns and not df['RBW_Hz'].isnull().all():
                rbw_values.append(df['RBW_Hz'].iloc[0]) # Assuming RBW is constant per file
            else:
                rbw_values.append(None) # Append None if RBW is missing or all NaN for this file
                console_print_func(f"Warning: RBW not found or invalid for file {os.path.basename(file_paths[df_idx])}. PSD for this file will be affected.")
            
            debug_print(f"Aligned dataframe {df_idx+1}'s power levels and collected RBW: {rbw_values[-1]}", file=current_file, function=current_function, console_print_func=console_print_func)

        except Exception as e:
            console_print_func(f"Error during alignment and interpolation for file {os.path.basename(file_paths[df_idx])}: {e}. Skipping this file.")
            debug_print(f"Error during alignment and interpolation for file {os.path.basename(file_paths[df_idx])}: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
            continue

    debug_print(f"After alignment loop: len(power_levels_aligned_list) = {len(power_levels_aligned_list)}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"After alignment loop: len(rbw_values) = {len(rbw_values)}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not power_levels_aligned_list:
        console_print_func("No dataframes successfully aligned for concatenation. Cannot proceed with averaging.")
        debug_print("No dataframes successfully aligned for concatenation.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (no aligned data for concat)", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None


    # Concatenate all aligned power series into a single DataFrame
    power_levels_df = pd.concat(power_levels_aligned_list, axis=1)
    power_levels_df.columns = [f"File_{i+1}" for i in range(len(power_levels_aligned_list))] # Name columns
    debug_print(f"Combined and aligned power_levels_df shape: {power_levels_df.shape}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Add debug prints to check for NaNs in power_levels_df
    if power_levels_df.empty or power_levels_df.isnull().all().all():
        console_print_func("Error: Aligned power data is empty or all NaN after processing. Cannot perform calculations.")
        debug_print("Aligned power data is empty or all NaN.", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    debug_print(f"Power levels DF before calculations (head):\n{power_levels_df.head()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Power levels DF NaN counts per column:\n{power_levels_df.isnull().sum()}", file=current_file, function=current_function, console_print_func=console_print_func)


    # Use a dictionary to map selected types to calculation functions
    calculation_functions = {
        "Average": _calculate_average,
        "Median": _calculate_median,
        "Range": _calculate_range,
        "Std Dev": _calculate_std_dev,
        "Variance": _calculate_variance,
        "PSD (dBm/Hz)": _calculate_psd
    }

    for avg_type in selected_avg_types:
        if avg_type in calculation_functions:
            if avg_type == "PSD (dBm/Hz)":
                calculated_series = calculation_functions[avg_type](power_levels_df, rbw_values, console_print_func)
            else:
                calculated_series = calculation_functions[avg_type](power_levels_df, console_print_func)
            
            # Assign the calculated series directly to the aggregated_df
            aggregated_df[avg_type] = calculated_series.values # Use .values to ensure alignment by index
            debug_print(f"Added '{avg_type}' column to aggregated_df. First 5 values: {aggregated_df[avg_type].head().tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
        else:
            console_print_func(f"Warning: Unknown average type '{avg_type}' requested. Skipping calculation.")
            debug_print(f"Unknown average type '{avg_type}' requested.", file=current_file, function=current_function, console_print_func=console_print_func)

    debug_print(f"Final aggregated_df columns: {aggregated_df.columns.tolist()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Aggregated DataFrame head:\n{aggregated_df.head()}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Aggregated DataFrame info:\n{aggregated_df.info()}", file=current_file, function=current_function, console_print_func=console_print_func)

    # --- Save the COMPLETE_MATH CSV with all selected columns ---
    complete_math_csv_filename = os.path.join(output_dir_full, f"COMPLETE_MATH_{plot_title_prefix}_MultiFileAverage_{timestamp_str}.csv")
    try:
        # Ensure headers are included for the complete math file
        aggregated_df.to_csv(complete_math_csv_filename, index=False, float_format='%.3f', sep=',')
        console_print_func(f"✅ Complete Math data saved to: {complete_math_csv_filename}")
        debug_print(f"Saved Complete Math CSV to: {complete_math_csv_filename}", file=current_file, function=current_function, console_print_func=console_print_func)
    except Exception as e:
        console_print_func(f"❌ Failed to save COMPLETE_MATH CSV: {e}")
        debug_print(f"Error saving COMPLETE_MATH CSV: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None # Return None if saving fails


    # --- Save individual selected data to separate CSVs in the new subfolder ---
    try:
        for col_name in aggregated_df.columns:
            if col_name != 'Frequency (Hz)':
                # Clean up column name for filename
                clean_col_name = re.sub(r'[^a-zA-Z0-9_]+', '', col_name).replace('dBm', '').replace('Hz', '').strip()
                csv_filename = os.path.join(output_dir_full, f"{clean_col_name}_{plot_title_prefix}_MultiFileAverage_{timestamp_str}.csv")
                # Do not include header for individual files as per previous request/pattern
                # Ensure that if a column is all NaN, it's not saved or handled gracefully
                if not aggregated_df[col_name].isnull().all():
                    aggregated_df[['Frequency (Hz)', col_name]].to_csv(csv_filename, index=False, float_format='%.3f', header=False, sep=',')
                    console_print_func(f"✅ Multi-file {col_name} data saved to: {csv_filename}")
                    debug_print(f"Saved {col_name} CSV to: {csv_filename}", file=current_file, function=current_function, console_print_func=console_print_func)
                else:
                    console_print_func(f"Skipping saving {col_name} CSV: All values are NaN.")
                    debug_print(f"Skipping saving {col_name} CSV: All values are NaN.", file=current_file, function=current_function, console_print_func=console_print_func)

        console_print_func("🎉 All selected individual CSVs generated successfully!")
    except Exception as e:
        console_print_func(f"❌ Failed to save individual multi-file aggregated CSVs: {e}")
        debug_print(f"Error saving individual multi-file aggregated CSVs: {e}", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None # Return None if CSV saving fails

    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return aggregated_df, output_dir_full


def generate_multi_file_average_and_plot(
    file_paths,
    selected_avg_types,
    plot_title_prefix,
    include_tv_markers,
    include_gov_markers,
    include_markers, # Added general markers for multi-file plot
    output_html_path_base, # Renamed to output_html_path_base for clarity
    open_html_after_complete,
    console_print_func
):
    """
    Generates an aggregated plot from multiple scan files after performing selected averaging.

    Inputs:
        file_paths (list): A list of full paths to the CSV scan files.
        selected_avg_types (list): A list of strings indicating which average types to calculate
                                   (e.g., ["Average", "Median", "PSD (dBm/Hz)"]).
        plot_title_prefix (str): A prefix for the plot title and output file names.
        include_tv_markers (bool): Whether to include TV band markers on the plot.
        include_gov_markers (bool): Whether to include Government band markers on the plot.
        include_markers (bool): Whether to include general markers on the plot.
        output_html_path_base (str): The base directory where the HTML plot will be saved.
        open_html_after_complete (bool): Whether to open the generated HTML plot in a browser.
        console_print_func (function): Function to print messages to the GUI console.

    Returns:
        tuple: A tuple containing the Plotly figure object and the path to the saved HTML file,
               or (None, None) if an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_print(f"Entering {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input file_paths ({len(file_paths)} files): {file_paths}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input selected_avg_types: {selected_avg_types}", file=current_file, function=current_function, console_print_func=console_print_func)
    debug_print(f"Input output_html_path_base: {output_html_path_base}", file=current_file, function=current_function, console_print_func=console_print_func)

    if not file_paths:
        console_print_func("No file paths provided for multi-file averaging.")
        debug_print("No file paths provided for multi-file averaging.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (no file paths)", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Call the new average_scan function to get the aggregated data and output folder
    aggregated_df, output_dir_full = average_scan(
        file_paths=file_paths,
        selected_avg_types=selected_avg_types,
        plot_title_prefix=plot_title_prefix,
        output_html_path_base=output_html_path_base,
        console_print_func=console_print_func
    )

    if aggregated_df is None or output_dir_full is None:
        console_print_func("🚫 Averaging and CSV generation failed. Cannot proceed with plotting.")
        debug_print("Averaging and CSV generation failed.", file=current_file, function=current_function, console_print_func=console_print_func)
        debug_print(f"Exiting {current_function} (averaging failed)", file=current_file, function=current_function, console_print_func=console_print_func)
        return None, None

    # Define plot title
    plot_title_suffix = ", ".join(selected_avg_types)
    plot_title = f"{plot_title_prefix} - {plot_title_suffix} (Multi-File Average)"
    debug_print(f"Generated plot title: {plot_title}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Define the actual HTML output path within the new subfolder
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S") # Use a new timestamp for the plot HTML
    html_output_path_final = os.path.join(output_dir_full, f"{plot_title_prefix}_MultiFileAverage_Plot_{timestamp_str}.html")
    debug_print(f"Final HTML output path: {html_output_path_final}", file=current_file, function=current_function, console_print_func=console_print_func)

    # Generate plot using plot_multi_trace_data
    fig, plot_html_path_return = plot_multi_trace_data(
        aggregated_df,
        plot_title,
        include_tv_markers,
        include_gov_markers,
        include_markers=include_markers, # Pass general markers for multi-file plot
        historical_dfs_with_names=None, # No historical overlays for this multi-file average from external folder
        output_html_path=html_output_path_final, # Use the final path in the new subfolder
        console_print_func=console_print_func
    )

    if fig:
        if open_html_after_complete:
            _open_plot_in_browser(plot_html_path_return, console_print_func)
            debug_print(f"Opened plot in browser: {plot_html_path_return}", file=current_file, function=current_function, console_print_func=console_print_func)
    elif not fig:
        console_print_func("🚫 Plotly figure was not generated for multi-file averaged data.")
        debug_print("Plotly figure not generated for multi-file averaged data.", file=current_file, function=current_function, console_print_func=console_print_func)

    debug_print(f"Exiting {current_function}", file=current_file, function=current_function, console_print_func=console_print_func)
    return fig, plot_html_path_return
