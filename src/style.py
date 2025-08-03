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
# Version 20250802.0148.1 (Explicitly copied TLabel layout for Dark.TLabel.Value to force registration.)
# Version 20250802.2245.0 (Introduced COLOR_PALETTE for shared color definitions.)
# Version 20250803.0005.0 (Adjusted LargePreset.TButton and SelectedPreset.Orange.TButton font sizes to 30pt.)
# Version 20250803.0010.0 (FIXED: SyntaxError: leading zeros in decimal integer literals by correcting current_version_hash.)
# Version 20250803.0020.0 (Adjusted LargePreset.TButton and SelectedPreset.Orange.TButton font sizes to 25pt.)

current_version = "20250803.0020.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 20 * 0 # Example hash, adjust as needed.

import tkinter as tk
from tkinter import ttk, TclError
import inspect # For debug_log

# Import the debug logic module to use debug_log
from src.debug_logic import debug_log

# --- Global Color Palette Definition ---
# This dictionary defines the color scheme for the application.
# It can be imported and used by other modules to ensure consistent theming.
COLOR_PALETTE = {
    'background': '#2b2b2b',
    'foreground': 'white',
    'input_bg': '#3c3c3c',
    'input_fg': 'white',
    'select_bg': '#007acc', # Blue for selected items
    'select_fg': 'white',
    'active_bg': '#606060', # General active/hover background
    'disabled_bg': '#3a3a3a', # Dark grey for disabled elements
    'disabled_fg': '#808080',

    # Specific button colors
    'green_btn': '#4CAF50',
    'green_btn_active': '#66BB6A',
    'green_btn_disabled': '#2E7D32',
    'red_btn': '#F44336',
    'red_btn_active': '#EF5350',
    'red_btn_disabled': '#C62828',
    'orange_btn': '#FF9800',
    'orange_btn_active': '#FFB74D',
    'orange_btn_disabled': '#E65100',
    'blue_btn': '#2196F3',
    'blue_btn_active': '#64B5F6',
    'blue_btn_disabled': '#1565C0',
    'purple_btn': '#9C27B0', # Added for export
    'purple_btn_active': '#BA68C8',
    'purple_btn_disabled': '#7B1FA2',

    # Text colors
    'value_fg': '#ADD8E6', # Light blue for values

    # Parent Tab Colors (as previously defined in main_app)
    'parent_tabs': {
        'Instrument': {'active': '#336699', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'},
        'Scan': {'active': '#669933', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'},
        'Presets': {'active': '#993366', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'},
        'Markers': {'active': '#339966', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'},
        'Settings': {'active': '#996633', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'},
        'About': {'active': '#663399', 'inactive': '#4a4a4a', 'fg_active': 'white', 'fg_inactive': 'white'}
    }
}


def apply_styles(style, debug_log_func, current_app_version):
    """
    Function Description:
    Applies custom Tkinter ttk styles for a consistent and modern dark theme
    across the application. This includes general widget styles, and specific
    styles for parent and child notebook tabs to support the two-layer tab structure.

    Inputs:
        style (ttk.Style): The ttk.Style object to configure.
        debug_log_func (function): The debug logging function (e.g., debug_log from src.debug_logic).
        current_app_version (str): The current version of the main application, for logging.

    Process of this function:
        1. Sets the overall theme to 'clam'.
        2. Configures general styles for 'TFrame', 'TLabelframe', 'TLabel', 'TEntry', 'TCombobox'.
        3. Defines specific button styles.
        4. Configures Notebook styles for parent and child tabs, using COLOR_PALETTE.
        5. Logs the application of styles.

    Outputs of this function:
        None. Modifies the global ttk.Style configuration.
    """
    debug_log_func(f"Applying custom Tkinter styles. Version: {current_version}. Making things look pretty!",
                    file=__file__,
                    version=current_app_version, # Use app_instance's version for logging context
                    function=inspect.currentframe().f_code.co_name)

    # Set the theme
    style.theme_use('clam')

    # --- General Styles ---
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('Dark.TFrame', background=COLOR_PALETTE['background']) # Specific dark frame style

    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold')) # Specific dark labelframe style

    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))

    # FUCKING IMPORTANT: Explicitly get TLabel layout and apply it to Dark.TLabel.Value
    try:
        tlabel_layout = style.layout('TLabel')
        style.layout('Dark.TLabel.Value', tlabel_layout)
        debug_log_func(f"Copied TLabel layout to Dark.TLabel.Value. This should finally register the damn thing! Version: {current_version}",
                        file=__file__,
                        version=current_app_version,
                        function=inspect.currentframe().f_code.co_name,
                        special=True)
    except TclError as e:
        debug_log_func(f"CRITICAL ERROR: Failed to copy TLabel layout for Dark.TLabel.Value: {e}. This is some serious bullshit! Version: {current_version}",
                        file=__file__,
                        version=current_app_version,
                        function=inspect.currentframe().f_code.co_name,
                        special=True)

    # NEW: Style for Dark.TLabel.Value - now that its layout is explicitly defined
    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 9, 'bold')) # Light blue for values


    style.configure('Green.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['green_btn'], font=('Helvetica', 10, 'bold')) # Green text for connected
    style.configure('Red.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))   # Red text for disconnected

    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], borderwidth=1, relief="solid")
    style.map('TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])

    style.configure('TCombobox', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], selectbackground=COLOR_PALETTE['input_bg'], selectforeground=COLOR_PALETTE['input_fg'])
    style.map('TCombobox', fieldbackground=[('readonly', COLOR_PALETTE['input_bg'])])

    # --- Button Styles ---
    style.configure('TButton',
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('TButton',
              background=[('active', COLOR_PALETTE['active_bg']), ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    style.configure('Green.TButton',
                    background=COLOR_PALETTE['green_btn'], # Green
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Green.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])])

    style.configure('Red.TButton',
                    background=COLOR_PALETTE['red_btn'], # Red
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Red.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']), ('disabled', COLOR_PALETTE['red_btn_disabled'])])

    style.configure('Orange.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Orange.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])

    style.configure('Blue.TButton',
                    background=COLOR_PALETTE['blue_btn'], # Blue
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Blue.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active']), ('disabled', COLOR_PALETTE['blue_btn_disabled'])])

    # NEW: Specific Scan Button Styles
    style.configure('StartScan.TButton',
                    background=COLOR_PALETTE['green_btn'], # Green
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'), # Larger font
                    padding=[20, 10], # More padding
                    relief="raised", # Raised effect
                    borderwidth=2,
                    focusthickness=0)
    style.map('StartScan.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    style.configure('PauseScan.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('PauseScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])

    style.configure('ResumeScan.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange (base for blinking)
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('ResumeScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    style.configure('StopScan.TButton',
                    background=COLOR_PALETTE['red_btn'], # Red
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('StopScan.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']), ('disabled', COLOR_PALETTE['red_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])


    # Preset Buttons
    style.configure("LargePreset.TButton",
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 25, "bold"), # Changed font size from 30 to 25
                    padding=[30, 15, 30, 15])
    style.map("LargePreset.TButton",
            background=[('active', COLOR_PALETTE['active_bg'])])

    # Updated SelectedPreset.TButton to be orange and font size to 25
    style.configure("SelectedPreset.Orange.TButton", # Renamed style to be explicit
                    background=COLOR_PALETTE['orange_btn'], # Orange color
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 25, "bold"), # Changed font size from 30 to 25
                    padding=[30, 15, 30, 15])
    style.map("SelectedPreset.Orange.TButton",
            background=[('active', COLOR_PALETTE['orange_btn_active'])]) # Darker orange on active/hover

    YAK_ORANGE = COLOR_PALETTE['orange_btn'] # Use from palette
    style.configure('LargeYAK.TButton',
                    font=('Helvetica', 100, 'bold'),
                    background=YAK_ORANGE,
                    foreground=COLOR_PALETTE['foreground'],
                    padding=[20, 10])
    style.map('LargeYAK.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])]) # Darker orange on active
    
    # Device Buttons (for MarkersDisplayTab)
    style.configure('DeviceButton.TButton',
                    background=COLOR_PALETTE['blue_btn'], # Blue
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 8, 'bold'),
                    padding=[5, 5, 5, 5], # Smaller padding for more buttons
                    relief="flat",
                    focusthickness=0)
    style.map('DeviceButton.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active']), ('disabled', COLOR_PALETTE['blue_btn_disabled'])])

    # Active Scan Button (for MarkersDisplayTab - when a device is actively being scanned)
    style.configure('ActiveScan.TButton',
                    background=COLOR_PALETTE['green_btn'], # Green
                    foreground='black', # Black font for contrast on green
                    font=('Helvetica', 8, 'bold'),
                    padding=[5, 5, 5, 5],
                    relief="flat",
                    focusthickness=0)
    style.map('ActiveScan.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])])


    # Markers Tab Specific Styles
    style.configure('Markers.TFrame', background=COLOR_PALETTE['background'])
    style.configure('Markers.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Markers.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    style.configure('Markers.TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], borderwidth=1, relief="solid")
    style.map('Markers.TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])

    # Markers Tab Buttons (general) - default blue
    style.configure('Markers.TButton',
                    background=COLOR_PALETTE['blue_btn'], # Blue
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active']), ('disabled', COLOR_PALETTE['blue_btn_disabled'])])

    # Markers Tab Selected Button (orange)
    style.configure('Markers.SelectedButton.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.SelectedButton.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])


    # Treeview Style for Marker Editor
    style.configure("Treeview",
                    background=COLOR_PALETTE['input_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    fieldbackground=COLOR_PALETTE['input_bg'],
                    font=("Helvetica", 9))
    style.map("Treeview",
              background=[('selected', COLOR_PALETTE['select_bg'])], # Blue selection
              foreground=[('selected', COLOR_PALETTE['select_fg'])])

    style.configure("Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', COLOR_PALETTE['active_bg'])])

    # Treeview Style for Zones & Groups (MarkersDisplayTab)
    style.configure("Markers.Inner.Treeview",
                    background=COLOR_PALETTE['input_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    fieldbackground=COLOR_PALETTE['input_bg'],
                    font=("Helvetica", 9))
    style.map("Markers.Inner.Treeview",
              background=[('selected', COLOR_PALETTE['select_bg'])], # Blue selection
              foreground=[('selected', COLOR_PALETTE['select_fg'])])

    style.configure("Markers.Inner.Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    relief="flat")
    style.map("Markers.Inner.Treeview.Heading",
              background=[('active', COLOR_PALETTE['active_bg'])])


    # --- Notebook (Tab) Styles for Parent Tabs ---
    style.configure("Parent.TNotebook",
                    background=COLOR_PALETTE['background'],
                    tabposition='nw',
                    borderwidth=0) # Remove border around the notebook itself

    # Configure the actual tab elements for parent tabs
    style.configure("Parent.TNotebook.Tab",
                    background=COLOR_PALETTE['active_bg'], # Default inactive tab color
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 10, "bold"),
                    padding=[10, 5],
                    relief="flat",
                    borderwidth=0) # Remove border around individual tabs

    # Map colors for each parent tab dynamically based on selection state
    for tab_name, colors in COLOR_PALETTE['parent_tabs'].items():
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
                  bordercolor=[('!selected', COLOR_PALETTE['background'])], # Border color matches notebook background when inactive
                  lightcolor=[('!selected', COLOR_PALETTE['background'])],
                  darkcolor=[('!selected', COLOR_PALETTE['background'])],
                  expand=[('!selected', [0,0,0,0])], # No expansion when unselected
                  sticky=[('!selected', 'nsew')],
                  )

    # --- Notebook (Tab) Styles for Child Tabs ---
    style.configure("Child.TNotebook",
                    background=COLOR_PALETTE['background'],
                    tabposition='n',
                    borderwidth=0)

    style.configure("Child.TNotebook.Tab",
                    background=COLOR_PALETTE['active_bg'], # Default background for child tabs
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 9),
                    padding=[8, 4],
                    relief="flat",
                    borderwidth=0)

    style.map("Child.TNotebook.Tab",
              background=[('selected', COLOR_PALETTE['active_bg']), ('active', COLOR_PALETTE['active_bg'])],
              foreground=[('selected', COLOR_PALETTE['foreground']), ('active', COLOR_PALETTE['foreground'])],
              bordercolor=[('selected', COLOR_PALETTE['active_bg'])],
              lightcolor=[('selected', COLOR_PALETTE['active_bg'])],
              darkcolor=[('selected', COLOR_PALETTE['active_bg'])],
              expand=[('selected', [0,0,0,0])],
              sticky=[('selected', 'nsew')],
              )

    debug_log_func(f"Custom Tkinter styles applied successfully. The GUI is looking sharp! Version: {current_version}",
                    file=__file__,
                    version=current_app_version, # Changed to current_app_version for consistency
                    function="The styles definition",
                    special=True)
