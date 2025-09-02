# agents/agent_YaketyYak.py
#
# This agent provides a high-level API for executing different types of SCPI commands
# (GET, SET, DO, RIG, BEG). It acts as a bridge between the application's business logic
# and the low-level SCPI dispatcher.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250902.114500.1

import inspect

# Assume ScpiDispatcher is imported
from agents.agent_yak_dispatch_scpi import ScpiDispatcher

# --- Global Scope Variables ---
current_version = "20250902.114500.1"
current_version_hash = (20250902 * 114500 * 1)
current_file = f"{os.path.basename(__file__)}"

def YakBeg(dispatcher: ScpiDispatcher, command_type, console_print_func, *variable_values):
    """
    Executes a 'BEG' (Beg) VISA command and returns the response.
    """
    return dispatcher.dispatch_command(command_type, "BEG", *variable_values)

def YakRig(dispatcher: ScpiDispatcher, command_type, console_print_func, *variable_values):
    """
    Executes a 'RIG' VISA command for multi-parameter settings.
    """
    return dispatcher.dispatch_command(command_type, "RIG", *variable_values)

def YakDo(dispatcher: ScpiDispatcher, command_type, console_print_func):
    """
    Executes a 'DO' VISA command (a simple write without a response).
    """
    return dispatcher.dispatch_command(command_type, "DO")

def YakGet(dispatcher: ScpiDispatcher, command_type, console_print_func):
    """
    Executes a 'GET' VISA command and returns the response.
    """
    return dispatcher.dispatch_command(command_type, "GET")

def YakSet(dispatcher: ScpiDispatcher, command_type, variable_value, console_print_func):
    """
    Executes a 'SET' VISA command with a specific value.
    """
    return dispatcher.dispatch_command(command_type, "SET", variable_value)