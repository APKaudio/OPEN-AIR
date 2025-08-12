# src/program_style.py
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
# Version 20250811.213200.0

current_version = "20250811.213200.0"
current_version_hash = 20250811 * 213200 * 0

import tkinter as tk
from tkinter import ttk, TclError
import inspect
import os

from display.debug_logic import debug_log

COLOR_PALETTE = {
    'background': '#2b2b2b',
    'foreground': 'white',
    'input_bg': '#3c3c3c',
    'input_fg': 'white',
    'select_bg': '#007acc',
    'select_fg': 'white',
    'active_bg': '#606060',
    'disabled_bg': '#3a3a3a',
    'disabled_fg': '#808080',
    'green_btn': '#4CAF50',
    'green_btn_active': '#66BB6A',
    'red_btn': '#F44336',
    'red_btn_active': '#EF5350',
    'orange_btn': '#FF9800',
    'orange_btn_active': '#FFA726',
    'blue_btn': '#2196F3',
    'blue_btn_active': '#64B5F6',
    'purple_btn': '#673AB7',
    'purple_btn_active': '#7E57C2',
    'value_fg': '#ADD8E6',
    'grey_btn': '#707070',
    'grey_btn_active': '#858585',
    'white': 'white', # Explicit white for clarity
    'black': 'black', # Explicit black for clarity
    'yellow_btn': '#FFEB3B', # NEW: Yellow button color
    'yellow_btn_active': '#FFF176', # NEW: Yellow button active color
}

COLOR_PALETTE_TABS = {
    'Instruments': {'active': '#d13438', 'fg': 'white'},
    'Markers': {'active': '#ff8c00', 'fg': 'black'},
    'Presets': {'active': '#ffb900', 'fg': 'black'},
    'Scanning': {'active': '#00b294', 'fg': 'white'},
    'Plotting': {'active': '#0078d4', 'fg': 'white'},
    'Experiments': {'active': '#8a2be2', 'fg': 'white'},
}

