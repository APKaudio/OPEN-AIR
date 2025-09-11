# managers/manager_yak_inputs.py
#
# This manager handles loading the command repository and preparing SCPI commands
# by substituting input values.

import os
import inspect
import json
import re
import pathlib
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250910.234000.0"
current_file = f"{os.path.basename(__file__)}"
YAKETY_YAK_REPO_PATH = pathlib.Path("DATA/YAKETYYAK.json")


class YakInputsManager:
    """
    Manages the command repository and input substitution for SCPI commands.
    """
    def __init__(self):
        self.command_repo = {}
        self._load_repo_from_file()

    def _load_repo_from_file(self):
        """
        Loads the command repository from a local JSON file.
        Creates a new, empty repository file if one does not exist or is empty.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        if not YAKETY_YAK_REPO_PATH.parent.exists():
            YAKETY_YAK_REPO_PATH.parent.mkdir(parents=True, exist_ok=True)
            debug_log(
                message=f"🐐🐐🐐📁 Created DATA directory at '{YAKETY_YAK_REPO_PATH.parent}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        
        if YAKETY_YAK_REPO_PATH.is_file() and YAKETY_YAK_REPO_PATH.stat().st_size > 0:
            try:
                with open(YAKETY_YAK_REPO_PATH, 'r') as f:
                    self.command_repo = json.load(f)
                debug_log(
                    message=f"🐐🐐🐐💾 Loaded command repository from local file '{YAKETY_YAK_REPO_PATH}'.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
            except json.JSONDecodeError as e:
                debug_log(
                    message=f"🐐🐐🐐🟡 Failed to decode JSON from file. The error be: {e}. Creating a new, valid repository.",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                self.command_repo = {}
                self._save_repo_to_file()
            except Exception as e:
                debug_log(
                    message=f"🐐🐐🐐🔴 An unexpected error occurred while loading the repository file. The error be: {e}",
                    file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
                )
                self.command_repo = {}
                self._save_repo_to_file()
        else:
            debug_log(
                message=f"🐐🐐🐐🟡 Local repository file not found or is empty at '{YAKETY_YAK_REPO_PATH}'. Creating a new, empty repository.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
            self.command_repo = {}
            self._save_repo_to_file()

    def _save_repo_to_file(self):
        """Saves the current command repository to the local JSON file."""
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            with open(YAKETY_YAK_REPO_PATH, 'w') as f:
                json.dump(self.command_repo, f, indent=4)
            debug_log(
                message=f"🐐🐐🐐💾 Successfully saved command repository to '{YAKETY_YAK_REPO_PATH}'.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        except Exception as e:
            debug_log(
                message=f"🐐🐐🐐🔴 Failed to save repository file. The error be: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

    def update_repo_from_json(self, json_string):
        """
        Replaces the entire in-memory repository with a new JSON payload and saves it.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            new_repo = json.loads(json_string)
            self.command_repo = new_repo
            self._save_repo_to_file()
            debug_log(
                message=f"🐐🐐🐐🔄 Repository successfully updated and saved from a full JSON payload.",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )
        except Exception as e:
            debug_log(
                message=f"🐐🐐🐐🔴 Failed to update repository from JSON payload. The error be: {e}",
                file=current_file, version=current_version, function=current_function_name, console_print_func=console_log
            )

    def prepare_command(self, path_parts, payload_data):
        """
        Navigates the repository, substitutes inputs, and returns the final command string.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        repo_path = self.command_repo
        
        debug_log(f"🐐🐐🐐🔎 Navigating repository to find command details.", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        
        for part in path_parts:
            part_clean = part.replace(" ", "_")
            if part_clean in repo_path:
                repo_path = repo_path.get(part_clean)
            else:
                debug_log(f"🐐🐐🐐❌ Path part '{part_clean}' not found in repository. Aborting.", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
                return None, {}

        if not repo_path:
            debug_log(f"🐐🐐🐐🟡 Aborting! The command blueprints are missing from my glorious repository!", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
            return None, {}
        
        scpi_command_template = repo_path.get('scpi_details', {}).get('generic_model', {}).get('SCPI_value')
        if not scpi_command_template:
            debug_log(f"🐐🐐🐐🔴 No SCPI_value found in command details: {repo_path}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
            return None, {}

        command_string = scpi_command_template
        input_values = payload_data.get('scpi_inputs', {})
        debug_log(f"🐐🐐🐐⚙️ Substituting input values: {input_values}", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        for key, details in input_values.items():
            placeholder = f"<{key}>"
            value_to_substitute = details.get('value', '')
            if placeholder in command_string:
                command_string = command_string.replace(placeholder, str(value_to_substitute))
        
        command_string = re.sub(r'<[^>]+>', '', command_string).strip()
        debug_log(f"🐐🐐🐐📝 Final SCPI command string ready: '{command_string}'", file=current_file, version=current_version, function=current_function_name, console_print_func=console_log)
        
        return command_string, repo_path