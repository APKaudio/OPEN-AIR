# managers/visa_utils.py
#
# This file (visa_utils.py) provides utility functions for listing and connecting to VISA (Virtual Instrument Software Architecture) resources.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
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

from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args
import workers.setup.app_constants as app_constants

LOCAL_DEBUG_ENABLE = False

def list_visa_resources(
):
    # Lists available VISA resources (instruments).
   
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(message="Listing VISA resources... Let's find some devices!", **_get_log_args())
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
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(message=f"Found VISA resources (Reordered): {resources}.", **_get_log_args())
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}."
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(message=error_msg, **_get_log_args())
        return []

def connect_to_instrument(resource_name, 
):
    # Establishes a connection to a VISA instrument.
    
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(message=f"Connecting to instrument: {resource_name}. Fingers crossed!", **_get_log_args())
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 5000
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.query_delay = 0.1
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(message=f"Connection successful to {resource_name}. We're in!", **_get_log_args())
        return inst
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}."
        
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(message=error_msg, **_get_log_args())
        return None

def disconnect_instrument(inst, 
):
    # Closes the connection to a VISA instrument.
   
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(message="Disconnecting instrument... Saying goodbye!", **_get_log_args())
    if inst:
        try:
            inst.close()
            
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(message="Instrument connection closed. All done!", **_get_log_args())
            return True
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}."
            
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(message=error_msg, **_get_log_args())
            return False
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(message="No instrument to disconnect. Already gone!", **_get_log_args())
    return False
