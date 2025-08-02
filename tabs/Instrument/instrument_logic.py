# src/instrument_logic.py
#
# This file contains the core logic for interacting with the instrument,
# including connection, disconnection, applying settings, and querying
# current instrument states. It abstracts the SCPI commands and handles
# data flow between the GUI and the hardware.
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
# Version 20250802.1701.9 (Updated imports to use new refactored utility files.)

current_version = "20250802.1701.9" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 9 # Example hash, adjust as needed

import tkinter as tk
import pyvisa
import os
import time
import sys
import inspect # Import inspect module

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import necessary functions from the new, specialized utility modules
from tabs.Instrument.utils_instrument_connection import (
    list_visa_resources,
    connect_to_instrument,
    disconnect_instrument
)
from tabs.Instrument.utils_instrument_read_and_write import (
    write_safe,
    query_safe
)
from tabs.Instrument.utils_instrument_initialize import (
    initialize_instrument
)
from tabs.Instrument.utils_instrument_query_settings import (
    query_current_instrument_settings
)

# Constants for frequency conversion
MHZ_TO_HZ_CONVERSION = 1_000_000
KHZ_TO_HZ_CONVERSION = 1_000

def populate_resources_logic(app_instance, console_print_func):
    # Function Description:
    # Populates the VISA resource combobox with available instruments.
    #
    # Inputs:
    # - app_instance: The main application instance, used to access Tkinter variables and update UI.
    # - console_print_func: A function to print messages to the GUI console.
    #
    # Process:
    # 1. Logs the start of the resource population.
    # 2. Calls `list_visa_resources` to discover available VISA instruments.
    # 3. Updates the `app_instance.available_resources` Tkinter variable with the discovered resources.
    # 4. Updates the UI connection status based on whether resources were found.
    # 5. Logs the completion or failure of the process.
    #
    # Outputs:
    # - A tuple of discovered VISA resources.
    #
    # (2025-08-02) Change: Added `is_scanning=False` to `app_instance.update_connection_status` call.
    # (2025-08-02) Change: Modified to return resources for direct combobox update.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Updated import for `list_visa_resources` from `utils_instrument_connection`.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Populating VISA resources. Let's find those devices! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    console_print_func("💬 Searching for VISA instruments...")
    resources = ()
    try:
        resources = list_visa_resources(console_print_func)
        app_instance.available_resources.set(",".join(resources))
        debug_log(f"Found VISA resources: {resources}. Success!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # Update UI based on whether resources were found
        app_instance.update_connection_status(app_instance.inst is not None, is_scanning=False)
        return resources
    except Exception as e:
        console_print_func(f"❌ Error listing VISA resources: {e}. This thing is a pain in the ass!")
        debug_log(f"Error listing VISA resources: {e}. What a goddamn mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.available_resources.set("")
        app_instance.update_connection_status(False, is_scanning=False) # Ensure UI is updated even on error
        return ()

def connect_instrument_logic(app_instance, console_print_func):
    # Function Description:
    # Handles the connection process to the selected VISA instrument.
    #
    # Inputs:
    # - app_instance: The main application instance, used to access Tkinter variables and update UI.
    # - console_print_func: A function to print messages to the GUI console.
    #
    # Process:
    # 1. Logs the start of the connection attempt.
    # 2. Retrieves the selected resource from the UI.
    # 3. Calls `connect_to_instrument` to establish the connection.
    # 4. If successful, queries instrument identification and settings, updates UI.
    # 5. Updates connection status and logs success or failure.
    #
    # Outputs:
    # - True if connection and initial query are successful, False otherwise.
    #
    # (2025-08-02) Change: Initial implementation.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Updated imports for `connect_to_instrument`, `disconnect_instrument`, `write_safe`, `query_safe`.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to connect to instrument. Let's make this happen! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    selected_resource = app_instance.selected_resource.get()
    if not selected_resource:
        console_print_func("⚠️ No instrument selected. Please refresh devices and select one. You gotta pick one, you know!")
        debug_log("No resource selected for connection. User is a lazy bastard.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    console_print_func(f"💬 Connecting to {selected_resource}...")
    try:
        inst = connect_to_instrument(selected_resource, console_print_func)
        if inst:
            app_instance.inst = inst
            # Query instrument identification
            idn_response = query_safe(inst, "*IDN?", console_print_func)
            if idn_response:
                parts = idn_response.strip().split(',')
                if len(parts) >= 4:
                    app_instance.instrument_model.set(parts[1].strip())
                    app_instance.instrument_serial.set(parts[2].strip())
                    app_instance.instrument_firmware.set(parts[3].strip())
                    # Attempt to get options if available (e.g., for Agilent/Keysight)
                    if len(parts) > 4: # Some instruments might have more parts
                        app_instance.instrument_options.set(parts[4].strip())
                    else:
                        app_instance.instrument_options.set("N/A")
                else:
                    app_instance.instrument_model.set(idn_response.strip()) # Fallback if IDN is not standard
                    app_instance.instrument_serial.set("N/A")
                    app_instance.instrument_firmware.set("N/A")
                    app_instance.instrument_options.set("N/A")
                debug_log(f"Instrument IDN: {idn_response.strip()}. Got the goods!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log("Failed to query *IDN? from instrument. What the hell went wrong?!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                console_print_func("❌ Failed to query instrument identification.")
                disconnect_instrument_logic(app_instance, console_print_func) # Disconnect on IDN failure
                return False

            # Query and display current settings
            if not query_current_settings_logic(app_instance, console_print_func):
                console_print_func("❌ Failed to query current instrument settings after connection. This is a disaster!")
                debug_log("Failed to query current settings after connection. What a mess!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                disconnect_instrument_logic(app_instance, console_print_func) # Disconnect on settings query failure
                return False

            console_print_func("✅ Instrument connected and identified successfully. We're in!")
            debug_log("Instrument connected and identified. Fucking awesome!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            app_instance.update_connection_status(True, is_scanning=False)
            return True
        else:
            console_print_func("❌ Failed to connect to instrument. Check resource string and connection. This is a goddamn mess!")
            debug_log("Failed to connect to instrument. What the hell went wrong?!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            app_instance.update_connection_status(False, is_scanning=False)
            return False
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error during connection: {e}. This is a critical error!")
        debug_log(f"VISA Error connecting to instrument: {e}. What a pain in the ass!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.inst = None
        app_instance.update_connection_status(False, is_scanning=False)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred during connection: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred during connection: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.inst = None
        app_instance.update_connection_status(False, is_scanning=False)
        return False

def disconnect_instrument_logic(app_instance, console_print_func):
    # Function Description:
    # Handles the disconnection process from the current VISA instrument.
    #
    # Inputs:
    # - app_instance: The main application instance, used to access Tkinter variables and update UI.
    # - console_print_func: A function to print messages to the GUI console.
    #
    # Process:
    # 1. Logs the start of the disconnection attempt.
    # 2. Calls `disconnect_instrument` to close the VISA session.
    # 3. Resets instrument-related UI elements and variables.
    # 4. Updates connection status and logs success or failure.
    #
    # Outputs:
    # - True if disconnection is successful, False otherwise.
    #
    # (2025-08-02) Change: Initial implementation.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Updated import for `disconnect_instrument` from `utils_instrument_connection`.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to disconnect instrument. Let's pull the plug! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if app_instance.inst:
        console_print_func("💬 Disconnecting instrument...")
        if disconnect_instrument(app_instance.inst, console_print_func):
            app_instance.inst = None
            app_instance.instrument_model.set("N/A")
            app_instance.instrument_serial.set("N/A")
            app_instance.instrument_firmware.set("N/A")
            app_instance.instrument_options.set("N/A")
            console_print_func("✅ Instrument disconnected successfully. Adios!")
            debug_log("Instrument disconnected. Mission accomplished!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            app_instance.update_connection_status(False, is_scanning=False)
            return True
        else:
            console_print_func("❌ Failed to disconnect instrument. This is a goddamn mess!")
            debug_log("Failed to disconnect instrument. What the hell went wrong?!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
    else:
        console_print_func("⚠️ No instrument is currently connected. Nothing to disconnect, you know!")
        debug_log("No instrument to disconnect. User is trying to disconnect a ghost.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

def apply_settings_logic(app_instance, console_print_func):
    # Function Description:
    # Applies the current settings from the GUI to the connected instrument.
    #
    # Inputs:
    # - app_instance: The main application instance, used to access Tkinter variables and retrieve settings.
    # - console_print_func: A function to print messages to the GUI console.
    #
    # Process:
    # 1. Logs the start of applying settings.
    # 2. Checks if an instrument is connected.
    # 3. Retrieves settings from Tkinter variables.
    # 4. Calls `initialize_instrument` to apply settings to the instrument.
    # 5. Logs success or failure.
    #
    # Outputs:
    # - True if settings are applied successfully, False otherwise.
    #
    # (2025-08-02) Change: Initial implementation.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Corrected call to `initialize_instrument` with correct arguments.
    # (2025-08-02) Change: Updated import for `initialize_instrument` from `utils_instrument_initialize`.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Applying settings to instrument. Let's dial this in! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot apply settings. You gotta connect first, you know!")
        debug_log("No instrument connected to apply settings. This is a goddamn mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    console_print_func("💬 Applying settings to instrument...")
    try:
        center_freq_hz = float(app_instance.center_freq_hz_var.get())
        span_hz = float(app_instance.span_hz_var.get())
        rbw_hz = float(app_instance.rbw_hz_var.get())
        vbw_hz = float(app_instance.vbw_hz_var.get())
        sweep_time_s = float(app_instance.sweep_time_s_var.get())
        ref_level_dbm = float(app_instance.reference_level_dbm_var.get())
        attenuation_db = int(app_instance.attenuation_var.get())
        freq_shift_hz = float(app_instance.freq_shift_var.get())
        maxhold_enabled = app_instance.maxhold_enabled_var.get()
        high_sensitivity_enabled = app_instance.high_sensitivity_var.get()
        preamp_on = app_instance.preamp_on_var.get()

        # Get the model match from app_instance.instrument_model
        model_match = app_instance.instrument_model.get()

        if initialize_instrument(
            app_instance.inst,
            ref_level_dbm,
            high_sensitivity_enabled,
            preamp_on,
            rbw_hz, # Passing rbw_hz as rbw_config_val
            vbw_hz, # Passing vbw_hz as vbw_config_val
            model_match,
            console_print_func
        ):
            console_print_func("✅ Settings applied successfully. Boom!")
            debug_log("Settings applied to instrument. Fucking awesome!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return True
        else:
            console_print_func("❌ Failed to apply settings. What the hell went wrong?!")
            debug_log("Failed to apply settings to instrument. This is a disaster!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
    except ValueError as e:
        console_print_func(f"❌ Invalid setting value: {e}. Please check your inputs. You entered some garbage!")
        debug_log(f"ValueError applying settings: {e}. User entered some crap.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while applying settings: {e}. This thing is a pain in the ass!")
        debug_log(f"An unexpected error occurred applying settings: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

def query_current_settings_logic(app_instance, console_print_func):
    # Function Description:
    # Queries the current settings from the connected instrument and updates the GUI.
    #
    # Inputs:
    # - app_instance: The main application instance, used to update Tkinter variables.
    # - console_print_func: A function to print messages to the GUI console.
    #
    # Process:
    # 1. Logs the start of querying settings.
    # 2. Checks if an instrument is connected.
    # 3. Calls `query_current_instrument_settings` to retrieve settings.
    # 4. Updates Tkinter variables with the retrieved values.
    # 5. Logs success or failure.
    #
    # Outputs:
    # - True if settings are queried and updated successfully, False otherwise.
    #
    # (2025-08-02) Change: Initial implementation.
    # (2025-08-02) Change: Updated debug file name to use `os.path.basename(__file__)`.
    # (2025-08-02) Change: Corrected call to `query_current_instrument_settings` with correct arguments.
    # (2025-08-02) Change: Updated import for `query_current_instrument_settings` from `utils_instrument_query_settings`.
    # (2025-08-02) Change: Updated import for `query_safe` from `utils_instrument_read_and_write`.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Querying current settings from instrument. Let's see what's going on! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot query settings. Connect first, you lazy bastard!")
        debug_log("No instrument connected to query settings. This is a goddamn mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    console_print_func("💬 Querying current settings from instrument...")
    try:
        # Pass MHZ_TO_HZ_CONVERSION to query_current_instrument_settings
        center_freq_mhz, span_mhz, rbw_hz = \
            query_current_instrument_settings(app_instance.inst, MHZ_TO_HZ_CONVERSION, console_print_func)

        # Update Tkinter variables
        if center_freq_mhz is not None:
            app_instance.center_freq_hz_var.set(center_freq_mhz * MHZ_TO_HZ_CONVERSION)
        if span_mhz is not None:
            app_instance.span_hz_var.set(span_mhz * MHZ_TO_HZ_CONVERSION)
        if rbw_hz is not None:
            app_instance.rbw_hz_var.set(rbw_hz)
        # The remaining variables (vbw_hz, sweep_time_s, ref_level_dbm, attenuation_db, freq_shift_hz)
        # are not returned by query_current_instrument_settings, so they need to be queried individually
        # or their updates removed if they are not meant to be updated here.
        # For now, I'm assuming they should be queried individually if needed.

        # Query VBW
        vbw_str = query_safe(app_instance.inst, ":SENSe:BANDwidth:VIDeo?", console_print_func)
        if vbw_str:
            app_instance.vbw_hz_var.set(float(vbw_str))
            debug_log(f"Queried VBW: {vbw_str.strip()} Hz.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Query Sweep Time
        sweep_time_str = query_safe(app_instance.inst, ":SENSe:SWEep:TIME?", console_print_func)
        if sweep_time_str:
            app_instance.sweep_time_s_var.set(float(sweep_time_str))
            debug_log(f"Queried Sweep Time: {sweep_time_str.strip()} s.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Query Reference Level
        ref_level_str = query_safe(app_instance.inst, ":DISPlay:WINDow:TRACe:Y:RLEVel?", console_print_func)
        if ref_level_str:
            ref_level_val = ref_level_str.strip().replace("DBM", "")
            app_instance.reference_level_dbm_var.set(float(ref_level_val))
            debug_log(f"Queried Reference Level: {ref_level_val} dBm.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Query Attenuation (assuming a command exists for it, if not, this will fail)
        # NOTE: There is no direct query for attenuation in utils_instrument_control.py's query_current_instrument_settings
        # I'm adding a placeholder query here. You might need to confirm the correct SCPI command.
        attenuation_str = query_safe(app_instance.inst, ":POWer:ATTenuation?", console_print_func) # Placeholder command
        if attenuation_str:
            app_instance.attenuation_var.set(int(float(attenuation_str))) # Attenuation is usually an integer
            debug_log(f"Queried Attenuation: {attenuation_str.strip()} dB.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        # Query Frequency Shift (assuming a command exists for it)
        # NOTE: There is no direct query for frequency shift in utils_instrument_control.py's query_current_instrument_settings
        # I'm adding a placeholder query here. You might need to confirm the correct SCPI command.
        freq_shift_str = query_safe(app_instance.inst, ":SENSe:FREQuency:SHIFt?", console_print_func) # Placeholder command
        if freq_shift_str:
            app_instance.freq_shift_var.set(float(freq_shift_str))
            debug_log(f"Queried Frequency Shift: {freq_shift_str.strip()} Hz.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


        # Query and update maxhold, high sensitivity, and preamp states
        maxhold_str = query_safe(app_instance.inst, ":DISPlay:WINDow:TRACe:MAXHold:STATe?", console_print_func)
        if maxhold_str:
            app_instance.maxhold_enabled_var.set(maxhold_str.strip().upper() == "ON")
            debug_log(f"Queried Maxhold State: {maxhold_str.strip()}. Good to go!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        preamp_str = query_safe(app_instance.inst, ":SENSe:POWer:RF:GAIN:STATe?", console_print_func)
        if preamp_str:
            app_instance.preamp_on_var.set(preamp_str.strip().upper() == "ON")
            debug_log(f"Queried Preamp State: {preamp_str.strip()}. Nice!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        high_sensitivity_str = query_safe(app_instance.inst, ":SENSe:POWer:RF:HSENse?", console_print_func)
        if high_sensitivity_str:
            app_instance.high_sensitivity_var.set(high_sensitivity_str.strip().upper() == "ON")
            debug_log(f"Queried High Sensitivity State: {high_sensitivity_str.strip()}. Sweet!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)

        console_print_func("✅ Current settings queried successfully from instrument. All systems go!")
        debug_log("Settings queried from instrument. UI updated! Fucking awesome!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while querying settings: {e}. This is a critical error!")
        debug_log(f"VISA Error querying settings: {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while querying settings: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred while querying settings: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
