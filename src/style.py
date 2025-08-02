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
# Version 20250802.0050.1 (Refactored debug_print to debug_log; updated imports and flair.)

current_version = "20250802.0050.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 50 * 1 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect # For debug_log

# Import the debug logic module to use debug_log
from src.debug_logic import debug_log


def apply_styles(style, debug_log_func, current_app_version, parent_tab_colors):
    """
    Function Description:
    Configures and applies custom ttk styles for a modern dark theme
    to various Tkinter widgets within the application. This includes
    defining styles for parent and child notebooks to support the
    two-layer tab structure with unique and dynamic colors for parent tabs.

    Inputs:
        style (ttk.Style): The ttk.Style object of the main application.
        debug_log_func (function): The debug logging function to use.
        current_app_version (str): The current version string of the application for logging.
        parent_tab_colors (dict): A dictionary mapping parent tab names to their colors.

    Process of this function:
        1. Sets the overall theme to 'alt'.
        2. Configures general TButton styles (background, foreground, font, padding).
        3. Configures TEntry styles (background, foreground, border).
        4. Configures TLabel styles (foreground, font).
        5. Configures TCombobox styles.
        6. Configures TCheckbutton styles.
        7. Configures TFrame styles.
        8. Configures TProgressbar styles.
        9. Configures styles for the main parent notebook tabs, including active/inactive states
           and dynamic colors based on `parent_tab_colors`.
        10. Configures styles for child notebooks to provide a consistent appearance.
        11. Configures specific button styles like 'BigScanButton', 'LargePreset.TButton',
            'SelectedPreset.Orange.TButton', and 'LargeYAK.TButton'.
        12. Logs the application of styles using `debug_log_func`.

    Outputs of this function:
        None. Modifies the global ttk.Style object.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log_func(f"Applying custom Tkinter styles. Making the GUI look sharp! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

    # Set the theme
    style.theme_use('alt')

    # General Button Style
    style.configure("TButton",
                    background="#4a4a4a",
                    foreground="white",
                    font=("Helvetica", 10, "bold"),
                    padding=10)
    style.map("TButton",
              background=[('active', '#606060')])

    # Entry Style
    style.configure("TEntry",
                    fieldbackground="#333333",
                    foreground="white",
                    bordercolor="#606060",
                    lightcolor="#606060",
                    darkcolor="#222222")

    # Label Style
    style.configure("TLabel",
                    foreground="white",
                    background="#2e2e2e",
                    font=("Helvetica", 10))

    # Combobox Style
    style.configure("TCombobox",
                    fieldbackground="#333333",
                    background="#4a4a4a",
                    foreground="white",
                    selectbackground="#606060",
                    selectforeground="white",
                    bordercolor="#606060",
                    lightcolor="#606060",
                    darkcolor="#222222")
    style.map('TCombobox',
              fieldbackground=[('readonly', '#333333')],
              selectbackground=[('readonly', '#606060')],
              selectforeground=[('readonly', 'white')],
              background=[('readonly', '#4a4a4a')])

    # Checkbutton Style
    style.configure("TCheckbutton",
                    background="#2e2e2e",
                    foreground="white",
                    font=("Helvetica", 10))
    style.map("TCheckbutton",
              background=[('active', '#3a3a3a')])

    # Frame Style (for general background)
    style.configure("TFrame",
                    background="#2e2e2e")

    # Progressbar Style
    style.configure("TProgressbar",
                    background="#007acc", # Blue color for progress
                    troughcolor="#333333",
                    bordercolor="#606060")

    # --- Notebook (Tab) Styles ---

    # Parent Notebook (Main Tabs)
    style.configure("Parent.TNotebook",
                    background="#2e2e2e",
                    tabposition='nw') # Tabs on the top-left

    # Map colors for each parent tab dynamically
    for tab_name, color_hex in parent_tab_colors.items():
        # Active tab style
        style.configure(f"{tab_name}.TNotebook.Tab",
                        background=color_hex,
                        foreground="white",
                        font=("Helvetica", 10, "bold"),
                        padding=[10, 5])
        style.map(f"{tab_name}.TNotebook.Tab",
                  background=[('selected', color_hex), ('active', color_hex)],
                  foreground=[('selected', 'white'), ('active', 'white')])

        # Inactive tab style (default for other tabs)
        # This will be the default for any tab not currently selected
        style.configure(f"TNotebook.Tab",
                        background="#4a4a4a", # Default inactive tab color
                        foreground="white",
                        font=("Helvetica", 10),
                        padding=[10, 5])
        style.map(f"TNotebook.Tab",
                  background=[('active', '#606060'), ('!selected', '#4a4a4a')],
                  foreground=[('active', 'white'), ('!selected', 'white')])


    # Child Notebooks (Nested Tabs) - consistent dark look
    # Instrument Child Notebook
    style.configure("InstrumentChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("InstrumentChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("InstrumentChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])

    # Scanning Child Notebook
    style.configure("ScanningChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("ScanningChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("ScanningChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])

    # Plotting Child Notebook
    style.configure("PlottingChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("PlottingChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("PlottingChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])

    # Markers Child Notebook
    style.configure("MarkersChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("MarkersChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("MarkersChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])

    # Presets Child Notebook
    style.configure("PresetsChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("PresetsChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("PresetsChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])

    # Experiments Child Notebook
    style.configure("ExperimentsChild.TNotebook",
                    background="#2e2e2e",
                    tabposition='n')
    style.configure("ExperimentsChild.TNotebook.Tab",
                    background="#444444",
                    foreground="white",
                    font=("Helvetica", 9),
                    padding=[8, 4])
    style.map("ExperimentsChild.TNotebook.Tab",
              background=[('selected', '#555555'), ('active', '#666666')],
              foreground=[('selected', 'white'), ('active', 'white')])


    # Custom Button Styles
    style.configure('BigScanButton',
                    font=('Helvetica', 12, 'bold'),
                    background="#007acc", # Blue
                    foreground="white",
                    padding=[20, 10])
    style.map('BigScanButton',
              background=[('active', '#005f99')]) # Darker blue on active

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
              background=[('active', '#e07b00')]) # Darker orange on active
    
    debug_log_func(f"Custom Tkinter styles applied successfully. The GUI is looking sharp! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function,
                    special=True)
