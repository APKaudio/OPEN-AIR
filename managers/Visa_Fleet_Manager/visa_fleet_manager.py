# managers/Visa_Fleet_Manager/visa_fleet_manager.py
#
# The STANDALONE orchestrator. No MQTT dependencies.
#
# Author: Gemini Agent
#

import threading
import time
import inspect
import json
import os
import string
import datetime # For timestamp in query filename

try:
    from workers.logger.logger import debug_logger
    from workers.logger.log_utils import _get_log_args
except ModuleNotFoundError:
    print("Warning: 'workers.logger' not found. Using dummy logger for VisaFleetManager.")
    def debug_logger(message, *args, **kwargs):
        if kwargs.get('level', 'INFO') != 'DEBUG':
            print(f"[{kwargs.get('level', 'INFO')}] {message}")
    def _get_log_args(*args, **kwargs):
        return {} # Return empty dict, as logger args are not available
from managers.Visa_Fleet_Manager.manager_visa_supervisor import VisaFleetSupervisor

# --- Constants ---
# The project root is assumed to be three levels up from this script (OPEN-AIR/managers/Visa_Fleet_Manager)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
VISA_FLEET_JSON_PATH = os.path.join(PROJECT_ROOT, "DATA", "VISA_FLEET.json")
QUERY_DATA_DIR = os.path.join(PROJECT_ROOT, "DATA") # This path is correct with updated PROJECT_ROOT


# --- KNOWLEDGE BASE (from cli_visa_find.py) ---
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

class VisaFleetManager:
    def __init__(self):
        current_function_name = inspect.currentframe().f_code.co_name
        debug_logger(
            message=f"💳 🟢️️️🟢 Initializing VisaFleetManager. The commander of the fleet is online!",
            **_get_log_args()
        )
        
        # Callbacks are initially empty (No-op)
        self.cb_inventory = lambda x: None
        self.cb_response = lambda s, r, c, i: None
        self.cb_error = lambda s, m, c: None
        self.cb_status = lambda s, st: None

        self._current_inventory = [] # Internal storage for the latest inventory
        self._load_inventory_from_json() # Load inventory on startup

        # Initialize Supervisor (Headless)
        self.fleet_supervisor = VisaFleetSupervisor(manager_ref=self)
        self._running = False
        
        debug_logger(message=f"💳 ✅ VisaFleetManager initialized. Supervisor ready.", **_get_log_args())

    def _get_inventory_filepath(self):
        """Returns the absolute path to the inventory JSON file."""
        return VISA_FLEET_JSON_PATH

    def _save_inventory_to_json(self, inventory_data):
        """Saves the current fleet inventory to a JSON file."""
        filepath = self._get_inventory_filepath()
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Ensure inventory_data is a list of dictionaries for json.dump
            if isinstance(inventory_data, dict): # If it's the dict from supervisor, convert
                data_to_save = list(inventory_data.values())
            else:
                data_to_save = inventory_data

            with open(filepath, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            debug_logger(f"💳 Saved fleet inventory to {filepath}", **_get_log_args())
        except Exception as e:
            debug_logger(f"💳 Error saving inventory to JSON: {e}", **_get_log_args(), level="ERROR")

    def _load_inventory_from_json(self):
        """Loads fleet inventory from a JSON file if it exists."""
        filepath = self._get_inventory_filepath()
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    self._current_inventory = json.load(f)
                debug_logger(f"💳 Loaded fleet inventory from {filepath} with {len(self._current_inventory)} devices.", **_get_log_args())
            except json.JSONDecodeError as e:
                debug_logger(f"💳 Error decoding inventory JSON from {filepath}: {e}", **_get_log_args(), level="ERROR")
                self._current_inventory = [] # Reset on error
            except Exception as e:
                debug_logger(f"💳 Error loading inventory from JSON: {e}", **_get_log_args(), level="ERROR")
                self._current_inventory = [] # Reset on error
        else:
            debug_logger(f"💳 No existing inventory file found at {filepath}.", **_get_log_args())
            self._current_inventory = [] # Initialize empty if file doesn't exist

    def _save_query_response_to_json(self, serial, response, command, corr_id):
        """
        Saves a query response to a JSON file in the DATA directory.
        Filename format: DATA/{serial}_query_{timestamp}.json
        """
        os.makedirs(QUERY_DATA_DIR, exist_ok=True) # Ensure DATA directory exists

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
            debug_logger(f"💳 Saved query response for {serial} to {filepath}", **_get_log_args())
        except Exception as e:
            debug_logger(f"💳 Error saving query response to JSON: {e}", **_get_log_args(), level="ERROR")


    def set_callbacks(self, on_inventory_update, on_device_response, on_device_error, on_proxy_status):
        """Link external listeners (like the MQTT Bridge or a GUI) to internal events."""
        self.cb_inventory = on_inventory_update
        self.cb_response = on_device_response
        self.cb_error = on_device_error
        self.cb_status = on_proxy_status

    def start(self):
        self._running = True
        debug_logger("💳 Core: VisaFleetManager Started (Standalone Mode).", **_get_log_args())

    def stop(self):
        self._running = False
        if self.fleet_supervisor: # Ensure supervisor exists before trying to shut it down
            self.fleet_supervisor.shutdown()
        debug_logger("💳 Core: VisaFleetManager Stopped.", **_get_log_args())


    def trigger_scan(self):
        """Public API to start a scan."""
        debug_logger("💳 Core: Scan Triggered via API.", **_get_log_args())
        self.fleet_supervisor.scan_and_manage_fleet()

    def enqueue_command(self, serial, command, query=False, correlation_id="N/A"):
        """Public API to send a command to a specific device."""
        proxy = self.fleet_supervisor.get_proxy_for_device(serial)
        if proxy:
            proxy.enqueue_command(command, query, correlation_id)
        else:
            self.cb_error(serial, "Device not found in fleet manager", command)

    # --- Internal Event Handlers (Called by Supervisor/Proxies) ---
    
    def _augment_device_details(self, device_entry):
        """
        Looks up the Model Number in KNOWN_DEVICES and adds Type/Notes to the entry.
        """
        model = device_entry.get("model", "Unknown")
        
        # Default values
        device_entry["device_type"] = "Unknown Instrument"
        device_entry["notes"] = "Not in Knowledge Base"
        
        if model in KNOWN_DEVICES:
            info = KNOWN_DEVICES[model]
            device_entry["device_type"] = info["type"]
            device_entry["notes"] = info["notes"]
            
        return device_entry

    def _notify_inventory(self, inventory_data):
        """Receives updated inventory from Supervisor, augments it, and saves it."""
        augmented_inventory = []
        for device_entry in inventory_data:
            augmented_inventory.append(self._augment_device_details(device_entry))

        self._current_inventory = augmented_inventory
        self._save_inventory_to_json(augmented_inventory)
        self.cb_inventory(augmented_inventory)

    def _notify_response(self, serial, response, command, corr_id):
        """Receives device response and saves it to a JSON file."""
        self._save_query_response_to_json(serial, response, command, corr_id)
        self.cb_response(serial, response, command, corr_id)

    def _notify_error(self, serial, message, command):
        self.cb_error(serial, message, command)

    def _notify_status(self, serial, status):
        self.cb_status(serial, status)

    @property
    def current_inventory(self):
        """Returns the last known inventory list."""
        return self._current_inventory