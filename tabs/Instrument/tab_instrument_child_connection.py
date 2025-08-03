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
# Version 20250803.1405.0 (Corrected variable name from selected_resource_var to selected_resource.)

current_version = "20250803.1405.0" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250803 * 1405 * 0 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os
import threading
# Import instrument control logic functions
from tabs.Instrument.utils_instrument_connection import connect_to_instrument, disconnect_instrument
from tabs.Instrument.utils_instrument_initialize import initialize_instrument
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings as query_instrument_settings
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe

# Import instrument control logic functions
from tabs.Instrument.utils_instrument_connection import connect_to_instrument, disconnect_instrument # Corrected function names
from tabs.Instrument.utils_instrument_initialize import initialize_instrument
from tabs.Instrument.utils_instrument_query_settings import query_current_instrument_settings as query_instrument_settings
from tabs.Instrument.utils_instrument_read_and_write import write_safe, query_safe

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

# Corrected imports for instrument logic functions (these remain as previously suggested)
from tabs.Instrument.instrument_logic import apply_settings_logic, query_current_settings_logic,list_visa_resources,disconnect_instrument_logic,connect_instrument_logic
# Import restore settings logic directly from its module, not instrument_logic
from src.settings_and_config.restore_settings_logic import restore_default_settings_logic, restore_last_used_settings_logic
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
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_model_var, style='Dark.TLabel').grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Serial:", style='Dark.TLabel').grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_serial_var, style='Dark.TLabel').grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # Row 1: Firmware & Options
        ttk.Label(settings_display_frame, text="Firmware:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_firmware_var, style='Dark.TLabel').grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Options:", style='Dark.TLabel').grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.instrument_options_var, style='Dark.TLabel').grid(row=1, column=3, padx=5, pady=2, sticky="w")


        # Row 2: Center Freq & Span
        ttk.Label(settings_display_frame, text="Center Freq (Hz):", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.center_freq_mhz_var, style='Dark.TLabel').grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(settings_display_frame, text="Span (Hz):", style='Dark.TLabel').grid(row=2, column=2, padx=5, pady=2, sticky="w")
        ttk.Label(settings_display_frame, textvariable=self.app_instance.span_mhz_var, style='Dark.TLabel').grid(row=2, column=3, padx=5, pady=2, sticky="w")

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
            2. Updates `self.app_instance.available_resources` and `self.resource_combobox['values']` on the main thread using `app_instance.after`.
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
        self.app_instance.after(0, lambda: self.app_instance.available_resources.set(resource_names))
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
        Event handler for when a VISA resource is selected from the combobox.
        Updates the application's selected resource variable.

        Inputs:
            event (tk.Event): The event object (not used directly but required for binding).

        Process:
            1. Updates `self.app_instance.selected_resource` with the currently selected value.
            2. Enables/disables the connect button based on whether a resource is selected.

        Outputs:
            None. Updates internal state and UI.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Resource selected: {self.app_instance.selected_resource.get()}. Version: {self.current_version}. User made a choice!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)
        # Ensure the connect button is enabled if a resource is selected
        if self.app_instance.selected_resource.get():
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.DISABLED)

    def _toggle_connection(self):
        """
        Function Description:
        Toggles the instrument connection state (Connect/Disconnect).
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables the connect/disconnect button.
            2. Starts a new thread to call `_toggle_connection_thread`.
            3. Re-enables the connect/disconnect button in the thread's completion.

        Outputs:
            None. Initiates connection/disconnection.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Toggling connection. Current state: {self.app_instance.is_connected.get()}. Version: {self.current_version}. Taking action!",
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
            1. Checks current connection status.
            2. If connected, calls `disconnect_instrument_logic`.
            3. If disconnected, calls `connect_instrument_logic`.
            4. Updates connection status label and button text on the main thread.
            5. Re-enables the connect button on the main thread.
            6. Manages the state of UI elements based on connection status.

        Outputs:
            None. Updates GUI elements and global connection state.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _toggle_connection_thread. Version: {self.current_version}. The connection dance begins!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if self.app_instance.is_connected.get():
            # Disconnect
            debug_log(f"Attempting to disconnect instrument. Version: {self.current_version}. Time to say goodbye!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            # Pass the app_instance to disconnect_instrument_logic
            success = disconnect_instrument_logic(self.app_instance, self.console_print_func)
            if success:
                self.app_instance.inst = None # Clear the instrument instance in main_app
                self.app_instance.is_connected.set(False)
                # Clear instrument info
                self.app_instance.after(0, lambda: self.app_instance.instrument_model_var.set("N/A"))
                self.app_instance.after(0, lambda: self.app_instance.instrument_serial_var.set("N/A"))
                self.app_instance.after(0, lambda: self.app_instance.instrument_firmware_var.set("N/A"))
                self.app_instance.after(0, lambda: self.app_instance.instrument_options_var.set("N/A"))
                self.app_instance.after(0, lambda: self.app_instance.center_freq_mhz_var.set(0.0))
                self.app_instance.after(0, lambda: self.app_instance.span_mhz_var.set(0.0))
                self.app_instance.after(0, lambda: self.app_instance.rbw_hz_var.set("0 Hz"))
                self.app_instance.after(0, lambda: self.app_instance.vbw_hz_var.set("0 Hz"))
                self.app_instance.after(0, lambda: self.app_instance.sweep_time_s_var.set("0 s"))
                self.app_instance.after(0, lambda: self.app_instance.preamp_on_var.set(False))
                self.app_instance.after(0, lambda: self.app_instance.high_sensitivity_var.set(False))
                debug_log(f"Instrument disconnected successfully. Version: {self.current_version}. Mission accomplished!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=self.current_version,
                            function=current_function)
            else:
                debug_log(f"Instrument disconnection failed. Version: {self.current_version}. Error!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=current_version,
                            function=current_function)
        else:
            # Connect
            resource_name = self.app_instance.selected_resource.get()
            if not resource_name:
                self.console_print_func("⚠️ Please select a VISA resource first. Come on!")
                debug_log(f"No resource selected for connection. Version: {self.current_version}. User needs to pick one!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=current_version,
                            function=current_function)
                self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))
                return

            debug_log(f"Attempting to connect to instrument: {resource_name}. Version: {self.current_version}. Let's make this happen!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=current_version,
                        function=current_function)
            # Pass the app_instance to connect_instrument_logic
            success = connect_instrument_logic(self.app_instance, self.console_print_func)
            if success:
                self.app_instance.is_connected.set(True)
                # Query and display initial settings and instrument info
                self.app_instance.after(0, lambda: self._query_settings_and_info())
                debug_log(f"Instrument connected and initialized. Version: {self.current_version}. Success!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=current_version,
                            function=current_function)
            else:
                debug_log(f"Instrument connection failed. Version: {self.current_version}. What a failure!",
                            file=f"{self.current_file} - {self.current_version}",
                            version=current_version,
                            function=current_function)

        self.app_instance.after(0, lambda: self._update_connection_status_ui())
        self.app_instance.after(0, lambda: self.connect_button.config(state=tk.NORMAL))


    def _update_connection_status_ui(self):
        """
        Function Description:
        Updates the connection status label and button text based on
        `self.app_instance.is_connected` and `self.app_instance.selected_resource`.
        Also enables/disables other UI elements based on connection state.

        Inputs:
            None.

        Process:
            1. Updates `connection_status_label` text and color.
            2. Updates `connect_button` text and style.
            3. Enables/disables combobox, refresh button, and settings display elements.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating connection status UI. Version: {self.current_version}. Making sure everything looks right!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        is_connected = self.app_instance.is_connected.get()
        resource_found = bool(self.app_instance.selected_resource.get())

        if is_connected:
            self.connection_status_label.config(text="Status: Connected! 🚀", foreground="green")
            self.connect_button.config(text="Disconnect", style='Red.TButton')
            self.resource_combobox.config(state=tk.DISABLED) # Disable combobox when connected
            self.refresh_button.config(state=tk.DISABLED) # Disable refresh when connected
            # Enable settings display and action buttons
            for child in self.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Current Instrument Settings":
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.NORMAL)
                elif isinstance(child, ttk.Frame) and any(b.cget("text") == "Apply Settings" for b in child.winfo_children()):
                    for sub_child in child.winfo_children():
                        sub_child.config(state=tk.NORMAL)
        else:
            self.connection_status_label.config(text="Status: Disconnected 💀", foreground="red") # Ensure status is red when disconnected
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
        if resource_found and not is_connected: # Only enable if resource found AND not already connected
            self.connect_button.config(state=tk.NORMAL)
        elif not resource_found: # If no resource found, disable it
            self.connect_button.config(state=tk.DISABLED)


    def _query_settings_and_info(self):
        """
        Function Description:
        Queries the connected instrument for its identification information
        (model, serial, firmware, options) and current settings (Center Freq,
        Span, RBW, VBW, Sweep Time, Preamplifier, High Sensitivity) and
        updates the corresponding Tkinter variables.

        This function is called after a successful connection.
        It runs in a separate thread.

        Inputs:
            None.

        Process:
            1. Calls `query_current_settings_logic` to get instrument info and settings.
            2. Updates Tkinter variables on the main thread using `app_instance.after`.
            3. Handles potential errors during query.

        Outputs:
            None. Updates GUI elements.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Querying instrument settings and info. Version: {self.current_version}. Getting the deets!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        threading.Thread(target=self._query_settings_and_info_thread, daemon=True).start()

    def _query_settings_and_info_thread(self):
        """
        Worker function for _query_settings_and_info.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _query_settings_and_info_thread. Version: {self.current_version}. Digging for data!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # The query_current_settings_logic now takes the app_instance directly
        success = query_current_settings_logic(self.app_instance, self.console_print_func)

        if success:
            debug_log(f"Instrument settings and info queried successfully. Version: {self.current_version}. All good!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"Failed to query instrument settings and info. Version: {self.current_version}. This is not good!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)


    def _apply_settings(self):
        """
        Function Description:
        Applies the current settings (Center Freq, Span, RBW, VBW, Sweep Time,
        Preamplifier, High Sensitivity) to the connected instrument.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables action buttons.
            2. Starts a new thread to call `_apply_settings_thread`.
            3. Re-enables action buttons in the thread's completion.

        Outputs:
            None. Initiates settings application.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Applying settings. Version: {self.current_version}. Time to configure!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self._set_action_buttons_state(tk.DISABLED)
        threading.Thread(target=self._apply_settings_thread, daemon=True).start()

    def _apply_settings_thread(self):
        """
        Worker function for _apply_settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _apply_settings_thread. Version: {self.current_version}. Making changes!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        # The apply_settings_logic now takes the app_instance directly
        success = apply_settings_logic(self.app_instance, self.console_print_func)
        if success:
            self.app_instance.after(0, lambda: self._query_settings_and_info()) # Re-query to confirm settings
            debug_log(f"Settings applied successfully. Version: {self.current_version}. Confirmed!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"Failed to apply settings. Version: {self.current_version}. Oh no!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))


    def _initialize_instrument(self):
        """
        Function Description:
        Initializes the connected instrument with a set of predefined basic settings.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables action buttons.
            2. Starts a new thread to call `_initialize_instrument_thread`.
            3. Re-enables action buttons in the thread's completion.

        Outputs:
            None. Initiates instrument initialization.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing instrument. Version: {self.current_version}. Getting it ready!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self._set_action_buttons_state(tk.DISABLED)
        threading.Thread(target=self._initialize_instrument_thread, daemon=True).start()

    def _initialize_instrument_thread(self):
        """
        Worker function for _initialize_instrument.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _initialize_instrument_thread. Version: {self.current_version}. Preparing for action!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument connected to initialize. Connect first!")
            debug_log(f"No instrument connected for initialization. Version: {self.current_version}. Connect the damn thing!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))
            return

        # The initialize_instrument function now takes app_instance, console_print_func
        # and other parameters directly from app_instance
        success = initialize_instrument(
            self.app_instance.inst,
            self.app_instance.ref_level_dbm_var.get(),
            self.app_instance.high_sensitivity_var.get(),
            self.app_instance.preamp_on_var.get(),
            float(self.app_instance.rbw_hz_var.get()), # Pass RBW as float
            float(self.app_instance.vbw_hz_var.get()), # Pass VBW as float
            self.app_instance.instrument_model_var.get(),
            self.console_print_func
        )
        if success:
            self.app_instance.after(0, lambda: self._query_settings_and_info()) # Re-query to confirm settings
            debug_log(f"Instrument initialized successfully. Version: {self.current_version}. Ready to go!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"Failed to initialize instrument. Version: {self.current_version}. Something went wrong!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))


    def _restore_default_settings(self):
        """
        Function Description:
        Restores instrument settings to factory defaults.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables action buttons.
            2. Starts a new thread to call `_restore_default_settings_thread`.
            3. Re-enables action buttons in the thread's completion.

        Outputs:
            None. Initiates default settings restoration.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restoring default settings. Version: {self.current_version}. Going back to basics!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self._set_action_buttons_state(tk.DISABLED)
        threading.Thread(target=self._restore_default_settings_thread, daemon=True).start()

    def _restore_default_settings_thread(self):
        """
        Worker function for _restore_default_settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _restore_default_settings_thread. Version: {self.current_version}. Wiping the slate clean!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument connected to restore defaults. Connect first!")
            debug_log(f"No instrument connected for default settings restore. Version: {self.current_version}. Connect the damn thing!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))
            return

        success = restore_default_settings_logic(self.app_instance.inst, self.console_print_func)
        if success:
            self.app_instance.after(0, lambda: self._query_settings_and_info()) # Re-query to confirm settings
            debug_log(f"Default settings restored successfully. Version: {self.current_version}. Fresh start!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"Failed to restore default settings. Version: {self.current_version}. What a pain!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))


    def _restore_last_used_settings(self):
        """
        Function Description:
        Restores instrument settings to the last saved configuration.
        This function is executed in a separate thread to prevent GUI freezing.

        Inputs:
            None.

        Process:
            1. Disables action buttons.
            2. Starts a new thread to call `_restore_last_used_settings_thread`.
            3. Re-enables action buttons in the thread's completion.

        Outputs:
            None. Initiates last used settings restoration.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Restoring last used settings. Version: {self.current_version}. Going back in time!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        self._set_action_buttons_state(tk.DISABLED)
        threading.Thread(target=self._restore_last_used_settings_thread, daemon=True).start()

    def _restore_last_used_settings_thread(self):
        """
        Worker function for _restore_last_used_settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Running _restore_last_used_settings_thread. Version: {self.current_version}. Reverting to previous state!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("⚠️ No instrument connected to restore last used settings. Connect first!")
            debug_log(f"No instrument connected for last used settings restore. Version: {self.current_version}. Connect the damn thing!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
            self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))
            return

        success = restore_last_used_settings_logic(self.app_instance.inst, self.console_print_func)
        if success:
            self.app_instance.after(0, lambda: self._query_settings_and_info()) # Re-query to confirm settings
            debug_log(f"Last used settings restored successfully. Version: {self.current_version}. History lesson learned!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        else:
            debug_log(f"Failed to restore last used settings. Version: {self.current_version}. This is a disaster!",
                        file=f"{self.current_file} - {self.current_version}",
                        version=self.current_version,
                        function=current_function)
        self.app_instance.after(0, lambda: self._set_action_buttons_state(tk.NORMAL))


    def _set_action_buttons_state(self, state):
        """
        Helper function to set the state of all action buttons (Apply, Initialize, Restore).
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Setting action button state to: {state}. Version: {self.current_version}. UI control engaged!",
                    file=f"{self.current_file} - {self.current_version}",
                    version=self.current_version,
                    function=current_function)

        for child in self.winfo_children():
            if isinstance(child, ttk.Frame) and any(b.cget("text") == "Apply Settings" for b in child.winfo_children()):
                for sub_child in child.winfo_children():
                    sub_child.config(state=state)
                break # Assuming there's only one such frame


    def _on_tab_selected(self, event):
        """
        Function Description:
        Called when this tab is selected in the notebook.
        Can be used to refresh data or update UI elements specific to this tab.

        Inputs:
            event (tk.Event): The event object.

        Process:
            1. Checks if the currently selected tab is this InstrumentTab instance.
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
