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
# Build Log: https://like.audio/category/software/spectrum-runner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250821.110100.1 (FIXED: Added the missing import of 'ttkthemes' to resolve the TclError.)

current_version = "20250821.110100.1"
current_version_hash = (20250821 * 110100 * 1)

import tkinter as tk
from tkinter import ttk, TclError
import inspect
import os

# FIXED: Explicitly import ttkthemes to make the themes available to the style engine
import ttkthemes
from ttkthemes import ThemedStyle

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
    'yellow_btn': '#FFEB3B',
    'yellow_btn_active': '#FFF176',
    'dark_grey_slider': '#1F1F1F',
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
    
def _revert_to_default_styles(style):
    """
    Reverts to the default Tkinter styles if a TclError occurs.
    """
    style.configure('.', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('TLabelFrame', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('TButton', background='lightgrey', foreground='black')
    style.configure('TCheckbutton', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('TEntry', fieldbackground='white', foreground='black')
    style.configure('TCombobox', fieldbackground='white', foreground='black')
    style.configure('TPanedwindow', background=COLOR_PALETTE['background'])
    style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
    style.configure('Treeview.Heading', background='lightgrey', foreground='black')
    style.configure('Vertical.TScrollbar', troughcolor='lightgrey', background='darkgrey')
    style.configure('Horizontal.TScrollbar', troughcolor='lightgrey', background='darkgrey')
    style.map('TButton', background=[('active', 'gray')])
    style.map('TCheckbutton', background=[('active', 'gray')])
    style.map('TEntry', fieldbackground=[('disabled', 'lightgrey')], foreground=[('disabled', 'darkgrey')])
def apply_styles(style, debug_log_func, current_app_version):
    """Applies custom Tkinter ttk styles for a consistent dark theme."""
    current_function = inspect.currentframe().f_code.co_name
    debug_log_func(f"Entering {current_function}. Applying all application-wide widget styles. 🎨",
                   file=f"{os.path.basename(__file__)} - {current_app_version}",
                   version=current_app_version,
                   function=current_function, special=True)

    try:
        # If the style is not a ThemedStyle, replace it with one to access ttkthemes
        if not isinstance(style, ThemedStyle):
            root = style.master if hasattr(style, 'master') else None
            style = ThemedStyle(root)
        available_themes = style.theme_names()
        if 'dark' in available_themes:
            style.theme_use('dark')
        else:
            debug_log_func("❌ `dark` theme not found. Attempting to use a standard theme.",
                             file=f"{os.path.basename(__file__)} - {current_app_version}",
                             version=current_app_version,
                             function=current_function)
            # Fallback to a standard theme if 'clam' is not found
            if 'clam' in available_themes:
                style.theme_use('clam')
            else:
                style.theme_use('default')

    except TclError as e:
        debug_log_func(f"❌ TclError: {e}. Reverting to default styles.",
                         file=f"{os.path.basename(__file__)} - {current_app_version}",
                         version=current_app_version,
                         function=current_function)
        _revert_to_default_styles(style)
        
    style.configure('.', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('.', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])

    # --- General Styles ---
    style.configure('TFrame', background=COLOR_PALETTE['background'])
    style.configure('Dark.TFrame', background=COLOR_PALETTE['background'])
    
    style.configure('TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    style.configure('Dark.TLabelframe', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'])
    
    style.configure('TLabelframe.Label', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 13, 'bold'))

    style.configure('TLabel', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    
    try:
        tlabel_layout = style.layout('TLabel')
        if tlabel_layout:
            style.layout('Dark.TLabel.Value', tlabel_layout)
            style.layout('Red.TLabel.Value', tlabel_layout)
    except TclError as e:
        debug_log_func(f"CRITICAL ERROR: Failed to copy TLabel layout: {e}", file=os.path.basename(__file__), version=current_app_version, function="apply_styles")

    style.configure('Dark.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['value_fg'], font=('Helvetica', 10, 'bold'))
    style.configure('Red.TLabel.Value', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))
    
    style.configure('Dark.TLabel.Success', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['green_btn'], font=('Helvetica', 10, 'bold'))
    style.configure('Dark.TLabel.Error', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['red_btn'], font=('Helvetica', 10, 'bold'))
    style.configure('Disconnected.TLabel', background=COLOR_PALETTE['red_btn'], foreground=COLOR_PALETTE['white'], font=('Helvetica', 10, 'bold'))

    # REVERTED: The custom 'Dark.TLabel.Result' style and its layout have been removed.
    # The label will now use the default 'TLabel' style.


    # UPDATED: Changed font size for Entry widgets to 14pt AND added selectbackground
    style.configure('TEntry', fieldbackground=COLOR_PALETTE['input_bg'], foreground='white', borderwidth=1, relief="solid", font=('Helvetica', 14))
    style.map('TEntry', fieldbackground=[('focus', COLOR_PALETTE['active_bg'])])
    style.map('TEntry', selectbackground=[('selected', COLOR_PALETTE['select_bg'])])

    style.configure('TCheckbutton', background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 9))
    style.map('TCheckbutton',
        background=[('active', COLOR_PALETTE['background'])],
        foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    # UPDATED: Changed font size for Combobox widgets to 14pt
    style.configure('TCombobox',
                     fieldbackground=COLOR_PALETTE['input_bg'],
                     selectbackground=COLOR_PALETTE['select_bg'],
                     foreground=COLOR_PALETTE['input_fg'],
                     selectforeground=COLOR_PALETTE['select_fg'],
                     background=COLOR_PALETTE['input_bg'],
                     font=('Helvetica', 14))
    style.map('TCombobox',
              fieldbackground=[('readonly', COLOR_PALETTE['input_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])],
              selectbackground=[('readonly', COLOR_PALETTE['select_bg'])],
              selectforeground=[('readonly', COLOR_PALETTE['select_fg'])])

    # --- New Slider Style ---
    # Define the layout for the new custom slider style based on the stock clam theme's layout
    # FIXED: Layout corrected to build on the stock clam theme's layout.
    style.layout('Horizontal.InteractionBars.TScale',
        [('Horizontal.Scale.trough',
          {'sticky': 'nswe'}),
         ('Horizontal.Scale.slider',
          {'side': 'left', 'sticky': 'ew'})])

    style.layout('Vertical.InteractionBars.TScale',
        [('Vertical.Scale.trough',
          {'sticky': 'nswe'}),
         ('Vertical.Scale.slider',
          {'side': 'top', 'sticky': 'ns'})])

    style.configure('InteractionBars.TScale',
                     background=COLOR_PALETTE['background'],
                     troughcolor=COLOR_PALETTE['dark_grey_slider'],
                     sliderrelief='flat',
                     sliderthickness=15,
                     borderwidth=0)
    
    # --- Custom Tab Button Styles (Parents) & Child Notebook Styles ---
    for name, config in COLOR_PALETTE_TABS.items():
        active_color = config['active']
        inactive_color = _get_dark_color(active_color)
        
        # UPDATED: Changed font size for active parent buttons to 13pt
        style.configure(f'{name}.Active.TButton', background=active_color, foreground=config['fg'], font=('Helvetica', 13, 'bold'), relief='flat')
        style.map(f'{name}.Active.TButton', background=[('active', active_color)])
        
        # UPDATED: Changed font size for inactive parent buttons to 13pt
        style.configure(f'{name}.Inactive.TButton', background=inactive_color, foreground=COLOR_PALETTE['foreground'], font=('Helvetica', 13, 'bold'), relief='flat')
        style.map(f'{name}.Inactive.TButton', background=[('active', active_color)])

        child_style_name = f'{name}.Child.TNotebook'
        child_tab_style_name = f'{child_style_name}.Tab'
        
        style.configure(child_style_name, background=COLOR_PALETTE['background'], borderwidth=1)
        # UPDATED: Changed font size for child tabs to 13pt
        style.configure(child_tab_style_name, background=inactive_color, foreground=COLOR_PALETTE['foreground'], padding=[8, 4], font=('Helvetica', 13, 'bold'))
        style.map(child_tab_style_name, background=[('selected', active_color)], foreground=[('selected', config['fg'])])

    # --- Device Buttons (Markers Tab) ---
    # UPDATED: Changed font size for device buttons to 13pt
    style.configure('DeviceButton.Inactive.TButton', 
                     background=COLOR_PALETTE['active_bg'], 
                     foreground=COLOR_PALETTE['foreground'], 
                     font=('Helvetica', 13),
                     padding=5,
                     anchor='center',
                     justify='center')
    style.map('DeviceButton.Inactive.TButton', background=[('active', COLOR_PALETTE['select_bg'])])
    
    # UPDATED: Changed font size for active device buttons to 13pt
    style.configure('DeviceButton.Active.TButton',
                     background=COLOR_PALETTE['orange_btn'],
                     foreground='black',
                     font=('Helvetica', 13, 'bold'),
                     padding=5,
                     anchor='center',
                     justify='center')
    style.map('DeviceButton.Active.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # UPDATED: Changed font size for blinking device buttons to 13pt
    style.configure('DeviceButton.Blinking.TButton',
                     background=COLOR_PALETTE['red_btn'],
                     foreground='white',
                     font=('Helvetica', 13, 'bold'),
                     padding=5,
                     anchor='center',
                     justify='center')
    style.map('DeviceButton.Blinking.TButton', background=[('active', COLOR_PALETTE['red_btn_active'])])


    # --- Styles for Control Buttons (Markers Tab) ---
    # UPDATED: Changed font size for control buttons to 13pt
    style.configure('ControlButton.Inactive.TButton',
                     background=COLOR_PALETTE['grey_btn'],
                     foreground=COLOR_PALETTE['foreground'],
                     font=('Helvetica', 13),
                     padding=5,
                     anchor='center',
                     justify='center')
    style.map('ControlButton.Inactive.TButton',
              background=[('active', COLOR_PALETTE['grey_btn_active'])])
    
    # UPDATED: Changed font size for active control buttons to 13pt
    style.configure('ControlButton.Active.TButton',
                     background=COLOR_PALETTE['orange_btn'],
                     foreground='black',
                     font=('Helvetica', 13, 'bold'),
                     padding=[5, 5],
                     anchor='center',
                     justify='center')
    style.map('ControlButton.Active.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # --- Styles for Band Selection Buttons (Running Tab) ---
    # UPDATED: Changed font size for band buttons to 13pt
    style.configure('Band.TButton',
                     background=COLOR_PALETTE['grey_btn'],
                     foreground='white',
                     font=('Helvetica', 13),
                     padding=[5, 5],
                     anchor='center',
                     justify='center',
                     relief='flat',
                     borderwidth=1)
    style.map('Band.TButton',
              background=[('active', COLOR_PALETTE['grey_btn_active'])])

    # UPDATED: Changed font size for low band buttons to 13pt
    style.configure('Band.Low.TButton',
                     background=COLOR_PALETTE['yellow_btn'],
                     foreground='black',
                     font=('Helvetica', 13, 'bold'),
                     padding=[5, 5],
                     anchor='center',
                     justify='center',
                     relief='raised',
                     borderwidth=2)
    style.map('Band.Low.TButton',
              background=[('active', COLOR_PALETTE['yellow_btn_active'])])

    # UPDATED: Changed font size for medium band buttons to 13pt
    style.configure('Band.Medium.TButton',
                     background=COLOR_PALETTE['orange_btn'],
                     foreground='black',
                     font=('Helvetica', 13, 'bold'),
                     padding=[5, 5],
                     anchor='center',
                     justify='center',
                     relief='raised',
                     borderwidth=2)
    style.map('Band.Medium.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active'])])

    # UPDATED: Changed font size for high band buttons to 13pt
    style.configure('Band.High.TButton',
                     background=COLOR_PALETTE['red_btn'],
                     foreground='white',
                     font=('Helvetica', 13, 'bold'),
                     padding=[5, 5],
                     anchor='center',
                     justify='center',
                     relief='raised',
                     borderwidth=2)
    style.map('Band.High.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active'])])

    # --- Run Control Buttons (Start, Pause, Stop) ---
    # UPDATED: Changed font size for scan control buttons to 13pt
    style.configure('StartScan.TButton',
                     background=COLOR_PALETTE['green_btn'],
                     foreground='white',
                     font=('Helvetica', 13, 'bold'),
                     padding=[10, 5])
    style.map('StartScan.TButton',
              background=[('active', COLOR_PALETTE['green_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    # UPDATED: Changed font size for scan control buttons to 13pt
    style.configure('PauseScan.TButton',
                     background=COLOR_PALETTE['orange_btn'],
                     foreground='black',
                     font=('Helvetica', 13, 'bold'),
                     padding=[10, 5])
    style.map('PauseScan.TButton',
              background=[('active', COLOR_PALETTE['orange_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])

    # UPDATED: Changed font size for scan control buttons to 13pt
    style.configure('StopScan.TButton',
                     background=COLOR_PALETTE['red_btn'],
                     foreground='white',
                     font=('Helvetica', 13, 'bold'),
                     padding=[10, 5])
    style.map('StopScan.TButton',
              background=[('active', COLOR_PALETTE['red_btn_active']),
                          ('disabled', COLOR_PALETTE['disabled_bg'])],
              foreground=[('disabled', COLOR_PALETTE['disabled_fg'])])
    
    # UPDATED: Changed font size for scan control buttons to 13pt
    style.configure('ResumeScan.Blink.TButton',
                     background=COLOR_PALETTE['select_bg'],
                     foreground='white',
                     font=('Helvetica', 13, 'bold'),
                     padding=[10, 5])
    style.map('ResumeScan.Blink.TButton',
              background=[('active', COLOR_PALETTE['blue_btn_active'])])


    # --- Other Generic Buttons ---
    # UPDATED: Changed font size for generic buttons to 13pt
    style.configure('Green.TButton', background=COLOR_PALETTE['green_btn'], foreground='white', font=('Helvetica', 13))
    style.map('Green.TButton', background=[('active', COLOR_PALETTE['green_btn_active'])])
    # UPDATED: Changed font size for generic buttons to 13pt
    style.configure('Red.TButton', background=COLOR_PALETTE['red_btn'], foreground='white', font=('Helvetica', 13))
    style.map('Red.TButton', background=[('active', COLOR_PALETTE['red_btn_active'])])
    # UPDATED: Changed font size for generic buttons to 13pt
    style.configure('Blue.TButton', background=COLOR_PALETTE['blue_btn'], foreground='white', font=('Helvetica', 13))
    style.map('Blue.TButton', background=[('active', COLOR_PALETTE['blue_btn_active'])])
    # UPDATED: Changed font size for generic buttons to 13pt
    style.configure('Orange.TButton', background=COLOR_PALETTE['orange_btn'], foreground='black', font=('Helvetica', 13))
    style.map('Orange.TButton', background=[('active', COLOR_PALETTE['orange_btn_active'])])
    # UPDATED: Changed font size for generic buttons to 13pt
    style.configure('Purple.TButton', background=COLOR_PALETTE['purple_btn'], foreground='white', font=('Helvetica', 13))
    style.map('Purple.TButton', background=[('active', COLOR_PALETTE['purple_btn_active'])])

    # --- Treeview ---
    # UPDATED: Changed font size for Treeview to 13pt
    style.configure("Treeview", background=COLOR_PALETTE['input_bg'], foreground=COLOR_PALETTE['foreground'], fieldbackground=COLOR_PALETTE['input_bg'], font=("Helvetica", 13))
    style.map("Treeview", background=[('selected', COLOR_PALETTE['select_bg'])], foreground=[('selected', COLOR_PALETTE['select_fg'])])
    # UPDATED: Changed font size for Treeview headings to 13pt
    style.configure("Treeview.Heading", font=("Helvetica", 13, "bold"), background=COLOR_PALETTE['active_bg'], foreground=COLOR_PALETTE['foreground'], relief="flat")
    style.map("Treeview.Heading", background=[('active', COLOR_PALETTE['active_bg'])])

    debug_log_func(f"✅ Exiting {current_function}. All widget styles have been applied.",
                     file=f"{os.path.basename(__file__)} - {current_app_version}",
                     version=current_app_version,
                     function=current_function, special=True)