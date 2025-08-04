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

import tkinter as tk
from tkinter import ttk
from functools import partial

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

def apply_saved_geometry(app_instance):
    """Applies the last saved window geometry to the application."""
    last_geometry = app_instance.config.get('LAST_USED', 'last_GLOBAL__window_geometry', fallback='1400x850+100+100')
    app_instance.geometry(last_geometry)

def create_main_layout_and_widgets(app_instance):
    """Creates the main paned window layout and populates it with all widgets."""

    main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    main_paned_window.pack(expand=True, fill='both')

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
    sash_position = app_instance.paned_window_sash_position_var.get()
    main_paned_window.sashpos(0, sash_position)
    
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