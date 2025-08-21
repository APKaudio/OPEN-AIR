# src/program_gui_utils.py
#
# This file provides utility functions for creating and managing the main application GUI layout,
# including the main window layout, the tab container, and other top-level widgets.
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
#
# Version 20250821.124500.2
# REFACTORED: The sash position logic was removed from this file to be handled by the main application instance at the correct time.

import os
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime

# Import logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import other components
from .TABS_PARENT import TABS_PARENT
from display.DISPLAY_PARENT import DISPLAY_PARENT

# Import styling functions
from src.program_style import apply_styles

# --- Version Information ---
current_version = "20250821.124500.2"
current_version_hash = (20250821 * 124500 * 2)
current_file = f"{os.path.basename(__file__)}"


def create_main_layout_and_widgets(app_instance, orchestrator):
    """
    Creates the main two-pane layout, with the left pane for tabs and the right for display.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
              file=current_file, version=current_version, function=current_function)
              
    try:
        app_instance.orchestrator = orchestrator

        # Create the main paned window
        app_instance.paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
        app_instance.paned_window.grid(row=0, column=0, sticky="nsew")

        # Configure the main window grid
        app_instance.grid_rowconfigure(0, weight=1)
        app_instance.grid_columnconfigure(0, weight=1)

        # Create the left and right frames for the panes
        left_frame = ttk.Frame(app_instance.paned_window, style="PrimaryContainer.TFrame")
        right_frame = ttk.Frame(app_instance.paned_window, style="PrimaryContainer.TFrame")

        # Add the frames to the paned window
        app_instance.paned_window.add(left_frame, weight=3)
        app_instance.paned_window.add(right_frame, weight=7)
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Create and place the TABS_PARENT and DISPLAY_PARENT components
        app_instance.tabs_parent = TABS_PARENT(left_frame, app_instance, app_instance.style_obj)
        app_instance.tabs_parent.grid(row=0, column=0, sticky="nsew")

        app_instance.display_parent_tab = DISPLAY_PARENT(right_frame, app_instance, app_instance.style_obj)
        app_instance.display_parent_tab.grid(row=0, column=0, sticky="nsew")
        
        # Apply the geometry settings after the widgets are created
        # This will load the sash position from the config, but not apply it yet.
        # It's necessary for the orchestrator to have access to the config values.
        apply_saved_geometry(app_instance)

        # Set the parent notebook for the display pane's children
        app_instance.display_parent_tab.set_parent_notebook(app_instance.display_parent_tab.notebook)
        
        console_log("✅ All main GUI widgets created successfully!")
        debug_log(f"⚙️ ✅ Exiting {current_function}. GUI is built and ready.",
                  file=current_file, version=current_version, function=current_function)

    except Exception as e:
        console_log(f"❌ Error creating main layout: {e}")
        debug_log(f"❌ Failed to create main layout. Arrr, the code be capsized! The error be: {e}",
                  file=current_file, version=current_version, function=current_function)
        
def apply_saved_geometry(app_instance):
    """
    Applies the saved window geometry and state from the config file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
              file=current_file, version=current_version, function=current_function)
    
    try:
        # Load window geometry
        if app_instance.config and app_instance.config.has_option('Application', 'geometry'):
            geometry = app_instance.config.get('Application', 'geometry')
            app_instance.geometry(geometry)
            debug_log(f"✅ Applied saved geometry: {geometry}",
                      file=current_file, version=current_version, function=current_function)
        
        # Load window state (zoomed, etc.)
        if app_instance.config and app_instance.config.has_option('Application', 'window_state'):
            window_state = app_instance.config.get('Application', 'window_state')
            if window_state:
                app_instance.state(window_state)
                debug_log(f"✅ Applied saved window state: {window_state}",
                          file=current_file, version=current_version, function=current_function)
                          
        debug_log(f"⚙️ ✅ Exiting {current_function}",
                  file=current_file, version=current_version, function=current_function)
    
    except Exception as e:
        debug_log(f"❌ Error applying saved geometry. Arrr, the code be capsized! The error be: {e}",
                  file=current_file, version=current_version, function=current_function)