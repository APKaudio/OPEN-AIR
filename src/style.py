# src/style.py
#
# This file centralizes the Tkinter `ttk.Style` configurations for the application.
# It defines custom styles for various widgets, including buttons, labels, entries,
# and especially the nested notebook tabs, ensuring a consistent and modern dark theme.
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
# Version 20250801.1600.11 (Added specific active/inactive styles for each parent notebook tab.
#                      These styles will be applied dynamically in main_app.py's _on_parent_tab_change.
#                      Updated debug prints to new format.)

import tkinter as tk
from tkinter import ttk

def apply_styles(style, debug_print, current_version, parent_tab_colors):
    """
    Configures and applies custom ttk styles for a modern dark theme
    to various Tkinter widgets within the application. This includes
    defining styles for parent and child notebooks to support the
    two-layer tab structure with unique and dynamic colors for parent tabs.

    Inputs:
        style (ttk.Style): The ttk.Style object of the main application.
        debug_print (function): Function to print debug messages to the GUI console.
        current_version (str): The current version string of the application.
        parent_tab_colors (dict): A dictionary containing color mappings for parent tabs.

    Process:
        1. Sets the ttk theme to 'clam'.
        2. Defines a set of consistent color variables for the theme.
        3. Configures styles for general widgets like `TFrame`, `TLabel`, `TEntry`, `TCombobox`.
        4. Defines and maps styles for various `TButton` types (default, Blue, Green, Red, Orange, Purple, LargeYAK).
        5. Configures styles for `TCheckbutton`, `TLabelFrame`, and `TNotebook` (tabs).
        6. Defines specific styles for parent notebooks, including unique
           backgrounds for selected and unselected parent tabs.
        7. Configures styles for `Treeview` widgets (headings and rows).
        8. Defines specific styles for the "Markers Tab".

    Outputs:
        None. Applies visual styling to the application's GUI.
    """
    debug_print(f"🚫🐛 [DEBUG] Applying ttk styles from src/style.py... Version: {current_version}",
                file=f"src/style.py - {current_version}",
                function=apply_styles.__name__)

    style.theme_use('clam')

    # General background and foreground colors
    BG_DARK = "#1e1e1e"
    FG_LIGHT = "#cccccc"
    ACCENT_BLUE = "#007bff"
    ACCENT_GREEN = "#28a745"
    ACCENT_RED = "#dc3545"
    ACCENT_ORANGE = "#ffc107"
    ACCENT_PURPLE = "#6f42c1"

    style.configure('.', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10))
    style.configure('TFrame', background=BG_DARK)
    style.configure('TLabel', background=BG_DARK, foreground=FG_LIGHT)
    style.configure('TEntry', fieldbackground="#3b3b3b", foreground="#ffffff", borderwidth=1, relief="flat")
    style.map('TEntry', fieldbackground=[('focus', '#4a4a4a')])
    style.configure('TCombobox', fieldbackground="#3b3b3b", foreground="#ffffff", selectbackground=ACCENT_BLUE, selectforeground="white")
    style.map('TCombobox', fieldbackground=[('readonly', '#3b3b3b')], arrowcolor=[('!disabled', FG_LIGHT)])

    # Buttons
    style.configure('TButton',
                    background="#4a4a4a",
                    foreground="white",
                    font=('Helvetica', 10, 'bold'),
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor=ACCENT_BLUE,
                    padding=5)
    style.map('TButton',
            background=[('active', '#606060'), ('disabled', '#303030')],
            foreground=[('disabled', '#808060')])

    # Specific button styles
    style.configure('Blue.TButton', background=ACCENT_BLUE, foreground="white")
    style.map('Blue.TButton', background=[('active', '#0056b3'), ('disabled', '#004085')])

    style.configure('Green.TButton', background=ACCENT_GREEN, foreground="white")
    style.map('Green.TButton', background=[('active', '#218838'), ('disabled', '#1e7e34')])

    style.configure('Red.TButton', background=ACCENT_RED, foreground="white")
    style.map('Red.TButton', background=[('active', '#c82333'), ('disabled', '#bd2130')])

    style.configure('Orange.TButton', background=ACCENT_ORANGE, foreground="#333333")
    style.map('Orange.TButton', background=[('active', '#e0a800'), ('disabled', '#d39e00')])

    style.configure('Purple.TButton', background=ACCENT_PURPLE, foreground="white")
    style.map('Purple.TButton', background=[('active', '#5a2d9e'), ('disabled', '#4d2482')])

    # Big Scan Buttons (30pt font)
    style.configure('BigScanButton.TButton',
                    font=('Helvetica', 30, 'bold'), # 30pt font
                    borderwidth=0,
                    focusthickness=3,
                    padding=[10, 5]) # Adjust padding for larger font
    style.map('BigScanButton.TButton',
              focuscolor=ACCENT_BLUE)

    style.configure('BigScanButton.Green.TButton',
                    background=ACCENT_GREEN,
                    foreground="white")
    style.map('BigScanButton.Green.TButton',
              background=[('active', '#218838'), ('disabled', '#1e7e34')],
              foreground=[('disabled', '#808060')])

    style.configure('BigScanButton.Orange.TButton',
                    background=ACCENT_ORANGE,
                    foreground="#333333")
    style.map('BigScanButton.Orange.TButton',
              background=[('active', '#e0a800'), ('disabled', '#d39e00')],
              foreground=[('disabled', '#808060')])

    style.configure('BigScanButton.Red.TButton',
                    background=ACCENT_RED,
                    foreground="white")
    style.map('BigScanButton.Red.TButton',
              background=[('active', '#c82333'), ('disabled', '#bd2130')],
              foreground=[('disabled', '#808060')])

    style.configure('BigScanButton.Disabled.TButton',
                    background='#303030',
                    foreground='#808060')


    # Flashing Button Styles (30pt font)
    style.configure('FlashingGreen.TButton',
                    background=ACCENT_GREEN,
                    foreground="white",
                    font=('Helvetica', 30, 'bold')) # Ensure 30pt font
    style.map('FlashingGreen.TButton',
              background=[('active', ACCENT_GREEN), ('!active', ACCENT_GREEN)]) # Keep color consistent

    style.configure('FlashingDark.TButton',
                    background="#2b2b2b", # Dark background for flashing
                    foreground="white",
                    font=('Helvetica', 30, 'bold')) # Ensure 30pt font
    style.map('FlashingDark.TButton',
              background=[('active', "#2b2b2b"), ('!active', "#2b2b2b")]) # Keep color consistent


    # Checkbuttons
    style.configure('TCheckbutton', background=BG_DARK, foreground=FG_LIGHT, indicatorcolor="#4a4a4a")
    style.map('TCheckbutton',
            background=[('active', BG_DARK)],
            foreground=[('disabled', '#808080')],
            indicatorcolor=[('selected', ACCENT_BLUE)])

    # LabelFrame
    style.configure('TLabelFrame', background=BG_DARK, foreground=FG_LIGHT, borderwidth=1, relief="solid")
    style.configure('TLabelFrame.Label', background=BG_DARK, foreground=FG_LIGHT, font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background="#1e1e1e", foreground="#cccccc")
    style.configure('Dark.TLabelframe.Label', background="#1e1e1e", foreground="#cccccc")
    style.configure('Dark.TFrame', background="#1e1e1e")

    # --- Parent Notebook Styles ---
    # Generic Parent Notebook style (for the notebook frame itself)
    style.configure('Parent.TNotebook', background=BG_DARK, borderwidth=0)
    # Configure the tab elements directly for Parent.TNotebook.Tab
    # This will apply to ALL parent tabs. We use style.map for state-based changes.
    style.configure('Parent.TNotebook.Tab',
                         background="#3b3b3b", # Default inactive background
                         foreground=FG_LIGHT,
                         padding=[15, 8],
                         font=('Helvetica', 11, 'bold'))

    # Map colors for Parent.TNotebook.Tab based on state
    style.map('Parent.TNotebook.Tab',
                   background=[('selected', ACCENT_BLUE), ('active', ACCENT_BLUE)], # Common active color
                   foreground=[('selected', 'white'), ('active', 'white')],
                   expand=[('selected', [1, 1, 1, 0])]) # Expand selected tab

    # NEW: Specific styles for each parent tab (Active and Inactive states)
    # These styles are applied to the individual tabs using notebook.tab(tab_id, style=...)
    for tab_name, colors in parent_tab_colors.items():
        # Active style for the specific parent tab
        style.configure(f'Parent.Tab.{tab_name}.Active',
                        background=colors["active"],
                        foreground=colors["fg_active"],
                        font=('Helvetica', 11, 'bold')) # Keep font consistent
        style.map(f'Parent.Tab.{tab_name}.Active',
                  background=[('active', colors["active"])], # Keep color on hover when active
                  foreground=[('active', colors["fg_active"])])

        # Inactive style for the specific parent tab
        style.configure(f'Parent.Tab.{tab_name}.Inactive',
                        background=colors["inactive"],
                        foreground=colors["fg_inactive"],
                        font=('Helvetica', 11, 'bold')) # Keep font consistent
        style.map(f'Parent.Tab.{tab_name}.Inactive',
                  background=[('active', colors["active"])], # Change to active color on hover when inactive
                  foreground=[('active', colors["fg_active"])])


    # --- Child Notebook Styles (Matching Parent Colors) ---
    # These styles are applied to the *child notebooks themselves* and their tabs.
    # Instrument Child Notebook Tabs (Red)
    style.configure('InstrumentChild.TNotebook', background=parent_tab_colors["INSTRUMENT"]["active"], borderwidth=0)
    style.configure('InstrumentChild.TNotebook.Tab', background=parent_tab_colors["INSTRUMENT"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
    style.map('InstrumentChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["INSTRUMENT"]["active"]), ('active', parent_tab_colors["INSTRUMENT"]["active"])],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])

    # Scanning Child Notebook Tabs (Orange)
    style.configure('ScanningChild.TNotebook', background=parent_tab_colors["SCANNING"]["active"], borderwidth=0)
    style.configure('ScanningChild.TNotebook.Tab', background=parent_tab_colors["SCANNING"]["inactive"], foreground=BG_DARK, padding=[10, 5])
    style.map('ScanningChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["SCANNING"]["active"]), ('active', parent_tab_colors["SCANNING"]["active"])],
            foreground=[('selected', BG_DARK)],
            expand=[('selected', [1, 1, 1, 0])])

    # Plotting Child Notebook Tabs (Yellow)
    style.configure('PlottingChild.TNotebook', background=parent_tab_colors["PLOTTING"]["active"], borderwidth=0)
    style.configure('PlottingChild.TNotebook.Tab', background=parent_tab_colors["PLOTTING"]["inactive"], foreground=BG_DARK, padding=[10, 5])
    style.map('PlottingChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["PLOTTING"]["active"]), ('active', parent_tab_colors["PLOTTING"]["active"])],
            foreground=[('selected', 'black')], # Black foreground for yellow for better contrast
            expand=[('selected', [1, 1, 1, 0])])


    # Markers Child Notebook Tabs (Green)
    style.configure('MarkersChild.TNotebook', background=parent_tab_colors["MARKERS"]["active"], borderwidth=0)
    style.configure('MarkersChild.TNotebook.Tab', background=parent_tab_colors["MARKERS"]["inactive"], foreground=BG_DARK, padding=[10, 5])
    style.map('MarkersChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["MARKERS"]["active"]), ('active', parent_tab_colors["MARKERS"]["active"])],
            foreground=[('selected', BG_DARK)], # White foreground for green
            expand=[('selected', [1, 1, 1, 0])])

    # Presets Child Notebook Tabs (Blue)
    style.configure('PresetsChild.TNotebook', background=parent_tab_colors["PRESETS"]["active"], borderwidth=0)
    style.configure('PresetsChild.TNotebook.Tab', background=parent_tab_colors["PRESETS"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
    style.map('PresetsChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["PRESETS"]["active"]), ('active', parent_tab_colors["PRESETS"]["active"])],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])

    # Experiments Child Notebook Tabs (Purple)
    style.configure('ExperimentsChild.TNotebook', background=parent_tab_colors["EXPERIMENTS"]["active"], borderwidth=0)
    style.configure('ExperimentsChild.TNotebook.Tab', background=parent_tab_colors["EXPERIMENTS"]["inactive"], foreground=FG_LIGHT, padding=[10, 5])
    style.map('ExperimentsChild.TNotebook.Tab',
            background=[('selected', parent_tab_colors["EXPERIMENTS"]["active"]), ('active', parent_tab_colors["EXPERIMENTS"]["active"])],
            foreground=[('selected', 'white')],
            expand=[('selected', [1, 1, 1, 0])])


    # Treeview (for MarkersDisplayTab and VisaInterpreterTab)
    style.configure('Treeview',
                    background="#3b3b3b",
                    foreground="#ffffff",
                    fieldbackground="#3b3b3b",
                    rowheight=25)
    style.map('Treeview',
            background=[('selected', ACCENT_BLUE)],
            foreground=[('selected', 'white')])

    style.configure('Treeview.Heading',
                    background="#4a4a4a",
                    foreground="white",
                    font=('Helvetica', 10, "bold"))
    style.map('Treeview.Heading',
            background=[('active', '#606060')])

    # Markers Tab Specific Styles (from the immersive artifact)
    style.configure("Markers.TFrame",
                        background="#1e1e1e", # Dark background for the main markers tab frame
                        foreground="#cccccc") # Light grey text for general labels

    style.configure("Dark.TLabelframe",
                        background="#2b2b2b", # Slightly lighter dark for labelled frames
                        foreground="#ffffff", # White text for the labelframe title
                        bordercolor="#444444",
                        lightcolor="#444444",
                        darkcolor="#1a1a1a")
    style.map("Dark.TLabelframe",
              background=[('active', '#3a3a3a')]) # Subtle change on active

    style.configure("Dark.TLabelframe.Label",
                        background="#2b2b2b",
                        foreground="#ffffff",
                        font=("Arial", 10, "bold"))

    style.configure("Dark.TFrame",
                        background="#1e1e1e") # For inner frames without a label

    style.configure("Markers.Inner.Treeview",
                        background="#2b2b2b", # Dark background for treeview
                        foreground="#cccccc", # Light grey text
                        fieldbackground="#2b2b2b",
                        bordercolor="#444444",
                        lightcolor="#444444",
                        darkcolor="#1a1a1a",
                        font=("Arial", 9))
    style.map("Markers.Inner.Treeview",
              background=[('selected', '#555555')], # Darker grey when selected
              foreground=[('selected', '#ffffff')]) # White text when selected

    style.configure("Markers.TLabel",
                        background="#1e1e1e", # Dark background for labels
                        foreground="#cccccc", # Light grey text
                        font=("Arial", 9))

    style.configure("Markers.TEntry",
                        fieldbackground="#3a3a3a", # Darker input field
                        foreground="#ffffff", # White text
                        insertcolor="#ffffff", # White cursor
                        bordercolor="#555555",
                        lightcolor="#555555",
                        darkcolor="#222222",
                        font=("Arial", 9))
    style.map("Markers.TEntry",
              fieldbackground=[('focus', '#4a4a4a')]) # Slightly lighter on focus

    style.configure("Markers.TButton",
                        background="#4a4a4a", # Default dark grey button
                        foreground="white",
                        font=("Arial", 9, "bold"),
                        borderwidth=1,
                        relief="raised",
                        focusthickness=2,
                        focuscolor="#007bff") # Blue focus highlight
    style.map("Markers.TButton",
              background=[('active', '#5a5a5a'), # Lighter grey on hover
                          ('pressed', '#3a3a3a')], # Darker grey on press
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])

    style.configure("ActiveScan.TButton",
                        background="#28a745", # Green
                        foreground="#000000", # Black text
                        font=("Arial", 9, "bold"))
    style.map("ActiveScan.TButton",
              background=[('active', '#218838'),
                          ('pressed', '#1e7e34')],
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])


    style.configure("Markers.SelectedButton.TButton",
                        background="#ff8c00", # Orange
                        foreground="#000000", # Black text for contrast
                        font=("Arial", 9, "bold"),
                        borderwidth=2, # Thicker border for selected
                        relief="solid", # Solid border
                        bordercolor="#ffaa00") # Slightly lighter orange border
    style.map("Markers.SelectedButton.TButton",
              background=[('active', '#e67e00'), # Darker orange on hover
                          ('pressed', '#cc7000')], # Even darker on press
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])

    style.configure("DeviceButton.TButton",
                        background="#007bff", # Blue
                        foreground="#ffffff", # White text
                        font=("Arial", 9, "bold"))
    style.map("DeviceButton.TButton",
              background=[('active', '#0056b3'),
                          ('pressed', '#004085')],
              foreground=[('active', '#ffffff'),
                          ('pressed', '#ffffff')])


    # Updated LargePreset.TButton font size to 10
    style.configure("LargePreset.TButton",
                    background="#4a4a4a",
                    foreground="white",
                    font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                    padding=[30, 15, 30, 15])
    style.map("LargePreset.TButton",
            background=[('active', '#606060')])

    # Updated SelectedPreset.TButton to be orange and font size to 10
    style.configure("SelectedPreset.Orange.TButton", # Renamed style to be explicit
                    background="#ff8c00", # Orange color
                    foreground="white",
                    font=("Helvetica", 10, "bold"), # Changed font size from 14 to 10
                    padding=[30, 15, 30, 15])
    style.map("SelectedPreset.Orange.TButton",
            background=[('active', '#e07b00')]) # Darker orange on active/hover

    YAK_ORANGE = "#ff8c00"
    style.configure('LargeYAK.TButton',
                    font=('Helvetica', 100, 'bold'),
                    background=YAK_ORANGE,
                    foreground="white",
                    padding=[20, 10])
    style.map('LargeYAK.TButton',
              background=[('active', '#e07b00'), ('disabled', '#cc7000')])

    debug_print(f"🚫🐛 [DEBUG] ttk styles applied from src/style.py. Version: {current_version}",
                file=f"src/style.py - {current_version}",
                function=apply_styles.__name__)

