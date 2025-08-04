# src/program_gui_utils.py
#
# This module is responsible for constructing the main graphical user interface (GUI)
# for the RF Spectrum Analyzer Controller application. It creates the main window layout,
# including the paned window, and populates it with all the parent and child tabs.
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
# Version 20250803.214500.1 (REFACTORED: Replaced ttk.Notebook with custom button-based tab system.)
# Version 20250804.021433.0 (FIXED: Exposed main_paned_window to app_instance and corrected geometry loading key.)
# Version 20250804.023600.0 (FIXED: Bound <<PanedWindowSashMoved>> to update sash_position_var.)

import tkinter as tk
from tkinter import ttk
from functools import partial
import inspect
import os

# --- Import all Parent and Child Tab classes ---
from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT
from tabs.Start_Pause_Stop.tab_scan_controler_button_logic import ScanControlTab
from tabs.Console.ConsoleTab import ConsoleTab
from src.console_logic import console_log
from src.debug_logic import debug_log

current_version = "20250804.023600.0" # Incremented version

def apply_saved_geometry(app_instance):
    # Function Description:
    # Applies the last saved window geometry to the application's main window.
    # It retrieves the geometry string from the application's configuration
    # and sets it on the Tkinter root window.
    #
    # Inputs to this function:
    #   app_instance (object): The main application instance (an instance of `App`).
    #
    # Process of this function:
    #   1. Retrieves the 'geometry' setting from the 'Application' section of
    #      `app_instance.config`. It falls back to a default if not found.
    #   2. Logs the retrieved geometry for debugging.
    #   3. Applies the geometry string to the `app_instance` (Tkinter root window).
    #
    # Outputs of this function:
    #   None. Modifies the application's window size and position.
    #
    # (2025-08-04.021433.0) Change: Corrected config key from 'last_GLOBAL__window_geometry' to 'geometry'.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Applying saved window geometry.",
                file=os.path.basename(__file__), function=current_function, version=current_version)

    # CORRECTED: Load 'geometry' from 'Application' section
    last_geometry = app_instance.config.get('Application', 'geometry', fallback='1400x850+100+100')
    app_instance.geometry(last_geometry)
    debug_log(f"Applied geometry: {last_geometry}",
                file=os.path.basename(__file__), function=current_function, version=current_version)


