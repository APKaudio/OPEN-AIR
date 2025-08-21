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
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250802.0055.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0055.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 55 * 1 # Example hash, adjust as needed

import pandas as pd
import numpy as np # Ensure numpy is imported for std, var, and log10
import os
import csv
from datetime import datetime
import re
import platform # For opening folder cross-platform
import inspect # Import inspect module

# Updated imports for new logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import plotting functions and constants
from Plotting.utils_plotting import plot_multi_trace_data, _open_plot_in_browser
from ref.frequency_bands import (
    MHZ_TO_HZ,
    TV_PLOT_BAND_MARKERS,
    GOV_PLOT_BAND_MARKERS
)

# --- Helper Functions for Calculations and Folder Management ---

def _create_output_subfolder(base_output_dir, prefix, timestamp_str, console_print_func=None):
    """
    Function Description:
    Creates a new subfolder for scan outputs based on a prefix and timestamp.

    Inputs:
        base_output_dir (str): The base directory where the subfolder will be created.
        prefix (str): A descriptive prefix for the subfolder name (e.g., scan name, group name).
        timestamp_str (str): A timestamp string (e.g., YYYYMMDD_HHMMSS) for uniqueness.
        console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Constructs the full path for the new subfolder.
    2. Creates the directory using `os.makedirs(exist_ok=True)`.
    3. Logs the creation of the subfolder to the console and debug log.

    Outputs of this function:
        str: The full path to the newly created subfolder.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Preparing to create output subfolder! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)

    subfolder_name = f"{prefix}_{timestamp_str}"
    output_dir_full = os.path.join(base_output_dir, subfolder_name)
    os.makedirs(output_dir_full, exist_ok=True)
    console_print_func(f"Created output subfolder: {output_dir_full}")
    debug_log(f"Created output subfolder: {output_dir_full}. Ready for data!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Subfolder created successfully! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return output_dir_full

def _calculate_average(power_levels_df, console_print_func=None):
    """
    Function Description:
    Calculates the average power levels across all traces in the DataFrame.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Calculates the mean across rows (axis=1) of the input DataFrame.
    2. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the average power level for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating average power levels! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    average_levels = power_levels_df.mean(axis=1)
    debug_log(f"Calculated Average. First 5 values: {average_levels.head().tolist()}. Looking good!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Average calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return average_levels

def _calculate_median(power_levels_df, console_print_func=None):
    """
    Function Description:
    Calculates the median power levels across all traces in the DataFrame.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Calculates the median across rows (axis=1) of the input DataFrame.
    2. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the median power level for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating median power levels! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    median_levels = power_levels_df.median(axis=1)
    debug_log(f"Calculated Median. First 5 values: {median_levels.head().tolist()}. Spot on!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Median calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return median_levels

def _calculate_range(power_levels_df, console_print_func=None):
    """
    Function Description:
    Calculates the range (max - min) of power levels across all traces in the DataFrame.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Calculates the maximum and minimum across rows (axis=1).
    2. Subtracts min from max to get the range.
    3. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the range of power levels for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating power level range! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    range_levels = power_levels_df.max(axis=1) - power_levels_df.min(axis=1)
    debug_log(f"Calculated Range. First 5 values: {range_levels.head().tolist()}. Getting the spread!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Range calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return range_levels

def _calculate_std_dev(power_levels_df, console_print_func=None):
    """
    Function Description:
    Calculates the standard deviation of power levels across all traces in the DataFrame.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Calculates the standard deviation across rows (axis=1) of the input DataFrame.
    2. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the standard deviation of power levels for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating standard deviation! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    std_dev_levels = power_levels_df.std(axis=1)
    debug_log(f"Calculated Std Dev. First 5 values: {std_dev_levels.head().tolist()}. Measuring consistency!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Standard deviation calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return std_dev_levels

def _calculate_variance(power_levels_df, console_print_func=None):
    """
    Function Description:
    Calculates the variance of power levels across all traces in the DataFrame.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Calculates the variance across rows (axis=1) of the input DataFrame.
    2. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the variance of power levels for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating power level variance! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    variance_levels = power_levels_df.var(axis=1)
    debug_log(f"Calculated Variance. First 5 values: {variance_levels.head().tolist()}. Seeing the spread!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Exiting {current_function}. Variance calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return variance_levels

def _calculate_psd(power_levels_df, rbw_values, console_print_func=None):
    """
    Function Description:
    Calculates the Power Spectral Density (PSD) from power levels and RBW values.
    If multiple traces, calculates PSD for each then averages.

    Inputs:
    - power_levels_df (pandas.DataFrame): DataFrame where each column represents a scan trace
                                          and rows are frequency points.
    - rbw_values (list): A list of RBW values (in Hz), one for each trace in `power_levels_df`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Initializes a Series for PSD levels with NaN.
    2. Checks for valid RBW values. If invalid, logs a warning and returns NaN Series.
    3. Converts power levels from dBm to linear mW.
    4. Iterates through each trace, calculates its PSD, and appends to a list.
    5. If multiple PSD traces are calculated, combines them and takes the mean.
    6. Logs the calculation and a sample of the results.

    Outputs of this function:
    - pandas.Series: A Series containing the calculated PSD for each frequency point.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Calculating Power Spectral Density! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    
    psd_levels = pd.Series([np.nan] * len(power_levels_df.index), index=power_levels_df.index) # Initialize with NaN

    if not rbw_values or all(rbw is None or rbw <= 0 for rbw in rbw_values):
        console_print_func("Warning: Resolution Bandwidth (RBW) not provided or invalid for PSD calculation. PSD will be NaN.")
        debug_log("RBW missing or invalid for PSD calculation. Can't do it!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (invalid RBW). PSD calculation aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return psd_levels

    linear_power_mW_traces = 10**(power_levels_df / 10)
    psd_traces = []
    
    # Ensure rbw_values matches the number of columns in power_levels_df
    if len(rbw_values) != power_levels_df.shape[1]:
        console_print_func(f"Warning: Number of RBW values ({len(rbw_values)}) does not match number of power traces ({power_levels_df.shape[1]}). Using first RBW for all traces for PSD calculation.")
        debug_log(f"RBW count mismatch. Using first RBW for all traces. Adjusting!",
                    file=current_file, version=current_version, function=current_function)
        # Fallback to using the first valid RBW for all traces if mismatch
        valid_rbw = next((rbw for rbw in rbw_values if rbw is not None and rbw > 0), None)
        if valid_rbw:
            rbw_values = [valid_rbw] * power_levels_df.shape[1]
        else:
            console_print_func("Error: No valid RBW found for PSD calculation. PSD will be NaN.")
            debug_log("No valid RBW found for PSD. This is a problem!",
                        file=current_file, version=current_version, function=current_function)
            return psd_levels
    
    # Ensure all RBW values are valid before proceeding
    if any(rbw is None or rbw <= 0 for rbw in rbw_values):
        console_print_func("Error: One or more RBW values are invalid for PSD calculation. PSD will be NaN.")
        debug_log("Invalid RBW values detected during PSD calculation. Aborting!",
                    file=current_file, version=current_version, function=current_function)
        return psd_levels


    for i, col in enumerate(power_levels_df.columns):
        rbw = rbw_values[i]
        psd_trace = 10 * np.log10(linear_power_mW_traces[col] / rbw)
        psd_traces.append(psd_trace)
        debug_log(f"Calculated PSD for trace {i+1} with RBW {rbw}. Trace processed!",
                    file=current_file, version=current_version, function=current_function)

    if psd_traces:
        combined_psd_df = pd.concat(psd_traces, axis=1)
        psd_levels = combined_psd_df.mean(axis=1)
        debug_log(f"Calculated multi-trace averaged PSD. First 5 values: {psd_levels.head().tolist()}. Done and dusted!",
                    file=current_file, version=current_version, function=current_function)
    else:
        console_print_func("No valid PSD data could be calculated for any trace. PSD column will be NaN.")
        debug_log("No valid PSD data for multi-trace average. Nothing to combine!",
                    file=current_file, version=current_version, function=current_function)

    debug_log(f"Exiting {current_function}. PSD calculation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return psd_levels


def average_scan(
    file_paths,
    selected_avg_types,
    plot_title_prefix,
    output_html_path_base,
    console_print_func=None
):
    """
    Function Description:
    Performs averaging and statistical calculations on a list of scan files
    and saves the results to separate CSV files in a new subfolder.

    Inputs:
        file_paths (list): A list of full paths to the CSV scan files.
        selected_avg_types (list): A list of strings indicating which average types to calculate
                                   (e.g., ["Average", "Median", "PSD (dBm/Hz)"]).
        plot_title_prefix (str): A prefix for the output folder and file names (e.g., "MyScan").
        output_html_path_base (str): The base directory where the new subfolder will be created.
        console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Returns:
        tuple: A tuple containing:
               - pandas.DataFrame: The aggregated DataFrame, or None if an error occurs.
               - str: The full path to the newly created output subfolder, or None if an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Starting multi-file averaging! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input file_paths ({len(file_paths)} files): {file_paths}. Ready to process!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input selected_avg_types: {selected_avg_types}. Calculations selected!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input output_html_path_base: {output_html_path_base}. Output destination set!",
                file=current_file, version=current_version, function=current_function)

    if not file_paths:
        console_print_func("No file paths provided for averaging.")
        debug_log("No file paths provided for averaging. Nothing to do!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (no file paths). Averaging aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # --- Create a new subfolder for this multi-file averaged plot's outputs ---
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir_full = _create_output_subfolder(
        base_output_dir,
        f"{plot_title_prefix}_AppliedMath", # Prefix for applied math folder
        timestamp_str, # Timestamp for subfolder
        console_print_func
    )
    debug_log(f"Output subfolder created for applied math: {output_dir_full}. Organized and ready!",
                file=current_file, version=current_version, function=current_function)

    all_scans_dfs = []
    # Regex to extract RBW and Offset from filename for PSD calculation and frequency normalization
    filename_pattern = re.compile(
        r'.*_RBW(?P<rbw_val>\d+K?)_HOLD\d+_(?:Offset(?P<offset_val>-?\d+))?_(?P<date_time>\d{8}_\d{6})\.csv$'
    )

    all_frequencies = pd.Series(dtype=float) # To collect all unique frequencies for the master reference

    for df_idx, f_path in enumerate(file_paths):
        debug_log(f"Processing file {df_idx+1}/{len(file_paths)}: {os.path.basename(f_path)}. Reading data!",
                    file=current_file, version=current_version, function=current_function)
        try:
            df = pd.read_csv(f_path, header=None)
            
            if df.shape[1] < 2:
                console_print_func(f"Skipping {os.path.basename(f_path)}: CSV does not contain at least two columns (Frequency, Power). Found {df.shape[1]} columns. Malformed file!")
                debug_log(f"Skipping {os.path.basename(f_path)}: Insufficient columns in CSV. Bad data!",
                            file=current_file, version=current_version, function=current_function)
                continue

            df.columns = ['Frequency (Hz)', 'Power (dBm)']
            debug_log(f"Successfully read CSV: {os.path.basename(f_path)} with implied columns: {df.columns.tolist()}. Data loaded!",
                        file=current_file, version=current_version, function=current_function)
            
            df['Frequency (Hz)'] = pd.to_numeric(df['Frequency (Hz)'], errors='coerce')
            df['Power (dBm)'] = pd.to_numeric(df['Power (dBm)'], errors='coerce') # Ensure power is numeric
            df.dropna(subset=['Frequency (Hz)', 'Power (dBm)'], inplace=True) # Drop rows with NaN in either
            df.drop_duplicates(subset=['Frequency (Hz)'], keep='first', inplace=True)

            if df.empty:
                console_print_func(f"Warning: File {os.path.basename(f_path)} became empty after cleaning non-numeric or duplicate data. Skipping. No usable data!")
                debug_log(f"File {os.path.basename(f_path)} empty after data cleanup. Nothing left!",
                            file=current_file, version=current_version, function=current_function)
                continue

            file_name = os.path.basename(f_path)
            match = filename_pattern.match(file_name)
            debug_log(f"Regex match result for '{file_name}': {match}. Pattern check complete!",
                        file=current_file, version=current_version, function=current_function)
            
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
                debug_log(f"File {file_name}: Extracted RBW={rbw_hz}, Offset={current_offset_hz}. Frequency normalized. Data adjusted!",
                            file=current_file, version=current_version, function=current_function)
            else:
                debug_log(f"File {file_name}: Filename pattern mismatch. RBW and Offset not extracted. Assuming no offset and default RBW for PSD. Can't parse!",
                            file=current_file, version=current_version, function=current_function)
                console_print_func(f"Warning: Filename '{file_name}' did not match expected pattern for RBW/Offset. PSD calculation might be inaccurate. Proceeding with caution!")

            df['RBW_Hz'] = rbw_hz # Add RBW to the dataframe for later PSD calculation
            all_scans_dfs.append(df)
            all_frequencies = pd.concat([all_frequencies, df['Frequency (Hz)']]) # Collect frequencies
            debug_log(f"Added DF from {os.path.basename(f_path)} to all_scans_dfs. Current count: {len(all_scans_dfs)}. Data collected!",
                        file=current_file, version=current_version, function=current_function)
        except Exception as e:
            console_print_func(f"Error reading {os.path.basename(f_path)}: {e}. File problem!")
            debug_log(f"Error reading {os.path.basename(f_path)}: {e}. Failed to load!",
                        file=current_file, version=current_version, function=current_function)

    if not all_scans_dfs:
        console_print_func("No valid scan data could be loaded from the selected files for averaging. Nothing to work with!")
        debug_log("No valid scan data could be loaded from the selected files for averaging. Empty handed!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (no valid data). Averaging aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # Create a master reference frequency series from all collected frequencies
    reference_freq_series = all_frequencies.sort_values().drop_duplicates().reset_index(drop=True)
    
    # Add debug prints for reference_freq_series
    if reference_freq_series.empty or reference_freq_series.isnull().any():
        console_print_func("Error: Master reference frequency series is empty or contains NaN values. Cannot proceed. This is a critical bug!")
        debug_log("Master reference frequency series is invalid. Cannot proceed!",
                    file=current_file, version=current_version, function=current_function)
        return None, None
    debug_log(f"Master reference frequency axis (first few points): {reference_freq_series.head().tolist()}. Axis established!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Master reference frequency axis (last few points): {reference_freq_series.tail().tolist()}. End of axis!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Master reference frequency axis (info):\n{reference_freq_series.info()}. Axis details!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Master reference frequency axis (isnull sum): {reference_freq_series.isnull().sum()}. NaN check!",
                file=current_file, version=current_version, function=current_function)


    # Initialize aggregated_df with the master frequency axis
    aggregated_df = pd.DataFrame({'Frequency (Hz)': reference_freq_series})
    debug_log(f"Initialized aggregated_df with Frequency (Hz) column. Shape: {aggregated_df.shape}. DataFrame ready!",
                file=current_file, version=current_version, function=current_function)

    power_levels_aligned_list = []
    rbw_values = [] # Collect RBW values for PSD calculation

    for df_idx, df in enumerate(all_scans_dfs):
        try:
            # Reindex the 'Power (dBm)' column to the common reference frequency
            aligned_power_series = df.set_index('Frequency (Hz)')['Power (dBm)'].reindex(reference_freq_series)

            # Interpolate NaN values introduced by reindex
            aligned_power_series = aligned_power_series.interpolate(method='linear', limit_direction='both')

            if aligned_power_series.empty or aligned_power_series.isnull().all():
                console_print_func(f"Warning: Aligned and interpolated power series for file {os.path.basename(file_paths[df_idx])} is empty or all NaNs. Skipping this file for averaging. No usable data after alignment!")
                debug_log(f"Aligned and interpolated power series for file {os.path.basename(file_paths[df_idx])} is empty/NaNs. Skipping!",
                            file=current_file, version=current_version, function=current_function)
                continue

            power_levels_aligned_list.append(aligned_power_series)
            
            # Ensure RBW is extracted and appended for PSD calculation
            if 'RBW_Hz' in df.columns and not df['RBW_Hz'].isnull().all():
                rbw_values.append(df['RBW_Hz'].iloc[0]) # Assuming RBW is constant per file
            else:
                rbw_values.append(None) # Append None if RBW is missing or all NaN for this file
                console_print_func(f"Warning: RBW not found or invalid for file {os.path.basename(file_paths[df_idx])}. PSD for this file will be affected. Inaccurate PSD ahead!")
            
            debug_log(f"Aligned dataframe {df_idx+1}'s power levels and collected RBW: {rbw_values[-1]}. Alignment complete!",
                        file=current_file, version=current_version, function=current_function)

        except Exception as e:
            console_print_func(f"Error during alignment and interpolation for file {os.path.basename(file_paths[df_idx])}: {e}. Skipping this file. Alignment failed!")
            debug_log(f"Error during alignment and interpolation for file {os.path.basename(file_paths[df_idx])}: {e}. Skipping file!",
                        file=current_file, version=current_version, function=current_function)
            continue

    debug_log(f"After alignment loop: len(power_levels_aligned_list) = {len(power_levels_aligned_list)}. All aligned!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"After alignment loop: len(rbw_values) = {len(rbw_values)}. RBW values collected!",
                file=current_file, version=current_version, function=current_function)

    if not power_levels_aligned_list:
        console_print_func("No dataframes successfully aligned for concatenation. Cannot proceed with averaging. No data to combine!")
        debug_log("No dataframes successfully aligned for concatenation. Nothing to average!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (no aligned data for concat). Averaging aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return None, None


    # Concatenate all aligned power series into a single DataFrame
    power_levels_df = pd.concat(power_levels_aligned_list, axis=1)
    power_levels_df.columns = [f"File_{i+1}" for i in range(len(power_levels_aligned_list))] # Name columns
    debug_log(f"Combined and aligned power_levels_df shape: {power_levels_df.shape}. DataFrame assembled!",
                file=current_file, version=current_version, function=current_function)

    # Add debug prints to check for NaNs in power_levels_df
    if power_levels_df.empty or power_levels_df.isnull().all().all():
        console_print_func("Error: Aligned power data is empty or all NaN after processing. Cannot perform calculations. Critical data loss!")
        debug_log("Aligned power data is empty or all NaN. Cannot calculate!",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    debug_log(f"Power levels DF before calculations (head):\n{power_levels_df.head()}. Ready for math!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Power levels DF NaN counts per column:\n{power_levels_df.isnull().sum()}. NaN check complete!",
                file=current_file, version=current_version, function=current_function)


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
            debug_log(f"Added '{avg_type}' column to aggregated_df. First 5 values: {aggregated_df[avg_type].head().tolist()}. Column added!",
                        file=current_file, version=current_version, function=current_function)
        else:
            console_print_func(f"Warning: Unknown average type '{avg_type}' requested. Skipping calculation. What is this?!")
            debug_log(f"Unknown average type '{avg_type}' requested. Skipping!",
                        file=current_file, version=current_version, function=current_function)

    debug_log(f"Final aggregated_df columns: {aggregated_df.columns.tolist()}. All columns present!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Aggregated DataFrame head:\n{aggregated_df.head()}. Final data overview!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Aggregated DataFrame info:\n{aggregated_df.info()}. DataFrame details!",
                file=current_file, version=current_version, function=current_function)

    # --- Save the COMPLETE_MATH CSV with all selected columns ---
    complete_math_csv_filename = os.path.join(output_dir_full, f"COMPLETE_MATH_{plot_title_prefix}_MultiFileAverage_{timestamp_str}.csv")
    try:
        # Ensure headers are included for the complete math file
        aggregated_df.to_csv(complete_math_csv_filename, index=False, float_format='%.3f', sep=',')
        console_print_func(f"✅ Complete Math data saved to: {complete_math_csv_filename}. Success!")
        debug_log(f"Saved Complete Math CSV to: {complete_math_csv_filename}. Mission accomplished!",
                    file=current_file, version=current_version, function=current_function)
    except Exception as e:
        console_print_func(f"❌ Failed to save COMPLETE_MATH CSV: {e}. This is a disaster!")
        debug_log(f"Error saving COMPLETE_MATH CSV: {e}. Failed to save!",
                    file=current_file, version=current_version, function=current_function)
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
                    console_print_func(f"✅ Multi-file {col_name} data saved to: {csv_filename}. Data exported!")
                    debug_log(f"Saved {col_name} CSV to: {csv_filename}. File created!",
                                file=current_file, version=current_version, function=current_function)
                else:
                    console_print_func(f"Skipping saving {col_name} CSV: All values are NaN. Nothing to save!")
                    debug_log(f"Skipping saving {col_name} CSV: All values are NaN. Empty column!",
                                file=current_file, version=current_version, function=current_function)

        console_print_func("🎉 All selected individual CSVs generated successfully! What a triumph!")
    except Exception as e:
        console_print_func(f"❌ Failed to save individual multi-file aggregated CSVs: {e}. This is a problem!")
        debug_log(f"Error saving individual multi-file aggregated CSVs: {e}. Failed to export!",
                    file=current_file, version=current_version, function=current_function)
        return None, None # Return None if CSV saving fails

    debug_log(f"Exiting {current_function}. Averaging and CSV generation complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
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
    console_print_func=None
):
    """
    Function Description:
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
        console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Returns:
        tuple: A tuple containing the Plotly figure object and the path to the saved HTML file,
               or (None, None) if an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Preparing to generate multi-file average plot! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input file_paths ({len(file_paths)} files): {file_paths}. Plotting these files!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input selected_avg_types: {selected_avg_types}. Plot types selected!",
                file=current_file, version=current_version, function=current_function)
    debug_log(f"Input output_html_path_base: {output_html_path_base}. Plot output destination set!",
                file=current_file, version=current_version, function=current_function)

    if not file_paths:
        console_print_func("No file paths provided for multi-file averaging.")
        debug_log("No file paths provided for multi-file averaging. Nothing to plot!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (no file paths). Plotting aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
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
        console_print_func("🚫 Averaging and CSV generation failed. Cannot proceed with plotting. Data missing!")
        debug_log("Averaging and CSV generation failed. Plotting aborted!",
                    file=current_file, version=current_version, function=current_function)
        debug_log(f"Exiting {current_function} (averaging failed). Plotting aborted! Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return None, None

    # Define plot title
    plot_title_suffix = ", ".join(selected_avg_types)
    plot_title = f"{plot_title_prefix} - {plot_title_suffix} (Multi-File Average)"
    debug_log(f"Generated plot title: {plot_title}. Title ready!",
                file=current_file, version=current_version, function=current_function)

    # Define the actual HTML output path within the new subfolder
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S") # Use a new timestamp for the plot HTML
    html_output_path_final = os.path.join(output_dir_full, f"{plot_title_prefix}_MultiFileAverage_Plot_{timestamp_str}.html")
    debug_log(f"Final HTML output path: {html_output_path_final}. Path set!",
                file=current_file, version=current_version, function=current_function)

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
            debug_log(f"Opened plot in browser: {plot_html_path_return}. Plot launched!",
                        file=current_file, version=current_version, function=current_function)
    elif not fig:
        console_print_func("🚫 Plotly figure was not generated for multi-file averaged data. No plot to show!")
        debug_log("Plotly figure not generated for multi-file averaged data. Figure missing!",
                    file=current_file, version=current_version, function=current_function)

    debug_log(f"Exiting {current_function}. Multi-file averaging and plotting complete! Version: {current_version}",
                file=current_file, version=current_version, function=current_function)
    return fig, plot_html_path_return
