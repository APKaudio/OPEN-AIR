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
# Version 20250802.1500.1 (Modified populate_resources_logic to return resources for direct combobox update.)

current_version = "20250802.1500.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 35 * 11 # Example hash, adjust as needed

import tkinter as tk
import pyvisa
import os
import time
import sys
import inspect # Import inspect module

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import necessary functions from utils.utils_instrument_control
from tabs.Instrument.utils_instrument_control import (
    connect_to_instrument, disconnect_instrument, write_safe, query_safe,
    initialize_instrument,
    list_visa_resources
)


# Constants
MHZ_TO_HZ_CONVERSION = 1_000_000.0
GHZ_TO_HZ_CONVERSION = 1_000_000_000.0

def populate_resources_logic(app_instance, console_print_func):
    """
    Function Description:
    Discovers available VISA resources (instruments) and attempts to set the
    selected resource in the application's Tkinter variable. It now returns
    the list of discovered resources for direct use by the GUI.

    Inputs to this function:
    - app_instance (object): The main application instance, providing access to shared Tkinter variables.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Logs the start of resource discovery.
    2. Calls `list_visa_resources` to get available instruments.
    3. If resources are found:
        a. Attempts to set `app_instance.selected_resource` to the last used resource from config.
        b. If no last used resource or it's not found, sets it to the first available resource.
        c. Prints a success message to the console.
    4. If no resources are found:
        a. Clears `app_instance.selected_resource`.
        b. Prints an error message to the console.
    5. Handles exceptions during resource listing.
    6. Ensures `app_instance.update_connection_status` is called.

    Outputs of this function:
    - list: A list of strings, where each string is a VISA resource name.
            Returns an empty list if no resources are found or an error occurs.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Searching for VISA instruments...")
    debug_log(f"Populating VISA resources. Let's find those devices! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)
    
    resources = [] # Initialize resources list
    try:
        resources = list_visa_resources(console_print_func)
        if resources:
            # Do NOT set app_instance.available_resources here.
            # The combobox's 'values' attribute will be set directly by the calling tab.
            
            # Attempt to select the last used resource from config
            last_selected = app_instance.config.get('LAST_USED_SETTINGS', 'last_instrument_connection__visa_resource', fallback='')
            if last_selected and last_selected in resources:
                app_instance.selected_resource.set(last_selected)
                debug_log(f"Restored last selected resource: {last_selected}. Found it!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.selected_resource.set(resources[0]) # Select the first one by default
                debug_log(f"Selected first available resource: {resources[0]}. Defaulting!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            console_print_func(f"✅ Found {len(resources)} VISA instruments. Ready to connect!")
        else:
            app_instance.selected_resource.set("")
            console_print_func("❌ No VISA instruments found. Check connections and drivers. What a mess!")
            debug_log("No VISA instruments found.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
    except Exception as e:
        console_print_func(f"❌ Error listing VISA resources: {e}. This is a disaster!")
        debug_log(f"Error listing VISA resources: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    finally:
        # Ensure UI is updated after resource population attempt
        app_instance.update_connection_status(app_instance.inst is not None)
        return resources # Return the list of resources


def connect_instrument_logic(app_instance, console_print_func):
    """
    Function Description:
    Connects to the selected VISA instrument.

    Inputs to this function:
    - app_instance (object): The main application instance, providing access to shared state.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Logs the connection attempt.
    2. Retrieves the selected resource name from `app_instance.selected_resource`.
    3. If no resource is selected, prints an error and returns False.
    4. Calls `connect_to_instrument` from `utils_instrument_control.py`.
    5. If connection is successful:
        a. Stores the instrument object in `app_instance.inst`.
        b. Queries instrument identification information (model, serial, firmware, options).
        c. Stores identification information in respective Tkinter variables in `app_instance`.
        d. Initializes the instrument.
        e. Updates connection status.
        f. Returns True.
    6. If connection fails:
        a. Clears instrument identification information.
        b. Updates connection status.
        c. Returns False.
    7. Handles exceptions during connection.

    Outputs of this function:
    - bool: True if connection is successful, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Connecting instrument...")
    debug_log(f"Attempting to connect instrument. Version: {current_version}. Let's get connected!",
                file=__file__,
                version=current_version,
                function=current_function)
    
    selected_resource = app_instance.selected_resource.get()
    if not selected_resource:
        console_print_func("❌ No instrument selected. Please select a resource first. You lazy bastard!")
        debug_log("No resource selected for connection.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        inst = connect_to_instrument(selected_resource, console_print_func)
        if inst:
            app_instance.rm = inst.resource_manager # Store the resource manager
            app_instance.inst = inst # Store the instrument object

            # Query instrument identification
            model = query_safe(inst, "*IDN?", console_print_func)
            if model:
                parts = model.strip().split(',')
                app_instance.instrument_model.set(parts[1].strip() if len(parts) > 1 else "Unknown Model")
                app_instance.instrument_serial.set(parts[2].strip() if len(parts) > 2 else "Unknown Serial")
                app_instance.instrument_firmware.set(parts[3].strip() if len(parts) > 3 else "Unknown Firmware")
                # Attempt to query options if supported by the model
                if app_instance.instrument_model.get() == "N9340B":
                    options = query_safe(inst, ":SYSTem:OPTion:CATalog?", console_print_func)
                    app_instance.instrument_options.set(options.strip() if options else "N/A")
                else:
                    app_instance.instrument_options.set("N/A (Model does not support options query)")

                console_print_func(f"✅ Instrument Identified: {app_instance.instrument_model.get()} (S/N: {app_instance.instrument_serial.get()})")
                debug_log(f"Instrument identified: Model={app_instance.instrument_model.get()}, Serial={app_instance.instrument_serial.get()}",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.instrument_model.set("N/A")
                app_instance.instrument_serial.set("N/A")
                app_instance.instrument_firmware.set("N/A")
                app_instance.instrument_options.set("N/A")
                console_print_func("⚠️ Could not query instrument identification. What a shame!")
                debug_log("Failed to query instrument identification.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            # Initialize instrument settings (e.g., reset, set defaults)
            initialize_instrument(inst, console_print_func)
            
            app_instance.update_connection_status(True) # Update UI to connected state
            return True
        else:
            app_instance.inst = None # Ensure inst is None if connection failed
            app_instance.instrument_model.set("N/A")
            app_instance.instrument_serial.set("N/A")
            app_instance.instrument_firmware.set("N/A")
            app_instance.instrument_options.set("N/A")
            app_instance.update_connection_status(False) # Update UI to disconnected state
            return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred during connection: {e}. This is a disaster!")
        debug_log(f"Unexpected error during connection: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        app_instance.inst = None
        app_instance.instrument_model.set("N/A")
        app_instance.instrument_serial.set("N/A")
        app_instance.instrument_firmware.set("N/A")
        app_instance.instrument_options.set("N/A")
        app_instance.update_connection_status(False)
        return False

def disconnect_instrument_logic(app_instance, console_print_func):
    """
    Function Description:
    Disconnects from the currently connected VISA instrument.

    Inputs to this function:
    - app_instance (object): The main application instance, providing access to shared state.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Logs the disconnection attempt.
    2. If an instrument is connected (`app_instance.inst` is not None):
        a. Calls `disconnect_instrument` from `utils_instrument_control.py`.
        b. If disconnection is successful, clears `app_instance.inst` and instrument info variables.
        c. Updates connection status.
        d. Returns True/False based on disconnection success.
    3. If no instrument is connected, logs a message and returns False.
    4. Handles exceptions during disconnection.

    Outputs of this function:
    - bool: True if disconnection is successful, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Disconnecting instrument...")
    debug_log(f"Attempting to disconnect instrument. Version: {current_version}. Goodbye!",
                file=__file__,
                version=current_version,
                function=current_function)
    
    if app_instance.inst:
        if disconnect_instrument(app_instance.inst, console_print_func):
            app_instance.inst = None
            app_instance.instrument_model.set("N/A")
            app_instance.instrument_serial.set("N/A")
            app_instance.instrument_firmware.set("N/A")
            app_instance.instrument_options.set("N/A")
            app_instance.update_connection_status(False) # Update UI to disconnected state
            return True
        else:
            debug_log("Failed to disconnect instrument cleanly.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            app_instance.update_connection_status(False) # Still update UI to disconnected even if error
            return False
    else:
        console_print_func("⚠️ No instrument to disconnect. Already disconnected, you moron!")
        debug_log("No instrument to disconnect.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False


def apply_instrument_settings_logic(app_instance, console_print_func):
    """
    Function Description:
    Applies the current settings from the GUI's Tkinter variables to the connected instrument.

    Inputs to this function:
    - app_instance (object): The main application instance, providing access to shared Tkinter variables and instrument object.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Logs the attempt to apply settings.
    2. Checks if an instrument is connected. If not, prints an error and returns False.
    3. Retrieves values from various Tkinter variables (center_freq, span, rbw, vbw, ref_level, preamp, high_sensitivity).
    4. Sends corresponding SCPI commands to the instrument using `write_safe`.
    5. Handles specific instrument model nuances (e.g., N9340B preamp command).
    6. Prints success or error messages to the console and debug log.
    7. Returns True on success, False on failure.

    Outputs of this function:
    - bool: True if settings are applied successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Applying settings to instrument...")
    debug_log(f"Attempting to apply instrument settings. Version: {current_version}. Let's get this done!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot apply settings. Connect first, you idiot!")
        debug_log("No instrument connected to apply settings.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        inst = app_instance.inst

        # Apply Center Frequency
        center_freq_hz = app_instance.center_freq_hz_var.get()
        write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", console_print_func)
        debug_log(f"Applied Center Frequency: {center_freq_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Span
        span_hz = app_instance.span_hz_var.get()
        write_safe(inst, f":SENSe:FREQuency:SPAN {span_hz}", console_print_func)
        debug_log(f"Applied Span: {span_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply RBW
        rbw_hz = app_instance.rbw_hz_var.get()
        write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", console_print_func)
        debug_log(f"Applied RBW: {rbw_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply VBW (if not auto)
        vbw_hz = app_instance.vbw_hz_var.get()
        write_safe(inst, f":SENSe:BANDwidth:VIDeo {vbw_hz}", console_print_func)
        debug_log(f"Applied VBW: {vbw_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Reference Level
        ref_level_dbm = app_instance.reference_level_dbm_var.get()
        # Ensure ref_level_dbm is a valid number before sending
        try:
            float(ref_level_dbm) # Try converting to float to validate
            write_safe(inst, f":DISPlay:WINdow:TRACe:Y:RLEVel {ref_level_dbm}DBM", console_print_func)
            debug_log(f"Applied Reference Level: {ref_level_dbm} dBm.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        except ValueError:
            console_print_func(f"⚠️ Invalid Reference Level value: '{ref_level_dbm}'. Not applying. Fix your shit!")
            debug_log(f"Invalid Reference Level value: '{ref_level_dbm}'. Skipping application.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


        # Apply Preamp (if instrument model supports it)
        if app_instance.instrument_model.get() == "N9340B":
            preamp_on = app_instance.preamp_on_var.get()
            preamp_state = "ON" if preamp_on else "OFF"
            write_safe(app_instance.inst, f":INPut:GAIN:STATe {preamp_state}", console_print_func)
            debug_log(f"Applied Preamp State: {preamp_state}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Preamp control not applicable for model: {app_instance.instrument_model.get()}. Skipping.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


        # Apply High Sensitivity
        high_sensitivity = app_instance.high_sensitivity_var.get()
        high_sensitivity_state = "ON" if high_sensitivity else "OFF"
        write_safe(app_instance.inst, f":SENSe:POWer:RF:HSENse {high_sensitivity_state}", console_print_func)
        debug_log(f"Applied High Sensitivity State: {high_sensitivity_state}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        console_print_func("✅ All settings applied to instrument.")
        debug_log("Settings applied to instrument. Hardware configured!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return True
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while applying settings: {e}. This is a critical error!")
        debug_log(f"VISA Error applying settings: {e}. What a mess!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while applying settings: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred while applying settings: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False


def query_current_instrument_settings_logic(app_instance, console_print_func):
    """
    Function Description:
    Queries the current settings from the connected instrument and updates
    the corresponding Tkinter variables in the GUI.

    Inputs to this function:
    - app_instance (object): The main application instance, providing access to shared Tkinter variables and instrument object.
    - console_print_func (function): Function to print messages to the GUI console.

    Process of this function:
    1. Logs the query attempt.
    2. Checks if an instrument is connected. If not, prints an error and returns False.
    3. Queries various settings (Center Freq, Span, RBW, VBW, Ref Level, Preamp, High Sensitivity)
        from the instrument using `query_safe`.
    4. Updates the respective Tkinter variables in `app_instance`.
    5. Handles specific instrument model nuances (e.g., N9340B preamp query).
    6. Prints success or error messages to the console and debug log.
    7. Returns True on success, False on failure.

    Outputs of this function:
    - bool: True if settings are queried successfully, False otherwise.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Querying current instrument settings...")
    debug_log(f"Attempting to query current instrument settings. Version: {current_version}. Let's get the facts!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected. Cannot query settings. Connect first, you idiot!")
        debug_log("No instrument connected to query settings.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    inst = app_instance.inst
    try:
        # Query Center Frequency
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            app_instance.center_freq_hz_var.set(float(center_freq_str))
            debug_log(f"Queried Center Frequency: {center_freq_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Span
        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            app_instance.span_hz_var.set(float(span_str))
            debug_log(f"Queried Span: {span_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query RBW
        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            app_instance.rbw_hz_var.set(float(rbw_str))
            debug_log(f"Queried RBW: {rbw_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query VBW
        vbw_str = query_safe(inst, ":SENSe:BANDwidth:VIDeo?", console_print_func)
        if vbw_str:
            app_instance.vbw_hz_var.set(float(vbw_str))
            debug_log(f"Queried VBW: {vbw_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Sweep Time
        sweep_time_str = query_safe(inst, ":SENSe:SWEep:TIME?", console_print_func)
        if sweep_time_str:
            app_instance.sweep_time_s_var.set(float(sweep_time_str))
            debug_log(f"Queried Sweep Time: {sweep_time_str.strip()} s.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Reference Level
        ref_level_str = query_safe(inst, ":DISPlay:WINdow:TRACe:Y:RLEVel?", console_print_func)
        if ref_level_str:
            # Remove "DBM" suffix if present and convert to float
            ref_level_val = ref_level_str.strip().replace("DBM", "")
            app_instance.reference_level_dbm_var.set(ref_level_val)
            debug_log(f"Queried Reference Level: {ref_level_val} dBm.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Preamp (if instrument model supports it)
        if app_instance.instrument_model.get() == "N9340B":
            preamp_state_str = query_safe(inst, ":INPut:GAIN:STATe?", console_print_func)
            if preamp_state_str:
                app_instance.preamp_on_var.set(preamp_state_str.strip().upper() == "ON")
                debug_log(f"Queried Preamp State: {preamp_state_str.strip()}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            debug_log(f"Preamp query not applicable for model: {app_instance.instrument_model.get()}. Skipping.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


        # Query High Sensitivity
        high_sensitivity_str = query_safe(inst, ":SENSe:POWer:RF:HSENse?", console_print_func)
        if high_sensitivity_str:
            app_instance.high_sensitivity_var.set(high_sensitivity_str.strip().upper() == "ON")
            debug_log(f"Queried High Sensitivity State: {high_sensitivity_str.strip()}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        console_print_func("✅ Current settings queried successfully from instrument.")
        debug_log("Settings queried from instrument. UI updated!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return True
    except pyvisa.errors.VisaIOError as e:
        console_print_func(f"❌ VISA error while querying settings: {e}. This is a critical error!")
        debug_log(f"VISA Error querying settings: {e}. What a mess!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred while querying settings: {e}. This is a disaster!")
        debug_log(f"An unexpected error occurred while querying settings: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

