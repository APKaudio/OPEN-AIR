# managers/manager_instrument_settings_bandwidth.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251207.204500.14
# FIXED: Updated all topic paths to reflect the new nested structure in the bandwidth JSON configuration.

import os
import inspect
import json
import time 
import threading 
import pathlib

# Assume these are imported from a central logging utility and MQTT controller
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility

# --- Global Scope Variables ---
current_version = "20251207.204500.14"
current_version_hash = (20251207 * 204500 * 14)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = False


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
        "RBW_Hz/value": "Settings/fields/Resolution Bandwidth/fields/RBW/value",
        "VBW_Hz/value": "Settings/fields/Video Bandwidth/fields/vbw_MHz/value",
        "VBW_Auto_On/value": "Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected",
        "Continuous_Mode_On/value": "Settings/fields/Sweep_Mode/options/Continuous/selected", 
        "Sweep_Time_s/value": "Settings/fields/Sweep_time_s/value",
    }
    
    TOPIC_RBW_PRESET_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Resolution Bandwidth/fields/Resolution Band Width/options/+/value"
    TOPIC_VBW_PRESET_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Video Bandwidth/fields/Video Band Width /options/+/value"
    
    # CONSTANTS for subscribing to units topics.
    TOPIC_RBW_UNITS_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Resolution Bandwidth/fields/Resolution Band Width/options/+/units"
    TOPIC_VBW_UNITS_WILDCARD = "OPEN-AIR/configuration/instrument/bandwidth/Settings/fields/Video Bandwidth/fields/Video Band Width /options/+/units"

    UNIT_MULTIPLIERS = {
        "HZ": 1, "KHZ": 1000, "MHZ": 1000000, "GHZ": 1000000000,
        "S": 1, "MS": 0.001, "US": 0.000001
    }

    # --- END CONSTANTS ---

    def __init__(self, mqtt_controller: MqttControllerUtility):
        current_function_name = "BandwidthSettingsManager.__init__"
        
        self.mqtt_controller = mqtt_controller
        self.base_topic = "OPEN-AIR/configuration/instrument/bandwidth"
        
        self.rbw_value = None 
        self.vbw_value = None 
        self.sweep_time_value = None
        
        self.rbw_preset_values = {} 
        self.vbw_preset_values = {} 
        
        self.rbw_preset_units = {}
        self.vbw_preset_units = {}
        
        # Locking mechanism to prevent feedback loops
        self._locked_state = {
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/RBW/value": False,
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/vbw_MHz/value": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/OFF/selected": False,
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected": False, 
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected": False, 
        }
        
        self._subscribe_to_topics()
        self._update_all_from_device()

    def _subscribe_to_topics(self):
        current_function_name = "BandwidthSettingsManager._subscribe_to_topics"
        
        topic_list = [
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/RBW/value",
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value",
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/vbw_MHz/value",
            
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/Resolution Band Width/options/+/selected",
            self.TOPIC_RBW_PRESET_WILDCARD, 
            self.TOPIC_RBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/Video Band Width /options/+/selected",
            self.TOPIC_VBW_PRESET_WILDCARD, 
            self.TOPIC_VBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected",
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/OFF/selected",
            
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected", 
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected", 
        ]
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self._on_message)
            
        for yak_suffix in self.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self._on_message)

    def _publish_rbw_and_trigger(self, value_mhz):
        value_hz = int(round(value_mhz * self.HZ_TO_MHZ))
        self._publish_to_yak_and_trigger(
            value=value_hz, 
            input_topic=self.YAK_RBW_INPUT,
            trigger_topic=self.YAK_RBW_TRIGGER
        )
        
    def _publish_sweep_time_and_trigger(self, value_s):
        self._publish_to_yak_and_trigger(
            value=float(value_s),
            input_topic=self.YAK_SWEEP_TIME_INPUT,
            trigger_topic=self.YAK_SWEEP_TIME_TRIGGER
        )

    def _publish_vbw_and_trigger(self, value_mhz):
        value_hz = int(round(value_mhz * self.HZ_TO_MHZ))
        self._publish_to_yak_and_trigger(
            value=value_hz, 
            input_topic=self.YAK_VBW_INPUT,
            trigger_topic=self.YAK_VBW_TRIGGER
        )

    def _publish_vbw_auto_and_trigger(self, is_auto_on):
        trigger_topic = self.YAK_VBW_AUTO_ON_TRIGGER if is_auto_on else self.YAK_VBW_AUTO_OFF_TRIGGER
        self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=True, retain=False)
        time.sleep(0.01)
        self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=False, retain=False)
        self._update_all_from_device()

    def _publish_to_yak_and_trigger(self, value, input_topic, trigger_topic):
        self.mqtt_controller.publish_message(topic=input_topic, subtopic="", value=value, retain=True)
        self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=True, retain=False)
        time.sleep(0.01)
        self.mqtt_controller.publish_message(topic=trigger_topic, subtopic="", value=False, retain=False)
        self._update_all_from_device()
            
    def _update_all_from_device(self):
        self.mqtt_controller.publish_message(topic=self.YAK_UPDATE_TOPIC, subtopic="", value=True, retain=False)
        time.sleep(0.01)
        self.mqtt_controller.publish_message(topic=self.YAK_UPDATE_TOPIC, subtopic="", value=False, retain=False)
        console_log("✅ UPDATE ALL command sent to refresh bandwidth settings from device.")
    
    def _get_multiplier(self, unit_string: str) -> float:
        clean_unit = unit_string.strip().upper()
        return self.UNIT_MULTIPLIERS.get(clean_unit, 1.0)

    def _process_yak_output(self, topic, payload):
        try:
            yak_suffix = topic.split('/scpi_outputs/')[1]
            gui_suffix = self.YAK_NAB_OUTPUTS.get(yak_suffix)
            if not gui_suffix: return

            try:
                raw_value = json.loads(payload).get('value', payload)
            except (json.JSONDecodeError, TypeError):
                raw_value = payload
            
            full_gui_topic = f"{self.base_topic}/{gui_suffix}"
            if full_gui_topic in self._locked_state:
                self._locked_state[full_gui_topic] = True
            
            if "RBW_Hz" in yak_suffix:
                final_value_mhz = float(raw_value) / self.HZ_TO_MHZ
                self.rbw_value = final_value_mhz 
                self._publish_update(topic_suffix=gui_suffix, value=final_value_mhz)
            elif "VBW_Hz" in yak_suffix:
                final_value_mhz = float(raw_value) / self.HZ_TO_MHZ
                self.vbw_value = final_value_mhz
                self._publish_update(topic_suffix=gui_suffix, value=final_value_mhz)
            elif "VBW_Auto_On" in yak_suffix:
                is_on = (str(raw_value).strip() == '1')
                self._publish_update(topic_suffix="Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected", value=is_on)
                self._publish_update(topic_suffix="Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/OFF/selected", value=not is_on)
            elif "Continuous_Mode_On" in yak_suffix:
                is_on = (str(raw_value).strip() == '1')
                self._publish_update(topic_suffix="Settings/fields/Sweep_Mode/options/Continuous/selected", value=is_on)
                self._publish_update(topic_suffix="Settings/fields/Sweep_Mode/options/Single/selected", value=not is_on)
            elif "Sweep_Time_s" in yak_suffix:
                final_value = float(raw_value)
                self.sweep_time_value = final_value
                self._publish_update(topic_suffix=gui_suffix, value=final_value)
        except Exception as e:
            console_log(f"❌ Error processing YAK output for {topic}: {e}")

    def _on_message(self, topic, payload):
        if topic.startswith(f"{self.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs"):
            self._process_yak_output(topic, payload)
            return
        
        try:
            value = json.loads(payload).get('value', payload)
        except (json.JSONDecodeError, TypeError):
            value = payload

        if self._locked_state.get(topic, False):
            self._locked_state[topic] = False
            return

        def _get_option_number(t):
            try: return int(t.split('/')[-2])
            except (ValueError, IndexError): return None

        # --- Message Routing ---
        topic_map = {
            "Resolution Bandwidth/fields/RBW/value": ("rbw_value", 0.1, self._publish_rbw_and_trigger),
            "Sweep_time_s/value": ("sweep_time_value", 0.001, self._publish_sweep_time_and_trigger),
            "Video Bandwidth/fields/vbw_MHz/value": ("vbw_value", 0.001, self._publish_vbw_and_trigger)
        }

        for suffix, (attr, threshold, func) in topic_map.items():
            if topic.endswith(f"/{suffix}"):
                new_val = float(value)
                if getattr(self, attr) is None or abs(getattr(self, attr) - new_val) > threshold:
                    setattr(self, attr, new_val)
                    func(new_val)
                return

        if "Resolution Bandwidth/fields/Resolution Band Width/options" in topic:
            if topic.endswith("/value"):
                opt_num = _get_option_number(topic)
                if opt_num is not None: self.rbw_preset_values[opt_num] = float(value)
            elif topic.endswith("/units"):
                opt_num = _get_option_number(topic)
                if opt_num is not None: self.rbw_preset_units[opt_num] = str(value)
            elif topic.endswith("/selected") and str(value).lower() == 'true':
                self._apply_preset(topic, self.rbw_preset_values, self.rbw_preset_units, "Settings/fields/Resolution Bandwidth/fields/RBW/value", is_rbw=True)
            return

        if "Video Bandwidth/fields/Video Band Width /options" in topic:
            if topic.endswith("/value"):
                opt_num = _get_option_number(topic)
                if opt_num is not None: self.vbw_preset_values[opt_num] = float(value)
            elif topic.endswith("/units"):
                opt_num = _get_option_number(topic)
                if opt_num is not None: self.vbw_preset_units[opt_num] = str(value)
            elif topic.endswith("/selected") and str(value).lower() == 'true':
                self._apply_preset(topic, self.vbw_preset_values, self.vbw_preset_units, "Settings/fields/Video Bandwidth/fields/vbw_MHz/value", is_rbw=False)
            return

        if "Video Bandwidth/fields/VBW_Automatic/options" in topic and topic.endswith("/selected") and str(value).lower() == 'true':
            is_on = "ON" in topic
            self._publish_vbw_auto_and_trigger(is_auto_on=is_on)
            return

    def _apply_preset(self, topic, preset_value_map, preset_unit_map, target_suffix, is_rbw: bool):
        try:
            option_number = int(topic.split('/')[-2])
            raw_value = preset_value_map.get(option_number)
            unit_string = preset_unit_map.get(option_number)
            
            if raw_value is not None and unit_string is not None:
                multiplier = self._get_multiplier(unit_string=unit_string)
                final_value_hz = raw_value * multiplier
                new_value_mhz = final_value_hz / self.HZ_TO_MHZ
                
                full_target_topic = f"{self.base_topic}/{target_suffix}"
                if full_target_topic in self._locked_state:
                    self._locked_state[full_target_topic] = True
                
                self._publish_update(topic_suffix=target_suffix, value=new_value_mhz)
                self.mqtt_controller.publish_message(topic=topic, subtopic="", value=True, retain=False)
                
                yak_input = self.YAK_RBW_INPUT if is_rbw else self.YAK_VBW_INPUT
                yak_trigger = self.YAK_RBW_TRIGGER if is_rbw else self.YAK_VBW_TRIGGER
                self._publish_to_yak_and_trigger(value=final_value_hz, input_topic=yak_input, trigger_topic=yak_trigger)
            else:
                console_log(f"❌ Error: Preset data missing for option {option_number}.")
                self.mqtt_controller.publish_message(topic=topic, subtopic="", value=False, retain=False)
                self._update_all_from_device()
        except Exception as e:
            console_log(f"❌ Error applying preset: {e}")

    def _publish_update(self, topic_suffix, value):
        full_topic = f"{self.base_topic}/{topic_suffix}"
        rounded_value = round(float(value), 6) 
        self.mqtt_controller.publish_message(topic=full_topic, subtopic="", value=rounded_value, retain=False)