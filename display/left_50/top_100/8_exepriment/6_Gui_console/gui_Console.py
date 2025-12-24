# display/gui_Elements.py
# (Internal Name: gui_generic_wrapper.py)
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
# Version 20251223.195000.2

import os
import pathlib
import json
import tkinter as tk
from tkinter import ttk
import inspect

# --- Protocol: Integration Layer ---
from workers.builder.dynamic_gui_builder import DynamicGuiBuilder
from workers.logger.logger import debug_log
import workers.setup.app_constants as app_constants
from workers.utils.log_utils import _get_log_args 

# --- Protocol: Global Variables ---
current_version = "20251223.195000.2"
current_version_hash = 20251223195000
current_file = f"{os.path.basename(__file__)}"

# --- Fully Dynamic Resolution ---
current_path = pathlib.Path(__file__).resolve()
JSON_CONFIG_FILE = current_path.with_suffix('.json') 

# Automatically turns 'gui_yak_bandwidth' into 'OPEN-AIR/yak/bandwidth'
module_name = current_path.stem.replace('gui_', '')

class GhostMqtt:
    """
    🧪 A harmless 'Mad Scientist' placeholder to satisfy legacy builder checks.
    It absorbs signals like a temporal sink!
    """
    def add_subscriber(self, *args, **kwargs): 
        pass
    def publish(self, *args, **kwargs): 
        pass

class GenericInstrumentGui(ttk.Frame):
    """
    A generic container that instantiates a DynamicGuiBuilder based on its own filename.
    Designed to render even if network utilities (MQTT) are disabled or missing.
    """
    def __init__(self, parent, config=None, *args, **kwargs):
        # Protocol 2.7: Display the entire file.
        # Consume 'config' and other non-standard keys to prevent tk error
        super().__init__(parent, **kwargs)
        
        # 1. Debug Entry
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🧪 Great Scott! Initializing GenericInstrumentGui for '{module_name}'! Spinning up the turbines...",
                **_get_log_args()
            )

        # 2. Status Label (The 'Loading...' Indicator)
        self.status_label = ttk.Label(self, text=f"⏳ Constructing {module_name}...", foreground="blue")
        self.status_label.pack(pady=20, padx=20)

        # 3. Geometry Configuration (CRITICAL FIX!)
        # We must tell this frame to let its children EXPAND!
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        try:
            # 4. Determine Config Path
            processed_path = JSON_CONFIG_FILE
            
            if not processed_path.exists():
                raise FileNotFoundError(f"The sacred scrolls are missing! Cannot find: {processed_path}")

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🖥️📂 Reading the sacred scrolls at {processed_path}",
                    **_get_log_args()
                )

            # 5. Ignite the Builder
            # We pass 'self' as the parent. The builder typically creates a Canvas/Frame inside 'self'.
            self.dynamic_gui = DynamicGuiBuilder(
                parent=self,
                json_path=processed_path
            )
            
            # The Builder usually packs/grids itself, but if it doesn't, we ensure it fills the void here:
            # Note: DynamicGuiBuilder usually handles its own packing, but relying on 
            # the parent's grid configuration (step 3) is key.
            
            # 6. Success! Destroy the loading label.
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ It works! It works! The DynamicGuiBuilder has completed its task for {module_name}!",
                    **_get_log_args()
                )
            
            self.status_label.destroy()

        except Exception as e:
            # 7. Error Handling (The Bridge is Out!)
            error_msg = f"❌ CRITICAL FAILURE in Wrapper: {e}"
            self.status_label.config(text=error_msg, foreground="red")
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🏴‍☠️💥 Great Scott! The wrapper has failed to contain the builder! Error: {e}",
                    **_get_log_args()
                )

    def _on_tab_selected(self, *args, **kwargs):
        """
        Called by the grand orchestrator (Application) when this tab is brought to focus.
        Using *args to swallow any positional events or data passed by the orchestrator.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️🔵 Tab '{module_name}' activated! Stand back, I'm checking the data flow!",
                **_get_log_args()
            )
        
        # Add logic here if specific refresh actions are needed on tab focus
        pass