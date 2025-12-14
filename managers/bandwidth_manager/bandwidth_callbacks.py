# managers/bandwidth_manager/bandwidth_callbacks.py

import json
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from .bandwidth_state import BandwidthState
from .bandwidth_yak_communicator import BandwidthYakCommunicator
from .bandwidth_presets import BandwidthPresets

Local_Debug_Enable = True

class BandwidthCallbacks:
    """Handles MQTT message callbacks and logic for bandwidth settings."""

    def __init__(self, mqtt_controller: MqttControllerUtility, state: BandwidthState, yak_communicator: BandwidthYakCommunicator, presets: BandwidthPresets):
        self.mqtt_controller = mqtt_controller
        self.state = state
        self.yak_communicator = yak_communicator
        self.presets = presets
        self.base_topic = self.state.base_topic

    def subscribe_to_topics(self):
        topic_list = [
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/RBW/value",
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value",
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/vbw_MHz/value",
            
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/Resolution Band Width/options/+/selected",
            self.presets.TOPIC_RBW_PRESET_WILDCARD, 
            self.presets.TOPIC_RBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/Video Band Width /options/+/selected",
            self.presets.TOPIC_VBW_PRESET_WILDCARD, 
            self.presets.TOPIC_VBW_UNITS_WILDCARD,  
            
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected",
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/OFF/selected",
            
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected", 
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected", 
        ]
        
        for topic in topic_list:
            self.mqtt_controller.add_subscriber(topic_filter=topic, callback_func=self.on_message)
            
        for yak_suffix in self.yak_communicator.YAK_NAB_OUTPUTS.keys():
            yak_topic = f"{self.yak_communicator.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs/{yak_suffix}"
            self.mqtt_controller.add_subscriber(topic_filter=yak_topic, callback_func=self.on_message)

        self.yak_communicator.update_all_from_device()

    def on_message(self, topic, payload):
        if topic.startswith(f"{self.yak_communicator.YAK_BASE}/nab/NAB_bandwidth_settings/scpi_outputs"):
            self.yak_communicator.process_yak_output(topic, payload)
            return
        
        try:
            value = json.loads(payload).get('value', payload)
        except (json.JSONDecodeError, TypeError):
            value = payload

        if self.state._locked_state.get(topic, False):
            self.state._locked_state[topic] = False
            return

        if self.presets.handle_preset_message(topic, value):
            return

        topic_map = {
            "Resolution Bandwidth/fields/RBW/value": ("rbw_value", 0.1, self.yak_communicator.publish_rbw_and_trigger),
            "Sweep_time_s/value": ("sweep_time_value", 0.001, self.yak_communicator.publish_sweep_time_and_trigger),
            "Video Bandwidth/fields/vbw_MHz/value": ("vbw_value", 0.001, self.yak_communicator.publish_vbw_and_trigger)
        }

        for suffix, (attr, threshold, func) in topic_map.items():
            if topic.endswith(f"/{suffix}"):
                new_val = float(value)
                if getattr(self.state, attr) is None or abs(getattr(self.state, attr) - new_val) > threshold:
                    setattr(self.state, attr, new_val)
                    func(new_val)
                return

        if "Video Bandwidth/fields/VBW_Automatic/options" in topic and topic.endswith("/selected") and str(value).lower() == 'true':
            is_on = "ON" in topic
            self.yak_communicator.publish_vbw_auto_and_trigger(is_auto_on=is_on)
            return
