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
# Version 20250812.163000.1 (INITIAL: Created the function to get peak values and update the CSV.)

current_version = "20250812.163000.1"
current_version_hash = 20250812 * 163000 * 1

import os
import csv
import pandas as pd
import inspect
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from tabs.Instrument.Yakety_Yak import YakSet, YakGet, YakDo
from ref.frequency_bands import MHZ_TO_HZ

def get_peak_values_and_update_csv(app_instance, zone_name, console_print_func):
    """
    Function Description:
    Gets peak values for devices in a specific zone, adds a "Peak" column
    to MARKERS.CSV, and populates it with the queried values.

    Inputs:
    - app_instance (object): A reference to the main application instance.
    - zone_name (str): The name of the zone to process.
    - console_print_func (function): A function to print to the GUI console.

    Process:
    1. Reads the MARKERS.CSV file into a pandas DataFrame.
    2. Filters the DataFrame to get all devices in the specified zone.
    3. Calculates the min and max frequencies of the zone and adds a buffer.
    4. Sets the instrument's frequency range to this buffered range using YakSet.
    5. For the first six devices in the zone, it sets a marker on each one using YakSet.
    6. Queries the amplitude (Y-value) of each marker using YakGet.
    7. Stores these values.
    8. Adds a new "Peak" column to the DataFrame.
    9. Populates the "Peak" column with the queried values, matching them to the correct devices.
    10. Saves the updated DataFrame back to MARKERS.CSV.
    11. Reloads the presets data to reflect the changes.

    Outputs:
    - pandas.DataFrame: The updated DataFrame with the new "Peak" column.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}. Getting peak values for zone: {zone_name}. It's showtime!",
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

        # Get all frequencies for the specified zone
        zone_devices = df[df['ZONE'] == zone_name].copy()
        if zone_devices.empty:
            console_print_func(f"⚠️ No devices found in zone '{zone_name}'.")
            return df
            
        # Add a buffer to the frequency range
        min_freq_mhz = zone_devices['FREQ'].min()
        max_freq_mhz = zone_devices['FREQ'].max()
        buffer_mhz = 1.0 # 1 MHz buffer
        
        start_freq_mhz = max(0, min_freq_mhz - buffer_mhz)
        end_freq_mhz = max_freq_mhz + buffer_mhz
        
        start_freq_hz = int(start_freq_mhz * MHZ_TO_HZ)
        end_freq_hz = int(end_freq_mhz * MHZ_TO_HZ)
        
        console_print_func(f"💬 Setting instrument range to: {start_freq_mhz:.3f} MHz - {end_freq_mhz:.3f} MHz")

        # Set instrument frequency range
        YakSet(app_instance, "FREQUENCY/START", str(start_freq_hz), console_print_func)
        YakSet(app_instance, "FREQUENCY/STOP", str(end_freq_hz), console_print_func)

        peak_values = {}
        for i in range(1, 7): # Use markers 1 through 6
            if i <= len(zone_devices):
                device = zone_devices.iloc[i-1]
                device_freq_mhz = device['FREQ']
                device_name = device['NAME']

                # Set marker X value to the device's frequency
                marker_x_command_type = f"MARKER/{i}/PLACE/X"
                marker_x_value_hz = int(device_freq_mhz * MHZ_TO_HZ)
                
                if YakSet(app_instance, marker_x_command_type, str(marker_x_value_hz), console_print_func) == "PASSED":
                    console_print_func(f"✅ Marker {i} placed on device '{device_name}' at {device_freq_mhz:.3f} MHz.")
                    
                    # Query marker Y value
                    marker_y_command_type = f"MARKER/{i}/CALCULATE/Y"
                    y_value = YakGet(app_instance, marker_y_command_type, console_print_func)
                    
                    if y_value is not None:
                        try:
                            peak_values[device_name] = float(y_value)
                            console_print_func(f"✅ Retrieved Y-value for marker {i}: {y_value} dBm.")
                        except ValueError:
                            console_print_func(f"❌ Failed to parse Y-value for marker {i}.")
                            peak_values[device_name] = np.nan
                    else:
                        peak_values[device_name] = np.nan
                else:
                    console_print_func(f"❌ Failed to place marker {i} on device '{device_name}'.")

        # Add a "Peak" column and update the CSV
        if 'Peak' not in df.columns:
            df['Peak'] = np.nan # Add the column if it doesn't exist

        for index, row in df.iterrows():
            device_name = row['NAME']
            if device_name in peak_values:
                df.loc[index, 'Peak'] = peak_values[device_name]

        df.to_csv(markers_file_path, index=False)
        console_print_func("✅ Updated MARKERS.CSV with new Peak values.")
        debug_log(f"Updated MARKERS.CSV with new Peak values for zone '{zone_name}'.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        return df

    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred: {e}")
        debug_log(f"Error in get_peak_values_and_update_csv: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        return None
