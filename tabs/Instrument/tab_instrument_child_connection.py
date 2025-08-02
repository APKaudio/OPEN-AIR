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
# Version 20250802.0230.1 (Refined _do_refresh_resources for robust combobox population and selection.)

current_version = "20250802.0230.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 75 * 12 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk
import inspect
import os
import threading

# Import instrument control logic functions - CORRECTED PATHS
from src.instrument_logic import (
    populate_resources_logic, connect_instrument_logic, disconnect_instrument_logic,
    query_current_instrument_settings_logic, apply_settings_logic
)
# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log # Import console_log


class InstrumentTab(ttk.Frame):
    """
    A Tkinter Frame that manages the Instrument Connection tab.
    Handles VISA resource discovery, instrument connection/disconnection,
    and displays current instrument settings.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs): # Added style_obj
        """
        Initializes the InstrumentTab.

        Inputs:
            master (tk.Widget): The parent widget.
            app_instance (App): The main application instance, used for accessing
                                shared state like instrument objects and config.
            console_print_func (function, optional): Function to use for console output.
            style_obj (ttk.Style, optional): The ttk.Style object from the main app.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Initializing InstrumentTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.style_obj = style_obj # Store the style object

        # Explicitly remove 'style_obj' from kwargs before passing them to the superclass
        # This is a defensive measure to prevent TclError if it somehow ends up in kwargs.
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, **filtered_kwargs) # Pass filtered kwargs

        self._create_widgets()
        self._update_ui_elements_visibility(connected=False, resource_found=False) # Initial state


    def _create_widgets(self):
        """
        Creates and arranges the widgets for the Instrument Connection tab.
        This includes resource discovery, connection controls, and settings display.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Creating InstrumentTab widgets.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Configure grid for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) # Connection Controls
        self.grid_rowconfigure(1, weight=1) # Instrument Settings Display

        # --- Connection Controls Frame ---
        connection_frame = ttk.LabelFrame(self, text="Instrument Connection", padding=(10, 10, 10, 10), style='Dark.TLabelframe')
        connection_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        connection_frame.grid_columnconfigure(0, weight=1)
        connection_frame.grid_columnconfigure(1, weight=1)
        connection_frame.grid_columnconfigure(2, weight=1)
        connection_frame.grid_columnconfigure(3, weight=1) # For Refresh Devices button

        # VISA Resource Dropdown
        ttk.Label(connection_frame, text="VISA Resource:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # Link textvariable to app_instance.selected_resource
        self.resource_dropdown = ttk.Combobox(connection_frame, textvariable=self.app_instance.selected_resource, state="readonly", style='Dark.TCombobox')
        self.resource_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.resource_dropdown.bind("<<ComboboxSelected>>", self._on_resource_selected)

        # Refresh Devices Button
        self.refresh_button = ttk.Button(connection_frame, text="Refresh Devices", command=self._refresh_resources, style='Blue.TButton')
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Connect/Disconnect Buttons
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self._connect_instrument, style='Green.TButton')
        self.connect_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self._disconnect_instrument, state=tk.DISABLED, style='Red.TButton')
        self.disconnect_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Query Settings Button
        self.query_settings_button = ttk.Button(connection_frame, text="Query Instrument Settings", command=self._query_current_instrument_settings, style='Orange.TButton')
        self.query_settings_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        # Apply Settings Button
        self.apply_settings_button = ttk.Button(connection_frame, text="Apply Settings to Instrument", command=self._apply_settings_to_instrument, style='Orange.TButton')
        self.apply_settings_button.grid(row=1, column=3, padx=5, pady=5, sticky="ew")


        # --- Instrument Settings Display Frame ---
        settings_display_frame = ttk.LabelFrame(self, text="Current Instrument Settings", padding=(10, 10, 10, 10), style='Dark.TLabelframe')
        settings_display_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        settings_display_frame.grid_columnconfigure(1, weight=1) # Make value column expand

        # Labels for displaying settings
        self.settings_labels = {} # Store labels for easy update

        # Instrument Model
        ttk.Label(settings_display_frame, text="Instrument Model:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.settings_labels["model"] = ttk.Label(settings_display_frame, text="N/A", style='Dark.TLabel.Value')
        self.settings_labels["model"].grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Center Frequency
        ttk.Label(settings_display_frame, text="Center Frequency:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.current_center_freq_var = tk.StringVar(self, value="N/A")
        self.settings_labels["center_freq"] = ttk.Label(settings_display_frame, textvariable=self.current_center_freq_var, style='Dark.TLabel.Value')
        self.settings_labels["center_freq"].grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Span
        ttk.Label(settings_display_frame, text="Span:", style='Dark.TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.current_span_var = tk.StringVar(self, value="N/A")
        self.settings_labels["span"] = ttk.Label(settings_display_frame, textvariable=self.current_span_var, style='Dark.TLabel.Value')
        self.settings_labels["span"].grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # RBW
        ttk.Label(settings_display_frame, text="RBW:", style='Dark.TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.current_rbw_var = tk.StringVar(self, value="N/A")
        self.settings_labels["rbw"] = ttk.Label(settings_display_frame, textvariable=self.current_rbw_var, style='Dark.TLabel.Value')
        self.settings_labels["rbw"].grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # VBW
        ttk.Label(settings_display_frame, text="VBW:", style='Dark.TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.current_vbw_var = tk.StringVar(self, value="N/A")
        self.settings_labels["vbw"] = ttk.Label(settings_display_frame, textvariable=self.current_vbw_var, style='Dark.TLabel.Value')
        self.settings_labels["vbw"].grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # Reference Level
        ttk.Label(settings_display_frame, text="Reference Level:", style='Dark.TLabel').grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.current_ref_level_var = tk.StringVar(self, value="N/A")
        self.settings_labels["ref_level"] = ttk.Label(settings_display_frame, textvariable=self.current_ref_level_var, style='Dark.TLabel.Value')
        self.settings_labels["ref_level"].grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        # Preamp State
        ttk.Label(settings_display_frame, text="Preamp State:", style='Dark.TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.current_preamp_var = tk.StringVar(self, value="N/A")
        self.settings_labels["preamp"] = ttk.Label(settings_display_frame, textvariable=self.current_preamp_var, style='Dark.TLabel.Value')
        self.settings_labels["preamp"].grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        # High Sensitivity State
        ttk.Label(settings_display_frame, text="High Sensitivity:", style='Dark.TLabel').grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.current_high_sensitivity_var = tk.StringVar(self, value="N/A")
        self.settings_labels["high_sensitivity"] = ttk.Label(settings_display_frame, textvariable=self.current_high_sensitivity_var, style='Dark.TLabel.Value')
        self.settings_labels["high_sensitivity"].grid(row=7, column=1, padx=5, pady=2, sticky="ew")

        debug_log(f"InstrumentTab widgets created.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _refresh_resources(self):
        """
        Initiates the VISA resource discovery process in a separate thread
        to keep the GUI responsive.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        console_log("Searching for VISA instruments...", function=current_function)
        debug_log(f"Initiating resource refresh.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self._disable_buttons_during_operation()
        threading.Thread(target=self._do_refresh_resources).start()


    def _do_refresh_resources(self):
        """
        Performs the actual VISA resource discovery and updates the dropdown.
        This runs in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        try:
            resources = populate_resources_logic(self.app_instance.rm, console_log)
            
            # This function will be called on the main thread
            def update_combobox_and_selection():
                # Step 1: Set the values for the dropdown
                self.resource_dropdown.config(values=resources) 
                
                # Step 2: Attempt to restore last selected resource or pick the first one
                if resources:
                    last_selected = self.app_instance.selected_resource.get()
                    if last_selected and last_selected in resources:
                        self.app_instance.selected_resource.set(last_selected)
                        console_log(f"Restored last selected resource: {last_selected}", function=current_function)
                    else:
                        self.app_instance.selected_resource.set(resources[0]) # Select the first one by default
                        console_log(f"Selected first available resource: {resources[0]}", function=current_function)
                    
                    # Step 3: Save the selected resource to config.ini
                    self.app_instance.config.set('LAST_USED_SETTINGS', 'last_instrument_connection__visa_resource', self.app_instance.selected_resource.get())
                    # The trace on selected_resource will call save_config, so no explicit call here.
                    console_log(f"Saved selected resource to config: {self.app_instance.selected_resource.get()}", function=current_function)

                    debug_log(f"Found resources: {resources}. Selected: {self.app_instance.selected_resource.get()}",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    # Step 4: Update UI elements visibility based on resource found (and not connected yet)
                    self._update_ui_elements_visibility(connected=False, resource_found=True)
                else:
                    self.app_instance.selected_resource.set("") # Clear selection
                    console_log("🚫 No VISA instruments found.", function=current_function)
                    debug_log(f"No VISA instruments found.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    self._update_ui_elements_visibility(connected=False, resource_found=False)
                
                # Step 5: Always re-enable buttons after the operation
                self._enable_buttons_after_operation() 

            self.app_instance.after(0, update_combobox_and_selection)

        except Exception as e:
            console_log(f"❌ Error refreshing resources: {e}", function=current_function)
            debug_log(f"Error refreshing resources: {e}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            self.app_instance.after(0, lambda: self._update_ui_elements_visibility(connected=False, resource_found=False))
            self.app_instance.after(0, self._enable_buttons_after_operation) # Ensure buttons are re-enabled even on error


    def _on_resource_selected(self, event):
        """
        Handles the event when a resource is selected from the dropdown.
        Updates the UI visibility.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        selected_resource = self.app_instance.selected_resource.get()
        debug_log(f"Resource selected: {selected_resource}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        # Enable connect button if a resource is selected
        self._update_ui_elements_visibility(connected=False, resource_found=bool(selected_resource))


    def _connect_instrument(self):
        """
        Initiates the instrument connection process in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        selected_resource = self.app_instance.selected_resource.get()
        if not selected_resource:
            console_log("⚠️ Please select a VISA resource first.", function=current_function)
            debug_log(f"Attempted connect without selected resource.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        console_log(f"Connecting to {selected_resource}...", function=current_function)
        debug_log(f"Initiating connection to {selected_resource}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self._disable_buttons_during_operation()
        threading.Thread(target=self._do_connect_instrument, args=(selected_resource,)).start()


    def _do_connect_instrument(self, resource_name):
        """
        Performs the actual instrument connection. This runs in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        success = connect_instrument_logic(self.app_instance, resource_name, console_log)
        self.app_instance.after(0, lambda: self._update_ui_elements_visibility(connected=success, resource_found=True))
        self.app_instance.after(0, self._enable_buttons_after_operation)
        if success:
            # Query settings immediately after successful connection
            self.app_instance.after(0, self._query_current_instrument_settings)


    def _disconnect_instrument(self):
        """
        Initiates the instrument disconnection process in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        console_log("Disconnecting instrument...", function=current_function)
        debug_log(f"Initiating disconnection.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self._disable_buttons_during_operation()
        threading.Thread(target=self._do_disconnect_instrument).start()


    def _do_disconnect_instrument(self):
        """
        Performs the actual instrument disconnection. This runs in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        success = disconnect_instrument_logic(self.app_instance, console_log)
        self.app_instance.after(0, lambda: self._update_ui_elements_visibility(connected=False, resource_found=bool(self.app_instance.selected_resource.get())))
        self.app_instance.after(0, self._enable_buttons_after_operation)
        if success:
            self.app_instance.after(0, self._clear_settings_display)


    def _query_current_instrument_settings(self):
        """
        Initiates querying current instrument settings in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        if not self.app_instance.inst:
            console_log("⚠️ Not connected to an instrument. Cannot query settings.", function=current_function)
            debug_log(f"Attempted query without connection.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        console_log("Querying current instrument settings...", function=current_function)
        debug_log(f"Initiating query of current instrument settings.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self._disable_buttons_during_operation()
        threading.Thread(target=self._do_query_current_instrument_settings).start()


    def _do_query_current_instrument_settings(self):
        """
        Performs the actual querying of instrument settings and updates the display.
        This runs in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        success = query_current_instrument_settings_logic(self.app_instance, console_log)
        self.app_instance.after(0, self._enable_buttons_after_operation)
        if success:
            self.app_instance.after(0, self._update_settings_display)
        else:
            self.app_instance.after(0, self._clear_settings_display)


    def _apply_settings_to_instrument(self):
        """
        Initiates applying settings to the instrument in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        if not self.app_instance.inst:
            console_log("⚠️ Not connected to an instrument. Cannot apply settings.", function=current_function)
            debug_log(f"Attempted apply settings without connection.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        console_log("Applying settings to instrument...", function=current_function)
        debug_log(f"Initiating apply settings to instrument.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self._disable_buttons_during_operation()
        threading.Thread(target=self._do_apply_settings_to_instrument).start()


    def _do_apply_settings_to_instrument(self):
        """
        Performs the actual application of settings to the instrument.
        This runs in a separate thread.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        success = apply_settings_logic(self.app_instance, console_log)
        self.app_instance.after(0, self._enable_buttons_after_operation)
        if success:
            console_log("✅ Settings applied successfully.", function=current_function)
            # After applying, query to confirm the settings are reflected
            self.app_instance.after(0, self._query_current_instrument_settings)
        else:
            console_log("❌ Failed to apply settings.", function=current_function)


    def _update_settings_display(self):
        """
        Updates the labels in the Instrument Settings Display frame
        with the current values from the app_instance's Tkinter variables.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Updating instrument settings display.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.settings_labels["model"].config(text=self.app_instance.instrument_model if self.app_instance.instrument_model else "N/A")
        self.current_center_freq_var.set(f"{self.app_instance.center_freq_hz_var.get() / 1e9:.3f} GHz")
        self.current_span_var.set(f"{self.app_instance.span_hz_var.get() / 1e6:.3f} MHz")
        self.current_rbw_var.set(f"{self.app_instance.rbw_hz_var.get() / 1e3:.3f} kHz")
        self.current_vbw_var.set(f"{self.app_instance.vbw_hz_var.get() / 1e3:.3f} kHz")
        self.current_ref_level_var.set(f"{self.app_instance.reference_level_dbm_var.get()} dBm") # Assuming this is string var
        self.current_preamp_var.set("ON" if self.app_instance.preamp_on_var.get() else "OFF")
        self.current_high_sensitivity_var.set("ON" if self.app_instance.high_sensitivity_var.get() else "OFF")


    def _clear_settings_display(self):
        """
        Clears the displayed instrument settings.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Clearing instrument settings display.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.settings_labels["model"].config(text="N/A")
        self.current_center_freq_var.set("N/A")
        self.current_span_var.set("N/A")
        self.current_rbw_var.set("N/A")
        self.current_vbw_var.set("N/A")
        self.current_ref_level_var.set("N/A")
        self.current_preamp_var.set("N/A")
        self.current_high_sensitivity_var.set("N/A")


    def _disable_buttons_during_operation(self):
        """Disables relevant buttons during an ongoing operation."""
        self.refresh_button.config(state=tk.DISABLED)
        self.connect_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.DISABLED)
        self.query_settings_button.config(state=tk.DISABLED)
        self.apply_settings_button.config(state=tk.DISABLED)
        self.resource_dropdown.config(state="disabled") # Disable dropdown during operation


    def _enable_buttons_after_operation(self):
        """Enables/disables buttons based on current connection status after an operation."""
        is_connected = self.app_instance.inst is not None
        resource_found = bool(self.app_instance.selected_resource.get())
        self._update_ui_elements_visibility(connected=is_connected, resource_found=resource_found)


    def _update_ui_elements_visibility(self, connected: bool, resource_found: bool):
        """
        Function Description:
        Dynamically updates the visibility and state of UI elements based on
        the instrument's connection status and whether a resource is selected.

        Inputs:
            connected (bool): True if the instrument is currently connected.
            resource_found (bool): True if at least one VISA resource has been found.

        Process of this function:
            1. Logs the current state.
            2. Configures the state of the `refresh_button`, `resource_dropdown`,
               `connect_button`, `disconnect_button`, `query_settings_button`,
               and `apply_settings_button` based on `connected` and `resource_found`.
            3. Updates the main application's connection status label via `app_instance`.
            # Removed: 4. Updates the state of debug checkboxes based on app_instance variables.

        Outputs of this function:
            None. Modifies UI element states.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Updating UI visibility. Connected: {connected}, Resource Found: {resource_found}.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Refresh button is always enabled unless an operation is active
        self.refresh_button.config(state=tk.NORMAL)

        # Resource dropdown
        if resource_found:
            self.resource_dropdown.config(state="readonly")
        else:
            self.resource_dropdown.config(state="disabled")
            self.app_instance.selected_resource.set("") # Clear selection if no resources

        # Connect/Disconnect buttons
        if connected:
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.query_settings_button.config(state=tk.NORMAL)
            self.apply_settings_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.NORMAL if resource_found else tk.DISABLED)
            self.disconnect_button.config(state=tk.DISABLED)
            self.query_settings_button.config(state=tk.DISABLED)
            self.apply_settings_button.config(state=tk.DISABLED)

        # Update the main app's connection status label (now handled by ScanControlTab)
        self.app_instance.update_connection_status(connected)

        # Removed: Set initial state of debug checkboxes based on app_instance variables
        # Removed: self.general_debug_checkbox.config(variable=self.app_instance.general_debug_enabled_var)
        # Removed: self.log_visa_commands_checkbox.config(variable=self.app_instance.log_visa_commands_enabled_var)


    def _on_tab_selected(self, event):
        """
        Called when this tab is selected in the notebook.
        Refreshes the UI elements based on current connection status.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"InstrumentTab selected. Refreshing UI based on connection status.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        is_connected = self.app_instance.inst is not None
        resource_found = bool(self.app_instance.selected_resource.get())

        if is_connected:
            debug_log("Instrument is connected. Clearing settings display on tab selection (no automatic query, you gotta push the button for that, you lazy bastard).",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self._clear_settings_display() # Just clear, don't query automatically
        else:
            debug_log("Instrument is NOT connected. Clearing settings display on tab selection.",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            self._clear_settings_display()

        # --- NEW: Update UI visibility based on connection status when tab is selected ---
        # We assume that if the tab is selected, we should at least show the "Find Instruments" button.
        # If already connected, the state will reflect that.
        self._update_ui_elements_visibility(connected=is_connected, resource_found=resource_found)
        # --- END NEW ---

