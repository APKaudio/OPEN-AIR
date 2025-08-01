# src/tab_instrument_child_connection.py
#
# This file manages the Instrument Connection tab in the GUI, handling
# VISA resource discovery, instrument connection/disconnection, and
# displaying current instrument settings. It aims to reduce chattiness
# and improve performance by only populating VISA resources on explicit
# user action (e.g., "Refresh Devices" button press).
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
# Version 20250731.5
current_version = "Version 20250731.5" # this variable should always be defined below the header to make the debuggin better

import tkinter as tk
from tkinter import ttk
import inspect

# Import instrument control logic functions
from src.instrument_logic import (
    populate_resources_logic, connect_instrument_logic, disconnect_instrument_logic,
    apply_settings_logic, query_current_instrument_settings_logic
)
from utils.utils_instrument_control import debug_print, set_debug_mode, log_visa_command, query_safe # Import debug control functions and query_safe
from ref.frequency_bands import MHZ_TO_HZ # Import for display conversion
from src.config_manager import save_config # Import save_config

class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame that provides functionality for connecting to, disconnecting from,
    and querying the spectrum analyzer. It also displays available VISA resources
    and current instrument settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the InstrumentTab.

        Inputs:
            master (tk.Widget): The parent widget (the ttk.Notebook).
            app_instance (App): The main application instance, used for accessing
                                shared state like Tkinter variables and console print function.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        # Use the shared variables from app_instance
        self.selected_resource = self.app_instance.selected_resource
        self.resource_names = self.app_instance.resource_names

        # Tkinter variables for displaying current instrument settings
        self.current_center_freq_var = tk.StringVar(self)
        self.current_span_var = tk.StringVar(self)
        self.current_rbw_var = tk.StringVar(self)
        self.current_ref_level_var = tk.StringVar(self)
        self.current_freq_shift_var = tk.StringVar(self)
        self.current_max_hold_var = tk.StringVar(self)
        self.current_high_sensitivity_var = tk.StringVar(self)

        # --- NEW: Tkinter BooleanVars for controlling widget visibility ---
        # (2025-07-31 16:04) Change: Added BooleanVars for dynamic UI element visibility.
        self.visa_resource_visible = tk.BooleanVar(self, value=False)
        self.connect_button_visible = tk.BooleanVar(self, value=False)
        self.disconnect_query_buttons_visible = tk.BooleanVar(self, value=False)
        # --- END NEW ---

        self._create_widgets()

        # Initialize the resource dropdown to a default "N/A" state
        self.selected_resource.set("N/A")
        # Ensure the menu is empty initially or contains only "N/A"
        menu = self.resource_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="N/A", command=tk._setit(self.selected_resource, "N/A"))


    def _toggle_general_debug(self):
        """Toggles the global debug mode based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Toggling general debug. Current state: {self.app_instance.general_debug_enabled_var.get()}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        set_debug_mode(self.app_instance.general_debug_enabled_var.get())
        self.console_print_func(f"Debug Mode: {'Enabled' if self.app_instance.general_debug_enabled_var.get() else 'Disabled'}")

    def _toggle_visa_logging(self):
        """Toggles the global VISA command logging based on checkbox state."""
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Toggling VISA logging. Current state: {self.app_instance.log_visa_commands_enabled_var.get()}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        log_visa_command(self.app_instance.log_visa_commands_enabled_var.get())
        self.console_print_func(f"VISA Command Logging: {'Enabled' if self.app_instance.log_visa_commands_enabled_var.get() else 'Disabled'}")

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges the widgets for the Instrument Connection tab.
        This function has been heavily modified to implement dynamic visibility
        of UI elements based on connection state and user interaction.

        Inputs to this function:
        - None (uses self and its Tkinter variables)

        Process of this function:
        1. Configures grid columns for the main frame.
        2. Creates the "Instrument Connection" label frame.
        3. Places the "STEP 1 - Find Instruments" button at the top, full width.
        4. Creates and initially hides the "STEP 2 - Choose Visa Resource from list" label and dropdown.
        5. Creates and initially hides the "STEP 3 - CONNECT" button.
        6. Creates the "Current Instrument Values" label frame.
        7. Places the "STEP 4 - Test connection" button at the top of the "Current Instrument Values" frame.
        8. Creates and places read-only entry fields for instrument values.
        9. Creates the "Debug Options" frame with checkboxes.
        10. Creates the "Disconnect" button below the "Current Instrument Values" box, full width.
        11. Binds visibility variables to the grid layout for dynamic showing/hiding.

        Outputs of this function:
        - Populates the InstrumentTab with all its GUI elements.

        (2025-07-31 16:04) Change: Refactored widget creation for dynamic visibility and reordered elements.
        (2025-07-31 16:06) Change: Removed "Apply Settings" button.
        (2025-07-31 16:08) Change: Renamed "Query Instrument" to "STEP 4 - Test connection".
        (2025-07-31 16:10) Change: Moved "Disconnect" button below "Current Instrument Values" and made it full width.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Creating InstrumentTab widgets...",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1) # For buttons

        # Frame for resource selection and connection buttons
        connection_frame = ttk.LabelFrame(self, text="Instrument Connection", padding="10 10 10 10", style='Dark.TLabelframe')
        connection_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        connection_frame.grid_columnconfigure(0, weight=1)
        connection_frame.grid_columnconfigure(1, weight=2) # Resource dropdown
        # No need for column 2 weight here as the refresh button will span all columns

        # --- NEW: STEP 1 - Find Instruments Button (full width) ---
        self.refresh_devices_button = ttk.Button(connection_frame, text="STEP 1 - Find Instruments", command=self._populate_resources_and_show_visa)
        self.refresh_devices_button.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        # --- END NEW ---

        # --- NEW: VISA Resource Label and Dropdown (initially hidden) ---
        self.visa_resource_label = ttk.Label(connection_frame, text="STEP 2 - Choose Visa Resource from list:", style='TLabel')
        # We will grid this conditionally based on self.visa_resource_visible
        self.resource_dropdown = ttk.OptionMenu(connection_frame, self.selected_resource, "N/A", # Set initial value to "N/A"
                                                command=self._on_resource_selected)
        self.resource_dropdown.config(width=40)
        # We will grid this conditionally based on self.visa_resource_visible
        # --- END NEW ---

        # --- NEW: Connect Button (initially hidden) ---
        self.connect_button = ttk.Button(connection_frame, text="STEP 3 - CONNECT", command=self._connect_instrument)
        # We will grid this conditionally based on self.connect_button_visible
        # --- END NEW ---

        # Frame for Current Instrument Values Display
        current_values_frame = ttk.LabelFrame(self, text="Current Instrument Values", padding="10 10 10 10", style='Dark.TLabelframe')
        current_values_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        current_values_frame.grid_columnconfigure(0, weight=1)
        current_values_frame.grid_columnconfigure(1, weight=1)

        # --- NEW: Query Instrument Button (moved to top of current_values_frame) ---
        self.query_settings_button = ttk.Button(current_values_frame, text="STEP 4 - Test connection", command=self._query_settings)
        self.query_settings_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        # This will also be managed by self.disconnect_query_buttons_visible
        # --- END NEW ---

        ttk.Label(current_values_frame, text="Center Freq (MHz):", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_center_freq_var, state='readonly', style='TEntry').grid(row=1, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="Span (MHz):", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_span_var, state='readonly', style='TEntry').grid(row=2, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="RBW (Hz):", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_rbw_var, state='readonly', style='TEntry').grid(row=3, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="Reference Level (dBm):", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_ref_level_var, state='readonly', style='TEntry').grid(row=4, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="Frequency Shift (Hz):", style='TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_freq_shift_var, state='readonly', style='TEntry').grid(row=5, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="Max Hold:", style='TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_max_hold_var, state='readonly', style='TEntry').grid(row=6, column=1, padx=2, pady=2, sticky="ew")

        ttk.Label(current_values_frame, text="High Sensitivity:", style='TLabel').grid(row=7, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(current_values_frame, textvariable=self.current_high_sensitivity_var, state='readonly', style='TEntry').grid(row=7, column=1, padx=2, pady=2, sticky="ew")

        # Debug Options Frame
        debug_frame = ttk.LabelFrame(self, text="Debug Options", padding="10 10 10 10", style='Dark.TLabelframe')
        debug_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        debug_frame.grid_columnconfigure(0, weight=1)
        debug_frame.grid_columnconfigure(1, weight=1)

        self.general_debug_checkbox = ttk.Checkbutton(debug_frame, text="Enable General Debug",
                                                      variable=self.app_instance.general_debug_enabled_var,
                                                      command=self._toggle_general_debug, style='TCheckbutton')
        self.general_debug_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.log_visa_commands_checkbox = ttk.Checkbutton(debug_frame, text="Log VISA Commands",
                                                          variable=self.app_instance.log_visa_commands_enabled_var,
                                                          command=self._toggle_visa_logging, style='TCheckbutton')
        self.log_visa_commands_checkbox.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # --- NEW: Disconnect button (moved below current_values_frame) ---
        # (2025-07-31 16:10) Change: Moved Disconnect button creation to main frame, after debug_frame.
        self.disconnect_button = ttk.Button(self, text="Disconnect", command=self._disconnect_instrument)
        # This will be managed by self.disconnect_query_buttons_visible
        # --- END NEW ---

        # --- NEW: Bind visibility variables to grid management ---
        # (2025-07-31 16:04) Change: Added trace methods to BooleanVars for dynamic grid management.
        self.visa_resource_visible.trace_add("write", lambda *args: self._update_visa_resource_visibility(connection_frame))
        self.connect_button_visible.trace_add("write", lambda *args: self._update_connect_button_visibility(connection_frame))
        self.disconnect_query_buttons_visible.trace_add("write", lambda *args: self._update_disconnect_query_buttons_visibility(connection_frame, current_values_frame))
        # --- END NEW ---

        # Initial state update
        self._update_ui_elements_visibility(connected=False, resource_found=False)

        debug_print("InstrumentTab widgets created.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

    # --- NEW: Helper functions for dynamic visibility ---
    # (2025-07-31 16:04) Change: Added helper functions to manage widget grid/grid_forget.
    def _update_visa_resource_visibility(self, parent_frame):
        """Manages the visibility of the VISA resource label and dropdown."""
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Updating VISA resource visibility. State: {self.visa_resource_visible.get()}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        if self.visa_resource_visible.get():
            self.visa_resource_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
            self.resource_dropdown.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        else:
            self.visa_resource_label.grid_forget()
            self.resource_dropdown.grid_forget()

    def _update_connect_button_visibility(self, parent_frame):
        """Manages the visibility of the Connect button."""
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Updating Connect button visibility. State: {self.connect_button_visible.get()}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        if self.connect_button_visible.get():
            self.connect_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        else:
            self.connect_button.grid_forget()

    def _update_disconnect_query_buttons_visibility(self, connection_frame, current_values_frame):
        """
        Function Description:
        Manages the visibility of Disconnect and Query Instrument buttons.
        The "Apply Settings" button has been removed.

        Inputs to this function:
        - connection_frame (ttk.LabelFrame): The frame containing connection-related buttons.
        - current_values_frame (ttk.LabelFrame): The frame containing current instrument values and the Query button.

        Process of this function:
        1. If `disconnect_query_buttons_visible` is True, it grids the Disconnect and Query Instrument buttons.
        2. If `disconnect_query_buttons_visible` is False, it hides them.

        Outputs of this function:
        - Updates the visibility of the Disconnect and Query Instrument buttons.

        (2025-07-31 16:06) Change: Removed "Apply Settings" button from visibility management.
        (2025-07-31 16:10) Change: Updated Disconnect button grid position to be full width below debug options.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Updating Disconnect/Query buttons visibility. State: {self.disconnect_query_buttons_visible.get()}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        if self.disconnect_query_buttons_visible.get():
            # Disconnect button is now in the main 'self' frame, below debug_frame
            self.disconnect_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
            self.query_settings_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew") # Re-grid in current_values_frame
        else:
            self.disconnect_button.grid_forget()
            self.query_settings_button.grid_forget()

    def _update_ui_elements_visibility(self, connected, resource_found):
        """
        Function Description:
        Centralized function to manage the visibility of various UI elements
        based on connection status and whether resources have been found.

        Inputs to this function:
        - connected (bool): True if an instrument is currently connected, False otherwise.
        - resource_found (bool): True if VISA resources have been discovered, False otherwise.

        Process of this function:
        1. Sets the `visa_resource_visible` BooleanVar based on `resource_found`.
        2. Sets the `connect_button_visible` BooleanVar based on `resource_found` AND NOT `connected`.
        3. Sets the `disconnect_query_buttons_visible` BooleanVar based on `connected`.
        4. Disables/enables the "STEP 1 - Find Instruments" button based on connection status.

        Outputs of this function:
        - Updates the visibility and state of various GUI elements.

        (2025-07-31 16:04) Change: Implemented central UI state management.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Updating UI elements visibility. Connected: {connected}, Resources Found: {resource_found}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        self.visa_resource_visible.set(resource_found)
        self.connect_button_visible.set(resource_found and not connected)
        self.disconnect_query_buttons_visible.set(connected)

        # Disable "STEP 1 - Find Instruments" button if connected
        if connected:
            self.refresh_devices_button.config(state=tk.DISABLED)
        else:
            self.refresh_devices_button.config(state=tk.NORMAL)
    # --- END NEW ---

    def _populate_resources_and_show_visa(self):
        """
        Function Description:
        This function is called when "STEP 1 - Find Instruments" is clicked.
        It populates VISA resources and then makes the VISA resource dropdown visible.

        Inputs to this function:
        - None

        Process of this function:
        1. Calls the core resource population logic.
        2. Updates the UI visibility to show the VISA resource selection.

        Outputs of this function:
        - Updates the GUI to show the VISA resource selection.

        (2025-07-31 16:04) Change: New wrapper function to handle button click and subsequent UI reveal.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print("STEP 1 button clicked. Populating resources and showing VISA selection.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        self._populate_resources()
        # After populating, ensure the resource dropdown and label are visible
        self._update_ui_elements_visibility(connected=self.app_instance.inst is not None, resource_found=True)


    def _populate_resources(self):
        # Function Description
        # This function calls the logic to discover VISA resources and updates
        # the resource dropdown menu in the GUI. It attempts to set the
        # selected resource to the last used one from the configuration,
        # or defaults to the first available if the last used is not found.
        #
        # Inputs to this function
        #   None (uses self.app_instance and its variables)
        #
        # Process of this function
        #   1. Calls populate_resources_logic to get available VISA resources.
        #   2. Clears the existing dropdown menu.
        #   3. Adds discovered resources to the dropdown.
        #   4. Retrieves the last selected resource from config.
        #   5. Sets the dropdown to the last selected resource if it's available,
        #      otherwise sets it to the first available if resources are found, or "N/A".
        #   6. Saves the currently selected resource to config.
        #
        # Outputs of this function
        #   Updates the GUI's resource_dropdown and self.selected_resource Tkinter variable.
        #
        # (2025-07-31 16:04) Change: Ensured dropdown is cleared and populated dynamically.
        #                     Added logic for last_selected_resource from config. Updated debug.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Populating VISA resources...",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        populate_resources_logic(self.app_instance, self.console_print_func)

        # Update dropdown menu after populating resources
        menu = self.resource_dropdown["menu"]
        menu.delete(0, "end")
        resources = self.resource_names.get().split()

        # Get last selected resource from config
        last_selected_resource = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_selected_visa_resource', fallback='N/A')
        debug_print(f"Last selected VISA resource from config: {last_selected_resource}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        # Add resources to dropdown
        if resources:
            for resource in resources:
                menu.add_command(label=resource, command=tk._setit(self.selected_resource, resource))

            # Set the selected resource to the last used one if it's in the current list
            if last_selected_resource in resources:
                self.selected_resource.set(last_selected_resource)
                debug_print(f"Set selected resource to last used: {last_selected_resource}",
                            file=f"src/tab_instrument_child_connection.py - {current_version}",
                            function=current_function, console_print_func=self.console_print_func)
            elif resources: # If last_selected_resource is not found, set to the first available
                self.selected_resource.set(resources[0])
                debug_print(f"Last used resource not found, set to first available: {resources[0]}",
                            file=f"src/tab_instrument_child_connection.py - {current_version}",
                            function=current_function, console_print_func=self.console_print_func)
            # --- NEW: Automatically show connect button if resources are found and not connected ---
            self._update_ui_elements_visibility(connected=self.app_instance.inst is not None, resource_found=True)
            # --- END NEW ---
        else:
            self.selected_resource.set("N/A") # Set to "N/A" if no resources found
            menu.add_command(label="N/A", command=tk._setit(self.selected_resource, "N/A")) # Ensure "N/A" is an option
            debug_print("No VISA resources found, setting selected resource to 'N/A'. This is a pain in the ass!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            # --- NEW: Hide connect button if no resources found ---
            self._update_ui_elements_visibility(connected=False, resource_found=False)
            # --- END NEW ---

        # Save the currently selected resource (either loaded or default) to config
        save_config(self.app_instance)


    def _on_resource_selected(self, selected_value):
        """
        Function Description:
        Callback when a new VISA resource is selected from the dropdown.
        Saves the selected resource to config.ini and updates UI visibility
        to show the "STEP 3 - CONNECT" button.

        Inputs to this function:
        - selected_value (str): The value of the selected VISA resource.

        Process of this function:
        1. Logs the selected resource.
        2. Saves the selected resource to the application configuration.
        3. Updates the UI to show the connect button if a valid resource is selected.

        Outputs of this function:
        - Saves configuration, updates GUI elements.

        (2025-07-31 16:04) Change: Added UI visibility update for connect button.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print(f"Selected resource changed to: {selected_value}. Saving to config.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        self.app_instance.config['LAST_USED_SETTINGS']['last_selected_visa_resource'] = selected_value
        save_config(self.app_instance)

        # --- NEW: Show connect button when a resource is selected (if not already connected) ---
        if selected_value != "N/A" and not self.app_instance.inst:
            self.connect_button_visible.set(True)
        else:
            self.connect_button_visible.set(False) # Hide if N/A or already connected
        # --- END NEW ---


    def _connect_instrument(self):
        # Function Description
        # Attempts to connect to the instrument using the selected VISA resource.
        # Upon successful connection, it updates the GUI's connection status, revealing
        # the disconnect and query buttons. It does NOT automatically query settings.
        #
        # Inputs to this function
        #   None (uses self.app_instance and its instrument object)
        #
        # Process of this function
        #   1. Calls connect_instrument_logic.
        #   2. Calls app_instance.update_connection_status to update all relevant GUI elements.
        #   3. Updates UI visibility for disconnect and query buttons.
        #
        # Outputs of this function
        #   Modifies app_instance.inst, updates GUI display elements.
        #
        # (2025-07-31 16:04) Change: Added `debug_print` and ensured `update_connection_status` is called.
        #                     Also updated UI visibility for disconnect/query buttons.
        # (2025-07-31 16:08) Change: Removed automatic call to _query_settings_display after connection.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Attempting to connect instrument...",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        if connect_instrument_logic(self.app_instance, self.console_print_func):
            debug_print("Instrument connected successfully. No automatic query, you gotta push the button for that, you lazy bastard.",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            # Removed: self._query_settings_display() # No longer automatically query after connection
            # --- NEW: Show disconnect and query buttons, hide connect button ---
            self._update_ui_elements_visibility(connected=True, resource_found=True)
            # --- END NEW ---
        else:
            debug_print("Instrument connection failed. This is a goddamn nightmare!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            # --- NEW: Ensure connect button remains if connection failed but resources are still there ---
            self._update_ui_elements_visibility(connected=False, resource_found=True)
            # --- END NEW ---

        # Trigger full GUI update via main app, regardless of success/failure
        # This is where the main app needs to properly update all relevant tabs
        self.app_instance.update_connection_status(self.app_instance.inst is not None)
        debug_print(f"Connection status update triggered for GUI. Connected state: {self.app_instance.inst is not None}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)


    def _disconnect_instrument(self):
        # Function Description
        # Disconnects from the currently connected instrument.
        # Updates the GUI to hide disconnect/query buttons and show the resource selection.
        #
        # Inputs to this function
        #   None (uses self.app_instance and its instrument object)
        #
        # Process of this function
        #   1. Calls disconnect_instrument_logic.
        #   2. Clears the displayed instrument settings.
        #   3. Calls app_instance.update_connection_status to update all relevant GUI elements.
        #   4. Updates UI visibility to hide disconnect/query buttons and show resource selection.
        #
        # Outputs of this function
        #   Modifies app_instance.inst, updates GUI display elements.
        #
        # (2025-07-31 16:04) Change: Added `debug_print` and ensured `update_connection_status` is called.
        #                     Also updated UI visibility for disconnect/query buttons.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Attempting to disconnect instrument...",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        disconnect_instrument_logic(self.app_instance, self.console_print_func)
        self._clear_settings_display() # Clear display after disconnect
        # Trigger full GUI update via main app
        self.app_instance.update_connection_status(self.app_instance.inst is not None)
        debug_print(f"Disconnection complete. Connection status update triggered for GUI. Connected state: {self.app_instance.inst is not None}",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        # --- NEW: Hide disconnect and query buttons, show visa resource and connect button ---
        self._update_ui_elements_visibility(connected=False, resource_found=True) # Assume resources are still there
        # --- END NEW ---


    def _apply_settings(self):
        """
        Function Description:
        This function previously applied settings to the instrument.
        It is now deprecated as the "Apply Settings" button has been removed.

        Inputs to this function:
        - None (uses self.app_instance and its instrument object)

        Process of this function:
        - This function is no longer called directly from the GUI.
        - The logic for applying settings might be integrated elsewhere or removed entirely.

        Outputs of this function:
        - None (function is effectively a placeholder now).

        (2025-07-31 16:06) Change: Deprecated this function as the "Apply Settings" button has been removed.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Attempting to apply settings to instrument... (This function is deprecated and should not be called directly!)",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        # The logic below is kept for now, but this function is no longer linked to a GUI button.
        # If apply_settings_logic is still needed, it should be called from another part of the code.
        if apply_settings_logic(self.app_instance, self.console_print_func):
            debug_print("Settings applied successfully. Querying display.",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            self._query_settings_display() # Update display after applying settings
        else:
            debug_print("Failed to apply settings. What the hell went wrong now?!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)

    def _query_settings(self):
        # Function Description
        # Triggers a query of the current instrument settings and updates the display.
        # This is a wrapper to call _query_settings_display.
        #
        # Inputs to this function
        #   None
        #
        # Process of this function
        #   1. Calls _query_settings_display.
        #
        # Outputs of this function
        #   Updates GUI display elements.
        #
        # (2025-07-31 16:04) Change: Added `debug_print`.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("User requested to query instrument settings for display. Let's see what this thing is doing.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        self._query_settings_display()

    def _query_settings_display(self):
        """
        Function Description:
        Queries the current settings from the instrument and updates the display variables.
        Handles cases where no instrument is connected.

        Inputs to this function:
        - None (uses self.app_instance.inst and Tkinter StringVars)

        Process of this function:
        1. Checks if an instrument is connected. If not, logs a warning and clears display.
        2. Attempts to query various instrument settings (Center Freq, Span, RBW, Ref Level, Freq Shift, Max Hold, High Sensitivity).
        3. Updates the corresponding Tkinter StringVars with the queried values.
        4. Handles potential errors during query and clears display on failure.

        Outputs of this function:
        - Updates the read-only entry fields in the GUI with current instrument settings.
        - Returns True on success, False on failure.

        (2025-07-31 16:04) Change: Added `debug_print` and enhanced error handling messages.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Querying current instrument settings for display...",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        if not self.app_instance.inst:
            self.console_print_func("⚠️ Warning: No instrument connected. Cannot query settings for display.")
            debug_print("No instrument connected. Cannot query settings for display. Fucking useless!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            self._clear_settings_display()
            return False

        try:
            # Query Center Frequency
            center_freq_str = query_safe(self.app_instance.inst, ":SENSe:FREQuency:CENTer?", self.console_print_func)
            self.current_center_freq_var.set(f"{float(center_freq_str) / MHZ_TO_HZ:.3f}" if center_freq_str else "N/A")

            # Query Span
            span_str = query_safe(self.app_instance.inst, ":SENSe:FREQuency:SPAN?", self.console_print_func)
            self.current_span_var.set(f"{float(span_str) / MHZ_TO_HZ:.3f}" if span_str else "N/A")

            # Query RBW
            rbw_str = query_safe(self.app_instance.inst, ":SENSe:BANDwidth:RESolution?", self.console_print_func)
            self.current_rbw_var.set(f"{float(rbw_str):.0f}" if rbw_str else "N/A")

            # Query Reference Level
            ref_level_str = query_safe(self.app_instance.inst, ":DISPlay:WINDow:TRACe:Y:RLEVel?", self.console_print_func)
            self.current_ref_level_var.set(f"{float(ref_level_str):.1f}" if ref_level_str else "N/A")

            # Query Frequency Shift
            freq_shift_str = query_safe(self.app_instance.inst, ":FREQuency:OFFSet?", self.console_print_func)
            self.current_freq_shift_var.set(f"{float(freq_shift_str):.0f}" if freq_shift_str else "N/A")

            # Query Max Hold status
            max_hold_mode_str = query_safe(self.app_instance.inst, ":TRACe2:MODE?", self.console_print_func)
            self.current_max_hold_var.set("ON" if max_hold_mode_str and "MAXH" in max_hold_mode_str.upper() else "OFF")

            # Query High Sensitivity (Preamplifier Gain)
            high_sensitivity_str = query_safe(self.app_instance.inst, ":POWer:GAIN?", self.console_print_func)
            self.current_high_sensitivity_var.set("ON" if high_sensitivity_str and float(high_sensitivity_str) > 0 else "OFF")


            self.console_print_func("✅ Current instrument settings displayed.")
            debug_print("Current instrument settings displayed. Fucking finally!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            return True
        except Exception as e:
            self.console_print_func(f"❌ Error querying instrument settings for display: {e}")
            debug_print(f"Error querying instrument settings for display: {e}. This bugger is being problematic! What the hell is its problem?!",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            self._clear_settings_display()
            return False

    def _clear_settings_display(self):
        # Function Description
        # Clears all the displayed instrument settings in the GUI.
        #
        # Inputs to this function
        #   None (uses Tkinter StringVars)
        #
        # Process of this function
        #   1. Sets all current_*_var Tkinter variables to an empty string.
        #
        # Outputs of this function
        #   Clears text fields in the GUI.
        #
        # (2025-07-31 16:04) Change: Added `debug_print`.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Clearing instrument settings display. Wiping the slate clean, just like my ex did to my bank account.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)
        self.current_center_freq_var.set("")
        self.current_span_var.set("")
        self.current_rbw_var.set("")
        self.current_ref_level_var.set("")
        self.current_freq_shift_var.set("")
        self.current_max_hold_var.set("")
        self.current_high_sensitivity_var.set("")

    def _on_tab_selected(self, event):
        # Function Description
        # Callback for when this tab is selected. It ensures the UI reflects
        # the current connection status and refreshes displayed settings if connected.
        # It no longer automatically queries instrument settings upon selection.
        #
        # Inputs to this function
        #   event: The Tkinter event object (not directly used but part of callback signature).
        #
        # Process of this function:
        #   1. Logs that the Instrument Tab has been selected.
        #   2. Calls app_instance.update_connection_status to update button states across tabs.
        #   3. If an instrument is connected, it clears the settings display; otherwise, it clears the display.
        #      (The automatic query has been removed).
        #   4. Sets the initial state of debug checkboxes based on global variables.
        #   5. Updates the visibility of UI elements based on current connection status.
        #
        # Outputs of this function:
        #   Updates GUI element states and displayed values.
        #
        # (2025-07-31 16:04) Change: Removed _populate_resources() from here. Added robust debug messaging.
        #                     Integrated _update_ui_elements_visibility for initial tab load.
        # (2025-07-31 16:08) Change: Removed automatic call to _query_settings_display.
        current_function = inspect.currentframe().f_code.co_name
        debug_print("Instrument Tab selected. Initializing display state. Let's make sure this thing isn't broken.",
                    file=f"src/tab_instrument_child_connection.py - {current_version}",
                    function=current_function, console_print_func=self.console_print_func)

        # Ensure buttons are in the correct state when tab is selected
        is_connected = self.app_instance.inst is not None
        self.app_instance.update_connection_status(is_connected)

        # Query and display current settings if connected
        if is_connected:
            debug_print("Instrument is connected. Clearing settings display on tab selection (no automatic query, you gotta push the button for that, you lazy bastard).",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            self._clear_settings_display() # Just clear, don't query automatically
        else:
            debug_print("Instrument is NOT connected. Clearing settings display on tab selection.",
                        file=f"src/tab_instrument_child_connection.py - {current_version}",
                        function=current_function, console_print_func=self.console_print_func)
            self._clear_settings_display()

        # Set initial state of debug checkboxes based on app_instance variables
        # Ensure these are configured correctly even if tab wasn't previously active
        self.general_debug_checkbox.config(variable=self.app_instance.general_debug_enabled_var)
        self.log_visa_commands_checkbox.config(variable=self.app_instance.log_visa_commands_enabled_var)

        # --- NEW: Update UI visibility based on connection status when tab is selected ---
        # We assume that if the tab is selected, we should at least show the "Find Instruments" button.
        # If already connected, the state will reflect that.
        self._update_ui_elements_visibility(connected=is_connected, resource_found=self.resource_names.get() != "")
        # --- END NEW ---
