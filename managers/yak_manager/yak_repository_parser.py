# managers/yak_manager/yak_repository_parser.py

import os
import inspect
from workers.worker_active_logging import debug_log, console_log

current_version = "1.0.0"
current_file = f"{os.path.basename(__file__)}"

def get_command_node(repo, command_path_parts, function_name):
    """
    Traverses the repository to find the base node for a command and logs each step.
    Returns the command's base dictionary or None if not found.
    """
    debug_log(f"🔍🔵 Entering {function_name} to get command node for path: {command_path_parts}.",
              file=current_file,
              version=current_version,
              function=function_name,
              console_print_func=console_log)
    
    current_node = repo
    
    for part in command_path_parts:
        debug_log(f"🔍 Trying to get part: '{part}' from current_node.",
                  file=current_file,
                  version=current_version,
                  function=function_name,
                  console_print_func=console_log)
        
        current_node = current_node.get(part)
        
        if not current_node:
            console_log(f"❌ Error: Command path not found at intermediate step.")
            return None
        
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
        debug_log(f"✅ SCPI Command found at path: {'/'.join(scpi_path)}",
                  file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
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
        debug_log(f"✅ Inputs found at path: {'/'.join(scpi_inputs_path)}",
                  file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
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
        debug_log(f"✅ Outputs found at path: {'/'.join(scpi_outputs_path)}",
                  file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        debug_log(f"⬅️ scpi_outputs = {outputs_count} {output_details}",
                  file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        return scpi_outputs
    else:
        console_log("🟡 No outputs found.")
        return None
