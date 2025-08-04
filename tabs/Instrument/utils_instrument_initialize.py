# tabs/Instrument/utils_instrument_initialize.py
#
# This file contains functions for initializing the spectrum analyzer.
# This includes setting basic instrument parameters when first connected
# or before a scan.
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
# Version 20250803.1750.0 (Initial creation of initialize_instrument_logic.)
# Version 20250804.030000.0 (FIXED: Added model_match parameter to initialize_instrument_logic signature.)

current_version = "20250804.030000.0"

import inspect
import os
import time

from src.debug_logic import debug_log
from tabs.Instrument.utils_instrument_read_and_write import write_safe

def initialize_instrument_logic(inst, model_match, ref_level_dbm, high_sensitivity_on, preamp_on, rbw_config_val, vbw_config_val, console_print_func):
    # Function Description:
    # Initializes the connected spectrum analyzer with a set of basic parameters.
    # This function is called once after connection or before a new scan.
    #
    # Inputs:
    #   inst (pyvisa.resources.Resource): The PyVISA instrument object.
    #   model_match (str): The detected model of the instrument (e.g., "N9340B"). Used for conditional logic if needed.
    #   ref_level_dbm (float): Reference level in dBm.
    #   high_sensitivity_on (bool): True to enable high sensitivity mode.
    #   preamp_on (bool): True to enable preamplifier.
    #   rbw_config_val (float): Resolution Bandwidth in Hz.
    #   vbw_config_val (float): Video Bandwidth in Hz.
    #   console_print_func (function): Function to print messages to the GUI console.
    #
    # Process:
    #   1. Logs entry with debug information.
    #   2. Checks if instrument is connected.
    #   3. Sends SCPI commands to:
    #      - Reset instrument (`*RST`).
    #      - Set display format to LOG.
    #      - Set unit to DBM.
    #      - Set average mode to OFF and average count to 1 (for initial state).
    #      - Set sweep points (e.g., 501 or 1001 based on model/default).
    #      - Apply initial RBW, VBW, Reference Level, High Sensitivity, Preamplifier.
    #      - Set trace mode to VIEW (for initial display).
    #   4. Returns True on success, False on failure.
    #
    # Outputs:
    #   bool: True if initialization was successful, False otherwise.
    #
    # (2025-08-04.030000.0) Change: Added model_match to signature and updated version.
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Initializing instrument with basic settings. Model: {model_match}. Getting set up! Version: {current_version}",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if not inst:
        console_print_func("⚠️ Warning: Instrument not connected. Cannot initialize. Fix it!")
        debug_log("Instrument not connected for initialization. Fucking useless!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False

    success = True

    # Reset and configure basic display settings
    if not write_safe(inst, "*RST", console_print_func): success = False
    time.sleep(0.1)
    if not write_safe(inst, ":DISPlay:FORMat LOG", console_print_func): success = False
    if not write_safe(inst, ":UNIT:POWer DBM", console_print_func): success = False
    
    # Configure averaging (usually off for raw sweeps, or reset to 1)
    if not write_safe(inst, ":SENSe:AVERage:STATe OFF", console_print_func): success = False
    if not write_safe(inst, ":SENSe:AVERage:COUNt 1", console_print_func): success = False

    # Set sweep points (common default, adjust if instrument specific)
    # Could be conditional on model_match if different instruments have different optimal points
    sweep_points = "501" # Common default for many spectrum analyzers
    if model_match == "N9340B":
        sweep_points = "461"
    elif model_match == "N9342CN":
        sweep_points = "501" # Or 500, depending on precise model/firmware. Sticking to 501 for typical plots.
    if not write_safe(inst, f":SENSe:SWEep:POINts {sweep_points}", console_print_func): success = False
    
    # Apply configured values for RBW, VBW, Ref Level
    if not write_safe(inst, f":SENSe:BANDwidth:RESolution {rbw_config_val}HZ", console_print_func): success = False
    if not write_safe(inst, f":SENSe:BANDwidth:VIDeo {vbw_config_val}HZ", console_print_func): success = False
    if not write_safe(inst, f":DISPlay:WINDow:TRACe:Y:RLEVel {ref_level_dbm}DBM", console_print_func): success = False

    # High Sensitivity and Preamp
    high_sensitivity_cmd = ":SENSe:POWer:RF:HSENs ON" if high_sensitivity_on else ":SENSe:POWer:RF:HSENs OFF"
    if not write_safe(inst, high_sensitivity_cmd, console_print_func): success = False
    
    preamp_cmd = ":SENSe:POWer:RF:GAIN ON" if preamp_on else ":SENSe:POWer:RF:GAIN OFF"
    if not write_safe(inst, preamp_cmd, console_print_func): success = False
    
    # Set trace mode to VIEW to see the trace on the instrument display initially
    if not write_safe(inst, ":TRACe1:MODE VIEW", console_print_func): success = False

    if success:
        debug_log(f"Instrument initialized successfully. Ready for action! Version: {current_version}",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return True
    else:
        console_print_func("❌ Failed to fully initialize instrument. This is a mess!")
        debug_log("Instrument initialization failed. What a disaster!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return False