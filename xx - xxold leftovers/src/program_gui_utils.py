# src/program_gui_utils.py
#
# Version 20250821.223500.1 (Corrected Dependencies)

import os
import tkinter as tk
from tkinter import ttk
import inspect
from datetime import datetime

from .TABS_PARENT import TABS_PARENT 
from display.DISPLAY_PARENT import DISPLAY_PARENT

# --- Version Information ---
current_version = "20250821.223500.1"
current_file = os.path.basename(__file__)

def create_main_layout(app_instance, style_obj):
    """Creates and configures the main GUI layout."""
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ 🟢 Entering {current_function}")
    try:
        main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True)

        display_parent = DISPLAY_PARENT(main_paned_window, app_instance, style_obj)
        tabs_parent = TABS_PARENT(main_paned_window, app_instance) 

        main_paned_window.add(tabs_parent, weight=1)
        main_paned_window.add(display_parent, weight=4)

        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Main layout created successfully.")
        return main_paned_window, tabs_parent, display_parent
    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Error creating main layout: {e}")
        raise

def apply_saved_geometry(app_instance):
    """Applies the last saved window geometry and state from the config file."""
    # This function remains unchanged.
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ 🟢 Entering {current_function}")
    try:
        if hasattr(app_instance, 'program_config') and app_instance.program_config.has_option('Application', 'geometry'):
            geometry = app_instance.program_config.get('Application', 'geometry')
            app_instance.geometry(geometry)
        if hasattr(app_instance, 'program_config') and app_instance.program_config.has_option('Application', 'window_state'):
            window_state = app_instance.program_config.get('Application', 'window_state')
            if window_state:
                app_instance.state(window_state)
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ⚙️ ✅ Exiting {current_function}")
    except Exception as e:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Error applying saved geometry: {e}")