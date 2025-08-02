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
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250802.0065.1 (Added BigScanButton style definition.)

current_version = "20250802.0065.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 65 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect # For debug_log

# Import the debug logic module to use debug_log
from src.debug_logic import debug_log


def apply_styles(style, debug_log_func, current_app_version, parent_tab_colors):
    """
    Function Description:
    Applies custom Tkinter ttk styles for a consistent and modern dark theme
    across the application. This includes general widget styles, and specific
    styles for parent and child notebook tabs to support the two-layer tab structure.

    Inputs:
        style (ttk.Style): The ttk.Style object to configure.
        debug_log_func (function): The debug logging function (e.g., debug_log from src.debug_logic).
        current_app_version (str): The current version of the main application, for logging.
        parent_tab_colors (dict): A dictionary containing color mappings for parent tabs.

    Process of this function:
        1. Sets the overall theme to 'clam'.
        2. Configures general styles for 'TFrame', 'TLabelframe', 'TLabel', 'TEntry', 'TCombobox'.
        3. Defines specific button styles:
           - 'TButton' (default dark grey)
           - 'Green.TButton' (for success/connect actions)
           - 'Red.TButton' (for disconnect/stop actions)
           - 'Orange.TButton' (for save/warning actions)
           - 'Blue.TButton' (for general actions)
           - 'BigScanButton' (new, larger style for scan controls)
           - 'LargePreset.TButton' (for preset buttons)
           - 'SelectedPreset.Orange.TButton' (for selected preset buttons)
           - 'LargeYAK.TButton' (for YAK button)
           - 'DeviceButton.TButton' (for device buttons)
           - 'ActiveScan.TButton' (for actively scanned device buttons)
           - 'Markers.TButton' (general marker tab buttons)
           - 'Markers.SelectedButton.TButton' (selected marker tab buttons)
           - 'Markers.TLabel', 'Markers.TLabelframe', 'Markers.TEntry', 'Markers.Treeview'
        4. Configures Notebook styles for parent and child tabs, including dynamic
           tab colors based on `parent_tab_colors`.
        5. Logs the application of styles.

    Outputs of this function:
        None. Modifies the global ttk.Style configuration.

    (2025-07-30) Change: Initial implementation of apply_styles.
    (2025-07-31) Change: Added styles for parent and child notebooks, including dynamic tab colors.
    (2025-07-31) Change: Added styles for progressbar and specific button types (Connect, Disconnect, etc.).
    (2025-07-31) Change: Added 'Markers.TFrame', 'Markers.TLabel', 'Markers.TLabelframe', 'Markers.TEntry' styles.
    (2025-07-31) Change: Added 'Markers.Treeview' style.
    (2025-07-31) Change: Added 'BigScanButton' style for larger scan control buttons.
    (2025-07-31) Change: Added 'LargePreset.TButton' and 'SelectedPreset.Orange.TButton' styles.
    (2025-07-31) Change: Added 'LargeYAK.TButton' style.
    (2025-07-31) Change: Added 'DeviceButton.TButton' and 'ActiveScan.TButton' styles.
    (2025-07-31) Change: Added 'Markers.SelectedButton.TButton' for unified selected style.
    (2025-08-01) Change: Refactored debug_print to debug_log.
    (2025-08-01) Change: Fixed parent tab styling to use style.map for correct active/inactive states.
    (2025-08-01) Change: Added styles for connection status labels (Green.TLabel, Red.TLabel).
    (2025-08-02 0060.1) Change: Added BigScanButton style definition.
    (2025-08-02 0065.1) Change: Updated BigScanButton style to blue.
    """
    debug_log_func(f"Applying custom Tkinter styles. Version: {current_version}. Making things look pretty!",
                    file=__file__,
                    version=current_app_version, # Use app_instance's version for logging context
                    function=inspect.currentframe().f_code.co_name)

    # Set the theme
    style.theme_use('clam')

    # --- General Styles ---
    style.configure('TFrame', background='#2b2b2b')
    style.configure('Dark.TFrame', background='#2b2b2b') # Specific dark frame style

    style.configure('TLabelframe', background='#2b2b2b', foreground='white', font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background='#2b2b2b', foreground='white', font=('Helvetica', 10, 'bold')) # Specific dark labelframe style

    style.configure('TLabel', background='#2b2b2b', foreground='white', font=('Helvetica', 9))
    style.configure('Green.TLabel', background='#2b2b2b', foreground='#4CAF50', font=('Helvetica', 10, 'bold')) # Green text for connected
    style.configure('Red.TLabel', background='#2b2b2b', foreground='#F44336', font=('Helvetica', 10, 'bold'))   # Red text for disconnected

    style.configure('TEntry', fieldbackground='#3c3c3c', foreground='white', borderwidth=1, relief="solid")
    style.map('TEntry', fieldbackground=[('focus', '#4a4a4a')])

    style.configure('TCombobox', fieldbackground='#3c3c3c', foreground='white', selectbackground='#3c3c3c', selectforeground='white')
    style.map('TCombobox', fieldbackground=[('readonly', '#3c3c3c')])

    # --- Button Styles ---
    style.configure('TButton',
                    background='#4a4a4a',
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('TButton',
              background=[('active', '#606060'), ('disabled', '#3a3a3a')],
              foreground=[('disabled', '#808080')])

    style.configure('Green.TButton',
                    background='#4CAF50', # Green
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Green.TButton',
              background=[('active', '#66BB6A'), ('disabled', '#2E7D32')])

    style.configure('Red.TButton',
                    background='#F44336', # Red
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Red.TButton',
              background=[('active', '#EF5350'), ('disabled', '#C62828')])

    style.configure('Orange.TButton',
                    background='#FF9800', # Orange
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Orange.TButton',
              background=[('active', '#FFB74D'), ('disabled', '#E65100')])

    style.configure('Blue.TButton',
                    background='#2196F3', # Blue
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Blue.TButton',
              background=[('active', '#64B5F6'), ('disabled', '#1565C0')])

    # NEW: Big Scan Button Style - Changed to blue
    style.configure('BigScanButton',
                    background='#007acc', # Blue
                    foreground='white',
                    font=('Helvetica', 12, 'bold'), # Larger font
                    padding=[20, 10], # More padding
                    relief="raised", # Raised effect
                    borderwidth=2,
                    focusthickness=0)
    style.map('BigScanButton',
              background=[('active', '#005f99'), ('disabled', '#3a3a3a')], # Darker blue on active
              foreground=[('disabled', '#808080')])

    # Preset Buttons
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
              background=[('active', '#e07b00')]) # Darker orange on active
    
    # Device Buttons (for MarkersDisplayTab)
    style.configure('DeviceButton.TButton',
                    background='#2196F3', # Blue
                    foreground='white',
                    font=('Helvetica', 8, 'bold'),
                    padding=[5, 5, 5, 5], # Smaller padding for more buttons
                    relief="flat",
                    focusthickness=0)
    style.map('DeviceButton.TButton',
              background=[('active', '#64B5F6'), ('disabled', '#1565C0')])

    # Active Scan Button (for MarkersDisplayTab - when a device is actively being scanned)
    style.configure('ActiveScan.TButton',
                    background='#4CAF50', # Green
                    foreground='black', # Black font for contrast on green
                    font=('Helvetica', 8, 'bold'),
                    padding=[5, 5, 5, 5],
                    relief="flat",
                    focusthickness=0)
    style.map('ActiveScan.TButton',
              background=[('active', '#66BB6A'), ('disabled', '#2E7D32')])


    # Markers Tab Specific Styles
    style.configure('Markers.TFrame', background='#1e1e1e')
    style.configure('Markers.TLabelframe', background='#1e1e1e', foreground='#cccccc', font=('Helvetica', 10, 'bold'))
    style.configure('Markers.TLabel', background='#1e1e1e', foreground='#cccccc', font=('Helvetica', 9))
    style.configure('Markers.TEntry', fieldbackground='#333333', foreground='#cccccc', borderwidth=1, relief="solid")
    style.map('Markers.TEntry', fieldbackground=[('focus', '#444444')])

    # Markers Tab Buttons (general) - default blue
    style.configure('Markers.TButton',
                    background='#2196F3', # Blue
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.TButton',
              background=[('active', '#64B5F6'), ('disabled', '#1565C0')])

    # Markers Tab Selected Button (orange)
    style.configure('Markers.SelectedButton.TButton',
                    background='#FF9800', # Orange
                    foreground='white',
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.SelectedButton.TButton',
              background=[('active', '#FFB74D'), ('disabled', '#E65100')])


    # Treeview Style for Marker Editor
    style.configure("Treeview",
                    background="#333333",
                    foreground="white",
                    fieldbackground="#333333",
                    font=("Helvetica", 9))
    style.map("Treeview",
              background=[('selected', '#007acc')], # Blue selection
              foreground=[('selected', 'white')])

    style.configure("Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background="#4a4a4a",
                    foreground="white",
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', '#606060')])

    # Treeview Style for Zones & Groups (MarkersDisplayTab)
    style.configure("Markers.Inner.Treeview",
                    background="#333333",
                    foreground="white",
                    fieldbackground="#333333",
                    font=("Helvetica", 9))
    style.map("Markers.Inner.Treeview",
              background=[('selected', '#007acc')], # Blue selection
              foreground=[('selected', 'white')])

    style.configure("Markers.Inner.Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background="#4a4a4a",
                    foreground="white",
                    relief="flat")
    style.map("Markers.Inner.Treeview.Heading",
              background=[('active', '#606060')])


    # --- Notebook (Tab) Styles for Parent Tabs ---
    style.configure("Parent.TNotebook",
                    background="#2e2e2e",
                    tabposition='nw',
                    borderwidth=0) # Remove border around the notebook itself

    # Configure the actual tab elements for parent tabs
    style.configure("Parent.TNotebook.Tab",
                    background="#4a4a4a", # Default inactive tab color
                    foreground="white",
                    font=("Helvetica", 10, "bold"),
                    padding=[10, 5],
                    relief="flat",
                    borderwidth=0) # Remove border around individual tabs

    # Map colors for each parent tab dynamically based on selection state
    for tab_name, colors in parent_tab_colors.items():
        # Active state for selected tab
        style.map("Parent.TNotebook.Tab",
                  background=[('selected', colors['active']), ('active', colors['active'])],
                  foreground=[('selected', colors['fg_active']), ('active', colors['fg_active'])],
                  bordercolor=[('selected', colors['active'])], # Border color matches tab color when selected
                  lightcolor=[('selected', colors['active'])],
                  darkcolor=[('selected', colors['active'])],
                  expand=[('selected', [0,0,0,0])], # No expansion when selected
                  sticky=[('selected', 'nsew')],
                  )
        # Inactive state for unselected tabs
        style.map("Parent.TNotebook.Tab",
                  background=[('!selected', colors['inactive']), ('!selected', colors['inactive'])],
                  foreground=[('!selected', colors['fg_inactive']), ('!selected', colors['fg_inactive'])],
                  bordercolor=[('!selected', '#2e2e2e')], # Border color matches notebook background when inactive
                  lightcolor=[('!selected', '#2e2e2e')],
                  darkcolor=[('!selected', '#2e2e2e')],
                  expand=[('!selected', [0,0,0,0])], # No expansion when unselected
                  sticky=[('!selected', 'nsew')],
                  )

    # --- Notebook (Tab) Styles for Child Tabs ---
    style.configure("Child.TNotebook",
                    background="#2e2e2e",
                    tabposition='n',
                    borderwidth=0)

    style.configure("Child.TNotebook.Tab",
                    background="#444444", # Default background for child tabs
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4],
                    relief="flat",
                    borderwidth=0)

    style.map("Child.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')],
              bordercolor=[('selected', '#555555')],
              lightcolor=[('selected', '#555555')],
              darkcolor=[('selected', '#555555')],
              expand=[('selected', [0,0,0,0])],
              sticky=[('selected', 'nsew')],
              )

    debug_log_func(f"Custom Tkinter styles applied successfully. The GUI is looking sharp! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function="The styles defition",
                    special=True)

