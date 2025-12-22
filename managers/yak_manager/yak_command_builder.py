# managers/yak_manager/yak_command_builder.py
#
# This file (yak_command_builder.py) provides functionality to build SCPI commands by filling placeholders in a template with values from inputs.
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
from workers.logger.logger import debug_log, console_log, log_visa_command

Local_Debug_Enable = True

current_file = f"{os.path.basename(__file__)}"


def fill_scpi_placeholders(scpi_command_template: str, scpi_inputs: dict):
    """
    Takes an SCPI command template and replaces placeholders with values from inputs.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
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
                if Local_Debug_Enable:
                    debug_log(f"🔁 Replaced placeholder '{placeholder}' with value '{value_to_substitute}'.",
                              file=current_file,
                              version=current_version,
                              function=current_function_name,
                              console_print_func=console_log)

    console_log(f"✅ Filled SCPI Command: {filled_command}")
    return filled_command