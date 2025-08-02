# tabs/Instrument/utils_instrument_connection.py
#
# This module provides low-level functions specifically for managing VISA instrument
# connections: listing available resources, connecting to an instrument, and
# disconnecting from an instrument. It abstracts the direct PyVISA communication
# details related to connection management from higher-level application logic.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250802.1701.5 (Refactored from utils_instrument_control.py to handle connection logic.)

current_version = "20250802.1701.5" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 1701 * 5 # Example hash, adjust as needed

import pyvisa
import inspect # Import inspect module
import os # Import os module to fix NameError

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

def list_visa_resources(console_print_func=None, *args, **kwargs):
    """
    Function Description:
    Lists available VISA resources (instruments).

    Inputs to this function:
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.
    - *args: Catches any unexpected positional arguments.
    - **kwargs: Catches any unexpected keyword arguments.

    Process of this function:
    1. Initializes PyVISA ResourceManager.
    2. Logs any unexpected arguments received.
    3. Lists available resources.
    4. Logs the discovered resources or any errors.

    Outputs of this function:
    - list: A list of strings, where each string is a VISA resource name.
            Returns an empty list if no resources are found or an error occurs.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Listing VISA resources... Let's find some devices!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    if args or kwargs:
        debug_log(f"WARNING: list_visa_resources received unexpected arguments! Args: {args}, Kwargs: {kwargs}. What the hell are these?!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        console_print_func(f"⚠️ Warning: list_visa_resources received unexpected arguments! This might be the source of the problem. Check the call!")

    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        debug_log(f"Found VISA resources: {resources}. Success!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return list(resources)
    except Exception as e:
        error_msg = f"❌ Error listing VISA resources: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return []


def connect_to_instrument(resource_name, console_print_func=None):
    """
    Function Description:
    Establishes a connection to a VISA instrument.

    Inputs to this function:
    - resource_name (str): The VISA resource string (e.g., "GPIB0::1::INSTR").
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Initializes PyVISA ResourceManager.
    2. Opens the specified resource.
    3. Sets instrument timeout, read/write termination characters, and query delay.
    4. Logs connection status.

    Outputs of this function:
    - pyvisa.resources.Resource or None: The connected PyVISA instrument object if successful,
                                         None otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Connecting to instrument: {resource_name}. Fingers crossed!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource_name)
        inst.timeout = 10000 # Set a timeout (milliseconds) - Increased for robustness
        inst.read_termination = '\n' # Set read termination character
        inst.write_termination = '\n' # Set write termination character
        inst.query_delay = 0.1 # Small delay between write and read for query
        console_print_func(f"✅ Successfully connected to {resource_name}. It's alive!")
        debug_log(f"Connection successful to {resource_name}. We're in!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return inst
    except pyvisa.errors.VisaIOError as e:
        error_msg = f"❌ VISA error connecting to {resource_name}: {e}. This is a nightmare!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None
    except Exception as e:
        error_msg = f"❌ An unexpected error occurred while connecting to {resource_name}: {e}. What a mess!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        return None


def disconnect_instrument(inst, console_print_func=None):
    """
    Function Description:
    Closes the connection to a VISA instrument.

    Inputs to this function:
    - inst (pyvisa.resources.Resource): The PyVISA instrument object to disconnect.
    - console_print_func (function, optional): Function to print messages to the GUI console.
                                               Defaults to console_log if None.

    Process of this function:
    1. Checks if the instrument object is valid.
    2. Attempts to close the instrument connection.
    3. Logs disconnection status.

    Outputs of this function:
    - bool: True if disconnection is successful, False otherwise.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Disconnecting instrument... Saying goodbye!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    if inst:
        try:
            inst.close()
            console_print_func("✅ Instrument disconnected. See ya!")
            debug_log("Instrument connection closed. All done!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return True
        except pyvisa.errors.VisaIOError as e:
            error_msg = f"❌ VISA error disconnecting instrument: {e}. This thing is stuck!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
        except Exception as e:
            error_msg = f"❌ An unexpected error occurred while disconnecting instrument: {e}. What a pain!"
            console_print_func(error_msg)
            debug_log(error_msg,
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
            return False
    debug_log("No instrument to disconnect. Already gone!",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    return False
