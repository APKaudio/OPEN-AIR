# workers/mqtt/mqtt_subscriber_router.py
#
# Purpose: The ear. Listens to topics and routes them to a callback.
# Key Function: subscribe_to_topic(topic: str, callback_function)
# Key Function: _on_message(client, userdata, msg) -> Decodes the byte payload and fires the callback.

import paho.mqtt.client as mqtt
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args

class MqttSubscriberRouter:
    def __init__(self):
        self._subscribers = {}

    def subscribe_to_topic(self, topic_filter: str, callback_func):
        """
        Stores a callback function for a given topic filter and subscribes if the client is connected.
        """
        self._subscribers[topic_filter] = callback_func
        
        # Avoid circular import by importing here
        from .mqtt_connection_manager import MqttConnectionManager
        client = MqttConnectionManager().get_client_instance()
        
        if client and client.is_connected():
            client.subscribe(topic_filter)
            debug_log(message=f"Subscribed to {topic_filter}", **_get_log_args())
        else:
            debug_log(message=f"Client not connected. Subscription to {topic_filter} is pending.", **_get_log_args())

    def _on_message(self, client, userdata, msg):
        """
        Callback for when an MQTT message is received.
        It decodes the message and dispatches it to the appropriate subscriber.
        """
        topic = msg.topic
        try:
            payload = msg.payload.decode()
        except UnicodeDecodeError:
            debug_log(message=f"Could not decode payload for topic {topic}", **_get_log_args())
            return
            
        for topic_filter, callback_func in self._subscribers.items():
            if mqtt.topic_matches_sub(topic_filter, topic):
                try:
                    callback_func(topic, payload)
                except Exception as e:
                    debug_log(message=f"Error in callback for topic {topic}: {e}", **_get_log_args())

    def get_on_message_callback(self):
        """
        Returns the _on_message method to be used by the MqttConnectionManager.
        """
        return self._on_message
