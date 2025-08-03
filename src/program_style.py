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
# Feature Requests can be emailed to i @ like . audio
#
# Version 20250803.193500.0 (FIXED: TclError by copying layout for custom styles. Added Band Button styles.)
# Version 20250803.1800.0 (ADDED: Red.TLabel.Value style for disconnected status.)
# Version 20250803.0335.0 (Refined Markers tab button styles into 4 distinct states.)
# Version 20250803.0330.0 (Added extensive comments describing each style, its usage, and states.)
# Version 20250803.0325.0 (Grouped all Markers tab specific styles together for better organization.)

current_version = "20250803.193500.0"

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
    'orange_btn_active': '#FFB74D',
    'blue_btn': '#2196F3',
    'blue_btn_active': '#64B5F6',
    'value_fg': '#ADD8E6',
}

def apply_styles(style, debug_log_func, current_app_version):
    """Applies custom Tkinter ttk styles for a consistent dark theme."""
    style.theme_use('clam')

    # --- General Styles ---
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('Dark.TFrame', background=COLOR_PALETTE['background'])
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    
    # CRITICAL: Copy layout for custom Label styles to prevent TclError
    try:
        tlabel_layout = style.layout('TLabel')
        style.layout('Dark.TLabel.Value', tlabel_layout)
        style.layout('Red.TLabel.Value', tlabel_layout)
    except TclError as e:
        debug_log_func(f"CRITICAL ERROR: Failed to copy TLabel layout: {e}", file=__file__, version=current_app_version, function="apply_styles")

    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 9, 'bold'))
    style.configure('Red.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))
    
    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'], borderwidth=1, relief="solid")
    style.map('TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])
    style.configure('TCombobox', fieldbackground=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['input_fg'])
    style.map('TCombobox', fieldbackground=[('readonly', COLOR_PALETTE['input_bg'])])

    # --- General Button Styles ---
    style.configure('TButton', background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9, 'bold'), padding=5, relief="flat")
    style.map('TButton', background=[('active', COLOR_PALETTE['active_bg']), ('disabled', COLOR_PALETTE['disabled_bg'])], foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])
    style.configure('Green.TButton', background=COLOR_PALETTE['green_btn'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9, 'bold'), padding=5, relief="flat")
    style.map('Green.TButton', background=[('active', COLOR_PALETTE['green_btn_active'])])
    style.configure('Red.TButton', background=COLOR_PALETTE['red_btn'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9, 'bold'), padding=5, relief="flat")
    style.map('Red.TButton', background=[('active', COLOR_PALETTE['red_btn_active'])])
    style.configure('Orange.TButton', background=COLOR_PALETTE['orange_btn'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9, 'bold'), padding=5, relief="flat")
    style.map('Orange.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])
    style.configure('Blue.TButton', background=COLOR_PALETTE['blue_btn'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9, 'bold'), padding=5, relief="flat")
    style.map('Blue.TButton', background=[('active', COLOR_PALETTE['blue_btn_active'])])

    # --- BANDSTO SCAN Buttons Style ---
    # Style for band selection buttons (default state)
    style.configure("Band.TButton",
                    background=COLOR_PALETTE['active_bg'], # Grey
                    foreground=COLOR_PALETTE['foreground'],
                    font=("Helvetica", 10, "bold"),
                    padding=[10, 5, 10, 5],
                    anchor='w')
    style.map("Band.TButton", background=[('active', COLOR_PALETTE['active_bg'])])

    # Style for selected band selection buttons
    style.configure("Band.Selected.TButton",
                    background=COLOR_PALETTE['orange_btn'], # Orange
                    foreground='black', # Black text for contrast
                    font=("Helvetica", 10, "bold"),
                    padding=[10, 5, 10, 5],
                    anchor='w')
    style.map("Band.Selected.TButton", background=[('active', COLOR_PALETTE['orange_btn_active'])])
    
    # --- Treeview Styles ---
    style.configure("Treeview", background=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], fieldbackground=COLOR_PALETTE['input_bg'], font=("Helvetica", 9))
    style.map("Treeview", background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], relief="flat")
    style.map("Treeview.Heading", background=[('active', COLOR_PALETTE['active_bg'])])
