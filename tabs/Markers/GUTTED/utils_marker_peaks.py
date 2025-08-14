# tabs/Markers/utils_marker_peaks.py
#
# This file provides utility functions for retrieving peak values from a spectrum
# analyzer and updating the MARKERS.CSV file with this data. The core functionality
# is to set the instrument's frequency range based on a selected group of markers,
# place markers on individual devices within that group, query the resulting amplitude
# (Y-axis) value, and save this data back to the CSV.
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
#
# Version 20250814.011923.1

current_version = "20250814.011923.1"
current_version_hash = (20250814 * 11923 * 1)

import os
import csv
import pandas as pd
import inspect
import numpy as np
import time
import threading

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.Yakety_Yak import YakSet, YakDo, YakNab, YakBeg
from ref.frequency_bands import MHZ_TO_HZ

# Global lock for instrument access
_instrument_lock = threading.Lock()

def get_peak_values_and_update_csv(app_instance, devices_to_process, console_print_func):
    """
    Function Description:
    Gets peak values for a CHUNK of devices (up to 6), adds/updates a "Peak" column 
    in the main MARKERS.CSV file, and saves the changes immediately.
    This function is designed to be called iteratively by a parent loop.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - devices_to_process (DataFrame): A DataFrame of up to 6 devices to process.
    - console_print_func (function): A function to print to the GUI console.

    Outputs:
    - pandas.DataFrame or None: The fully updated DataFrame from MARKERS.CSV, or None on failure.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Getting peak values for a chunk of {len(devices_to_process)} devices.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot get peak values.")
        return None

    markers_file_path = app_instance.MARKERS_FILE_PATH
    if not os.path.exists(markers_file_path):
        console_print_func("❌ MARKERS.CSV file not found. Cannot proceed.")
        return None

    try:
        if devices_to_process.empty:
            console_print_func(f"⚠️ No devices in this chunk to process.")
            return pd.read_csv(markers_file_path)

        peak_values = {}
        
        # Prepare a list of frequencies for the YakBeg command
        marker_freqs_hz = [int(device.get('FREQ') * MHZ_TO_HZ) for index, device in devices_to_process.iterrows()]
        padded_freqs = marker_freqs_hz + [0] * (6 - len(marker_freqs_hz))

        with _instrument_lock:
            y_values_str = YakBeg(app_instance, "MARKER/PLACE/ALL", console_print_func, *padded_freqs)

        if y_values_str and y_values_str != "FAILED":
            # FIXED: Split by semicolon, which the instrument is actually returning.
            y_values = y_values_str.split(";")
            for i, (index, device) in enumerate(devices_to_process.iterrows()):
                device_name = device.get('NAME')
                if i < len(y_values):
                    try:
                        peak_values[device_name] = float(y_values[i])
                    except (ValueError, TypeError):
                        peak_values[device_name] = np.nan
                else:
                    peak_values[device_name] = np.nan
        else:
            console_print_func("❌ Failed to retrieve Y-values for marker batch.")
            debug_log("YakBeg failed to return a valid response for markers.",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function)
            # Set all peaks for this chunk to NaN on failure
            for index, device in devices_to_process.iterrows():
                peak_values[device.get('NAME')] = np.nan

        # Read the entire current CSV, update it, and save it back.
        df_master = pd.read_csv(markers_file_path)
        if 'Peak' not in df_master.columns:
            df_master['Peak'] = np.nan

        # Update the master DataFrame with the new peak values for this chunk
        for device_name, peak_val in peak_values.items():
            df_master.loc[df_master['NAME'] == device_name, 'Peak'] = peak_val

        df_master.to_csv(markers_file_path, index=False)
        debug_log(message=f"Updated and saved MARKERS.CSV with peak values for {len(peak_values)} devices.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        return df_master

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred: {e}")
        debug_log(message=f"Error in get_peak_values_and_update_csv: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return None