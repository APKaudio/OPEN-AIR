# workers/builder/dynamic_gui_config_loader.py
#
# This file (dynamic_gui_config_loader.py) provides utility functions to derive JSON configuration file paths from base topics, searching specific 'datasets' subdirectories.
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


import inspect
import pathlib
import os # For os.path.basename and os.getcwd

# Assuming sys.path is already set up by main.py
from display.logger import debug_log, console_log, log_visa_command

# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent
current_file = str(current_file_path.relative_to(project_root)).replace("\\", "/")

DATASET_ROOT_DIR = project_root / "datasets" # Using project_root to define DATASET_ROOT_DIR

def get_json_filepath_from_base_topic(
    base_topic: str,
    class_name: str, # Pass the class name from the caller for logging
    calling_file: str, # Pass the calling file for logging
    calling_version: str, # Pass the calling version for logging
    console_print_func # Pass the console_log from the caller for logging
) -> pathlib.Path | None:
    """
    Derives the JSON configuration file path from the base_topic.
    Searches in 'datasets/YAK', 'datasets/configuration', and 'datasets/Orchestration'.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    
    # Determine the relevant subdirectory and base filename part
    core_topic_name = ""
    target_subdir = ""
    filename_prefix = ""

    if base_topic.lower().startswith("open-air/yak/"):
        core_topic_name = base_topic[len("open-air/"):].lower().replace('/', '_')
        target_subdir = "YAK"
        filename_prefix = "dataset_"
    elif base_topic.lower().startswith("open-air/configuration/"):
        core_topic_name = base_topic[len("open-air/configuration/"):].lower().replace('/', '_')
        target_subdir = "configuration"
        filename_prefix = "dataset_configuration_"
    elif base_topic.lower().startswith("open-air/dataset/orchestration"): # New Orchestration topic
        core_topic_name = base_topic[len("open-air/dataset/orchestration"):].lower().replace('/', '_').strip('_')
        target_subdir = "Orchestration"
        filename_prefix = "dataset_configuration_"
        if not core_topic_name: # If topic is just "open-air/dataset/orchestration"
            core_topic_name = "orchestration"
    else:
        # Handle topics that don't fit the OPEN-AIR/repository or OPEN-AIR/configuration pattern
        
        # Special handling for "application"
        if base_topic.lower() == "application":
            app_config_filename = "dataset_configuration_application.json"
            app_config_filepath = DATASET_ROOT_DIR / "configuration" / app_config_filename
            if app_config_filepath.is_file():
                debug_log(
                    message=f"🔍🔵 Found JSON config for 'application' at: {app_config_filepath}",
                    file=calling_file,
                    version=calling_version,
                    function=f"{class_name}.{current_function_name}",
                    console_print_func=console_print_func
                )
                return app_config_filepath

        # Special handling for "application_filepaths"
        if base_topic.lower() == "application_filepaths":
            app_filepaths_config_filename = "dataset_configuration_application_filepaths.json"
            app_filepaths_config_filepath = DATASET_ROOT_DIR / "configuration" / app_filepaths_config_filename
            if app_filepaths_config_filepath.is_file():
                debug_log(
                    message=f"🔍🔵 Found JSON config for 'application_filepaths' at: {app_filepaths_config_filepath}",
                    file=calling_file,
                    version=calling_version,
                    function=f"{class_name}.{current_function_name}",
                    console_print_func=console_print_func
                )
                debug_log(
                    message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: {app_filepaths_config_filepath}",
                    file=calling_file,
                    version=calling_version,
                    function=f"{class_name}.{current_function_name}",
                    console_print_func=console_print_func
                )
                return app_filepaths_config_filepath

        # Handle "Orchestration" (previously "Start-Stop-Pause")
        # This block is for base_topic == "Orchestration" explicitly
        if base_topic.lower() == "orchestration":
            orchestration_filename = "dataset_configuration_orchestration.json"
            orchestration_filepath = DATASET_ROOT_DIR / "Orchestration" / orchestration_filename
            if orchestration_filepath.is_file():
                debug_log(
                    message=f"🔍🔵 Found JSON config for 'Orchestration' at: {orchestration_filepath}",
                    file=calling_file,
                    version=calling_version,
                    function=f"{class_name}.{current_function_name}",
                    console_print_func=console_print_func
                )
                debug_log(
                    message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: {orchestration_filepath}",
                    file=calling_file,
                    version=calling_version,
                    function=f"{class_name}.{current_function_name}",
                    console_print_func=console_print_func
                )
                return orchestration_filepath
        
        # Fallback for other cases (e.g., if topic structure is simpler or unknown prefix)
        simple_topic_parts = base_topic.lower().replace('/', '_')
        
        repo_filename = f"dataset_YAK_{simple_topic_parts}.json"
        repo_filepath = DATASET_ROOT_DIR / "YAK" / repo_filename
        if repo_filepath.is_file():
            debug_log(
                message=f"🔍🔵 Found JSON config (fallback repo) at: {repo_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            debug_log(
                message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: {repo_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            return repo_filepath
        
        config_filename = f"dataset_configuration_{simple_topic_parts}.json"
        config_filepath = DATASET_ROOT_DIR / "configuration" / config_filename
        if config_filepath.is_file():
            debug_log(
                message=f"🔍🔵 Found JSON config (fallback config) at: {config_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            debug_log(
                message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: {config_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            return config_filepath

        debug_log(
            message=f"⚠️ Warning: No JSON config file found for base_topic: {base_topic}",
            file=calling_file,
            version=calling_version,
            function=f"{class_name}.{current_function_name}",
            console_print_func=console_print_func
        )
        debug_log(
            message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: None (No file found)",
            file=calling_file,
            version=calling_version,
            function=f"{class_name}.{current_function_name}",
            console_print_func=console_print_func
        )
        return None
        
    # If a specific prefix was matched (OPEN-AIR/yak or OPEN-AIR/configuration or OPEN-AIR/dataset/orchestration)
    if core_topic_name:
        final_filename = f"{filename_prefix}{core_topic_name}.json"
        final_filepath = DATASET_ROOT_DIR / target_subdir / final_filename
        if final_filepath.is_file():
            debug_log(
                message=f"🔍🔵 Found JSON config (prefixed match) at: {final_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            debug_log(
                message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: {final_filepath}",
                file=calling_file,
                version=calling_version,
                function=f"{class_name}.{current_function_name}",
                console_print_func=console_print_func
            )
            return final_filepath

    debug_log(
        message=f"⚠️ Warning: No JSON config file found for base_topic: {base_topic}",
        file=calling_file,
        version=calling_version,
        function=f"{class_name}.{current_function_name}",
        console_print_func=console_print_func
    )
    debug_log(
        message=f"🔍🔵 Exiting get_json_filepath_from_base_topic() with path: None (No file found)",
        file=calling_file,
        version=calling_version,
        function=f"{class_name}.{current_function_name}",
        console_print_func=console_print_func
    )
    return None
