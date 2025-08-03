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
# Version 20250803.1115.4 (Fixed argument mismatch for apply_settings_logic call.)

current_version = "20250803.1115.4" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1115 * 4 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os
import threading

# Import instrument control logic functions
from tabs.Instrument.utils_instrument_connection import list_visa_resources, connect_to_instrument, disconnect_instrument
from tabs.Instrument.utils_instrument_initialize import initialize_instrument
from tabs.Instrument.utils_instrument_query_settings import query_instrument_settings
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Import the logic functions from instrument_logic.py
from tabs.Instrument.instrument_logic import apply_settings_logic, disconnect_instrument_logic, connect_instrument_logic, query_current_settings_logic, restore_default_settings_logic, restore_last_used_settings_logic


class InstrumentTab(ttk.Frame):
    """
    Function Description:
    Manages the Instrument Connection tab in the GUI.
    Handles VISA resource discovery, instrument connection/disconnection,
    and displaying current instrument settings. It dynamically manages
    the visibility of UI elements based on connection state.

    Inputs:
        parent (ttk.Notebook): The parent notebook widget.
        app_instance (App): A reference to the main application instance.
        console_print_func (function): Function to print messages to the GUI console.
        style_obj (ttk.Style): The ttk.Style object for applying styles.

    Process:
        1. Initializes the Tkinter Frame.
        2. Stores references to the app instance, console print function, and style object.
        3. Calls `_create_widgets` to build the tab's UI.
        4. Binds the `_on_tab_selected` method to the tab's visibility event.

    Outputs:
        None. Initializes the InstrumentTab UI.
    """
    def __init__(self, parent, app_instance, console_print_func, **kwargs):
        # Explicitly filter style_obj from kwargs before passing to super().__init__
        style_obj = kwargs.pop('style_obj', None)
        super().__init__(parent, **kwargs)

        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style = style_obj # Store the style object

        # Get current file and function for debug_log
        self.current_file = os.path.basename(__file__)
        self.current_version = current_version # Use the module-level current_version

        debug_log(f"Initializing InstrumentTab. Version: {self.current_version}. Let's get this show on the road!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=inspect.currentframe().f_code.co_name)

        self._create_widgets()

        # Bind the tab selection event
        parent.bind("<<NotebookTabChanged>>", self._on_tab_selected)

    def _create_widgets(self):
        """
        Function Description:
        Creates and arranges all GUI widgets for the Instrument Connection tab.
        This includes frames for resource selection, connection control,
        instrument settings display, and action buttons.

        Inputs:
            None.

        Process:
            1. Configures the grid layout for the main frame.
            2. Creates and packs a frame for VISA resource selection,
                including a label, combobox for available resources,
                and a "Refresh Devices" button.
            3. Creates and packs a frame for connection control,
                including a connection status label and Connect/Disconnect button.
            4. Creates and packs a frame for instrument settings display,
                including labels for Center Freq, Span, RBW, VBW, Sweep Time,
                Preamplifier, and High Sensitivity.
            5. Creates and packs a frame for action buttons (Apply Settings, Initialize, Restore Defaults, Restore Last Used).
            6. Populates the combobox with initial available resources.

        Outputs:
            None. Populates the InstrumentTab with GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for InstrumentTab. Version: {self.current_version}. Building the interface!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Resource selection
        self.grid_rowconfigure(1, weight=0) # Connection control
        self.grid_rowconfigure(2, weight=1) # Instrument settings
        self.grid_rowconfigure(3, weight=0) # Action buttons

        # --- VISA Resource Selection ---
        resource_frame = ttk.LabelFrame(self, text="VISA Resource Selection", style='Dark.TLabelframe')
        resource_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        resource_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(resource_frame, text="Available Resources:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.resource_combobox = ttk.Combobox(resource_frame, textvariable=self.app_instance.selected_resource, state="readonly", style='TCombobox')
        self.resource_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.resource_combobox.bind("<<ComboboxSelected>>", self._on_resource_selected)

        self.refresh_button = ttk.Button(resource_frame, text="Refresh Devices", command=self._refresh_devices, style='Dark.TButton')
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5)

        # Populate the combobox with initial available resources
        self._refresh_devices()


        # --- Connection Control ---
        connection_frame = ttk.LabelFrame(self, text="Instrument Connection", style='Dark.TLabelframe')
        connection_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        connection_frame.grid_columnconfigure(0, weight=1)
        connection_frame.grid_columnconfigure(1, weight=1)

        self.connection_status_label = ttk.Label(connection_frame, text="Status: Disconnected 💀", foreground="red", style='Dark.TLabel')
        self.connection_status_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self._toggle_connection, style='FlashingGray.TButton')
        self.connect_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")


        # --- Instrument Settings Display ---
        settings_display_frame = ttk.LabelFrame(self, text="Current Instrument Settings", style='Dark.TLabelframe')
        settings_display_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        settings_display_frame.grid_columnconfigure(1, weight=1)
        settings_display_frame.grid_columnconfigure(3, weight=1)

        # Row 0: Instrument Info
        ttk.Label(settings_display_frame, text="Model:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_model, style='Dark.TLabel').grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Serial:", style='Dark.TLabel').grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_serial, style='Dark.TLabel').grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # Row 1: Firmware & Options
        ttk.Label(settings_display_frame, text="Firmware:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_firmware, style='Dark.TLabel').grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Options:", style='Dark.TLabel').grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_options, style='Dark.TLabel').grid(row=1, column=3, padx=5, pady=2, sticky="w")


        # Row 2: Center Freq & Span
        ttk.Label(settings_display_frame, text="Center Freq (Hz):", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.center_freq_hz_var, style='Dark.TLabel').grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Span (Hz):", style='Dark.TLabel').grid(row=2, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.span_hz_var, style='Dark.TLabel').grid(row=2, column=3, padx=5, pady=2, sticky="w")

        # Row 3: RBW & VBW
        ttk.Label(settings_display_frame, text="RBW (Hz):", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.rbw_hz_var, style='Dark.TLabel').grid(row=3, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="VBW (Hz):", style='Dark.TLabel').grid(row=3, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.vbw_hz_var, style='Dark.TLabel').grid(row=3, column=3, padx=5, pady=2, sticky="w")

        # Row 4: Sweep Time
        ttk.Label(settings_display_frame, text="Sweep Time (s):", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.sweep_time_s_var, style='Dark.TLabel').grid(row=4, column=1, padx=5, pady=2, sticky="w")

        # Row 5: Preamplifier & High Sensitivity
        ttk.Label(settings_display_frame, text="Preamplifier:", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.preamp_on_var, style='Dark.TLabel').grid(row=5, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="High Sensitivity:", style='Dark.TLabel').grid(row=5, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.high_sensitivity_var, style='Dark.TLabel').grid(row=5, column=3, padx=5, pady=2, sticky="w")


        # --- Action Buttons ---
        action_buttons_frame = ttk.Frame(self, style='Dark.TFrame')
        action_buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1,2,3), weight=1)

        ttk.Button(action_buttons_frame, text="Apply Settings", command=self._apply_settings, style='Dark.TButton').grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Initialize Instrument", command=self._initialize_instrument, style='Dark.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Restore Defaults", command=self._restore_default_settings, style='Dark.TButton').grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(action_buttons_frame, text="Restore Last Used", command=self._restore_last_used_settings, style='Dark.TButton').grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        debug_log(f"InstrumentTab widgets created. Ready to rock!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)


    def _refresh_devices(self):
        """
        Function Description:
        Discovers available VISA resources and updates the combobox.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables the refresh button.
            2. Starts a new thread to call `_refresh_devices_thread`.
            3. Re-enables the refresh button in the thread's completion.

        Outputs:
            None. Updates the `resource_combobox`.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Refreshing VISA devices. Version: {self.current_version}. Searching for instruments!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.refresh_button.config(state=tk.DISABLED)
        threading.Thread(target=self._refresh_devices_thread, daemon=True).start()

    def _refresh_devices_thread(self):
        """
        Function Description:
        Worker function for `_refresh_devices`. Lists VISA resources
        and updates the Tkinter variable for the combobox.

        Inputs:
            None.

        Process:
            1. Calls `list_visa_resources` to get available resources.
            2. Updates `self.app_instance.available_resources` and `self.resource_combobox['values']`
                on the main thread using `app_instance.after`.
            3. Selects the first resource if available, or clears the selection.
            4. Re-enables the refresh button on the main thread.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _refresh_devices_thread. Version: {self.current_version}. The hunt is on!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        resources = list_visa_resources(self.console_print_func)
        resource_names = [r for r in resources] # Convert to list of strings

        # Update Tkinter variables on the main thread
        self.app_instance.after(0, lambda: self.app_instance.available_resources.set(",".join(resource_names)))
        self.app_instance.after(0, lambda: self.resource_combobox.config(values=resource_names))

        if resource_names:
            # If a resource was previously selected and is still available, keep it selected.
            # Otherwise, select the first one.
            current_selection = self.app_instance.selected_resource.get()
            if current_selection and current_selection in resource_names:
                self.app_instance.after(0, lambda: self.resource_combobox.set(current_selection))
                debug_log(f"Retained previous selection: {current_selection}. Version: {self.current_version}. Smart move!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
            else:
                self.app_instance.after(0, lambda: self.resource_combobox.set(resource_names[0]))
                self.app_instance.after(0, lambda: self.app_instance.selected_resource.set(resource_names[0]))
                debug_log(f"Selected first available resource: {resource_names[0]}. Version: {self.current_version}. Fresh start!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
        else:
            self.app_instance.after(0, lambda: self.resource_combobox.set(""))
            self.app_instance.after(0, lambda: self.app_instance.selected_resource.set(""))
            debug_log(f"No VISA resources found. Version: {self.current_version}. This is a bummer!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

        self.app_instance.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))


    def _on_resource_selected(self, event):
        """
        Function Description:
        Handles the event when a new VISA resource is selected from the combobox.
        Updates the `selected_resource` Tkinter variable in the main app instance.

        Inputs:
            event (tkinter.Event): The event object.

        Process:
            1. Retrieves the currently selected value from the combobox.
            2. Updates `self.app_instance.selected_resource` with the new value.
            3. Logs the selection.

        Outputs:
            None. Updates application state.
        """
        current_function = inspect.currentframe().f_code.co_name
        selected_resource = self.resource_combobox.get()
        self.app_instance.selected_resource.set(selected_resource)
        debug_log(f"VISA resource selected: {selected_resource}. Version: {self.current_version}. Choice made!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)


    def _toggle_connection(self):
        """
        Function Description:
        Toggles the instrument connection status (connects if disconnected, disconnects if connected).
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables the connect button.
            2. Starts a new thread to call `_toggle_connection_thread`.
            3. Re-enables the connect button in the thread's completion.

        Outputs:
            None. Manages instrument connection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Toggling instrument connection. Version: {self.current_version}. Let's get connected (or disconnected)!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.connect_button.config(state=tk.DISABLED)
        threading.Thread(target=self._toggle_connection_thread, daemon=True).start()

    def _toggle_connection_thread(self):
        """
        Function Description:
        Worker function for `_toggle_connection`. Handles the actual
        connection/disconnection logic.

        Inputs:
            None.

        Process:
            1. Checks if the instrument is currently connected (`self.app_instance.inst`).
            2. If connected, calls `disconnect_instrument_logic`.
            3. If disconnected, calls `connect_instrument_logic` using the selected resource.
            4. Updates the main application's connection status via `app_instance.update_connection_status`.
            5. Re-enables the connect button on the main thread.
            6. If connected after the toggle, queries settings to update the display.

        Outputs:
            None. Manages instrument connection and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _toggle_connection_thread. Version: {self.current_version}. The connection dance begins!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if self.app_instance.inst:
            debug_log(f"Instrument is connected. Disconnecting. Version: {self.current_version}.",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            disconnect_instrument_logic(self.app_instance, self.console_print_func)
            self.app_instance.after(0, lambda: self.app_instance.update_connection_status(False, self.app_instance.scanning))
            self.app_instance.after(0, self._clear_settings_display) # Clear display on disconnect
        else:
            selected_resource = self.app_instance.selected_resource.get()
            if selected_resource:
                debug_log(f"Instrument is disconnected. Connecting to {selected_resource}. Version: {self.current_version}.",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
                # Corrected function call to connect_instrument_logic
                connect_success = connect_instrument_logic(self.app_instance, self.console_print_func)
                # app_instance.inst is now updated within connect_instrument_logic
                self.app_instance.after(0, lambda: self.app_instance.update_connection_status(connect_success, self.app_instance.scanning))
                if connect_success:
                    self.app_instance.after(0, self._query_settings_from_instrument) # Query settings on successful connect
            else:
                self.app_instance.after(0, lambda: self.console_print_func("❌ No VISA resource selected. Please select a device to connect."))
                debug_log(f"No VISA resource selected for connection. Version: {self.current_version}. What are we connecting to?!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)

        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))


    def _apply_settings(self):
        """
        Function Description:
        Applies the current settings from the GUI to the connected instrument.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables relevant buttons.
            2. Starts a new thread to call `_apply_settings_thread`.
            3. Re-enables buttons in the thread's completion.

        Outputs:
            None. Applies instrument settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Applying instrument settings. Version: {self.current_version}. Sending commands!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.connect_button.config(state=tk.DISABLED)
        # Add other buttons to disable if necessary
        threading.Thread(target=self._apply_settings_thread, daemon=True).start()

    def _apply_settings_thread(self):
        """
        Function Description:
        Worker function for `_apply_settings`. Handles the actual
        application of settings to the instrument.

        Inputs:
            None.

        Process:
            1. Checks if the instrument is connected.
            2. If connected, calls `apply_settings_logic` with relevant Tkinter variable values.
            3. Re-enables buttons on the main thread.

        Outputs:
            None. Applies settings and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _apply_settings_thread. Version: {self.current_version}. The instrument is listening!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if self.app_instance.inst:
            # Corrected call to apply_settings_logic - pass only app_instance and console_print_func
            apply_settings_logic(self.app_instance, self.console_print_func)
        else:
            self.app_instance.after(0, lambda: self.console_print_func("❌ Instrument not connected. Cannot apply settings."))
            debug_log(f"Instrument not connected. Cannot apply settings. Version: {self.current_version}. What a mess!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
        # Re-enable other buttons here


    def _initialize_instrument(self):
        """
        Function Description:
        Initializes the connected instrument to a known state.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables relevant buttons.
            2. Starts a new thread to call `_initialize_instrument_thread`.
            3. Re-enables buttons in the thread's completion.

        Outputs:
            None. Initializes instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing instrument. Version: {self.current_version}. Resetting to factory settings!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.connect_button.config(state=tk.DISABLED)
        # Add other buttons to disable if necessary
        threading.Thread(target=self._initialize_instrument_thread, daemon=True).start()

    def _initialize_instrument_thread(self):
        """
        Function Description:
        Worker function for `_initialize_instrument`. Handles the actual
        initialization of the instrument.

        Inputs:
            None.

        Process:
            1. Checks if the instrument is connected.
            2. If connected, calls `initialize_instrument`.
            3. Re-enables buttons on the main thread.

        Outputs:
            None. Initializes instrument and updates GUI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _initialize_instrument_thread. Version: {self.current_version}. Fresh start!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if self.app_instance.inst:
            # initialize_instrument expects specific parameters, not app_instance directly
            # We need to get these from app_instance's Tkinter variables
            ref_level_dbm = float(self.app_instance.reference_level_dbm_var.get())
            high_sensitivity_on = self.app_instance.high_sensitivity_var.get()
            preamp_on = self.app_instance.preamp_on_var.get()
            rbw_config_val = float(self.app_instance.rbw_hz_var.get()) # Assuming this is the desired RBW for initialization
            vbw_config_val = float(self.app_instance.vbw_hz_var.get()) # Assuming this is the desired VBW for initialization
            model_match = self.app_instance.instrument_model.get() # Get the connected instrument model

            initialize_instrument(
                self.app_instance.inst,
                ref_level_dbm,
                high_sensitivity_on,
                preamp_on,
                rbw_config_val,
                vbw_config_val,
                model_match,
                self.console_print_func
            )
            self.app_instance.after(0, self._query_settings_from_instrument) # Query settings after initialization
        else:
            self.app_instance.after(0, lambda: self.console_print_func("❌ Instrument not connected. Cannot initialize."))
            debug_log(f"Instrument not connected. Cannot initialize. Version: {self.current_version}. What a pain!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
        # Re-enable other buttons here


    def _restore_default_settings(self):
        """
        Function Description:
        Restores default settings to the GUI variables.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables relevant buttons.
            2. Starts a new thread to call `_restore_default_settings_thread`.
            3. Re-enables buttons in the thread's completion.

        Outputs:
            None. Restores GUI settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restoring default settings. Version: {self.current_version}. Back to basics!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.connect_button.config(state=tk.DISABLED)
        # Add other buttons to disable if necessary
        threading.Thread(target=self._restore_default_settings_thread, daemon=True).start()

    def _restore_default_settings_thread(self):
        """
        Function Description:
        Worker function for `_restore_default_settings`. Handles the actual
        restoration of default settings to the Tkinter variables.

        Inputs:
            None.

        Process:
            1. Calls `restore_default_settings_logic` to update Tkinter variables.
            2. If the instrument is connected, applies these settings to the instrument.
            3. Re-enables buttons on the main thread.

        Outputs:
            None. Restores settings and updates GUI/instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _restore_default_settings_thread. Version: {self.current_version}. The defaults are calling!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        restore_default_settings_logic(self.app_instance, self.console_print_func)
        if self.app_instance.inst:
            self.app_instance.after(0, self._apply_settings_thread) # Apply to instrument if connected
        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
        # Re-enable other buttons here


    def _restore_last_used_settings(self):
        """
        Function Description:
        Restores the last used settings to the GUI variables from config.ini.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables relevant buttons.
            2. Starts a new thread to call `_restore_last_used_settings_thread`.
            3. Re-enables buttons in the thread's completion.

        Outputs:
            None. Restores GUI settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restoring last used settings. Version: {self.current_version}. Back in time!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self.connect_button.config(state=tk.DISABLED)
        # Add other buttons to disable if necessary
        threading.Thread(target=self._restore_last_used_settings_thread, daemon=True).start()

    def _restore_last_used_settings_thread(self):
        """
        Function Description:
        Worker function for `_restore_last_used_settings`. Handles the actual
        restoration of last used settings to the Tkinter variables.

        Inputs:
            None.

        Process:
            1. Calls `restore_last_used_settings_logic` to update Tkinter variables.
            2. If the instrument is connected, applies these settings to the instrument.
            3. Re-enables buttons on the main thread.

        Outputs:
            None. Restores settings and updates GUI/instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _restore_last_used_settings_thread. Version: {self.current_version}. Remembering the past!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        restore_last_used_settings_logic(self.app_instance, self.console_print_func)
        if self.app_instance.inst:
            self.app_instance.after(0, self._apply_settings_thread) # Apply to instrument if connected
        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
        # Re-enable other buttons here


    def _query_settings_from_instrument(self):
        """
        Function Description:
        Queries the current settings from the connected instrument and updates
        the corresponding Tkinter variables in the GUI.

        Inputs:
            None.

        Process:
            1. Checks if the instrument is connected.
            2. If connected, calls `query_instrument_settings` to retrieve values.
            3. Updates `self.app_instance`'s Tkinter variables for center frequency,
                span, RBW, VBW, sweep time, preamplifier, and high sensitivity.
            4. If not connected, logs an error.

        Outputs:
            None. Updates GUI display based on instrument state.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Querying settings from instrument. Version: {self.current_version}. Getting the scoop!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if self.app_instance.inst:
            # query_current_settings_logic expects app_instance and console_print_func
            query_current_settings_logic(self.app_instance, self.console_print_func)

            debug_log(f"Settings queried and UI updated. Version: {self.current_version}. Success!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            self.app_instance.after(0, lambda: self.console_print_func("❌ Instrument not connected. Cannot query settings."))
            debug_log(f"Instrument not connected. Cannot query settings. Version: {self.current_version}. This is a disaster!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)

    def _clear_settings_display(self):
        """
        Function Description:
        Clears the displayed instrument settings in the GUI, typically called
        when the instrument is disconnected.

        Inputs:
            None.

        Process:
            1. Sets all relevant Tkinter variables to default/empty values.
            2. Logs the action.

        Outputs:
            None. Clears GUI display.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Clearing instrument settings display. Version: {self.current_version}. Wiping the slate clean!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Schedule updates on the main thread
        self.app_instance.after(0, lambda: self.app_instance.center_freq_hz_var.set(0.0))
        self.app_instance.after(0, lambda: self.app_instance.span_hz_var.set(0.0))
        self.app_instance.after(0, lambda: self.app_instance.rbw_hz_var.set(0.0))
        self.app_instance.after(0, lambda: self.app_instance.vbw_hz_var.set(0.0))
        self.app_instance.after(0, lambda: self.app_instance.sweep_time_s_var.set(0.0))
        self.app_instance.after(0, lambda: self.app_instance.preamp_on_var.set(False))
        self.app_instance.after(0, lambda: self.app_instance.high_sensitivity_var.set(False))
        self.app_instance.after(0, lambda: self.app_instance.instrument_model.set("N/A"))
        self.app_instance.after(0, lambda: self.app_instance.instrument_serial.set("N/A"))
        self.app_instance.after(0, lambda: self.app_instance.instrument_firmware.set("N/A"))
        self.app_instance.after(0, lambda: self.app_instance.instrument_options.set("N/A"))


    def _on_tab_selected(self, event):
        """
        Function Description:
        Called when this tab is selected in the notebook.
        Refreshes the UI elements based on the current connection status.
        If connected, it queries the settings from the instrument to update the display.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"InstrumentTab selected. Refreshing UI based on connection status. Version: {self.current_version}. Time to shine!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # Check if this tab is the currently selected tab in its parent notebook
        # This prevents unnecessary refreshes when other tabs in the same parent notebook are selected
        if event and event.widget.select() != self._w:
            return

        is_connected = self.app_instance.inst is not None
        # Use selected_resource, not selected_resource_var
        resource_found = bool(self.app_instance.selected_resource.get())

        # Always update UI visibility first based on current connection state
        self._update_ui_elements_visibility(connected=is_connected, resource_found=resource_found)

        if is_connected:
            debug_log("Instrument is connected. Querying current settings to update display. Version: {self.current_version}. Getting the latest data!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            # Call query settings logic to update the display
            self._query_settings_from_instrument()
        else:
            debug_log("Instrument is NOT connected. Clearing settings display on tab selection. Version: {self.current_version}. Nothing to see here!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            self._clear_settings_display()

    def _update_ui_elements_visibility(self, connected, resource_found):
        """
        Function Description:
        Manages the visibility and state of various UI elements on the tab
        based on the instrument's connection status and whether a resource is found.

        Inputs:
            connected (bool): True if the instrument is connected, False otherwise.
            resource_found (bool): True if a VISA resource is selected, False otherwise.

        Process:
            1. Updates the state and text of the connect button.
            2. Updates the state of the resource combobox and refresh button.
            3. Updates the state of settings display labels and action buttons.
            4. Logs the visibility update.

        Outputs:
            None. Adjusts GUI element visibility.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating UI element visibility. Connected: {connected}, Resource Found: {resource_found}. Version: {self.current_version}. Adapting the view!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if connected:
            self.connect_button.config(text="Disconnect", style="FlashingGreen.TButton")
            self.resource_combobox.config(state=tk.DISABLED)
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
