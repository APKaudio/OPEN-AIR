# managers/Visa_Fleet_Manager/manager_visa_dynamic_drivers.py
#
# Provides base and specialized driver classes for managing different types of VISA instruments.
#
# Author: Gemini Agent
#

import orjson
import re
import time
from workers.setup.config_reader import Config
app_constants = Config.get_instance()

from workers.logger.logger import  debug_logger
from workers.logger.log_utils import _get_log_args

# Assume VisaProxyFleet is available for communication
# In a real project, this would be imported from the same package or a shared utility.
# For this example, we'll assume it's accessible.
# from .visa_proxy_fleet import VisaProxyFleet 

class InstrumentDriverError(Exception):
    """Custom exception for instrument driver related errors."""
    pass

class GenericInstrumentDriver:
    """
    A base class for all instrument drivers.
    Provides common methods like *IDN? and *RST, and a generic command interface.
    """
    def __init__(self, visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn):
        self.proxy = visa_proxy_fleet
        self.device_serial = device_serial
        self.instrument_model = instrument_model
        self.manufacturer = manufacturer
        self.idn_string = instrument_idn
        
        debug_logger(
            message=f"💳 🟢️️️🟢 Initialized GenericInstrumentDriver for {self.device_serial} ({self.instrument_model}).",
            **_get_log_args()
        )

    def idn(self):
        """Queries the instrument for its identification string (*IDN?)."""
        try:
            response = self.proxy.query("*IDN?")
            if response:
                return response
            else:
                raise InstrumentDriverError("Received empty response for *IDN?")
        except Exception as e:
            raise InstrumentDriverError(f"Failed to query *IDN? for {self.device_serial}: {e}")

    def reset(self):
        """Sends the *RST SCPI command to reset the instrument."""
        try:
            success = self.proxy.write("*RST")
            if success:
                return True
            else:
                raise InstrumentDriverError(f"Reset command (*RST) failed for {self.device_serial}.")
        except Exception as e:
            raise InstrumentDriverError(f"Failed to send *RST for {self.device_serial}: {e}")

    def send_command(self, command, query=False, correlation_id=None):
        """
        Sends a raw SCPI command to the instrument.
        :param command: The SCPI command string.
        :param query: Boolean, True if this is a query command.
        :param correlation_id: Optional correlation ID for tracking responses.
        :return: The response string if query is True, otherwise True for success.
        """
        try:
            if query:
                response = self.proxy.query(command, correlation_id=correlation_id if correlation_id else f"{self.device_serial}-{int(time.time())}")
                return response
            else:
                success = self.proxy.write(command)
                return success
        except Exception as e:
            raise InstrumentDriverError(f"Failed to send raw command '{command}' to {self.device_serial}: {e}")

    def get_status(self):
        """Placeholder for getting general instrument status."""
        debug_logger(f"GenericInstrumentDriver does not implement get_status for {self.device_serial}.")
        return "Status: Not Implemented"

    def get_device_serial(self):
        """Returns the device serial number used for MQTT topic identification."""
        return self.device_serial

    def get_instrument_model(self):
        """Returns the instrument model string."""
        return self.instrument_model
        
    def get_manufacturer(self):
        """Returns the instrument manufacturer string."""
        return self.manufacturer

    def get_idn_string(self):
        """Returns the full *IDN? string."""
        return self.idn_string

# --- Example Specialized Drivers ---

class TektronixScopeDriver(GenericInstrumentDriver):
    """
    Driver for Tektronix oscilloscopes.
    """
    def __init__(self, visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn):
        super().__init__(visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn)
        debug_logger(
            message=f"💳 🟢️️️🟢 Initialized TektronixScopeDriver for {self.device_serial}.",
            **_get_log_args()
        )

    def autoset_execute(self):
        """Performs an AutoSet operation on the oscilloscope."""
        try:
            success = self.proxy.write("AUTOSET EXECUTE")
            if success:
                debug_logger(f"TektronixScopeDriver ({self.device_serial}): Autoset executed successfully.", **_get_log_args())
                return True
            else:
                raise InstrumentDriverError(f"Autoset EXECUTE command failed for Tektronix scope {self.device_serial}.")
        except Exception as e:
            raise InstrumentDriverError(f"Failed to execute autoset for Tektronix scope {self.device_serial}: {e}")

    def set_waveform_source(self, channel):
        """Sets the waveform source channel (e.g., 'CH1', 'CH2')."""
        if not isinstance(channel, int) or not 1 <= channel <= 4: # Assuming channels 1-4
            raise ValueError("Invalid channel number. Must be between 1 and 4.")
        
        try:
            success = self.proxy.write(f"DAT:SOU CH{channel}")
            if success:
                debug_logger(f"TektronixScopeDriver ({self.device_serial}): Waveform source set to CH{channel}.", **_get_log_args())
                return True
            else:
                raise InstrumentDriverError(f"Failed to set waveform source to CH{channel} for {self.device_serial}.")
        except Exception as e:
            raise InstrumentDriverError(f"Failed to set waveform source for Tektronix scope {self.device_serial}: {e}")

    def get_waveform_data(self, channel=1):
        """Retrieves waveform data from the specified channel."""
        self.set_waveform_source(channel) # Ensure source is set
        try:
            waveform_data = self.proxy.query("CURV?")
            return waveform_data
        except Exception as e:
            raise InstrumentDriverError(f"Failed to get waveform data from CH{channel} for Tektronix scope {self.device_serial}: {e}")

