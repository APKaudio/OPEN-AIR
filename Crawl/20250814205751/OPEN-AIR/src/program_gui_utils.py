# src/program_gui_utils.py
#
# This module is responsible for constructing the main graphical user interface (GUI)
# for the application. It creates the main window layout, including the paned window,
# and populates it with the main tab container and the display/control panes.
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
# Version 20250814.113100.1

current_version = "20250814.113100.1"
current_version_hash = (20250814 * 113100 * 1)

import tkinter as tk
from tkinter import ttk
import inspect
import os

# --- Import Parent Containers ---
from tabs.TABS_PARENT import TABS_PARENT
from display.DISPLAY_PARENT import TAB_DISPLAY_PARENT
from display.console_logic import console_log
from display.debug_logic import debug_log

def apply_saved_geometry(app_instance):
    # Applies the last saved window geometry and state.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Applying saved window geometry and state.",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
    try:
        last_geometry = app_instance.config.get('Application', 'geometry', fallback='1200x800+100+100')
        last_state = app_instance.config.get('Application', 'window_state', fallback='normal')
        app_instance.geometry(last_geometry)
        app_instance.state(last_state)
    except Exception as e:
        console_log(f"❌ Error applying saved geometry: {e}")


def create_main_layout_and_widgets(app_instance, orchestrator_logic):
    # Constructs the main GUI layout with a horizontal PanedWindow.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Creating main layout: Left (TABS_PARENT) and Right (TAB_DISPLAY_PARENT).",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

    main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    main_paned_window.pack(expand=True, fill='both')
    app_instance.paned_window = main_paned_window

    # --- Left Pane ---
    left_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(left_frame, weight=1)

    # --- Right Pane ---
    right_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(right_frame, weight=1)
    
    # --- Populate Panes ---
    app_instance.tabs_parent = TABS_PARENT(left_frame, app_instance)
    app_instance.tabs_parent.pack(expand=True, fill='both')
    
    # Pass the orchestrator_logic to the display parent
    app_instance.display_parent_tab = TAB_DISPLAY_PARENT(right_frame, app_instance, orchestrator_logic)
    app_instance.display_parent_tab.pack(expand=True, fill='both')

    # --- Set Sash Position After Panes are Populated ---
    app_instance.update_idletasks() 
    try:
        sash_pos_percent = app_instance.config.getfloat('Application', 'paned_window_sash_position_percentage', fallback=50)
        sash_pos = int(main_paned_window.winfo_width() * (sash_pos_percent / 100.0))
        main_paned_window.sashpos(0, sash_pos)
    except Exception as e:
        console_log(f"⚠️ Could not set sash position from config: {e}. Using default.")
        initial_sash_pos = int(app_instance.winfo_width() / 2)
        main_paned_window.sashpos(0, initial_sash_pos)
    
    console_log("✅ Main GUI layout created successfully.")