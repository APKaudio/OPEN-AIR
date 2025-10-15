# managers/manager_instrument_settings_bandwidth.py
#
# A manager for bandwidth-related settings (RBW, VBW, Sweep Time), ensuring that
# the GUI state and device commands are synchronized.
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
# Version 20251014.231400.1
# FIXED: Renamed class from FrequencySettingsManager to BandwidthSettingsManager.
# FIXED: Implemented two-way synchronization logic for RBW, VBW, Sweep Time, and VBW Auto.

import os
import inspect
import json
import time 

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20251014.231400.1"
# Hash calculated based on YYYYMMDD * HHMMSS * Revision (20251014 * 231400 * 1)
current_version_hash = (20251014 * 231400 * 1)
current_file = f"{os.path.basename(__file__)}"


class BandwidthSettingsManager:
    """
    Manages the logic and synchronization of all bandwidth-related settings.
    """
    
    # --- CONSTANTS FOR YAK/SCPI COMMANDS (Protocol 4.1) ---
    HZ_TO_MHZ = 1_000_000.0
    YAK_BASE = "OPEN-AIR/repository/yak/Bandwidth"
    
    # YAK Triggers
    YAK_UPDATE_TOPIC = f"{YAK_BASE}/nab/NAB_bandwidth_settings/scpi_details/generic_model/trigger"
    YAK_RBW_TRIGGER = f"{YAK_BASE}/set/Set_RBW/scpi_details/generic_model/trigger"
    YAK_SWEEP_TIME_TRIGGER = f"{YAK_BASE}/set/Set_Sweep_time/scpi_details/generic_model/trigger"
    YAK_VBW_TRIGGER = f"{YAK_BASE}/set/Set_VBW/scpi_details/generic_model/trigger"
    YAK_VBW_AUTO_ON_TRIGGER = f"{YAK_BASE}/set/do_Video_Bandwidth_Auto_ON/scpi_details/generic_model/trigger"
    YAK_VBW_AUTO_OFF_TRIGGER = f"{YAK_BASE}/set/do_Video_Bandwidth_Auto_OFF/scpi_details/generic_model/trigger"

    # YAK Inputs
    YAK_RBW_INPUT = f"{YAK_BASE}/set/Set_RBW/scpi_inputs/hz_value/value"
    YAK_SWEEP_TIME_INPUT = f"{YAK_BASE}/set/Set_Sweep_time/scpi_inputs/s_value/value"
    YAK_VBW_INPUT = f"{YAK_BASE}/set/Set_VBW/scpi_inputs/hz_value/value"

    # YAK Outputs & GUI Topics (Used for Function 7 - UPDATE ALL)
    YAK_NAB_OUTPUTS = {
        "RBW_Hz/value": "Settings/fields/RBW/value",
        "VBW_Hz/value": "Settings/fields/vbw_MHz/value",
        "VBW_Auto_On/value": "Settings/fields/VBW_Automatic/options/ON/selected",
        "Sweep_Time_s/value": "Settings/fields/Sweep_time_s/value",
    }
    
    # --- END CONSTANTS ---


    def __init__(self, mqtt_controller: MqttControllerUtility):
        # Initializes the manager and subscribes to relevant topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/bandwidth"
        
        # Internal state variables to track current values (Optional for bandwidth, focusing on locks)
        self.rbw_value = None
        self.vbw_value = None
        self.sweep_time_value = None
        
        # Dictionary to store preset values dynamically
        self.rbw_preset_values = {}
        self.vbw_preset_values = {}
        
        # NEW: A dictionary to track the locked state of controls.
        self._locked_state = {
            f"{self.base_topic}/Settings/fields/RBW/value": False,
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value": False,
            f"{self.base_topic}/Settings/fields/vbw_MHz/value": False,
        }
        
        debug_log(
            message=f"🛠️🟢 Initializing BandwidthSettingsManager and setting up subscriptions.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._subscribe_to_topics()

    def _subscribe_to_topics(self):
        # Subscribes to all necessary bandwidth and preset topics.
        current_function_name = inspect.currentframe().f_code.co_name
        
        topic_list = [
            f"{self.base_topic}/Settings/fields/RBW/value",
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value",
            f"{self.base_topic}/Settings/fields/vbw_MHz/value",
            
            # Subscriptions for RBW Presets (Function 2)
            f"{self.base_topic}/Settings/fields/Resolutiin_Band_Width/options/+/selected",
            f"{self.base_topic}/Settings/fields/Resolutiin_Band_Width/options/+/value",
            
            # Subscriptions for VBW Presets (Function 5)
            f"{self.base_topic}/Settings/fields/Video_Band_Width_/options/+/selected",
            f"{self.base_topic}/Settings/fields/Video_Band_Width_/options/+/value",
            
            # Subscriptions for VBW Auto (Function 6)
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/ON/selected",
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/OFF/selected",
        ]
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self._on_message)
            debug_log(
                message=f"🔍 Subscribed to '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
        # ALSO SUBSCRIBE TO YAK REPOSITORY OUTPUTS (for the UPDATE ALL function)
        for yak_suffix in self.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self._on_message)
            debug_log(
                message=f"🔍 Subscribed to YAK output '{yak_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


    # --- YAK/SCPI Command Dispatch Helpers ---

    def _publish_rbw_and_trigger(self, value_hz):
        # Implements Function 1 logic: Send RBW to YAK and Trigger
        self._publish_to_yak_and_trigger(
            value=value_hz,
            input_topic=self.YAK_RBW_INPUT,
            trigger_topic=self.YAK_RBW_TRIGGER
        )
        
    def _publish_sweep_time_and_trigger(self, value_s):
        # Implements Function 3 logic: Send Sweep Time to YAK and Trigger
        self._publish_to_yak_and_trigger(
            value=value_s,
            input_topic=self.YAK_SWEEP_TIME_INPUT,
            trigger_topic=self.YAK_SWEEP_TIME_TRIGGER
        )

    def _publish_vbw_and_trigger(self, value_hz):
        # Implements Function 4 logic: Send VBW to YAK and Trigger
        self._publish_to_yak_and_trigger(
            value=value_hz,
            input_topic=self.YAK_VBW_INPUT,
            trigger_topic=self.YAK_VBW_TRIGGER
        )

    def _publish_vbw_auto_and_trigger(self, is_auto_on):
        # Implements Function 6 logic: Send VBW Auto ON/OFF command to YAK and Trigger
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            trigger_topic = self.YAK_VBW_AUTO_ON_TRIGGER if is_auto_on else self.YAK_VBW_AUTO_OFF_TRIGGER
            
            # 1. Trigger the SCPI command (True then False)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=True,
                retain=False
            )
            time.sleep(0.01)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=False,
                retain=False
            )
            
            debug_log(
                message=f"🐐✅ VBW Auto {'ON' if is_auto_on else 'OFF'} dispatched to {trigger_topic}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            # 2. Call the master update function to re-synchronize all 4 values.
            self._update_all_from_device()
            
        except Exception as e:
            console_log(f"❌ Error dispatching VBW Auto command: {e}")
            debug_log(
                message=f"🛠️🔴 VBW Auto dispatch failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_to_yak_and_trigger(self, value, input_topic, trigger_topic):
        # Helper that publishes the value to YAK input and executes the trigger sequence.
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # 1. Publish the raw value to the YAK input topic
            self.mqtt_controller.publish_message(
                topic=input_topic,
                subtopic="",
                value=value,
                retain=True
            )

            # 2. Trigger the SCPI command (True then False)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=True,
                retain=False
            )
            time.sleep(0.01)
            self.mqtt_controller.publish_message(
                topic=trigger_topic,
                subtopic="",
                value=False,
                retain=False
            )
            
            debug_log(
                message=f"🐐✅ YAK command dispatched. Sent '{value}' to {input_topic}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            # 3. Call the master update function to re-synchronize all 4 values.
            self._update_all_from_device()

        except Exception as e:
            console_log(f"❌ Error dispatching YAK command: {e}")
            debug_log(
                message=f"🛠️🔴 YAK dispatch failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            

    # --- Core Synchronization Logic (Function 7 - UPDATE ALL) ---

    def _update_all_from_device(self):
        # Implements the 'UPDATE ALL' logic by querying the device for all four values.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🐐🟢 Triggering NAB_bandwidth_settings to synchronize all 4 values.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # 1. Trigger the NAB command (True then False)
        self.mqtt_controller.publish_message(
            topic=self.YAK_UPDATE_TOPIC,
            subtopic="",
            value=True,
            retain=False
        )
        time.sleep(0.01)
        self.mqtt_controller.publish_message(
            topic=self.YAK_UPDATE_TOPIC,
            subtopic="",
            value=False,
            retain=False
        )
        
        console_log("✅ UPDATE ALL command sent to refresh bandwidth settings from device.")
    

    def _process_yak_output(self, topic, payload):
        # Processes the output from the NAB_bandwidth_settings query and updates the GUI.
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # 1. Determine which GUI topic corresponds to this YAK output topic
            yak_suffix = topic.split('/scpi_outputs/')[1]
            gui_suffix = self.YAK_NAB_OUTPUTS.get(yak_suffix)
            
            if not gui_suffix:
                debug_log(f"🟡 Unknown YAK output suffix: {yak_suffix}. Ignoring.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                return

            # 2. Extract and convert the value from the payload (which is Hz or a string from YAK)
            try:
                raw_value = json.loads(payload).get('value', payload)
            except (json.JSONDecodeError, TypeError):
                raw_value = payload
            
            # Set the lock before publishing back to GUI (to prevent feedback loop)
            full_gui_topic = f"{self.base_topic}/{gui_suffix}"
            self._locked_state[full_gui_topic] = True
            
            # 3. Handle Conversions and Special Logic
            if "RBW_Hz" in yak_suffix:
                # RBW_Hz (Hz) -> GUI RBW (Hz)
                final_value = float(raw_value)
                self.rbw_value = final_value
                self._publish_update(topic_suffix=gui_suffix, value=final_value)
            elif "VBW_Hz" in yak_suffix:
                # VBW_Hz (Hz) -> GUI VBW (MHz)
                final_value = float(raw_value) / self.HZ_TO_MHZ
                self.vbw_value = final_value
                self._publish_update(topic_suffix=gui_suffix, value=final_value)
            elif "Sweep_Time_s" in yak_suffix:
                # Sweep_Time_s (s) -> GUI Sweep Time (s)
                final_value = float(raw_value)
                self.sweep_time_value = final_value
                self._publish_update(topic_suffix=gui_suffix, value=final_value)
            elif "VBW_Auto_On" in yak_suffix:
                # VBW_Auto_On ('1' or '0') -> GUI VBW Automatic Toggle (ON/OFF)
                is_on = (str(raw_value).strip() == '1')
                
                # Set the 'ON' toggle state
                self._publish_update(topic_suffix="Settings/fields/VBW_Automatic/options/ON/selected", value=is_on)
                # Set the 'OFF' toggle state
                self._publish_update(topic_suffix="Settings/fields/VBW_Automatic/options/OFF/selected", value=not is_on)

            debug_log(
                message=f"🐐✅ YAK output processed. Synced {gui_suffix} with '{raw_value}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
        except Exception as e:
            console_log(f"❌ Error processing YAK output for {topic}: {e}")
            debug_log(
                message=f"🛠️🔴 NAB synchronization failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


    # --- Message Handler and Logic ---

    def _on_message(self, topic, payload):
        # The main message processing callback.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Handle incoming YAK repository updates first (for the UPDATE ALL function)
        if topic.startswith(f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs"):
            self._process_yak_output(topic, payload)
            return

        # NEW: Check the internal lock state before processing GUI topic changes.
        if self._locked_state.get(topic, False):
            debug_log(
                message=f"🟡 Message on locked topic '{topic}' received. Ignoring to prevent loop.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self._locked_state[topic] = False
            return
            
        debug_log(
            message=f"🛠️🔵 Received message on topic '{topic}' with payload '{payload}'. Executing logic.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            try:
                parsed_payload = json.loads(payload)
                value = parsed_payload.get('value', payload)
            except json.JSONDecodeError:
                value = payload
                
            # Handle Value changes from GUI (Functions 1, 3, 4)
            if topic.endswith("/RBW/value"):
                # Function 1 - Change RBW (Value is in Hz)
                new_val_hz = float(value)
                if self.rbw_value is None or abs(self.rbw_value - new_val_hz) > 0.1:
                    self.rbw_value = new_val_hz
                    self._publish_rbw_and_trigger(new_val_hz)
                    
            elif topic.endswith("/Sweep_time_s/value"):
                # Function 3 - Change Sweep Time (Value is in seconds)
                new_val_s = float(value)
                if self.sweep_time_value is None or abs(self.sweep_time_value - new_val_s) > 0.001:
                    self.sweep_time_value = new_val_s
                    self._publish_sweep_time_and_trigger(new_val_s)

            elif topic.endswith("/vbw_MHz/value"):
                # Function 4 - Change VBW (Value is in MHz -> convert to Hz for YAK)
                new_val_mhz = float(value)
                new_val_hz = new_val_mhz * self.HZ_TO_MHZ
                if self.vbw_value is None or abs(self.vbw_value - new_val_mhz) > 0.001:
                    self.vbw_value = new_val_mhz
                    self._publish_vbw_and_trigger(new_val_hz)
            
            # Handle Presets and Auto Toggles (Functions 2, 5, 6)
            
            elif "Resolutiin_Band_Width/options" in topic:
                # Function 2 - RBW Presets
                if topic.endswith("/value"):
                    option_number = int(topic.split('/')[-2])
                    self.rbw_preset_values[option_number] = float(value)
                elif topic.endswith("/selected") and str(value).lower() == 'true':
                    self._apply_preset(topic, self.rbw_preset_values, target_suffix="Settings/fields/RBW/value")

            elif "Video_Band_Width_/options" in topic:
                # Function 5 - VBW Presets
                if topic.endswith("/value"):
                    option_number = int(topic.split('/')[-2])
                    # Preset value is assumed to be in Hz, store it as Hz.
                    self.vbw_preset_values[option_number] = float(value) 
                elif topic.endswith("/selected") and str(value).lower() == 'true':
                    # Target is VBW/value (which is in MHz). We convert the Hz value.
                    self._apply_preset(topic, self.vbw_preset_values, target_suffix="Settings/fields/vbw_MHz/value", convert_to_mhz=True)
                    
            elif "VBW_Automatic/options" in topic and topic.endswith("/selected"):
                # Function 6 - VBW Automatic Toggle
                is_selected = str(value).lower() == 'true'
                if is_selected:
                    is_on = "ON" in topic
                    self._publish_vbw_auto_and_trigger(is_on)

            console_log("✅ Celebration of success! The bandwidth settings logic ran.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The logic has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    # --- Preset Helper ---
    
    def _apply_preset(self, topic, preset_map, target_suffix, convert_to_mhz=False):
        # Extracts the value from a selected preset and publishes it to the target topic.
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            option_number = int(topic.split('/')[-2])
            raw_value = preset_map.get(option_number)
            
            if raw_value is not None:
                new_value = raw_value / self.HZ_TO_MHZ if convert_to_mhz else raw_value
                
                # Set lock for the target topic before publishing
                full_target_topic = f"{self.base_topic}/{target_suffix}"
                self._locked_state[full_target_topic] = True
                
                self._publish_update(topic_suffix=target_suffix, value=new_value)
                
                debug_log(
                    message=f"🔁 Preset applied! Published value '{new_value}' to '{full_target_topic}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            else:
                debug_log(
                    message=f"🟡 Warning: Preset value for option {option_number} not found in map.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
        except Exception as e:
            debug_log(
                message=f"🛠️🔴 Failed to apply preset from topic '{topic}'. The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    # --- Publishing Helper ---

    def _publish_update(self, topic_suffix, value):
        # Publishes a message to the specified topic.
        current_function_name = inspect.currentframe().f_code.co_name
        
        full_topic = f"{self.base_topic}/{topic_suffix}"
        
        rounded_value = round(float(value), 3)
        
        debug_log(
            message=f"💾 Publishing new value '{rounded_value}' to topic '{full_topic}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self.mqtt_controller.publish_message(
            topic=full_topic,
            subtopic="",
            value=rounded_value,
            retain=False
        )