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
# Version 20250802.0205.11 (Conditional query for :INPut:GAIN:STATe? based on instrument model.)

current_version = "20250802.0205.11" # this variable should always be defined below the header to make the debugging better
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
# (2025-08-02 12:40) Change: Wrapped long import statement in parentheses for explicit line continuation.
# (2025-08-02 12:50) Change: Corrected function names to match those defined in utils_instrument_control.py.
# (2025-08-02 12:55) Change: Re-confirmed the corrected import for connect_to_instrument.
# (2025-08-02 12:58) Change: Removed import of save_preset_state and load_preset_state as they are not found in utils_instrument_control.py.
# (2025-08-02 13:05) Change: Removed import of query_instrument_model, query_instrument_serial_number, query_instrument_firmware, query_instrument_options, query_instrument_error_queue as they are not implemented in utils_instrument_control.py.
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
    Populates the VISA resource dropdown with available instruments.
    This function is now responsible for updating the Tkinter variable directly.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Searching for VISA instruments...")
    debug_log(f"Populating VISA resources. Let's find those devices! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)
    
    try:
        resources = list_visa_resources(console_print_func)
        if resources:
            app_instance.available_resources.set(resources)
            
            # Attempt to select the last used resource from config
            last_selected = app_instance.config.get('LAST_USED_SETTINGS', 'selected_resource', fallback='')
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
            app_instance.available_resources.set([])
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


def connect_instrument_logic(app_instance, console_print_func):
    """
    Connects to the selected VISA instrument.
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
        # Pass the console_print_func to connect_to_instrument
        inst = connect_to_instrument(selected_resource, console_print_func) # Corrected function name
        if inst:
            app_instance.inst = inst
            # Removed calls to non-existent query functions
            app_instance.instrument_model = "N/A" # Default or query if implemented elsewhere
            app_instance.instrument_serial = "N/A" # Default or query if implemented elsewhere
            app_instance.instrument_firmware = "N/A" # Default or query if implemented elsewhere
            app_instance.instrument_options = "N/A" # Default or query if implemented elsewhere
            
            console_print_func(f"✅ Connected to {selected_resource}")
            console_print_func(f"ℹ️ Model: {app_instance.instrument_model}, S/N: {app_instance.instrument_serial}, FW: {app_instance.instrument_firmware}")
            debug_log(f"Successfully connected to {selected_resource}. Model: {app_instance.instrument_model}. We're in!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return True
        else:
            app_instance.inst = None
            app_instance.instrument_model = "N/A"
            app_instance.instrument_serial = "N/A"
            app_instance.instrument_firmware = "N/A"
            app_instance.instrument_options = "N/A"
            console_print_func("❌ Failed to connect to instrument. Check connection. What a mess!")
            debug_log("Failed to connect to instrument.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return False
    except Exception as e:
        app_instance.inst = None
        app_instance.instrument_model = "N/A"
        app_instance.instrument_serial = "N/A"
        app_instance.instrument_firmware = "N/A"
        app_instance.instrument_options = "N/A"
        console_print_func(f"❌ Error connecting to instrument: {e}. This is a disaster!")
        debug_log(f"Error connecting to instrument: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    finally:
        app_instance.update_connection_status(app_instance.inst is not None)


def disconnect_instrument_logic(app_instance, console_print_func):
    """
    Disconnects the currently connected VISA instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Disconnecting instrument...")
    debug_log(f"Attempting to disconnect instrument. Time to say goodbye! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)

    if app_instance.inst:
        try:
            disconnect_instrument(app_instance.inst, console_print_func)
            app_instance.inst = None
            app_instance.instrument_model = "N/A"
            app_instance.instrument_serial = "N/A"
            app_instance.instrument_firmware = "N/A"
            app_instance.instrument_options = "N/A"
            console_print_func("✅ Instrument disconnected. See ya!")
            debug_log("Instrument disconnected successfully.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return True
        except Exception as e:
            console_print_func(f"❌ Error disconnecting instrument: {e}. This is a disaster!")
            debug_log(f"Error disconnecting instrument: {e}. Fucking hell!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return False
        finally: # Corrected indentation: This finally block belongs to the try/except above
            app_instance.update_connection_status(app_instance.inst is not None)
    else:
        console_print_func("ℹ️ No instrument connected to disconnect. Nothing to do here!")
        debug_log("No instrument connected to disconnect.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return True # Considered successful if nothing to disconnect


def query_current_instrument_settings_logic(app_instance, console_print_func):
    """
    Queries the current settings from the connected instrument and updates the GUI.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Querying current instrument settings...")
    debug_log(f"Querying current instrument settings. Getting the scoop! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)

    inst = app_instance.inst
    if not inst:
        console_print_func("❌ No instrument connected to query settings. Connect the damn thing first!")
        debug_log("No instrument connected for settings query.",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False

    try:
        # Query Center Frequency
        center_freq_str = query_safe(inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        if center_freq_str:
            app_instance.center_freq_hz_var.set(float(center_freq_str))
            console_print_func(f"ℹ️ Queried Center Frequency: {float(center_freq_str):.3f} Hz.")
            debug_log(f"Queried Center Frequency: {float(center_freq_str):.3f} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Span
        span_str = query_safe(inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        if span_str:
            app_instance.span_hz_var.set(float(span_str))
            console_print_func(f"ℹ️ Queried Span: {float(span_str):.3f} Hz.")
            debug_log(f"Queried Span: {float(span_str):.3f} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query RBW
        rbw_str = query_safe(inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        if rbw_str:
            app_instance.rbw_hz_var.set(float(rbw_str))
            console_print_func(f"ℹ️ Queried RBW: {float(rbw_str):.3f} Hz.")
            debug_log(f"Queried RBW: {float(rbw_str):.3f} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query VBW
        vbw_str = query_safe(inst, ":SENSe:BANDwidth:VIDeo?", console_print_func)
        if vbw_str:
            app_instance.vbw_hz_var.set(float(vbw_str))
            console_print_func(f"ℹ️ Queried VBW: {float(vbw_str):.3f} Hz.")
            debug_log(f"Queried VBW: {float(vbw_str):.3f} Hz.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Query Reference Level
        ref_level_str = query_safe(inst, ":DISPlay:WINDow:TRACe:Y:RLEVel?", console_print_func)
        if ref_level_str:
            app_instance.reference_level_dbm_var.set(float(ref_level_str))
            console_print_func(f"ℹ️ Queried Reference Level: {float(ref_level_str):.3f} dBm.")
            debug_log(f"Queried Reference Level: {float(ref_level_str):.3f} dBm.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        
        # (2025-08-02 13:10) Change: Conditionally query Preamp State based on instrument model.
        preamp_on = False # Default to False if query fails or not applicable
        if app_instance.instrument_model == "N9342CN":
            try:
                preamp_str = query_safe(inst, ":INPut:GAIN:STATe?", console_print_func)
                if preamp_str:
                    preamp_on = (preamp_str.strip().upper() == "ON" or preamp_str.strip() == "1")
                    app_instance.preamp_on_var.set(preamp_on)
                    console_print_func(f"ℹ️ Queried Preamp State: {'ON' if preamp_on else 'OFF'}.")
                    debug_log(f"Queried Preamp State: {'ON' if preamp_on else 'OFF'}.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                else:
                    console_print_func("🚫🐛 Could not determine Preamp state due to empty query response. Setting to OFF. This is a **fucking nightmare**!")
                    debug_log("Could not determine Preamp state due to empty query response. Setting to OFF.",
                                file=__file__,
                                version=current_version,
                                function=current_function)
                    app_instance.preamp_on_var.set(False) # Ensure it's set to a default
            except pyvisa.errors.VisaIOError as e:
                console_print_func(f"🛑 VISA error querying ':INPut:GAIN:STATe?': {e}. This goddamn thing is broken!")
                debug_log(f"VISA error querying Preamp state: {e}. Setting to OFF.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                app_instance.preamp_on_var.set(False) # Ensure it's set to a default on error
            except Exception as e:
                console_print_func(f"❌ An unexpected error occurred while querying Preamp state: {e}. This is a disaster!")
                debug_log(f"Unexpected error querying Preamp state: {e}. Setting to OFF.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                app_instance.preamp_on_var.set(False) # Ensure it's set to a default on error
        else:
            app_instance.preamp_on_var.set(False) # Default to False for other models
            debug_log("Preamp state query skipped for non-N9342CN model.",
                        file=__file__,
                        version=current_version,
                        function=current_function)


        # Query High Sensitivity (N9342CN specific)
        if app_instance.instrument_model == "N9342CN":
            high_sensitivity_str = query_safe(inst, ":SENSe:POWer:RF:HSENse?", console_print_func)
            if high_sensitivity_str:
                high_sensitivity = (high_sensitivity_str.strip().upper() == "ON" or high_sensitivity_str.strip() == "1")
                app_instance.high_sensitivity_var.set(high_sensitivity)
                console_print_func(f"ℹ️ Queried High Sensitivity: {'ON' if high_sensitivity else 'OFF'}.")
                debug_log(f"Queried High Sensitivity: {'ON' if high_sensitivity else 'OFF'}.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
            else:
                console_print_func("🚫🐛 Could not determine High Sensitivity state due to empty query response. Setting to OFF. This is a **fucking nightmare**!")
                debug_log("Could not determine High Sensitivity state due to empty query response. Setting to OFF.",
                            file=__file__,
                            version=current_version,
                            function=current_function)
                app_instance.high_sensitivity_var.set(False) # Ensure it's set to a default
        else:
            app_instance.high_sensitivity_var.set(False) # Default to False for other models
            debug_log("High Sensitivity query skipped for non-N9342CN model.",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        console_print_func("✅ Current instrument settings updated in GUI. All values retrieved!")
        debug_log("Current instrument settings updated in GUI. UI synced!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return True
    except Exception as e:
        console_print_func(f"❌ An error occurred while querying settings: {e}. This is a disaster!")
        debug_log(f"Error querying instrument settings: {e}. Fucking hell!",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        return False
    finally:
        app_instance.update_connection_status(app_instance.inst is not None)


def apply_instrument_settings_logic(app_instance, console_print_func):
    """
    Applies the settings from the GUI to the connected instrument.
    """
    current_function = inspect.currentframe().f_code.co_name
    console_print_func("Applying settings to instrument...")
    debug_log(f"Applying settings to instrument. Hardware configuration in progress! Version: {current_version}",
                file=__file__,
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected to apply settings. Connect the damn thing first!")
        debug_log("No instrument connected for applying settings.",
                    file=__file__,
                    version=current_function,
                    function=current_function)
        return False

    try:
        # Apply Center Frequency
        center_freq_hz = app_instance.center_freq_hz_var.get()
        write_safe(app_instance.inst, f":SENSe:FREQuency:CENTer {center_freq_hz}", console_print_func)
        debug_log(f"Applied Center Frequency: {center_freq_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Span
        span_hz = app_instance.span_hz_var.get()
        write_safe(app_instance.inst, f":SENSe:FREQuency:SPAN {span_hz}", console_print_func)
        debug_log(f"Applied Span: {span_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply RBW
        rbw_hz = app_instance.rbw_hz_var.get()
        write_safe(app_instance.inst, f":SENSe:BANDwidth:RESolution {rbw_hz}", console_print_func)
        debug_log(f"Applied RBW: {rbw_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply VBW
        vbw_hz = app_instance.vbw_hz_var.get()
        write_safe(app_instance.inst, f":SENSe:BANDwidth:VIDeo {vbw_hz}", console_print_func)
        debug_log(f"Applied VBW: {vbw_hz} Hz.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Reference Level
        ref_level_dbm = app_instance.reference_level_dbm_var.get()
        write_safe(app_instance.inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}", console_print_func)
        debug_log(f"Applied Reference Level: {ref_level_dbm} dBm.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply Preamp State
        preamp_state = "ON" if app_instance.preamp_on_var.get() else "OFF"
        write_safe(app_instance.inst, f":INPut:GAIN:STATe {preamp_state}", console_print_func)
        debug_log(f"Applied Preamp State: {preamp_state}.",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # Apply High Sensitivity (N9342CN specific)
        if app_instance.instrument_model == "N9342CN":
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
