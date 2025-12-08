# managers/yak_manager/yak_command_builder.py

import os
import inspect
from workers.active.worker_active_logging import debug_log, console_log

current_version = "1.0.0"
current_file = f"{os.path.basename(__file__)}"

def fill_scpi_placeholders(scpi_command_template: str, scpi_inputs: dict):
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
            filled_command = filled_command.replace('\"', '"')
            
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
