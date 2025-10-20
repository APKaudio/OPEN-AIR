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
# Source Code: https://https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20251019.224155.13
# FIXED: Re-implemented the state locking mechanism (_locked_state) specifically 
#        to prevent infinite feedback loops. The lock is set when the manager 
#        receives a NAB/QUERY response and publishes to a GUI topic, and it is 
#        unlocked upon receiving the echo in _on_message. This isolates the NAB 
#        update from triggering SET commands.

import os
import inspect
import json
import time 
import threading 
import pathlib # Retained pathlib import as it is part of the final version.

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20251019.224155.13"
# Hash calculated based on YYYYMMDD * HHMMSS * Revision (20251019 * 224155 * 13)
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
current_version_hash = (20251019 * 224155 * 13)
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
    # Logically correct mapping (assuming YAK Manager is fixed)
    YAK_NAB_OUTPUTS = {
        "RBW_Hz/value": "Settings/fields/RBW/value",
        "VBW_Hz/value": "Settings/fields/vbw_MHz/value",
        "VBW_Auto_On/value": "Settings/fields/VBW_Automatic/options/ON/selected",
        "Continuous_Mode_On/value": "Settings/fields/Sweep_Mode/options/Continuous/selected", 
        "Sweep_Time_s/value": "Settings/fields/Sweep_time_s/value",
    }
    TOPIC_RBW_PRESET_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Resolutiin_Band_Width/options/+/value"
    TOPIC_VBW_PRESET_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Video_Band_Width_/options/+/value"
    
    # CONSTANTS for subscribing to units topics.
    TOPIC_RBW_UNITS_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Resolutiin_Band_Width/options/+/units"
    TOPIC_VBW_UNITS_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Video_Band_Width_/options/+/units"

    # Unit Multiplier Map (for converting preset values to base Hz/s)
    UNIT_MULTIPLIERS = {
        "HZ": 1,
        "KHZ": 1000,
        "MHZ": 1000000,
        "GHZ": 1000000000,
        "S": 1,
        "MS": 0.001,
        "US": 0.000001
    }

    # --- END CONSTANTS ---


    def __init__(self, mqtt_controller: MqttControllerUtility):
        # NOTE: Using placeholder for current_function_name as inspect.currentframe() 
        current_function_name = "BandwidthSettingsManager.__init__"
        
        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/bandwidth"
        
        # Tracked in MHz for consistency with GUI
        self.rbw_value = None 
        self.vbw_value = None 
        self.sweep_time_value = None
        
        # Stored in raw value (as per JSON config format)
        self.rbw_preset_values = {} 
        self.vbw_preset_values = {} 
        
        # Stored in raw unit string (e.g., "kHz")
        self.rbw_preset_units = {}
        self.vbw_preset_units = {}
        
        # --- RE-IMPLEMENTED LOCKING MECHANISM for loop prevention ---
        self._locked_state = {
            f"{self.base_topic}/Settings/fields/RBW/value": False,
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value": False,
            f"{self.base_topic}/Settings/fields/vbw_MHz/value": False,
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/ON/selected": False,
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/OFF/selected": False,
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected": False,
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected": False, 
        }
        
        debug_log(
            message=f"🛠️🟢 Initializing BandwidthSettingsManager. Args: mqtt_controller={id(mqtt_controller)}. Internal maps initialized.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._subscribe_to_topics()
        
        # FIXED: Explicitly request initial config state to populate preset maps.
        debug_log(
            message=f"🛠️🔵 Forcing initial NAB update to populate preset maps (RBW/VBW config values).",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        self._update_all_from_device()
        
        debug_log(
            message=f"🛠️🟢 Initialization complete. Current internal values: RBW={self.rbw_value}, VBW={self.vbw_value}, SweepTime={self.sweep_time_value}. Locked state keys: {list(self._locked_state.keys())}",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )


    def _subscribe_to_topics(self):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._subscribe_to_topics"
        
        topic_list = [
            f"{self.base_topic}/Settings/fields/RBW/value",
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value",
            f"{self.base_topic}/Settings/fields/vbw_MHz/value",
            
            f"{self.base_topic}/Settings/fields/Resolutiin_Band_Width/options/+/selected",
            BandwidthSettingsManager.TOPIC_RBW_PRESET_WILDCARD, 
            BandwidthSettingsManager.TOPIC_RBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/Video_Band_Width_/options/+/selected",
            BandwidthSettingsManager.TOPIC_VBW_PRESET_WILDCARD, 
            BandwidthSettingsManager.TOPIC_VBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/ON/selected",
            f"{self.base_topic}/Settings/fields/VBW_Automatic/options/OFF/selected",
            
            # Subscribe to the Continuous Mode topics
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected", 
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected", 
        ]
        
        debug_log(
            message=f"🔍🟢 Starting subscription process for {len(topic_list) + len(self.YAK_NAB_OUTPUTS)} topics.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self._on_message)
            debug_log(
                message=f"🔍 Subscribed GUI/Config topic: '{topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
        for yak_suffix in BandwidthSettingsManager.YAK_NAB_OUTPUTS.keys():
            # YAK_NAB_OUTPUTS keys now include the suffix, e.g., "RBW_Hz/value"
            yak_topic = f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self._on_message)
            debug_log(
                message=f"🔍 Subscribed YAK output topic: '{yak_topic}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _publish_rbw_and_trigger(self, value_mhz):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._publish_rbw_and_trigger"
        # Publish value is the integer Hz equivalent
        value_hz = int(round(value_mhz * self.HZ_TO_MHZ))
        
        debug_log(
            message=f"🐐🔵 Converting RBW MHz={value_mhz} to Hz={value_hz}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._publish_to_yak_and_trigger(
            value=value_hz, 
            input_topic=self.YAK_RBW_INPUT,
            trigger_topic=self.YAK_RBW_TRIGGER
        )
        
    def _publish_sweep_time_and_trigger(self, value_s):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._publish_sweep_time_and_trigger"
        
        debug_log(
            message=f"🐐🔵 Publishing raw Sweep Time (s): {value_s}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._publish_to_yak_and_trigger(
            value=float(value_s),
            input_topic=self.YAK_SWEEP_TIME_INPUT,
            trigger_topic=self.YAK_SWEEP_TIME_TRIGGER
        )

    def _publish_vbw_and_trigger(self, value_mhz):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._publish_vbw_and_trigger"
        # Publish value is the integer Hz equivalent
        value_hz = int(round(value_mhz * self.HZ_TO_MHZ))
        
        debug_log(
            message=f"🐐🔵 Converting VBW MHz={value_mhz} to Hz={value_hz}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._publish_to_yak_and_trigger(
            value=value_hz, 
            input_topic=self.YAK_VBW_INPUT,
            trigger_topic=self.YAK_VBW_TRIGGER
        )

    def _publish_vbw_auto_and_trigger(self, is_auto_on):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._publish_vbw_auto_and_trigger"
        
        debug_log(f"🐐🟢 Entering {current_function_name} with is_auto_on={is_auto_on}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        
        try:
            trigger_topic = self.YAK_VBW_AUTO_ON_TRIGGER if is_auto_on else self.YAK_VBW_AUTO_OFF_TRIGGER
            
            debug_log(
                message=f"🐐🔵 Publishing True to trigger topic: {trigger_topic}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=True, retain=False)
            time.sleep(0.01)
            self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=False, retain=False)
            
            debug_log(
                message=f"🐐✅ VBW Auto {'ON' if is_auto_on else 'OFF'} dispatched to {trigger_topic}. Calling update.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
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
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._publish_to_yak_and_trigger"
        
        debug_log(f"🐐🟢 Entering {current_function_name}. Value='{value}', Input='{input_topic}', Trigger='{trigger_topic}'", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

        try:
            debug_log(
                message=f"🐐🔵 Publishing retained value '{value}' to input topic: {input_topic}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self.mqtt_controller.publish_message(
                topic=input_topic,
                subtopic="",
                value=value,
                retain=True
            )

            debug_log(
                message=f"🐐🔵 Publishing True/False sequence to trigger topic: {trigger_topic}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=True, retain=False)
            time.sleep(0.01)
            self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=False, retain=False)
            
            debug_log(
                message=f"🐐✅ YAK command sequence complete. Calling update.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            self._update_all_from_device()

        except Exception as e:
            console_log(f"❌ Error dispatching YAK command: {e}")
            debug_log(
                message=f"🛠️🔴 YAK dispatch failed! Input='{input_topic}'. The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _update_all_from_device(self):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._update_all_from_device"
        debug_log(
            message=f"🐐🟢 Entering {current_function_name}. Triggering NAB_bandwidth_settings to synchronize all 5 values.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self.mqtt_controller.publish_message(topic=self.YAK_UPDATE_TOPIC, subtopic="", value=True, retain=False)
        time.sleep(0.01)
        self.mqtt_controller.publish_message(topic=self.YAK_UPDATE_TOPIC, subtopic="", value=False, retain=False)
        
        console_log("✅ UPDATE ALL command sent to refresh bandwidth settings from device.")
    
    def _get_multiplier(self, unit_string: str) -> float:
        # Gets the numeric multiplier for a given unit string (e.g., "kHz" -> 1000)
        current_function_name = "BandwidthSettingsManager._get_multiplier"
        
        debug_log(f"🔍🟢 Entering {current_function_name} with unit_string='{unit_string}'", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        
        try:
            # Clean and uppercase the unit string for lookup
            clean_unit = unit_string.strip().upper()
            multiplier = self.UNIT_MULTIPLIERS.get(clean_unit, 1.0)
            
            debug_log(
                message=f"🔍🔵 Looked up clean unit '{clean_unit}'. Multiplier found: {multiplier}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            if multiplier == 1.0 and clean_unit not in self.UNIT_MULTIPLIERS:
                debug_log(
                    message=f"🟡 Unknown unit string '{unit_string}'. Defaulting multiplier to 1.0 (assuming Hz/s).",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            
            return multiplier

        except Exception as e:
            debug_log(
                message=f"🛠️🔴 Failed to calculate unit multiplier for '{unit_string}'. The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return 1.0 # Default to 1.0 on error


    def _process_yak_output(self, topic, payload):
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._process_yak_output"
        
        debug_log(f"🐐🟢 Entering {current_function_name}. Topic='{topic}', Raw Payload='{payload}'", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        
        try:
            # Note: yak_suffix now includes '/value' e.g. "RBW_Hz/value"
            yak_suffix = topic.split('/scpi_outputs/')[1]
            gui_suffix = self.YAK_NAB_OUTPUTS.get(yak_suffix)
            
            if not gui_suffix:
                debug_log(f"🟡 Unknown YAK output suffix: {yak_suffix}. Ignoring.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                return

            try:
                # Payload extraction is always tricky, log both states.
                raw_value_json = json.loads(payload)
                raw_value = raw_value_json.get('value', payload)
                debug_log(f"🔍🔵 Parsed payload. raw_value='{raw_value}'.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except (json.JSONDecodeError, TypeError):
                raw_value = payload
                debug_log(f"🔍🔵 Failed JSON parse. Using raw payload. raw_value='{raw_value}'.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            
            full_gui_topic = f"{self.base_topic}/{gui_suffix}"
            
            # --- START LOCKING THE GUI TOPIC BEFORE PUBLICATION ---
            if full_gui_topic in self._locked_state:
                debug_log(f"🔒🔵 Setting lock state for NAB echo topic: {full_gui_topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._locked_state[full_gui_topic] = True
            # --- END LOCKING ---
            
            # 3. Handle Conversions and Special Logic
            if "RBW_Hz" in yak_suffix:
                final_value_hz = float(raw_value)
                final_value_mhz = final_value_hz / self.HZ_TO_MHZ
                self.rbw_value = final_value_mhz 
                debug_log(f"🔍🔵 RBW conversion: {final_value_hz} Hz -> {final_value_mhz} MHz. Publishing update.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._publish_update(topic_suffix=gui_suffix, value=final_value_mhz)
                
            elif "VBW_Hz" in yak_suffix:
                final_value_hz = float(raw_value)
                final_value_mhz = final_value_hz / self.HZ_TO_MHZ
                self.vbw_value = final_value_mhz
                debug_log(f"🔍🔵 VBW conversion: {final_value_hz} Hz -> {final_value_mhz} MHz. Publishing update.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._publish_update(topic_suffix=gui_suffix, value=final_value_mhz)
                
            elif "VBW_Auto_On" in yak_suffix:
                is_on = (str(raw_value).strip() == '1')
                debug_log(f"🔍🔵 VBW Auto: Raw='{raw_value}', is_on={is_on}. Publishing updates.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._publish_update(topic_suffix="Settings/fields/VBW_Automatic/options/ON/selected", value=is_on)
                self._publish_update(topic_suffix="Settings/fields/VBW_Automatic/options/OFF/selected", value=not is_on)
                
            # LOGICAL MAPPING: Continuous Mode (Receives boolean)
            elif "Continuous_Mode_On" in yak_suffix:
                is_on = (str(raw_value).strip() == '1')
                debug_log(f"🔍🔵 Continuous Mode: Raw='{raw_value}', is_on={is_on}. Publishing updates for Continuous/Single.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                
                # Update Continuous Mode toggle
                self._publish_update(topic_suffix="Settings/fields/Sweep_Mode/options/Continuous/selected", value=is_on)
                
                # Update Single Mode toggle (assumed opposite)
                self._publish_update(topic_suffix="Settings/fields/Sweep_Mode/options/Single/selected", value=not is_on)


            # LOGICAL MAPPING: Sweep Time (Receives float)
            elif "Sweep_Time_s" in yak_suffix:
                final_value = float(raw_value)
                self.sweep_time_value = final_value
                debug_log(f"🔍🔵 Sweep Time: {final_value} s. Publishing update.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._publish_update(topic_suffix=gui_suffix, value=final_value)


            debug_log(
                message=f"🐐✅ YAK output processed. Synced {gui_suffix} with '{raw_value}'. Exiting function.",
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
        # NOTE: Using placeholder for current_function_name
        current_function_name = "BandwidthSettingsManager._on_message"
        
        debug_log(f"🛠️🟢 Entering {current_function_name}. Topic='{topic}', Raw Payload='{payload}'", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        
        if topic.startswith(f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs"):
            self._process_yak_output(topic, payload)
            return
        
        try:
            try:
                parsed_payload = json.loads(payload)
                value = parsed_payload.get('value', payload)
                debug_log(f"🔍🔵 Payload parsed successfully. Value='{value}'.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except json.JSONDecodeError:
                value = payload
                debug_log(f"🔍🔵 Payload is not JSON. Using raw payload. Value='{value}'.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        except Exception:
            value = payload
            debug_log(f"🔍🔵 General payload parsing error. Using raw payload. Value='{value}'.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

        # Helper to extract option number
        def _get_option_number(t):
            parts = t.split('/')
            try:
                return int(parts[-2])
            except (ValueError, IndexError):
                return None

        # --- START LOCK CHECK ---
        if self._locked_state.get(topic, False):
            debug_log(
                message=f"🟡 Message on locked topic '{topic}' received. Value='{value}'. IGNORING to prevent loop. UNLOCKING topic.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            # UNLOCK THE TOPIC IMMEDIATELY AFTER RECEIVING THE ECHO
            self._locked_state[topic] = False
            return
        # --- END LOCK CHECK ---


        # --- LOGIC FOR POPULATING RBW PRESET MAPS (Value Topics) ---
        if topic.startswith(f"{self.base_topic}/Settings/fields/Resolutiin_Band_Width/options/") and topic.endswith("/value"):
            try:
                option_number = _get_option_number(topic)
                if option_number is not None:
                    value_float = float(str(value))
                    # Store the value 
                    self.rbw_preset_values[option_number] = value_float 
                    debug_log(f"💾 Stored RBW preset RAW value: Option {option_number} is {value_float}. Map size: {len(self.rbw_preset_values)}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except Exception as e:
                debug_log(f"🟡 Error processing RBW preset value: {e}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            return
        
        # --- LOGIC FOR POPULATING VBW PRESET MAPS (Value Topics) ---
        if topic.startswith(f"{self.base_topic}/Settings/fields/Video_Band_Width_/options/") and topic.endswith("/value"):
            try:
                option_number = _get_option_number(topic)
                if option_number is not None:
                    value_float = float(str(value))
                    # Store the value 
                    self.vbw_preset_values[option_number] = value_float 
                    debug_log(f"💾 Stored VBW preset RAW value: Option {option_number} is {value_float}. Map size: {len(self.vbw_preset_values)}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except Exception as e:
                debug_log(f"🟡 Error processing VBW preset value: {e}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            return
        
        # --- LOGIC FOR POPULATING RBW PRESET MAPS (Unit Topics) ---
        if topic.startswith(f"{self.base_topic}/Settings/fields/Resolutiin_Band_Width/options/") and topic.endswith("/units"):
            try:
                option_number = _get_option_number(topic)
                if option_number is not None:
                    unit_str = str(value)
                    self.rbw_preset_units[option_number] = unit_str 
                    debug_log(f"💾 Stored RBW preset unit: Option {option_number} is '{unit_str}'. Map size: {len(self.rbw_preset_units)}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except Exception as e:
                debug_log(f"🟡 Error processing RBW preset unit: {e}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            return
            
        # --- LOGIC FOR POPULATING VBW PRESET MAPS (Unit Topics) ---
        if topic.startswith(f"{self.base_topic}/Settings/fields/Video_Band_Width_/options/") and topic.endswith("/units"):
            try:
                option_number = _get_option_number(topic)
                if option_number is not None:
                    unit_str = str(value)
                    self.vbw_preset_units[option_number] = unit_str 
                    debug_log(f"💾 Stored VBW preset unit: Option {option_number} is '{unit_str}'. Map size: {len(self.vbw_preset_units)}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            except Exception as e:
                debug_log(f"🟡 Error processing VBW preset unit: {e}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            return
            
        
        try:
            # Attempt conversion outside of specific blocks
            new_val_float = float(value) if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()) else None
            debug_log(f"🔍🔵 Value conversion check: new_val_float={new_val_float}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)


            if topic.endswith("/RBW/value"):
                if new_val_float is not None:
                    debug_log(f"🔍🔵 Current RBW value: {self.rbw_value}. New value: {new_val_float}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                    
                    if self.rbw_value is None or abs(self.rbw_value - new_val_float) > 0.1:
                        self.rbw_value = new_val_float
                        self._publish_rbw_and_trigger(value_mhz=new_val_float) 
                    else:
                        debug_log("🟡 RBW change below threshold (0.1 MHz). Ignoring.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

                
            elif topic.endswith("/Sweep_time_s/value"):
                if new_val_float is not None:
                    debug_log(f"🔍🔵 Current Sweep Time value: {self.sweep_time_value}. New value: {new_val_float}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                    
                    if self.sweep_time_value is None or abs(self.sweep_time_value - new_val_float) > 0.001: 
                        self.sweep_time_value = new_val_float
                        self._publish_sweep_time_and_trigger(value_s=new_val_float)
                    else:
                        debug_log("🟡 Sweep Time change below threshold (0.001 s). Ignoring.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)


            elif topic.endswith("/vbw_MHz/value"):
                if new_val_float is not None:
                    new_val_mhz = new_val_float
                    debug_log(f"🔍🔵 Current VBW value: {self.vbw_value}. New value: {new_val_mhz}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                    if self.vbw_value is None or abs(self.vbw_value - new_val_mhz) > 0.001:
                        self.vbw_value = new_val_mhz
                        self._publish_vbw_and_trigger(value_mhz=new_val_mhz) 
                    else:
                        debug_log("🟡 VBW change below threshold (0.001 MHz). Ignoring.", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

            
            elif "Resolutiin_Band_Width/options" in topic and topic.endswith("/selected") and str(value).lower() == 'true':
                debug_log(f"🔍🔵 Preset Button Pressed (RBW). Topic: {topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._apply_preset(
                    topic=topic, 
                    preset_value_map=self.rbw_preset_values, 
                    preset_unit_map=self.rbw_preset_units,
                    target_suffix="Settings/fields/RBW/value", 
                    is_rbw=True
                )

            elif "Video_Band_Width_/options" in topic and topic.endswith("/selected") and str(value).lower() == 'true':
                debug_log(f"🔍🔵 Preset Button Pressed (VBW). Topic: {topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                self._apply_preset(
                    topic=topic, 
                    preset_value_map=self.vbw_preset_values,
                    preset_unit_map=self.vbw_preset_units,
                    target_suffix="Settings/fields/vbw_MHz/value", 
                    is_rbw=False
                )
                    
            elif "VBW_Automatic/options" in topic and topic.endswith("/selected"):
                is_selected = str(value).lower() == 'true'
                debug_log(f"🔍🔵 VBW Auto toggle detected. is_selected={is_selected}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                if is_selected:
                    is_on = "ON" in topic
                    self._publish_vbw_auto_and_trigger(is_auto_on=is_on)
                    
            elif "Sweep_Mode/options/Continuous/selected" in topic:
                is_selected = str(value).lower() == 'true'
                debug_log(f"🔍🔵 Sweep Mode Continuous toggle detected. is_selected={is_selected}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                # No YAK command is triggered from here; this is likely just for locking the sweep time value if going into Continuous mode

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
    
    def _apply_preset(self, topic, preset_value_map, preset_unit_map, target_suffix, is_rbw: bool):
        # Applies a preset value to both the GUI (in MHz) and the device (in Hz).
        current_function_name = "BandwidthSettingsManager._apply_preset"
        
        debug_log(f"🔁🟢 Entering {current_function_name}. Topic='{topic}', is_rbw={is_rbw}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
        
        try:
            # 1. Get the option number, raw value, and unit string
            option_number = int(topic.split('/')[-2])
            raw_value = preset_value_map.get(option_number)
            unit_string = preset_unit_map.get(option_number)
            
            debug_log(f"🔍🔵 Preset lookup for option {option_number}: Raw Value='{raw_value}', Unit='{unit_string}'", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
            
            if raw_value is not None and unit_string is not None:
                # 2. Convert raw value + unit to final Hz value for YAK
                multiplier = self._get_multiplier(unit_string=unit_string)
                final_value_hz = raw_value * multiplier
                
                # 3. Convert final Hz value to MHz for GUI Topic publication
                new_value_mhz = final_value_hz / self.HZ_TO_MHZ
                
                debug_log(f"🔍🔵 Conversion complete: Multiplier={multiplier}, final_value_hz={final_value_hz}, new_value_mhz={new_value_mhz}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

                full_target_topic = f"{self.base_topic}/{target_suffix}"
                
                # --- START LOCKING THE GUI TOPIC BEFORE PUBLICATION ---
                if full_target_topic in self._locked_state:
                    debug_log(f"🔒🔵 Setting lock state for NAB echo topic: {full_target_topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                    self._locked_state[full_target_topic] = True
                # --- END LOCKING ---
                
                # 4. Publish to GUI Topic (in MHz)
                self._publish_update(topic_suffix=target_suffix, value=new_value_mhz)
                
                # 4.5 Explicitly set the source button to True for visual feedback
                self.mqtt_controller.publish_message(
                    topic=topic,  # The button's /selected topic
                    subtopic="",
                    value=True,
                    retain=False
                )
                debug_log(f"💾 Published True state to button topic: {topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)
                
                # 5. Publish to YAK Topic (in Hz) and trigger
                yak_input = self.YAK_RBW_INPUT if is_rbw else self.YAK_VBW_INPUT
                yak_trigger = self.YAK_RBW_TRIGGER if is_rbw else self.YAK_VBW_TRIGGER

                self._publish_to_yak_and_trigger(
                    value=final_value_hz, 
                    input_topic=yak_input, 
                    trigger_topic=yak_trigger
                )

                debug_log(
                    message=f"🔁✅ Preset applied! Exiting function.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            else:
                # --- REFRESH AND UN-SELECT LOGIC (Failure Path) ---
                error_message = f"Preset data missing for option {option_number}. RAW value: {raw_value}, Unit: {unit_string}. Current Value Map Keys: {list(preset_value_map.keys())}. Current Unit Map Keys: {list(preset_unit_map.keys())}"
                console_log(f"❌ Error: {error_message} Attempting to refresh configuration and un-select button...")
                
                debug_log(
                    message=f"🛠️🔴 Preset lookup failed! Missing config data. Un-selecting button. The error be: {error_message}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                
                # 1. Un-select the button that was just pressed to clear the stuck state
                self.mqtt_controller.publish_message(
                    topic=topic,  # The button's /selected topic
                    subtopic="",
                    value=False,
                    retain=False
                )
                debug_log(f"💾 Published False state to button topic: {topic}", file=current_file, version=current_version, function=f"{self.__class__.__name__}.{current_function_name}", console_print_func=console_log)

                
                # 2. Trigger a full update to prompt the MQTT broker to resend retained config messages.
                self._update_all_from_device()

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
        current_function_name = "BandwidthSettingsManager._publish_update"
        
        full_topic = f"{self.base_topic}/{topic_suffix}"
        
        # Rounding for GUI display consistency
        rounded_value = round(float(value), 6) 
        
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