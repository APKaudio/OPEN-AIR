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
# Version 20250821.105800.1 (FIXED: Removed the redundant theme_use call to prevent TclError.)

import os
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime

# Import logging functions
from display.debug_logic import debug_log
from display.console_logic import console_log

# Import other components
from tabs.TABS_PARENT import TABS_PARENT
from display.DISPLAY_PARENT import DISPLAY_PARENT

# Import styling functions
from src.program_style import apply_styles

# --- Version Information ---
current_version = "20250821.105800.1"
current_version_hash = (20250821 * 105800 * 1)
current_file = f"{os.path.basename(__file__)}"


def apply_saved_geometry(app_instance):
    """
    Applies the last-used window geometry and state from the config file.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
                file=current_file, version=current_version, function=current_function)
    
    config = app_instance.config
    geometry = config.get('Application', 'geometry', fallback=None)
    window_state = config.get('Application', 'window_state', fallback='normal')

    if geometry:
        try:
            app_instance.geometry(geometry)
            debug_log(f"✅ Applied saved geometry: {geometry}",
                        file=current_file, version=current_version, function=current_function)
        except tk.TclError:
            debug_log(f"❌ Failed to apply saved geometry: {geometry}. Invalid format.",
                        file=current_file, version=current_version, function=current_function)
    
    if window_state == 'zoomed':
        app_instance.state('zoomed')
        debug_log(f"✅ Applied saved window state: {window_state}",
                    file=current_file, version=current_version, function=current_function)
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file, version=current_version, function=current_function)


def create_main_layout_and_widgets(app_instance, orchestrator_logic):
    """
    Creates the main UI layout and widgets for the application.
    This function should be called after program initialization is complete.
    
    Args:
        app_instance (tk.Tk): The main application instance.
        orchestrator_logic: The instance of the OrchestratorLogic.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function}",
                file=current_file, version=current_version, function=current_function)
    
    try:
        # Create a style object and apply the theme from the config
        app_instance.style_obj = ttk.Style(app_instance)
        
        # Main window layout
        app_instance.rowconfigure(0, weight=1)
        app_instance.columnconfigure(0, weight=1)

        # Create a PanedWindow to hold the left and right panes
        paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
        paned_window.grid(row=0, column=0, sticky="nsew")

        # Left pane for the tabs
        left_frame = ttk.Frame(paned_window, style='TFrame')
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        paned_window.add(left_frame, weight=1)
        
        # Right pane for the display and console
        right_frame = ttk.Frame(paned_window, style='TFrame')
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        paned_window.add(right_frame, weight=1)

        # Initialize the tabs and display panes
        app_instance.tabs_parent = TABS_PARENT(left_frame, app_instance, app_instance.style_obj)
        app_instance.tabs_parent.grid(row=0, column=0, sticky="nsew")

        app_instance.display_parent_tab = DISPLAY_PARENT(right_frame, app_instance, app_instance.style_obj)
        app_instance.display_parent_tab.grid(row=0, column=0, sticky="nsew")

        # Set the sash position
        sash_position_percentage = int(app_instance.config.get('Application', 'paned_window_sash_position_percentage', fallback='45'))
        paned_window.sashpos(0, (app_instance.winfo_width() * sash_position_percentage) // 100)

        # Apply the geometry settings after the widgets are created
        apply_saved_geometry(app_instance)

        # Set the parent notebook for the display pane's children
        app_instance.display_parent_tab.set_parent_notebook(app_instance.display_parent_tab.notebook)
        
        # REMOVED: This is a duplicate call and causes the TclError
        # app_instance.style_obj.theme_use(app_instance.current_style_theme_var.get())

    except Exception as e:
        console_log(f"❌ Error creating main layout: {e}")
        debug_log(f"❌ Failed to create main layout. Error: {e}",
                  file=current_file, version=current_version, function=current_function)
        raise

    debug_log(f"⚙️ ✅ Exiting {current_function}. GUI is built and ready.",
                file=current_file, version=current_version, function=current_function)