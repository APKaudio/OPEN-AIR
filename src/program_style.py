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
# Version 20250803.232000.0 (MODIFIED: Changed active ControlButton style to orange.)
# Version 20250803.231500.0 (ADDED: 'ControlButton' styles. MODIFIED: Increased 'DeviceButton' font to 14pt.)
# Version 20250803.232501.0 (ADDED: New 'DeviceButton' styles with larger, centered font.)
# Version 20250803.232500.0 (ADDED: Custom styles for active/inactive device buttons on Markers tab.)
# Version 20250803.225500.0 (ADDED: Unique, color-coded styles for each parent's child tabs.)

current_version = "20250803.232000.0"

import tkinter as tk
from tkinter import ttk, TclError
import inspect

from src.debug_logic import debug_log

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
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    
    try:
        tlabel_layout = style.layout('TLabel')
        if tlabel_layout:
            style.layout('Dark.TLabel.Value', tlabel_layout)
            style.layout('Red.TLabel.Value', tlabel_layout)
    except TclError as e:
        debug_log_func(f"CRITICAL ERROR: Failed to copy TLabel layout: {e}", file=__file__, version=current_app_version, function="apply_styles")

    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 9, 'bold'))
    style.configure('Red.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))
    
    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], borderwidth=1, relief="solid")
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

    # --- Control Buttons (Span, RBW, Trace) ---
    style.configure('ControlButton.Inactive.TButton',
                    background=_get_dark_color(COLOR_PALETTE['blue_btn']),
                    foreground=COLOR_PALETTE['foreground'],
                    font=('Helvetica', 10, 'bold'),
                    padding=8,
                    anchor='center')
    style.map('ControlButton.Inactive.TButton', background=[('active', COLOR_PALETTE['blue_btn'])])

    style.configure('ControlButton.Active.TButton',
                    background=COLOR_PALETTE['orange_btn'],
                    foreground='black',
                    font=('Helvetica', 10, 'bold'),
                    padding=8,
                    anchor='center')
    style.map('ControlButton.Active.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # --- Other Widget Styles ---
    style.configure("Treeview", background=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], fieldbackground=COLOR_PALETTE['input_bg'], font=("Helvetica", 9))
    style.map("Treeview", background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], relief="flat")
    style.map("Treeview.Heading", background=[('active', COLOR_PALETTE['active_bg'])])

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