def _get_dark_color(hex_color):
    """Calculates a 50% darker version of a hex color."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = int(r * 0.5); g = int(g * 0.5); b = int(b * 0.5)
    return f'#{r:02x}{g:02x}{b:02x}'

def apply_styles(style, debug_log_func, current_app_version):
    """Applies custom Tkinter ttk styles for a consistent dark theme."""
    style.theme_use('clam')

    # --- General Styles ---
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('Dark.TFrame', background=COLOR_PALETTE['background'])
    # Updated TLabelframe font and foreground to make it more translucent
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 12, 'bold'))
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 12, 'bold'))
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    
    try:
        tlabel_layout = style.layout('TLabel')
        if tlabel_layout:
            style.layout('Dark.TLabel.Value', tlabel_layout)
            style.layout('Red.TLabel.Value', tlabel_layout)
    except TclError as e:
        debug_log_func(f"CRITICAL ERROR: Failed to copy TLabel layout: {e}", file=os.path.basename(__file__), version=current_app_version, function="apply_styles")

    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 11, 'bold'))
    style.configure('Red.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 11, 'bold'))
    
    # Updated TEntry style
    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground='white', borderwidth=1, relief="solid", font=('Helvetica', 11))
    style.map('TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])
    
    # --- Custom Tab Button Styles (Parents) & Child Notebook Styles ---
    for name, config in COLOR_PALETTE_TABS.items():
        active_color = config['active']
        inactive_color = _get_dark_color(active_color)
        
        style.configure(f'{name}.Active.TButton', background=active_color, foreground=config['fg'], font=('Helvetica', 14, 'bold'), relief='flat')
        style.map(f'{name}.Active.TButton', background=[('active', active_color)])
        
        style.configure(f'{name}.Inactive.TButton', background=inactive_color, foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 11, 'bold'), relief='flat')
        style.map(f'{name}.Inactive.TButton', background=[('active', active_color)])

        child_style_name = f'{name}.Child.TNotebook'
        child_tab_style_name = f'{child_style_name}.Tab'
        
        style.configure(child_style_name, background=COLOR_PALETTE['background'], borderwidth=1)
        style.configure(child_tab_style_name, background=inactive_color, foreground=COLOR_PALETTE['foreground'], padding=[8, 4], font=('Helvetica', 10, 'bold'))
        style.map(child_tab_style_name, background=[('selected', active_color)], foreground=[('selected', config['fg'])])

    # --- Device Buttons (Markers Tab) ---
    style.configure('DeviceButton.Inactive.TButton', 
                    background=COLOR_PALETTE['active_bg'], 
                    foreground=COLOR_PALETTE['foreground'], 
                    font=('Helvetica', 14),
                    padding=5,
                    anchor='center',
                    justify='center')
    style.map('DeviceButton.Inactive.TButton', background=[('active', COLOR_PALETTE['select_bg'])])
    
    style.configure('DeviceButton.Active.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground='black',
                    font=('Helvetica', 14, 'bold'),
                    padding=5,
                    anchor='center',
                    justify='center')
    style.map('DeviceButton.Active.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # --- Styles for Control Buttons (Markers Tab) ---
    style.configure('ControlButton.Inactive.TButton',
                    background=COLOR_PALETTE['grey_btn'],
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 10),
                    padding=5,
                    anchor='center',
                    justify='center')
    style.map('ControlButton.Inactive.TButton',
              background=[('active', COLOR_PALETTE['grey_btn_active'])])
    
    style.configure('ControlButton.Active.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['black'],
                    font=('Helvetica', 10, 'bold'),
                    padding=5,
                    anchor='center',
                    justify='center')
    style.map('ControlButton.Active.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # --- Styles for Band Selection Buttons (Scanning Tab) ---
    # Unselected
    style.configure('Band.TButton',
                    background=COLOR_PALETTE['grey_btn'], # Grey for unselected
                    foreground='white',
                    font=('Helvetica', 10),
                    padding=[5, 5],
                    anchor='center',
                    justify='center',
                    relief='flat',
                    borderwidth=1)
    style.map('Band.TButton',
              background=[('active', COLOR_PALETTE['grey_btn_active'])]) # Lighter grey on hover

    # Low Importance (Yellow)
    style.configure('Band.Low.TButton',
                    background=COLOR_PALETTE['yellow_btn'],
                    foreground='black', # Black text for contrast on yellow
                    font=('Helvetica', 10, 'bold'),
                    padding=[5, 5],
                    anchor='center',
                    justify='center',
                    relief='raised',
                    borderwidth=2)
    style.map('Band.Low.TButton',
              background=[('active', COLOR_PALETTE['yellow_btn_active'])])

    # Medium Importance (Orange)
    style.configure('Band.Medium.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground='black',
                    font=('Helvetica', 10, 'bold'),
                    padding=[5, 5],
                    anchor='center',
                    justify='center',
                    relief='raised',
                    borderwidth=2)
    style.map('Band.Medium.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # High Importance (Red)
    style.configure('Band.High.TButton',
                    background=COLOR_PALETTE['red_btn'],
                    foreground='white',
                    font=('Helvetica', 10, 'bold'),
                    padding=[5, 5],
                    anchor='center',
                    justify='center',
                    relief='raised',
                    borderwidth=2)
    style.map('Band.High.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active'])])

    # --- Styles for Local Preset Buttons ---
    # Base for unselected preset buttons
    style.configure('LocalPreset.TButton',
                    background=COLOR_PALETTE['active_bg'], # Or a slightly darker shade
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 25), # MODIFIED: Font size to 25pt
                    padding=[10, 8], # More padding for multi-line text
                    anchor='center', # Center text for multi-line
                    justify='center',
                    relief='flat',
                    borderwidth=1,
                    focusthickness=0) # Remove dotted focus outline
    style.map('LocalPreset.TButton',
              background=[('active', COLOR_PALETTE['select_bg'])], # Darker on hover
              foreground=[('active', COLOR_PALETTE['select_fg'])]) # Keep foreground white on hover

    # Style for selected preset button
    style.configure('SelectedPreset.Orange.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground='black', # Black text for visibility on orange
                    font=('Helvetica', 25, 'bold'), # MODIFIED: Font size to 25pt, bold for selected
                    padding=[10, 8],
                    anchor='center',
                    justify='center',
                    relief='raised', # Make it look "pushed" or selected
                    borderwidth=2,
                    focusthickness=0)
    style.map('SelectedPreset.Orange.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])],
              foreground=[('active', 'black')])

    # --- Scan Control Buttons (Start, Pause, Stop) ---
    style.configure('StartScan.TButton',
                    background=COLOR_PALETTE['green_btn'],
                    foreground=COLOR_PALETTE['white'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[10, 5])
    style.map('StartScan.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    style.configure('PauseScan.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground=COLOR_PALETTE['black'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[10, 5])
    style.map('PauseScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    style.configure('StopScan.TButton',
                    background=COLOR_PALETTE['red_btn'],
                    foreground=COLOR_PALETTE['white'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[10, 5])
    style.map('StopScan.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])
    
    # Style for the blinking resume button
    style.configure('ResumeScan.Blink.TButton',
                    background=COLOR_PALETTE['select_bg'], # Blue to make it "blink" distinctively
                    foreground=COLOR_PALETTE['white'],
                    font=('Helvetica', 12, 'bold'),
                    padding=[10, 5])
    style.map('ResumeScan.Blink.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active'])])


    # --- Other Generic Buttons (e.g. for general use in UI) ---
    style.configure('Green.TButton', background=COLOR_PALETTE['green_btn'], foreground='white')
    style.map('Green.TButton', background=[('active', COLOR_PALETTE['green_btn_active'])])
    style.configure('Red.TButton', background=COLOR_PALETTE['red_btn'], foreground='white')
    style.map('Red.TButton', background=[('active', COLOR_PALETTE['red_btn_active'])])
    style.configure('Blue.TButton', background=COLOR_PALETTE['blue_btn'], foreground='white')
    style.map('Blue.TButton', background=[('active', COLOR_PALETTE['blue_btn_active'])])
    style.configure('Orange.TButton', background=COLOR_PALETTE['orange_btn'], foreground='black')
    style.map('Orange.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])
    style.configure('Purple.TButton', background=COLOR_PALETTE['purple_btn'], foreground='white')
    style.map('Purple.TButton', background=[('active', COLOR_PALETTE['purple_btn_active'])])

    # --- Other Widget Styles (Treeview, etc.) ---
    style.configure("Treeview", background=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], fieldbackground=COLOR_PALETTE['input_bg'], font=("Helvetica", 9))
    style.map("Treeview", background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], relief="flat")
    style.map("Treeview.Heading", background=[('active', COLOR_PALETTE['active_bg'])])

