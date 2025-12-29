# display/right_50/top_10/gui_start_pause_stop.py
#
# A GUI frame that uses the DynamicGuiBuilder to create widgets for frequency settings.
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
# Version: 20251229.1622.1

import os
import inspect
import tkinter as tk
from tkinter import ttk
import pathlib

# --- Module Imports ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.logger.logger import debug_logger
# Use the global log args helper if available, or fall back to local if needed
from workers.utils.log_utils import _get_log_args 
from workers.setup.config_reader import Config # Import the Config class

# Globals
app_constants = Config.get_instance() # Get the singleton instance
current_version = "20251229.1622.1"
current_version_hash = 32806990980 # 20251229 * 1622 * 1

# --- Global Scope Variables ---
current_file_path = pathlib.Path(__file__).resolve()
project_root = current_file_path.parent.parent.parent.parent.parent # Adjusted for depth (display/right_50/top_10/file.py)
# Note: Adjust parent count above if project root detection is off, or use app_constants.PROJECT_ROOT if available.
JSON_CONFIG_FILE = current_file_path.with_suffix('.json')

class StartPauseStopGui(ttk.Frame):
    """
    A GUI component for Start/Pause/Stop functionality, instantiating DynamicGuiBuilder.
    """
    def __init__(self, parent, json_path, config, **kwargs): 
        """
        Initializes the Frequency frame and the dynamic GUI builder.
        
        Args:
            parent: The parent widget.
            json_path (str): The path to the JSON configuration file (passed by ModuleLoader).
            config (dict): The configuration dictionary (passed by ModuleLoader).
            **kwargs: Additional keyword arguments for the Frame.
        """
        # 1. Initialize the Parent Frame (Cleanly!)
        super().__init__(parent, **kwargs)

        # 2. Absorb the Arguments (Do not let them hit the superclass!)
        self.json_path = json_path
        self.config_data = config

        # Explicitly extract state_mirror_engine and subscriber_router from config
        self.state_mirror_engine = config.get('state_mirror_engine')
        self.subscriber_router = config.get('subscriber_router')
        
        # --- Dynamic GUI Builder ---
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 Great Scott! Entering '{current_function_name}'! Initializing StartPauseStopGui with json: {self.json_path}",
                **_get_log_args()
            )
        
        try:
            # 3. Construct the GUI
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=self.json_path, # Use the path passed in, or default to global
                config=self.config_data 
            )
            
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message="✅ It works! It works! The StartPauseStopGui dynamic builder is alive!",
                    **_get_log_args()
                )

        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ ERROR! The bridge is out! '{current_function_name}' crashed! Exception: {e}",
                    **_get_log_args()
                )
            # Re-raise or handle gracefully depending on policy? 
            # For now, we log the scream and let the UI show the error via ModuleLoader if it propagates.
            raise e