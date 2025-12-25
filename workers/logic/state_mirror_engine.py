# workers/logic/state_mirror_engine.py
#
# Manages the synchronization between the GUI state and the MQTT Broker.
# Acts as the "Flux Capacitor" of data flow—translating between visual widgets
# and the invisible energy of MQTT topics.
#
# Author: Anthony Peter Kuzub
# Version 20251225.004500.1

import orjson
import inspect
import uuid
import time
from workers.logger.logger import debug_log, console_log
from workers.utils.log_utils import _get_log_args
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          
from workers.mqtt import mqtt_publisher_service

app_constants = Config.get_instance() # Get the singleton instance      

import workers.utils.topic_utils as topic_utils

# Globals
current_version = "20251225.004500.1"
current_version_hash = 20251225 * 4500 * 1

class StateMirrorEngine:
    def __init__(self, base_topic, subscriber_router):
        self.base_topic = base_topic
        self.subscriber_router = subscriber_router
        self.registered_widgets = {} # Map topic -> (tk_variable, tab_name)
        self.instance_id = str(uuid.uuid4()) # Unique ID for this GUI instance

        # 🧪 FIX: IMMEDIATE SUBSCRIPTION
        # We must listen to the very timeline we are creating!
        self._subscribe_to_timeline()

    def _subscribe_to_timeline(self):
        """
        Subscribes to the entire hierarchy of this engine's domain.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Subscribe to everything under the base topic (e.g., OPEN-AIR/Mixing Console/#)
        wildcard_topic = f"{self.base_topic}/#"
        
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🧪 Great Scott! Attaching electrodes to the timeline! Subscribing to: {wildcard_topic}",
                **_get_log_args()
            )
            
        # Register the callback for this wildcard
        # Note: The subscriber router must handle the routing to this specific callback
        self.subscriber_router.subscribe_to_topic(
            topic_filter=wildcard_topic, 
            callback_func=self.sync_incoming_mqtt_to_gui
        )

    def register_widget(self, widget_id, tk_variable, tab_name):
        """
        Registers a widget to be tracked by the engine.
        """
        # (Existing logic to register widget...)
        full_topic = topic_utils.get_topic(self.base_topic, tab_name, widget_id)
        self.registered_widgets[full_topic] = {
            "var": tk_variable,
            "tab": tab_name,
            "id": widget_id
        }
        
        # Also subscribe explicitly to this specific topic if the router requires exact matches
        # (Optional depending on router logic, but safe to add)
        # self.subscriber_router.subscribe_to_topic(full_topic, self.sync_incoming_mqtt_to_gui)

    def broadcast_gui_change_to_mqtt(self, widget_id):
        """
        Called when the GUI changes (User Input).
        It broadcasts the change to the MQTT broker, including the instance_id.
        """
        found_widget_info = None
        found_full_topic = None

        # Find the widget info and full topic associated with the widget_id
        for full_topic, widget_info in self.registered_widgets.items():
            if widget_info["id"] == widget_id:
                found_widget_info = widget_info
                found_full_topic = full_topic
                break
        
        if found_widget_info and found_full_topic:
            tk_var = found_widget_info["var"]
            value = tk_var.get()
            
            payload_data = {
                "val": value,
                "src": "gui", # Indicate source is GUI
                "ts": time.time(), # Timestamp
                "instance_id": self.instance_id # Unique ID of this GUI instance
            }
            payload_json = orjson.dumps(payload_data)
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"DEBUG: Payload JSON to be published from StateMirrorEngine: {payload_json}",
                    **_get_log_args()
                )
            mqtt_publisher_service.publish_payload(found_full_topic, payload_json)
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"⬆️ GUI Change Broadcast: Widget '{widget_id}' to {value} on {found_full_topic}. (Instance: {self.instance_id})",
                    **_get_log_args()
                )
        else:
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"⚠️ Attempted to broadcast change for unregistered widget_id: {widget_id}",
                    **_get_log_args()
                )

    def is_widget_registered(self, widget_id: str) -> bool:
        """Checks if a widget is registered by its widget_id."""
        for widget_info in self.registered_widgets.values():
            if widget_info["id"] == widget_id:
                return True
        return False

    def publish_command(self, topic: str, payload: str):
        """Publishes a command to the MQTT broker."""
        mqtt_publisher_service.publish_payload(topic, payload)
        debug_log(message=f"Published command to topic {topic}", **_get_log_args())

    def sync_incoming_mqtt_to_gui(self, topic, payload):
        """
        Handles incoming messages from the Broker.
        This is where we prevent the Time Paradox (Infinite Loop).
        """
        current_function_name = inspect.currentframe().f_code.co_name

        try:
            # 1. Parse the Data
            # Handle cases where payload might be bytes or string
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = str(payload)
            
            # Pre-validate: If it doesn't look like JSON, log a warning and return.
            # This handles empty strings, simple strings like 'OFFLINE', etc.
            stripped_payload = payload_str.strip()
            if not stripped_payload.startswith(('{', '[')):
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"⚠️ Non-JSON payload received for topic '{topic}'. Payload: '{payload_str}'. Ignoring for StateMirrorEngine.",
                        **_get_log_args()
                    )
                return
            
            data = orjson.loads(stripped_payload)
            
            # 🧪 LOGGING: Confirm receipt
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"📥 Great Scott! Message returned! Topic: {topic}",
                    **_get_log_args()
                )

            # 2. Extract Source & Value
            source = data.get("src", "unknown")
            new_value = data.get("val", None)
            sender_instance_id = data.get("instance_id", None) # Extract sender's instance ID

            # 3. GRANDFATHER PARADOX CHECK
            if source == "gui" and sender_instance_id == self.instance_id:
                # This is an echo of our own voice!
                # We acknowledge it, but we DO NOT touch the widget or re-trigger logic.
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🐈‍⬛ Déjà vu detected (Source: GUI, Instance: {sender_instance_id}). Ignoring echo to preserve causality.",
                        **_get_log_args()
                    )
                return

            # 4. Update the Widget (If it's from Device or Backend)
            if topic in self.registered_widgets:
                widget_info = self.registered_widgets[topic]
                tk_var = widget_info["var"]
                
                # Prevent feedback loop during update
                # (Assuming you have a mechanism to temporarily disable the trace, 
                # or rely on the fact that setting the var might trigger the trace again 
                # but the 'src' check in broadcast_gui_change will handle it?)
                
                current_val = tk_var.get()
                
                # Only update if different (prevent jitter)
                if str(current_val) != str(new_value):
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(
                            message=f"⚡ fluxing... Updating GUI Widget '{widget_info['id']}' to {new_value}",
                            **_get_log_args()
                        )
                    tk_var.set(new_value)
            else:
                # Topic not registered to a specific widget
                pass

        except Exception as e:
            debug_log(
                message=f"🔥 The Flux Capacitor is cracking! Error in sync_incoming_mqtt_to_gui: {e}",
                **_get_log_args()
            )