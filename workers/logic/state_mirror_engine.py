# workers/logic/state_mirror_engine.py
#
# Purpose: The Orchestrator. It holds the reference to the "Live" variables.
# Key Function: register_widget(widget_id, tk_variable) -> Maps a generic ID to a specific TKinter variable.
# Key Function: sync_incoming_mqtt_to_gui(topic, value) -> Updates the TK variable silently (to avoid loop).
# Key Function: broadcast_gui_change_to_mqtt(widget_id) -> Called when user touches GUI.

import orjson
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args
from workers.mqtt import mqtt_publisher_service
from workers.utils.topic_utils import get_topic

class StateMirrorEngine:
    def __init__(self, base_topic):
        self._widget_map = {}
        self._widget_tab_map = {}
        self.base_topic = base_topic
        self._silent_update = False

    def register_widget(self, widget_id, tk_variable, tab_name):
        """Maps a generic widget ID to a specific TKinter variable."""
        self._widget_map[widget_id] = tk_variable
        self._widget_tab_map[widget_id] = tab_name
        debug_log(message=f"Registered widget '{widget_id}' on tab '{tab_name}'", **_get_log_args())

    def sync_incoming_mqtt_to_gui(self, topic: str, payload: str):
        """
        Updates the TKinter variable associated with a topic.
        This function is intended to be used as a callback for the MqttSubscriberRouter.
        It updates the variable silently to avoid a broadcast loop.
        """
        try:
            parts = topic.split('/')
            if len(parts) > 2:
                tab_name = parts[1]
                widget_id = '/'.join(parts[2:])

                if widget_id in self._widget_map:
                    tk_var = self._widget_map[widget_id]
                    
                    # The payload is expected to be a JSON string with a "value" key.
                    data = orjson.loads(payload)
                    value = data.get("value")

                    # To avoid loops, we set a flag to indicate that this change
                    # is coming from MQTT and should not be broadcast back.
                    self._silent_update = True
                    tk_var.set(value)
                    self._silent_update = False
                    
                    debug_log(message=f"Updated widget '{widget_id}' with value '{value}' from MQTT", **_get_log_args())
                else:
                    debug_log(message=f"Widget '{widget_id}' not found in widget map.", **_get_log_args())
            else:
                debug_log(message=f"Invalid topic format: {topic}", **_get_log_args())

        except orjson.JSONDecodeError:
            debug_log(message=f"Could not decode payload for topic {topic}", **_get_log_args())
        except Exception as e:
            debug_log(message=f"Error syncing MQTT message to GUI: {e}", **_get_log_args())

    def broadcast_gui_change_to_mqtt(self, widget_id: str):
        """
        Called when a user interacts with a GUI widget.
        It broadcasts the change to the MQTT broker.
        """
        if self._silent_update:
            return
            
        if widget_id in self._widget_map:
            tk_var = self._widget_map[widget_id]
            value = tk_var.get()
            tab_name = self._widget_tab_map.get(widget_id)

            if tab_name:
                topic = get_topic(self.base_topic, tab_name, widget_id)
                payload = orjson.dumps({"value": value})
                
                mqtt_publisher_service.publish_payload(topic, payload)
                debug_log(message=f"Broadcasted GUI change for widget '{widget_id}' with value '{value}' to MQTT on topic {topic}", **_get_log_args())
            else:
                debug_log(message=f"Tab name for widget '{widget_id}' not found.", **_get_log_args())
        else:
            debug_log(message=f"Widget '{widget_id}' not found for broadcast.", **_get_log_args())

    def is_widget_registered(self, widget_id: str) -> bool:
        """Checks if a widget is registered."""
        return widget_id in self._widget_map

    def publish_command(self, topic: str, payload: str):
        """Publishes a command to the MQTT broker."""
        mqtt_publisher_service.publish_payload(topic, payload)
        debug_log(message=f"Published command to topic {topic}", **_get_log_args())

    def ingest_json(self, json_data: dict):
        """
        Publishes the entire JSON structure to the base topic.
        This is the "Genesis" step.
        """
        mqtt_publisher_service.publish_json_structure(self.base_topic, json_data)
