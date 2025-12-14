# managers/yak_manager/yak_trigger_handler.py
#
# This file (yak_trigger_handler.py) orchestrates command execution by processing YAK triggers from MQTT, looking up SCPI command details, building the final command, and dispatching it to the instrument.
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

from display.logger import debug_log, console_log, log_visa_command
from managers.yak_manager.yak_repository_parser import get_command_node, lookup_scpi_command, lookup_inputs, lookup_outputs
from managers.yak_manager.yak_command_builder import fill_scpi_placeholders
from managers.yak_manager.manager_yak_tx import YakTxManager
from managers.yak_manager.manager_yak_rx import YakRxManager
from workers.utils.worker_project_paths import YAKETY_YAK_REPO_PATH 

Local_Debug_Enable = True

current_file = f"{os.path.basename(__file__)}"


def handle_yak_trigger(yak_manager, topic, payload):
    """
    Orchestrates the command details lookup by first getting the base node
    and then calling the specialized lookup functions.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message="TRIGGER TRIGGER TRIGGER",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )

    try:
        if not YAKETY_YAK_REPO_PATH.is_file():
            console_log(f"❌ Error: Repository file not found at {YAKETY_YAK_REPO_PATH}")
            return

        with open(YAKETY_YAK_REPO_PATH, 'r') as f:
            repo = json.load(f)

        repo_path_parts = topic.replace("OPEN-AIR/repository/", "").split('/')
        
        command_path_to_node = [part.replace(' ', '_') for part in repo_path_parts[:-3]]
        model_key = repo_path_parts[-2]
        
        command_node = get_command_node(repo=repo, command_path_parts=command_path_to_node, function_name=current_function_name)
        if command_node is None:
            return

        scpi_template = lookup_scpi_command(command_node=command_node, model_key=model_key, command_path=command_path_to_node)
        scpi_inputs = lookup_inputs(command_node=command_node, command_path=command_path_to_node)
        command_outputs = lookup_outputs(command_node=command_node, command_path=command_path_to_node)
        
        if scpi_template:
            final_scpi_command = fill_scpi_placeholders(scpi_command_template=scpi_template, scpi_inputs=scpi_inputs)
            
            yak_tx_manager = YakTxManager(dispatcher_instance=yak_manager.dispatcher)
            command_type = repo_path_parts[1]
            response_value = yak_tx_manager.execute_command(command_type=command_type, command_string=final_scpi_command)
            
            if response_value and response_value != "FAILED":
                yak_rx_manager = YakRxManager(mqtt_controller=yak_manager.mqtt_util)
                yak_rx_manager.process_response(path_parts=repo_path_parts, command_details={"scpi_outputs": command_outputs}, response=response_value)
        
        if Local_Debug_Enable:
            debug_log(
                message=f"🔍 Processed trigger for topic: {topic}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
    except Exception as e:
        console_log(f"❌ Error processing trigger for topic {topic}: {e}")
        if Local_Debug_Enable:
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log
            )
    
