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
# Version 20250802.0030.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0030.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 30 * 1 # Example hash, adjust as needed

import tkinter as tk
import pyvisa
import os
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


def populate_resources_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Discovers available VISA resources and populates the GUI's resource dropdown.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `resource_names` Tkinter variable and `inst`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Calls `list_visa_resources` to get a list of available resources.
    3. Updates `app_instance.resource_names` with the discovered resources.
    4. If no resources are found, updates the GUI message accordingly.
    5. If already connected to an instrument that is not in the new list,
       disconnects from it.

    Outputs of this function:
    - None. Updates Tkinter variables and may disconnect the instrument.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Populating VISA resources. Let's find those devices!",
                file=__file__,
                version=current_version,
                function=current_function)

    resources = list_visa_resources(console_print_func)
    app_instance.resource_names.set(" ".join(resources)) # Update the Tkinter variable
    app_instance.resource_dropdown['values'] = resources # Update dropdown values

    if not resources:
        console_print_func("⚠️ No VISA instruments found. Is NI-VISA installed? Check connections!")
        debug_log("No VISA resources found. This is problematic!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        app_instance.selected_resource.set("") # Clear selection if no resources
    else:
        # If currently connected instrument is no longer in the list, disconnect
        if app_instance.inst and app_instance.inst.resource_name not in resources:
            console_print_func("⚠️ Connected instrument no longer found in resource list. Disconnecting...")
            debug_log("Connected instrument not in new resource list. Forcing disconnect.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            disconnect_instrument_logic(app_instance, console_print_func)
        
        # If there's a previously selected resource, try to re-select it if it's still available
        last_selected = app_instance.config.get('LAST_USED_SETTINGS', 'last_selected_resource', fallback='')
        if last_selected in resources:
            app_instance.selected_resource.set(last_selected)
            console_print_func(f"✅ Re-selected last used resource: {last_selected}.")
            debug_log(f"Re-selected last used resource: {last_selected}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        elif resources:
            # Otherwise, select the first one found
            app_instance.selected_resource.set(resources[0])
            console_print_func(f"✅ Selected first available resource: {resources[0]}.")
            debug_log(f"Selected first available resource: {resources[0]}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            app_instance.selected_resource.set("") # No resources, clear selection

    app_instance.update_connection_status(app_instance.inst is not None)
    debug_log("VISA resource population complete. Dropdown updated!",
                file=__file__,
                version=current_version,
                function=current_function)


def connect_instrument_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Handles the connection process to the selected VISA instrument.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `selected_resource`, `inst`, `model_match`, and config.
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

    resource_name = app_instance.selected_resource.get()
    if not resource_name:
        console_print_func("⚠️ Please select a VISA resource first. Can't connect to nothing!")
        debug_log("No resource selected. Connection aborted.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return

    # Disconnect if already connected to prevent multiple connections
    if app_instance.inst:
        disconnect_instrument_logic(app_instance, console_print_func)

    inst = connect_to_instrument(resource_name, console_print_func)
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
                app_instance.model_match = model_match
                console_print_func(f"✅ Connected to: {idn_response.strip()} (Model: {model_match}). Identified!")
                debug_log(f"Instrument IDN: {idn_response.strip()}, Model: {model_match}. Device recognized!",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                app_instance.model_match = "UNKNOWN"
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
                app_instance.model_match,
                console_print_func
            )

            if not init_success:
                console_print_func("❌ Failed to initialize instrument. Disconnecting. What a mess!")
                debug_log("Instrument initialization failed. Disconnecting.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                disconnect_instrument_logic(app_instance, console_print_func)
                return

            # Query and display current settings after initialization
            query_current_instrument_settings_logic(app_instance, console_print_func)

            # Save the successfully connected resource to config
            app_instance.config.set('LAST_USED_SETTINGS', 'last_selected_resource', resource_name)
            save_config(app_instance.config, app_instance.CONFIG_FILE_PATH, console_print_func, app_instance)
            debug_log(f"Saved last selected resource: {resource_name}.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        except Exception as e:
            console_print_func(f"❌ Error during instrument setup after connection: {e}. This is a disaster!")
            debug_log(f"Error during instrument setup after connection: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            disconnect_instrument_logic(app_instance, console_print_func)
    else:
        console_print_func("❌ Failed to connect to instrument. Check resource name and physical connection!")
        debug_log("Failed to connect to instrument. Connection failed!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    app_instance.update_connection_status(app_instance.inst is not None)
    debug_log("Instrument connection process complete. Status updated!",
                file=__file__,
                version=current_version,
                function=current_function)


def disconnect_instrument_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Handles the disconnection process from the instrument.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `inst` and `model_match`.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Calls `disconnect_instrument` to close the connection.
    3. Clears `app_instance.inst` and `app_instance.model_match`.
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
        app_instance.model_match = None
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


def apply_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Applies the current settings from the GUI's Tkinter variables to the connected instrument.
    This includes Center Frequency, Span, RBW, Reference Level, Frequency Shift,
    High Sensitivity, and Preamplifier.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `inst` and various Tkinter variables.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Checks if an instrument is connected.
    3. Retrieves current settings from Tkinter variables.
    4. Sends SCPI commands using `write_safe` to apply each setting.
    5. Handles potential errors during application.
    6. Queries and updates the displayed settings after application.

    Outputs of this function:
    - bool: True if all settings were applied successfully, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Attempting to apply settings to instrument. Making changes!",
                file=__file__,
                version=current_version,
                function=current_function)

    inst = app_instance.inst
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot apply settings. Connect the damn thing first!")
        debug_log("Instrument not connected for apply_settings_logic. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    success = True
    try:
        center_freq_hz = float(app_instance.center_freq_hz_var.get())
        span_hz = float(app_instance.span_hz_var.get())
        rbw_hz = float(app_instance.rbw_hz_var.get())
        ref_level_dbm = float(app_instance.reference_level_dbm_var.get())
        freq_shift_hz = float(app_instance.freq_shift_hz_var.get())
        high_sensitivity_on = app_instance.high_sensitivity_var.get()
        preamp_on = app_instance.preamp_on_var.get()

        # Apply Center Frequency
        if not write_safe(inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", console_print_func): success = False
        time.sleep(0.05)

        # Apply Span
        span_cmd = f":SENSe:FREQuency:SPAN {span_hz}"
        if span_hz == 0.0: # Special case for "Full Span"
            span_cmd = ":SENSe:FREQuency:SPAN MAX"
        if not write_safe(inst, span_cmd, console_print_func): success = False
        time.sleep(0.05)

        # Apply RBW
        if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", console_print_func): success = False
        time.sleep(0.05)

        # Apply Reference Level
        if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", console_print_func): success = False
        time.sleep(0.05)

        # Apply Frequency Shift
        if not write_safe(inst, f":SENSe:FREQuency:RFShift {freq_shift_hz}", console_print_func): success = False
        time.sleep(0.05)

        # Apply High Sensitivity
        # This command is specific to N9342CN, so check model_match
        if app_instance.model_match == "N9342CN":
            high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
            if not write_safe(inst, high_sensitivity_cmd, console_print_func): success = False
            time.sleep(0.05)
        elif high_sensitivity_on:
            console_print_func(f"ℹ️ High Sensitivity (HSENsitive) command skipped for model {app_instance.model_match}. It's specific to N9342CN. Not applicable!")
            debug_log(f"High Sensitivity (HSENsitive) command skipped for model {app_instance.model_match}. Not supported!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Apply Preamplifier
        preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
        if not write_safe(inst, preamp_cmd, console_print_func): success = False
        time.sleep(0.05)

        if success:
            console_print_func("✅ All settings applied to instrument. Looking good!")
            debug_log("All settings applied successfully.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            console_print_func("❌ Failed to apply all settings to instrument. This is a disaster!")
            debug_log("Failed to apply all settings to instrument. What a mess!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Refresh the displayed settings in the GUI after applying
        query_current_instrument_settings_logic(app_instance, console_print_func)
        return success

    except Exception as e:
        console_print_func(f"❌ An error occurred while applying settings: {e}. This is a critical bug!")
        debug_log(f"Error applying settings: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False


def query_current_instrument_settings_logic(app_instance, console_print_func=None):
    """
    Function Description:
    Queries the current instrument settings (Center Freq, Span, RBW, Ref Level,
    Freq Shift, High Sensitivity, Preamp) and updates the corresponding Tkinter
    variables in the GUI.

    Inputs:
    - app_instance (object): The main application instance, used to access
                             `inst` and various Tkinter variables.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Prints a debug message.
    2. Checks if an instrument is connected.
    3. Queries each setting using `query_safe`.
    4. Updates the respective Tkinter variables.
    5. Special logic for High Sensitivity, which depends on Attenuation and Gain states.
    6. Logs success or failure.

    Outputs of this function:
    - bool: True if settings were queried and updated successfully, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Querying current instrument settings. Getting the latest info!",
                file=__file__,
                version=current_version,
                function=current_function)

    inst = app_instance.inst
    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot query settings. Connect the damn thing first!")
        debug_log("Instrument not connected for query_current_instrument_settings_logic. Fucking useless!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Query Center Frequency
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_center_freq_var.set(f"{float(center_freq_str) / MHZ_TO_HZ:.3f}")

        # Query Span
        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_span_var.set(f"{float(span_str) / MHZ_TO_HZ:.3f}")

        # Query RBW
        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_rbw_var.set(f"{float(rbw_str):.0f}")

        # Query Reference Level
        ref_level_str = query_safe(inst, ":DISPlay:WINDow:TRACe:Y:RLEVel?", console_print_func)
        if ref_level_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_ref_level_var.set(f"{float(ref_level_str):.1f}")

        # Query Frequency Shift
        freq_shift_str = query_safe(inst, ":SENSe:FREQuency:RFShift?", console_print_func)
        if freq_shift_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_freq_shift_var.set(f"{float(freq_shift_str):.0f}")

        # Query Preamplifier State
        preamp_state_str = query_safe(inst, ":POWer:GAIN?", console_print_func)
        if preamp_state_str:
            app_instance.instrument_parent_tab.instrument_connection_tab.current_preamp_var.set("ON" if "1" in preamp_state_str else "OFF")

        # Query High Sensitivity State (N9342CN specific)
        if app_instance.model_match == "N9342CN":
            high_sensitivity_state_str = query_safe(inst, ":SENSe:POWer:RF:HSENs?", console_print_func)
            if high_sensitivity_state_str:
                app_instance.instrument_parent_tab.instrument_connection_tab.current_high_sensitivity_var.set("Enabled" if "1" in high_sensitivity_state_str else "Disabled")
            else:
                app_instance.instrument_parent_tab.instrument_connection_tab.current_high_sensitivity_var.set("Disabled")
                debug_log("Could not query High Sensitivity state from N9342CN. Setting to Disabled.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
        else:
            # For other models, high sensitivity is typically attenuation off and preamp on
            atten_auto_str_safe = query_safe(inst, ":POWer:ATTenuation:AUTO?", console_print_func)
            gain_state_str_safe = query_safe(inst, ":POWer:GAIN?", console_print_func)

            if atten_auto_str_safe and gain_state_str_safe:
                # High sensitivity is typically attenuation off and preamp on
                app_instance.instrument_parent_tab.instrument_connection_tab.current_high_sensitivity_var.set("Enabled" if ("OFF" in atten_auto_str_safe.upper() and "ON" in gain_state_str_safe.upper()) else "Disabled")
            else:
                # If queries failed or returned empty, set to Disabled or a default
                app_instance.instrument_parent_tab.instrument_connection_tab.current_high_sensitivity_var.set("Disabled")
                debug_log("🚫🐛 Could not determine High Sensitivity state due to empty query responses. Setting to Disabled. This is a **fucking nightmare**!",
                            file=__file__,
                            version=current_version,
                            function=current_function)


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
