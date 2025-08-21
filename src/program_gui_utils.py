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
# Version 20250821.145000.1
# FIXED: Re-added the missing create_app_menu function to resolve the ImportError.

import os
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime

# Import logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import other components
from src.TABS_PARENT import TABS_PARENT
from display.DISPLAY_PARENT import DISPLAY_PARENT

# Import styling functions
from src.program_style import apply_styles

# CORRECTED: The original import path was incorrect. Now correctly importing from
# the central file path module.
from ref.ref_file_paths import DATA_FOLDER_PATH, CONFIG_FILE_PATH

# --- Version Information ---
current_version = "20250821.145000.1"
current_version_hash = 20250821 * 145000 * 1
current_file = f"{os.path.basename(__file__)}"


def create_main_layout_and_widgets(app_instance, style_obj):
    """
    Creates the main two-pane layout of the application.
    
    Args:
        app_instance: The main application instance.
        style_obj: The Tkinter style object for applying styles.
        
    Returns:
        tuple: A tuple containing the PanedWindow, the tabs parent frame, and the display parent frame.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
              file=current_file, version=current_version, function=current_function)
    
    try:
        main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill="both", expand=True)

        tabs_parent = TABS_PARENT(main_paned_window, app_instance, style_obj)
        tabs_parent.pack(fill="both", expand=True)

        display_parent = DISPLAY_PARENT(main_paned_window, app_instance, style_obj)
        display_parent.pack(fill="both", expand=True)

        # Ensure widgets are added as children of the PanedWindow
        main_paned_window.add(tabs_parent)
        main_paned_window.add(display_parent)

        debug_log(f"⚙️ ✅ Exiting {current_function}",
                  file=current_file, version=current_version, function=current_function)
        
        return main_paned_window, tabs_parent, display_parent
    
    except Exception as e:
        debug_log(f"❌ Error creating main layout: {e}",
                  file=current_file, version=current_version, function=current_function)
        raise

def create_app_menu(app_instance):
    """
    Creates the application's menu bar.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to create the app menu. 📋",
              file=current_file, version=current_version, function=current_function)
    
    menu_bar = tk.Menu(app_instance)
    app_instance.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Exit", command=app_instance.on_closing)

    debug_log(f"⚙️ ✅ Exiting {current_function}",
              file=current_file, version=current_version, function=current_function)
              
def apply_saved_geometry(app_instance):
    """
    Applies the last saved window geometry and state from the config file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
              file=current_file, version=current_version, function=current_function)
    
    try:
        # Load window geometry
        if app_instance.program_config and app_instance.program_config.has_option('Application', 'geometry'):
            geometry = app_instance.program_config.get('Application', 'geometry')
            app_instance.geometry(geometry)
            debug_log(f"✅ Applied saved geometry: {geometry}",
                      file=current_file, version=current_version, function=current_function)
        
        # Load window state (zoomed, etc.)
        if app_instance.program_config and app_instance.program_config.has_option('Application', 'window_state'):
            window_state = app_instance.program_config.get('Application', 'window_state')
            if window_state:
                app_instance.state(window_state)
                debug_log(f"✅ Applied saved window state: {window_state}",
                          file=current_file, version=current_version, function=current_function)
                          
        debug_log(f"⚙️ ✅ Exiting {current_function}",
                  file=current_file, version=current_version, function=current_function)
    
    except Exception as e:
        debug_log(f"❌ Error applying saved geometry. Arrr, the code be capsized! The error be: {e}",
                  file=current_file, version=current_version, function=current_function)
        raise