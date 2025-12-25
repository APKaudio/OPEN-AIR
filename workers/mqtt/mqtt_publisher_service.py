# workers/mqtt/mqtt_publisher_service.py
#
# Purpose: A dedicated courier. Takes a topic and a payload, checks if connected, and sends it.
# Key Function: publish_payload(topic: str, payload: str, retain: bool)
# Key Function: publish_json_structure(base_topic: str, json_data: dict) -> The "Verbatim" requirement.

from .mqtt_connection_manager import MqttConnectionManager
import orjson
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args

def publish_payload(topic: str, payload: str, retain: bool = False):
    """
    Publishes a payload to a given topic.
    """
    connection_manager = MqttConnectionManager()
    client = connection_manager.get_client_instance()
    if client and client.is_connected():
        client.publish(topic, payload, retain=retain)
        debug_log(message=f"Published to {topic}: {payload}", **_get_log_args())
    else:
        debug_log(message=f"❌ Not connected to broker. Cannot publish to {topic}.", **_get_log_args())

def publish_json_structure(base_topic: str, json_data: dict):
    """
    Publishes the entire JSON structure to a base topic.
    The "Verbatim" requirement.
    """
    connection_manager = MqttConnectionManager()
    client = connection_manager.get_client_instance()
    if client and client.is_connected():
        payload = orjson.dumps(json_data)
        client.publish(base_topic, payload, retain=True)
        debug_log(message=f"Published JSON structure to {base_topic}", **_get_log_args())
    else:
        debug_log(message=f"❌ Not connected to broker. Cannot publish JSON structure to {base_topic}.", **_get_log_args())
