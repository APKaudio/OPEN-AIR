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
# Version 20250803.0310.0 (Adjusted button styles for Markers tab, increased font size, and consistent active/inactive colors.)
# Version 20250803.0315.0 (Removed redundant Markers.TButton style; ensured Markers.General.TButton is default inactive.)
# Version 20250803.0320.0 (FIXED: Markers.General.TButton active state to use orange_btn_active for consistent hover feedback.)
# Version 20250803.0325.0 (Grouped all Markers tab specific styles together for better organization.)
# Version 20250803.0330.0 (Added extensive comments describing each style, its usage, and states.)
# Version 20250803.0335.0 (Refined Markers tab button styles into 4 distinct states: Device Selected/Scanning, Device Selected/Not Scanning, Config Active, Config Inactive.)

current_version = "20250803.0335.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 335 * 0 # Example hash, adjust as needed.

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
    'active_bg': '#606060', # General active/hover background (grey)
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

    # --- General Application-Wide Styles ---
    # These styles apply to common Tkinter widgets across the entire application.

    # Style for basic Tkinter Frames
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('Dark.TFrame', background=COLOR_PALETTE['background']) # Specific dark frame style for explicit use

    # Style for Tkinter LabelFrames (frames with a title)
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold')) # Specific dark labelframe style

    # Style for basic Tkinter Labels
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))

    # CRITICAL: This block ensures that 'Dark.TLabel.Value' style is properly registered
    # by copying the layout from a standard TLabel. Without this, custom styles might not apply.
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

    # Style for labels displaying important values (e.g., frequency, span)
    # Uses a light blue foreground for better visibility.
    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 9, 'bold'))

    # Styles for status labels (e.g., instrument connection status)
    style.configure('Green.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['green_btn'], font=('Helvetica', 10, 'bold')) # Green text for "Connected"
    style.configure('Red.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))   # Red text for "Disconnected"

    # Style for Tkinter Entry widgets (text input fields)
    # - `fieldbackground`: Background color of the input area.
    # - `foreground`: Text color.
    # - `focus`: When the entry has focus, its `fieldbackground` changes to `active_bg`.
    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], borderwidth=1, relief="solid")
    style.map('TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])

    # Style for Tkinter Combobox widgets (dropdown menus)
    # - `fieldbackground`: Background color of the input area.
    # - `foreground`: Text color.
    # - `selectbackground`: Background color of selected item in dropdown list.
    # - `selectforeground`: Text color of selected item in dropdown list.
    # - `readonly`: When combobox is readonly, its `fieldbackground` is `input_bg`.
    style.configure('TCombobox', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], selectbackground=COLOR_PALETTE['input_bg'], selectforeground=COLOR_PALETTE['input_fg'])
    style.map('TCombobox', fieldbackground=[('readonly', COLOR_PALETTE['input_bg'])])

    # --- General Button Styles ---
    # These styles define the default appearance and behavior for various buttons.

    # Default TButton style
    # - `background`: Default background color when not active/hovered.
    # - `foreground`: Text color.
    # - `font`, `padding`, `relief`, `focusthickness`: Visual properties.
    # - `active`: When hovered or pressed, background changes to `active_bg`.
    # - `disabled`: When disabled, background changes to `disabled_bg` and text to `disabled_fg`.
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

    # Green themed button
    style.configure('Green.TButton',
                    background=COLOR_PALETTE['green_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Green.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])])

    # Red themed button
    style.configure('Red.TButton',
                    background=COLOR_PALETTE['red_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Red.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']), ('disabled', COLOR_PALETTE['red_btn_disabled'])])

    # Orange themed button
    style.configure('Orange.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Orange.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])

    # Blue themed button
    style.configure('Blue.TButton',
                    background=COLOR_PALETTE['blue_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 9, 'bold'),
                    padding=5,
                    relief="flat")
    style.map('Blue.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active']), ('disabled', COLOR_PALETTE['blue_btn_disabled'])])

    # --- Scan Tab Specific Button Styles ---
    # These styles are designed for the buttons within the 'Scan' tab.

    # Style for the 'Start Scan' button
    # - `background`: Green when not active.
    # - `active`: Lighter green when hovered/pressed.
    # - `disabled`: Darker green when disabled.
    style.configure('StartScan.TButton',
                    background=COLOR_PALETTE['green_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('StartScan.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    # Style for the 'Pause Scan' button
    # - `background`: Orange when not active.
    # - `active`: Lighter orange when hovered/pressed.
    # - `disabled`: Darker orange when disabled.
    style.configure('PauseScan.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('PauseScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])

    # Style for the 'Resume Scan' button (similar to Pause, but might blink)
    # - `background`: Orange when not active.
    # - `active`: Lighter orange when hovered/pressed.
    # - `disabled`: Darker orange when disabled.
    style.configure('ResumeScan.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('ResumeScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    # Style for the 'Stop Scan' button
    # - `background`: Red when not active.
    # - `active`: Lighter red when hovered/pressed.
    # - `disabled`: Darker red when disabled.
    style.configure('StopScan.TButton',
                    background=COLOR_PALETTE['red_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[20, 10],
                    relief="raised",
                    borderwidth=2,
                    focusthickness=0)
    style.map('StopScan.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']), ('disabled', COLOR_PALETTE['red_btn_disabled'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])


    # --- Presets Tab Specific Button Styles ---
    # These styles are used for the preset management buttons in the 'Presets' tab.

    # Style for large, general preset buttons (e.g., in the Local Presets grid)
    # - `background`: Grey when not active.
    # - `active`: Remains grey when hovered/pressed (as per previous request).
    style.configure("LargePreset.TButton",
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 25, "bold"), # Increased font size
                    padding=[30, 15, 30, 15])
    style.map("LargePreset.TButton",
            background=[('active', COLOR_PALETTE['active_bg'])])
    
    # Style for the currently selected preset button (explicitly orange)
    # - `background`: Orange when not active (i.e., when it is the selected preset).
    # - `active`: Lighter orange when hovered/pressed.
    style.configure("SelectedPreset.Orange.TButton",
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 25, "bold"), # Increased font size
                    padding=[30, 15, 20, 15])
    style.map("SelectedPreset.Orange.TButton",
            background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # Style for a very large "YAK" button (specific to one part of the app)
    # - `background`: Orange when not active.
    # - `active`: Lighter orange when hovered/pressed.
    YAK_ORANGE = COLOR_PALETTE['orange_btn']
    style.configure('LargeYAK.TButton',
                    font=('Helvetica', 100, 'bold'),
                    background=YAK_ORANGE,
                    foreground=COLOR_PALETTE['foreground'],
                    padding=[20, 10])
    style.map('LargeYAK.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])])
    
    # --- Markers Tab Specific Styles ---
    # These styles are used for various elements within the 'Markers' tab.

    # General frame, label, and entry styles for the Markers tab
    style.configure('Markers.TFrame', background=COLOR_PALETTE['background'])
    style.configure('Markers.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Markers.TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    style.configure('Markers.TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], borderwidth=1, relief="solid")
    style.map('Markers.TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])


    # --- Markers Tab Device Button States ---

    # 1. Device Button: Not Selected, Not Scanning
    # This is the default state for device buttons in the Markers tab.
    # - `background`: Grey (`active_bg`) when not hovered or pressed.
    # - `active`: Remains grey (`active_bg`) when hovered or pressed.
    # - `disabled`: Dark grey (`disabled_bg`) when disabled.
    style.configure('Markers.Device.Default.TButton',
                    background=COLOR_PALETTE['active_bg'], # Grey for inactive
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 13, 'bold'),
                    padding=[5, 5, 5, 5],
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.Device.Default.TButton',
              background=[('active', COLOR_PALETTE['active_bg']), ('disabled', COLOR_PALETTE['disabled_bg'])])

    # 2. Device Button: Selected, Not Scanning
    # This state applies when a device button is clicked and selected, but the instrument
    # is not actively scanning on its frequency.
    # - `background`: Orange (`orange_btn`) when not hovered or pressed.
    # - `active`: Lighter orange (`orange_btn_active`) when hovered or pressed.
    # - `disabled`: Darker orange (`orange_btn_disabled`) when disabled.
    style.configure('Markers.Device.Selected.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange for selected
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 13, 'bold'),
                    padding=[5, 5, 5, 5],
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.Device.Selected.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])

    # 3. Device Button: Selected AND Being Scanned
    # This state applies when a device button is clicked and selected, AND the instrument
    # is actively scanning on its frequency. This is the primary "active" visual cue.
    # - `background`: Green (`green_btn`) when not hovered or pressed.
    # - `active`: Lighter green (`green_btn_active`) when hovered or pressed.
    # - `disabled`: Darker green (`green_btn_disabled`) when disabled.
    style.configure('Markers.Device.Scanning.TButton',
                    background=COLOR_PALETTE['green_btn'], # Green for active scan
                    foreground='black', # Black font for contrast on green
                    font=('Helvetica', 13, 'bold'),
                    padding=[5, 5, 5, 5],
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.Device.Scanning.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['green_btn_disabled'])])


    # --- Markers Tab Configuration Button States (Span, RBW, POKE, Trace Modes) ---

    # 1. Configuration Button: Inactive (Not Selected)
    # This is the default state for configuration buttons in the Markers tab when they are not active.
    # - `background`: Grey (`active_bg`) when not hovered or pressed.
    # - `active`: Lighter orange (`orange_btn_active`) when hovered or pressed (provides feedback).
    # - `disabled`: Dark grey (`disabled_bg`) when disabled.
    style.configure('Markers.Config.Default.TButton',
                    background=COLOR_PALETTE['active_bg'], # Grey for inactive
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 14, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.Config.Default.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['disabled_bg'])])

    # 2. Configuration Button: Active (Selected)
    # This state applies when a configuration button (like a specific Span or RBW) is currently active.
    # - `background`: Orange (`orange_btn`) when not hovered or pressed.
    # - `active`: Lighter orange (`orange_btn_active`) when hovered or pressed.
    # - `disabled`: Darker orange (`orange_btn_disabled`) when disabled.
    style.configure('Markers.Config.Selected.TButton',
                    background=COLOR_PALETTE['orange_btn'], # Orange for selected
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 14, 'bold'),
                    padding=5,
                    relief="flat",
                    focusthickness=0)
    style.map('Markers.Config.Selected.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['orange_btn_disabled'])])


    # --- Treeview Styles ---
    # These styles apply to Tkinter Treeview widgets used for displaying hierarchical data.

    # Treeview Style for the Marker Editor (e.g., in PresetEditorTab)
    # - `background`: Dark grey for the treeview background.
    # - `foreground`: White text.
    # - `selected`: Blue background and white text when an item is selected.
    style.configure("Treeview",
                    background=COLOR_PALETTE['input_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    fieldbackground=COLOR_PALETTE['input_bg'],
                    font=("Helvetica", 9))
    style.map("Treeview",
              background=[('selected', COLOR_PALETTE['select_bg'])],
              foreground=[('selected', COLOR_PALETTE['select_fg'])])

    # Treeview Heading style for the Marker Editor
    # - `background`: General active grey for headings.
    # - `active`: Remains active grey when hovered.
    style.configure("Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', COLOR_PALETTE['active_bg'])])

    # Treeview Style for Zones & Groups within the Markers Display Tab
    # Similar to general Treeview but with a specific name for clarity.
    style.configure("Markers.Inner.Treeview",
                    background=COLOR_PALETTE['input_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    fieldbackground=COLOR_PALETTE['input_bg'],
                    font=("Helvetica", 9))
    style.map("Markers.Inner.Treeview",
              background=[('selected', COLOR_PALETTE['select_bg'])],
              foreground=[('selected', COLOR_PALETTE['select_fg'])])

    # Treeview Heading style for Zones & Groups in Markers Display Tab
    style.configure("Markers.Inner.Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    relief="flat")
    style.map("Markers.Inner.Treeview.Heading",
              background=[('active', COLOR_PALETTE['active_bg'])])


    # --- Notebook (Tab) Styles for Parent Tabs ---
    # These styles control the appearance of the main top-level tabs.

    # Overall Notebook style for parent tabs
    style.configure("Parent.TNotebook",
                    background=COLOR_PALETTE['background'],
                    tabposition='nw', # Tabs positioned at North-West
                    borderwidth=0) # No border around the entire notebook

    # Style for individual parent tab elements
    # - `background`: Default inactive tab color (grey).
    # - `foreground`: Text color.
    # - `font`, `padding`, `relief`, `borderwidth`: Visual properties.
    style.configure("Parent.TNotebook.Tab",
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 10, "bold"),
                    padding=[10, 5],
                    relief="flat",
                    borderwidth=0)

    # Dynamic mapping for parent tab colors based on selection and hover states.
    # Iterates through `COLOR_PALETTE['parent_tabs']` to apply specific colors per tab.
    for tab_name, colors in COLOR_PALETTE['parent_tabs'].items():
        # Active state for a selected tab (when the tab is currently open)
        # - `selected`: Background is the tab's specific active color.
        # - `active`: When hovered over, background is also the tab's specific active color.
        # - `bordercolor`, `lightcolor`, `darkcolor`: Borders match the active color.
        style.map("Parent.TNotebook.Tab",
                  background=[('selected', colors['active']), ('active', colors['active'])],
                  foreground=[('selected', colors['fg_active']), ('active', colors['fg_active'])],
                  bordercolor=[('selected', colors['active'])],
                  lightcolor=[('selected', colors['active'])],
                  darkcolor=[('selected', colors['active'])],
                  expand=[('selected', [0,0,0,0])], # No expansion when selected
                  sticky=[('selected', 'nsew')],
                  )
        # Inactive state for unselected tabs (when the tab is not currently open)
        # - `!selected`: Background is the tab's specific inactive color.
        # - `!selected`: When hovered over, background is also the tab's specific inactive color.
        # - `bordercolor`, `lightcolor`, `darkcolor`: Borders match the notebook background.
        style.map("Parent.TNotebook.Tab",
                  background=[('!selected', colors['inactive']), ('!selected', colors['inactive'])],
                  foreground=[('!selected', colors['fg_inactive']), ('!selected', colors['fg_inactive'])],
                  bordercolor=[('!selected', COLOR_PALETTE['background'])],
                  lightcolor=[('!selected', COLOR_PALETTE['background'])],
                  darkcolor=[('!selected', COLOR_PALETTE['background'])],
                  expand=[('!selected', [0,0,0,0])], # No expansion when unselected
                  sticky=[('!selected', 'nsew')],
                  )

    # --- Notebook (Tab) Styles for Child Tabs ---
    # These styles control the appearance of the nested tabs within parent tabs.

    # Overall Notebook style for child tabs
    style.configure("Child.TNotebook",
                    background=COLOR_PALETTE['background'],
                    tabposition='n', # Tabs positioned at North
                    borderwidth=0)

    # Style for individual child tab elements
    # - `background`: Default background for child tabs (grey).
    # - `foreground`: Text color.
    # - `font`, `padding`, `relief`, `borderwidth`: Visual properties.
    style.configure("Child.TNotebook.Tab",
                    background=COLOR_PALETTE['active_bg'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 9),
                    padding=[8, 4],
                    relief="flat",
                    borderwidth=0)

    # Mapping for child tab colors based on selection and hover states.
    # Child tabs generally have a more uniform appearance compared to parent tabs.
    # - `selected`: Background is `active_bg` (grey).
    # - `active`: When hovered, background is also `active_bg` (grey).
    # - `bordercolor`, `lightcolor`, `darkcolor`: Borders match `active_bg`.
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
