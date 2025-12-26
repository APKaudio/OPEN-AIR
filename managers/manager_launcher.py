# managers/manager_launcher.py

import os
import inspect

from workers.logger.logger import  debug_logger
from workers.utils.log_utils import _get_log_args

# --- MQTT and Proxy Imports ---
from workers.mqtt.mqtt_connection_manager import MqttConnectionManager
from workers.mqtt.mqtt_subscriber_router import MqttSubscriberRouter
from workers.logic.state_mirror_engine import StateMirrorEngine
from managers.VisaScipi.manager_visa import VisaManagerOrchestrator
from managers.yak.yak_translator import YakTranslator # Import YakTranslator
from managers.yak.manager_yak_rx import YakRxManager # Import YakRxManager


def launch_managers(app, splash): # Removed scpi_dispatcher
    current_function_name = inspect.currentframe().f_code.co_name
    debug_logger(message=f"🟢️️️🟢 Entering '{current_function_name}'. Preparing to launch a fleet of managers!", **_get_log_args())
    splash.set_status("Initializing managers...")

    try:
        # 1. Initialize MQTT Core Components
        mqtt_connection_manager = MqttConnectionManager()
        subscriber_router = MqttSubscriberRouter()
        state_mirror_engine = StateMirrorEngine(base_topic="OPEN-AIR", subscriber_router=subscriber_router)
        
        # Connect MQTT Client (if not already connected by Application)
        mqtt_connection_manager.connect_to_broker(
            on_message_callback=subscriber_router.get_on_message_callback(),
            subscriber_router=subscriber_router
        )

        # 2. Initialize Visa Manager Orchestrator
        visa_orchestrator = VisaManagerOrchestrator(
            mqtt_connection_manager=mqtt_connection_manager,
            subscriber_router=subscriber_router
        )

        # 3. Initialize Yak Translator
        yak_translator = YakTranslator(
            mqtt_connection_manager=mqtt_connection_manager,
            subscriber_router=subscriber_router
        )

        # 4. Initialize Yak RX Manager
        yak_rx_manager = YakRxManager(
            mqtt_connection_manager=mqtt_connection_manager,
            subscriber_router=subscriber_router,
            yak_translator=yak_translator
        )

        debug_logger(message="✅ All core managers have been successfully launched!", **_get_log_args())
        splash.set_status("Managers initialized.")
        
        # Consolidate all managers into one dictionary
        all_managers = {
            "mqtt_connection_manager": mqtt_connection_manager,
            "subscriber_router": subscriber_router,
            "state_mirror_engine": state_mirror_engine,
            "yak_translator": yak_translator,
            "yak_rx_manager": yak_rx_manager,
        }
        all_managers.update(visa_orchestrator.get_managers())

        # Return instantiated managers for use by the application if needed
        return all_managers

    except Exception as e:
        debug_logger(message=f"❌ Critical error during manager launch: {e}", **_get_log_args())
        splash.set_status(f"Manager initialization failed: {e}", error=True)
        return None