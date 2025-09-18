# managers/manager_yak_on_trigger.py
#
# This manager listens for MQTT messages and orchestrates the command
# execution by delegating tasks to specialized sub-managers.

import os
import inspect
import json
import pathlib
import re

# --- Utility and Manager Imports ---
from workers.worker_logging import debug_log, console_log
from managers.manager_yak_tx import YakTxManager
from managers.manager_visa_dispatch_scpi import ScpiDispatcher
from managers.manager_yak_rx import YakRxManager


current_version = "20250917.232502.1"
current_version_hash = (20250917 * 232502 * 1)
current_file = f"{os.path.basename(__file__)}"

YAKETY_YAK_REPO_PATH = pathlib.Path("DATA/YAKETYYAK.json")


def _get_command_node(repo, command_path_parts, function_name):
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


def _lookup_scpi_command(command_node, model_key, command_path):
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

def _lookup_inputs(command_node, command_path):
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


def _lookup_outputs(command_node, command_path):
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
        
def _fill_scpi_placeholders(scpi_command_template: str, scpi_inputs: dict):
    """
    Takes an SCPI command template and replaces placeholders with values from inputs.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(f"🔍🔵 Entering {current_function_name} to fill SCPI placeholders.",
              file=current_file,
              version=current_version,
              function=current_function_name,
              console_print_func=console_log)
              
    filled_command = scpi_command_template
    
    if scpi_inputs:
        for key, details in scpi_inputs.items():
            placeholder = f"<{key}>"
            value_to_substitute = str(details.get("value", ""))
            
            # --- NEW FIX: Replace the placeholder value with a single double quote for the path terminator ---
            filled_command = filled_command.replace('\\"', '"')
            
            if placeholder == "<path_terminator>" and placeholder in filled_command:
                filled_command = filled_command.replace(placeholder, '"')
                value_to_substitute = '"'
            
            if placeholder == "<path_starter>" and placeholder in filled_command:
                filled_command = filled_command.replace(placeholder, '"')
                value_to_substitute = '"'
            
            if placeholder in filled_command:
                filled_command = filled_command.replace(placeholder, value_to_substitute)
                debug_log(f"🔁 Replaced placeholder '{placeholder}' with value '{value_to_substitute}'.",
                          file=current_file,
                          version=current_version,
                          function=current_function_name,
                          console_print_func=console_log)

    console_log(f"✅ Filled SCPI Command: {filled_command}")
    return filled_command

def YAK_TRIGGER_COMMAND(self, topic, payload):
    """
    Orchestrates the command details lookup by first getting the base node
    and then calling the specialized lookup functions.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message="TRIGGER TRIGGER TRIGGER",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # Load the JSON repository from the specified file path.
        if not YAKETY_YAK_REPO_PATH.is_file():
            console_log(f"❌ Error: Repository file not found at {YAKETY_YAK_REPO_PATH}")
            return

        with open(YAKETY_YAK_REPO_PATH, 'r') as f:
            repo = json.load(f)

        # Deconstruct the topic to navigate the JSON structure.
        repo_path_parts = topic.replace("OPEN-AIR/repository/", "").split('/')
        
        # The path to the command's base node is everything up to the model key and trigger word.
        command_path_to_node = [part.replace(' ', '_') for part in repo_path_parts[:-3]]
        model_key = repo_path_parts[-2]
        
        # First, traverse the path to get the base command node.
        command_node = _get_command_node(repo=repo, command_path_parts=command_path_to_node, function_name=current_function_name)
        if command_node is None:
            return

        # Now call the lookup functions on that node.
        scpi_template = _lookup_scpi_command(command_node=command_node, model_key=model_key, command_path=command_path_to_node)
        scpi_inputs = _lookup_inputs(command_node=command_node, command_path=command_path_to_node)
        command_outputs = _lookup_outputs(command_node=command_node, command_path=command_path_to_node)
        
        # Call the new function to fill in the placeholders
        if scpi_template:
            final_scpi_command = _fill_scpi_placeholders(scpi_command_template=scpi_template, scpi_inputs=scpi_inputs)
            
            # Capture the return value from the command execution
            yak_tx_manager = YakTxManager(dispatcher_instance=self.dispatcher)
            # The command type is derived from the second part of the path (e.g., 'beg', 'get', 'set')
            command_type = repo_path_parts[1]
            response_value = yak_tx_manager.execute_command(command_type=command_type, command_string=final_scpi_command)
            
            # Check if there is a valid response to process
            if response_value and response_value != "FAILED":
                # Pass the response to the RX Manager for processing
                yak_rx_manager = YakRxManager(mqtt_controller=self.mqtt_util)
                yak_rx_manager.process_response(path_parts=repo_path_parts, command_details={"scpi_outputs": command_outputs}, response=response_value)
        
        debug_log(
            message=f"🔍 Processed trigger for topic: {topic}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
    except Exception as e:
        console_log(f"❌ Error processing trigger for topic {topic}: {e}")
        debug_log(
            message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )