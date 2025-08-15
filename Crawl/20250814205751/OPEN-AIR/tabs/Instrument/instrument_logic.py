# tabs/Instrument/instrument_logic.py
#
# This file contains the core logic for managing the connection to and interaction
# with a VISA instrument, such as a spectrum analyzer. It provides high-level
# functions for connecting, disconnecting, and querying the device for its settings.
# This file serves as an abstraction layer between the GUI and the low-level
# VISA read/write utilities.
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
#
# Version 20250813.101300.1 (REFACTORED: Rewrote query_current_settings_logic to use high-level YakGet calls to eliminate redundancy and simplify the code.)

current_version = "20250813.101300.1"
current_version_hash = 20250813 * 101300 * 1

import inspect
import os
import time
import sys
import tkinter as tk
import pyvisa
import traceback

from display.debug_logic import debug_log
from display.console_logic import console_log

# Import low-level VISA utilities
from tabs.Instrument.Yakety_Yak import YakGet, YakSet, YakDo, query_safe, write_safe
from tabs.Instrument.utils_instrument_connection import connect_to_instrument, disconnect_instrument, list_visa_resources


def populate_resources_logic(app_instance, combobox_widget, console_print_func):
    # Function Description:
    # Populates the `visa_resource_var` Combobox with available VISA instrument addresses.
    # It first clears the existing list, then calls `list_visa_resources` to find
    # available devices, and finally populates the combobox with the results.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Populating VISA resources. Let's find those devices! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)
    
    app_instance.visa_resource_var.set("")
    combobox_widget['values'] = []

    resources = list_visa_resources(console_print_func)
    if resources:
        combobox_widget['values'] = resources
        app_instance.visa_resource_var.set(resources[0])
        debug_log(f"Found VISA resources: {resources}. Success!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
    else:
        console_print_func("No VISA instruments found. Check connections.")
        debug_log("No VISA resources found. Time for some detective work. 🕵️‍♀️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)

def connect_instrument_logic(app_instance, console_print_func):
    # Function Description:
    # Handles the full connection sequence to a VISA instrument.
    # It attempts to establish a connection, queries the instrument's IDN string,
    # and updates the application's state variables accordingly.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to connect to instrument. Let's make this happen! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)
    
    selected_resource = app_instance.visa_resource_var.get()
    if not selected_resource:
        console_print_func("❌ No instrument selected. Cannot connect.")
        debug_log("No resource selected. This is a fine mess! 🤦‍♂️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        return False
        
    try:
        # Step 1: Connect to the instrument
        app_instance.inst = connect_to_instrument(selected_resource, console_print_func)
        if not app_instance.inst:
            app_instance.is_connected.set(False)
            return False

        # Step 2: Query IDN using YakGet and populate model
        idn_response = YakGet(app_instance, "SYSTEM/ID", console_print_func)
        if idn_response and idn_response != "FAILED":
            idn_parts = idn_response.split(',')
            if len(idn_parts) >= 2:
                app_instance.connected_instrument_manufacturer.set(idn_parts[0].strip())
                app_instance.connected_instrument_model.set(idn_parts[1].strip())
            else:
                console_print_func("⚠️ Warning: Could not parse instrument IDN. Proceeding with generic model.")
                app_instance.connected_instrument_manufacturer.set("N/A")
                app_instance.connected_instrument_model.set("GENERIC")
        else:
            console_print_func("⚠️ Warning: Could not query instrument IDN. Proceeding with generic settings.")
            app_instance.connected_instrument_manufacturer.set("N/A")
            app_instance.connected_instrument_model.set("GENERIC")
        
        app_instance.is_connected.set(True)
        debug_log("Connection successful! The instrument is alive! 🥳",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        return True
    
    except Exception as e:
        console_print_func(f"❌ Error during connection: {e}")
        debug_log(f"Connection failed spectacularly! Error: {e}. What a disaster! Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        disconnect_instrument(app_instance, console_print_func)
        app_instance.is_connected.set(False)
        return False


def disconnect_instrument_logic(app_instance, console_print_func):
    # Function Description:
    # Disconnects the application from the currently connected VISA instrument.
    # It checks if an instrument instance exists and attempts to close the connection.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to disconnect instrument. Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)
    
    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Nothing to disconnect.")
        debug_log("No instrument to disconnect. This is a mess.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        return True
    
    result = disconnect_instrument(app_instance.inst, console_print_func)
    app_instance.inst = None
    app_instance.is_connected.set(False)
    
    if result:
        debug_log("Successfully disconnected. Until we meet again! �",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
    else:
        debug_log("Disconnecting failed. This is a catastrophe!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
    return result

def query_current_settings_logic(app_instance, console_print_func):
    # Function Description:
    # Queries the currently connected instrument for its essential settings,
    # including IDN string, Center Frequency, Span, RBW, Ref Level, Trace Mode,
    # and Preamp status. It then returns a dictionary containing all these values.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Querying current instrument settings. What's this thing up to? Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                function=current_function)

    if not app_instance.inst:
        console_print_func("⚠️ Warning: No instrument connected. Cannot query settings. Fix it!")
        debug_log("No instrument connected. Cannot query settings. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        return None
        
    settings = {}
    
    try:
        # Query the IDN string first
        settings['idn_string'] = YakGet(app_instance, "SYSTEM/ID", console_print_func)
        
        # Query Center Frequency
        center_freq_str = YakGet(app_instance, "FREQUENCY/CENTER", console_print_func)
        settings['center_freq_hz'] = float(center_freq_str) if center_freq_str and center_freq_str != 'FAILED' else "N/A"
        
        # Query Span
        span_str = YakGet(app_instance, "FREQUENCY/SPAN", console_print_func)
        settings['span_hz'] = float(span_str) if span_str and span_str != 'FAILED' else "N/A"
        
        # Query RBW
        rbw_str = YakGet(app_instance, "BANDWIDTH/RESOLUTION", console_print_func)
        settings['rbw_hz'] = float(rbw_str) if rbw_str and rbw_str != 'FAILED' else "N/A"

        # Query Ref Level
        ref_level_str = YakGet(app_instance, "AMPLITUDE/REFERENCE LEVEL", console_print_func)
        settings['ref_level_dbm'] = float(ref_level_str) if ref_level_str and ref_level_str != 'FAILED' else "N/A"
        
        # Query Trace Mode (Assuming we want Trace 2 for Max Hold)
        trace_mode_str = YakGet(app_instance, "TRACE/2/MODE", console_print_func)
        settings['trace_mode'] = trace_mode_str if trace_mode_str and trace_mode_str != 'FAILED' else "N/A"
        
        # Query Preamp Status (GAIN)
        preamp_on_str = YakGet(app_instance, "AMPLITUDE/POWER/GAIN", console_print_func)
        settings['preamp_on'] = (preamp_on_str == '1' or preamp_on_str == 'ON') if preamp_on_str and preamp_on_str != 'FAILED' else False

        debug_log("Finished querying instrument settings. A treasure trove of information! 🗺️",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        
        return settings
    
    except Exception as e:
        console_print_func(f"❌ Error querying settings: {e}")
        debug_log(f"Error querying instrument settings: {e}. What a disaster! Traceback: {traceback.format_exc()}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    function=current_function)
        return None