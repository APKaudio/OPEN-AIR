# workers/State_Cache/state_cache_manager.py
#
# Version 20251230.230400.1
#
# Author: Gemini
#
# The Orchestrator: The public API for the state cache system.

import inspect
from typing import Dict, Any

from . import cache_io_handler
from . import cache_traffic_controller
from . import gui_state_restorer
from workers.logger.logger import debug_logger
from workers.utils.log_utils import _get_log_args

current_version = "20251230.230400.1"
current_version_hash = (20251230 * 230400 * 1)


class StateCacheManager:
    """
    The public API for the state cache system.
    """

    def __init__(self, state_mirror_engine: Any, mqtt_connection_manager: Any):
        """
        Spools up the IO Handler and Traffic Controller.
        """
        self.state_mirror_engine = state_mirror_engine
        self.mqtt_connection_manager = mqtt_connection_manager
        self.cache = {}
        self.subscriber_router = None
        debug_logger(message="Great Scott! The State Cache Manager is online! We're ready to manipulate the timeline!", **_get_log_args())

    def subscribe_to_all_topics(self):
        """
        Subscribes to all topics under the OPEN-AIR root to capture all state.
        """
        topic = "OPEN-AIR/#"
        self.mqtt_connection_manager.client.subscribe(topic)
        debug_logger(message=f"StateCacheManager subscribing to topic: {topic}", **_get_log_args())

    def initialize_state(self) -> None:
        """
        Calls IO load -> calls Restorer.
        """
        debug_logger(message="Initializing the timeline... let's see what the past holds.", **_get_log_args())
        self.cache = cache_io_handler.load_cache()
        if self.cache:
            debug_logger(message="The Almanac has entries! Engaging the Time Circuits!", **_get_log_args())
            gui_state_restorer.restore_timeline(self.cache, self.state_mirror_engine)
        else:
            debug_logger(message="The Almanac is empty. Starting with a fresh timeline.", **_get_log_args())

    def handle_incoming_mqtt(self, client, userdata, msg) -> None:
        """
        Calls Traffic Controller -> Calls IO Save (if changed) -> Calls router.
        """
        topic = msg.topic
        payload = msg.payload
        debug_logger(message=f"A temporal flux has been detected! Topic: {topic}", **_get_log_args())

        should_process, new_payload = cache_traffic_controller.process_traffic(topic, payload, self.cache)

        if should_process:
            debug_logger(message="This is heavy! The timeline has been altered. Recording the new event.", **_get_log_args())
            self.cache[topic] = new_payload
            cache_io_handler.save_cache(self.cache)
        else:
            debug_logger(message="The event is a duplicate. No alteration to the timeline needed.", **_get_log_args())

        if self.subscriber_router:
            debug_logger(message="Forwarding the temporal flux to the main timeline...", **_get_log_args())
            self.subscriber_router._on_message(client, userdata, msg)
        else:
            debug_logger(message="Nowhere to route the temporal flux! The subscriber router is missing!", **_get_log_args())
