# src/style.py
# src/style.py
#
# This file centralizes all Tkinter ttk.Style configurations for the application.
# It provides a single function to apply a consistent visual theme across all widgets.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250801.1 (Initial creation - contains all ttk.Style definitions moved from main_app.py)

import tkinter as tk
from tkinter import ttk

def apply_styles(style_instance, debug_print_func=None, current_version=None):
    """
    Configures and applies custom ttk styles for a modern dark theme
    to various Tkinter widgets within the application.

    Inputs:
        style_instance (ttk.Style): The ttk.Style instance from the main application.
        debug_print_func (function, optional): A function for debug logging.
        current_version (str, optional): The current application version for debug logs.
    Outputs:
        None. Applies visual styling to the application's GUI via the provided style_instance.
    """
    if debug_print_func:
        debug_print_func(f"🚫🐛 [DEBUG] Setting up ttk styles from style.py... Version: {current_version}",
                         file=f"src/style.py - {current_version}",
                         function="apply_styles")

    style_instance.theme_use('clam')

    # General background and foreground colors
    BG_DARK = "#1e1e1e"
    FG_LIGHT = "#cccccc"
    ACCENT_BLUE = "#007bff"
    ACCENT_GREEN = "#28a745"
    ACCENT_RED = "#dc3545"
    ACCENT_ORANGE = "#ffc107"
    ACCENT_PURPLE = "#6f42c1"

    # Parent Tab Colors (These are constants, but their usage is dynamic in main_app.py)
    PARENT_INSTRUMENT_ACTIVE = "#FF0000"
    PARENT_INSTRUMENT_INACTIVE = "#660C0C"
    PARENT_SCANNING_ACTIVE = "#FF6600"
    PARENT_SCANNING_INACTIVE = "#926002"
    PARENT_PLOTTING_ACTIVE = "#D1D10E"
    PARENT_PLOTTING_INACTIVE = "#72720A"
    PARENT_MARKERS_ACTIVE = "#319131"
    PARENT_MARKERS_INACTIVE = "#1B4B1B"
    PARENT_PRESETS_ACTIVE = "#0303C9"
    PARENT_PRESETS_INACTIVE = "#00008B"
    PARENT_EXPERIMENTS_ACTIVE = ACCENT_PURPLE
    PARENT_EXPERIMENTS_INACTIVE = "#4d2482"

    style_instance.configure('.', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10))
    style_instance.configure('TFrame', background=BG_DARK)
    style_instance.configure('TLabel', background=BG_DARK, foreground=FG_LIGHT)
    style_instance.configure('TEntry', fieldbackground="#3b3b3b", foreground="#ffffff", borderwidth=1, relief="flat")
    style_instance.map('TEntry', fieldbackground=[('focus', '#4a4a4a')])
    style_instance.configure('TCombobox', fieldbackground="#3b3b3b", foreground="#ffffff", selectbackground=ACCENT_BLUE, selectforeground="white")
    style_instance.map('TCombobox', fieldbackground=[('readonly', '#3b3b3b')], arrowcolor=[('!disabled', FG_LIGHT)])

    # Buttons - Reverted global TButton style to 15pt font
    style_instance.configure('TButton',
                    background="#4a4a4a",
                    foreground="white",
                    font=('Helvetica', 15, 'bold'), # Reverted font size to 15pt
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor=ACCENT_BLUE,
                    padding=5) # Default padding
    style_instance.map('TButton',
            background=[('active', '#606060'), ('disabled', '#303030')],
            foreground=[('disabled', '#808060')])

    # NEW: Base Style for "big buttons" (Start, Pause, Stop)
    style_instance.configure('BigScanButton.TButton',
                    background="#4a4a4a", # Default background, will be overridden by specific colors
                    foreground="white",
                    font=('Helvetica', 100, 'bold'), # 30pt font for big buttons
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor=ACCENT_BLUE,
                    padding=(10, 20)) # Larger padding for big buttons

    # Specific color styles for BigScanButton
    style_instance.configure('BigScanButton.Green.TButton',
                         background=ACCENT_GREEN, foreground="white")
    style_instance.map('BigScanButton.Green.TButton',
                   background=[('active', '#218838'), ('disabled', '#1e7e34')],
                   foreground=[('disabled', '#808060')])

    style_instance.configure('BigScanButton.Orange.TButton',
                         background=ACCENT_ORANGE, foreground="#333333")
    style_instance.map('BigScanButton.Orange.TButton',
                   background=[('active', '#e0a800'), ('disabled', '#d39e00')],
                   foreground=[('disabled', '#808060')])

    style_instance.configure('BigScanButton.Red.TButton',
                         background=ACCENT_RED, foreground="white")
    style_instance.map('BigScanButton.Red.TButton',
                   background=[('active', '#c82333'), ('disabled', '#bd2130')],
                   foreground=[('disabled', '#808060')])

    # A specific disabled style for BigScanButtons
    style_instance.configure('BigScanButton.Disabled.TButton',
                         background='#303030', foreground='#808060')
    style_instance.map('BigScanButton.Disabled.TButton',
                   background=[('active', '#303030'), ('!active', '#303030')],
                   foreground=[('active', '#808060'), ('!active', '#808060')])


    # Flashing styles for the Pause/Resume button (now based on BigScanButton's font/padding)
    # These will alternate with BigScanButton.Green.TButton (for Resume)
    style_instance.configure('FlashingGreen.TButton', background='green', foreground='white',
                         font=('Helvetica', 30, 'bold'), padding=(10, 20))
    style_instance.map('FlashingGreen.TButton',
                   background=[('active', 'lightgreen'), ('!active', 'green')],
                   foreground=[('active', 'black'), ('!active', 'white')])

    style_instance.configure('FlashingDark.TButton', background='darkgray', foreground='white',
                         font=('Helvetica', 30, 'bold'), padding=(10, 20))
    style_instance.map('FlashingDark.TButton',
                   background=[('active', 'gray'), ('!active', 'darkgray')],
                   foreground=[('active', 'black'), ('!active', 'white')])


    # Checkbuttons
    style_instance.configure('TCheckbutton', background=BG_DARK, foreground=FG_LIGHT, indicatorcolor="#4a4a4a")
    style_instance.map('TCheckbutton',
            background=[('active', BG_DARK)],
            foreground=[('disabled', '#808080')],
            indicatorcolor=[('selected', ACCENT_BLUE)])

    # LabelFrame
    style_instance.configure('TLabelFrame', background=BG_DARK, foreground=FG_LIGHT, borderwidth=1, relief="solid")
    style_instance.configure('TLabelFrame.Label', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10, 'bold'))
    style_instance.configure('Dark.TLabelframe', background="#1e1e1e", foreground="#cccccc")
    style_instance.configure('Dark.TLabelframe.Label', background="#1e1e1e", foreground="#cccccc")
    style_instance.configure('Dark.TFrame', background="#1e1e1e")

    # --- Parent Notebook Styles ---
    # Generic Parent Notebook style (for the notebook frame itself)
    style_instance.configure('Parent.TNotebook', background=BG_DARK, borderwidth=0)
    # Configure the tab elements directly for Parent.TNotebook.Tab
    # This will apply to ALL parent tabs. We use style_instance.map for state-based changes.
    style_instance.configure('Parent.TNotebook.Tab',
                             background="#3b3b3b", # Default inactive background
                             foreground=FG_LIGHT,
                             padding=[15, 8],
                             font=('Helvetica', 11, 'bold'))

    # Map colors for Parent.TNotebook.Tab based on state
    style_instance.map('Parent.TNotebook.Tab',
                       background=[('selected', ACCENT_BLUE), ('active', ACCENT_BLUE)], # Common active color
                       foreground=[('selected', 'white'), ('active', 'white')],
                       expand=[('selected', [1, 1, 1, 0])]) # Expand selected tab

    # --- Child Notebook Styles (Matching Parent Colors) ---
    # These styles are applied to the *child notebooks themselves* and their tabs.
    # Instrument Child Notebook Tabs (Red)
    style_instance.configure('InstrumentChild.TNotebook', background=PARENT_INSTRUMENT_ACTIVE, borderwidth=0)
    style_instance.configure('InstrumentChild.TNotebook.Tab', background=PARENT_INSTRUMENT_INACTIVE, foreground=FG_LIGHT, padding=[10, 5])
    style_instance.map('InstrumentChild.TNotebook.Tab',
            background=[('selected', PARENT_INSTRUMENT_ACTIVE), ('active', PARENT_INSTRUMENT_ACTIVE)],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])

    # Scanning Child Notebook Tabs (Orange)
    style_instance.configure('ScanningChild.TNotebook', background=PARENT_SCANNING_ACTIVE, borderwidth=0)
    style_instance.configure('ScanningChild.TNotebook.Tab', background=PARENT_SCANNING_INACTIVE, foreground=BG_DARK, padding=[10, 5])
    style_instance.map('ScanningChild.TNotebook.Tab',
            background=[('selected', PARENT_SCANNING_ACTIVE), ('active', PARENT_SCANNING_ACTIVE)],
            foreground=[('selected', BG_DARK)],
            expand=[('selected', [1, 1, 1, 0])])

    # Plotting Child Notebook Tabs (Yellow)
    style_instance.configure('PlottingChild.TNotebook', background=PARENT_PLOTTING_ACTIVE, borderwidth=0)
    style_instance.configure('PlottingChild.TNotebook.Tab', background=PARENT_PLOTTING_INACTIVE, foreground=BG_DARK, padding=[10, 5])
    style_instance.map('PlottingChild.TNotebook.Tab',
            background=[('selected', PARENT_PLOTTING_ACTIVE), ('active', PARENT_PLOTTING_ACTIVE)],
            foreground=[('selected', 'black')], # Black foreground for yellow for better contrast
            expand=[('selected', [1, 1, 1, 0])])


    # Markers Child Notebook Tabs (Green)
    style_instance.configure('MarkersChild.TNotebook', background=PARENT_MARKERS_ACTIVE, borderwidth=0)
    style_instance.configure('MarkersChild.TNotebook.Tab', background=PARENT_MARKERS_INACTIVE, foreground=BG_DARK, padding=[10, 5])
    style_instance.map('MarkersChild.TNotebook.Tab',
            background=[('selected', PARENT_MARKERS_ACTIVE), ('active', PARENT_MARKERS_ACTIVE)],
            foreground=[('selected', BG_DARK)], # White foreground for green
            expand=[('selected', [1, 1, 1, 0])])

    # Presets Child Notebook Tabs (Blue)
    style_instance.configure('PresetsChild.TNotebook', background=PARENT_PRESETS_ACTIVE, borderwidth=0)
    style_instance.configure('PresetsChild.TNotebook.Tab', background=PARENT_PRESETS_INACTIVE, foreground=FG_LIGHT, padding=[10, 5])
    style_instance.map('PresetsChild.TNotebook.Tab',
            background=[('selected', PARENT_PRESETS_ACTIVE), ('active', PARENT_PRESETS_ACTIVE)],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])

    # Experiments Child Notebook Tabs (Purple)
    style_instance.configure('ExperimentsChild.TNotebook', background=PARENT_EXPERIMENTS_ACTIVE, borderwidth=0)
    style_instance.configure('ExperimentsChild.TNotebook.Tab', background=PARENT_EXPERIMENTS_INACTIVE, foreground=FG_LIGHT, padding=[10, 5])
    style_instance.map('ExperimentsChild.TNotebook.Tab',
            background=[('selected', PARENT_EXPERIMENTS_ACTIVE), ('active', PARENT_EXPERIMENTS_ACTIVE)],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])


    # Treeview (for MarkersDisplayTab and VisaInterpreterTab)
    style_instance.configure('Treeview',
                    background="#3b3b3b",
                    foreground="#ffffff",
                    fieldbackground="#3b3b3b",
                    rowheight=25)
    style_instance.map('Treeview',
            background=[('selected', ACCENT_BLUE)],
            foreground=[('selected', 'white')])

    style_instance.configure('Treeview.Heading',
                    background="#4a4a4a",
                    foreground="white",
                    font=('Helvetica', 10, "bold"))
    style_instance.map('Treeview.Heading',
            background=[('active', '#606060')])

    # Markers Tab Specific Styles (from the immersive artifact)
    style_instance.configure("Markers.TFrame",
                        background="#1e1e1e", # Dark background for the main markers tab frame
                        foreground="#cccccc") # Light grey text for general labels

    style_instance.configure("Dark.TLabelframe",
                        background="#2b2b2b", # Slightly lighter dark for labelled frames
                        foreground="#ffffff", # White text for the labelframe title
                        bordercolor="#444444",
                        lightcolor="#444444",
                        darkcolor="#1a1a1a")
    style_instance.map("Dark.TLabelframe",
              background=[('active', '#3a3a3a')]) # Subtle change on active

    style_instance.configure("Dark.TLabelframe.Label",
                        background="#2b2b2b",
                        foreground="#ffffff",
                        font=("Arial", 10, "bold"))

    style_instance.configure("Dark.TFrame",
                        background="#1e1e1e") # For inner frames without a label

    style_instance.configure("Markers.Inner.Treeview",
                        background="#2b2b2b", # Dark background for treeview
                        foreground="#cccccc", # Light grey text
                        fieldbackground="#2b2b2b",
                        bordercolor="#444444",
                        lightcolor="#444444",
                        darkcolor="#1a1a1a",
                        font=("Arial", 9))
    style_instance.map("Markers.Inner.Treeview",
              background=[('selected', '#555555')], # Darker grey when selected
              foreground=[('selected', '#ffffff')]) # White text when selected

    style_instance.configure("Markers.TLabel",
                        background="#1e1e1e", # Dark background for labels
                        foreground="#cccccc", # Light grey text
                        font=("Arial", 9))

    style_instance.configure("Markers.TEntry",
                        fieldbackground="#3a3a3a", # Darker input field
                        foreground="#ffffff", # White text
                        insertcolor="#ffffff", # White cursor
                        bordercolor="#555555",
                        lightcolor="#555555",
                        darkcolor="#222222",
                        font=("Arial", 9))
    style_instance.map("Markers.TEntry",
              fieldbackground=[('focus', '#4a4a4a')]) # Slightly lighter on focus

    style_instance.configure("Markers.TButton",
                        background="#4a4a4a", # Default dark grey button
                        foreground="white",
                        font=("Arial", 9, "bold"),
                        borderwidth=1,
                        relief="raised",
                        focusthickness=2,
                        focuscolor="#007bff") # Blue focus highlight
    style_instance.map("Markers.TButton",
              background=[('active', '#5a5a5a'), # Lighter grey on hover
                          ('pressed', '#3a3a3a')], # Darker grey on press
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])

    style_instance.configure("ActiveScan.TButton",
                        background="#28a745", # Green
                        foreground="#000000", # Black text
                        font=("Arial", 9, "bold"))
    style_instance.map("ActiveScan.TButton",
              background=[('active', '#218838'),
                          ('pressed', '#1e7e34')],
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])


    style_instance.configure("Markers.SelectedButton.TButton",
                        background="#ff8c00", # Orange
                        foreground="#000000", # Black text for contrast
                        font=("Arial", 9, "bold"),
                        borderwidth=2, # Thicker border for selected
                        relief="solid", # Solid border
                        bordercolor="#ffaa00") # Slightly lighter orange border
    style_instance.map("Markers.SelectedButton.TButton",
              background=[('active', '#e67e00'), # Darker orange on hover
                          ('pressed', '#cc7000')], # Even darker on press
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])

    style_instance.configure("DeviceButton.TButton",
                        background="#007bff", # Blue
                        foreground="#ffffff", # White text
                        font=("Arial", 9, "bold"))
    style_instance.map("DeviceButton.TButton",
              background=[('active', '#0056b3'),
                          ('pressed', '#004085')],
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])


    # Updated LargePreset.TButton font size to 10
    style_instance.configure("LargePreset.TButton",
                    background="#4a4a4a",
                    foreground="white",
                    font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                    padding=[30, 15, 30, 15])
    style_instance.map("LargePreset.TButton",
            background=[('active', '#606060')])

    # Updated SelectedPreset.TButton to be orange and font size to 10
    style_instance.configure("SelectedPreset.Orange.TButton", # Renamed style to be explicit
                    background="#ff8c00", # Orange color
                    foreground="white",
                    font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                    padding=[30, 15, 30, 15])
    style_instance.map("SelectedPreset.Orange.TButton",
            background=[('active', '#e07b00')]) # Darker orange on active/hover

    YAK_ORANGE = "#ff8c00"
    style_instance.configure('LargeYAK.TButton',
                    font=('Helvetica', 100, 'bold'),
                    background=YAK_ORANGE,
                    foreground="white",
                    padding=[20, 10])
    style_instance.map('LargeYAK.TButton',
              background=[('active', '#e07b00'), ('disabled', '#cc7000')])

    if debug_print_func:
        debug_print_func(f"🚫🐛 [DEBUG] ttk styles applied from style.py. Version: {current_version}",
                         file=f"src/style.py - {current_version}",
                         function="apply_styles")
