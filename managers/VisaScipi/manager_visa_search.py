# managers/VisaScipi/manager_visa_search.py
#
# This manager handles VISA device discovery and validation against yak_config.
#
# Author: Anthony Peter Kuzub
#
import orjson
import pathlib
import re
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args
from .manager_visa_list_visa_resources import list_visa_resources

class VisaDeviceSearcher:
    def __init__(self):
        self.yak_config = self._load_yak_config()

    def _load_yak_config(self):
        # Loads the connection_yak.json file.
        config_path = pathlib.Path("DATA/yak_configs/connection_yak.json")
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = orjson.loads(f.read())
                debug_log(message=f"💳 ✅ Yak configuration loaded from {config_path}", **_get_log_args())
                return config
            else:
                debug_log(message=f"💳 🟡 Yak configuration file not found at {config_path}. Using empty config.", **_get_log_args())
                return {"expected_devices": []}
        except orjson.JSONDecodeError as e:
            debug_log(message=f"💳 ❌ Error decoding {config_path}: {e}. Using empty config.", **_get_log_args())
            return {"expected_devices": []}
        except Exception as e:
            debug_log(message=f"💳 ❌ Error loading Yak configuration from {config_path}: {e}. Using empty config.", **_get_log_args())
            return {"expected_devices": []}

    def search_resources(self):
        debug_log(
            message=f"💳 GUI command received: initiating VISA resource search.",
            **_get_log_args()
        )
        all_resources = list_visa_resources()
        validated_resources = []
        
        expected_devices = self.yak_config.get("expected_devices", [])
        if not expected_devices:
            debug_log(message="💳 🟡 No expected devices configured in connection_yak.json. Returning all found resources.", **_get_log_args())
            return all_resources

        debug_log(message=f"💳 🔍 Validating {len(all_resources)} resources against {len(expected_devices)} expected device patterns.", **_get_log_args())

        for resource_name in all_resources:
            is_valid = False
            for device_spec in expected_devices:
                pattern = device_spec.get("resource_pattern")
                if pattern and re.match(pattern, resource_name):
                    debug_log(message=f"💳 ✅ Resource '{resource_name}' matched expected device pattern: '{pattern}'.", **_get_log_args())
                    validated_resources.append(resource_name)
                    is_valid = True
                    break
            if not is_valid:
                debug_log(message=f"💳 ❌ Resource '{resource_name}' did not match any expected device pattern.", **_get_log_args())
        
        if not validated_resources:
            debug_log(message="💳 🟡 No valid resources found matching any expected device patterns.", **_get_log_args())
            
        return validated_resources
