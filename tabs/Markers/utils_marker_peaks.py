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
# Version 20250814.233000.2 (FIXED: The `devices_in_chunk` variable is now correctly defined within the loop, resolving the `NameError`.)

current_version = "20250814.233000.2"
current_version_hash = 20250814 * 233000 * 2

import os
import csv
import pandas as pd
import inspect
import numpy as np
import time

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.Yakety_Yak import YakSet, YakGet, YakDo
from ref.frequency_bands import MHZ_TO_HZ

def _set_multiple_markers_x(app_instance, device_chunk, console_print_func):
    """
    Function Description:
    Sets multiple markers (up to 6) on the instrument at once.
    This function has been created to optimize the setting of markers for batch peak searches.
    It takes a list of devices (a chunk of the total devices) and sets a marker on each one.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - device_chunk (list): A list of up to 6 device dictionaries.
    - console_print_func (function): A function to print to the GUI console.

    Outputs:
    - bool: True if all markers in the chunk were set successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Setting markers for a chunk of {len(device_chunk)} devices.",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)

    success = True
    for i, device in enumerate(device_chunk):
        marker_number = i + 1 # Markers are 1-indexed
        device_freq_mhz = device.get('FREQ')
        device_name = device.get('NAME')

        if not pd.notna(device_freq_mhz):
            console_print_func(f"⚠️ Skipping device '{device_name}': Frequency is not a number. Fucking useless!")
            debug_log(f"Skipping marker set for device '{device_name}': Frequency is not a number.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            continue
            
        marker_x_command_type = f"MARKER/{marker_number}/PLACE/X"
        marker_x_value_hz = int(device_freq_mhz * MHZ_TO_HZ)
        
        # Turn on the marker and place it
        if YakDo(app_instance=app_instance, command_type=f"MARKER/{marker_number}/CALCULATE/STATE/ON", console_print_func=console_print_func) == "FAILED":
            console_print_func(f"❌ Failed to turn on Marker {marker_number} for '{device_name}'. Aborting set for this device.")
            success = False
            continue
            
        if YakSet(app_instance=app_instance, command_type=marker_x_command_type, variable_value=str(marker_x_value_hz), console_print_func=console_print_func) == "FAILED":
            console_print_func(f"❌ Failed to place Marker {marker_number} on device '{device_name}'.")
            success = False
            continue

        console_print_func(f"✅ Marker {marker_number} placed on device '{device_name}' at {device_freq_mhz:.3f} MHz.")

    debug_log(message=f"Exiting {current_function}. Marker setting for chunk complete. Success: {success}",
              file=f"{os.path.basename(__file__)} - {current_version}",
              version=current_version,
              function=current_function)
    return success

def get_peak_values_and_update_csv(app_instance, devices_to_process, console_print_func):
    """
    Function Description:
    Gets peak values for devices, adds a "Peak" column to MARKERS.CSV,
    and populates it with the queried values.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - devices_to_process (DataFrame): A DataFrame of devices to process.
    - console_print_func (function): A function to print to the GUI console.

    Process:
    1. Reads the MARKERS.CSV file into a pandas DataFrame.
    2. Filters the DataFrame to get all devices to process.
    3. Calculates the min and max frequencies of the selection and adds a buffer.
    4. Sets the instrument's frequency range to this buffered range using YakSet.
    5. For each batch of 6 devices, it sets a marker on each one using the new utility function.
    6. Queries the amplitude (Y-value) of each marker using YakGet.
    7. Stores these values.
    8. Updates the "Peak" column in the DataFrame.
    9. Saves the updated DataFrame back to MARKERS.CSV.

    Outputs:
    - pandas.DataFrame: The updated DataFrame with the new "Peak" column.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Entering {current_function}. Getting peak values for {len(devices_to_process)} devices. It's showtime!",
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
        buffer_mhz = span_mhz * 0.1
        
        start_freq_mhz = max(0, min_freq_mhz - buffer_mhz)
        end_freq_mhz = max_freq_mhz + buffer_mhz
        
        start_freq_hz = int(start_freq_mhz * MHZ_TO_HZ)
        end_freq_hz = int(end_freq_mhz * MHZ_TO_HZ)
        
        console_print_func(f"💬 Setting instrument range to: {start_freq_mhz:.3f} MHz - {end_freq_mhz:.3f} MHz")

        # Set instrument frequency range
        if YakSet(app_instance=app_instance, command_type="FREQUENCY/START", variable_value=str(start_freq_hz), console_print_func=console_print_func) == "FAILED":
            return None
        if YakSet(app_instance=app_instance, command_type="FREQUENCY/STOP", variable_value=str(end_freq_hz), console_print_func=console_print_func) == "FAILED":
            return None
            
        # Add a "Peak" column if it doesn't exist, and reset existing peaks for the selected devices
        if 'Peak' not in df.columns:
            df['Peak'] = np.nan
        else:
            df.loc[devices_to_process.index, 'Peak'] = np.nan
            df.to_csv(markers_file_path, index=False)
            df = pd.read_csv(markers_file_path)

        peak_values = {}
        # Iterate through devices in chunks of 6
        for chunk_start_index in range(0, len(devices_to_process), 6):
            # Process a maximum of 6 devices at a time
            devices_in_chunk = devices_to_process.iloc[chunk_start_index:chunk_start_index + 6]
            devices_in_chunk_list = devices_in_chunk.to_dict('records')
            
            # Use the new helper function to set all markers in the chunk
            if not _set_multiple_markers_x(app_instance, devices_in_chunk_list, console_print_func):
                console_print_func("❌ Failed to set one or more markers in batch. Aborting peak retrieval.")
                break # Exit the main loop if a batch fails

            # Now query all active markers for their Y values
            for i, device in enumerate(devices_in_chunk_list):
                marker_number = i + 1
                device_name = device.get('NAME')

                marker_y_command_type = f"MARKER/{marker_number}/CALCULATE/Y"
                y_value = YakGet(app_instance=app_instance, command_type=marker_y_command_type, console_print_func=console_print_func)
                
                if y_value is not None:
                    try:
                        peak_values[device_name] = float(y_value)
                        console_print_func(f"✅ Retrieved Y-value for marker {marker_number} on '{device_name}': {y_value} dBm.")
                    except ValueError:
                        console_print_func(f"❌ Failed to parse Y-value for marker {marker_number} on '{device_name}'.")
                        peak_values[device_name] = np.nan
                else:
                    peak_values[device_name] = np.nan

        # After processing all chunks, turn all markers off
        for i in range(1, 7):
            YakDo(app_instance=app_instance, command_type=f"MARKER/{i}/CALCULATE/STATE/OFF", console_print_func=console_print_func)

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
