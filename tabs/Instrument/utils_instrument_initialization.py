# tabs/Instrument/utils_instrument_initialization.py
#
# This file contains the core logic for initializing the spectrum analyzer.
# It includes functions for setting basic instrument parameters when first connected
# or before a scan. This file is separated to break circular import dependencies.
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
# Version 20250810.133200.1 (FIXED: Passed app_instance_ref and wrapped all console calls with after() to prevent cross-thread access and the fatal GIL error.)

current_version = "20250810.133200.1"

import inspect
import os
import time

from display.debug_logic import debug_log
from tabs.Instrument.utils_instrument_read_and_write import write_safe

# REMOVED: from src.console_logic import console_log # Removed this import to break circular dependency

def initialize_instrument_logic(inst, model_match, ref_level_dbm, high_sensitivity_on, preamp_on, rbw_config_val, vbw_config_val, app_instance_ref, console_print_func):
    """
    Initializes the connected spectrum analyzer with a set of basic parameters.
    This function is called once after connection or before a new scan.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Initializing instrument with basic settings. Model: {model_match}. Getting set up! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func("⚠️ Warning: Instrument not connected. Cannot initialize. Fix it!"))
        debug_log("Instrument not connected for initialization. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    success = True

    # Reset and configure basic display settings
    if not write_safe(inst, "*RST", app_instance_ref, console_print_func): success = False
    time.sleep(0.1)
    if not write_safe(inst, ":DISPlay:FORMat LOG", app_instance_ref, console_print_func): success = False
    if not write_safe(inst, ":UNIT:POWer DBM", app_instance_ref, console_print_func): success = False
    
    # Configure averaging (usually off for raw sweeps, or reset to 1)
    if not write_safe(inst, ":SENSe:AVERage:STATe OFF", app_instance_ref, console_print_func): success = False
    if not write_safe(inst, ":SENSe:AVERage:COUNt 1", app_instance_ref, console_print_func): success = False

    # Set sweep points (common default, adjust if instrument specific)
    sweep_points = "501" # Common default for many spectrum analyzers
    if model_match == "N9340B":
        sweep_points = "461"
    elif model_match == "N9342CN":
        sweep_points = "501"
    if not write_safe(inst, f":SENSe:SWEep:POINts {sweep_points}", app_instance_ref, console_print_func): success = False
    
    # Apply configured values for RBW, VBW, Ref Level
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_config_val}HZ", app_instance_ref, console_print_func): success = False
    if not write_safe(inst, f":SENSe:BANDwidth:VIDeo {vbw_config_val}HZ", app_instance_ref, console_print_func): success = False
    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", app_instance_ref, console_print_func): success = False

    # High Sensitivity and Preamp
    high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
    if not write_safe(inst, high_sensitivity_cmd, app_instance_ref, console_print_func): success = False
    
    preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
    if not write_safe(inst, preamp_cmd, app_instance_ref, console_print_func): success = False
    
    # Set trace mode to VIEW
    if not write_safe(inst, ":TRACe1:MODE VIEW", app_instance_ref, console_print_func): success = False

    if success:
        debug_log(f"Instrument initialized successfully. Ready for action! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func("✅ Instrument initialized successfully."))
        return True
    else:
        # WRAPPED WITH after() to prevent cross-thread access
        app_instance_ref.after(0, lambda: console_print_func("❌ Failed to fully initialize instrument. This is a mess!"))
        debug_log("Instrument initialization failed. What a disaster!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False
