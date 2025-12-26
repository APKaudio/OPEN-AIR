# managers/VisaScipi/manager_visa_mqtt_listen.py
#
# This manager handles listening to MQTT topics for device connection and control.
#
# Author: Anthony Peter Kuzub
#
import orjson
import threading
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args

# Constants for MQTT Topics
MQTT_TOPIC_SEARCH_TRIGGER = "OPEN-AIR/Device/Instrument_Connection/Search_and_Connect/Search_For_devices/trigger"
MQTT_TOPIC_DEVICE_SELECT = "OPEN-AIR/Device/Instrument_Connection/Search_and_Connect/Found_devices/options/+/selected"
MQTT_TOPIC_CONNECT_TRIGGER = "OPEN-AIR/Device/Instrument_Connection/Search_and_Connect/Connect_to_Device/trigger"
MQTT_TOPIC_DISCONNECT_TRIGGER = "OPEN-AIR/Device/Instrument_Connection/Search_and_Connect/Disconnect_device/trigger"
MQTT_TOPIC_CONNECT_RESOURCE_REQUEST = "OPEN-AIR/commands/instrument/connect"

class VisaMqttListener:
    def __init__(self, subscriber_router, searcher, connector, disconnector, gui_publisher):
        self.subscriber_router = subscriber_router
        self.searcher = searcher
        self.connector = connector
        self.disconnector = disconnector
        self.gui_publisher = gui_publisher

        self.found_resources = []
        self.selected_device_resource = None
        self.inst = None

        self._setup_mqtt_subscriptions()

    def _setup_mqtt_subscriptions(self):
        try:
            self.subscriber_router.subscribe_to_topic(topic_filter=MQTT_TOPIC_SEARCH_TRIGGER, callback_func=self._on_search_request)
            self.subscriber_router.subscribe_to_topic(topic_filter=MQTT_TOPIC_DEVICE_SELECT, callback_func=self._on_device_select)
            self.subscriber_router.subscribe_to_topic(topic_filter=MQTT_TOPIC_CONNECT_TRIGGER, callback_func=self._on_gui_connect_request)
            self.subscriber_router.subscribe_to_topic(topic_filter=MQTT_TOPIC_DISCONNECT_TRIGGER, callback_func=self._on_gui_disconnect_request)
            self.subscriber_router.subscribe_to_topic(topic_filter=MQTT_TOPIC_CONNECT_RESOURCE_REQUEST, callback_func=self._on_connect_request)
            debug_log(message="💳 ✅ VisaMqttListener subscribed to all necessary GUI and command topics.", **_get_log_args())
        except Exception as e:
            debug_log(message=f"💳 ❌ Error in VisaMqttListener._setup_mqtt_subscriptions: {e}", **_get_log_args())

    def _on_search_request(self, topic, payload):
        try:
            payload_data = orjson.loads(payload)
            if str(payload_data.get('value')).lower() == 'true':
                debug_log(message="💳 🔍 Search for devices initiated from GUI.", **_get_log_args())
                self.found_resources = self.searcher.search_resources()
                self.gui_publisher._update_found_devices_gui(self.found_resources)
        except (orjson.JSONDecodeError, AttributeError) as e:
            debug_log(message=f"💳 ❌ Error in _on_search_request: {e}", **_get_log_args())

    def _on_device_select(self, topic, payload):
        try:
            payload_data = orjson.loads(payload)
            if str(payload_data.get('value')).lower() == 'true':
                parts = topic.split('/')
                option_index = int(parts[-2]) - 1
                if 0 <= option_index < len(self.found_resources):
                    self.selected_device_resource = self.found_resources[option_index]
                    debug_log(message=f"💳 ✅ Device selected: {self.selected_device_resource}", **_get_log_args())
                else:
                    self.selected_device_resource = None
        except (orjson.JSONDecodeError, IndexError, ValueError, AttributeError) as e:
            debug_log(message=f"💳 ❌ Error in _on_device_select: {e}", **_get_log_args())

    def _on_gui_connect_request(self, topic, payload):
        try:
            payload_data = orjson.loads(payload)
            if str(payload_data.get('value')).lower() == 'true':
                if self.selected_device_resource:
                    debug_log(message=f"💳 🔵 Initiating connection to {self.selected_device_resource}...", **_get_log_args())
                    thread = threading.Thread(target=self._connect_and_get_inst, args=(self.selected_device_resource,), daemon=True)
                    thread.start()
                else:
                    debug_log(message="💳 🟡 No device selected to connect.", **_get_log_args())
        except (orjson.JSONDecodeError, AttributeError) as e:
            debug_log(message=f"💳 ❌ Error in _on_gui_connect_request: {e}", **_get_log_args())

    def _connect_and_get_inst(self, resource_name):
        self.inst = self.connector.connect_instrument_logic(resource_name)

    def _on_gui_disconnect_request(self, topic, payload):
        try:
            payload_data = orjson.loads(payload)
            if str(payload_data.get('value')).lower() == 'true':
                if self.inst:
                    debug_log(message="💳 🔵 Initiating disconnection...", **_get_log_args())
                    thread = threading.Thread(target=self.disconnector.disconnect_instrument_logic, args=(self.inst,), daemon=True)
                    thread.start()
                    self.inst = None
                else:
                    debug_log(message="💳 🟡 No device is currently connected.", **_get_log_args())
        except Exception as e:
            debug_log(message=f"💳 ❌ Error in _on_gui_disconnect_request: {e}", **_get_log_args())

    def _on_connect_request(self, topic, payload):
        try:
            payload_data = orjson.loads(payload)
            resource_name = payload_data.get('resource')
            if resource_name:
                debug_log(message=f"💳 MQTT: Direct connect request for resource: {resource_name}", **_get_log_args())
                thread = threading.Thread(target=self._connect_and_get_inst, args=(resource_name,), daemon=True)
                thread.start()
            else:
                debug_log(message="💳 MQTT: Connect request received but no resource_name in payload.", **_get_log_args())
        except orjson.JSONDecodeError:
            debug_log(message=f"💳 ❌ Failed to decode JSON payload for connect request: {payload}", **_get_log_args())
        except Exception as e:
            debug_log(message=f"💳 ❌ Error in _on_connect_request: {e}", **_get_log_args())
