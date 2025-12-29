# display/gui_generic_wrapper.py
#
# A plug-and-play GUI wrapper that dynamically resolves its config. 
# Decoupled from MQTT requirements for initial render to prevent stalling.
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
# Version 20251226.23580.1

import os
import pathlib
import orjson
import tkinter as tk
from tkinter import ttk
import inspect

# --- Protocol: Integration Layer ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.logger.logger import  debug_logger
from workers.setup.config_reader import Config # Import the Config class
app_constants = Config.get_instance() # Get the singleton instance
from workers.utils.log_utils import _get_log_args 

# --- Protocol: Global Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Fully Dynamic Resolution ---
current_path = pathlib.Path(__file__).resolve()
JSON_CONFIG_FILE = current_path.with_suffix('.json') 

# Automatically turns 'gui_yak_bandwidth' into 'OPEN-AIR/yak/bandwidth'
module_name = current_path.stem.replace('gui_', '')
# Automatically turns 'gui_yak_bandwidth' into 'OPEN-AIR/yak/bandwidth'
module_name = current_path.stem.replace('gui_', '')
## MQTT_TOPIC_FILTER = f"OPEN-AIR/{module_name.replace('_', '/')}"

#class GhostMqtt:
#    """A harmless 'Mad Scientist' placeholder to satisfy legacy builder checks."""
 #   def add_subscriber(self, *args, **kwargs): pass
 #   def publish(self, *args, **kwargs): pass

class GenericInstrumentGui(ttk.Frame):
    """
    A generic container that instantiates a DynamicGuiBuilder based on its own filename.
    Designed to render even if network utilities (MQTT) are disabled or missing.
    """
    def __init__(self, parent, *args, **kwargs):
        # Protocol 2.7: Display the entire file.
        # Consume 'config' and other non-standard keys passed by the orchestrator 
        config = kwargs.pop('config', {}) # Ensure config is always a dict
        
        super().__init__(parent, *args, **kwargs)
        current_function_name = inspect.currentframe().f_code.co_name
        self.current_class_name = self.__class__.__name__

        # Extract state_mirror_engine and subscriber_router from the config dictionary
        self.state_mirror_engine = config.get('state_mirror_engine')
        self.subscriber_router = config.get('subscriber_router')
        self.config_data = config # Store the full config for later use if needed

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🖥️🟢 SUMMONING: Preparing to build the GUI for '{module_name}'",
                **_get_log_args()
            )

        # Immediate visual feedback in the GUI
        self.status_label = ttk.Label(self, text=f"Initializing {module_name}...", font=("Arial", 10, "italic"))
        self.status_label.pack(pady=20)

        try:
            # --- Pre-Flight Path Check ---
            abs_json_path = JSON_CONFIG_FILE.absolute()
            
            if not abs_json_path.exists():
                error_msg = f"🟡 WARNING: Sacred Scroll missing at {abs_json_path}"
                debug_logger(
                    message=error_msg,
                    **_get_log_args()
                )
                self.status_label.config(text=error_msg, foreground="orange")
                return

            # --- YAK-SPECIFIC STRUCTURE NORMALIZATION ---
            # If the JSON doesn't contain 'OcaBlock' at the root, we wrap the whole thing 
            # in a Virtual Block so the builder knows to drill down.
            with open(abs_json_path, 'r') as f:
                raw_data = orjson.loads(f.read())
            
            # Check if root keys are widgets or if it's an 'Anonymous' block structure
            needs_wrapping = True
            for k, v in raw_data.items():
                if isinstance(v, dict) and (v.get("type") == "OcaBlock" or v.get("type", "").startswith("_")):
                    needs_wrapping = False
                    break
            
            processed_path = str(abs_json_path)
            
            if needs_wrapping:
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(
                        message=f"🖥️🔍 NORMALIZING: Wrapping JSON structure for {module_name}",
                        **_get_log_args()
                    )
                # Create a temporary normalized file
                temp_path = abs_json_path.parent / f"temp_norm_{abs_json_path.name}"
                norm_data = {
                    "Generic_Display_Block": { # Generic name for the wrapper block
                        "type": "OcaBlock",
                        "description": f"Dynamic Content for {module_name}",
                        "fields": raw_data
                    }
                }
                with open(temp_path, 'w') as tf:
                    orjson.dump(norm_data, tf, indent=4)
                processed_path = str(temp_path)
            
            ## If mqtt_util is None because it was shut off in the orchestrator, 
            ## we provide the GhostMqtt to prevent the DynamicGuiBuilder from returning early.
            #effective_mqtt = mqtt_util if mqtt_util is not None else GhostMqtt()

            # --- Presentation Layer ---
            # Instantiate the builder.
            #print(f"DEBUG: [Hand-off] Passing control to DynamicGuiBuilder for {module_name}")
            
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=processed_path,
                config=self.config_data # Pass the full config dictionary here
            )
            
            # If we reach here, the builder at least started.
            self.status_label.destroy()


        except Exception as e:
            error_msg = f"❌ CRITICAL FAILURE in Wrapper: {e}"
            
            self.status_label.config(text=error_msg, foreground="red")
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"🖥️🔴 Great Scott! The wrapper has failed to contain the builder! {e}",
                    **_get_log_args()
                )

    def _on_tab_selected(self, *args, **kwargs):
        """
        Called by the grand orchestrator (Application) when this tab is brought to focus.
        Using *args to swallow any positional events or data passed by the orchestrator.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🖥️🔵 Tab '{module_name}' activated! Stand back, I'm checking the data flow!",
                **_get_log_args()
            )
        
        # Add logic here if specific refresh actions are needed on tab focus
        pass