# workers/mqtt/setup/config_reader.py

import configparser
import pathlib
import threading # Import threading for thread-safe singleton

class Config:
    _instance = None
    _lock = threading.Lock() # Class-level lock for thread-safe singleton initialization

    # --- Default values ---
    CURRENT_VERSION = "unknown"
    PERFORMANCE_MODE = True
    SKIP_DEP_CHECK = True
    CLEAN_INSTALL_MODE = False
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
        # This __init__ will only be called once due to the singleton pattern
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._local_debug_enable_state = self.ENABLE_DEBUG_SCREEN
        self.read_config() # Read config immediately upon first instantiation

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of Config, ensuring it's initialized once.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls() # Calls __init__ which then calls read_config()
        return cls._instance

    @property
    def LOCAL_DEBUG_ENABLE(self):
        return self.ENABLE_DEBUG_SCREEN # Reflects the class-level setting

    @LOCAL_DEBUG_ENABLE.setter
    def LOCAL_DEBUG_ENABLE(self, value):
        # Direct modification of class-level attribute
        Config.ENABLE_DEBUG_SCREEN = value

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
        project_root = pathlib.Path(__file__).parent.parent.parent.parent
        config_path = project_root / 'config.ini'

        if config_path.exists():
            config.read(config_path)
            
            # --- Update class attributes directly ---
            if 'Version' in config:
                cls.CURRENT_VERSION = config['Version'].get('CURRENT_VERSION', cls.CURRENT_VERSION)
            
            if 'Mode' in config:
                cls.PERFORMANCE_MODE = config['Mode'].getboolean('PERFORMANCE_MODE', cls.PERFORMANCE_MODE)
                cls.SKIP_DEP_CHECK = config['Mode'].getboolean('SKIP_DEP_CHECK', cls.SKIP_DEP_CHECK)
                cls.CLEAN_INSTALL_MODE = config['Mode'].getboolean('CLEAN_INSTALL_MODE', cls.CLEAN_INSTALL_MODE)

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

