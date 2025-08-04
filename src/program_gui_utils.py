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
# Version 20250803.213500.0 (FIXED: Removed extra console_log argument from ConsoleTab constructor.)
# Version 20250803.212500.0 (FIXED: Removed invalid 'style' argument from notebook.add() calls.)
# Version 20250803.211600.0 (FIXED: Added missing console_print_func argument to Parent Tab constructors.)
# Version 20250803.211000.0 (FIXED: Moved 'style' argument to notebook.add() method to resolve TypeError.)
# Version 20250803.210500.0 (FIXED: Removed style from TPanedWindow to prevent TclError.)
# Version 20250803.214500.0 (CREATED: New GUI builder to construct the entire UI layout.)

import tkinter as tk
from tkinter import ttk

# --- Import all Parent and Child Tab classes ---
from tabs.Instrument.TAB_INSTRUMENT_PARENT import TAB_INSTRUMENT_PARENT
from tabs.Markers.TAB_MARKERS_PARENT import TAB_MARKERS_PARENT
from tabs.Presets.TAB_PRESETS_PARENT import TAB_PRESETS_PARENT
from tabs.Scanning.TAB_SCANNING_PARENT import TAB_SCANNING_PARENT
from tabs.Plotting.TAB_PLOTTING_PARENT import TAB_PLOTTING_PARENT
from tabs.Experiments.TAB_EXPERIMENTS_PARENT import TAB_EXPERIMENTS_PARENT
from tabs.Start_Pause_Stop.tab_scan_controler_button_logic import ScanControlTab
from tabs.Console.ConsoleTab import ConsoleTab
from src.console_logic import console_log # Import the console logger

def apply_saved_geometry(app_instance):
    """Applies the last saved window geometry to the application."""
    last_geometry = app_instance.config.get('LAST_USED', 'last_GLOBAL__window_geometry', fallback='1400x850+100+100')
    app_instance.geometry(last_geometry)

def create_main_layout_and_widgets(app_instance):
    """Creates the main paned window layout and populates it with all widgets."""

    # Create the main split-screen window
    main_paned_window = ttk.PanedWindow(app_instance, orient=tk.HORIZONTAL)
    main_paned_window.pack(expand=True, fill='both')

    # --- Left Pane (Main Tabs) ---
    left_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(left_frame, weight=1)

    # This is the main notebook that holds the parent tabs
    app_instance.parent_notebook = ttk.Notebook(left_frame, style='TNotebook')
    app_instance.parent_notebook.pack(expand=True, fill='both', padx=5, pady=5)
    app_instance.parent_notebook.bind("<<NotebookTabChanged>>", app_instance._on_parent_tab_change)

    # --- Right Pane (Scan Controls and Console) ---
    right_frame = ttk.Frame(main_paned_window, style='TFrame')
    main_paned_window.add(right_frame, weight=1)

    # Set the sash position from the config
    sash_position = app_instance.paned_window_sash_position_var.get()
    main_paned_window.sashpos(0, sash_position)

    # Create frames within the right pane
    right_top_frame = ttk.Frame(right_frame, style='TFrame')
    right_top_frame.pack(side='top', fill='x', padx=5, pady=(5,0))

    right_bottom_frame = ttk.Frame(right_frame, style='TFrame')
    right_bottom_frame.pack(side='top', expand=True, fill='both', padx=5, pady=5)

    # --- Populate Widgets ---
    app_instance.parent_tab_widgets = {}
    app_instance.tab_instances = {}

    # 1. Instruments Tab
    instrument_parent = TAB_INSTRUMENT_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(instrument_parent, text='Instruments')
    app_instance.parent_tab_widgets['Instruments'] = instrument_parent

    # 2. Markers Tab
    markers_parent = TAB_MARKERS_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(markers_parent, text='Markers')
    app_instance.parent_tab_widgets['Markers'] = markers_parent

    # 3. Presets Tab
    presets_parent = TAB_PRESETS_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(presets_parent, text='Presets')
    app_instance.parent_tab_widgets['Presets'] = presets_parent

    # 4. Scanning Tab
    scanning_parent = TAB_SCANNING_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(scanning_parent, text='Scanning')
    app_instance.parent_tab_widgets['Scanning'] = scanning_parent

    # 5. Plotting Tab
    plotting_parent = TAB_PLOTTING_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(plotting_parent, text='Plotting')
    app_instance.parent_tab_widgets['Plotting'] = plotting_parent

    # 6. Experiments Tab
    experiments_parent = TAB_EXPERIMENTS_PARENT(app_instance.parent_notebook, app_instance, console_log)
    app_instance.parent_notebook.add(experiments_parent, text='Experiments')
    app_instance.parent_tab_widgets['Experiments'] = experiments_parent
    
    # 7. Scan Controls (Top Right)
    scan_controls = ScanControlTab(right_top_frame, app_instance)
    scan_controls.pack(expand=True, fill='both')
    
    # 8. Console (Bottom Right)
    # CORRECTED: Removed the extra console_log argument
    app_instance.console_tab = ConsoleTab(right_bottom_frame, app_instance)
    app_instance.console_tab.pack(expand=True, fill='both')