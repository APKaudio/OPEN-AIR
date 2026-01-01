# managers/Visa_Fleet_Manager/manager_visa_json_builder.py
#
# Manages the construction and augmentation of JSON data for VISA devices.
#
# Author: Gemini Agent

import json
import os
import datetime
import inspect

try:
    from workers.logger.logger import debug_logger
    from workers.logger.log_utils import _get_log_args
except ModuleNotFoundError:
    print("Warning: 'workers.logger' not found. Using dummy logger for VisaJsonBuilder.")
    def debug_logger(message, *args, **kwargs):
        if kwargs.get('level', 'INFO') != 'DEBUG':
            print(f"[{kwargs.get('level', 'INFO')}] {message}")
    def _get_log_args(*args, **kwargs):
        return {} # Return empty dict, as logger args are not available

# --- Constants ---
# The project root is assumed to be two levels up from this script (OPEN-AIR/managers/Visa_Fleet_Manager)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VISA_FLEET_JSON_PATH = os.path.join(PROJECT_ROOT, "DATA", "VISA_FLEET.json")
QUERY_DATA_DIR = os.path.join(PROJECT_ROOT, "DATA")

# --- KNOWLEDGE BASE (from cli_visa_find.py, moved here for centralization) ---
# Maps Model Number -> {Type, Notes}
KNOWN_DEVICES = {
    "33220A": {"type": "Function Generator", "notes": "20 MHz Arbitrary Waveform"},
    "33210A": {"type": "Function Generator", "notes": "10 MHz Arbitrary Waveform"},
    "34401A": {"type": "Multimeter (DMM)",   "notes": "6.5 Digit Benchtop Standard"},
    "54641D": {"type": "Oscilloscope",       "notes": "Mixed Signal (2 Ana + 16 Dig)"},
    "DS1104Z": {"type": "Oscilloscope",       "notes": "100 MHz, 4 Channel Digital"},
    "66000A": {"type": "Power Mainframe",    "notes": "Modular System (8 Slots)"},
    "66101A": {"type": "DC Power Module",    "notes": "8V / 16A (128W)"},
    "66102A": {"type": "DC Power Module",    "notes": "20V / 7.5A (150W)"},
    "66103A": {"type": "DC Power Module",    "notes": "35V / 4.5A (150W)"},
    "66104A": {"type": "DC Power Module",    "notes": "60V / 2.5A (150W)"},
    "6060B":  {"type": "Electronic Load",    "notes": "DC Load (300 Watt)"},
    "3235":   {"type": "Switch Unit",        "notes": "High-perf Switching Matrix"},
    "3235A":  {"type": "Switch Unit",        "notes": "High-perf Switching Matrix"},
    "N9340B": {"type": "Spectrum Analyzer",  "notes": "Handheld (100 kHz - 3 GHz)"}
}

class VisaJsonBuilder:
    def __init__(self):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_logger(message=f"🛠️ VisaJsonBuilder initialized with {len(KNOWN_DEVICES)} known devices.", **_get_log_args())
        self.known_devices = KNOWN_DEVICES

    def augment_device_details(self, device_entry):
        """
        Looks up the Model Number in KNOWN_DEVICES and adds Type/Notes to the entry.
        """
        model = device_entry.get("model", "Unknown")
        
        # Default values
        device_entry["device_type"] = "Unknown Instrument"
        device_entry["notes"] = "Not in Knowledge Base"
        
        if model in self.known_devices:
            info = self.known_devices[model]
            device_entry["device_type"] = info["type"]
            device_entry["notes"] = info["notes"]
            
        return device_entry

    def save_inventory_to_json(self, inventory_data):
        """Saves the current fleet inventory to a JSON file, grouped by device_type and model."""
        filepath = VISA_FLEET_JSON_PATH
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Group the inventory data before saving
            grouped_data = self._group_devices_by_type_and_model(inventory_data)

            with open(filepath, 'w') as f:
                json.dump(grouped_data, f, indent=4)
            debug_logger(f"✅ Saved fleet inventory to {filepath}", **_get_log_args())
        except Exception as e:
            debug_logger(f"❌ Error saving inventory to JSON: {e}", **_get_log_args(), level="ERROR")

    def load_inventory_from_json(self):
        """Loads fleet inventory from a JSON file if it exists."""
        filepath = VISA_FLEET_JSON_PATH
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    inventory = json.load(f)
                debug_logger(f"✅ Loaded fleet inventory from {filepath} with {len(inventory)} devices.", **_get_log_args())
                return inventory
            except json.JSONDecodeError as e:
                debug_logger(f"❌ Error decoding inventory JSON from {filepath}: {e}", **_get_log_args(), level="ERROR")
                # Optionally, backup the corrupted file and create an empty one
                # os.rename(filepath, f"{filepath}.corrupted_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
                return {} # Return empty dict since the structure is now grouped
            except Exception as e:
                debug_logger(f"❌ Error loading inventory from JSON: {e}", **_get_log_args(), level="ERROR")
                return {} # Return empty dict
        else:
            debug_logger(f"ℹ️ No existing inventory file found at {filepath}. Initializing empty inventory.", **_get_log_args())
            return {} # Return empty dict for new grouped structure

    def save_query_response_to_json(self, serial, response, command, corr_id):
        """
        Saves a query response to a JSON file in the DATA directory.
        Filename format: DATA/{serial}_query_{timestamp}.json
        """
        os.makedirs(QUERY_DATA_DIR, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{serial}_query_{timestamp}.json"
        filepath = os.path.join(QUERY_DATA_DIR, filename)

        query_data = {
            "serial_number": serial,
            "command": command,
            "response": response,
            "correlation_id": corr_id,
            "timestamp": datetime.datetime.now().isoformat()
        }

        try:
            with open(filepath, 'w') as f:
                json.dump(query_data, f, indent=4)
            debug_logger(f"✅ Saved query response for {serial} to {filepath}", **_get_log_args())
        except Exception as e:
            debug_logger(f"❌ Error saving query response to JSON: {e}", **_get_log_args(), level="ERROR")

    def _group_devices_by_type_and_model(self, inventory_data):
        """
        Groups a flat list of device dictionaries first by 'device_type' and then by 'model'.
        """
        grouped_data = {}
        # Ensure inventory_data is a list of device dictionaries
        if isinstance(inventory_data, dict):
            inventory_data = list(inventory_data.values())

        for device in inventory_data:
            device_type = device.get("device_type", "Unknown Type")
            model = device.get("model", "Unknown Model")

            if device_type not in grouped_data:
                grouped_data[device_type] = {}
            if model not in grouped_data[device_type]:
                grouped_data[device_type][model] = []
            grouped_data[device_type][model].append(device)
        return grouped_data

