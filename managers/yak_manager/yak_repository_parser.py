# managers/yak_manager/yak_repository_parser.py
#
# This file (yak_repository_parser.py) provides utility functions for parsing the YAK repository, enabling lookup of SCPI commands, inputs, and outputs based on a given command node.
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


import os
import inspect
import json

from workers.logger.logger import debug_log, console_log, log_visa_command

Local_Debug_Enable = True

current_file = f"{os.path.basename(__file__)}"


def get_command_node(repo, command_path_parts, function_name):
    """
    Traverses the repository to find the base node for a command and logs each step.
    Returns the command's base dictionary or None if not found.
    """
    if Local_Debug_Enable:
        debug_log(f"🔍🔵 Entering {function_name} to get command node for path: {command_path_parts}.",
                  file=current_file,
                  version=current_version,
                  function=function_name,
                  console_print_func=console_log)
    
    current_node = repo
    
    for part in command_path_parts:
        if Local_Debug_Enable:
            debug_log(f"🔍 Trying to get part: '{part}' from current_node.",
                      file=current_file,
                      version=current_version,
                      function=function_name,
                      console_print_func=console_log)
        
        current_node = current_node.get(part)
        
        if not current_node:
            console_log(f"❌ Error: Command path not found at intermediate step.")
            return None
        
        if Local_Debug_Enable:
            debug_log(f"🔍 Succeeded. Current node keys are now: {list(current_node.keys())}",
                      file=current_file,
                      version=current_version,
                      function=function_name,
                      console_print_func=console_log)
    
    return current_node


def lookup_scpi_command(command_node, model_key, command_path):
    """
    Looks up and returns the SCPI command string from a given command node.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    scpi_details = command_node.get("scpi_details", {})
    scpi_value = scpi_details.get(model_key, {}).get("SCPI_value")
    
    scpi_path = command_path + [f"scpi_details/{model_key}/SCPI_value"]
    
    if scpi_value:
        if Local_Debug_Enable:
            debug_log(f"✅ SCPI Command found at path: {'/'.join(scpi_path)}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        if Local_Debug_Enable:
            debug_log(f"✅ SCPI Command: {scpi_value}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        return scpi_value
    else:
        console_log(f"🟡 SCPI Command not found for model '{model_key}' at path: {'/'.join(scpi_path)}")
        return None

def lookup_inputs(command_node, command_path):
    """
    Looks up and returns the inputs for a given command node.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    scpi_inputs_path = command_path + ["scpi_inputs"]
    scpi_inputs = command_node.get("scpi_inputs")
    
    if scpi_inputs:
        inputs_count = len(scpi_inputs)
        input_details = " ".join([f"({key} = {details.get('value', 'N/A')})" for key, details in scpi_inputs.items()])
        if Local_Debug_Enable:
            debug_log(f"✅ Inputs found at path: {'/'.join(scpi_inputs_path)}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        if Local_Debug_Enable:
            debug_log(f"➡️ scpi_inputs = {inputs_count} {input_details}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        return scpi_inputs
    else:
        console_log("🟡 No inputs found.")
        return None


def lookup_outputs(command_node, command_path):
    """
    Looks up and returns the outputs for a given command node.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    scpi_outputs_path = command_path + ["scpi_outputs"]
    scpi_outputs = command_node.get("scpi_outputs")
    
    if scpi_outputs:
        outputs_count = len(scpi_outputs)
        output_details = " ".join([f"({key} = {details.get('value', 'N/A')})" for key, details in scpi_outputs.items()])
        if Local_Debug_Enable:
            debug_log(f"✅ Outputs found at path: {'/'.join(scpi_outputs_path)}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        if Local_Debug_Enable:
            debug_log(f"⬅️ scpi_outputs = {outputs_count} {output_details}",
                      file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        return scpi_outputs
    else:
        console_log("🟡 No outputs found.")
        return None