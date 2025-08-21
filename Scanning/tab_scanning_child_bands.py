# tabs/Scanning/tab_scanning_child_bands.py
#
# This file defines the BandsTab, a Tkinter Frame that contains the UI for
# selecting and deselecting frequency bands for a scan. It has been
# refactored to allow multi-state selection (Low, Medium, High importance)
# and now includes a table and a bar chart to visualize the selected bands.
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
# Version 20250810.220100.5 (FIXED: Removed redundant save_config call from _on_tab_selected to prevent overwriting saved settings on app startup.)

current_version = "20250810.220100.5"
current_version_hash = 20250810 * 220100 * 5 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from display.debug_logic import debug_log
from display.console_logic import console_log
from settings_and_config.config_manager import save_config

class BandsTab(ttk.Frame):
    """
    A Tkinter Frame that provides the user interface for selecting frequency bands to scan.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the BandsTab, creating the UI for multi-state band selection,
        # a summary table, and a visual bar chart of the selected bands.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance.
        #   console_print_func (function): A function for printing to the console.
        #   **kwargs: Arbitrary keyword arguments.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing BandsTab...",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.bands_inner_frame_id = None
        self.band_chart_fig = None
        self.band_chart_ax = None
        self.band_chart_canvas = None

        self._create_widgets()
        # The call to _on_tab_selected here is crucial, but it shouldn't save the config!
        self.after(100, self._on_tab_selected)

        debug_log(f"BandsTab initialized. All the band buttons are ready to be toggled!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges all widgets in the tab, including the control buttons,
        # the frame for the band buttons, the summary table, and the bar chart.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating BandsTab widgets.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # Band buttons frame
        self.grid_rowconfigure(2, weight=1) # Table frame
        self.grid_rowconfigure(3, weight=1) # Chart frame

        # --- Band Selection Buttons ---
        band_button_frame = ttk.Frame(self, style='Dark.TFrame')
        band_button_frame.grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        band_button_frame.grid_columnconfigure(0, weight=1)
        band_button_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(band_button_frame, text="Select All", command=self._select_all_bands, style='Blue.TButton').grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(band_button_frame, text="Deselect All", command=self._deselect_all_bands, style='Blue.TButton').grid(row=0, column=1, padx=5, sticky="ew")

        # Frame for all Band Buttons
        self.bands_inner_frame = ttk.Frame(self, style='Dark.TFrame')
        self.bands_inner_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.bands_inner_frame.grid_columnconfigure(0, weight=1)
        self.bands_inner_frame.grid_columnconfigure(1, weight=1)

        # --- Selected Bands Table (Treeview) ---
        table_frame = ttk.Frame(self, style='Dark.TFrame')
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.band_table = ttk.Treeview(table_frame, columns=("Name", "Start", "Stop", "Level"), show="headings")
        self.band_table.heading("Name", text="Name")
        self.band_table.heading("Start", text="Start (MHz)")
        self.band_table.heading("Stop", text="Stop (MHz)")
        self.band_table.heading("Level", text="Level")
        self.band_table.grid(row=0, column=0, sticky="nsew")
        
        # --- Band Importance Chart (Matplotlib) ---
        chart_frame = ttk.Frame(self, style='Dark.TFrame')
        chart_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        self.band_chart_fig = Figure(figsize=(5, 3), dpi=100, facecolor='#2b2b2b')
        self.band_chart_ax = self.band_chart_fig.add_subplot(111, facecolor='#1e1e1e')
        self.band_chart_canvas = FigureCanvasTkAgg(self.band_chart_fig, master=chart_frame)
        self.band_chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        debug_log(f"BandsTab widgets created.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

    def _populate_band_buttons(self):
        # This function description tells me what this function does
        # Populates the scrollable frame with band selection buttons, dynamically
        # creating a button for each band defined in the application's band_vars.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the `bands_inner_frame` with buttons.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating band buttons.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        for widget in self.bands_inner_frame.winfo_children():
            widget.destroy()
        
        self.bands_inner_frame.grid_columnconfigure(0, weight=1)
        self.bands_inner_frame.grid_columnconfigure(1, weight=1)

        for i, band_item in enumerate(self.app_instance.band_vars):
            band = band_item["band"]
            level = band_item.get("level", 0) # Get level, default to 0
            
            button_text = f"{band['Band Name']}\nStart: {band['Start MHz']:.3f} MHz\nStop: {band['Stop MHz']:.3f} MHz"
            
            btn = ttk.Button(self.bands_inner_frame, text=button_text)
            band_item['widget'] = btn # Store widget reference
            
            btn.configure(command=lambda bi=band_item: self._on_band_button_toggle(bi))
            
            self._update_button_style(btn, level)

            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
            
        debug_log(f"Band buttons populated. Ready to toggle!",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)


    def _update_button_style(self, button, level):
        # This function description tells me what this function does
        # Updates the style of a band button based on its importance level.
        #
        # Inputs to this function
        #   button (ttk.Button): The button widget to style.
        #   level (int): The importance level (0=unselected, 1=low, 2=medium, 3=high).
        #
        # Outputs of this function
        #   None. Modifies the appearance of the button.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating button style for level {level}.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        if level == 1:
            button.configure(style="Band.Low.TButton")
        elif level == 2:
            button.configure(style="Band.Medium.TButton")
        elif level == 3:
            button.configure(style="Band.High.TButton")
        else:
            button.configure(style="Band.TButton")


    def _on_band_button_toggle(self, band_item):
        # This function description tells me what this function does
        # Cycles the importance level of a band when its button is clicked and
        # updates the button's style. It then updates the table, chart, and saves the config.
        #
        # Inputs to this function
        #   band_item (dict): The dictionary containing the band's info, level, and widget.
        #
        # Outputs of this function
        #   None. Updates internal state, saves config, and refreshes the UI.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Toggling band importance. Current level: {band_item.get('level', 0)}",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        current_level = band_item.get("level", 0)
        new_level = (current_level + 1) % 4
        band_item["level"] = new_level
        
        self._update_button_style(band_item["widget"], new_level)
        
        # This is the correct place to save the config, AFTER a user action.
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        
        self._update_band_table()
        self._update_band_chart()


    def _update_band_table(self):
        # This function description tells me what this function does
        # Updates the Treeview table to display all bands with a non-zero importance level.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Refreshes the content of the `band_table` Treeview.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating band table with selected bands.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        # Clear existing entries
        for item in self.band_table.get_children():
            self.band_table.delete(item)

        importance_map = {1: "Low", 2: "Medium", 3: "High"}
        for band_item in self.app_instance.band_vars:
            level = band_item.get("level", 0)
            if level > 0:
                band = band_item["band"]
                self.band_table.insert("", "end", values=(
                    band['Band Name'],
                    f"{band['Start MHz']:.3f}",
                    f"{band['Stop MHz']:.3f}",
                    importance_map.get(level, "Unknown")
                ))

        self.band_table.update_idletasks()
        console_log("Band importance table updated.", function=current_function)
        
    def _update_band_chart(self):
        # This function description tells me what this function does
        # Creates or updates a Matplotlib bar chart to visually represent the selected
        # bands, their frequency ranges, and their importance levels.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Renders the chart to the Tkinter canvas.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating band chart.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)

        self.band_chart_ax.clear()
        self.band_chart_ax.set_facecolor('#1e1e1e')
        self.band_chart_ax.tick_params(axis='x', colors='white')
        self.band_chart_ax.tick_params(axis='y', colors='white')
        self.band_chart_ax.spines['bottom'].set_color('white')
        self.band_chart_ax.spines['top'].set_color('white')
        self.band_chart_ax.spines['left'].set_color('white')
        self.band_chart_ax.spines['right'].set_color('white')
        self.band_chart_ax.set_title("Band Importance Levels", color='white')
        self.band_chart_ax.set_xlabel("Frequency (MHz)", color='white')
        self.band_chart_ax.set_ylabel("Importance", color='white')

        # Map importance levels to Y values
        importance_y_map = {0: -10, 1: 25, 2: 50, 3: 100}

        selected_bands = []
        for band_item in self.app_instance.band_vars:
            level = band_item.get("level", 0)
            band = band_item["band"]
            selected_bands.append({
                'name': band['Band Name'],
                'start': band['Start MHz'],
                'stop': band['Stop MHz'],
                'level': level
            })

        if not selected_bands:
            debug_log(f"No bands selected to plot.",
                        file=os.path.basename(__file__),
                        version=current_version,
                        function=current_function)
            self.band_chart_canvas.draw()
            return
            
        min_freq = min(b['start'] for b in selected_bands)
        max_freq = max(b['stop'] for b in selected_bands)
        if min_freq == max_freq:
            min_freq -= 1
            max_freq += 1
        
        self.band_chart_ax.set_xlim(min_freq, max_freq)
        self.band_chart_ax.set_ylim(-20, 110)

        for band in selected_bands:
            color = 'gray'
            if band['level'] == 1:
                color = 'yellow'
            elif band['level'] == 2:
                color = 'orange'
            elif band['level'] == 3:
                color = 'red'
            
            self.band_chart_ax.bar(
                x=(band['start'] + band['stop']) / 2,
                height=importance_y_map.get(band['level'], -10),
                width=band['stop'] - band['start'],
                color=color,
                edgecolor='white'
            )

        self.band_chart_canvas.draw()
        console_log("Band importance chart updated.", function=current_function)


    def _update_all_band_button_styles(self):
        # This function description tells me what this function does
        # Iterates through all band buttons and updates their visual style
        # to match the current state of their associated importance level.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Modifies the appearance of buttons.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating all band button styles.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        for band_item in self.app_instance.band_vars:
            widget = band_item.get("widget")
            level = band_item.get("level", 0)
            if widget:
                self._update_button_style(widget, level)


    def _select_all_bands(self):
        # This function description tells me what this function does
        # Sets all band importance levels to High (3) and updates the UI.
        # It then saves the new configuration.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Updates internal state and saves config.
        current_function = inspect.currentframe().f_code.co_name
        console_log("Selecting all bands for scan.", function=current_function)
        debug_log(f"Selecting all bands and saving config.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        for band_item in self.app_instance.band_vars:
            band_item["level"] = 3 # High importance
        
        self._update_all_band_button_styles()
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self._update_band_table()
        self._update_band_chart()


    def _deselect_all_bands(self):
        # This function description tells me what this function does
        # Sets all band importance levels to 0 (unselected) and updates the UI.
        # It then saves the new configuration.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Updates internal state and saves config.
        current_function = inspect.currentframe().f_code.co_name
        console_log("Deselecting all bands for scan.", function=current_function)
        debug_log(f"Deselecting all bands and saving config.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        for band_item in self.app_instance.band_vars:
            band_item["level"] = 0 # Unselected
        
        self._update_all_band_button_styles()
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self._update_band_table()
        self._update_band_chart()


    def _on_tab_selected(self, event=None):
        # This function description tells me what this function does
        # Is called when the tab is selected. It ensures the UI elements
        # are populated and their styles are updated to reflect the current state.
        #
        # Inputs to this function
        #   event (tkinter.Event, optional): The event object.
        #
        # Outputs of this function
        #   None. Refreshes the UI.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"BandsTab selected. Populating and refreshing all widgets.",
                    file=os.path.basename(__file__),
                    version=current_version,
                    function=current_function)
        
        # We only want to populate the UI here, not save the config.
        # The save action is triggered by the user interacting with the buttons.
        self._populate_band_buttons()
        self._update_all_band_button_styles()
        self._update_band_table()
        self._update_band_chart()
