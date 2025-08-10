# tabs/Instrument/instrument_logic.py
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
#
# Version 20250803.192000.0 (FIXED: Removed unnecessary FREQuency:SHIFt query.)
# Version 20250803.191800.0 (FIXED: AttributeError by using correct visa_resource_var and removing invalid variable set.)
# Version 20250803.1115.1 (Fixed ImportError: cannot import name 'initialize_instrument' by correcting import to 'initialize_instrument_logic'.)
# Version 20250804.025500.0 (FIXED: populate_resources_logic signature and functionality to accept resource_combobox.)
# Version 20250804.025800.0 (REMOVED: Query for :SENSe:FREQuency:RFShift? as per user request.)

current_version = "20250804.025800.0" # Incremented version

import tkinter as tk
import pyvisa
import os
import time
import sys
import inspect

from display.debug_logic import debug_log
from display.console_logic import console_log

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
    initialize_instrument_logic
)
from tabs.Instrument.utils_instrument_query_settings import (
    query_current_instrument_settings
)

MHZ_TO_HZ_CONVERSION = 1_000_000
KHZ_TO_HZ_CONVERSION = 1_000

def populate_resources_logic(app_instance, resource_combobox, console_print_func):
    """Populates the VISA resource combobox with available instruments."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Populating VISA resources. Let's find those devices! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    console_print_func("💬 Searching for VISA instruments...")
    
    resources = list_visa_resources(console_print_func)
    resource_combobox['values'] = resources
    
    if resources:
        app_instance.visa_resource_var.set(resources[0])
        debug_log(f"Found VISA resources: {resources}. Success!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        app_instance.visa_resource_var.set("")
        console_print_func("⚠️ No VISA instruments found. Is the instrument connected and VISA drivers installed?")
        debug_log("No VISA instruments found. Check connections and drivers!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


def connect_instrument_logic(app_instance, console_print_func):
    """Handles the connection process to the selected VISA instrument."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to connect to instrument. Let's make this happen! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    
    selected_resource = app_instance.visa_resource_var.get()
    
    if not selected_resource:
        console_print_func("⚠️ No instrument selected. Please refresh devices and select one.")
        return False

    console_print_func(f"💬 Connecting to {selected_resource}...")
    try:
        inst = connect_to_instrument(selected_resource, console_print_func)
        if inst:
            app_instance.inst = inst
            app_instance.is_connected.set(True)
            
            idn_response = query_safe(inst, "*IDN?", console_print_func)
            if idn_response:
                parts = idn_response.strip().split(',')
                model = parts[1].strip() if len(parts) > 1 else idn_response.strip()
                app_instance.connected_instrument_model.set(model)
            else:
                console_print_func("❌ Failed to query instrument identification. What a pain!")
                debug_log("Failed to query IDN. Fucking useless!",
                            file=f"{os.path.basename(__file__)} - {current_version}",
                            version=current_version,
                            function=current_function)
                disconnect_instrument_logic(app_instance, console_print_func)
                return False

            console_print_func("✅ Instrument connected and identified successfully.")
            return True
        else:
            console_print_func("❌ Failed to connect to instrument. What a mess!")
            debug_log("Connection attempt failed. This thing is broken!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            app_instance.is_connected.set(False)
            return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred during connection: {e}. This is a disaster!")
        debug_log(f"Unexpected error during connection: {e}. Fucking hell!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.inst = None
        app_instance.is_connected.set(False)
        return False

def disconnect_instrument_logic(app_instance, console_print_func):
    """Handles the disconnection process from the current VISA instrument."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Attempting to disconnect instrument. Cutting ties! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if app_instance.inst:
        console_print_func("💬 Disconnecting instrument...")
        if disconnect_instrument(app_instance.inst, console_print_func):
            app_instance.inst = None
            app_instance.is_connected.set(False)
            app_instance.connected_instrument_model.set("")
            console_print_func("✅ Instrument disconnected successfully.")
            debug_log("Instrument disconnected successfully.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return True
        else:
            console_print_func("❌ Failed to disconnect instrument. Still clinging on!")
            debug_log("Failed to disconnect instrument. What a mess!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
    else:
        console_print_func("⚠️ No instrument is currently connected to disconnect.")
        debug_log("No instrument to disconnect. Nothing to see here!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True # Return True as there's nothing to disconnect, it's already in the desired state


def query_current_settings_logic(app_instance, console_print_func):
    """Queries the current settings from the connected instrument."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Querying current instrument settings. What's this thing up to? Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not app_instance.inst:
        console_print_func("❌ No instrument connected to query.")
        debug_log("No instrument to query. Dead end!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None

    try:
        # Queries for settings using query_safe from utils_instrument_read_and_write
        center_freq_str = query_safe(app_instance.inst, ":SENSe:FREQuency:CENTer?", console_print_func)
        span_str = query_safe(app_instance.inst, ":SENSe:FREQuency:SPAN?", console_print_func)
        rbw_str = query_safe(app_instance.inst, ":SENSe:BANDwidth:RESolution?", console_print_func)
        ref_level_str = query_safe(app_instance.inst, ":DISPlay:WINDow:TRACe:Y:RLEVel?", console_print_func)
        
        # REMOVED: query for :SENSe:FREQuency:RFShift? as per user request
        # freq_shift_str = query_safe(app_instance.inst, ":SENSe:FREQuency:RFShift?", console_print_func)
        
        trace_mode_str = query_safe(app_instance.inst, ":TRACe2:MODE?", console_print_func) # Assuming TRACE2 for display
        preamp_status_str = query_safe(app_instance.inst, ":SENSe:POWer:RF:GAIN?", console_print_func)

        settings = {
            'center_freq_hz': float(center_freq_str) if center_freq_str else 'N/A',
            'span_hz': float(span_str) if span_str else 'N/A',
            'rbw_hz': float(rbw_str) if rbw_str else 'N/A',
            'ref_level_dbm': float(ref_level_str) if ref_level_str else 'N/A',
            # REMOVED: 'freq_shift_hz' from settings dictionary
            'trace_mode': trace_mode_str.strip() if trace_mode_str else 'N/A',
            'preamp_on': True if preamp_status_str and "1" in preamp_status_str else False
        }
        return settings
    except Exception as e:
        console_print_func(f"❌ Error querying settings: {e}. This is a disaster!")
        debug_log(f"Error querying settings: {e}. What a mess!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None