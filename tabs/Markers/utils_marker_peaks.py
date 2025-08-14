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
# Version 20250816.235603.2 (FIXED: The inefficient marker update method was replaced with a single, optimized YakBeg command to set and query multiple markers in one call. Corrected the function call arguments to YakBeg to avoid the 'multiple values for argument' error.)

current_version = "20250816.235603.2"
current_version_hash = (20250816 * 235603 * 2)

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

# REMOVED: The old helper function _set_multiple_markers_x is no longer needed.


def get_peak_values_and_update_csv(app_instance, devices_to_process, console_print_func):
    """
    Function Description:
    Gets peak values for devices, adds a "Peak" column to MARKERS.CSV,
    and populates it with the queried values. This version uses the new,
    optimized `YakBeg` command to set and query multiple markers at once.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - devices_to_process (DataFrame): A DataFrame of devices to process.
    - console_print_func (function): A function to print to the GUI console.

    Outputs:
    - pandas.DataFrame: The updated DataFrame with the new "Peak" column.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Getting peak values for {len(devices_to_process)} devices with the new YakBeg command. It's showtime!",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    # Check if instrument is connected
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot get peak values. This is a disaster!")
        return None

    markers_file_path = app_instance.MARKERS_FILE_PATH
    if not os.path.exists(markers_file_path):
        console_print_func("❌ MARKERS.CSV file not found. Cannot proceed.")
        return None

    try:
        df = pd.read_csv(markers_file_path)

        if devices_to_process.empty:
            console_print_func(f"⚠️ No devices found in this selection.")
            return df

        # Add a buffer to the frequency range
        min_freq_mhz = devices_to_process['FREQ'].min()
        max_freq_mhz = devices_to_process['FREQ'].max()
        span_mhz = max_freq_mhz - min_freq_mhz

        MIN_SPAN_KHZ = 100

        if span_mhz == 0:
            trace_center_freq_mhz = min_freq_mhz
            trace_span_mhz = MIN_SPAN_KHZ / 1e3
            start_freq_mhz = trace_center_freq_mhz - trace_span_mhz / 2
            end_freq_mhz = trace_center_freq_mhz + trace_span_mhz / 2
        else:
            buffer_mhz = span_mhz * 0.1
            start_freq_mhz = max(0, min_freq_mhz - buffer_mhz)
            end_freq_mhz = max_freq_mhz + buffer_mhz

        start_freq_hz = int(start_freq_mhz * MHZ_TO_HZ)
        end_freq_hz = int(end_freq_mhz * MHZ_TO_HZ)

        console_print_func(f"💬 Setting instrument range to: {start_freq_mhz:.3f} MHz - {end_freq_mhz:.3f} MHz")

        # Set instrument frequency range
        with _instrument_lock:
            if YakSet(app_instance=app_instance, command_type="FREQUENCY/START", variable_value=str(start_freq_hz), console_print_func=console_print_func) == "FAILED":
                return None
            if YakSet(app_instance=app_instance, command_type="FREQUENCY/STOP", variable_value=str(end_freq_hz), console_print_func=console_print_func) == "FAILED":
                return None

        # Add a "Peak" column if it doesn't exist, and reset existing peaks for the selected devices
        if 'Peak' not in df.columns:
            df['Peak'] = np.nan
        else:
            df.loc[devices_to_process.index, 'Peak'] = np.nan

        peak_values = {}

        # Iterate through devices in chunks of 6 to use the new YakBeg command
        for chunk_start_index in range(0, len(devices_to_process), 6):
            # Process a maximum of 6 devices at a time
            devices_in_chunk = devices_to_process.iloc[chunk_start_index:chunk_start_index + 6]
            devices_in_chunk_list = devices_in_chunk.to_dict('records')

            # Prepare a list of frequencies for the YakBeg command
            marker_freqs_hz = [int(device.get('FREQ') * MHZ_TO_HZ) for device in devices_in_chunk_list]
            # Pad the list with zeros if the chunk is less than 6 to avoid index errors
            padded_freqs = marker_freqs_hz + [0] * (6 - len(marker_freqs_hz))

            with _instrument_lock:
                # FIXED: The YakBeg call no longer passes 'app_instance' as a positional argument.
                y_values_str = YakBeg(app_instance=app_instance, command_type="MARKER/PLACE/ALL", console_print_func=console_print_func, args=padded_freqs)

            if y_values_str and y_values_str != "FAILED":
                # Split the formatted string to get individual values
                y_values = y_values_str.split("|||")
                for i, device in enumerate(devices_in_chunk_list):
                    device_name = device.get('NAME')
                    if i < len(y_values):
                        try:
                            peak_values[device_name] = float(y_values[i])
                            console_print_func(f"✅ Retrieved Y-value for marker {i+1} on '{device_name}': {y_values[i]} dBm.")
                        except (ValueError, TypeError):
                            console_print_func(f"❌ Failed to parse Y-value for marker {i+1} on '{device_name}'.")
                            peak_values[device_name] = np.nan
                    else:
                        peak_values[device_name] = np.nan
            else:
                console_print_func("❌ Failed to retrieve Y-values for all markers in batch.")
                debug_log("YakBeg failed to return a valid response. Y-values for this chunk are missing.",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function)

        # All markers are turned on/off automatically by the YakBeg command, so no need for explicit calls here.

        # Update the CSV
        for index, row in df.iterrows():
            device_name = row['NAME']
            if device_name in peak_values:
                df.loc[index, 'Peak'] = peak_values[device_name]

        df.to_csv(markers_file_path, index=False)
        console_print_func("✅ Updated MARKERS.CSV with new Peak values.")
        debug_log(message=f"Updated MARKERS.CSV with new Peak values for the selected devices.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        return df

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred: {e}")
        debug_log(message=f"Error in get_peak_values_and_update_csv: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return None