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
# Version 20250802.0205.1 (Removed direct Tkinter variable manipulation from populate_resources_logic.)

current_version = "20250802.0205.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 35 * 2 # Example hash, adjust as needed

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
from utils.utils_instrument_control import (
    list_visa_resources, connect_to_instrument, disconnect_instrument,
    initialize_instrument, write_safe, query_safe
)
from ref.frequency_bands import MHZ_TO_HZ, VBW_RBW_RATIO # Import VBW_RBW_RATIO
from src.config_manager import save_config # Import save_config


def populate_resources_logic(rm_instance, console_print_func=None):
    """
    Function Description:
    Discovers available VISA resources using the provided ResourceManager.

    Inputs:
    - rm_instance (pyvisa.ResourceManager): The PyVISA ResourceManager instance.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Calls `list_visa_resources` to get a list of available resources.
    3. Returns the list of resources.

    Outputs of this function:
    - list: A list of discovered VISA resource strings.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Populating VISA resources. Let's find those devices!",
                file=__file__,
                version=current_version,
                function=current_function)

    resources = list_visa_resources(rm_instance, console_print_func) # Pass rm_instance to list_visa_resources
    
    # This function should only return the resources. The UI update is handled by the caller.
    return resources


def connect_instrument_logic(app_instance, resource_name, console_print_func=None):
    """
    Function Description:
    Handles the connection process to the selected VISA instrument.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `selected_resource`, `inst`, `model_match`, and config.
    - resource_name (str): The name of the VISA resource to connect to.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Retrieves the selected resource name.
    3. If already connected, disconnects first.
    4. Calls `connect_to_instrument` to establish the connection.
    5. If connection is successful:
       a. Queries instrument IDN to determine model.
       b. Calls `initialize_instrument` to set up basic instrument parameters.
       c. Queries current settings and updates GUI.
       d. Saves the selected resource to config.
    6. Updates GUI connection status.

    Outputs of this function:
    - None. Modifies `app_instance.inst` and `app_instance.model_match`, updates GUI.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Attempting to connect to instrument. This is the moment of truth!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not resource_name or resource_name == "N/A": # Check for "N/A" as well
        console_print_func("⚠️ Please select a valid VISA resource first. Can't connect to nothing!")
        debug_log("No valid resource selected. Connection aborted.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False # Return False to indicate connection failure

    # Disconnect if already connected to prevent multiple connections
    if app_instance.inst:
        disconnect_instrument_logic(app_instance, console_print_func)

    inst = connect_to_instrument(app_instance.rm, resource_name, console_print_func) # Pass rm_instance
    app_instance.inst = inst # Store the instrument instance in app_instance

    if inst:
        try:
            # Query instrument IDN to determine model
            idn_response = query_safe(inst, "*IDN?", console_print_func)
            if idn_response:
                model_match = "UNKNOWN"
                if "N9342CN" in idn_response:
                    model_match = "N9342CN"
                elif "N9340B" in idn_response:
                    model_match = "N9340B"
                app_instance.instrument_model = model_match # Use app_instance.instrument_model
                console_print_func(f"✅ Connected to: {idn_response.strip()} (Model: {model_match}). Identified!")
                debug_log(f"Instrument IDN: {idn_response.strip()}, Model: {model_match}. Device recognized!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.instrument_model = "UNKNOWN"
                console_print_func("❌ Could not query instrument IDN. Model unknown. This is problematic!")
                debug_log("Could not query instrument IDN. Model unknown.",
                            file=__file__,
                            version=current_version,
                            function=current_function)

            # Initialize instrument with basic settings
            init_success = initialize_instrument(
                inst,
                float(app_instance.reference_level_dbm_var.get()),
                app_instance.high_sensitivity_var.get(),
                app_instance.preamp_on_var.get(),
                float(app_instance.rbw_hz_var.get()),
                float(app_instance.vbw_hz_var.get()),
                app_instance.instrument_model, # Use app_instance.instrument_model
                console_print_func
            )

            if not init_success:
                console_print_func("❌ Failed to initialize instrument. Disconnecting. What a mess!")
                debug_log("Instrument initialization failed. Disconnecting.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                disconnect_instrument_logic(app_instance, console_print_func)
                return False # Indicate connection failure

            # Query and display current settings after initialization
            query_current_instrument_settings_logic(app_instance, console_print_func)

            # Save the successfully connected resource to config
            app_instance.config.set('LAST_USED_SETTINGS', 'last_selected_visa_resource', resource_name)
            save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_print_func, app_instance)
            debug_log(f"Saved last selected resource: {resource_name}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return True # Indicate successful connection

        except Exception as e:
            console_print_func(f"❌ Error during instrument setup after connection: {e}. This is a disaster!")
            debug_log(f"Error during instrument setup after connection: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            disconnect_instrument_logic(app_instance, console_print_func)
            return False # Indicate connection failure
    else:
        console_print_func("❌ Failed to connect to instrument. Check resource name and physical connection!")
        debug_log("Failed to connect to instrument. Connection failed!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False # Indicate connection failure

    # This line is unreachable if the above returns are hit, but good for completeness
    # app_instance.update_connection_status(app_instance.inst is not None)
    # debug_log("Instrument connection process complete. Status updated!",
    #             file=__file__,
    #             version=current_version,
    #             function=current_function)


def disconnect_instrument_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Handles the disconnection process from the instrument.

    Inputs:
    - app_instance (object): The main application instance, used to access `inst` and `instrument_model`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Calls `disconnect_instrument` to close the connection.
    3. Clears `app_instance.inst` and `app_instance.instrument_model`.
    4. Clears instrument settings displayed in the GUI.
    5. Updates GUI connection status.

    Outputs of this function:
    - None. Clears `app_instance` attributes and updates GUI.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Attempting to disconnect instrument. Time to say goodbye!",
                file=__file__,
                version=current_version,
                function=current_function)

    if app_instance.inst:
        disconnect_instrument(app_instance.inst, console_print_func)
        app_instance.inst = None
        app_instance.instrument_model = None # Clear instrument model on disconnect
        console_print_func("✅ Instrument disconnected from application.")
        debug_log("Instrument instance cleared from app_instance.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    else:
        console_print_func("ℹ️ No instrument is currently connected to disconnect.")
        debug_log("No instrument to disconnect. Already disconnected!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Clear displayed settings in GUI
    if hasattr(app_instance, 'instrument_parent_tab') and \
       hasattr(app_instance.instrument_parent_tab, 'instrument_connection_tab'):
        app_instance.instrument_parent_tab.instrument_connection_tab._clear_settings_display()
        debug_log("Cleared instrument settings display in GUI.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
    app_instance.update_connection_status(app_instance.inst is not None)
    debug_log("Instrument disconnection process complete. Status updated!",
                file=__file__,
                version=current_version,
                function=current_function)
    return True # Indicate successful disconnection


def query_current_instrument_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Queries the currently connected instrument for its settings (Center Freq, Span, RBW, VBW,
    Reference Level, Preamp, High Sensitivity) and updates the corresponding Tkinter
    variables in the main application instance.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `inst` and various Tkinter variables for settings.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Checks if an instrument is connected. If not, logs an error and returns False.
    3. Queries each setting using `query_safe` and updates the corresponding Tkinter variable.
    4. Handles special cases for unit conversion (Hz to GHz/MHz/kHz) and boolean states.
    5. Logs success or error messages.

    Outputs of this function:
    - bool: True if all settings were successfully queried and updated, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying current instrument settings. Getting the scoop!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ Not connected to an instrument. Cannot query settings.")
        debug_log("No instrument connected for querying. Aborting.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Query Center Frequency
        center_freq_str = query_safe(app_instance.inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            app_instance.center_freq_hz_var.set(float(center_freq_str))
            debug_log(f"Queried Center Frequency: {center_freq_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.center_freq_hz_var.set(0.0)
            debug_log("🚫🐛 Could not determine Center Frequency. Setting to 0 Hz. This is a **fucking nightmare**!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Span
        span_str = query_safe(app_instance.inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            app_instance.span_hz_var.set(float(span_str))
            debug_log(f"Queried Span: {span_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.span_hz_var.set(0.0)
            debug_log("🚫🐛 Could not determine Span. Setting to 0 Hz. This is a **fucking nightmare**!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query RBW
        rbw_str = query_safe(app_instance.inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            app_instance.rbw_hz_var.set(float(rbw_str))
            debug_log(f"Queried RBW: {rbw_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.rbw_hz_var.set(0.0)
            debug_log("🚫🐛 Could not determine RBW. Setting to 0 Hz. This is a **fucking nightmare**!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query VBW
        vbw_str = query_safe(app_instance.inst, ":SENSe:BANDwidth:VIDeo?", console_print_func)
        if vbw_str:
            app_instance.vbw_hz_var.set(float(vbw_str))
            debug_log(f"Queried VBW: {vbw_str.strip()} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.vbw_hz_var.set(0.0)
            debug_log("🚫🐛 Could not determine VBW. Setting to 0 Hz. This is a **fucking nightmare**!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Reference Level
        ref_level_str = query_safe(app_instance.inst, ":DISPlay:WINdow:TRACe:Y:RLEVel?", console_print_func)
        if ref_level_str:
            app_instance.reference_level_dbm_var.set(float(ref_level_str))
            debug_log(f"Queried Reference Level: {ref_level_str.strip()} dBm.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.reference_level_dbm_var.set(-40.0) # Default if cannot query
            debug_log("🚫🐛 Could not determine Reference Level. Setting to -40 dBm. This is a **fucking nightmare**!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Preamp State (N9340B specific)
        if app_instance.instrument_model == "N9340B":
            preamp_str = query_safe(app_instance.inst, ":INPut:GAIN:STATe?", console_print_func)
            if preamp_str:
                app_instance.preamp_on_var.set(preamp_str.strip().upper() == "ON")
                debug_log(f"Queried Preamp State: {preamp_str.strip()}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.preamp_on_var.set(False)
                debug_log("🚫🐛 Could not determine Preamp state due to empty query response. Setting to OFF. This is a **fucking nightmare**!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            app_instance.preamp_on_var.set(False) # Default for other models
            debug_log("Preamp query skipped for non-N9340B model.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query High Sensitivity State (N9342CN specific)
        if app_instance.instrument_model == "N9342CN":
            high_sensitivity_str = query_safe(app_instance.inst, ":SENSe:POWer:RF:HSENse?", console_print_func)
            if high_sensitivity_str:
                app_instance.high_sensitivity_var.set(high_sensitivity_str.strip().upper() == "ON")
                debug_log(f"Queried High Sensitivity State: {high_sensitivity_str.strip()}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.high_sensitivity_var.set(False)
                debug_log("🚫🐛 Could not determine High Sensitivity state due to empty query response. Setting to OFF. This is a **fucking nightmare**!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            app_instance.high_sensitivity_var.set(False) # Default for other models
            debug_log("High Sensitivity query skipped for non-N9342CN model.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Ensure the Tkinter variables are updated on the main thread
        # This is crucial for the UI to reflect the changes immediately
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_center_freq_var.set(f"{app_instance.center_freq_hz_var.get() / 1e9:.3f} GHz"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_span_var.set(f"{app_instance.span_hz_var.get() / 1e6:.3f} MHz"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_rbw_var.set(f"{app_instance.rbw_hz_var.get() / 1e3:.3f} kHz"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_vbw_var.set(f"{app_instance.vbw_hz_var.get() / 1e3:.3f} kHz"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_ref_level_var.set(f"{app_instance.reference_level_dbm_var.get()} dBm"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_preamp_var.set("ON" if app_instance.preamp_on_var.get() else "OFF"))
        app_instance.after(0, lambda: app_instance.instrument_parent_tab.instrument_connection_tab.current_high_sensitivity_var.set("ON" if app_instance.high_sensitivity_var.get() else "OFF"))

        console_print_func("✅ Current instrument settings updated in GUI. All values retrieved!")
        debug_log("Current instrument settings updated in GUI. UI synced!",
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


def apply_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Applies the current settings from the GUI's Tkinter variables to the connected instrument.
    This includes Center Frequency, Span, RBW, Reference Level, Frequency Shift, High Sensitivity,
    and Preamplifier.

    Inputs:
    - app_instance (object): The main application instance, used to access `inst` and
                             various Tkinter variables for settings.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Checks if an instrument is connected. If not, logs an error and returns False.
    3. Retrieves current values from Tkinter variables.
    4. Applies each setting to the instrument using `write_safe`.
    5. Handles specific commands for different instrument models (e.g., N9340B vs N9342CN).
    6. Logs success or error messages.

    Outputs of this function:
    - bool: True if all settings were successfully applied, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Applying settings to instrument. Making it happen!",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ Not connected to an instrument. Cannot apply settings.")
        debug_log("No instrument connected for applying settings. Aborting.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Get values from Tkinter variables
        center_freq = app_instance.center_freq_hz_var.get()
        span = app_instance.span_hz_var.get()
        rbw = app_instance.rbw_hz_var.get()
        vbw = app_instance.vbw_hz_var.get()
        ref_level = app_instance.reference_level_dbm_var.get()
        preamp_on = app_instance.preamp_on_var.get()
        high_sensitivity = app_instance.high_sensitivity_var.get()
        freq_shift = app_instance.freq_shift_hz_var.get()

        # Apply Center Frequency
        write_safe(app_instance.inst, f":SENSe:FREQuency:CENTer {center_freq}", console_print_func)
        debug_log(f"Applied Center Frequency: {center_freq} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Span
        write_safe(app_instance.inst, f":SENSe:FREQuency:SPAN {span}", console_print_func)
        debug_log(f"Applied Span: {span} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply RBW
        write_safe(app_instance.inst, f":SENSe:BANDwidth:RESolution {rbw}", console_print_func)
        debug_log(f"Applied RBW: {rbw} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply VBW
        write_safe(app_instance.inst, f":SENSe:BANDwidth:VIDeo {vbw}", console_print_func)
        debug_log(f"Applied VBW: {vbw} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Reference Level
        write_safe(app_instance.inst, f":DISPlay:WINdow:TRACe:Y:RLEVel {ref_level}", console_print_func)
        debug_log(f"Applied Reference Level: {ref_level} dBm.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Frequency Shift (if applicable)
        if freq_shift != 0: # Only apply if there's a shift
            write_safe(app_instance.inst, f":SENSe:FREQuency:RF:SHIFt {freq_shift}", console_print_func)
            debug_log(f"Applied Frequency Shift: {freq_shift} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Apply Preamp State (N9340B specific)
        if app_instance.instrument_model == "N9340B":
            preamp_state = "ON" if preamp_on else "OFF"
            write_safe(app_instance.inst, f":INPut:GAIN:STATe {preamp_state}", console_print_func)
            debug_log(f"Applied Preamp State: {preamp_state}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Apply High Sensitivity State (N9342CN specific)
        elif app_instance.instrument_model == "N9342CN":
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
