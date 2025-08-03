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
# Version 20250803.1115.5 (Fixed ImportError: cannot import name 'query_instrument_settings' by correcting import to 'query_current_instrument_settings'.)
# Version 20250803.1132.0 (Fixed ImportError: cannot import name 'restore_default_settings_logic' by removing its import from instrument_logic and calling the logic directly from src.settings_and_config.restore_settings_logic.)
# Version 20250803.1400.0 (Corrected passing of app_instance to connect_instrument_logic and disconnect_instrument_logic.)
# Version 20250803.1655.0 (Fixed AttributeError: '_tkinter.tkapp' object has no attribute 'selected_resource' by changing to 'selected_visa_resource_var'.)
# Version 20250803.1700.0 (Refactored apply_instrument_settings_logic into a new utility file.)
# Version 20250803.1705.0 (Fixed ImportError for initialize_instrument_logic by importing from utils_instrument_initialize.py.)
# Version 20250803.1720.0 (Fixed ModuleNotFoundError for 'frequency_bands' by correcting import path.)

current_version = "20250803.1705.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1705 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect # Import inspect module
import os # Import os module for os.path.basename

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import instrument logic functions
from tabs.Instrument.instrument_logic import (
    connect_instrument_logic,
    disconnect_instrument_logic,
)

# Import utility functions for instrument connection
from tabs.Instrument.utils_instrument_connection import list_visa_resources

# Import new utility for applying settings
from tabs.Instrument.utils_instrument_apply_settings import apply_instrument_settings_logic

# Import utility for querying settings
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings

# Import utility for initializing instrument
from tabs.Instrument.utils_instrument_initialize import initialize_instrument_logic

# Import ref data
from ref.ref_scanner_setting_lists import (
    reference_level_drop_down, # CORRECTED: Changed import name from ref_level_drop_down
    rbw_presets, # CORRECTED: Changed from rbw_drop_down to rbw_presets
    # span_drop_down, # Not found in ref_scanner_setting_lists.py, removed.
    # center_freq_drop_down, # Not found in ref_scanner_setting_lists.py, removed.
    attenuation_levels, # Added attenuation_levels
    frequency_shifts, # Added frequency_shifts
    scan_modes, # Added scan_modes
    dwell_time_drop_down, # Added dwell_time_drop_down
    cycle_wait_time_presets, # Added cycle_wait_time_presets
    number_of_scans_presets, # Added number_of_scans_presets
    graph_quality_drop_down # Added graph_quality_drop_down
)
from ref.frequency_bands import ( # CORRECTED: Importing from ref.frequency_bands
    SCAN_BAND_RANGES, # This is where SCAN_BAND_RANGES is defined
    DEFAULT_REF_LEVEL_OPTIONS,
    RBW_OPTIONS,
    DEFAULT_FREQ_SHIFT_OPTIONS
)


