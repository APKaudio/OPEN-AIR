# tabs/Instrument/tab_instrument_child_connection.py
#
# This file manages the Instrument Connection tab in the GUI, handling
# VISA resource discovery, instrument connection/disconnection, and
# displaying current instrument settings. It aims to reduce chattiness
# and improve performance by only populating VISA resources on explicit
# user action (e.g., "Refresh Devices" button press). It also dynamically
# manages the visibility of UI elements based on connection state.
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
# Version 20250802.1555.1 (Fixed resource list not populating and streamlined UI updates.)

current_version = "20250802.1555.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 75 * 13 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os
import threading

# Import instrument control logic functions
from tabs.Instrument.instrument_logic import (
    populate_resources_logic, connect_instrument_logic, disconnect_instrument_logic,
    apply_instrument_settings_logic, query_current_instrument_settings_logic
)
from src.connection_status_logic import update_connection_status_logic
from src.settings_and_config.config_manager import save_config # Import save_config

# Import new debug_logic and console_logic modules
from src.debug_logic import debug_log
from src.console_logic import console_log

# Define current_file for consistent logging
current_file = os.path.basename(__file__)


class InstrumentTab(ttk.Frame):
    """
    Function Description:
    Manages the Instrument Connection tab in the GUI. This includes:
    - Discovering and displaying available VISA resources.
    - Connecting to and disconnecting from a selected instrument.
    - Displaying current instrument settings (Center Freq, Span, RBW, VBW, Ref Level, Preamp, High Sensitivity).
    - Providing buttons to apply current GUI settings to the instrument and query current instrument settings.
    - Dynamically updating UI element visibility based on connection state.
    - Saving and loading the last selected VISA resource to/from config.ini.

    Inputs:
        parent (tk.Widget): The parent widget (e.g., ttk.Notebook).
        app_instance (object): The main application instance, providing access to shared data and methods.
        console_print_func (function): Function to print messages to the console.
        style_obj (ttk.Style): The ttk.Style object for applying custom styles.

    Process of this class:
        1. Initializes the Tkinter Frame and sets up instance variables.
        2. Creates and arranges widgets:
           - Resource discovery section (label, combobox, refresh button).
           - Connection status section (labels for model, serial, firmware, options).
           - Connection control buttons (Connect, Disconnect).
           - Current settings display (labels for Center Freq, Span, RBW, VBW, Ref Level, Preamp, High Sensitivity).
           - Settings control buttons (Apply Settings, Query Settings).
        3. Sets up event bindings for buttons and combobox selection.
        4. Loads the last selected resource from config.ini on initialization.
        5. Updates UI element visibility based on initial connection status.
        6. Implements methods for:
           - Refreshing VISA resources (`_refresh_resources`).
           - Connecting to the selected instrument (`_connect_instrument`).
           - Disconnecting from the instrument (`_disconnect_instrument`).
           - Applying settings to the instrument (`_apply_settings_to_instrument`).
           - Querying settings from the instrument (`_query_settings_from_instrument`).
           - Clearing the settings display (`_clear_settings_display`).
           - Updating UI element visibility (`_update_ui_elements_visibility`).
           - Loading/saving last selected resource (`_load_last_selected_resource`, `_save_last_selected_resource`).
           - Handling tab selection events (`_on_tab_selected`).

    Outputs of this class:
        A functional Tkinter Frame for instrument connection and settings management.
    """
    def __init__(self, parent, app_instance, console_print_func, style_obj):
        """
        Initializes the InstrumentTab.
        """
        super().__init__(parent, style='Dark.TFrame')
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj # Store the style object

        debug_log(f"Initializing InstrumentTab...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        self._create_widgets()
        self._setup_bindings()
        self._load_last_selected_resource() # Load last selected resource on init
        # Initial state: disconnected and no resources found
        self._update_ui_elements_visibility(connected=False, resource_found=False)

        debug_log(f"InstrumentTab initialized.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the widgets for the Instrument Connection tab.

        Inputs:
            None.

        Process:
            1. Configures the grid layout for the main frame.
            2. Creates and places a LabelFrame for "VISA Resource Discovery".
            3. Inside the discovery frame:
               - Creates a Label and Combobox for VISA resources.
               - Creates a "Refresh Devices" button.
            4. Creates and places a LabelFrame for "Instrument Connection Status".
            5. Inside the status frame:
               - Creates Labels to display Instrument Model, Serial, Firmware, and Options.
            6. Creates and places a LabelFrame for "Connection Control".
            7. Inside the control frame:
               - Creates "Connect" and "Disconnect" buttons.
            8. Creates and places a LabelFrame for "Current Instrument Settings".
            9. Inside the settings frame:
               - Creates Labels to display Center Frequency, Span, RBW, VBW, Ref Level, Preamp, and High Sensitivity.
            10. Creates and places a LabelFrame for "Settings Control".
            11. Inside the settings control frame:
                - Creates "Apply Settings to Instrument" and "Query Settings from Instrument" buttons.

        Outputs:
            None. Populates the tab with GUI elements.
        """
        debug_log(f"Creating InstrumentTab widgets...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Resource Discovery
        self.grid_rowconfigure(1, weight=0) # Connection Status
        self.grid_rowconfigure(2, weight=0) # Connection Control
        self.grid_rowconfigure(3, weight=0) # Current Settings
        self.grid_rowconfigure(4, weight=1) # Settings Control (takes remaining space)


        # --- VISA Resource Discovery ---
        resource_frame = ttk.LabelFrame(self, text="VISA Resource Discovery", style='Dark.TLabelframe')
        resource_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        resource_frame.grid_columnconfigure(0, weight=1)
        resource_frame.grid_columnconfigure(1, weight=1)
        resource_frame.grid_columnconfigure(2, weight=0) # Button column

        ttk.Label(resource_frame, text="Available Resources:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.resource_combobox = ttk.Combobox(resource_frame, textvariable=self.app_instance.selected_resource, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.refresh_button = ttk.Button(resource_frame, text="Refresh Devices", command=self._refresh_resources, style='Blue.TButton')
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")


        # --- Instrument Connection Status ---
        status_frame = ttk.LabelFrame(self, text="Instrument Connection Status", style='Dark.TLabelframe')
        status_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=0) # Label column
        status_frame.grid_columnconfigure(1, weight=1) # Value column

        ttk.Label(status_frame, text="Model:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.model_label = ttk.Label(status_frame, textvariable=self.app_instance.instrument_model, style='Dark.TLabel.Value')
        self.model_label.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(status_frame, text="Serial:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.serial_label = ttk.Label(status_frame, textvariable=self.app_instance.instrument_serial, style='Dark.TLabel.Value')
        self.serial_label.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(status_frame, text="Firmware:", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.firmware_label = ttk.Label(status_frame, textvariable=self.app_instance.instrument_firmware, style='Dark.TLabel.Value')
        self.firmware_label.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(status_frame, text="Options:", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.options_label = ttk.Label(status_frame, textvariable=self.app_instance.instrument_options, style='Dark.TLabel.Value')
        self.options_label.grid(row=3, column=1, padx=5, pady=2, sticky="ew")


        # --- Connection Control ---
        connection_control_frame = ttk.LabelFrame(self, text="Connection Control", style='Dark.TLabelframe')
        connection_control_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        connection_control_frame.grid_columnconfigure(0, weight=1)
        connection_control_frame.grid_columnconfigure(1, weight=1)

        self.connect_button = ttk.Button(connection_control_frame, text="Connect", command=self._connect_instrument, style='Green.TButton')
        self.connect_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(connection_control_frame, text="Disconnect", command=self._disconnect_instrument, style='Red.TButton')
        self.disconnect_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


        # --- Current Instrument Settings Display ---
        settings_display_frame = ttk.LabelFrame(self, text="Current Instrument Settings (from GUI)", style='Dark.TLabelframe')
        settings_display_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        settings_display_frame.grid_columnconfigure(0, weight=0) # Label column
        settings_display_frame.grid_columnconfigure(1, weight=1) # Value column

        ttk.Label(settings_display_frame, text="Center Freq:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.display_center_freq = ttk.Label(settings_display_frame, textvariable=self.app_instance.center_freq_hz_var, style='Dark.TLabel.Value')
        self.display_center_freq.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="Span:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.display_span = ttk.Label(settings_display_frame, textvariable=self.app_instance.span_hz_var, style='Dark.TLabel.Value')
        self.display_span.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="RBW:", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.display_rbw = ttk.Label(settings_display_frame, textvariable=self.app_instance.rbw_hz_var, style='Dark.TLabel.Value')
        self.display_rbw.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="VBW:", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.display_vbw = ttk.Label(settings_display_frame, textvariable=self.app_instance.vbw_hz_var, style='Dark.TLabel.Value')
        self.display_vbw.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="Ref Level (dBm):", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.display_ref_level = ttk.Label(settings_display_frame, textvariable=self.app_instance.reference_level_dbm_var, style='Dark.TLabel.Value')
        self.display_ref_level.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="Preamp:", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.display_preamp = ttk.Label(settings_display_frame, textvariable=self.app_instance.preamp_on_var, style='Dark.TLabel.Value')
        self.display_preamp.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(settings_display_frame, text="High Sensitivity:", style='Dark.TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.display_high_sensitivity = ttk.Label(settings_display_frame, textvariable=self.app_instance.high_sensitivity_var, style='Dark.TLabel.Value')
        self.display_high_sensitivity.grid(row=6, column=1, padx=5, pady=2, sticky="ew")


        # --- Settings Control (Apply/Query) ---
        settings_control_frame = ttk.LabelFrame(self, text="Settings Control", style='Dark.TLabelframe')
        settings_control_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        settings_control_frame.grid_columnconfigure(0, weight=1)
        settings_control_frame.grid_columnconfigure(1, weight=1)

        self.apply_settings_button = ttk.Button(settings_control_frame, text="Apply Settings to Instrument", command=self._apply_settings_to_instrument, style='Orange.TButton')
        self.apply_settings_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.query_settings_button = ttk.Button(settings_control_frame, text="Query Settings from Instrument", command=self._query_settings_from_instrument, style='Blue.TButton')
        self.query_settings_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        debug_log(f"InstrumentTab widgets created. Ready to serve!",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _setup_bindings(self):
        """
        Function Description:
        Sets up event bindings for the widgets in the InstrumentTab.

        Inputs:
            None.

        Process:
            1. Binds the `<<ComboboxSelected>>` event to the resource combobox,
                triggering `_on_resource_selected`.

        Outputs:
            None. Establishes event handling.
        """
        debug_log(f"Setting up InstrumentTab bindings...",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)
        debug_log(f"InstrumentTab bindings setup complete.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _refresh_resources(self):
        """
        Function Description:
        Initiates the process of discovering available VISA resources in a separate thread
        to keep the GUI responsive. It updates the resource combobox with the found resources.

        Inputs:
            None.

        Process:
            1. Prints a console message.
            2. Prints a debug message.
            3. Disables relevant UI elements to prevent user interaction during resource discovery.
            4. Starts a new thread that calls `populate_resources_logic`.
            5. The `populate_resources_logic` function (in `src.instrument_logic.py`)
                will return the list of resources.
            6. A callback function is scheduled on the main Tkinter thread (`self.app_instance.after`)
                to update the combobox and re-enable buttons.

        Outputs:
            None. Triggers resource discovery and UI updates.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("Searching for VISA instruments...")
        debug_log(f"Initiating resource refresh.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Disable buttons during refresh
        self.refresh_button.config(state=tk.DISABLED)
        self.connect_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)
        self.resource_combobox.config(state="disabled")

        # Clear existing resources and selection
        self.app_instance.available_resources.set("")
        self.app_instance.selected_resource.set("")
        self.resource_combobox['values'] = []
        self._clear_settings_display() # Clear displayed settings

        # Clear instrument info labels
        self.app_instance.instrument_model.set("N/A")
        self.app_instance.instrument_serial.set("N/A")
        self.app_instance.instrument_firmware.set("N/A")
        self.app_instance.instrument_options.set("N/A")

        def _run_refresh_in_thread():
            """Helper function to run populate_resources_logic in a separate thread."""
            # populate_resources_logic now returns the list of resources
            resources = populate_resources_logic(self.app_instance, self.console_print_func)
            # Schedule the GUI update on the main thread
            self.app_instance.after(0, self._update_resources_in_gui_callback, resources)

        # Start resource population in a separate thread
        threading.Thread(target=_run_refresh_in_thread).start()

    def _update_resources_in_gui_callback(self, resources):
        """
        Function Description:
        Callback function executed on the main Tkinter thread to update the GUI
        with discovered VISA resources and re-enable buttons.

        Inputs:
            resources (list): A list of discovered VISA resource strings.

        Process:
            1. Updates the `values` of the resource combobox.
            2. Updates `app_instance.available_resources` for persistence.
            3. Sets the `selected_resource` to the first found resource or clears it.
            4. Calls `_update_ui_elements_visibility` to re-enable relevant buttons.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating GUI with discovered resources: {resources}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.resource_combobox['values'] = resources
        self.app_instance.available_resources.set(','.join(resources)) # Store for config

        if resources:
            # Try to re-select the last known resource, otherwise select the first
            last_selected = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_instrument_connection__visa_resource', fallback='')
            if last_selected and last_selected in resources:
                self.app_instance.selected_resource.set(last_selected)
                debug_log(f"Restored last selected resource in combobox: {last_selected}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
            else:
                self.app_instance.selected_resource.set(resources[0])
                debug_log(f"Setting selected resource to first available: {resources[0]}",
                            file=current_file,
                            version=current_version,
                            function=current_function)
            self._update_ui_elements_visibility(connected=self.app_instance.inst is not None, resource_found=True)
        else:
            self.app_instance.selected_resource.set("")
            self._update_ui_elements_visibility(connected=False, resource_found=False)

        debug_log(f"Resource combobox updated and UI elements re-enabled.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_resource_selected(self, event):
        """
        Function Description:
        Handles the event when a VISA resource is selected from the combobox.
        It saves the selected resource to the application's configuration.

        Inputs:
            event (tkinter.Event): The event object.

        Process:
            1. Prints a debug message.
            2. Calls `_save_last_selected_resource` to persist the selection.
            3. Updates UI element visibility to reflect that a resource is now selected.

        Outputs:
            None. Persists selected resource and updates UI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Resource selected: {self.app_instance.selected_resource.get()}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self._save_last_selected_resource()
        # A resource is selected, so update UI to enable connect button
        self._update_ui_elements_visibility(connected=False, resource_found=True)

    def _connect_instrument(self):
        """
        Function Description:
        Attempts to establish a connection to the selected VISA instrument in a
        separate thread to prevent GUI freezing. Updates UI based on connection success.

        Inputs:
            None.

        Process:
            1. Prints a console message.
            2. Prints a debug message.
            3. Disables the Connect button and enables the Disconnect button temporarily.
            4. Starts a new thread to call `connect_instrument_logic`.
            5. `connect_instrument_logic` will update `self.app_instance.inst`
                and other instrument info variables upon completion, and importantly,
                it calls `app_instance.update_connection_status` which will handle
                the overall UI update.

        Outputs:
            None. Triggers instrument connection and UI updates.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.app_instance.selected_resource.get()
        if not selected_resource:
            self.console_print_func("❌ No VISA resource selected. Please select a device.")
            debug_log(f"Attempted to connect without selecting a resource. User is an idiot!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func(f"Connecting to {selected_resource}...")
        debug_log(f"Initiating connection to {selected_resource}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Optimistic UI update while connecting (buttons handled by update_connection_status_logic)
        self.connect_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.resource_combobox.config(state="disabled")

        # The connect_instrument_logic will call app_instance.update_connection_status
        # which will then call update_connection_status_logic to manage all button states.
        threading.Thread(target=connect_instrument_logic,
                         args=(self.app_instance, self.console_print_func)).start()

    def _disconnect_instrument(self):
        """
        Function Description:
        Attempts to disconnect from the currently connected VISA instrument in a
        separate thread to prevent GUI freezing. Updates UI based on disconnection success.

        Inputs:
            None.

        Process:
            1. Prints a console message.
            2. Prints a debug message.
            3. Disables the Disconnect button and enables the Connect button temporarily.
            4. Starts a new thread to call `disconnect_instrument_logic`.
            5. `disconnect_instrument_logic` will set `self.app_instance.inst` to None
                and clear instrument info variables upon completion, and importantly,
                it calls `app_instance.update_connection_status` which will handle
                the overall UI update.

        Outputs:
            None. Triggers instrument disconnection and UI updates.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument is currently connected. Nothing to disconnect, you moron!")
            debug_log(f"Attempted to disconnect when no instrument was connected. What a waste of time!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func("Disconnecting instrument...")
        debug_log(f"Initiating disconnection.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Optimistic UI update while disconnecting (buttons handled by update_connection_status_logic)
        self.disconnect_button.config(state=tk.DISABLED)
        self.resource_combobox.config(state="disabled")

        # The disconnect_instrument_logic will call app_instance.update_connection_status
        # which will then call update_connection_status_logic to manage all button states.
        threading.Thread(target=disconnect_instrument_logic,
                         args=(self.app_instance, self.console_print_func)).start()

    def _apply_settings_to_instrument(self):
        """
        Function Description:
        Applies the current settings from the GUI's Tkinter variables to the connected instrument.
        This operation is performed in a separate thread to keep the GUI responsive.

        Inputs:
            None.

        Process:
            1. Checks if an instrument is connected; if not, logs an error and returns.
            2. Prints a console message.
            3. Prints a debug message.
            4. Disables the "Apply Settings" and "Query Settings" buttons to prevent re-entry.
            5. Starts a new thread to call `apply_instrument_settings_logic`.
            6. Re-enables buttons upon completion via `self.app_instance.after`.

        Outputs:
            None. Configures the connected instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot apply settings.")
            debug_log(f"Attempted to apply settings with no instrument connected. What a fucking waste!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func("Applying settings to instrument...")
        debug_log(f"Initiating apply settings to instrument.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Disable buttons while applying settings
        self.apply_settings_button.config(state=tk.DISABLED)
        self.query_settings_button.config(state=tk.DISABLED)

        # The apply_instrument_settings_logic will handle re-enabling buttons
        threading.Thread(target=apply_instrument_settings_logic,
                         args=(self.app_instance, self.console_print_func)).start()

    def _query_settings_from_instrument(self):
        """
        Function Description:
        Queries the current settings from the connected instrument and updates the GUI display.
        This operation is performed in a separate thread to keep the GUI responsive.

        Inputs:
            None.

        Process:
            1. Checks if an instrument is connected; if not, logs an error and returns.
            2. Prints a console message.
            3. Prints a debug message.
            4. Disables the "Apply Settings" and "HQuery Settings" buttons to prevent re-entry.
            5. Starts a new thread to call `query_current_instrument_settings_logic`.
            6. Updates the display labels with the queried values upon completion via `self.app_instance.after`.
            7. Re-enables buttons upon completion.

        Outputs:
            None. Updates GUI with instrument's current settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot query settings.")
            debug_log(f"Attempted to query settings with no instrument connected. What a fucking waste!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        self.console_print_func("Querying settings from instrument...")
        debug_log(f"Initiating query settings from instrument.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Disable buttons while querying
        self.apply_settings_button.config(state=tk.DISABLED)
        self.query_settings_button.config(state=tk.DISABLED)

        # The query_current_instrument_settings_logic will handle re-enabling buttons
        threading.Thread(target=query_current_instrument_settings_logic,
                         args=(self.app_instance, self.console_print_func)).start()

    def _clear_settings_display(self):
        """
        Function Description:
        Clears the displayed instrument settings on the GUI.

        Inputs:
            None.

        Process:
            1. Sets the text of all settings display labels to "N/A" or default values.

        Outputs:
            None. Resets the settings display.
        """
        debug_log(f"Clearing instrument settings display.",
                    file=current_file,
                    version=current_version,
                    function=inspect.currentframe().f_code.co_name)
        self.app_instance.center_freq_hz_var.set(0.0)
        self.app_instance.span_hz_var.set(0.0)
        self.app_instance.rbw_hz_var.set(0.0)
        self.app_instance.vbw_hz_var.set(0.0)
        self.app_instance.reference_level_dbm_var.set("N/A")
        self.app_instance.preamp_on_var.set(False)
        self.app_instance.high_sensitivity_var.set(False)

    def _update_ui_elements_visibility(self, connected, resource_found):
        """
        Function Description:
        Updates the visibility and state of various UI elements on the InstrumentTab
        based on the instrument's connection status and whether a resource has been found.

        Inputs:
            connected (bool): True if the instrument is currently connected.
            resource_found (bool): True if a VISA resource has been selected/found.

        Process:
            1. Prints a debug message.
            2. Sets the state of connection buttons (Connect, Disconnect) based on `connected` and `resource_found`.
            3. Sets the state of settings control buttons (Apply, Query) based on `connected`.
            4. Updates the resource combobox state.
            5. Updates the instrument info labels (Model, Serial, Firmware, Options) based on `connected`.

        Outputs:
            None. Adjusts UI element states.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating InstrumentTab UI visibility. Connected: {connected}, Resource Found: {resource_found}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Connection Control Buttons
        if connected:
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL) # Can refresh even when connected
            self.resource_combobox.config(state="readonly")
        elif resource_found:
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.NORMAL)
            self.resource_combobox.config(state="readonly")
        else: # No resource found or selected
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.NORMAL)
            self.resource_combobox.config(state="disabled")

        # Settings Control Buttons
        settings_button_state = tk.NORMAL if connected else tk.DISABLED
        self.apply_settings_button.config(state=settings_button_state)
        self.query_settings_button.config(state=settings_button_state)

        # Instrument Info Labels (Model, Serial, Firmware, Options)
        # These are now Tkinter StringVars, so their values are automatically updated
        # by the instrument_logic functions. We just need to ensure they are displayed.
        # The labels are always present, their text will reflect the StringVar value.
        if not connected:
            self.app_instance.instrument_model.set("N/A")
            self.app_instance.instrument_serial.set("N/A")
            self.app_instance.instrument_firmware.set("N/A")
            self.app_instance.instrument_options.set("N/A")
            self._clear_settings_display() # Clear settings display when disconnected

        debug_log(f"InstrumentTab UI visibility updated.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _load_last_selected_resource(self):
        """
        Function Description:
        Loads the last selected VISA resource from the application's configuration
        and sets it as the current selection in the combobox.

        Inputs:
            None.

        Process:
            1. Prints a debug message.
            2. Retrieves the 'last_instrument_connection__visa_resource' from config.ini.
            3. Sets the `self.app_instance.selected_resource` Tkinter variable.
            4. Prints a debug message about the loaded resource.

        Outputs:
            None. Updates the combobox selection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading last selected resource from config.ini...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        last_selected_from_config = self.app_instance.config.get('LAST_USED_SETTINGS', 'last_instrument_connection__visa_resource', fallback='').strip()
        self.app_instance.selected_resource.set(last_selected_from_config)

        if last_selected_from_config:
            debug_log(f"Last selected resource loaded: {last_selected_from_config}.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"No last selected resource found in config.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

    def _save_last_selected_resource(self):
        """
        Function Description:
        Saves the currently selected VISA resource to the application's configuration.

        Inputs:
            None.

        Process:
            1. Prints a debug message.
            2. Retrieves the current value of `self.app_instance.selected_resource`.
            3. Sets the 'last_instrument_connection__visa_resource' in the config.ini.
            4. Calls `save_config` to persist the changes to the file.

        Outputs:
            None. Persists the selected resource.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.app_instance.selected_resource.get()
        debug_log(f"Saving last selected resource to config.ini: {selected_resource}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        
        self.app_instance.config.set('LAST_USED_SETTINGS', 'last_instrument_connection__visa_resource', selected_resource)
        # Pass console_log from here to save_config
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        debug_log(f"Last selected resource saved: {selected_resource}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the UI elements based on the current connection status.
        If connected, it clears the settings display (but does not automatically query).
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"InstrumentTab selected. Refreshing UI based on connection status.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.inst is not None
        resource_found = bool(self.app_instance.selected_resource.get())

        if is_connected:
            debug_log("Instrument is connected. Clearing settings display on tab selection (no automatic query, you gotta push the button for that, you lazy bastard).",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            self._clear_settings_display() # Just clear, don't query automatically
        else:
            debug_log("Instrument is NOT connected. Clearing settings display on tab selection.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            self._clear_settings_display()

        # Update UI visibility based on connection status when tab is selected
        self._update_ui_elements_visibility(connected=is_connected, resource_found=resource_found)

