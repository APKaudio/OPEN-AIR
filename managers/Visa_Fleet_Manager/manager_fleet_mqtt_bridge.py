# managers/Visa_Fleet_Manager/manager_fleet_mqtt_bridge.py
#
# The "Translator" that connects the standalone Visa Fleet Manager to the MQTT network.
#
# Author: Gemini Agent
#

import orjson
import time

# Import the VisaJsonBuilder for file path and loading logic
from managers.Visa_Fleet_Manager.manager_visa_json_builder import VisaJsonBuilder

try:
    from workers.logger.logger import debug_logger
    from workers.logger.log_utils import _get_log_args
except ModuleNotFoundError:
    print("Warning: 'workers.logger' not found. Using dummy logger for FleetMqttBridge.")
    def debug_logger(message, *args, **kwargs):
        if kwargs.get('level', 'INFO') != 'DEBUG':
            print(f"[{kwargs.get('level', 'INFO')}] {message}")
    def _get_log_args(*args, **kwargs):
        return {} # Return empty dict, as logger args are not available

# Import the Standalone Core
from managers.Visa_Fleet_Manager.visa_fleet_manager import VisaFleetManager

class FleetMqttBridge:
    def __init__(self, mqtt_connection_manager, subscriber_router):
        self.mqtt_connection_manager = mqtt_connection_manager # Store the manager
        self.subscriber = subscriber_router # Store the router
        self.json_builder = VisaJsonBuilder() # Initialize the JSON builder
        
        # Instantiate the Core Logic (Headless)
        self.core_manager = VisaFleetManager()
        
        # --- Wire the Core Events to MQTT Publishers ---
        # We register "Listeners" to the core manager. When the core has data, 
        # it calls these functions, and we publish to MQTT.
        self.core_manager.set_callbacks(
            on_inventory_update=self._publish_inventory,
            on_device_response=self._publish_device_response,
            on_device_error=self._publish_device_error,
            on_proxy_status=self._publish_proxy_status
        )

        # --- MQTT Topic Definitions ---
        self.TOPIC_DISCOVERY = "OPEN-AIR/Device/Discovery/Search_Trigger"
        self.TOPIC_INVENTORY = "OPEN-AIR/setep/devices" # Changed topic here
        self.TOPIC_CMD_INBOX = "OPEN-AIR/Device/+/Tx_Inbox" # Wildcard for any device

    def start(self):
        """Starts the MQTT Bridge components and the Core Manager."""
        debug_logger("🌉 Bridge: Starting MQTT Bridge for Visa Fleet...", **_get_log_args())
        
        # MQTT connection is handled by manager_launcher now.
        # 1. Subscribe to Incoming Topics
        self.subscriber.subscribe_to_topic(self.TOPIC_DISCOVERY, self._on_discovery_request)
        self.subscriber.subscribe_to_topic(self.TOPIC_CMD_INBOX, self._on_device_command)
        
        # 3. Start the Core Logic
        self.core_manager.start()
        
        # 4. Publish initial inventory (loaded from JSON by core_manager)
        if self.core_manager.current_inventory:
            debug_logger("🌉 Bridge: Publishing initial inventory from file.", **_get_log_args())
            self._publish_inventory(self.core_manager.current_inventory) # Pass current_inventory, but _publish_inventory will reload
        
        debug_logger("🌉 Bridge: System Online.", **_get_log_args())

    def stop(self):
        self.core_manager.stop()
        # self.mqtt_util.disconnect() # Removed as mqtt_connection_manager handles disconnection

    # --- Inbound: MQTT -> Core Logic ---

    def _on_discovery_request(self, topic, payload):
        """Received 'Scan' command from MQTT -> Call Core.scan()"""
        try:
            data = orjson.loads(payload)
            if data.get("value") is True:
                debug_logger("🌉 Bridge: RX Discovery Request -> Triggering Core Scan.", **_get_log_args())
                self.core_manager.trigger_scan()
        except Exception as e:
            debug_logger(f"🌉 Bridge: Error parsing discovery request: {e}", **_get_log_args(), level="ERROR")

    def _on_device_command(self, topic, payload):
        """Received Command for specific device -> Call Core.send_command()"""
        # Topic format: OPEN-AIR/Device/{serial}/Tx_Inbox
        try:
            parts = topic.split('/')
            if len(parts) < 4: return
            
            target_serial = parts[2] # Extract Serial from topic
            
            data = orjson.loads(payload)
            cmd = data.get("command")
            is_query = data.get("query", False)
            corr_id = data.get("correlation_id", "N/A")
            
            if cmd:
                self.core_manager.enqueue_command(target_serial, cmd, is_query, corr_id)
                
        except Exception as e:
            debug_logger(f"🌉 Bridge: Error processing command payload: {e}", **_get_log_args(), level="ERROR")

    # --- Outbound: Core Logic -> MQTT ---

    def _publish_inventory(self, inventory_list):
        """Core updated inventory -> Reload from file and Publish to MQTT"""
        debug_logger(f"🌉 Bridge: Reloading grouped inventory from file and publishing to {self.TOPIC_INVENTORY}.", **_get_log_args())
        try:
            # Load the already grouped inventory from the JSON file
            grouped_inventory = self.json_builder.load_inventory_from_json()
            
            if grouped_inventory:
                # Convert the dictionary to a JSON string for publishing
                payload = orjson.dumps(grouped_inventory, option=orjson.OPT_INDENT_2).decode('utf-8')
                
                # Publish the JSON content
                self.mqtt_connection_manager.client.publish(
                    topic=self.TOPIC_INVENTORY, 
                    payload=payload, 
                    qos=1, 
                    retain=True # Retain makes the broker keep the last message for new subscribers
                )
                debug_logger(f"✅ Bridge: Successfully published grouped fleet inventory to {self.TOPIC_INVENTORY}.", **_get_log_args())
            else:
                debug_logger("⚠️ Bridge: No grouped fleet inventory found to publish.", **_get_log_args(), level="WARNING")
        except Exception as e:
            debug_logger(f"❌ Bridge: Error publishing grouped fleet inventory: {e}", **_get_log_args(), level="ERROR")

    def _publish_device_response(self, serial, response, command, corr_id):
        """Core received device data -> Publish to Rx_Outbox"""
        topic = f"OPEN-AIR/Device/{serial}/Rx_Outbox"
        payload = orjson.dumps({
            "response": response,
            "command": command,
            "correlation_id": corr_id,
            "timestamp": time.time()
        })
        self.mqtt_connection_manager.client.publish(topic=topic, payload=payload)

    def _publish_device_error(self, serial, message, command):
        """Core reported error -> Publish to Error topic"""
        topic = f"OPEN-AIR/Device/{serial}/Error"
        payload = orjson.dumps({
            "error": message, 
            "command": command, 
            "timestamp": time.time()
        })
        self.mqtt_connection_manager.client.publish(topic=topic, payload=payload)

    def _publish_proxy_status(self, serial, status):
        """Core connection status changed -> Publish Status"""
        topic = f"OPEN-AIR/Device/{serial}/Proxy_Status"
        payload = orjson.dumps({"status": status, "ts": time.time()})
        self.mqtt_connection_manager.client.publish(topic=topic, payload=payload, retain=True)

if __name__ == "__main__":
    bridge = FleetMqttBridge()
    bridge.start()
    while True:
        time.sleep(1)