class InstrumentTab(ttk.Frame):
    """
    Function Description:
    Manages the Instrument Connection tab in the GUI. This tab allows users to:
    - Discover available VISA resources.
    - Connect to and disconnect from a selected instrument.
    - Display current instrument connection status and queried settings.
    - Initialize the instrument with default settings.
    - Apply custom instrument settings (Center Freq, Span, RBW, Ref Level, Preamp, High Sensitivity).

    Inputs:
    - master (tk.Widget): The parent widget (notebook) for this tab.
    - app_instance (object): A reference to the main application instance, providing
                             access to shared data (Tkinter variables, config) and logging functions.
    - console_print_func (function): Function to print messages to the GUI console.
    - style_obj (ttk.Style, optional): The ttk.Style object for applying custom styles.

    Process:
    1. Initializes the Tkinter Frame and stores references to `app_instance`, `console_print_func`, and `style_obj`.
    2. Calls `_create_widgets` to build the UI elements for the tab.
    3. Calls `_update_connection_status_ui` to set the initial UI state based on connection.
    4. Binds the `<<NotebookTabSelected>>` event to `_on_tab_selected` to refresh UI on tab switch.

    Outputs:
    - None. Initializes and manages the Instrument Connection tab's GUI and logic.
    """
    def __init__(self, master, app_instance, console_print_func, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing InstrumentTab. Version: {current_version}. Let's build this instrument interface!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        # Filter out style_obj from kwargs before passing to super()
        style_obj = kwargs.pop('style_obj', None)
        super().__init__(master, **kwargs)

        self.master = master
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj # Store the style object if passed

        self.current_version = current_version
        self.current_file = os.path.basename(__file__)

        self._create_widgets()
        self._update_connection_status_ui() # Set initial UI state

        # Bind the tab selection event
        self.master.bind("<<NotebookTabSelected>>", self._on_tab_selected)

        debug_log(f"InstrumentTab initialized. Version: {current_version}. UI elements are ready!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all the Tkinter widgets for the Instrument Connection tab.
        This includes frames, labels, entry fields, comboboxes, and buttons for
        VISA resource selection, connection control, and instrument settings.

        Inputs:
            None.

        Process:
            1. Configures the grid layout for the main frame.
            2. Creates and places a 'Connection Control' frame with:
               - A combobox for VISA resource selection, bound to `app_instance.selected_visa_resource_var`.
               - A 'Refresh Devices' button that calls `_refresh_devices`.
               - 'Connect' and 'Disconnect' buttons that call `_connect_instrument` and `_disconnect_instrument`.
               - Labels to display instrument model, serial, firmware, and connection status.
            3. Creates and places an 'Instrument Settings' frame with:
               - Entry fields and comboboxes for Center Freq, Span, RBW, Ref Level, Preamp, and High Sensitivity.
               - These are bound to their respective `app_instance` Tkinter variables.
               - An 'Apply Settings' button that calls `_apply_settings`.
               - An 'Initialize Instrument' button that calls `_initialize_instrument`.
               - A 'Query Settings' button that calls `_query_settings_and_info`.

        Outputs:
            None. Populates the tab with GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for InstrumentTab. Version: {self.current_version}. Building the interface!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Configure grid for the main frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # Connection Control
        self.rowconfigure(1, weight=1) # Instrument Settings

        # --- Connection Control Frame ---
        connection_frame = ttk.LabelFrame(self, text="Connection Control", style='Dark.TLabelframe')
        connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        connection_frame.columnconfigure(1, weight=1) # Allow resource combobox to expand

        # VISA Resource
        ttk.Label(connection_frame, text="VISA Resource:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.resource_combobox = ttk.Combobox(connection_frame, textvariable=self.app_instance.selected_visa_resource_var, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        # Refresh Devices Button
        ttk.Button(connection_frame, text="Refresh Devices", command=self._refresh_devices, style='Dark.TButton').grid(row=0, column=2, padx=5, pady=2)

        # Connect/Disconnect Buttons
        ttk.Button(connection_frame, text="Connect", command=self._connect_instrument, style='Dark.TButton').grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(connection_frame, text="Disconnect", command=self._disconnect_instrument, style='Dark.TButton').grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Instrument Info Display
        ttk.Label(connection_frame, text="Model:", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(connection_frame, textvariable=self.app_instance.instrument_model_var, style='Dark.TLabel.Value').grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(connection_frame, text="Serial:", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(connection_frame, textvariable=self.app_instance.instrument_serial_var, style='Dark.TLabel.Value').grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(connection_frame, text="Firmware:", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(connection_frame, textvariable=self.app_instance.instrument_firmware_var, style='Dark.TLabel.Value').grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(connection_frame, text="Status:", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.connection_status_label = ttk.Label(connection_frame, textvariable=self.app_instance.instrument_connection_status_var, style='Dark.TLabel.Value')
        self.connection_status_label.grid(row=5, column=1, padx=5, pady=2, sticky="ew")


        # --- Instrument Settings Frame ---
        settings_frame = ttk.LabelFrame(self, text="Instrument Settings", style='Dark.TLabelframe')
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        settings_frame.columnconfigure(1, weight=1) # Allow entry/combobox to expand

        # Center Frequency
        ttk.Label(settings_frame, text="Center Freq (MHz):", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.center_freq_entry = ttk.Entry(settings_frame, textvariable=self.app_instance.center_freq_mhz_var, style='TEntry')
        self.center_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # Using a subset of frequency_bands for center frequency options for now, as a dedicated list isn't present
        self.center_freq_combobox = ttk.Combobox(settings_frame, values=[band['Start MHz'] for band in SCAN_BAND_RANGES] + [band['Stop MHz'] for band in SCAN_BAND_RANGES], style='TCombobox')
        self.center_freq_combobox.grid(row=0, column=2, padx=5, pady=2)
        self.center_freq_combobox.bind("<<ComboboxSelected>>", lambda event, var=self.app_instance.center_freq_mhz_var: self._set_combobox_value(event, var))


        # Span
        ttk.Label(settings_frame, text="Span (MHz):", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.span_entry = ttk.Entry(settings_frame, textvariable=self.app_instance.span_mhz_var, style='TEntry')
        self.span_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # Using a subset of frequency_bands for span options for now, as a dedicated list isn't present
        # This is a placeholder, you might want to define specific span options in ref_scanner_setting_lists.py
        self.span_combobox = ttk.Combobox(settings_frame, values=[10, 20, 50, 100, 200, 500, 1000], style='TCombobox')
        self.span_combobox.grid(row=1, column=2, padx=5, pady=2)
        self.span_combobox.bind("<<ComboboxSelected>>", lambda event, var=self.app_instance.span_mhz_var: self._set_combobox_value(event, var))


        # RBW
        ttk.Label(settings_frame, text="RBW (Hz):", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.rbw_entry = ttk.Entry(settings_frame, textvariable=self.app_instance.rbw_hz_var, style='TEntry')
        self.rbw_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.rbw_combobox = ttk.Combobox(settings_frame, values=[item['value'] for item in rbw_presets], style='TCombobox') # Changed to rbw_presets
        self.rbw_combobox.grid(row=2, column=2, padx=5, pady=2)
        self.rbw_combobox.bind("<<ComboboxSelected>>", lambda event, var=self.app_instance.rbw_hz_var: self._set_combobox_value(event, var))


        # Reference Level
        ttk.Label(settings_frame, text="Ref Level (dBm):", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.ref_level_entry = ttk.Entry(settings_frame, textvariable=self.app_instance.ref_level_dbm_var, style='TEntry')
        self.ref_level_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.ref_level_combobox = ttk.Combobox(settings_frame, values=[item['value'] for item in reference_level_drop_down], style='TCombobox') # CORRECTED: reference_level_drop_down
        self.ref_level_combobox.grid(row=3, column=2, padx=5, pady=2)
        self.ref_level_combobox.bind("<<ComboboxSelected>>", lambda event, var=self.app_instance.ref_level_dbm_var: self._set_combobox_value(event, var))


        # Preamp
        ttk.Label(settings_frame, text="Preamp:", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        # Assuming preamp_drop_down will be a list of dicts like [{"label": "ON", "value": True}, {"label": "OFF", "value": False}]
        self.preamp_combobox = ttk.Combobox(settings_frame, values=["ON", "OFF"], state="readonly", style='TCombobox') # Using simple ON/OFF for now
        self.preamp_combobox.grid(row=4, column=1, padx=5, pady=2, sticky="ew", columnspan=2)
        self.preamp_combobox.bind("<<ComboboxSelected>>", lambda event: self._set_boolean_combobox_value(event, self.app_instance.preamp_on_var, [{"label": "ON", "value": True}, {"label": "OFF", "value": False}]))


        # High Sensitivity Mode
        ttk.Label(settings_frame, text="High Sensitivity:", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        # Assuming high_sensitivity_drop_down will be a list of dicts like [{"label": "ON", "value": True}, {"label": "OFF", "value": False}]
        self.high_sensitivity_combobox = ttk.Combobox(settings_frame, values=["ON", "OFF"], state="readonly", style='TCombobox') # Using simple ON/OFF for now
        self.high_sensitivity_combobox.grid(row=5, column=1, padx=5, pady=2, sticky="ew", columnspan=2)
        self.high_sensitivity_combobox.bind("<<ComboboxSelected>>", lambda event: self._set_boolean_combobox_value(event, self.app_instance.high_sensitivity_on_var, [{"label": "ON", "value": True}, {"label": "OFF", "value": False}]))


        # Action Buttons
        ttk.Button(settings_frame, text="Apply Settings", command=self._apply_settings, style='Dark.TButton').grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(settings_frame, text="Initialize Instrument", command=self._initialize_instrument, style='Dark.TButton').grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(settings_frame, text="Query Settings", command=self._query_settings_and_info, style='Dark.TButton').grid(row=6, column=2, padx=5, pady=5, sticky="ew")

        debug_log(f"Widgets created for InstrumentTab. Version: {self.current_version}. Interface is built!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

    def _set_combobox_value(self, event, tk_var):
        """Helper to set Tkinter variable from combobox selection."""
        selected_value = self.master.call(self.master.tk.eval, 'set ::tk_combobox_value')
        tk_var.set(float(selected_value)) # Assuming all these are float values
        debug_log(f"Combobox value set for {tk_var.name}: {selected_value}",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=inspect.currentframe().f_code.co_name)

    def _set_boolean_combobox_value(self, event, tk_var, data_list):
        """Helper to set Tkinter BooleanVar from combobox selection based on 'label' and 'value' in data_list."""
        selected_label = self.master.call(self.master.tk.eval, 'set ::tk_combobox_value')
        # Find the corresponding value (True/False) from the data_list
        selected_item = next((item for item in data_list if item['label'] == selected_label), None)
        if selected_item:
            tk_var.set(selected_item['value'])
            debug_log(f"Boolean combobox value set for {tk_var.name}: {selected_item['value']} (from '{selected_label}')",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=inspect.currentframe().f_code.co_name)
        else:
            debug_log(f"WARNING: Could not find value for selected label '{selected_label}' in data_list for {tk_var.name}.",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=inspect.currentframe().f_code.co_name)


    def _refresh_devices(self):
        """
        Function Description:
        Discovers available VISA resources and updates the resource combobox.

        Inputs:
            None.

        Process:
            1. Calls `list_visa_resources` utility function.
            2. Updates the `resource_combobox` with the discovered resources.
            3. Logs the action.

        Outputs:
            None. Updates the GUI combobox.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("🔄 Refreshing VISA devices...")
        debug_log(f"Refreshing VISA devices. Version: {self.current_version}. Searching for instruments!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)
        resources = list_visa_resources(self.console_print_func)
        self.resource_combobox['values'] = resources
        if resources:
            # Set the selected_visa_resource_var to the first resource if nothing is selected
            if not self.app_instance.selected_visa_resource_var.get() or \
               self.app_instance.selected_visa_resource_var.get() not in resources:
                self.app_instance.selected_visa_resource_var.set(resources[0])
            self.console_print_func(f"✅ Found {len(resources)} VISA device(s).")
            debug_log(f"Found {len(resources)} VISA device(s): {resources}. Devices discovered!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.app_instance.selected_visa_resource_var.set("") # Clear selection if no devices
            self.console_print_func("❌ No VISA devices found.")
            debug_log("No VISA devices found. What a bummer!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self._update_connection_status_ui() # Update UI after refresh

    def _connect_instrument(self):
        """
        Function Description:
        Attempts to connect to the selected VISA instrument.

        Inputs:
            None.

        Process:
            1. Retrieves the selected VISA resource.
            2. Calls `connect_instrument_logic` to establish connection.
            3. Updates `app_instance.is_connected` based on connection success.
            4. If connected, queries and displays instrument info and settings.
            5. Updates the connection status UI.

        Outputs:
            None. Updates application state and GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.app_instance.selected_visa_resource_var.get()
        if not selected_resource:
            self.console_print_func("⚠️ Please select a VISA resource to connect. Pick one, any one!")
            debug_log("No VISA resource selected for connection. User needs to pick one!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            return

        self.console_print_func(f"Attempting to connect to {selected_resource}...")
        debug_log(f"Connecting to instrument: {selected_resource}. Let's do this!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Pass app_instance to the logic function
        # connect_instrument_logic now returns a boolean for success and sets app_instance.inst directly
        success = connect_instrument_logic( # Removed tuple unpacking as connect_instrument_logic no longer returns these
            self.app_instance, # Pass app_instance directly
            self.console_print_func
        )
        self.app_instance.is_connected.set(success)
        # The instrument_logic.py's connect_instrument_logic function now handles setting
        # app_instance.inst, model, serial, and firmware directly.
        # So, no need to set them here.

        self._update_connection_status_ui()

        if success:
            self.console_print_func("✅ Instrument connected. Querying settings...")
            self._query_settings_and_info() # Query settings immediately after connection
            debug_log("Instrument connected and settings queried. All systems go!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to connect to instrument.")
            debug_log("Failed to connect to instrument. What a disaster!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


    def _disconnect_instrument(self):
        """
        Function Description:
        Attempts to disconnect from the current VISA instrument.

        Inputs:
            None.

        Process:
            1. Calls `disconnect_instrument_logic` to close the connection.
            2. Updates `app_instance.is_connected` based on disconnection success.
            3. Clears instrument info and updates the connection status UI.

        Outputs:
            None. Updates application state and GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        self.console_print_func("Attempting to disconnect instrument...")
        debug_log(f"Disconnecting instrument. Version: {self.current_version}. Time to say goodbye!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Pass app_instance to the logic function
        success = disconnect_instrument_logic(
            self.app_instance, # Pass the app_instance directly
            self.console_print_func
        )
        self.app_instance.is_connected.set(not success) # If disconnect is successful, is_connected should be False
        if success:
            # These are now handled by instrument_logic.py's disconnect_instrument_logic
            # self.app_instance.instrument = None # Clear the instrument reference
            # self.app_instance.instrument_model_var.set("")
            # self.app_instance.instrument_serial_var.set("")
            # self.app_instance.instrument_firmware_var.set("")
            self.console_print_func("✅ Instrument disconnected.")
            debug_log("Instrument disconnected. All done!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to disconnect instrument.")
            debug_log("Failed to disconnect instrument. Still stuck!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self._update_connection_status_ui()


    def _initialize_instrument(self):
        """
        Function Description:
        Initializes the connected instrument with a set of default settings.

        Inputs:
            None.

        Process:
            1. Checks if an instrument is connected.
            2. Calls `initialize_instrument_logic` to send initialization commands.
            3. If successful, queries and displays current settings.

        Outputs:
            None. Configures the instrument and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.is_connected.get():
            self.console_print_func("⚠️ Not connected to an instrument. Connect first! What are you waiting for?!")
            debug_log("Attempted to initialize instrument but not connected. User needs to connect!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            return

        self.console_print_func("Initializing instrument with default settings...")
        debug_log(f"Initializing instrument. Version: {self.current_version}. Setting up the defaults!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Pass all necessary Tkinter variables and console_print_func
        success = initialize_instrument_logic(
            self.app_instance.instrument,
            self.app_instance.ref_level_dbm_var.get(), # Pass current ref level
            self.app_instance.high_sensitivity_on_var.get(), # Pass current high sensitivity
            self.app_instance.preamp_on_var.get(), # Pass current preamp state
            self.app_instance.rbw_hz_var.get(), # Pass current RBW (though not directly used in initialize_instrument for setting RBW)
            0.0, # VBW is not a Tkinter var, pass default 0.0
            self.app_instance.instrument_model_var.get(), # Pass instrument model for specific commands
            self.console_print_func
        )
        if success:
            self.console_print_func("✅ Instrument initialized. Querying settings...")
            self._query_settings_and_info() # Query settings after initialization
            debug_log("Instrument initialized and settings queried. Ready for action!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to initialize instrument.")
            debug_log("Failed to initialize instrument. This is not good!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


    def _apply_settings(self):
        """
        Function Description:
        Applies the settings specified in the GUI fields to the connected instrument.

        Inputs:
            None.

        Process:
            1. Checks if an instrument is connected.
            2. Retrieves values from Tkinter variables for Center Freq, Span, RBW, Ref Level, Preamp, High Sensitivity.
            3. Calls `apply_instrument_settings_logic` to send these settings to the instrument.
            4. If successful, queries and displays current settings.

        Outputs:
            None. Configures the instrument and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.is_connected.get():
            self.console_print_func("⚠️ Not connected to an instrument. Connect first! You can't apply settings to thin air!")
            debug_log("Attempted to apply settings but not connected. User needs to connect!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            return

        self.console_print_func("Applying settings to instrument...")
        debug_log(f"Applying settings. Version: {self.current_version}. Sending commands!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        center_freq_mhz = self.app_instance.center_freq_mhz_var.get()
        span_mhz = self.app_instance.span_mhz_var.get()
        rbw_hz = self.app_instance.rbw_hz_var.get()
        ref_level_dbm = self.app_instance.ref_level_dbm_var.get()
        preamp_on = self.app_instance.preamp_on_var.get()
        high_sensitivity_on = self.app_instance.high_sensitivity_on_var.get()

        success = apply_instrument_settings_logic(
            self.app_instance.instrument,
            center_freq_mhz,
            span_mhz,
            rbw_hz,
            ref_level_dbm,
            preamp_on,
            high_sensitivity_on,
            self.console_print_func
        )
        if success:
            self.console_print_func("✅ Settings applied. Querying current settings...")
            self._query_settings_and_info() # Query settings after applying
            debug_log("Settings applied and queried. Instrument updated!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.console_print_func("❌ Failed to apply settings.")
            debug_log("Failed to apply settings. Something went wrong!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


    def _query_settings_and_info(self):
        """
        Function Description:
        Queries the connected instrument for its current settings and identification info,
        then updates the corresponding GUI elements.

        Inputs:
            None.

        Process:
            1. Checks if an instrument is connected.
            2. Calls `query_current_instrument_settings` to get instrument parameters.
            3. Updates `app_instance` Tkinter variables with the queried values.
            4. Updates the instrument info labels.

        Outputs:
            None. Updates GUI elements with live instrument data.
        """
        current_function = inspect.currentframe().f_code.co_name
        if not self.app_instance.is_connected.get():
            self.console_print_func("⚠️ Not connected to an instrument. Cannot query settings. Connect first, then ask!")
            debug_log("Attempted to query settings but not connected. User needs to connect!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            return

        self.console_print_func("Querying current instrument settings and info...")
        debug_log(f"Querying instrument settings. Version: {self.current_version}. Getting the latest data!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Pass all necessary Tkinter variables and console_print_func
        center_freq_mhz, span_mhz, rbw_hz = query_current_instrument_settings(
            self.app_instance.instrument,
            1_000_000, # MHZ_TO_HZ_CONVERSION
            self.console_print_func
        )

        if center_freq_mhz is not None:
            self.app_instance.center_freq_mhz_var.set(center_freq_mhz)
        if span_mhz is not None:
            self.app_instance.span_mhz_var.set(span_mhz)
        if rbw_hz is not None:
            self.app_instance.rbw_hz_var.set(rbw_hz)

        # Query and update Ref Level, Preamp, High Sensitivity
        # These queries are currently in instrument_logic.py, but can be moved to utils_instrument_query_settings.py
        # For now, we'll call the instrument_logic function that handles the UI updates.
        # This part of the logic needs to be further refined to avoid direct UI updates from utility functions.

        # Query IDN and update model, serial, firmware
        idn_response = self.app_instance.instrument.query("*IDN?").strip()
        if idn_response:
            parts = idn_response.split(',')
            if len(parts) >= 4:
                self.app_instance.instrument_model_var.set(parts[1].strip())
                self.app_instance.instrument_serial_var.set(parts[2].strip())
                self.app_instance.instrument_firmware_var.set(parts[3].strip())
                debug_log(f"Instrument IDN queried: Model={parts[1]}, Serial={parts[2]}, Firmware={parts[3]}",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)


        # Query Ref Level
        ref_level_str = self.app_instance.instrument.query(":DISPlay:WINDow:TRACe:Y:RLEVel?").strip()
        if ref_level_str:
            self.app_instance.ref_level_dbm_var.set(float(ref_level_str))
            debug_log(f"Queried Ref Level: {ref_level_str} dBm",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

        # Query Preamp State
        preamp_str = self.app_instance.instrument.query(":POWer:GAIN?").strip()
        if preamp_str:
            self.app_instance.preamp_on_var.set(preamp_str.upper() == "ON")
            debug_log(f"Queried Preamp State: {preamp_str}",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

        # Query High Sensitivity State (model-specific)
        if self.app_instance.instrument_model_var.get() == "N9342CN":
            high_sensitivity_str = self.app_instance.instrument.query(":POWer:HSENsitive?").strip()
            if high_sensitivity_str:
                self.app_instance.high_sensitivity_on_var.set(high_sensitivity_str.upper() == "ON")
                debug_log(f"Queried High Sensitivity State: {high_sensitivity_str}",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
        else:
            self.app_instance.high_sensitivity_on_var.set(False) # Default to False if not N9342CN
            debug_log("High Sensitivity query skipped for non-N9342CN model.",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


        self.console_print_func("✅ Instrument settings queried successfully. All up to date!")
        debug_log("Instrument settings queried successfully. UI updated!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)


    def _update_connection_status_ui(self):
        """
        Function Description:
        Updates the UI elements related to the instrument connection status.
        Enables/disables buttons and sets the connection status label text
        based on the `app_instance.is_connected` BooleanVar.

        Inputs:
            None.

        Process:
            1. Retrieves the current connection status from `app_instance.is_connected`.
            2. Updates the `instrument_connection_status_var` text.
            3. Configures the state (enabled/disabled) of relevant buttons
               (Connect, Disconnect, Apply Settings, Initialize, Query Settings).
            4. Sets the text color of the status label based on connection state.

        Outputs:
            None. Modifies GUI element states and text.
        """
        current_function = inspect.currentframe().f_code.co_name
        is_connected = self.app_instance.is_connected.get()
        debug_log(f"Updating connection status UI. Connected: {is_connected}. Version: {self.current_version}.",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if is_connected:
            self.app_instance.instrument_connection_status_var.set("Connected")
            self.connection_status_label.config(style='Green.TLabel.Value') # Assuming 'Green.TLabel.Value' style exists
            # Enable buttons for connected state
            self.master.winfo_children()[1].winfo_children()[3].config(state=tk.DISABLED) # Connect button
            self.master.winfo_children()[1].winfo_children()[4].config(state=tk.NORMAL) # Disconnect button
            # Enable settings buttons
            self.master.winfo_children()[2].winfo_children()[12].config(state=tk.NORMAL) # Apply Settings
            self.master.winfo_children()[2].winfo_children()[13].config(state=tk.NORMAL) # Initialize Instrument
            self.master.winfo_children()[2].winfo_children()[14].config(state=tk.NORMAL) # Query Settings
            debug_log("UI updated to 'Connected' state. Buttons enabled!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.app_instance.instrument_connection_status_var.set("Disconnected")
            self.connection_status_label.config(style='Red.TLabel.Value') # Assuming 'Red.TLabel.Value' style exists
            # Disable buttons for disconnected state
            self.master.winfo_children()[1].winfo_children()[3].config(state=tk.NORMAL) # Connect button
            self.master.winfo_children()[1].winfo_children()[4].config(state=tk.DISABLED) # Disconnect button
            # Disable settings buttons
            self.master.winfo_children()[2].winfo_children()[12].config(state=tk.DISABLED) # Apply Settings
            self.master.winfo_children()[2].winfo_children()[13].config(state=tk.DISABLED) # Initialize Instrument
            self.master.winfo_children()[2].winfo_children()[14].config(state=tk.DISABLED) # Query Settings
            debug_log("UI updated to 'Disconnected' state. Buttons disabled!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

    def _on_resource_selected(self, event):
        """
        Function Description:
        Handles the event when a VISA resource is selected from the combobox.
        Updates the `selected_visa_resource_var` in the `app_instance`.

        Inputs:
            event (tk.Event): The event object.

        Process:
            1. Retrieves the currently selected value from the combobox.
            2. Sets the `app_instance.selected_visa_resource_var` to this value.
            3. Logs the selection.

        Outputs:
            None. Updates application state.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.resource_combobox.get()
        self.app_instance.selected_visa_resource_var.set(selected_resource)
        debug_log(f"VISA resource selected: {selected_resource}. Choice made!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

    def _on_tab_selected(self, event):
        """
        Function Description:
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.
        For the Instrument tab, we update the connection status UI and potentially query settings.

        Inputs:
            event (tk.Event): The event object.

        Process:
            1. Checks if the currently selected tab in the PARENT notebook is the Instrument tab itself.
            2. If so, updates the connection status UI and potentially queries settings.
            3. Calls the `_on_parent_tab_selected` method of the main app instance if it exists.

        Outputs:
            None. Updates GUI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument Child Connection Tab selected. Version: {self.current_version}. Time to shine!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Check if the currently selected tab in the PARENT notebook is the Instrument tab itself
        # This is crucial to prevent _on_tab_selected from firing when other top-level tabs are selected
        # and only run its logic when the Instrument tab is the active one.
        selected_parent_tab = self.app_instance.notebook.nametowidget(self.app_instance.notebook.select())
        if selected_parent_tab == self.master.master: # self.master is the child_notebook, self.master.master is the main_app.notebook
            self.app_instance.after(0, self._update_connection_status_ui)
            if self.app_instance.is_connected.get():
                self.app_instance.after(0, self._query_settings_and_info)

        # Propagate the tab selected event to the main app's parent tab handler
        # This will trigger ASCII art creation to display ASCII art when the parent tab is selected.
        if hasattr(self.app_instance, '_on_parent_tab_selected'):
            self.app_instance._on_parent_tab_selected(event)
