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
# Version 20250803.1143.0 (Fixed ModuleNotFoundError: No module named 'src.instrument_logic' by correcting the import path to instrument_logic.)

current_version = "20250803.1143.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1143 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import inspect

# Updated imports for new logging functions
from src.debug_logic import debug_log, log_visa_command
from src.console_logic import console_log

# Import instrument connection/initialization/query/apply logic
# Corrected import path for instrument_logic
from tabs.Instrument.instrument_logic import apply_settings_logic, disconnect_instrument_logic, connect_instrument_logic, query_current_settings_logic

# Import utility functions for VISA operations
from tabs.Instrument.utils_instrument_connection import list_visa_resources
from tabs.Instrument.utils_instrument_initialize import initialize_instrument
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings

# Import config manager for default/last used settings
from src.settings_and_config.restore_settings_logic import restore_default_settings_logic, restore_last_used_settings_logic

class InstrumentTab(ttk.Frame):
    # Function Description:
    # Initializes the InstrumentTab, setting up the GUI components for instrument connection,
    # settings display, and actions like refreshing devices, applying settings, and
    # restoring default/last used configurations.
    #
    # Inputs:
    # - parent: The parent widget (usually a ttk.Notebook tab).
    # - app_instance: The main application instance, used for accessing shared resources
    #                 like the instrument object, console, and debug logging functions.
    #
    # Process:
    # 1. Calls the parent class's __init__ method.
    # 2. Stores the app_instance for later use.
    # 3. Initializes Tkinter variables for UI elements (e.g., connection status, settings).
    # 4. Calls _create_widgets to build the UI.
    # 5. Calls _initialize_instrument to set up the initial instrument state.
    #
    # Outputs:
    # None directly, but sets up the GUI and initial instrument state.
    # (2025/08/03) Change: Updated docstring based on new requirements.
    def __init__(self, parent, app_instance, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing InstrumentTab. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        super().__init__(parent, *args, **kwargs)
        self.app_instance = app_instance
        self.instrument = None
        self.rm = None # Resource Manager
        self.visa_resources = [] # To store discovered VISA resources

        # Tkinter variables for displaying status and settings
        self.connection_status_var = tk.StringVar(value="Disconnected")
        self.resource_selected_var = tk.StringVar(value="")
        self.center_freq_var = tk.StringVar(value="N/A")
        self.span_var = tk.StringVar(value="N/A")
        self.rbw_var = tk.StringVar(value="N/A")
        self.ref_level_var = tk.StringVar(value="N/A")
        self.preamp_on_var = tk.BooleanVar(value=False)
        self.trace_mode_var = tk.StringVar(value="N/A")
        self.trace_avg_count_var = tk.StringVar(value="N/A")
        self.det_mode_var = tk.StringVar(value="N/A")
        self.vbw_var = tk.StringVar(value="N/A")
        self.sweep_time_var = tk.StringVar(value="N/A")
        self.input_attenuation_var = tk.StringVar(value="N/A")

        self._create_widgets()
        self._initialize_instrument() # Perform initial device discovery and connection check

    def _create_widgets(self):
        # Function Description:
        # Creates and arranges all the Tkinter widgets for the InstrumentTab.
        # This includes sections for connection management, current settings display,
        # and action buttons (Refresh, Connect/Disconnect, Apply Settings, Restore Defaults/Last Used).
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Sets up the main grid configuration.
        # 2. Creates a LabelFrame for "Instrument Connection".
        # 3. Adds widgets for resource selection (Combobox), Refresh, and Connect/Disconnect buttons.
        # 4. Creates a LabelFrame for "Current Instrument Settings" to display queried values.
        # 5. Populates this frame with Labels for various settings (Freq, Span, RBW, etc.).
        # 6. Creates a Frame for action buttons (Apply Settings, Restore Defaults, Restore Last Used).
        # 7. Binds the _on_tab_selected method to the notebook tab selection event.
        #
        # Outputs:
        # None directly, but populates the `self` (InstrumentTab) with all its GUI elements.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for InstrumentTab. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Connection frame
        self.grid_rowconfigure(1, weight=1) # Settings display
        self.grid_rowconfigure(2, weight=0) # Action buttons

        # Connection Frame
        connection_frame = ttk.LabelFrame(self, text="Instrument Connection", padding="10")
        connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        connection_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(connection_frame, text="VISA Resource:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.resource_combobox = ttk.Combobox(connection_frame, textvariable=self.resource_selected_var, state="readonly")
        self.resource_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        self.refresh_button = ttk.Button(connection_frame, text="Refresh Devices", command=self._refresh_devices)
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        self.connect_button = ttk.Button(connection_frame, text="Connect", style="Green.TButton", command=self._toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=5, pady=5)
        self.connect_button.config(state=tk.DISABLED) # Start disabled until resources are found

        ttk.Label(connection_frame, text="Status:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(connection_frame, textvariable=self.connection_status_var, foreground="blue").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Current Instrument Settings Display Frame
        settings_frame = ttk.LabelFrame(self, text="Current Instrument Settings", padding="10")
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        settings_frame.grid_columnconfigure(1, weight=1)
        settings_frame.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(settings_frame, text="Center Frequency:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.center_freq_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, text="Span:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.span_var).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

        row_idx += 1
        ttk.Label(settings_frame, text="RBW:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.rbw_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, text="Ref Level:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.ref_level_var).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

        row_idx += 1
        ttk.Label(settings_frame, text="Preamplifier:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(settings_frame, textvariable=tk.StringVar(value="On" if self.preamp_on_var.get() else "Off"),
                        variable=self.preamp_on_var, state=tk.DISABLED).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, text="Trace Mode:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.trace_mode_var).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

        row_idx += 1
        ttk.Label(settings_frame, text="Trace Avg Count:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.trace_avg_count_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, text="Detector Mode:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.det_mode_var).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

        row_idx += 1
        ttk.Label(settings_frame, text="VBW:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.vbw_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, text="Sweep Time:").grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.sweep_time_var).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

        row_idx += 1
        ttk.Label(settings_frame, text="Input Attenuation:").grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_frame, textvariable=self.input_attenuation_var).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")

        # Action Buttons Frame
        action_buttons_frame = ttk.Frame(self, padding="10")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1,2), weight=1)

        self.apply_settings_button = ttk.Button(action_buttons_frame, text="Apply Settings", command=self._apply_settings, state=tk.DISABLED)
        self.apply_settings_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.restore_default_settings_button = ttk.Button(action_buttons_frame, text="Restore Default Settings", command=self._restore_default_settings, state=tk.DISABLED)
        self.restore_default_settings_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.restore_last_used_settings_button = ttk.Button(action_buttons_frame, text="Restore Last Used Settings", command=self._restore_last_used_settings, state=tk.DISABLED)
        self.restore_last_used_settings_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")


        # Bind the tab selection event to refresh data
        # Assuming the parent of this tab is a ttk.Notebook
        if self.master and hasattr(self.master, 'bind'):
            self.master.bind("<<NotebookTabChanged>>", self._on_tab_selected)


    def _on_tab_selected(self, event):
        # Function Description:
        # Handles the event when this tab is selected within its parent notebook.
        # It's responsible for ensuring the UI reflects the current instrument state
        # (connected/disconnected) and for querying current settings if connected.
        #
        # Inputs:
        # - event: The Tkinter event object (<<NotebookTabChanged>>).
        #
        # Process:
        # 1. Checks if the currently selected tab is this `InstrumentTab` instance.
        # 2. If it is, logs the event.
        # 3. Calls `_update_ui_elements_visibility` to set button and display states.
        # 4. If an instrument is connected, initiates a thread to query and display
        #    the current instrument settings to ensure the UI is up-to-date.
        #
        # Outputs:
        # None. Updates the GUI state.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        selected_tab = self.master.tab(self.master.select(), "text")
        if selected_tab == "Connection": # Ensure this matches the tab's display text in the notebook
            debug_log(f"Instrument Connection Tab selected. Updating UI and querying settings if connected. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)
            self._update_ui_elements_visibility(self.instrument is not None, self.visa_resources)
            if self.instrument:
                # Query current settings when tab is selected and instrument is connected
                self._query_settings_from_instrument()
        else:
            debug_log(f"Another tab was selected: {selected_tab}. Instrument Connection Tab remains in background. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)

    def _initialize_instrument(self):
        # Function Description:
        # Initiates a background thread to discover VISA resources. This prevents the
        # GUI from freezing during the resource discovery process.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the start of the initialization process.
        # 2. Creates and starts a new thread targeting `_refresh_devices_thread`.
        #
        # Outputs:
        # None. The actual resource discovery and UI update happen in the thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing instrument in background. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        threading.Thread(target=self._refresh_devices_thread, daemon=True).start()

    def _refresh_devices(self):
        # Function Description:
        # Public method to trigger the refresh of VISA devices, typically called
        # when the "Refresh Devices" button is pressed.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the refresh request.
        # 2. Starts a new background thread `_refresh_devices_thread` to perform
        #    the actual resource listing to avoid GUI freezing.
        #
        # Outputs:
        # None. The refresh process runs in a separate thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        console_log("🔄 Refreshing VISA devices...")
        debug_log(f"Refresh devices button clicked. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        threading.Thread(target=self._refresh_devices_thread, daemon=True).start()

    def _refresh_devices_thread(self):
        # Function Description:
        # Worker thread function to list available VISA resources. Updates the
        # GUI combobox with the discovered resources and enables/disables the
        # connect button accordingly.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Disables UI elements to prevent user interaction during refresh.
        # 2. Calls `list_visa_resources` utility function.
        # 3. Updates `self.visa_resources` and `self.resource_combobox` with results.
        # 4. Enables/disables the connect button based on whether resources were found.
        # 5. Re-enables UI elements.
        # 6. Updates connection status message.
        #
        # Outputs:
        # None. Updates GUI elements via `self.app_instance.after`.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting device refresh thread. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

        # Disable UI elements during refresh
        self.app_instance.after(0, lambda: self.refresh_button.config(state=tk.DISABLED))
        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.DISABLED))
        self.app_instance.after(0, lambda: self.resource_combobox.config(state=tk.DISABLED))

        resources = list_visa_resources(self.app_instance.console_log_func, self.app_instance.debug_log_func)
        self.visa_resources = resources
        resource_found = bool(resources)

        self.app_instance.after(0, lambda: self.resource_combobox.set("")) # Clear current selection
        self.app_instance.after(0, lambda: self.resource_combobox.config(values=resources))

        if resource_found:
            self.app_instance.after(0, lambda: self.resource_selected_var.set(resources[0])) # Select first by default
            self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
            self.app_instance.after(0, lambda: console_log("✅ Devices refreshed. Select a resource and connect."))
        else:
            self.app_instance.after(0, lambda: self.connect_button.config(state=tk.DISABLED))
            self.app_instance.after(0, lambda: console_log("⚠️ No VISA devices found. Ensure instrument is connected and drivers are installed."))

        self.app_instance.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))
        self.app_instance.after(0, lambda: self.resource_combobox.config(state="readonly" if resource_found else tk.DISABLED))

        # Update UI visibility based on whether resources were found
        self.app_instance.after(0, lambda: self._update_ui_elements_visibility(self.instrument is not None, resources))

        debug_log(f"Device refresh thread finished. Resources found: {resource_found}. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _on_resource_selected(self, event):
        # Function Description:
        # Event handler for when a resource is selected in the combobox.
        # It enables the connect button if a resource is actually selected.
        #
        # Inputs:
        # - event: The Tkinter event object (<<ComboboxSelected>>).
        #
        # Process:
        # 1. Logs the selected resource.
        # 2. Enables the connect button if a resource is selected.
        #
        # Outputs:
        # None. Updates the connect button state.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.resource_selected_var.get()
        debug_log(f"Resource selected: {selected_resource}. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        if selected_resource:
            self.connect_button.config(state=tk.NORMAL)
        self._update_ui_elements_visibility(self.instrument is not None, self.visa_resources)

    def _toggle_connection(self):
        # Function Description:
        # Toggles the instrument connection state (connects if disconnected, disconnects if connected).
        # It initiates a separate thread for the connection/disconnection process to prevent GUI blocking.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the connection toggle attempt.
        # 2. Determines current connection state.
        # 3. Disables the connect/disconnect button during the process.
        # 4. Starts a new thread (`_toggle_connection_thread`) to handle the actual connection logic.
        #
        # Outputs:
        # None. The connection state change and UI updates occur within the thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Toggle connection button clicked. Current instrument state: {self.instrument is not None}. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        # Disable button during operation
        self.connect_button.config(state=tk.DISABLED)
        threading.Thread(target=self._toggle_connection_thread, daemon=True).start()

    def _toggle_connection_thread(self):
        # Function Description:
        # Worker thread function that handles the actual connection or disconnection of the instrument.
        # It calls the appropriate logic functions (`connect_instrument_logic` or `disconnect_instrument_logic`)
        # and updates the GUI based on the outcome.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. If currently connected, attempts to disconnect the instrument using `disconnect_instrument_logic`.
        #    If successful, clears settings display and updates UI.
        # 2. If currently disconnected, attempts to connect to the selected resource using `connect_instrument_logic`.
        #    If successful, initializes the instrument, queries settings, and updates UI.
        # 3. Handles PyVISA errors during connection/disconnection.
        # 4. Re-enables the connect/disconnect button and updates its text/style.
        #
        # Outputs:
        # None. Updates `self.instrument` and various GUI elements via `self.app_instance.after`.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Connection toggle thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

        if self.instrument:
            # Disconnect
            debug_log("Attempting to disconnect instrument. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)
            success = disconnect_instrument_logic(self.instrument, self.app_instance)
            if success:
                self.instrument = None
                self.app_instance.instrument = None # Update global instrument reference
                self.app_instance.after(0, self._clear_settings_display)
                self.app_instance.after(0, lambda: self.connection_status_var.set("Disconnected"))
                self.app_instance.after(0, lambda: self.resource_combobox.config(state="readonly")) # Re-enable combobox after disconnect
                self.app_instance.after(0, lambda: self._update_ui_elements_visibility(False, self.visa_resources))
        else:
            # Connect
            selected_resource = self.resource_selected_var.get()
            if not selected_resource:
                self.app_instance.after(0, lambda: console_log("❌ No VISA resource selected. Please select one."))
                debug_log("No VISA resource selected for connection. Aborting. Version: {current_version}",
                            file=f"{__file__} - {current_version}",
                            function=current_function)
                self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL)) # Re-enable button
                self.app_instance.after(0, lambda: self._update_ui_elements_visibility(False, self.visa_resources))
                return

            self.app_instance.after(0, lambda: self.connection_status_var.set("Connecting..."))
            debug_log(f"Attempting to connect to {selected_resource}. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)

            # Use connect_instrument_logic
            rm, inst = connect_instrument_logic(selected_resource, self.app_instance)

            if inst:
                self.instrument = inst
                self.rm = rm
                self.app_instance.instrument = inst # Update global instrument reference
                self.app_instance.rm = rm # Update global resource manager reference
                self.app_instance.after(0, lambda: self.connection_status_var.set("Connected"))
                self.app_instance.after(0, lambda: self.resource_combobox.config(state=tk.DISABLED)) # Disable combobox when connected
                self.app_instance.after(0, lambda: self._update_ui_elements_visibility(True, self.visa_resources))

                # After successful connection, initialize instrument and query settings
                self.app_instance.after(0, lambda: console_log("⚙️ Initializing instrument with default settings..."))
                threading.Thread(target=self._initialize_instrument_thread, daemon=True).start()
            else:
                self.app_instance.after(0, lambda: self.connection_status_var.set("Disconnected"))
                self.app_instance.after(0, lambda: console_log("❌ Connection failed."))
                self.app_instance.after(0, lambda: self._update_ui_elements_visibility(False, self.visa_resources))

        # Re-enable the button after the operation is complete
        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
        debug_log(f"Connection toggle thread finished. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _initialize_instrument_thread(self):
        # Function Description:
        # Worker thread function to initialize the connected instrument.
        # It calls the `initialize_instrument` utility and then queries settings
        # if initialization is successful.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the start of initialization.
        # 2. Calls `initialize_instrument` with the current instrument object and logging functions.
        # 3. If initialization succeeds, it then calls `_query_settings_from_instrument`
        #    to refresh the displayed settings.
        #
        # Outputs:
        # None. Updates GUI via `_query_settings_from_instrument`.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Instrument initialization thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        if self.instrument:
            initialized = initialize_instrument(
                self.instrument,
                self.app_instance.console_log_func,
                self.app_instance.debug_log_func
            )
            if initialized:
                self.app_instance.after(0, lambda: console_log("✅ Instrument initialized. Querying settings..."))
                self._query_settings_from_instrument() # Query settings after initialization
            else:
                self.app_instance.after(0, lambda: console_log("❌ Instrument initialization failed."))
        debug_log(f"Instrument initialization thread finished. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _apply_settings(self):
        # Function Description:
        # Initiates a thread to apply settings to the connected instrument.
        # This function acts as a wrapper to prevent GUI freezing.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the attempt to apply settings.
        # 2. Disables the "Apply Settings" button to prevent multiple clicks.
        # 3. Starts a new thread (`_apply_settings_thread`) to handle the actual logic.
        #
        # Outputs:
        # None. The actual setting application happens in the thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        console_log("🛠️ Applying settings to instrument...")
        debug_log(f"Apply settings button clicked. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        self.apply_settings_button.config(state=tk.DISABLED) # Disable button during operation
        threading.Thread(target=self._apply_settings_thread, daemon=True).start()

    def _apply_settings_thread(self):
        # Function Description:
        # Worker thread function that applies the current settings from the GUI
        # (e.g., from config) to the connected instrument.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Checks if an instrument is connected.
        # 2. Calls `apply_settings_logic` with the instrument and app instance.
        # 3. After applying, requeries the settings to update the display.
        # 4. Re-enables the "Apply Settings" button.
        #
        # Outputs:
        # None. Updates the instrument settings and GUI display.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Apply settings thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        if self.instrument:
            # Placeholder: In a real application, you'd get the settings from your config
            # or other UI elements and pass them to apply_settings_logic.
            # For now, we'll assume apply_settings_logic gets them from a shared config.
            success = apply_settings_logic(self.instrument, self.app_instance)
            if success:
                self.app_instance.after(0, lambda: console_log("✅ Settings applied successfully. Re-querying..."))
                self._query_settings_from_instrument() # Re-query to update display
            else:
                self.app_instance.after(0, lambda: console_log("❌ Failed to apply settings."))
        else:
            self.app_instance.after(0, lambda: console_log("⚠️ No instrument connected to apply settings."))

        self.app_instance.after(0, lambda: self.apply_settings_button.config(state=tk.NORMAL)) # Re-enable button
        debug_log(f"Apply settings thread finished. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _query_settings_from_instrument(self):
        # Function Description:
        # Queries the current settings from the connected instrument and updates
        # the corresponding Tkinter variables, which in turn update the GUI display.
        # This runs in a separate thread.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Checks if an instrument is connected.
        # 2. Calls `query_current_instrument_settings` to retrieve values.
        # 3. Updates Tkinter StringVars/BooleanVar with the queried data using `app_instance.after(0, ...)`,
        #    ensuring GUI updates happen on the main thread.
        # 4. Logs the process.
        #
        # Outputs:
        # None. Updates GUI display elements.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Querying settings from instrument. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

        if not self.instrument:
            self.app_instance.after(0, lambda: console_log("⚠️ No instrument connected to query settings."))
            debug_log("No instrument connected to query settings. Aborting. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)
            self.app_instance.after(0, self._clear_settings_display)
            return

        threading.Thread(target=self._query_settings_from_instrument_thread, daemon=True).start()

    def _query_settings_from_instrument_thread(self):
        # Function Description:
        # Worker thread function for querying current instrument settings.
        # Fetches various settings from the instrument and updates the UI
        # via `app_instance.after` calls to ensure thread safety for GUI updates.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Calls `query_current_instrument_settings` to get common settings.
        # 2. Queries additional settings like Ref Level, Preamplifier, Trace Mode, etc., individually.
        # 3. Updates the Tkinter variables on the main thread.
        # 4. Handles errors during querying.
        #
        # Outputs:
        # None. Updates the GUI display.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Query settings thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        try:
            center_freq_mhz, span_mhz, rbw_hz = query_current_instrument_settings(
                self.instrument,
                self.app_instance.console_log_func,
                self.app_instance.debug_log_func
            )

            self.app_instance.after(0, lambda: self.center_freq_var.set(f"{center_freq_mhz:.3f} MHz" if center_freq_mhz is not None else "N/A"))
            self.app_instance.after(0, lambda: self.span_var.set(f"{span_mhz:.3f} MHz" if span_mhz is not None else "N/A"))
            self.app_instance.after(0, lambda: self.rbw_var.set(f"{rbw_hz / 1000:.1f} kHz" if rbw_hz is not None else "N/A"))

            # Query Reference Level
            ref_level_str = query_current_settings_logic(self.instrument, "REF_LEVEL", self.app_instance) # Use the logic function
            if ref_level_str:
                self.app_instance.after(0, lambda: self.ref_level_var.set(f"{float(ref_level_str):.2f} dBm"))
                debug_log(f"Queried Ref Level: {ref_level_str}. Good to go!",
                            file=f"{__file__} - {current_version}",
                            function=current_function)

            # Query Preamplifier State
            preamp_str = query_current_settings_logic(self.instrument, "PREAMP_STATE", self.app_instance) # Use the logic function
            if preamp_str:
                self.app_instance.after(0, lambda: self.preamp_on_var.set(preamp_str.strip().upper() == "ON"))
                self.app_instance.after(0, lambda: self.preamp_on_var_display.set("On" if self.preamp_on_var.get() else "Off"))
                debug_log(f"Queried Preamp State: {preamp_str.strip()}. Nice!",
                            file=f"{__file__} - {current_version}",
                            function=current_function)

            # Query Trace Mode
            trace_mode_str = query_current_settings_logic(self.instrument, "TRACE_MODE", self.app_instance)
            if trace_mode_str:
                self.app_instance.after(0, lambda: self.trace_mode_var.set(trace_mode_str.strip()))

            # Query Trace Average Count
            trace_avg_count_str = query_current_settings_logic(self.instrument, "TRACE_AVG_COUNT", self.app_instance)
            if trace_avg_count_str:
                self.app_instance.after(0, lambda: self.trace_avg_count_var.set(trace_avg_count_str.strip()))

            # Query Detector Mode
            det_mode_str = query_current_settings_logic(self.instrument, "DETECTOR_MODE", self.app_instance)
            if det_mode_str:
                self.app_instance.after(0, lambda: self.det_mode_var.set(det_mode_str.strip()))

            # Query VBW
            vbw_str = query_current_settings_logic(self.instrument, "VBW", self.app_instance)
            if vbw_str:
                self.app_instance.after(0, lambda: self.vbw_var.set(f"{float(vbw_str):.1f} Hz"))

            # Query Sweep Time
            sweep_time_str = query_current_settings_logic(self.instrument, "SWEEP_TIME", self.app_instance)
            if sweep_time_str:
                self.app_instance.after(0, lambda: self.sweep_time_var.set(f"{float(sweep_time_str):.2f} S"))

            # Query Input Attenuation
            input_attenuation_str = query_current_settings_logic(self.instrument, "INPUT_ATTENUATION", self.app_instance)
            if input_attenuation_str:
                self.app_instance.after(0, lambda: self.input_attenuation_var.set(f"{float(input_attenuation_str):.1f} dB"))


            self.app_instance.after(0, lambda: console_log("✅ Instrument settings queried and displayed."))
            debug_log("Settings queried from instrument. UI updated! Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)
        except Exception as e:
            self.app_instance.after(0, lambda: console_log(f"❌ Error querying instrument settings: {e}. What a pain!"))
            debug_log(f"Error in _query_settings_from_instrument_thread: {e}. Fucking hell!",
                        file=f"{__file__} - {current_version}",
                        function=current_function)
        finally:
            debug_log(f"Query settings thread finished. Version: {current_version}",
                        file=f"{__file__} - {current_version}",
                        function=current_function)

    def _clear_settings_display(self):
        # Function Description:
        # Resets all displayed instrument settings to "N/A".
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Sets the value of all Tkinter StringVar and BooleanVar associated
        #    with instrument settings back to their default "N/A" or False states.
        #
        # Outputs:
        # None. Updates GUI display.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Clearing settings display. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        self.center_freq_var.set("N/A")
        self.span_var.set("N/A")
        self.rbw_var.set("N/A")
        self.ref_level_var.set("N/A")
        self.preamp_on_var.set(False)
        self.trace_mode_var.set("N/A")
        self.trace_avg_count_var.set("N/A")
        self.det_mode_var.set("N/A")
        self.vbw_var.set("N/A")
        self.sweep_time_var.set("N/A")
        self.input_attenuation_var.set("N/A")


    def _restore_default_settings(self):
        # Function Description:
        # Initiates a thread to restore default instrument settings.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the attempt to restore defaults.
        # 2. Disables relevant buttons.
        # 3. Starts `_restore_default_settings_thread`.
        #
        # Outputs:
        # None. The restoration happens in a thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        console_log("🔄 Restoring default settings...")
        debug_log(f"Restore default settings button clicked. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        self.restore_default_settings_button.config(state=tk.DISABLED)
        self.restore_last_used_settings_button.config(state=tk.DISABLED)
        threading.Thread(target=self._restore_default_settings_thread, daemon=True).start()

    def _restore_default_settings_thread(self):
        # Function Description:
        # Worker thread function to apply default settings to the instrument.
        # Calls the `restore_default_settings_logic` and updates the UI.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Checks for instrument connection.
        # 2. Calls `restore_default_settings_logic`.
        # 3. Requeries settings to update the display.
        # 4. Re-enables buttons.
        #
        # Outputs:
        # None. Updates instrument settings and GUI.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restore default settings thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        if self.instrument:
            success = restore_default_settings_logic(self.instrument, self.app_instance.console_log_func, self.app_instance.debug_log_func)
            if success:
                self.app_instance.after(0, lambda: console_log("✅ Default settings restored successfully."))
                self._query_settings_from_instrument() # Re-query to update display
            else:
                self.app_instance.after(0, lambda: console_log("❌ Failed to restore default settings."))
        else:
            self.app_instance.after(0, lambda: console_log("⚠️ No instrument connected to restore settings."))
        self.app_instance.after(0, lambda: self.restore_default_settings_button.config(state=tk.NORMAL))
        self.app_instance.after(0, lambda: self.restore_last_used_settings_button.config(state=tk.NORMAL))
        debug_log(f"Restore default settings thread finished. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _restore_last_used_settings(self):
        # Function Description:
        # Initiates a thread to restore the last used instrument settings.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Logs the attempt.
        # 2. Disables relevant buttons.
        # 3. Starts `_restore_last_used_settings_thread`.
        #
        # Outputs:
        # None. The restoration happens in a thread.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        console_log("🔄 Restoring last used settings...")
        debug_log(f"Restore last used settings button clicked. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        self.restore_default_settings_button.config(state=tk.DISABLED)
        self.restore_last_used_settings_button.config(state=tk.DISABLED)
        threading.Thread(target=self._restore_last_used_settings_thread, daemon=True).start()

    def _restore_last_used_settings_thread(self):
        # Function Description:
        # Worker thread function to apply the last used settings to the instrument.
        # Calls the `restore_last_used_settings_logic` and updates the UI.
        #
        # Inputs:
        # None
        #
        # Process:
        # 1. Checks for instrument connection.
        # 2. Calls `restore_last_used_settings_logic`.
        # 3. Requeries settings to update the display.
        # 4. Re-enables buttons.
        #
        # Outputs:
        # None. Updates instrument settings and GUI.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restore last used settings thread started. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        if self.instrument:
            success = restore_last_used_settings_logic(self.instrument, self.app_instance.console_log_func, self.app_instance.debug_log_func)
            if success:
                self.app_instance.after(0, lambda: console_log("✅ Last used settings restored successfully."))
                self._query_settings_from_instrument() # Re-query to update display
            else:
                self.app_instance.after(0, lambda: console_log("❌ Failed to restore last used settings."))
        else:
            self.app_instance.after(0, lambda: console_log("⚠️ No instrument connected to restore settings."))
        self.app_instance.after(0, lambda: self.restore_default_settings_button.config(state=tk.NORMAL))
        self.app_instance.after(0, lambda: self.restore_last_used_settings_button.config(state=tk.NORMAL))
        debug_log(f"Restore last used settings thread finished. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)

    def _update_ui_elements_visibility(self, is_connected, resource_found_list):
        # Function Description:
        # Adjusts the state (enabled/disabled) of various UI elements based on
        # whether an instrument is connected and if any VISA resources were found.
        #
        # Inputs:
        # - is_connected (bool): True if an instrument is currently connected, False otherwise.
        # - resource_found_list (list): List of discovered VISA resources.
        #
        # Process:
        # 1. Updates the connection button's text and style.
        # 2. Enables/disables the resource combobox and refresh button.
        # 3. Iterates through child widgets to enable/disable settings display
        #    and action buttons based on `is_connected` status.
        # 4. Ensures the connect button is enabled if resources are found, even if not connected.
        #
        # Outputs:
        # None. Modifies UI element states.
        # (2025/08/03) Change: Updated docstring based on new requirements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating UI visibility. Connected: {is_connected}, Resources found: {bool(resource_found_list)}. Version: {current_version}",
                    file=f"{__file__} - {current_version}",
                    function=current_function)
        resource_found = bool(resource_found_list)

        if is_connected:
            self.connect_button.config(text="Disconnect", style="Red.TButton")
            self.resource_combobox.config(state=tk.DISABLED) # Disable combobox when connected
            self.refresh_button.config(state=tk.DISABLED)

            # Enable settings display and action buttons
            for child in self.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Current Instrument Settings":
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.NORMAL)
                elif isinstance(child, ttk.Frame) and any(b.cget("text") == "Apply Settings" for b in child.winfo_children()):
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.NORMAL)
        else:
            self.connect_button.config(text="Connect", style="FlashingGray.TButton")
            self.resource_combobox.config(state="readonly" if resource_found else tk.DISABLED)
            self.refresh_button.config(state=tk.NORMAL)
            # Disable settings display and action buttons
            for child in self.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Current Instrument Settings":
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.DISABLED)
                elif isinstance(child, ttk.Frame) and any(b.cget("text") == "Apply Settings" for b in child.winfo_children()):
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.DISABLED)

        # Ensure the connect button is enabled if a resource is found, even if not connected
        if resource_found:
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.DISABLED)