# managers/manager_visa_device_search.py
#
# This manager handles all low-level VISA instrument search and connection logic,
# now publishing all device status and information to the MQTT broker.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Version 20250902.235024.3 (UPDATED: Implemented a synchronous resource search method.)

import inspect
import os
import traceback
import pyvisa
import tkinter as tk
import json
import datetime
import threading
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log


# --- Global Scope Variables ---
current_version = "20250902.235024.3"
current_file = f"{os.path.basename(__file__)}"


class VisaDeviceManager():
    """
    Manages VISA device discovery and connection logic.
    """

    def __init__(self, mqtt_controller: MqttControllerUtility):
        self.mqtt_util = mqtt_controller
        self.inst = None
        self._setup_mqtt_subscriptions()

    # Public method for the GUI to trigger a search
    def search_resources(self, console_print_func):
        """
        FIX: This method is now synchronous. It performs the search and directly returns
        a list of resources, bypassing the MQTT bus for this specific transaction.
        """
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

    # NEW: Public method for the GUI to trigger a connection
    def connect_instrument(self, resource_name, console_print_func):
        """
        Triggers a connection to a specific resource by publishing a command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"GUI command received: initiating connection to {resource_name}.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        payload = json.dumps({"resource": resource_name})
        self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument/connect", subtopic="", value=payload)

    # NEW: Public method for the GUI to trigger a disconnection
    def disconnect_instrument(self, console_print_func):
        """
        Triggers a disconnection by publishing a command.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"GUI command received: initiating disconnection.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        self.mqtt_util.publish_message(topic="OPEN-AIR/commands/instrument/disconnect", subtopic="", value="disconnect")


    def _setup_mqtt_subscriptions(self):
        """
        Subscribes to MQTT topics for receiving commands from the GUI.
        """
        # FIX: The search command is now a direct function call, so we no longer need a subscriber for it here.
        # self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/commands/instrument/search", callback_func=self._on_search_request)
        self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/commands/instrument/connect", callback_func=self._on_connect_request)
        self.mqtt_util.add_subscriber(topic_filter="OPEN-AIR/commands/instrument/disconnect", callback_func=self._on_disconnect_request)
        
        console_log("✅ VisaDeviceManager subscribed to command topics.")

    def _publish_status(self, topic_suffix, value):
        """
        Helper function to publish a value to a specific status topic.
        """
        if self.mqtt_util:
            base_topic = "OPEN-AIR/configuration/instrument/active/Instrument/fields"
            full_topic = f"{base_topic}/{topic_suffix}"
            self.mqtt_util.publish_message(topic=full_topic, subtopic="value", value=value, retain=False)
        else:
            console_log(f"❌ MQTT utility not initialized. Cannot publish to {topic_suffix}.")




    def populate_resources_logic(self, console_print_func):
        """
        Populates the MQTT topics with available VISA instrument addresses.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Populating VISA resources. Let's find those devices! Version: {current_version}",
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        resources = list_visa_resources(console_print_func)
        # FIX: The manager no longer publishes the resource list. It is returned directly.
        # self.mqtt_util.publish_message(topic="OPEN-AIR/status/instrument/resources", subtopic="list", value=json.dumps(resources))
        if resources:
            self.mqtt_util.publish_message(topic="OPEN-AIR/status/instrument/resources", subtopic="selected", value=resources[0])
            debug_log(
                message=f"Found and published VISA resources: {resources}. Success!",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
        else:
            console_print_func("No VISA instruments found. Check connections.")
            debug_log(
                message="No VISA resources found. Time for some detective work. 🕵️‍♀️",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )

    def _on_connect_request(self, topic, payload):
        """
        Handles an MQTT connect request to a specific VISA resource.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"MQTT Command: '{topic}' received. Starting connection process.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_log
        )
        try:
            payload_data = json.loads(payload)
            resource_name = payload_data.get('resource')
            if resource_name:
                thread = threading.Thread(target=self.connect_instrument_logic, args=(resource_name, console_log,), daemon=True)
                thread.start()
            else:
                console_log("❌ Connect request received without a valid resource name.")
                self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=False)
        except json.JSONDecodeError:
            console_log("❌ Failed to decode JSON payload for connect request.")
            self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=False)


    def connect_instrument_logic(self, resource_name, console_print_func):
        """
        Handles the full connection sequence to a VISA instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Attempting to connect to instrument. Let's make this happen! Version: {current_version}",
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        
        try:
            self.inst = connect_to_instrument(resource_name, console_print_func)
            if not self.inst:
                self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=False)
                return False

            try:
                idn_response = self.inst.query('*IDN?')
                idn_parts = idn_response.strip().split(',')
            except pyvisa.errors.VisaIOError as e:
                console_log(f"❌ VISA error querying IDN: {e}.")
                idn_parts = []
                
            manufacturer = idn_parts[0].strip() if len(idn_parts) >= 1 else "N/A"
            model = idn_parts[1].strip() if len(idn_parts) >= 2 else "N/A"
            serial_number = idn_parts[2].strip() if len(idn_parts) >= 3 else "N/A"
            version = idn_parts[3].strip() if len(idn_parts) >= 4 else "N/A"

            # Publish all details to MQTT
            self._publish_status("brand", manufacturer)
            self._publish_status("device_model", model)
            self._publish_status("device_serial_number", serial_number)
            self._publish_status("device_firmware", version)
            self._publish_status("visa_resource", resource_name)
            self._publish_status("Time_connected", datetime.datetime.now().strftime("%H:%M:%S"))
            self._publish_status("connected", True)
            self._publish_status("disconnected", False)


            self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=True)
            debug_log(
                message="Connection successful! The instrument is alive! 🥳",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            return True
        
        except Exception as e:
            console_print_func(f"❌ Error during connection: {e}")
            debug_log(
                message=f"Connection failed spectacularly! Error: {e}. Traceback: {traceback.format_exc()}",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            self.disconnect_instrument_logic(console_print_func)
            return False

    def _on_disconnect_request(self, topic, payload):
        """
        Handles an MQTT disconnect request.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"MQTT Command: '{topic}' received. Starting disconnection process.",
            file=current_file,
            version=current_version,
            function=current_function,
            console_print_func=console_log
        )
        
        if self.inst:
            thread = threading.Thread(target=self.disconnect_instrument_logic, args=(console_log,), daemon=True)
            thread.start()
        else:
            console_log("⚠️ No instrument is currently connected to disconnect.")
            self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=False)
            self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/disconnected/value", subtopic="", value=True)
            
    def disconnect_instrument_logic(self, console_print_func):
        """
        Disconnects the application from the currently connected VISA instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Attempting to disconnect instrument. Version: {current_version}",
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        
        if not self.inst:
            console_print_func("⚠️ Warning: No instrument connected. Nothing to disconnect.")
            debug_log(
                message="No instrument to disconnect. This is a mess.",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            return True
        
        result = disconnect_instrument(self.inst, console_print_func)
        self.inst = None
        
        if result:
            debug_log(
                message="Successfully disconnected. Until we meet again! 👋",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
        else:
            debug_log(
                message="Disconnecting failed. This is a catastrophe!",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            
        # Publish disconnection status
        self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/disconnected/value", subtopic="", value=True)
        self.mqtt_util.publish_message(topic="OPEN-AIR/configuration/instrument/active/Instrument/fields/connected/value", subtopic="", value=False)
        self._publish_status("brand", "N/A")
        self._publish_status("device_model", "N/A")
        self._publish_status("device_serial_number", "N/A")
        self._publish_status("device_firmware", "N/A")
        self._publish_status("visa_resource", "N/A")
        self._publish_status("Time_connected", "N/A")

        return result
    
    # --- Internal VISA Utility Functions ---
def list_visa_resources(console_print_func=None):
    """
    Lists available VISA resources (instruments).
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(
        message="Listing VISA resources... Let's find some devices!",
        file=f"{os.path.basename(__file__)}",
        version=current_version,
        function=current_function,
        console_print_func=console_print_func
    )
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        debug_log(
            message=f"Found VISA resources: {resources}.",
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}."
        console_print_func(error_msg)
        debug_log(
            message=error_msg,
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        return []


def connect_to_instrument(resource_name, console_print_func=None):
    """
    Establishes a connection to a VISA instrument.
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"Connecting to instrument: {resource_name}. Fingers crossed!",
        file=f"{os.path.basename(__file__)}",
        version=current_version,
        function=current_function,
        console_print_func=console_print_func
    )
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 10000
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.query_delay = 0.1
        console_print_func(f"✅ Successfully connected to {resource_name}.")
        debug_log(
            message=f"Connection successful to {resource_name}. We're in!",
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        return inst
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"❌ VISA error connecting to {resource_name}: {e}."
        console_print_func(error_msg)
        debug_log(
            message=error_msg,
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        return None
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}."
        console_print_func(error_msg)
        debug_log(
            message=error_msg,
            file=f"{os.path.basename(__file__)}",
            version=current_version,
            function=current_function,
            console_print_func=console_print_func
        )
        return None


def disconnect_instrument(inst, console_print_func=None):
    """
    Closes the connection to a VISA instrument.
    """
    console_print_func = console_print_func if console_print_func else console_log
    current_function = inspect.currentframe().f_code.co_name
    debug_log(
        message="Disconnecting instrument... Saying goodbye!",
        file=f"{os.path.basename(__file__)}",
        version=current_version,
        function=current_function,
        console_print_func=console_print_func
    )
    if inst:
        try:
            inst.close()
            console_print_func("✅ Instrument disconnected. See ya!")
            debug_log(
                message="Instrument connection closed. All done!",
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            return True
        except pyvisa.errors.VisaIOError as e:
            error_msg = f"❌ VISA error disconnecting instrument: {e}."
            console_print_func(error_msg)
            debug_log(
                message=error_msg,
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            return False
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}."
            console_print_func(error_msg)
            debug_log(
                message=error_msg,
                file=f"{os.path.basename(__file__)}",
                version=current_version,
                function=current_function,
                console_print_func=console_print_func
            )
            return False
    debug_log(
        message="No instrument to disconnect. Already gone!",
        file=f"{os.path.basename(__file__)}",
        version=current_version,
        function=current_function,
        console_print_func=console_print_func
    )
    return False