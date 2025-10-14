# managers/manager_visa_device_search.py
#
# This manager handles all low-level VISA instrument search and connection logic,
# now publishing all device status and information to the MQTT broker.
#
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
#
# Version 20250907.002515.6 (Fixed GUI slot mapping to start at option 1)

import inspect
import os
import traceback
import pyvisa
import tkinter as tk
import json
import datetime
import threading
from workers.worker_mqtt_controller_util import MqttControllerUtility
from managers.manager_visa_dispatch_scpi import ScpiDispatcher

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log


# --- Global Scope Variables --
current_version = "20250907.002515.6"
current_version_hash = (20250907 * 2515 * 6)
current_file = f"{os.path.basename(__file__)}"

# --- New Constant for Max Devices ---
MAX_GUI_DEVICE_SLOTS = 40


class VisaDeviceManager:
    """
    Manages VISA device discovery and connection logic.
    """

    def __init__(self, mqtt_controller: MqttControllerUtility, scpi_dispatcher: ScpiDispatcher):
        # Initializes the manager, sets up state variables and MQTT subscriptions.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🟢 Initiating the grand VISA device management experiment!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_util = mqtt_controller
            self.scpi_dispatcher = scpi_dispatcher
            self.inst = None
            self.found_resources = []
            self.selected_device_resource = None
            self._setup_mqtt_subscriptions()
            console_log("✅ The magnificent VISA Device Manager is online and ready for action!")
        except Exception as e:
            console_log(f"❌ Error in {self.__class__.__name__}.{current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 By Jove, the initialization has gone haywire! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def search_resources(self, console_print_func):
        # Performs the search and directly returns a list of resources.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"GUI command received: initiating VISA resource search.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        resources = list_visa_resources(console_print_func)
        return resources

    def connect_instrument(self, resource_name, console_print_func):
        # Triggers a connection to a specific resource by publishing a command.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Command received: initiating connection to {resource_name}.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        payload = json.dumps({"resource": resource_name})
        self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument/connect", subtopic="", value=payload)

    def disconnect_instrument(self, console_print_func):
        # Triggers a disconnection by publishing a command.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Command received: initiating disconnection.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument/disconnect", subtopic="", value="disconnect")

    def _setup_mqtt_subscriptions(self):
        # Subscribes to MQTT topics for receiving commands from the GUI.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🛠️🔵 My minions are tuning the receivers! Subscribing to command topics.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # FIXED: Subscribing to the new '/trigger' subtopic
            self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Search_For_devices/trigger", callback_func=self._on_search_request)
            self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Found_devices/options/+/selected", callback_func=self._on_device_select)
            self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Connect_to_Device/trigger", callback_func=self._on_gui_connect_request)
            self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Disconnect_device/trigger", callback_func=self._on_gui_disconnect_request)
            
            console_log("✅ VisaDeviceManager subscribed to all necessary GUI and command topics.")
        except Exception as e:
            console_log(f"❌ Error in {self.__class__.__name__}.{current_function_name}: {e}")

    def _on_search_request(self, topic, payload):
        # Handles the 'Search_For_devices' button press from the GUI.
        try:
            payload_data = json.loads(payload)
            # FIXED: Look for an explicit 'true' value
            if str(payload_data.get('value')).lower() == 'true':
                console_log("🔍 Search for devices initiated from GUI.")
                self.found_resources = self.search_resources(console_log)
                self._update_found_devices_gui(self.found_resources)
        except (json.JSONDecodeError, AttributeError):
            pass

    def _on_device_select(self, topic, payload):
        # Handles a device selection from the listbox.
        try:
            payload_data = json.loads(payload)
            # FIXED: Look for an explicit 'true' value
            if str(payload_data.get('value')).lower() == 'true':
                parts = topic.split('/')
                option_index = int(parts[-2]) - 1
                if 0 <= option_index < len(self.found_resources):
                    self.selected_device_resource = self.found_resources[option_index]
                    console_log(f"✅ Device selected: {self.selected_device_resource}")
                else:
                    self.selected_device_resource = None
        except (json.JSONDecodeError, IndexError, ValueError, AttributeError):
            pass

    def _on_gui_connect_request(self, topic, payload):
        # Handles the 'Connect_to_Device' button press.
        try:
            payload_data = json.loads(payload)
            # FIXED: Look for an explicit 'true' value
            if str(payload_data.get('value')).lower() == 'true':
                if self.selected_device_resource:
                    console_log(f"🔵 Initiating connection to {self.selected_device_resource}...")
                    thread = threading.Thread(target=self.connect_instrument_logic, args=(self.selected_device_resource, console_log,), daemon=True)
                    thread.start()
                else:
                    console_log("🟡 No device selected to connect.")
        except (json.JSONDecodeError, AttributeError):
            pass

    def _on_gui_disconnect_request(self, topic, payload):
        # Handles the 'Disconnect_device' button press.
        try:
            payload_data = json.loads(payload)
            # FIXED: Look for an explicit 'true' value
            if str(payload_data.get('value')).lower() == 'true':
                if self.inst:
                    console_log("🔵 Initiating disconnection...")
                    thread = threading.Thread(target=self.disconnect_instrument_logic, args=(console_log,), daemon=True)
                    thread.start()
                else:
                    console_log("🟡 No device is currently connected.")
        except Exception as e:
            console_log(f"❌ Error in _on_gui_disconnect_request: {e}")
            
    def _update_found_devices_gui(self, resources):
        # Updates the GUI's `Found_devices` listbox based on the search results,
        # supporting up to MAX_GUI_DEVICE_SLOTS (40) devices.
        try:
            base_topic = "OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Found_devices"
            
            # Use min() to ensure we don't try to fill more slots than exist or are needed
            num_resources_to_show = min(len(resources), MAX_GUI_DEVICE_SLOTS)
            
            # 1. Populate the slots with found resources
            # NOTE: range starts at 1 and goes up to num_resources_to_show + 1
            for i in range(1, num_resources_to_show + 1):
                option_topic_prefix = f"{base_topic}/options/{i}"
                device_name = resources[i-1]
                
                # Activate slot and set labels
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/active", subtopic="", value="true", retain=False)
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/label_active", subtopic="", value=device_name, retain=False)
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/label_inactive", subtopic="", value=device_name, retain=False)
                
            # 2. Deactivate remaining slots (from num_resources_to_show + 1 up to MAX_GUI_DEVICE_SLOTS)
            for i in range(num_resources_to_show + 1, MAX_GUI_DEVICE_SLOTS + 1):
                option_topic_prefix = f"{base_topic}/options/{i}"
                
                # Deactivate slot and clear labels
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/active", subtopic="", value="false", retain=False)
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/label_active", subtopic="", value="", retain=False)
                self.mqtt_util.publish_message(topic=f"{option_topic_prefix}/label_inactive", subtopic="", value="", retain=False)
            
            # Set the first item as selected if any were found
            if resources:
                first_device_topic = f"{base_topic}/options/1/selected"
                self.mqtt_util.publish_message(topic=first_device_topic, subtopic="", value='true', retain=False)
                console_log("✅ First device automatically selected after search.")
            
            console_log("✅ GUI device list updated with search results (up to 40 slots used).")
        except Exception as e:
            console_log(f"❌ Error in _update_found_devices_gui: {e}")

    def _publish_status(self, topic_suffix, value):
        # Helper function to publish a value to a specific status topic.
        if self.mqtt_util:
            base_topic = "OPEN-AIR/configuration/instrument/active/Instrument_Connection/Search_and_Connect/Device_status"
            self.mqtt_util.publish_message(topic=f"{base_topic}/{topic_suffix}", subtopic="value", value=value, retain=False)

    def _on_connect_request(self, topic, payload):
        # Handles an MQTT connect request to a specific VISA resource.
        try:
            payload_data = json.loads(payload)
            resource_name = payload_data.get('resource')
            if resource_name:
                thread = threading.Thread(target=self.connect_instrument_logic, args=(resource_name, console_log,), daemon=True)
                thread.start()
        except json.JSONDecodeError:
            console_log("❌ Failed to decode JSON payload for connect request.")

    def connect_instrument_logic(self, resource_name, console_print_func):
        # Handles the full connection sequence to a VISA instrument.
        try:
            self.inst = connect_to_instrument(resource_name, console_print_func)
            if not self.inst:
                # Tell the dispatcher we are not connected
                self.scpi_dispatcher.set_instrument_instance(inst=None)
                self._publish_status("connected", False)
                self._publish_status("disconnected", True)
                return False
            # Update the dispatcher with the new instrument instance
            self.scpi_dispatcher.set_instrument_instance(inst=self.inst)

            idn_response = self.inst.query('*IDN?')
            idn_parts = idn_response.strip().split(',')
            manufacturer = idn_parts[0].strip() if len(idn_parts) >= 1 else "N/A"
            model = idn_parts[1].strip() if len(idn_parts) >= 2 else "N/A"
            serial_number = idn_parts[2].strip() if len(idn_parts) >= 3 else "N/A"
            firmware = idn_parts[3].strip() if len(idn_parts) >= 4 else "N/A"
            self._publish_status("brand", manufacturer)
            self._publish_status("device_model", model)
            self._publish_status("device_series", model)
            self._publish_status("device_serial_number", serial_number)
            self._publish_status("device_firmware", firmware)
            self._publish_status("visa_resource", resource_name)
            self._publish_status("Time_connected", datetime.datetime.now().strftime("%H:%M:%S"))
            self._publish_status("connected", True)
            self._publish_status("disconnected", False)
            return True
        except Exception as e:
            console_log(f"❌ Error during connection logic: {e}")
            self.disconnect_instrument_logic(console_print_func)
            return False

    def _on_disconnect_request(self, topic, payload):
        # Handles an MQTT disconnect request.
        if self.inst:
            thread = threading.Thread(target=self.disconnect_instrument_logic, args=(console_log,), daemon=True)
            thread.start()
        else:
            console_log("⚠️ No instrument is currently connected to disconnect.")

    def disconnect_instrument_logic(self, console_print_func):
        # Disconnects the application from the currently connected VISA instrument.
        if not self.inst:
            return True
        result = disconnect_instrument(self.inst, console_print_func)
        self.inst = None
        # Tell the dispatcher we are disconnected
        self.scpi_dispatcher.set_instrument_instance(inst=None)
        self.selected_device_resource = None
        self._publish_status("disconnected", True)
        self._publish_status("connected", False)
        self._publish_status("brand", "N/A")
        self._publish_status("device_model", "N/A")
        self._publish_status("device_series", "N/A")
        self._publish_status("device_serial_number", "N/A")
        self._publish_status("device_firmware", "N/A")
        self._publish_status("visa_resource", "N/A")
        self._publish_status("Time_connected", "N/A")
        return result

def list_visa_resources(console_print_func=None):
    # Lists available VISA resources (instruments).
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Listing VISA resources... Let's find some devices!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    try:
        rm = pyvisa.ResourceManager()
        
        # KEY CHANGE: Explicitly search for all instrument types, especially TCPIP.
        # '?*::INSTR' is the wildcard search pattern for all resource types supported by the backend.
        all_resources = rm.list_resources('?*::INSTR') 

        # --- Resource Reordering Logic (FIX) ---
        usb_resources = []
        tcpip_resources = []
        other_resources = []

        for res in all_resources:
            if res.startswith('USB'):
                usb_resources.append(res)
            elif res.startswith('TCPIP'):
                tcpip_resources.append(res)
            else: # Catches ASRL, GPIB, etc.
                other_resources.append(res)
        
        # Prioritize list: USB -> TCPIP -> Other (ASRL)
        resources = usb_resources + tcpip_resources + other_resources
        # --- End Resource Reordering Logic ---
        
        debug_log(message=f"Found VISA resources (Reordered): {resources}.", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}."
        console_print_func(error_msg)
        debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return []

def connect_to_instrument(resource_name, console_print_func=None):
    # Establishes a connection to a VISA instrument.
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"Connecting to instrument: {resource_name}. Fingers crossed!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 5000
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.query_delay = 0.1
        console_print_func(f"✅ Successfully connected to {resource_name}.")
        debug_log(message=f"Connection successful to {resource_name}. We're in!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return inst
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}."
        console_print_func(error_msg)
        debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
        return None

def disconnect_instrument(inst, console_print_func=None):
    # Closes the connection to a VISA instrument.
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message="Disconnecting instrument... Saying goodbye!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    if inst:
        try:
            inst.close()
            console_print_func("✅ Instrument disconnected.")
            debug_log(message="Instrument connection closed. All done!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
            return True
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}."
            console_print_func(error_msg)
            debug_log(message=error_msg, file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
            return False
    debug_log(message="No instrument to disconnect. Already gone!", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function, console_print_func=console_print_func)
    return False
