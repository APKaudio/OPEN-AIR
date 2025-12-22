# managers/manager_visa_reset.py
#
# A dedicated manager to handle device reset and reboot commands received via MQTT.
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
# Version 20250907.002515.4
# FIXED: Updated subscriptions and callbacks to listen for the new '/trigger' subtopic,
# aligning with the updated actuator logic.

import os
import inspect
import json

# --- Utility and Worker Imports ---
from workers.logger.logger import debug_log, console_log, log_visa_command
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from .manager_visa_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20250907.002515.4"
current_version_hash = (20250907 * 2515 * 4)
current_file = f"{os.path.basename(__file__)}"


class VisaResetManager:
    """
    Listens for MQTT commands to reset or reboot the instrument and dispatches them.
    """
    def __init__(self, mqtt_controller: MqttControllerUtility, scpi_dispatcher: ScpiDispatcher):
        # Initializes the manager, linking it to the MQTT controller and SCPI dispatcher.
        current_function_name = inspect.currentframe().f_code.co_name
        self.current_class_name = self.__class__.__name__

        debug_log(
            message=f"🛠️🟢 Initiating the {self.current_class_name}. The enforcer of resets is online!",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            self.mqtt_controller = mqtt_controller
            self.scpi_dispatcher = scpi_dispatcher
            
            # --- SCPI Command Constants (No Magic Numbers) ---
            self.CMD_RESET_DEVICE = "*RST"
            self.CMD_REBOOT_DEVICE = ":SYSTem:POWer:RESet" # Per user instruction for power cycle

            # --- MQTT Topic Constants ---
            self.BASE_TOPIC = "OPEN-AIR/configuration/instrument/active/Instrument_Connection/System_Reset/fields"
            self.TOPIC_RESET = f"{self.BASE_TOPIC}/Reset_device/trigger"
            self.TOPIC_REBOOT = f"{self.BASE_TOPIC}/Reboot_device/trigger"

            self._setup_mqtt_subscriptions()
            console_log(f"✅ {self.current_class_name} initialized and listening.")

        except Exception as e:
            console_log(f"❌ Error in {self.current_class_name}.{current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Catastrophic failure during {self.current_class_name} initialization! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _setup_mqtt_subscriptions(self):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} to subscribe to reset/reboot topics.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # FIXED: Subscribing to the new '/trigger' subtopic
            self.mqtt_controller.add_subscriber(topic_filter=self.TOPIC_RESET, callback_func=self._on_reset_request)
            self.mqtt_controller.add_subscriber(topic_filter=self.TOPIC_REBOOT, callback_func=self._on_reboot_request)
            console_log("✅ Celebration of success! The reset manager did subscribe to its topics.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 The subscription circuits are fried! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_reset_request(self, topic, payload):
        # Handles a request to perform a soft reset (*RST) on the instrument.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} due to message on topic: {topic}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # FIXED: Check if the payload value is explicitly 'true'
            data = json.loads(payload)
            if str(data.get("value")).lower() == 'true':
                console_log(f"🔵 Command received: Soft Reset. Dispatching '{self.CMD_RESET_DEVICE}'.")
                self.scpi_dispatcher.write_safe(command=self.CMD_RESET_DEVICE)
                
        except (json.JSONDecodeError, AttributeError) as e:
            console_log(f"❌ Error processing reset request payload: {payload}. Error: {e}")
            debug_log(
                message=f"🛠️🔴 A garbled message! The reset contraption is confused! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _on_reboot_request(self, topic, payload):
        # Handles a request to perform a power cycle on the instrument.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} due to message on topic: {topic}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            # FIXED: Check if the payload value is explicitly 'true'
            data = json.loads(payload)
            if str(data.get("value")).lower() == 'true':
                console_log(f"🔵 Command received: Power Cycle. Dispatching '{self.CMD_REBOOT_DEVICE}'.")
                self.scpi_dispatcher.write_safe(command=self.CMD_REBOOT_DEVICE)

        except (json.JSONDecodeError, AttributeError) as e:
            console_log(f"❌ Error processing reboot request payload: {payload}. Error: {e}")
            debug_log(
                message=f"🛠️🔴 The reboot sequence has short-circuited! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )