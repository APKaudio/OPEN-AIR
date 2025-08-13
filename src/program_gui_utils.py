# src/program_gui_utils.py
#
# This is the description of what comes below
# This module is responsible for constructing the main graphical user interface (GUI)
# for the RF Spectrum Analyzer Controller application. It creates the main window layout,
# including the paned window, and populates it with the main tab container and the display/control panes.
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
# Version 20250812.234200.2

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime

# --- Import all Parent and Child Tab classes ---
from tabs.TABS_PARENT import TABS_PARENT # REFACTORED: Import the new master tab container
from tabs.Start_Pause_Stop.tab_scan_controler_button_logic import ScanControlTab
from display.DISPLAY_PARENT import TAB_DISPLAY_PARENT 

from display.console_logic import console_log
from display.debug_logic import debug_log

# --- Version Information ---
current_version = "20250812.234200.2"
current_version_hash = (int(current_version.split('.')[0]) * int(current_version.split('.')[1]) * int(current_version.split('.')[2]))


def apply_saved_geometry(app_instance):
    # Function Description
    # Applies the last saved window geometry and state to the application's main window.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Applying saved window geometry and state.",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

    last_geometry = app_instance.config.get('Application', 'geometry', fallback='1000x1000+0+0')
    last_state = app_instance.config.get('Application', 'window_state', fallback='normal')

    app_instance.geometry(last_geometry)
    app_instance.state(last_state)

    debug_log(f"Applied geometry: {last_geometry}, State: {last_state}",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)


def create_main_layout_and_widgets(app_instance):
    # Function Description
    # Constructs the main GUI layout. Creates a horizontal PanedWindow dividing the interface
    # into a left pane (for main tabs via TABS_PARENT) and a right pane (for scan controls and console).
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Creating main layout and widgets. Laying out the new two-column foundation!",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

    main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    main_paned_window.pack(expand=True, fill='both')
    
    app_instance.paned_window = main_paned_window

    main_paned_window.bind('<<PanedWindowSashMoved>>', 
                           lambda e: app_instance._on_sash_moved())
    debug_log("Bound <<PanedWindowSashMoved>> event.",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

    # --- Left Pane (Now contains the master TABS_PARENT) ---
    left_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(left_frame, weight=1)

    # --- Right Pane (Scan Controls and Display) ---
    right_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(right_frame, weight=1)
    
    # Restore sash position after frames are added
    try:
        sash_position_percentage = int(app_instance.config.get('Application', 'paned_window_sash_position_percentage', fallback='50'))
        # Use after() to ensure the main window has had a chance to render and get its size
        app_instance.after(100, lambda: _set_sash_position(app_instance, main_paned_window, sash_position_percentage))
    except Exception as e:
        debug_log(f"Ahoy! A scallywag error be found whilst settin' the sash position: {e}. We'll be proceedin' without it, but keep a weather eye open!",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
    
    # --- Populate Left Pane ---
    app_instance.tabs_parent = TABS_PARENT(left_frame, app_instance)
    app_instance.tabs_parent.pack(expand=True, fill='both')

    # --- Populate Right Pane ---
    right_top_frame = ttk.Frame(right_frame, style='TFrame')
    right_top_frame.pack(side='top', fill='x', padx=5, pady=(5,0))
    right_bottom_frame = ttk.Frame(right_frame, style='TFrame')
    right_bottom_frame.pack(side='top', expand=True, fill='both', padx=5, pady=5)

    scan_controls = ScanControlTab(right_top_frame, app_instance)
    scan_controls.pack(expand=True, fill='both')
    app_instance.scan_control_tab = scan_controls
    
    app_instance.display_parent_tab = TAB_DISPLAY_PARENT(right_bottom_frame, app_instance, console_log)
    app_instance.display_parent_tab.pack(expand=True, fill='both')
    
    # Check if the references were successfully set after initialization.
    if not hasattr(app_instance, 'scan_monitor_tab') or not app_instance.scan_monitor_tab:
         debug_log("❌ ERROR: `ScanMonitorTab` instance not found on app_instance after display parent creation. This is a critical error!",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function, special=True)
    if not hasattr(app_instance, 'console_text') or not app_instance.console_text:
        debug_log("❌ ERROR: Console text widget not found on app_instance after display parent creation. This is a critical error!",
                    file=f"{os.path.basename(__file__)} - {current_version}", function=current_function, special=True)

    debug_log("Main layout and widgets created. UI ready!",
                file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)

def _set_sash_position(app_instance, paned_window, percentage):
    # Function Description
    # Helper function to set the sash position after the main window is drawn.
    # This prevents issues where winfo_width() returns 1 on startup.
    current_function = inspect.currentframe().f_code.co_name
    try:
        window_width = app_instance.winfo_width()
        if window_width > 1:
            sash_pos = int((percentage / 100) * window_width)
            paned_window.sashpos(0, sash_pos)
            debug_log(f"Sash position restored to {sash_pos}px ({percentage}%)",
                      file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)
        else:
            # If the window is still not drawn, try again shortly.
            app_instance.after(100, lambda: _set_sash_position(app_instance, paned_window, percentage))
    except Exception as e:
        debug_log(f"By thunder! The contraption failed to set the sash position! Error: {e}",
                  file=f"{os.path.basename(__file__)} - {current_version}", function=current_function)