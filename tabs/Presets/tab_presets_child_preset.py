# tabs/Presets/tab_presets_child_preset.py
#
# This file defines the PresetFilesTab, a Tkinter Frame that displays available
# instrument preset files and allows loading them. It now uses a CSV file as a
# local cache for instrument preset details (Center, Span, RBW, NickName) and
# provides functionality to manage these nicknames.
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
# Version 20250801.1052.1 (Updated header and imports for new folder structure)

current_version = "20250801.1052.1" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import os
import sys
import inspect
import subprocess

# Import query_basic_instrument_settings_logic from instrument_logic - CORRECTED PATH
from src.instrument_logic import query_basic_instrument_settings_logic

# Import preset logic and CSV functions from preset_utils.py - CORRECTED PATH
from tabs.Presets.utils_preset import (
    load_selected_preset_logic, # NEW: Import the moved logic function
    query_device_presets_logic, # This one is now the moved logic function
    load_selected_preset as load_selected_preset_util, # Keep this alias for the low-level function if needed elsewhere
    save_user_preset_to_csv,
    load_user_presets_from_csv
)

from utils.utils_instrument_control import debug_print
from ref.frequency_bands import MHZ_TO_HZ # Import MHZ_TO_HZ for conversion

class PresetFilesTab(ttk.Frame):
    """
    A Tkinter Frame that displays available instrument preset files and allows loading them.
    It now uses a CSV file as a local cache for instrument preset details (Center, Span, RBW, NickName).
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # Function Description:
        # Initializes the PresetFilesTab, setting up the UI frame,
        # linking to the main application instance, and preparing
        # attributes for managing instrument preset files and their display.
        #
        # Inputs to this function:
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): Reference to the main application instance
        #                          to access shared variables and methods.
        #   console_print_func (function): A function to print messages to the
        #                                  application's console output.
        #   **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.
        #
        # Process of this function:
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to app_instance and console_print_func.
        #   3. Initializes internal lists and dictionaries for preset management:
        #      `instrument_preset_files` (list of device preset names).
        #      `cached_preset_details` (dictionary mapping preset filename to its loaded details).
        #      `preset_buttons` (mapping preset filename to button widget).
        #   4. Initializes `self.current_selected_button_widget` to track the currently
        #      visually selected button.
        #   5. Initializes `self.nickname_var` for the new nickname input.
        #   6. Calls `_create_widgets` to build the UI elements.
        #   7. Binds the `<<NotebookTabChanged>>` event to `_on_tab_selected` if a master is provided,
        #      ensuring the tab's state is updated when it becomes active.
        #
        # Outputs of this function:
        #   None. Initializes the Tkinter frame and its internal state.
        #
        # (2025-07-30) Change: Removed `user_preset_files`, added `cached_preset_details`.
        # (2025-07-30) Change: Added `self.nickname_var` for the new nickname input.
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print
        
        self.instrument_preset_files = [] # To store list of .sta files from device/local C:\PRESETS
        self.cached_preset_details = {}   # NEW: Dictionary to cache details from PRESETS.CSV
                                          # Key: Filename (e.g., "MY_PRESET.STA"), Value: {'Center': ..., 'Span': ..., 'RBW': ..., 'NickName': ...}
        
        self.preset_buttons = {} # Dictionary to store references to ALL preset buttons for dynamic updates
        self.current_selected_button_widget = None # Track the currently selected button widget for visual feedback

        self.nickname_var = tk.StringVar(self) # For the new Nickname Entry box

        self._create_widgets()
        # Bind the tab selection event
        if master:
            master.bind("<<NotebookTabChanged>>", self._on_tab_selected)

    def _create_widgets(self):
        # Function Description:
        # Creates and arranges the widgets for the Preset Files tab.
        # It sets up the "Query Presets from Device" button at the top,
        # followed by two scrollable canvas areas for "MON" and "Other" device presets,
        # and a new section for Nickname input with a "MAKE IT STICK" button at the bottom.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints a debug message.
        #   2. Configures the main grid for four columns.
        #   3. Creates and places the "Query Presets from Device" button in the top row.
        #   4. Creates LabelFrames and Canvas widgets for "MON Presets" and "Other Presets"
        #      in the row below the query button.
        #   5. Sets up scrollbars for each canvas and links them.
        #   6. Creates inner frames within each canvas to hold the actual preset buttons,
        #      configuring them for three-column layouts.
        #   7. Binds mouse wheel events to the canvases for scrolling.
        #   8. Creates a new frame for the Nickname input and "MAKE IT STICK" button,
        #      including a label, entry, and button, and places it in the bottom row.
        #
        # Outputs of this function:
        #   None. Populates the Tkinter frame with UI elements.
        #
        # (2025-07-30) Change: Moved Query Presets button to row 0, spanning all columns.
        # (2025-07-30) Change: Adjusted grid rows for MON/Other presets and Nickname section.
        # (2025-07-31) Change: Configured inner button frames to support 3 columns.
        """
        Creates and arranges the widgets for the Preset Files tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Creating PresetFilesTab widgets...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Configure grid for three main columns (two for MON, two for Other)
        # We need 3 columns for buttons, plus 2 for scrollbars.
        self.grid_columnconfigure(0, weight=1) # MON column content
        self.grid_columnconfigure(1, weight=0) # Scrollbar for MON
        self.grid_columnconfigure(2, weight=1) # Other column content
        self.grid_columnconfigure(3, weight=0) # Scrollbar for Other
        
        # Configure grid rows
        self.grid_rowconfigure(0, weight=0) # For the Query button (fixed height)
        self.grid_rowconfigure(1, weight=1) # Main row for canvases (expands)
        self.grid_rowconfigure(2, weight=0) # For the new Nickname section (fixed height)

        # --- Query Presets Button (TOP) ---
        self.query_presets_button = ttk.Button(self, text="Query Presets from Device", command=self._query_presets_from_device, state=tk.DISABLED, style='Blue.TButton')
        self.query_presets_button.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="ew") # Spanning across all columns

        # --- MON Presets Section ---
        # Create a container frame for MON presets to manage its label and canvas
        self.mon_section_frame = ttk.Frame(self, style='Dark.TFrame')
        self.mon_section_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.mon_section_frame.grid_rowconfigure(0, weight=0) # For label
        self.mon_section_frame.grid_rowconfigure(1, weight=1) # For canvas
        self.mon_section_frame.grid_columnconfigure(0, weight=1) # For canvas

        ttk.Label(self.mon_section_frame, text="MON Presets (Device)",
                  background="#333333", foreground="#F4902C", font=("Helvetica", 16, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.mon_preset_canvas = tk.Canvas(self.mon_section_frame, borderwidth=0, highlightthickness=0, bg='#333333')
        self.mon_preset_canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0) # No extra padding here

        self.mon_preset_scrollbar = ttk.Scrollbar(self.mon_section_frame, orient="vertical", command=self.mon_preset_canvas.yview)
        self.mon_preset_scrollbar.grid(row=1, column=1, sticky="ns") # Placed within mon_section_frame
        self.mon_preset_canvas.config(yscrollcommand=self.mon_preset_scrollbar.set)

        self.inner_mon_buttons_frame = ttk.Frame(self.mon_preset_canvas, style='Dark.TFrame')
        self.mon_preset_canvas.create_window((0, 0), window=self.inner_mon_buttons_frame, anchor="nw")
        self.inner_mon_buttons_frame.grid_columnconfigure(0, weight=1)
        self.inner_mon_buttons_frame.grid_columnconfigure(1, weight=1)
        self.inner_mon_buttons_frame.grid_columnconfigure(2, weight=1) # NEW: Third column
        self.inner_mon_buttons_frame.bind("<Configure>", lambda e: self.mon_preset_canvas.config(scrollregion=self.mon_preset_canvas.bbox("all")))
        self.mon_preset_canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.mon_preset_canvas.bind('<Leave>', self._unbind_mouse_wheel)

        # --- Other Presets Section ---
        # Create a container frame for Other presets
        self.other_section_frame = ttk.Frame(self, style='Dark.TFrame')
        self.other_section_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=5)
        self.other_section_frame.grid_rowconfigure(0, weight=0) # For label
        self.other_section_frame.grid_rowconfigure(1, weight=1) # For canvas
        self.other_section_frame.grid_columnconfigure(0, weight=1) # For canvas

        ttk.Label(self.other_section_frame, text="Other Presets (Device)",
                  background="#333333", foreground="#F4902C", font=("Helvetica", 16, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.other_preset_canvas = tk.Canvas(self.other_section_frame, borderwidth=0, highlightthickness=0, bg='#333333')
        self.other_preset_canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0) # No extra padding here

        self.other_preset_scrollbar = ttk.Scrollbar(self.other_section_frame, orient="vertical", command=self.other_preset_canvas.yview)
        self.other_preset_scrollbar.grid(row=1, column=1, sticky="ns") # Placed within other_section_frame
        self.other_preset_canvas.config(yscrollcommand=self.other_preset_scrollbar.set)

        self.inner_other_buttons_frame = ttk.Frame(self.other_preset_canvas, style='Dark.TFrame')
        self.other_preset_canvas.create_window((0, 0), window=self.inner_other_buttons_frame, anchor="nw")
        self.inner_other_buttons_frame.grid_columnconfigure(0, weight=1)
        self.inner_other_buttons_frame.grid_columnconfigure(1, weight=1)
        self.inner_other_buttons_frame.grid_columnconfigure(2, weight=1) # NEW: Third column
        self.inner_other_buttons_frame.bind("<Configure>", lambda e: self.other_preset_canvas.config(scrollregion=self.inner_other_buttons_frame.bbox("all")))
        self.other_preset_canvas.bind('<Enter>', self._bind_mouse_wheel)
        self.other_preset_canvas.bind('<Leave>', self._unbind_mouse_wheel)

        # --- Nickname Input Section (BOTTOM) ---
        self.nickname_frame = ttk.Frame(self, style='Dark.TFrame')
        self.nickname_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.nickname_frame.grid_columnconfigure(0, weight=0) # Label
        self.nickname_frame.grid_columnconfigure(1, weight=1) # Entry
        self.nickname_frame.grid_columnconfigure(2, weight=0) # Button

        ttk.Label(self.nickname_frame, text="Nick Name:",
                  background="#333333", foreground="#F4902C", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.nickname_entry = ttk.Entry(self.nickname_frame, textvariable=self.nickname_var, width=50, style='TEntry')
        self.nickname_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.make_it_stick_button = ttk.Button(self.nickname_frame, text="MAKE IT STICK", command=self._on_make_it_stick_click, style='Green.TButton')
        self.make_it_stick_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")


        debug_print("PresetFilesTab widgets created.", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _bind_mouse_wheel(self, event):
        # Function Description:
        # Binds mouse wheel events for the canvas to enable scrolling.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function:
        #   1. Binds the `<MouseWheel>`, `<Button-4>`, and `<Button-5>` events
        #      to the `_on_mouse_wheel` handler for the canvas.
        #
        # Outputs of this function:
        #   None. Configures event bindings.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """Binds mouse wheel events for the canvas."""
        event.widget.bind_all("<MouseWheel>", self._on_mouse_wheel)
        event.widget.bind_all("<Button-4>", self._on_mouse_wheel) # For Linux
        event.widget.bind_all("<Button-5>", self._on_mouse_wheel) # For Linux

    def _unbind_mouse_wheel(self, event):
        # Function Description:
        # Unbinds mouse wheel events for the canvas.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function:
        #   1. Unbinds the `<MouseWheel>`, `<Button-4>`, and `<Button-5>` events
        #      from the canvas.
        #
        # Outputs of this function:
        #   None. Removes event bindings.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """Unbinds mouse wheel events for the canvas."""
        event.widget.unbind_all("<MouseWheel>")
        event.widget.unbind_all("<Button-4>")
        event.widget.unbind_all("<Button-5>")

    def _on_mouse_wheel(self, event):
        # Function Description:
        # Handles mouse wheel scrolling for the canvas, adjusting the view
        # based on the platform and event delta.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object containing scroll information.
        #
        # Process of this function:
        #   1. Checks the operating system (`sys.platform`).
        #   2. Adjusts the `yview_scroll` of the canvas based on the event delta
        #      for macOS, Linux, or Windows.
        #
        # Outputs of this function:
        #   None. Scrolls the canvas view.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """Handles mouse wheel scrolling for the canvas."""
        if sys.platform == "darwin":
            event.widget.yview_scroll(-1 * int(event.delta), "units")
        elif event.num == 4: # Linux scroll up
            event.widget.yview_scroll(-1, "units")
        elif event.num == 5: # Linux scroll down
            event.widget.yview_scroll(1, "units")
        else: # Windows
            event.widget.yview_scroll(-1 * int(event.delta/120), "units")

    def _query_presets_from_device(self):
        # Function Description:
        # Queries the connected instrument for available preset files and updates the display.
        # This function is responsible for initiating the communication with the device
        # to retrieve its stored presets and then populating the UI with buttons for them.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints debug messages indicating the start of the query process.
        #   2. Calls `query_device_presets_logic` from `preset_utils` to get the list of presets.
        #   3. If presets are successfully retrieved:
        #      a. Updates `self.instrument_preset_files` with the new list.
        #      b. Calls `populate_instrument_preset_buttons` to render the new buttons.
        #   4. If no presets are retrieved or an error occurs, clears the display.
        #
        # Outputs of this function:
        #   None. Updates internal state and the GUI display of presets.
        #
        # (2025-07-30) Change: Renamed `device_preset_files` to `instrument_preset_files` and calls `populate_instrument_preset_buttons`.
        """
        Queries the connected instrument for available preset files and updates the display.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        self.console_print_func("Querying device presets...")
        debug_print("Calling query_device_presets_logic...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        # Add debug print for app_instance.inst before calling the logic function
        self.console_print_func(f"Instrument instance in _query_presets_from_device: {self.app_instance.inst}")
        debug_print(f"Instrument instance in _query_presets_from_device: {self.app_instance.inst}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Call the logic function from preset_utils
        presets = query_device_presets_logic(self.app_instance, self.console_print_func)
        
        if presets:
            self.instrument_preset_files = presets # Store instrument presets
            self.populate_instrument_preset_buttons(presets) # Populate instrument buttons
        else:
            self.instrument_preset_files = []
            self.populate_instrument_preset_buttons([]) # Clear display

    def _load_selected_preset(self):
        # Function Description:
        # Loads the currently selected preset onto the instrument.
        # This method is called by the main app's "Load Selected Preset" button.
        # It retrieves the selected preset name from `app_instance.last_selected_preset_name_var`,
        # calls the utility function to load it, and updates the UI accordingly.
        # It also updates the Nickname entry box and saves the preset details to CSV.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Retrieves the selected preset name from `app_instance.last_selected_preset_name_var`.
        #   3. If a preset is selected and an instrument is connected:
        #      a. Calls `load_selected_preset_logic` to load the preset.
        #      b. If successful, updates the `app_instance` variables for center frequency, span, and RBW,
        #         and then updates the button's visual information.
        #      c. Retrieves or defaults a nickname, updates the nickname entry, and saves to CSV.
        #      d. If unsuccessful, reverts the button style and clears the selection.
        #   4. If no preset is selected or no instrument is connected, prints a warning and
        #      ensures the UI reflects no selection.
        #
        # Outputs of this function:
        #   None. Interacts with the instrument and updates UI elements.
        #
        # (2025-07-30) Change: Uses app_instance.last_selected_preset_name_var for state.
        # (2025-07-30) Change: Updates app_instance variables for frequency, span, RBW upon successful load.
        # (2025-07-30) Change: Removed simpledialog.askstring. Nickname now populated from cache or default, and displayed in entry box.
        """
        Loads the currently selected preset onto the instrument.
        This method is called by the main app's "Load Selected Preset" button.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        
        # Get the selected preset name from the app_instance's persistent variable
        selected_preset_name = self.app_instance.last_selected_preset_name_var.get()

        if selected_preset_name and self.app_instance and self.app_instance.inst:
            self.console_print_func(f"Loading preset: {selected_preset_name}")
            debug_print(f"Calling load_selected_preset_logic for: {selected_preset_name}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            
            # Call the load logic function from preset_utils
            # These values (center_freq_hz, span_hz, rbw_hz) are returned in Hz
            success, center_freq_hz, span_hz, rbw_hz = load_selected_preset_logic(self.app_instance, selected_preset_name, self.console_print_func)
            
            if success:
                self.console_print_func(f"✅ Preset '{selected_preset_name}' loaded. Instrument settings updated.")
                
                # Convert to MHz for display and CSV storage
                center_freq_mhz_display = center_freq_hz / MHZ_TO_HZ
                span_mhz_display = span_hz / MHZ_TO_HZ

                self.app_instance.last_loaded_preset_center_freq_mhz_var.set(f"{center_freq_mhz_display:.3f}")
                self.app_instance.last_loaded_preset_span_mhz_var.set(f"{span_mhz_display:.3f}")
                self.app_instance.last_loaded_preset_rbw_hz_var.set(str(int(rbw_hz))) # Ensure RBW is integer string

                # Get NickName from cache or default
                cached_data = self.cached_preset_details.get(selected_preset_name, {})
                nickname = cached_data.get('NickName', selected_preset_name.replace('.STA', '').replace('_', ' '))
                self.nickname_var.set(nickname) # Update the Nickname entry box
                debug_print(f"In _load_selected_preset: Setting nickname_var to '{nickname}' from cached_data: {cached_data}", file=current_file, function=current_function, console_print_func=self.console_print_func)


                # Save the queried details (and NickName) to CSV
                preset_data_to_save = {
                    'Filename': selected_preset_name,
                    'Center': center_freq_mhz_display, # Save in MHz
                    'Span': span_mhz_display,           # Save in MHz
                    'RBW': rbw_hz,                      # Save in Hz
                    'NickName': nickname
                }
                save_user_preset_to_csv(preset_data_to_save, self.app_instance.CONFIG_FILE, self.console_print_func)
                self.cached_preset_details[selected_preset_name] = preset_data_to_save # Update cache in memory
                debug_print(f"In _load_selected_preset: Saved to CSV and updated cache for '{selected_preset_name}' with data: {preset_data_to_save}", file=current_file, function=current_function, console_print_func=self.console_print_func)


                # Update the button text with the new settings (now including NickName)
                self.update_preset_button_info(selected_preset_name, center_freq_mhz_display, span_mhz_display, rbw_hz, nickname)
                # The style is already applied at the beginning of this function, no need to re-apply here.
            else:
                self.console_print_func(f"❌ Failed to load preset '{selected_preset_name}'.")
                self._update_selected_button_style(None) # Deselect on failure
                self.app_instance.last_selected_preset_name_var.set("")
                self.app_instance.last_loaded_preset_center_freq_mhz_var.set("")
                self.app_instance.last_loaded_preset_span_mhz_var.set("")
                self.app_instance.last_loaded_preset_rbw_hz_var.set("")
                self.nickname_var.set("") # Clear nickname entry on failure
                debug_print(f"In _load_selected_preset: Load failed for '{selected_preset_name}'. Cleared UI elements.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.console_print_func("⚠️ Warning: No preset selected or instrument not connected to load.")
            debug_print("Not connected to instrument, cannot load preset.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self._update_selected_button_style(None) # Deselect if no instrument
            self.app_instance.last_selected_preset_name_var.set("")
            self.app_instance.last_loaded_preset_center_freq_mhz_var.set("")
            self.app_instance.last_loaded_preset_span_mhz_var.set("")
            self.app_instance.last_loaded_preset_rbw_hz_var.set("")
            self.nickname_var.set("") # Clear nickname entry if no preset selected/connected

    def _on_make_it_stick_click(self):
        # Function Description:
        # Callback for the "MAKE IT STICK" button. This function takes the
        # current text from the Nickname entry box and applies it as the
        # NickName for the currently selected preset, saving it to the CSV
        # cache and updating the corresponding button's display.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Retrieves the currently selected preset's filename.
        #   2. Retrieves the new nickname from the `nickname_var` (entry box).
        #   3. If a preset is selected:
        #      a. Retrieves the existing cached data for the preset.
        #      b. Updates the 'NickName' field in the cached data.
        #      c. Saves the updated preset data to the CSV file using `save_user_preset_to_csv`.
        #      d. Updates the in-memory `cached_preset_details`.
        #      e. Calls `update_preset_button_info` to refresh the button's text.
        #   4. If no preset is selected, prints a warning to the console.
        #
        # Outputs of this function:
        #   None. Updates internal state, GUI, and saves data to CSV.
        #
        # (2025-07-30) Change: New function to handle nickname persistence.
        """
        Callback for the "MAKE IT STICK" button. Updates the NickName for the
        currently selected preset and saves it to the CSV.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("MAKE IT STICK button clicked.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        selected_preset_name = self.app_instance.last_selected_preset_name_var.get()
        new_nickname = self.nickname_var.get().strip()
        debug_print(f"In _on_make_it_stick_click: Selected preset name: '{selected_preset_name}', New nickname: '{new_nickname}'", file=current_file, function=current_function, console_print_func=self.console_print_func)


        if not selected_preset_name:
            self.console_print_func("⚠️ Warning: No preset selected to apply Nick Name to. Select a preset first.")
            debug_print("No preset selected for NickName update.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            return

        if not new_nickname:
            self.console_print_func("⚠️ Warning: Nick Name cannot be empty. Using default.")
            new_nickname = selected_preset_name.replace('.STA', '').replace('_', ' ')
            self.nickname_var.set(new_nickname) # Set the default back to the entry box
            debug_print(f"In _on_make_it_stick_click: New nickname was empty, defaulting to '{new_nickname}'", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Retrieve the existing cached data for the selected preset
        cached_data = self.cached_preset_details.get(selected_preset_name, {})
        debug_print(f"In _on_make_it_stick_click: Cached data for '{selected_preset_name}': {cached_data}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        
        # Ensure all required keys exist, even if empty, before updating NickName
        preset_data_to_save = {
            'Filename': selected_preset_name,
            'Center': cached_data.get('Center'),
            'Span': cached_data.get('Span'),
            'RBW': cached_data.get('RBW'),
            'NickName': new_nickname
        }
        debug_print(f"In _on_make_it_stick_click: Data to save: {preset_data_to_save}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Save the updated details to CSV
        save_user_preset_to_csv(preset_data_to_save, self.app_instance.CONFIG_FILE, self.console_print_func)
        self.cached_preset_details[selected_preset_name] = preset_data_to_save # Update cache in memory
        self.console_print_func(f"✅ Nick Name '{new_nickname}' saved for preset '{selected_preset_name}'.")
        debug_print(f"In _on_make_it_stick_click: Nick Name '{new_nickname}' applied and saved for preset '{selected_preset_name}'. Updated cached_preset_details: {self.cached_preset_details.get(selected_preset_name)}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Update the button text with the new nickname
        self.update_preset_button_info(
            selected_preset_name,
            preset_data_to_save.get('Center'),
            preset_data_to_save.get('Span'),
            preset_data_to_save.get('RBW'),
            new_nickname
        )


    def _update_selected_button_style(self, new_selected_preset_key):
        # Function Description:
        # Manages the visual style of preset buttons, ensuring only one button
        # has the "selected" style at any given time.
        #
        # Inputs to this function:
        #   new_selected_preset_key (str or None): The filename of the preset
        #                                          to highlight as selected.
        #                                          If None, all buttons are deselected.
        #
        # Outputs of this function:
        #   None. Modifies the visual style of Tkinter buttons.
        #
        # (2025-07-30) Change: Simplified as only one type of preset now. Selected button color changed to orange.
        """
        Manages the visual style of preset buttons, ensuring only one button
        has the "selected" style at any given time.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"Updating selected button style to: {new_selected_preset_key}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # If there was a previously selected button, revert its style
        if self.current_selected_button_widget:
            self.current_selected_button_widget.config(style='LargePreset.TButton')
            debug_print(f"Reverted style for previous button: {self.current_selected_button_widget.cget('text').splitlines()[0]}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self.current_selected_button_widget = None

        # If a new preset is being selected, apply the selected style
        if new_selected_preset_key and new_selected_preset_key in self.preset_buttons:
            self.current_selected_button_widget = self.preset_buttons[new_selected_preset_key]
            # Change the style to 'SelectedPreset.Orange.TButton'
            self.current_selected_button_widget.config(style='SelectedPreset.Orange.TButton')
            debug_print(f"Applied 'SelectedPreset.Orange' style to button: {new_selected_preset_key}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        elif new_selected_preset_key is None:
            debug_print("Deselecting all preset buttons.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            debug_print(f"Could not find button for preset '{new_selected_preset_key}' to apply style. Fucking hell!", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def update_preset_button_info(self, preset_key, center_freq_mhz, span_mhz, rbw_hz, nickname=None):
        # Function Description:
        # Updates the label of a specific preset button with frequency, span, RBW, and NickName info.
        # This function formats the provided numerical data into a readable string
        # and updates the text displayed on the corresponding button.
        #
        # Inputs to this function:
        #   preset_key (str): The filename of the preset.
        #   center_freq_mhz (float): Center frequency in MHz.
        #   span_mhz (float): Span in MHz.
        #   rbw_hz (float): RBW in Hz.
        #   nickname (str, optional): The nickname for the preset. If None, it defaults to the filename.
        #
        # Outputs of this function:
        #   None. Modifies the text of a Tkinter button.
        #
        # (2025-07-30) Change: Added `nickname` parameter and updated button text formatting.
        """
        Updates the label of a specific preset button with frequency, span, and RBW info.
        Inputs:
            preset_key (str): The filename of the preset.
            center_freq_mhz (float): Center frequency in MHz.
            span_mhz (float): Span in MHz.
            rbw_hz (float): RBW in Hz.
            nickname (str, optional): The nickname for the preset. If None, it defaults to the filename.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"Updating button '{preset_key}' with C:{center_freq_mhz:.3f}MHz SP:{span_mhz:.3f}MHz RBW:{rbw_hz}Hz, Nickname: {nickname}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        if preset_key in self.preset_buttons:
            button = self.preset_buttons[preset_key]
            
            display_name = nickname if nickname else preset_key.replace('.STA', '').replace('_', ' ')

            # Format frequency, span, and RBW.
            # Ensure rbw_hz is treated as a number for division
            formatted_freq = f"C: {center_freq_mhz:.3f} MHz" if center_freq_mhz is not None else "C: N/A"
            formatted_span = f"SP: {span_mhz:.3f} MHz" if span_mhz is not None else "SP: N/A"
            formatted_rbw = f"RBW: {rbw_hz / 1000:.1f} kHz" if rbw_hz is not None else "RBW: N/A"

            # Combine original text (now NickName) with new info, using newlines
            new_text = f"{display_name}\n({preset_key})\n{formatted_freq}\n{formatted_span}\n{formatted_rbw}"
            
            button.config(text=new_text)
            debug_print(f"Button '{preset_key}' text updated to:\n{new_text}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            debug_print(f"Button for preset '{preset_key}' not found for update. What the fuck!", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def get_selected_preset(self):
        # Function Description:
        # Returns the name of the currently selected preset, as stored in the
        # `app_instance`'s persistent variable.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Outputs of this function:
        #   str or None: The name of the selected preset, or an empty string if none is selected.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """
        Returns the name of the currently selected preset.
        """
        return self.app_instance.last_selected_preset_name_var.get()

    def clear_preset_buttons_visual_only(self):
        # Function Description:
        # Clears all dynamically created preset buttons from the display
        # and resets the internal state variables related to button management.
        # It also adds placeholder labels if no presets are found.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Destroys all child widgets within the "MON" and "Other" inner button frames.
        #   3. Clears the `self.preset_buttons` dictionary.
        #   4. Resets `self.current_selected_button_widget` to None.
        #   5. Updates the scroll regions of the canvases.
        #   6. Adds "No presets found" labels to both canvases.
        #
        # Outputs of this function:
        #   None. Clears the GUI display and resets internal state.
        #
        # (2025-07-30) Change: Simplified to clear only two button frames.
        """
        Clears all dynamically created preset buttons from the display
        and resets the internal state variables related to button management.
        This function is for visual clearing only and does NOT affect the
        persistent state stored in app_instance.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Clearing all preset buttons (visual only)...", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        for widget in self.inner_mon_buttons_frame.winfo_children():
            widget.destroy()
        for widget in self.inner_other_buttons_frame.winfo_children():
            widget.destroy()

        self.preset_buttons.clear() # Clear the stored button references
        self.current_selected_button_widget = None # Clear the currently selected button widget

        self.inner_mon_buttons_frame.update_idletasks()
        self.mon_preset_canvas.config(scrollregion=self.inner_mon_buttons_frame.bbox("all"))
        self.inner_other_buttons_frame.update_idletasks()
        self.other_preset_canvas.config(scrollregion=self.inner_other_buttons_frame.bbox("all"))

        # CRITICAL FIX: DO NOT CLEAR THE PERSISTENT VARIABLE HERE!
        # self.app_instance.last_selected_preset_name_var.set("") # REMOVED THIS LINE

        self.instrument_preset_files = [] # Clear the stored list of instrument presets
        # self.source_of_displayed_presets = "unknown" # No longer needed
        
        # Add placeholder labels if no presets are displayed
        ttk.Label(self.inner_mon_buttons_frame, text="No MON presets found.",
                      background="#333333", foreground="white").grid(row=0, column=0, columnspan=3, padx=10, pady=10) # Adjusted columnspan
        ttk.Label(self.inner_other_buttons_frame, text="No other presets found.",
                      background="#333333", foreground="white").grid(row=0, column=0, columnspan=3, padx=10, pady=10) # Adjusted columnspan


    def populate_instrument_preset_buttons(self, presets_to_display):
        # Function Description:
        # Populates the MON and Other preset sections with buttons based on the provided list of presets.
        # It clears existing buttons, categorizes presets, creates new buttons for each,
        # and updates their display information from cache or with default "N/A" values.
        #
        # Inputs to this function:
        #   presets_to_display (list): A list of preset filenames (strings) to be displayed as buttons.
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Calls `clear_preset_buttons_visual_only` to remove all existing buttons and placeholders.
        #   3. Categorizes `presets_to_display` into `mon_presets` and `other_presets`.
        #   4. If `mon_presets` is not empty, removes the "No MON presets found" label.
        #   5. Loops through `mon_presets`:
        #      a. Retrieves cached data for the preset (or uses defaults if not found).
        #      b. Constructs the initial button text with nickname and N/A for details if not in cache.
        #      c. Creates and grids a `ttk.Button` in `inner_mon_buttons_frame`.
        #      d. Stores a reference to the button in `self.preset_buttons`.
        #   6. Repeats steps 4 and 5 for `other_presets` in `inner_other_buttons_frame`.
        #   7. Updates the scroll regions for both canvases.
        #   8. Prints success messages.
        #
        # Outputs of this function:
        #   None. Dynamically creates and updates Tkinter buttons.
        #
        # (2025-07-31) Change: Added explicit removal of "No presets found" labels before adding buttons.
        #                     Ensured buttons are created even if cached data is missing, showing "N/A".
        # (2025-07-31) Change: Adjusted column wrapping logic for 3 columns.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        self.console_print_func(f"Populating instrument preset buttons with {len(presets_to_display)} items...")
        debug_print(f"Populating instrument preset buttons with {len(presets_to_display)} items...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Clear existing buttons and add placeholder labels
        self.clear_preset_buttons_visual_only() 

        # Re-load cached user presets to ensure self.cached_preset_details is fresh
        # This is important because a new PRESETS.CSV might have just been created
        # or updated by another part of the application.
        self.cached_preset_details = {p['Filename']: p for p in load_user_presets_from_csv(self.app_instance.CONFIG_FILE, self.console_print_func)}
        debug_print(f"In populate_instrument_preset_buttons: Loaded {len(self.cached_preset_details)} cached preset details for button population. Current cache: {self.cached_preset_details}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        mon_presets = sorted([p for p in presets_to_display if "MON" in p.upper()])
        other_presets = sorted([p for p in presets_to_display if "MON" not in p.upper()])

        # --- Populate MON presets ---
        # Remove "No MON presets found" label if we have actual presets
        if mon_presets:
            for widget in self.inner_mon_buttons_frame.winfo_children():
                if isinstance(widget, ttk.Label) and "No MON presets found" in widget.cget("text"):
                    widget.destroy()
                    debug_print("Removed 'No MON presets found' label.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            
            mon_row = 0
            mon_col = 0
            for preset_key in mon_presets:
                # Try to get cached data for detailed display. If not found, values will be None.
                cached_data = self.cached_preset_details.get(preset_key, {})
                nickname = cached_data.get('NickName', preset_key.replace('.STA', '').replace('_', ' '))
                center_freq_mhz = cached_data.get('Center')
                span_mhz = cached_data.get('Span')
                rbw_hz = cached_data.get('RBW')

                # Construct the initial button text. update_preset_button_info will format it fully.
                # If data is not in cache, these will be None and update_preset_button_info will show N/A
                formatted_freq = f"C: {center_freq_mhz:.3f} MHz" if center_freq_mhz is not None else "C: N/A"
                formatted_span = f"SP: {span_mhz:.3f} MHz" if span_mhz is not None else "SP: N/A"
                formatted_rbw = f"RBW: {rbw_hz / 1000:.1f} kHz" if rbw_hz is not None else "RBW: N/A"
                
                button_initial_text = f"{nickname}\n({preset_key})\n{formatted_freq}\n{formatted_span}\n{formatted_rbw}"

                button = ttk.Button(self.inner_mon_buttons_frame, 
                                    text=button_initial_text,
                                    command=lambda pk=preset_key: self._on_preset_button_click(pk),
                                    style='LargePreset.TButton')
                button.grid(row=mon_row, column=mon_col, padx=5, pady=5, sticky="ew")
                self.preset_buttons[preset_key] = button # Store reference

                debug_print(f"Created MON button for: {preset_key} at ({mon_row},{mon_col}) with text:\n{button_initial_text}", file=current_file, function=current_function, console_print_func=self.console_print_func)

                mon_col += 1
                if mon_col > 2: # Changed to 3 columns (0, 1, 2)
                    mon_col = 0
                    mon_row += 1
        else:
            debug_print("No MON presets to display. Placeholder label will remain.", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # --- Populate Other presets ---
        # Remove "No other presets found" label if we have actual presets
        if other_presets:
            for widget in self.inner_other_buttons_frame.winfo_children():
                if isinstance(widget, ttk.Label) and "No other presets found" in widget.cget("text"):
                    widget.destroy()
                    debug_print("Removed 'No other presets found' label.", file=current_file, function=current_function, console_print_func=self.console_print_func)

            other_row = 0
            other_col = 0
            for preset_key in other_presets:
                # Try to get cached data for detailed display. If not found, values will be None.
                cached_data = self.cached_preset_details.get(preset_key, {})
                nickname = cached_data.get('NickName', preset_key.replace('.STA', '').replace('_', ' '))
                center_freq_mhz = cached_data.get('Center')
                span_mhz = cached_data.get('Span')
                rbw_hz = cached_data.get('RBW')

                formatted_freq = f"C: {center_freq_mhz:.3f} MHz" if center_freq_mhz is not None else "C: N/A"
                formatted_span = f"SP: {span_mhz:.3f} MHz" if span_mhz is not None else "SP: N/A"
                formatted_rbw = f"RBW: {rbw_hz / 1000:.1f} kHz" if rbw_hz is not None else "RBW: N/A"
                
                button_initial_text = f"{nickname}\n({preset_key})\n{formatted_freq}\n{formatted_span}\n{formatted_rbw}"

                button = ttk.Button(self.inner_other_buttons_frame, 
                                    text=button_initial_text,
                                    command=lambda pk=preset_key: self._on_preset_button_click(pk),
                                    style='LargePreset.TButton')
                button.grid(row=other_row, column=other_col, padx=5, pady=5, sticky="ew")
                self.preset_buttons[preset_key] = button # Store reference

                debug_print(f"Created Other button for: {preset_key} at ({other_row},{other_col}) with text:\n{button_initial_text}", file=current_file, function=current_function, console_print_func=self.console_print_func)

                other_col += 1
                if other_col > 2: # Changed to 3 columns (0, 1, 2)
                    other_col = 0
                    other_row += 1
        else:
            debug_print("No Other presets to display. Placeholder label will remain.", file=current_file, function=current_function, console_print_func=self.console_print_func)


        # Update scroll regions after all buttons are added
        self.inner_mon_buttons_frame.update_idletasks()
        self.mon_preset_canvas.config(scrollregion=self.inner_mon_buttons_frame.bbox("all"))
        
        self.inner_other_buttons_frame.update_idletasks()
        self.other_preset_canvas.config(scrollregion=self.inner_other_buttons_frame.bbox("all"))

        self.console_print_func("Instrument preset buttons populated and scroll regions updated.")
        debug_print("Instrument preset buttons populated and scroll regions updated.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_preset_button_click(self, preset_name):
        # Function Description:
        # Handles the click event for a preset button.
        # This function updates the application's state to reflect the selected preset,
        # visually highlights the clicked button, and initiates the loading of the preset
        # onto the instrument.
        #
        # Inputs to this function:
        #   preset_name (str): The filename of the preset associated with the clicked button.
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Updates `app_instance.last_selected_preset_name_var` with the clicked preset's name.
        #   3. Calls `_update_selected_button_style` to apply the visual "selected" style.
        #   4. Calls `_load_selected_preset` to execute the preset loading logic.
        #
        # Outputs of this function:
        #   None. Updates internal state and triggers other functions.
        #
        # (2025-07-31) Change: New function to handle button clicks.
        """
        Handles the click event for a preset button.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        self.console_print_func(f"Preset button clicked: {preset_name}")
        debug_print(f"Preset button clicked: {preset_name}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Update the app_instance's variable for the last selected preset
        self.app_instance.last_selected_preset_name_var.set(preset_name)

        # Update the visual style of the buttons
        self._update_selected_button_style(preset_name)

        # Load the selected preset onto the instrument
        self._load_selected_preset()


    def on_connection_status_changed(self, is_connected):
        # Function Description:
        # Called by the main application when the instrument connection status changes.
        # This method updates the state of the query presets button and re-populates/restores
        # the preset buttons based on the new connection status, ensuring the UI reflects
        # the available presets and the previously selected one. It now also loads
        # cached preset details from CSV. It clears the nickname entry on disconnection.
        #
        # Inputs to this function:
        #   is_connected (bool): True if the instrument is connected, False otherwise.
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Enables/disables the `query_presets_button` based on `is_connected`.
        #   3. Always loads cached preset details from CSV.
        #   4. If `is_connected` is True:
        #      a. If the instrument is "N9342CN", auto-queries device presets.
        #      b. Otherwise, populates with local device presets.
        #   5. If `is_connected` is False:
        #      a. Clears instrument preset buttons.
        #      b. Populates with local device presets (which will show "No presets found" if none).
        #      c. Clears the nickname entry box.
        #   6. Calls `_restore_selected_preset_style` to re-apply the visual selection
        #      and button info after any population.
        #
        # Outputs of this function:
        #   None. Updates the GUI state of the tab.
        #
        # (2025-07-30) Change: Consolidated preset loading.
        # (2025-07-30) Change: Cleared nickname entry on disconnection.
        # (2025-07-31) Change: Modified logic for connected state to re-display
        #                     previously queried device presets if available,
        #                     or prompt user to query.
        # (2025-07-31) Change: Removed incorrect call to _populate_local_preset_list
        #                     when instrument is connected but not N9342CN.
        # (2025-07-31) Change: Ensured device is queried for presets when connected and N9342CN.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"PresetFilesTab received connection status update: {is_connected}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Always load cached preset details from CSV first
        self.cached_preset_details = {
            p['Filename']: p for p in load_user_presets_from_csv(self.app_instance.CONFIG_FILE, self.console_print_func)
        }
        debug_print(f"In on_connection_status_changed: Loaded {len(self.cached_preset_details)} cached preset details for refresh. Current cache: {self.cached_preset_details}", file=current_file, function=current_function, console_print_func=self.console_print_func)


        if is_connected:
            self.query_presets_button.config(state=tk.NORMAL)
            # When connected, always attempt to query the device for presets.
            # This ensures the display is always up-to-date with the instrument's current state.
            self.console_print_func("Instrument connected. Attempting to query device presets...")
            presets = query_device_presets_logic(self.app_instance, self.console_print_func)
            
            if presets:
                self.instrument_preset_files = presets # Update the stored list
                self.populate_instrument_preset_buttons(presets)
                self.console_print_func(f"Instrument connected. Displaying {len(presets)} device presets.")
            else:
                self.instrument_preset_files = [] # Clear if query failed or no presets found
                self.populate_instrument_preset_buttons([]) # Show "No presets found" labels.
                self.console_print_func("❌ Failed to query device presets or no presets found on device. Displaying no presets.")
        else:
            # If disconnected, clear the device preset list and display local presets (if any).
            self.query_presets_button.config(state=tk.DISABLED)
            self.instrument_preset_files = [] # Clear internal list of device presets
            self.populate_instrument_preset_buttons([]) # Clear current display (shows "No presets found")
            self.console_print_func("Instrument disconnected. Displaying local presets only (if any).")
            self._populate_local_preset_list() # This will populate with local files or show "No presets found"
            self.nickname_var.set("") # Clear nickname entry on disconnection

        self._restore_selected_preset_style()


    def _on_tab_selected(self, event):
        # Function Description:
        # Callback when this tab is selected in the notebook.
        # This function ensures that the preset buttons and their states are
        # refreshed whenever the Instrument Presets tab becomes active.
        # It now leverages `on_connection_status_changed` for centralized logic.
        #
        # Inputs to this function:
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function:
        #   1. Prints a debug message.
        #   2. Checks if the event widget is the main notebook and if this tab
        #      is the currently selected one.
        #   3. If this tab is selected, it calls `on_connection_status_changed`
        #      to refresh the display based on the current instrument connection.
        #
        # Outputs of this function:
        #   None. Updates the GUI state of the tab.
        #
        # (2025-07-30) Change: Reverted to calling `on_connection_status_changed`
        #                     to ensure full tab refresh on selection.
        """
        Callback when this tab is selected. Updates the state of the preset display.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("PresetFilesTab selected.", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        if event.widget != self.master:
            return

        selected_tab_id = self.master.select()
        selected_tab_widget = self.master.nametowidget(selected_tab_id)

        if selected_tab_widget == self:
            debug_print("PresetFilesTab is the selected tab. Updating its state.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            # Reverted to calling on_connection_status_changed to ensure full refresh
            self.on_connection_status_changed(self.app_instance.inst is not None)
        else:
            debug_print(f"Another tab selected: {selected_tab_widget.winfo_class()}. Not updating PresetFilesTab.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _restore_selected_preset_style(self):
        # Function Description:
        # Restores the visual "selected" style and detailed information to the
        # preset button that corresponds to the `last_selected_preset_name_var`
        # stored in the `app_instance`. This ensures that when the tab is
        # re-selected, the UI accurately reflects the last loaded preset.
        # It also populates the nickname entry with the cached nickname.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Retrieves the last selected preset name (key) from `app_instance.last_selected_preset_name_var`.
        #   3. If a preset key is found and a corresponding button exists in `self.preset_buttons`:
        #      a. Calls `_update_selected_button_style` to apply the selected style.
        #      b. Retrieves the cached data for the preset.
        #      c. Calls `update_preset_button_info` to refresh the button's text with these details.
        #      d. Populates the `nickname_var` (entry box) with the cached nickname.
        #   4. If no preset is selected or the button is not found, ensures no button is visually selected
        #      and clears the nickname entry.
        #
        # Outputs of this function:
        #   None. Modifies the visual style and text of a Tkinter button and the nickname entry.
        #
        # (2025-07-30) Change: Populates nickname entry with cached nickname.
        # (2025-07-31) Change: Ensured nickname is passed to update_preset_button_info in fallback scenario.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Attempting to restore selected preset style...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        last_selected_key = self.app_instance.last_selected_preset_name_var.get()
        debug_print(f"In _restore_selected_preset_style: last_selected_key: '{last_selected_key}'", file=current_file, function=current_function, console_print_func=self.console_print_func)

        if last_selected_key and last_selected_key in self.preset_buttons:
            debug_print(f"Found last selected preset '{last_selected_key}'. Restoring style.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self._update_selected_button_style(last_selected_key)
            
            # Also restore the detailed info on the button if available from cache
            if last_selected_key in self.cached_preset_details:
                cached_data = self.cached_preset_details[last_selected_key]
                debug_print(f"In _restore_selected_preset_style: Found cached data for '{last_selected_key}': {cached_data}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                self.update_preset_button_info(
                    last_selected_key,
                    cached_data.get('Center'), # These are already in MHz from CSV
                    cached_data.get('Span'),   # These are already in MHz from CSV
                    cached_data.get('RBW'),    # These are already in Hz from CSV
                    cached_data.get('NickName')
                )
                nickname_to_set = cached_data.get('NickName', '')
                self.nickname_var.set(nickname_to_set) # Populate nickname entry
                debug_print(f"In _restore_selected_preset_style: Set nickname_var to '{nickname_to_set}' for '{last_selected_key}' from cache.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            else:
                # Fallback to app_instance vars if not in cache (shouldn't happen often if saving works)
                try:
                    # These values from app_instance are already in MHz/Hz as set by _on_preset_button_click
                    center_freq_mhz = float(self.app_instance.last_loaded_preset_center_freq_mhz_var.get()) if self.app_instance.last_loaded_preset_center_freq_mhz_var.get() else None
                    span_mhz = float(self.app_instance.last_loaded_preset_span_mhz_var.get()) if self.app_instance.last_loaded_preset_span_mhz_var.get() else None
                    rbw_hz = float(self.app_instance.last_loaded_preset_rbw_hz_var.get()) if self.app_instance.last_loaded_preset_rbw_hz_var.get() else None
                    
                    # Ensure nickname is also passed in this fallback scenario
                    fallback_nickname = last_selected_key.replace('.STA', '').replace('_', ' ')
                    self.update_preset_button_info(last_selected_key, center_freq_mhz, span_mhz, rbw_hz, fallback_nickname)
                    self.nickname_var.set(fallback_nickname) # Default nickname
                    debug_print(f"In _restore_selected_preset_style: Restored button info for '{last_selected_key}' from app_instance vars (cache miss). Set nickname_var to '{fallback_nickname}'.", file=current_file, function=current_function, console_print_func=self.console_print_func)
                except ValueError as e:
                    debug_print(f"�🐛 Warning: Could not convert stored preset frequency/span/RBW for '{last_selected_key}'. Error: {e}. Fucking data corruption!", file=current_file, function=current_function, console_print_func=self.console_print_func)
                    self.update_preset_button_info(last_selected_key, None, None, None) # Update with N/A
                    self.nickname_var.set("") # Clear nickname entry
        else:
            debug_print("No last selected preset found or button not in current list. Ensuring no button is selected and nickname entry is clear.", file=current_file, function=current_function, console_print_func=self.console_print_func)
            self._update_selected_button_style(None)
            self.nickname_var.set("") # Clear nickname entry
            self.app_instance.last_selected_preset_name_var.set("") # Ensure the persistent variable is also cleared

    def _open_local_preset_folder(self):
        # Function Description:
        # Opens the local preset folder (e.g., 'presets' directory in the app's root).
        # Creates the folder if it doesn't exist.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Process of this function:
        #   1. Prints debug messages.
        #   2. Determines the path to the local presets folder.
        #   3. Checks if the folder exists and creates it if necessary, handling errors.
        #   4. Uses `subprocess.Popen` to open the folder using the appropriate command
        #      for the current operating system (Windows, macOS, Linux).
        #   5. Prints success or error messages to the console.
        #
        # Outputs of this function:
        #   None. Interacts with the file system to open a directory.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """
        Opens the local preset folder (e.g., 'presets' directory in the app's root).
        Creates the folder if it doesn't exist.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        
        # Define the path to the local presets folder
        # Assuming it's a 'presets' directory relative to the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level from 'src' to the root, then into 'presets'
        preset_folder = os.path.join(os.path.dirname(script_dir), "presets")

        if not os.path.exists(preset_folder):
            try:
                os.makedirs(preset_folder, exist_ok=True)
                self.console_print_func(f"Created preset folder: {preset_folder}")
                debug_print(f"Created preset folder: {preset_folder}", file=current_file, function=current_function, console_print_func=self.console_print_func)
            except Exception as e:
                self.console_print_func(f"❌ Failed to create preset folder: {e}")
                debug_print(f"Failed to create preset folder: {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)
                return

        try:
            # Open the folder using the appropriate command for the OS
            if sys.platform == "win32":
                subprocess.Popen(['explorer', preset_folder]) # Use explorer for Windows
            elif sys.platform == "darwin": # macOS
                subprocess.Popen(["open", preset_folder])
            else: # Linux
                subprocess.Popen(["xdg-open", preset_folder])
            self.console_print_func(f"Opened preset folder: {preset_folder}")
            debug_print(f"Opened preset folder: {preset_folder}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        except Exception as e:
            self.console_print_func(f"❌ Could not open preset folder: {e}")
            debug_print(f"Error opening preset folder '{preset_folder}': {e}", file=current_file, function=current_function, console_print_func=self.console_print_func)

    def _populate_local_preset_list(self):
        # Function Description:
        # This is a placeholder function. In a full implementation, this would
        # load presets from a local directory (e.g., 'presets' folder in the app's root)
        # and populate the buttons with those. For now, it just clears the buttons
        # and leaves the "No presets found" labels.
        #
        # Inputs to this function:
        #   None (operates on self).
        #
        # Outputs of this function:
        #   None.
        #
        # (2025-07-31) Change: New placeholder function.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Populating local preset list (placeholder - currently does nothing but clear).", file=current_file, function=current_function, console_print_func=self.console_print_func)
        self.clear_preset_buttons_visual_only() # Just clear for now
        self.console_print_func("No local presets loaded (feature not fully implemented).")
