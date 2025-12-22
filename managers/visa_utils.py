# managers/visa_utils.py
#
# This file (visa_utils.py) provides utility functions for listing and connecting to VISA (Virtual Instrument Software Architecture) resources.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#


import pyvisa
import os
import inspect

from workers.logger.logger import debug_log, console_log, log_visa_command

Local_Debug_Enable = False

current_file = f"{os.path.basename(__file__)}"

def list_visa_resources(console_print_func=None):
    # Lists available VISA resources (instruments).
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.Local_Debug_Enable: 
        debug_log(message="Listing VISA resources... Let's find some devices!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    try:
        rm = pyvisa.ResourceManager()
        
        # KEY CHANGE: Explicitly search for all instrument types, especially TCPIP.
        # '?*::INSTR' is the wildcard search pattern for all resource types supported by the backend.
        all_resources = rm.list_resources('?*::INSTR') 

        # --- Resource Reordering Logic (FIX) ---
        usb_resources = []
        tcpip_resources = []
        other_resources = []

        for res in all_resources:
            if res.startswith('USB'):
                usb_resources.append(res)
            elif res.startswith('TCPIP'):
                tcpip_resources.append(res)
            else: # Catches ASRL, GPIB, etc.
                other_resources.append(res)
        
        # Prioritize list: USB -> TCPIP -> Other (ASRL)
        resources = usb_resources + tcpip_resources + other_resources
        # --- End Resource Reordering Logic ---
        
        if app_constants.Local_Debug_Enable: 
            debug_log(message=f"Found VISA resources (Reordered): {resources}.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}."
        console_print_func(error_msg)
        if app_constants.Local_Debug_Enable: 
            debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return []

def connect_to_instrument(resource_name, console_print_func=None):
    # Establishes a connection to a VISA instrument.
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.Local_Debug_Enable: 
        debug_log(message=f"Connecting to instrument: {resource_name}. Fingers crossed!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 5000
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.query_delay = 0.1
        console_print_func(f"✅ Successfully connected to {resource_name}.")
        if app_constants.Local_Debug_Enable: 
            debug_log(message=f"Connection successful to {resource_name}. We're in!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return inst
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}."
        console_print_func(error_msg)
        if app_constants.Local_Debug_Enable: 
            debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return None

def disconnect_instrument(inst, console_print_func=None):
    # Closes the connection to a VISA instrument.
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.Local_Debug_Enable: 
        debug_log(message="Disconnecting instrument... Saying goodbye!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    if inst:
        try:
            inst.close()
            console_print_func("✅ Instrument disconnected.")
            if app_constants.Local_Debug_Enable: 
                debug_log(message="Instrument connection closed. All done!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
            return True
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}."
            console_print_func(error_msg)
            if app_constants.Local_Debug_Enable: 
                debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
            return False
    if app_constants.Local_Debug_Enable: 
        debug_log(message="No instrument to disconnect. Already gone!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    return False
