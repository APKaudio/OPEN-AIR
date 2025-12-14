Local_Debug_Enable = True

# managers/bandwidth_manager/bandwidth_state.py

class BandwidthState:
    """Holds the state for bandwidth-related settings."""
    def __init__(self):
        self.base_topic = "OPEN-AIR/configuration/instrument/bandwidth"
        
        self.rbw_value = None 
        self.vbw_value = None 
        self.sweep_time_value = None
        
        self.rbw_preset_values = {} 
        self.vbw_preset_values = {} 
        
        self.rbw_preset_units = {}
        self.vbw_preset_units = {}
        
        self._locked_state = {
            f"{self.base_topic}/Settings/fields/Resolution Bandwidth/fields/RBW/value": False,
            f"{self.base_topic}/Settings/fields/Sweep_time_s/value": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/vbw_MHz/value": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/ON/selected": False,
            f"{self.base_topic}/Settings/fields/Video Bandwidth/fields/VBW_Automatic/options/OFF/selected": False,
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Continuous/selected": False, 
            f"{self.base_topic}/Settings/fields/Sweep_Mode/options/Single/selected": False, 
        }

    UNIT_MULTIPLIERS = {
        "HZ": 1, "KHZ": 1000, "MHZ": 1000000, "GHZ": 1000000000,
        "S": 1, "MS": 0.001, "US": 0.000001
    }

    def get_multiplier(self, unit_string: str) -> float:
        clean_unit = unit_string.strip().upper()
        return self.UNIT_MULTIPLIERS.get(clean_unit, 1.0)