def create_main_layout_and_widgets(app_instance):
    # Function Description:
    # Constructs the main GUI layout of the application. This includes creating
    # a horizontal `ttk.PanedWindow` to divide the interface into a left pane
    # (for main tabs) and a right pane (for scan controls and console).
    # It dynamically creates tab buttons and their corresponding content frames,
    # and populates the right pane with the scan control and console widgets.
    # It also stores references to key GUI elements on the `app_instance` for
    # easy access and configuration saving.
    #
    # Inputs to this function:
    #   app_instance (object): The main application instance (an instance of `App`),
    #                          to which GUI elements will be attached and which provides
    #                          access to shared application state.
    #
    # Process of this function:
    #   1. Logs entry with debug information.
    #   2. Creates the main horizontal `ttk.PanedWindow` and packs it.
    #   3. Assigns the `main_paned_window` to `app_instance.paned_window` for external access.
    #   4. Creates and adds the left and right frames to the paned window.
    #   5. Attempts to set the sash position using `app_instance.paned_window_sash_position_var`.
    #   6. Creates a custom tab button bar at the top of the left pane.
    #   7. Creates a content frame within the left pane to hold the actual tab content.
    #   8. Defines a list of tab names and their corresponding class constructors.
    #   9. Iterates through the tab definitions:
    #      a. Creates a `ttk.Button` for each tab and links it to `app_instance.switch_tab`.
    #      b. Creates an instance of the tab's content class, passing `app_instance` and `console_log`.
    #      c. Grids the content frame and stores references to buttons and content frames
    #         on `app_instance.tab_buttons` and `app_instance.tab_content_frames` respectively.
    #   10. Populates the right pane with `ScanControlTab` and `ConsoleTab` instances.
    #       Assigns the `ConsoleTab` instance to `app_instance.console_tab`.
    #   11. Logs exit with debug information.
    #
    # Outputs of this function:
    #   None. Configures the application's main window and populates it with widgets.
    #   Sets `app_instance.paned_window`, `app_instance.tab_buttons`,
    #   `app_instance.tab_content_frames`, and `app_instance.console_tab`.
    #
    # (2025-08-04.021433.0) Change: Assigned main_paned_window to app_instance.paned_window.
    # (2025-08-04.023600.0) Change: Bound <<PanedWindowSashMoved>> to update sash_position_var.
    current_function = inspect.currentframe().f_code.co_name
    debug_log("Creating main layout and widgets. Laying out the foundation!",
                file=os.path.basename(__file__), function=current_function, version=current_version)

    main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    main_paned_window.pack(expand=True, fill='both')
    
    # EXPOSED: Assign the paned window to the app_instance
    app_instance.paned_window = main_paned_window

    # Bind the sash moved event to update the Tkinter variable
    # This is crucial for capturing live sash movements.
    main_paned_window.bind('<<PanedWindowSashMoved>>', 
                           lambda e: app_instance.paned_window_sash_position_var.set(main_paned_window.sashpos(0)))
    debug_log("Bound <<PanedWindowSashMoved>> event to update paned_window_sash_position_var.",
                file=os.path.basename(__file__), function=current_function, version=current_version)


    # --- Left Pane ---
    left_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(left_frame, weight=1)

    # --- NEW: Custom Tab Button Bar ---
    tab_button_frame = ttk.Frame(left_frame, style='TFrame')
    tab_button_frame.pack(side='top', fill='x', padx=5, pady=(5, 0))
    tab_button_frame.grid_columnconfigure(tuple(range(6)), weight=1) # Make buttons expand

    # --- NEW: Content Frame for Tab Content ---
    content_frame = ttk.Frame(left_frame, style='TFrame')
    content_frame.pack(side='top', expand=True, fill='both', padx=5, pady=(0, 5))
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    # --- Right Pane (Scan Controls and Console) ---
    right_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(right_frame, weight=1)
    
    # Try to set sash position if the variable exists and has a value
    try:
        sash_position = app_instance.paned_window_sash_position_var.get()
        main_paned_window.sashpos(0, sash_position)
        debug_log(f"Set sash position to: {sash_position}",
                    file=os.path.basename(__file__), function=current_function, version=current_version)
    except AttributeError:
        debug_log("paned_window_sash_position_var not found or not initialized. Skipping sash position restore.",
                    file=os.path.basename(__file__), function=current_function, version=current_version)
    except Exception as e:
        debug_log(f"Error setting sash position: {e}",
                    file=os.path.basename(__file__), function=current_function, version=current_version)
    
    right_top_frame = ttk.Frame(right_frame, style='TFrame')
    right_top_frame.pack(side='top', fill='x', padx=5, pady=(5,0))
    right_bottom_frame = ttk.Frame(right_frame, style='TFrame')
    right_bottom_frame.pack(side='top', expand=True, fill='both', padx=5, pady=5)

    # --- Store references on the app instance ---
    app_instance.tab_buttons = {}
    app_instance.tab_content_frames = {}
    
    tab_names = ["Instruments", "Markers", "Presets", "Scanning", "Plotting", "Experiments"]
    tab_classes = [
        TAB_INSTRUMENT_PARENT, TAB_MARKERS_PARENT, TAB_PRESETS_PARENT,
        TAB_SCANNING_PARENT, TAB_PLOTTING_PARENT, TAB_EXPERIMENTS_PARENT
    ]

    for i, (name, content_class) in enumerate(zip(tab_names, tab_classes)):
        # Create the tab button
        button = ttk.Button(
            tab_button_frame,
            text=name,
            style=f'{name}.Inactive.TButton',
            command=partial(app_instance.switch_tab, name)
        )
        button.grid(row=0, column=i, sticky='ew')
        app_instance.tab_buttons[name] = button

        # Create the content frame
        content = content_class(content_frame, app_instance, console_log)
        content.grid(row=0, column=0, sticky='nsew')
        app_instance.tab_content_frames[name] = content

    # --- Populate Right Pane ---
    scan_controls = ScanControlTab(right_top_frame, app_instance)
    scan_controls.pack(expand=True, fill='both')
    
    app_instance.console_tab = ConsoleTab(right_bottom_frame, app_instance)
    app_instance.console_tab.pack(expand=True, fill='both')

    debug_log("Main layout and widgets created. UI ready!",
                file=os.path.basename(__file__), function=current_function, version=current_version)