class KeithleyDMMDriver(GenericInstrumentDriver):
    """
    Driver for Keithley DMMs (Digital Multimeters).
    """
    def __init__(self, visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn):
        super().__init__(visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn)
        debug_logger(
            message=f"💳 🟢️️️🟢 Initialized KeithleyDMMDriver for {self.device_serial}.",
            **_get_log_args()
        )

    def set_measurement_function(self, function_type):
        """
        Sets the measurement function (e.g., 'VOLT:DC', 'CURR:DC', 'RES').
        Example functions: VOLT:DC, CURR:DC, RES, VOLT:AC, CURR:AC, FREQ, TEMP
        """
        valid_functions = ["VOLT:DC", "CURR:DC", "RES", "VOLT:AC", "CURR:AC", "FREQ", "TEMP"]
        # Keithley SCPI commands often use SENSE/<function>/<subsystem>
        # This is a simplified example, actual commands may vary by model.
        base_scpi_command = f"SENS:{function_type.upper()}"
        
        if function_type.upper() not in valid_functions:
            raise ValueError(f"Invalid measurement function type: {function_type}. Supported: {', '.join(valid_functions)}")
        
        try:
            # Attempt to write a command that configures the function, might need more specific SCPI
            # For example, for DC Voltage on a 2000 series Keithley, it might be 'SENS:VOLT:DC:RANG 10' or similar.
            # For simplicity, we'll just send a generic setup command.
            # A more robust driver would query the instrument for supported functions/ranges.
            success = self.proxy.write(base_scpi_command) # This is a placeholder, actual commands vary.
            if success:
                debug_logger(f"KeithleyDMMDriver ({self.device_serial}): Measurement function set to {function_type.upper()} (via command: {base_scpi_command}).", **_get_log_args())
                return True
            else:
                raise InstrumentDriverError(f"Failed to set measurement function to {function_type.upper()} for DMM {self.device_serial}.")
        except Exception as e:
            raise InstrumentDriverError(f"Failed to set measurement function for Keithley DMM {self.device_serial}: {e}")

    def measure_voltage_dc(self):
        """Initiates a DC Voltage measurement."""
        # This assumes set_measurement_function is called implicitly or is handled by the query command itself.
        # A more robust implementation would explicitly set the function first.
        try:
            # Some DMMs combine function setting and measurement query
            # Example: MEAS:VOLT:DC?
            response = self.proxy.query("MEAS:VOLT:DC?") 
            return response
        except Exception as e:
            raise InstrumentDriverError(f"Failed to measure DC voltage for Keithley DMM {self.device_serial}: {e}")

    def measure_resistance(self):
        """Initiates a Resistance measurement."""
        try:
            # Example: MEAS:RES?
            response = self.proxy.query("MEAS:RES?")
            return response
        except Exception as e:
            raise InstrumentDriverError(f"Failed to measure resistance for Keithley DMM {self.device_serial}: {e}")

# --- Driver Factory ---

class InstrumentDriverFactory:
    """
    Factory class to create the appropriate instrument driver based on IDN information.
    """
    def __init__(self):
        pass # No initialization needed for this simple factory

    def create_driver(self, visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn):
        """
        Creates an instrument driver instance based on manufacturer and model.
        :param visa_proxy_fleet: The VisaProxyFleet instance for communication.
        :param device_serial: The unique serial number of the device (or resource name fallback).
        :param instrument_model: The parsed instrument model string.
        :param manufacturer: The parsed manufacturer string.
        :param instrument_idn: The full *IDN? response string.
        :return: An instance of a specific InstrumentDriver or GenericInstrumentDriver.
        """
        debug_logger(
            message=f" driver_factory: Attempting to create driver for {device_serial} "
                    f"(Model: {instrument_model}, Manufacturer: {manufacturer}).",
            **_get_log_args()
        )

        # --- Add your driver detection logic here ---
        # This is where you map manufacturer/model to specific driver classes.

        if "TEKTRONIX" in manufacturer.upper():
            if "TDS" in instrument_model.upper(): # Example for Tektronix TDS series
                return TektronixScopeDriver(visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn)
        
        elif "KEITHLEY" in manufacturer.upper():
            # More specific model checks could be added here if needed
            return KeithleyDMMDriver(visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn)
            
        # Fallback to generic driver if no specific match is found
        else:
            debug_logger(
                message=f" driver_factory: No specific driver found for {manufacturer} {instrument_model} ({device_serial}). "
                        f"Falling back to GenericInstrumentDriver.",
                **_get_log_args()
            )
            return GenericInstrumentDriver(visa_proxy_fleet, device_serial, instrument_model, manufacturer, instrument_idn)

# --- Helper function to parse *IDN? string ---
def parse_idn_string(idn_string):
    """
    Parses the standard *IDN? string into components.
    Expected format: MANUFACTURER,MODEL,SERIALNUMBER,FIRMWARE_VERSION
    Returns a dictionary with keys: manufacturer, model, serial_number, firmware.
    Returns None for any component if not found.
    """
    if not idn_string:
        return {
            "manufacturer": None,
            "model": None,
            "serial_number": None,
            "firmware": None
        }
        
    parts = idn_string.strip().split(',')
    
    manufacturer = parts[0].strip() if len(parts) >= 1 and parts[0].strip() else None
    model = parts[1].strip() if len(parts) >= 2 and parts[1].strip() else None
    serial_number = parts[2].strip() if len(parts) >= 3 and parts[2].strip() else None
    firmware = parts[3].strip() if len(parts) >= 4 and parts[3].strip() else None
    
    # Basic cleanup for empty strings that might result from extra commas
    return {
        "manufacturer": manufacturer if manufacturer else None,
        "model": model if model else None,
        "serial_number": serial_number if serial_number else None,
        "firmware": firmware if firmware else None
    }