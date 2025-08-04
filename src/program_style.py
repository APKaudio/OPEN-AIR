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
#
# Version 20250803.212000.0 (REMOVED: All custom parent TNotebook styles that were causing errors.)
# Version 20250803.210300.0 (FIXED: Removed TPanedWindow style to prevent TclError.)
# Version 20250803.213000.0 (ADDED: Colored styles for all Parent and Child notebook tabs.)

current_version = "20250803.212000.0"

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
    'dark_green_btn': '#1B5E20',
    'red_btn': '#F44336',
    'red_btn_active': '#EF5350',
    'dark_red_btn': '#B71C1C',
    'orange_btn': '#FF9800',
    'orange_btn_active': '#FFA726',
    'dark_orange_btn': '#E65100',
    'blue_btn': '#2196F3',
    'blue_btn_active': '#64B5F6',
    'value_fg': '#ADD8E6',
    'tab_child_bg': '#4a4a4a', 
    'tab_child_selected_bg': '#6a6a6a',
}

def apply_styles(style, debug_log_func, current_app_version):
    """Applies custom Tkinter ttk styles for a consistent dark theme."""
    style.theme_use('clam')

    # --- General Styles ---
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 10, 'bold'))
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))

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

    # --- Scan Control Button Styles ---
    style.configure('StartScan.TButton', background=COLOR_PALETTE['green_btn'], foreground='white', font=('Helvetica', 10, 'bold'), padding=8)
    style.map('StartScan.TButton', background=[('active', COLOR_PALETTE['green_btn_active']), ('disabled', COLOR_PALETTE['dark_green_btn'])])
    style.configure('PauseScan.TButton', background=COLOR_PALETTE['orange_btn'], foreground='black', font=('Helvetica', 10, 'bold'), padding=8)
    style.map('PauseScan.TButton', background=[('active', COLOR_PALETTE['orange_btn_active']), ('disabled', COLOR_PALETTE['dark_orange_btn'])])
    style.configure('ResumeScan.Blink.TButton', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['orange_btn'], font=('Helvetica', 10, 'bold'), padding=8)
    style.configure('StopScan.TButton', background=COLOR_PALETTE['red_btn'], foreground='white', font=('Helvetica', 10, 'bold'), padding=8)
    style.map('StopScan.TButton', background=[('active', COLOR_PALETTE['red_btn_active']), ('disabled', COLOR_PALETTE['dark_red_btn'])])
    
    # --- Treeview Styles ---
    style.configure("Treeview", background=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], fieldbackground=COLOR_PALETTE['input_bg'], font=("Helvetica", 9))
    style.map("Treeview", background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], relief="flat")
    style.map("Treeview.Heading", background=[('active', COLOR_PALETTE['active_bg'])])

    # --- Notebook Styles ---
    # The custom parent notebook styles have been removed as they are not supported by Tkinter.
    # A single, neutral style is applied to the main notebook now.
    style.configure('TNotebook', background=COLOR_PALETTE['background'], borderwidth=1)
    style.configure('TNotebook.Tab', background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], padding=[10, 5], font=('Helvetica', 10, 'bold'))
    style.map('TNotebook.Tab', background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    
    # Generic Style for Child Notebooks
    style.configure('Child.TNotebook', background=COLOR_PALETTE['background'])
    style.configure('Child.TNotebook.Tab', background=COLOR_PALETTE['tab_child_bg'], foreground=COLOR_PALETTE['foreground'], padding=[8, 4], font=('Helvetica', 9))
    style.map('Child.TNotebook.Tab', background=[('selected', COLOR_PALETTE['tab_child_selected_bg'])])