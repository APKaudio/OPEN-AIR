# src/program_gui_utils.py
#
# This module provides utility functions for GUI-related tasks,
# such as applying saved window geometry, setting up application styles,
# and creating the main application widgets. It helps to keep the
# main application file cleaner by centralizing these common GUI setup operations.
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
# Version 20250803.1500.0 (Initial creation: Moved _apply_saved_geometry and _setup_styles from main_app.py)
# Version 20250803.1505.0 (Moved _create_widgets from main_app.py to this file as create_widgets)

import os
import inspect
import tkinter as tk # Needed for tk.HORIZONTAL, tk.END etc.
from tkinter import TclError, ttk

# Import logging and config management functions
import src.debug_logic as debug_logic_module
import src.console_logic as console_logic_module
from src.settings_and_config.config_manager import save_config
from src.program_style import apply_styles # Import apply_styles for setup_styles

# Import tab classes that are now created within create_widgets
from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT
from tabs.Console.ConsoleTab import ConsoleTab
from tabs.Start_Pause_Stop.tab_scan_controler_button_logic import ScanControlTab


current_version = "20250803.1505.0" # this variable should always be defined below the header to make the debugging better

def apply_saved_geometry(app_instance):
    """
    Function Description:
    Applies the window geometry saved in config.ini, or uses a default
    if no saved geometry is found or if it's invalid.

    Inputs:
        app_instance (App): The main application instance, providing access to
                            config, default geometry, and logging functions.

    Process:
        1. Retrieves the window geometry from the 'LAST_USED_SETTINGS'
            section of the application's config, using a default fallback.
        2. Attempts to apply the retrieved geometry to the main window.
        3. If a `TclError` occurs (due to invalid geometry string),
            it logs the error and applies the hardcoded default geometry.

    Outputs:
        None. Sets the main window's size and position.
    """
    current_function = inspect.currentframe().f_code.co_name

    saved_geometry = app_instance.config.get('LAST_USED_SETTINGS', 'last_GLOBAL__window_geometry', fallback=app_instance.DEFAULT_WINDOW_GEOMETRY)
    try:
        app_instance.geometry(saved_geometry)
        debug_logic_module.debug_log(f"Applied saved geometry: {saved_geometry}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    except TclError as e:
        debug_logic_module.debug_log(f"ERROR: Invalid saved geometry '{saved_geometry}': {e}. Using default.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        app_instance.geometry(app_instance.DEFAULT_WINDOW_GEOMETRY)

def setup_styles(app_instance):
    """
    Function Description:
    Configures and applies custom ttk styles for a modern dark theme
    to various Tkinter widgets within the application. This includes
    defining styles for parent and child notebooks to support the
    two-layer tab structure with unique and dynamic colors for parent tabs.

    Inputs:
        app_instance (App): The main application instance, providing access to
                            the ttk.Style object and logging functions.

    Process:
        1. Calls the external `apply_styles` function from `src.style`
            to apply all centralized style configurations.

    Outputs:
        None. Applies visual styling to the application's GUI.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_logic_module.debug_log(f"Setting up ttk styles...",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)
    apply_styles(app_instance.style, debug_logic_module.debug_log, app_instance.current_version)


def create_widgets(app_instance):
    """
    Function Description:
    Creates and arranges all GUI widgets in the main application window.
    It sets up a two-column layout using ttk.PanedWindow for a resizable divider,
    with parent tabs on the left and scan control/console on the right.

    Inputs:
        app_instance (App): The main application instance, providing access to
                            Tkinter variables, logging functions, and other app attributes.

    Process:
        1. Prints a debug message.
        2. Configures the main window's grid to host the PanedWindow.
        3. Creates `app_instance.main_panedwindow` for the resizable layout.
        4. Creates `app_instance.parent_notebook` for the top-level parent tabs and adds it to the left pane.
        5. Instantiates and adds all `TAB_X_PARENT` classes to `app_instance.parent_notebook`,
            storing references to parent tab widgets and their child notebooks.
        6. Binds the `<<NotebookTabChanged>>` event for the parent notebook.
        7. Creates `right_column_container` for the right pane and adds it to the PanedWindow.
        8. Instantiates `ScanControlTab` and places it in the right column.
        9. Instantiates `ConsoleTab` and places it below the `ScanControlTab`.
        10. Applies the saved sash position to the PanedWindow.

    Outputs:
        None. Populates the main window with GUI elements.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_logic_module.debug_log(f"Starting main application widgets with nested tabs...",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

    app_instance.grid_columnconfigure(0, weight=1)
    app_instance.grid_rowconfigure(0, weight=1)

    app_instance.main_panedwindow = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    app_instance.main_panedwindow.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    app_instance.parent_notebook = ttk.Notebook(app_instance.main_panedwindow, style='Parent.TNotebook')
    app_instance.main_panedwindow.add(app_instance.parent_notebook, weight=1)

    # Dictionary to hold references to child tab instances for easy lookup
    # Structure: { "ParentTabName": { "ChildTabName": instance } }
    app_instance.tab_instances = {
        "Instrument": {},
        "Scanning": {},
        "Plotting": {},
        "Markers": {},
        "Presets": {},
        "Experiments": {},
        "JSON API": {} # Assuming a JSON API tab will exist
    }

    app_instance.child_notebooks = {}
    app_instance.parent_tab_widgets = {}

    # Instrument Parent Tab and its children
    app_instance.instrument_parent_tab = TAB_INSTRUMENT_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log, style_obj=app_instance.style)
    app_instance.parent_notebook.add(app_instance.instrument_parent_tab, text="INSTRUMENT")
    app_instance.child_notebooks["INSTRUMENT"] = app_instance.instrument_parent_tab.child_notebook
    app_instance.parent_tab_widgets["INSTRUMENT"] = app_instance.instrument_parent_tab
    # Correctly map child tabs for Instrument
    if hasattr(app_instance.instrument_parent_tab, 'instrument_settings_tab'):
        app_instance.tab_instances["Instrument"]["Connection"] = app_instance.instrument_parent_tab.instrument_settings_tab
    if hasattr(app_instance.instrument_parent_tab, 'visa_interpreter_tab'):
        app_instance.tab_instances["Instrument"]["VISA Interpreter"] = app_instance.instrument_parent_tab.visa_interpreter_tab


    # Scanning Parent Tab and its children
    app_instance.scanning_parent_tab = TAB_SCANNING_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log)
    app_instance.parent_notebook.add(app_instance.scanning_parent_tab, text="SCANNING")
    app_instance.child_notebooks["SCANNING"] = app_instance.scanning_parent_tab.child_notebook
    app_instance.parent_tab_widgets["SCANNING"] = app_instance.scanning_parent_tab
    # Correctly map child tabs for Scanning
    if hasattr(app_instance.scanning_parent_tab, 'scan_configuration_tab'):
        app_instance.tab_instances["Scanning"]["Scan Configuration"] = app_instance.scanning_parent_tab.scan_configuration_tab
    if hasattr(app_instance.scanning_parent_tab, 'scan_meta_data_tab'):
        app_instance.tab_instances["Scanning"]["Scan Meta Data"] = app_instance.scanning_parent_tab.scan_meta_data_tab
    # Note: Scan Control Tab is handled separately below as it's in the right column


    # Plotting Parent Tab and its children
    app_instance.plotting_parent_tab = TAB_PLOTTING_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log)
    app_instance.parent_notebook.add(app_instance.plotting_parent_tab, text="PLOTTING")
    app_instance.child_notebooks["PLOTTING"] = app_instance.plotting_parent_tab.child_notebook
    app_instance.parent_tab_widgets["PLOTTING"] = app_instance.plotting_parent_tab
    # Correctly map child tabs for Plotting
    if hasattr(app_instance.plotting_parent_tab, 'plotting_tab'):
        app_instance.tab_instances["Plotting"]["Plotting"] = app_instance.plotting_parent_tab.plotting_tab


    # Markers Parent Tab and its children
    app_instance.markers_parent_tab = TAB_MARKERS_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log)
    app_instance.parent_notebook.add(app_instance.markers_parent_tab, text="MARKERS")
    app_instance.child_notebooks["MARKERS"] = app_instance.markers_parent_tab.child_notebook
    app_instance.parent_tab_widgets["MARKERS"] = app_instance.markers_parent_tab
    # Correctly map child tabs for Markers
    if hasattr(app_instance.markers_parent_tab, 'markers_display_tab'):
        app_instance.tab_instances["Markers"]["Markers Display"] = app_instance.markers_parent_tab.markers_display_tab


    # Presets Parent Tab and its children
    app_instance.presets_parent_tab = TAB_PRESETS_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log, style_obj=app_instance.style)
    app_instance.parent_notebook.add(app_instance.presets_parent_tab, text="PRESETS")
    app_instance.child_notebooks["PRESETS"] = app_instance.presets_parent_tab.child_notebook
    app_instance.parent_tab_widgets["PRESETS"] = app_instance.presets_parent_tab
    # Correctly map child tabs for Presets
    if hasattr(app_instance.presets_parent_tab, 'presets_tab'):
        app_instance.tab_instances["Presets"]["Presets"] = app_instance.presets_parent_tab.presets_tab
    if hasattr(app_instance.presets_parent_tab, 'initial_config_tab'): # Added initial_config_tab
        app_instance.tab_instances["Presets"]["Initial Configuration"] = app_instance.presets_parent_tab.initial_config_tab


    # Experiments Parent Tab and its children
    app_instance.experiments_parent_tab = TAB_EXPERIMENTS_PARENT(app_instance.parent_notebook, app_instance=app_instance, console_print_func=console_logic_module.console_log)
    app_instance.parent_notebook.add(app_instance.experiments_parent_tab, text="EXPERIMENTS")
    app_instance.child_notebooks["EXPERIMENTS"] = app_instance.experiments_parent_tab.child_notebook
    app_instance.parent_tab_widgets["EXPERIMENTS"] = app_instance.experiments_parent_tab
    app_instance.tab_instances["Experiments"]["Experiments"] = app_instance.experiments_parent_tab.child_notebook


    app_instance.parent_notebook.bind("<<NotebookTabChanged>>", app_instance._on_parent_tab_change)


    # --- Right Column Container Frame ---
    right_column_container = ttk.Frame(app_instance.main_panedwindow, style='Dark.TFrame')
    app_instance.main_panedwindow.add(right_column_container, weight=1)
    right_column_container.grid_columnconfigure(0, weight=1)
    right_column_container.grid_rowconfigure(0, weight=0) # Scan Control row
    right_column_container.grid_rowconfigure(1, weight=1) # Console row


    # --- Scan Control Buttons Frame ---
    scan_control_frame = ttk.Frame(right_column_container, style='Dark.TFrame')
    scan_control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    scan_control_frame.grid_columnconfigure(0, weight=1)

    app_instance.scan_control_tab = ScanControlTab(scan_control_frame, app_instance=app_instance)
    app_instance.scan_control_tab.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
    # Store the ScanControlTab instance directly as it's not part of a nested notebook
    app_instance.tab_instances["Scanning"]["Scan Control"] = app_instance.scan_control_tab


    # --- Console and Debug Options Frame (Directly in right_column_container) ---
    app_instance.console_tab = ConsoleTab(right_column_container, app_instance=app_instance)
    app_instance.console_tab.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    # Store the ConsoleTab instance directly
    #app_instance.tab_instances["Console"]["Console"] = self # This line was commented out in main_app, keeping it commented.


    # Apply the saved sash position after all widgets are added to the paned window
    sash_pos = app_instance.paned_window_sash_position_var.get()
    if sash_pos > 0:
        app_instance.main_panedwindow.sashpos(0, sash_pos)
        debug_logic_module.debug_log(f"Applied saved PanedWindow sash position: {sash_pos}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
    else:
        debug_logic_module.debug_log(f"WARNING: Invalid saved PanedWindow sash position: {sash_pos}. Using default.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    debug_logic_module.debug_log(f"Main application widgets created.",
                file=f"{os.path.basename(__file__)} - {current_version}",
                version=current_version,
                function=current_function)

