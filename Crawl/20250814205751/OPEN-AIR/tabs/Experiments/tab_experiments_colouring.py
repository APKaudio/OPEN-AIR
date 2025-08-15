# tabs/Experiments/tab_experiments_colouring.py
#
# This file defines the ColouringTab, a Tkinter Frame that provides
# functionality to read and display the color palette defined in style.py.
# It will show each color variable's name and a small colored box.
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
# Version 20250816.200000.11 (FIXED: The tab now dynamically reads and displays all colors and styles from `program_style.py`, with clear labels and live previews of buttons.)

current_version = "20250816.200000.11"
current_version_hash = 20250816 * 200000 * 11

import tkinter as tk
from tkinter import ttk, TclError
import inspect
import os
import re

# Import the COLOR_PALETTE and other styles from style.py
from src.program_style import COLOR_PALETTE, COLOR_PALETTE_TABS, _get_dark_color
from display.debug_logic import debug_log
from display.console_logic import console_log

class ColouringTab(ttk.Frame):
    """
    A Tkinter Frame that displays the color palette defined in style.py.
    It shows each color variable's name and a small colored box representing its value,
    along with sections for font sizes and common UI element styles.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the ColouringTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Initializing ColouringTab...",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log

        self._create_widgets()

        debug_log(f"ColouringTab initialized. Ready to display colors and styles!",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Creates the widgets for the Colouring tab, including a scrollable frame
        to display the color variables, font sizes, and common UI element styles.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Creating ColouringTab widgets...",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Create a Canvas and a Scrollbar for scrollable content
        self.canvas = tk.Canvas(self, background=COLOR_PALETTE['background'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) # For Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # For Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel) # For Linux (scroll down)


        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self._populate_content()

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling for the canvas."""
        if self.canvas.winfo_exists(): # Check if canvas still exists
            if event.num == 4 or event.delta > 0: # Scroll up
                self.canvas.yview_scroll(-1, "unit")
            elif event.num == 5 or event.delta < 0: # Scroll down
                self.canvas.yview_scroll(1, "unit")

    def _populate_content(self):
        """
        Populates the scrollable frame with color palette, font sizes, and common styles.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Populating ColouringTab content...",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Clear any existing widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        row_idx = 0

        # --- Section 1: Color Palette (Grouped Horizontally) ---
        color_palette_main_frame = ttk.LabelFrame(self.scrollable_frame, text="Color Palette", style='Dark.TLabelframe', padding=(10, 10))
        color_palette_main_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        color_palette_main_frame.grid_columnconfigure(0, weight=1)
        color_palette_main_frame.grid_columnconfigure(1, weight=1)
        color_palette_main_frame.grid_columnconfigure(2, weight=1)
        row_idx += 1

        # Frame for Defaults/Globals
        defaults_frame = ttk.LabelFrame(color_palette_main_frame, text="Defaults / Globals", style='Dark.TLabelframe', padding=(5, 5))
        defaults_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        defaults_frame.grid_columnconfigure(0, weight=1) # For color name label
        defaults_frame.grid_columnconfigure(1, weight=0) # For color box

        # Frame for Buttons
        buttons_color_frame = ttk.LabelFrame(color_palette_main_frame, text="Button Colors", style='Dark.TLabelframe', padding=(5, 5))
        buttons_color_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        buttons_color_frame.grid_columnconfigure(0, weight=1)
        buttons_color_frame.grid_columnconfigure(1, weight=0)

        # Frame for Parent Tabs
        parent_tabs_color_frame = ttk.LabelFrame(color_palette_main_frame, text="Parent Tab Colors", style='Dark.TLabelframe', padding=(5, 5))
        parent_tabs_color_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        parent_tabs_color_frame.grid_columnconfigure(0, weight=1)
        parent_tabs_color_frame.grid_columnconfigure(1, weight=0)


        default_row_idx = 0
        button_row_idx = 0
        parent_tab_row_idx = 0

        for color_name, color_value in COLOR_PALETTE.items():
            if '_btn' in color_name: # Simple check for button related colors
                self._add_color_display_row(buttons_color_frame, f"{color_name}: {color_value}", color_value, button_row_idx)
                button_row_idx += 1
            elif color_name in ['white', 'black']:
                self._add_color_display_row(defaults_frame, f"{color_name}: {color_value}", color_value, default_row_idx)
                default_row_idx += 1
            else: # Defaults/Globals
                self._add_color_display_row(defaults_frame, f"{color_name}: {color_value}", color_value, default_row_idx)
                default_row_idx += 1
        
        # New loop for COLOR_PALETTE_TABS
        for tab_name, tab_colors in COLOR_PALETTE_TABS.items():
            ttk.Label(parent_tabs_color_frame, text=f"--- {tab_name.replace('_', ' ').title()} ---",
                      style='Dark.TLabel.Value', font=('Helvetica', 11, 'bold')).grid(row=parent_tab_row_idx, column=0, columnspan=2, pady=(10, 2), sticky="w", padx=5)
            parent_tab_row_idx += 1
            for state_name, hex_code in tab_colors.items():
                self._add_color_display_row(parent_tabs_color_frame, f"{state_name}: {hex_code}", hex_code, parent_tab_row_idx, indent=1)
                parent_tab_row_idx += 1
                if state_name == 'active':
                    # Add inactive color as well for clarity
                    inactive_color = _get_dark_color(hex_code)
                    self._add_color_display_row(parent_tabs_color_frame, f"inactive: {inactive_color}", inactive_color, parent_tab_row_idx, indent=1)
                    parent_tab_row_idx += 1


        # --- Section 2: Font Sizes ---
        font_sizes_frame = ttk.LabelFrame(self.scrollable_frame, text="Common Font Sizes (Helvetica)", style='Dark.TLabelframe', padding=(10, 10))
        font_sizes_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        font_sizes_frame.grid_columnconfigure(0, weight=1)
        row_idx += 1

        common_font_sizes = [9, 10, 11, 12, 13, 14, 25, 100] # Based on style.py analysis
        current_font_row = 0
        for size in common_font_sizes:
            ttk.Label(font_sizes_frame, text=f"Font Size {size}pt", # Removed "Example Text"
                      background=COLOR_PALETTE['background'],
                      foreground=COLOR_PALETTE['foreground'],
                      font=('Helvetica', size, 'bold' if size >= 12 else '')).grid(row=current_font_row, column=0, sticky="w", padx=5, pady=2)
            current_font_row += 1

        # --- Section 3: Common UI Element Styles ---
        ui_styles_frame = ttk.LabelFrame(self.scrollable_frame, text="Common UI Element Styles", style='Dark.TLabelframe', padding=(10, 10))
        ui_styles_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        ui_styles_frame.grid_columnconfigure(0, weight=1)
        ui_styles_frame.grid_columnconfigure(1, weight=1)
        row_idx += 1

        # Define some conceptual styles based on style.py
        common_ui_styles = {
            "TLabel (Default)": {"widget_type": "label", "style_name": "TLabel"},
            "Dark.TLabel.Value": {"widget_type": "label", "style_name": "Dark.TLabel.Value"},
            "Red.TLabel.Value": {"widget_type": "label", "style_name": "Red.TLabel.Value"},
            "TEntry (Default)": {"widget_type": "entry", "style_name": "TEntry"},
            "TButton (Default)": {"widget_type": "button", "style_name": "TButton"},
            "Green.TButton": {"widget_type": "button", "style_name": "Green.TButton"},
            "Red.TButton": {"widget_type": "button", "style_name": "Red.TButton"},
            "Orange.TButton": {"widget_type": "button", "style_name": "Orange.TButton"},
            "Blue.TButton": {"widget_type": "button", "style_name": "Blue.TButton"},
            "Purple.TButton": {"widget_type": "button", "style_name": "Purple.TButton"},
            "StartScan.TButton": {"widget_type": "button", "style_name": "StartScan.TButton"},
            "PauseScan.TButton": {"widget_type": "button", "style_name": "PauseScan.TButton"},
            "StopScan.TButton": {"widget_type": "button", "style_name": "StopScan.TButton"},
            "LocalPreset.TButton": {"widget_type": "button", "style_name": "LocalPreset.TButton"},
            "SelectedPreset.Orange.TButton": {"widget_type": "button", "style_name": "SelectedPreset.Orange.TButton"},
            "DeviceButton.Blinking.TButton": {"widget_type": "button", "style_name": "DeviceButton.Blinking.TButton"},
            "ControlButton.Active.TButton": {"widget_type": "button", "style_name": "ControlButton.Active.TButton"},
            "Band.Low.TButton": {"widget_type": "button", "style_name": "Band.Low.TButton"},
            "Band.Medium.TButton": {"widget_type": "button", "style_name": "Band.Medium.TButton"},
            "Band.High.TButton": {"widget_type": "button", "style_name": "Band.High.TButton"},
        }
        
        current_ui_row = 0
        for display_name, properties in common_ui_styles.items():
            try:
                style_name = properties['style_name']
                style_spec = self.app_instance.style.lookup(style_name, 'font')
                if style_spec:
                    style_font = style_spec
                else:
                    style_font = ("Helvetica", 9)
            except TclError:
                style_font = ("Helvetica", 9)

            style_box = ttk.Frame(ui_styles_frame, style='Dark.TFrame', relief="solid", borderwidth=1)
            style_box.grid(row=current_ui_row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            style_box.grid_columnconfigure(0, weight=1) # For the label/button inside the box

            # Display style name and font
            ttk.Label(style_box, text=f"Style: {display_name} (Font: {style_font})",
                      background=COLOR_PALETTE['background'], foreground=COLOR_PALETTE['foreground'],
                      font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=2)

            example_text = display_name
            
            if properties.get("widget_type") == "button":
                example_widget = ttk.Button(style_box, text=example_text, style=style_name)
            elif properties.get("widget_type") == "entry":
                example_widget = ttk.Entry(style_box, style=style_name)
                example_widget.insert(0, example_text)
            else: # label
                example_widget = ttk.Label(style_box, text=example_text, style=style_name)
                
            example_widget.grid(row=1, column=0, sticky="w", padx=5, pady=2)

            current_ui_row += 1


        self.scrollable_frame.update_idletasks() # Update layout to ensure scrollregion is calculated correctly

    def _add_color_display_row(self, parent_frame, text, hex_color, row_idx, indent=0):
        """Helper to add a row for color display."""
        current_file = os.path.basename(__file__)
        current_function = inspect.currentframe().f_code.co_name

        padx_val = 5 + (indent * 15) # Indent nested colors

        # Label for color name and hex value
        color_label = ttk.Label(parent_frame, text=text,
                                background=COLOR_PALETTE['background'],
                                foreground=COLOR_PALETTE['foreground'],
                                font=('Helvetica', 9))
        color_label.grid(row=row_idx, column=0, sticky="w", padx=padx_val, pady=2)

        # Small frame to display the color
        color_box = tk.Frame(parent_frame, width=20, height=20, relief="solid", borderwidth=1, background=hex_color)
        color_box.grid(row=row_idx, column=1, sticky="e", padx=5, pady=2)

        debug_log(f"Displayed color: {text} with hex: {hex_color}",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the displayed colors and styles.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"ColouringTab selected. Refreshing color and style display.",
                    file=f"{current_file} - {current_version}",
                    version=current_version,
                    function=current_function)
        self._populate_content()