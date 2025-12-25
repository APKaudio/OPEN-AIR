# workers/mqtt/setup/config_reader.py

import configparser
import pathlib

class Config:
    # --- Default values ---
    CURRENT_VERSION = "unknown"
    PERFORMANCE_MODE = True
    SKIP_DEP_CHECK = True
    ENABLE_DEBUG_MODE = False
    ENABLE_DEBUG_FILE = False
    ENABLE_DEBUG_SCREEN = False
    LOG_TRUNCATION_ENABLED = False
    UI_LAYOUT_SPLIT_EQUAL = 50
    UI_LAYOUT_FULL_WEIGHT = 100
    MQTT_BROKER_ADDRESS = "localhost"
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = None
    MQTT_PASSWORD = None

    def __init__(self):
        # Initialize the internal state for LOCAL_DEBUG_ENABLE
        self._local_debug_enable_state = self.ENABLE_DEBUG_SCREEN

    @property
    def LOCAL_DEBUG_ENABLE(self):
        return self._local_debug_enable_state

    @LOCAL_DEBUG_ENABLE.setter
    def LOCAL_DEBUG_ENABLE(self, value):
        self._local_debug_enable_state = value

    # This dictionary is for compatibility with older code that uses global_settings
    @property
    def global_settings(self):
        return {
            "general_debug_enabled": self.ENABLE_DEBUG_MODE,
            "debug_to_terminal": self.ENABLE_DEBUG_SCREEN,
            "debug_to_file": self.ENABLE_DEBUG_FILE,
            "log_truncation_enabled": self.LOG_TRUNCATION_ENABLED,
        }

    @classmethod
    def read_config(cls):
        """
        Reads configuration from config.ini and updates class attributes.
        """
        config = configparser.ConfigParser()
        # Assuming this file is at workers/mqtt/setup/config_reader.py, the project root is 4 levels up.
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        config_path = project_root / 'config.ini'

        if config_path.exists():
            config.read(config_path)
            
            if 'Version' in config:
                cls.CURRENT_VERSION = config['Version'].get('CURRENT_VERSION', cls.CURRENT_VERSION)
            
            if 'Mode' in config:
                cls.PERFORMANCE_MODE = config['Mode'].getboolean('PERFORMANCE_MODE', cls.PERFORMANCE_MODE)
                cls.SKIP_DEP_CHECK = config['Mode'].getboolean('SKIP_DEP_CHECK', cls.SKIP_DEP_CHECK)

            if 'Debug' in config:
                cls.ENABLE_DEBUG_MODE = config['Debug'].getboolean('ENABLE_DEBUG_MODE', cls.ENABLE_DEBUG_MODE)
                cls.ENABLE_DEBUG_FILE = config['Debug'].getboolean('ENABLE_DEBUG_FILE', cls.ENABLE_DEBUG_FILE)
                cls.ENABLE_DEBUG_SCREEN = config['Debug'].getboolean('ENABLE_DEBUG_SCREEN', cls.ENABLE_DEBUG_SCREEN)
                cls.LOG_TRUNCATION_ENABLED = config['Debug'].getboolean('LOG_TRUNCATION_ENABLED', cls.LOG_TRUNCATION_ENABLED)

            if 'UI' in config:
                cls.UI_LAYOUT_SPLIT_EQUAL = int(config['UI'].get('LAYOUT_SPLIT_EQUAL', cls.UI_LAYOUT_SPLIT_EQUAL))
                cls.UI_LAYOUT_FULL_WEIGHT = int(config['UI'].get('LAYOUT_FULL_WEIGHT', cls.UI_LAYOUT_FULL_WEIGHT))

            if 'MQTT' in config:
                cls.MQTT_BROKER_ADDRESS = config['MQTT'].get('BROKER_ADDRESS', cls.MQTT_BROKER_ADDRESS)
                cls.MQTT_BROKER_PORT = int(config['MQTT'].get('BROKER_PORT', cls.MQTT_BROKER_PORT))
                cls.MQTT_USERNAME = config['MQTT'].get('MQTT_USERNAME', cls.MQTT_USERNAME)
                cls.MQTT_PASSWORD = config['MQTT'].get('MQTT_PASSWORD', cls.MQTT_PASSWORD)
        else:
            print(f"Warning: config.ini not found at {config_path}. Using default settings.")

# Instantiate the config to be used by other modules
app_constants = Config()
app_constants.read_config()

