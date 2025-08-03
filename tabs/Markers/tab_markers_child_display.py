# tabs/Markers/tab_markers_child_display.py
#
# This file manages the Markers Display tab in the GUI, handling
# the display of extracted frequency markers, span control, and trace mode selection.
# It is designed to ONLY interact with the instrument when a user explicitly
# clicks a relevant button (device button, span button, or trace mode button).
# It DOES NOT make any automatic instrument queries on tab selection or data loading.
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
# Version 20250802.0050.1 (Fixed TclError: unknown option "-console_print_func" by removing from kwargs.)
# Version 20250803.0340.0 (Updated button styles to use the new, more specific names from style.py.)
# Version 20250803.0755.0 (Added debug logs for device button styling and ensured style application.)
# Version 20250803.0800.0 (Fixed device button highlighting persistence across tree selections.)

current_version = "20250803.0800.0" # this variable should always be defined below the header to make the debugging better

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk # Keep other imports
import os
import csv
import inspect
import json # Import json for serializing/deserializing row data
import math # Import math for ceil function (still useful for general calculations, though not directly for this column logic)

# Import new marker utility functions and constants - CORRECTED PATHS
from tabs.Markers.utils_markers import SPAN_OPTIONS, RBW_OPTIONS, set_span_logic, set_frequency_logic, set_trace_modes_logic, set_marker_logic, blank_hold_traces_logic, set_rbw_logic
# Import the new debug_logic and console_logic modules
from src.debug_logic import debug_log # Changed from debug_print
from src.console_logic import console_log # Changed from console_print_func
from ref.frequency_bands import MHZ_TO_HZ # Import MHZ_TO_HZ for conversion


# Removed the hardcoded MARKERS_FILE_PATH, it will now be determined dynamically


class MarkersDisplayTab(ttk.Frame):
    """
    A Tkinter Frame that displays extracted frequency markers in a hierarchical treeview
    and as clickable buttons.
    """
    def __init__(self, master=None, headers=None, rows=None, app_instance=None, **kwargs):
        """
        Initializes the MarkersDisplayTab.

        Inputs:
            master (tk.Widget): The parent widget.
            headers (list): A list of column headers for the marker data.
            rows (list): A list of dictionaries, where each dictionary represents
                         a row of marker data with keys matching the headers.
            app_instance (App): The main application instance, used for accessing
                                shared state like instrument connection and focus width.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Initializing MarkersDisplayTab...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else [] # Store full rows data
        self.app_instance = app_instance # Store reference to the main app instance
        # self.console_print_func is removed, using console_log directly

        # Apply style to the main frame (this style is now defined globally in main_app.py)
        self.config(style="Markers.TFrame")
        self.last_selected_span_button = None # To keep track of the last selected span button
        self.current_span_hz = None # To store the currently active span value in Hz

        # Trace mode state variables
        self.live_mode_var = tk.BooleanVar(self, value=True) # Default to Live
        self.max_hold_mode_var = tk.BooleanVar(self, value=False)
        self.min_hold_mode_var = tk.BooleanVar(self, value=False)
        self.trace_mode_buttons = {} # To store references to trace mode buttons

        # For managing selected device button state across selections
        self.current_selected_device_button = None # Reference to the currently active button widget
        self.selected_device_unique_id = None
        self.current_selected_device_data = None # NEW: Store the full data of the selected device

        self.last_selected_poke_button = None # NEW: To track the state of the POKE button

        # --- NEW: Tkinter StringVars for displaying selected device info and RBW ---
        # (2025-07-31 17:00) Change: Added StringVars for displaying selected device details.
        # (2025-07-31 17:15) Change: Added StringVars for RBW display and manual frequency input.
        self.current_displayed_device_name_var = tk.StringVar(self, value="N/A")
        self.current_displayed_device_type_var = tk.StringVar(self, value="N/A")
        self.current_displayed_center_freq_var = tk.StringVar(self, value="N/A")
        self.current_span_var = tk.StringVar(self, value="N/A")
        self.current_trace_modes_var = tk.StringVar(self, value="N/A")
        self.current_rbw_var = tk.StringVar(self, value="N/A") # For displaying current RBW
        self.last_selected_rbw_button = None # To keep track of the last selected RBW button widget
        self.manual_freq_entry_var = tk.StringVar(self, value="") # For manual frequency input
        # --- END NEW ---

        self._create_widgets()


    def _create_widgets(self):
        """
        Creates the widgets for the Markers Display tab, including the treeview
        for zones/groups and the frame for device buttons.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Creating MarkersDisplayTab widgets...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Main frame for the split layout
        main_split_frame = ttk.Frame(self, style="Markers.TFrame") # Use ttk.Frame
        main_split_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(0, weight=1) # Allow main_split_frame to expand
        self.grid_columnconfigure(0, weight=1)

        # --- MODIFIED: Set fixed width for column 0 (Zones & Groups, Current Instrument Settings) ---
        main_split_frame.grid_columnconfigure(0, weight=0, minsize=300) # Left half (treeview and settings) fixed 300px
        main_split_frame.grid_columnconfigure(1, weight=1) # Right half (device buttons, manual freq) expands
        # --- END MODIFIED ---

        main_split_frame.grid_rowconfigure(0, weight=1) # Top row for treeview and device buttons

        # NEW: Updated grid_rowconfigure for the new layout
        main_split_frame.grid_rowconfigure(1, weight=0) # Row for Span control (fixed height)
        main_split_frame.grid_rowconfigure(2, weight=0) # Row for Current settings (left) and Manual freq (right)
        main_split_frame.grid_rowconfigure(3, weight=0) # Row for Trace mode controls (fixed height)
        main_split_frame.grid_rowconfigure(4, weight=0) # Row for RBW control (full width)


        # Left Half: Treeview for Zones and Groups
        tree_frame = ttk.LabelFrame(main_split_frame, text="Zones & Groups", padding=(1,1,1,1), style='Dark.TLabelframe')
        # --- MODIFIED: Ensure tree_frame uses fixed width by being in column 0 with minsize ---
        tree_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
        # --- END MODIFIED ---
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.zone_group_tree = ttk.Treeview(tree_frame, show="tree", style="Markers.Inner.Treeview")
        self.zone_group_tree.pack(fill=tk.BOTH, expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.zone_group_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.zone_group_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Bind selection event to update device buttons
        self.zone_group_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right Half: Buttons for Devices
        buttons_frame = ttk.LabelFrame(main_split_frame, text="Devices", padding=(1,1,1,1), style='Dark.TLabelframe')
        buttons_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)

        # Removed: self.buttons_canvas = tk.Canvas(...)
        # Removed: buttons_scrollbar = ttk.Scrollbar(...)
        # Removed: self.buttons_canvas.configure(yscrollcommand=...)
        # Removed: self.buttons_canvas.bind('<Configure>', ...)

        # Direct placement of inner_buttons_frame within buttons_frame
        self.inner_buttons_frame = ttk.Frame(buttons_frame, style='Dark.TFrame') # Parent changed from self.buttons_canvas to buttons_frame
        self.inner_buttons_frame.pack(fill=tk.BOTH, expand=True) # Use pack instead of create_window

        # Configure columns for the grid layout within inner_buttons_frame
        # Changed to 2 columns for buttons to make them wider
        self.inner_buttons_frame.grid_columnconfigure(0, weight=1)
        self.inner_buttons_frame.grid_columnconfigure(1, weight=1)

        # Now call _populate_zone_group_tree after inner_buttons_frame is initialized
        self._populate_zone_group_tree()

        # Initially populate with an empty list to clear any previous buttons
        self._populate_device_buttons([])


        # --- Span Control Buttons Frame (NEW: Now at row 1, full width, with title) ---
        span_control_frame = ttk.LabelFrame(main_split_frame, text="Span Control", padding=(1,1,1,1), style="Dark.TLabelframe")
        span_control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Configure columns for the buttons within span_control_frame
        for i in range(len(SPAN_OPTIONS)):
            span_control_frame.grid_columnconfigure(i, weight=1)

        # Create buttons
        self.span_buttons = {}
        col = 0
        # Iterate through SPAN_OPTIONS to create buttons
        for text_key, span_hz_value in SPAN_OPTIONS.items():
            # Format the second line of the button text
            display_value = f"{span_hz_value / MHZ_TO_HZ:.3f} MHz" if span_hz_value >= MHZ_TO_HZ else f"{span_hz_value / 1000:.0f} KHz"
            button_text = f"{text_key}\n{display_value}"

            btn = ttk.Button(span_control_frame, text=button_text, style="Markers.Config.Default.TButton", # Default style for unselected
                             command=lambda s=span_hz_value, t=text_key: self._on_span_button_click(s, self.span_buttons[t], t)) # Pass span_hz, button_widget, and text_key

            # Store button reference before gridding to ensure it's in the dict for the lambda
            self.span_buttons[text_key] = btn
            btn.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            col += 1

        # Set "Normal" as the initially selected button and span
        # Find the "Normal" button and its span value
        normal_span_hz = SPAN_OPTIONS["Normal"]
        normal_button_widget = self.span_buttons["Normal"]
        self._on_span_button_click(normal_span_hz, normal_button_widget, "Normal")


        # --- NEW: Current Instrument Settings & Manual Frequency Control Frames (Now at row 2, with titles) ---
        self.current_settings_frame = ttk.LabelFrame(main_split_frame, text="Current Instrument Settings", padding=(1,1,1,1), style="Dark.TLabelframe")
        # --- MODIFIED: Ensure current_settings_frame uses fixed width by being in column 0 with minsize ---
        self.current_settings_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5) # Left half of row 2
        # --- END MODIFIED ---
        self.current_settings_frame.grid_columnconfigure(0, weight=1) # Allow label to expand
        self.current_settings_frame.grid_columnconfigure(1, weight=1) # For values

        ttk.Label(self.current_settings_frame, text="Span:", style="Markers.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_span_label = ttk.Label(self.current_settings_frame, textvariable=self.current_span_var, style="Markers.TLabel") # Use textvariable
        self.current_span_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="Trace Modes:", style="Markers.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.current_trace_modes_label = ttk.Label(self.current_settings_frame, textvariable=self.current_trace_modes_var, style="Markers.TLabel") # Use textvariable
        self.current_trace_modes_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="RBW:", style="Markers.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.current_rbw_label = ttk.Label(self.current_settings_frame, textvariable=self.current_rbw_var, style="Markers.TLabel")
        self.current_rbw_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)


        ttk.Label(self.current_settings_frame, text="Selected Name:", style="Markers.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.current_name_label = ttk.Label(self.current_settings_frame, textvariable=self.current_displayed_device_name_var, style="Markers.TLabel")
        self.current_name_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="Selected Device:", style="Markers.TLabel").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.current_device_label = ttk.Label(self.current_settings_frame, textvariable=self.current_displayed_device_type_var, style="Markers.TLabel")
        self.current_device_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(self.current_settings_frame, text="Selected Freq (MHz):", style="Markers.TLabel").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.current_freq_label = ttk.Label(self.current_settings_frame, textvariable=self.current_displayed_center_freq_var, style="Markers.TLabel")
        self.current_freq_label.grid(row=5, column=1, sticky="w", padx=5, pady=2)


        # Manual Frequency Control Frame (Right half of row 2, with title)
        manual_freq_frame = ttk.LabelFrame(main_split_frame, text="Manual Frequency Control", padding=(1,1,1,1), style="Dark.TLabelframe")
        manual_freq_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5) # Right half of row 2
        manual_freq_frame.grid_columnconfigure(0, weight=1) # Allow entry to expand

        self.manual_freq_entry = ttk.Entry(manual_freq_frame, textvariable=self.manual_freq_entry_var, width=20, style="Markers.TEntry")
        self.manual_freq_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.poke_button = ttk.Button(manual_freq_frame, text="POKE", style="Markers.Config.Default.TButton", command=self._on_poke_button_click)
        self.poke_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")


        # --- Trace Mode Control Buttons Frame (NEW: Now at row 3, full width, with title) ---
        trace_mode_control_frame = ttk.LabelFrame(main_split_frame, text="Trace Mode Control", padding=(1,1,1,1), style="Dark.TLabelframe")
        trace_mode_control_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Configure columns for the buttons within trace_mode_control_frame
        trace_mode_control_frame.grid_columnconfigure(0, weight=1)
        trace_mode_control_frame.grid_columnconfigure(1, weight=1)
        trace_mode_control_frame.grid_columnconfigure(2, weight=1)

        # Create Trace Mode buttons
        # The command will toggle the associated BooleanVar and then call the update logic
        btn_live = ttk.Button(trace_mode_control_frame, text="Live", style="Markers.Config.Default.TButton",
                              command=lambda: self._on_trace_mode_button_click("Live"))
        btn_max_hold = ttk.Button(trace_mode_control_frame, text="Max Hold", style="Markers.Config.Default.TButton",
                                  command=lambda: self._on_trace_mode_button_click("Max Hold"))
        btn_min_hold = ttk.Button(trace_mode_control_frame, text="Min Hold", style="Markers.Config.Default.TButton",
                                  command=lambda: self._on_trace_mode_button_click("Min Hold"))

        self.trace_mode_buttons["Live"] = {"button": btn_live, "var": self.live_mode_var}
        self.trace_mode_buttons["Max Hold"] = {"button": btn_max_hold, "var": self.max_hold_mode_var}
        self.trace_mode_buttons["Min Hold"] = {"button": btn_min_hold, "var": self.min_hold_mode_var}

        btn_live.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        btn_max_hold.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        btn_min_hold.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

        # Initialize button colors based on default states (Live is True, others False)
        self._update_trace_mode_button_styles() # Call this to set initial colors


        # --- Resolution Bandwidth (RBW) Control Frame (NEW: Now at row 4, full width, with title) ---
        rbw_control_frame = ttk.LabelFrame(main_split_frame, text="Resolution Bandwidth (RBW)", padding=(1,1,1,1), style="Dark.TLabelframe")
        rbw_control_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5) # Full width of row 4

        # Configure columns for the RBW buttons
        for i in range(len(RBW_OPTIONS)):
            rbw_control_frame.grid_columnconfigure(i, weight=1)

        self.rbw_buttons = {}
        col = 0
        for text_key, rbw_hz_value in RBW_OPTIONS.items():
            btn = ttk.Button(rbw_control_frame, text=text_key, style="Markers.Config.Default.TButton",
                             command=lambda r=rbw_hz_value, t=text_key: self._on_rbw_button_click(r, self.rbw_buttons[t], t))
            self.rbw_buttons[text_key] = btn
            btn.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            col += 1

        # Set a default RBW selection (e.g., "1 MHz")
        default_rbw_key = "1 MHz"
        if default_rbw_key in self.rbw_buttons:
            self._on_rbw_button_click(RBW_OPTIONS[default_rbw_key], self.rbw_buttons[default_rbw_key], default_rbw_key)


    def _populate_zone_group_tree(self):
        """
        Populates the Treeview with zones and groups only.
        The tree structure will be: ZONE -> GROUP.
        If GROUP is empty, it will not create a group node, but the markers will still be associated with the zone.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Populating zone/group tree (2 levels)...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        self.zone_group_tree.delete(*self.zone_group_tree.get_children()) # Clear existing data

        # Nested dictionary to store data: {ZONE: {GROUP: [rows]}}
        nested_grouped_data = {}

        for row in self.rows:
            zone = row.get('ZONE', 'Uncategorized Zone').strip()
            group = row.get('GROUP', '').strip() # Get group, strip whitespace, default to empty string

            if zone not in nested_grouped_data:
                nested_grouped_data[zone] = {}

            # If group is empty, use a placeholder key to store markers directly under the zone.
            # Otherwise, use the group name.
            group_key = group if group else "__NO_GROUP__"

            if group_key not in nested_grouped_data[zone]:
                nested_grouped_data[zone][group_key] = []

            nested_grouped_data[zone][group_key].append(row)

        for zone_name in sorted(nested_grouped_data.keys()):
            zone_id = self.zone_group_tree.insert("", "end", text=zone_name, open=True, tags=('zone',))

            for group_key in sorted(nested_grouped_data[zone_name].keys()):
                if group_key != "__NO_GROUP__": # Only create a group node if a group name exists
                    self.zone_group_tree.insert(zone_id, "end", text=group_key, open=True, tags=('group',))
                # No leaf nodes for individual markers here, as per the new requirement.
                # The markers will be retrieved directly from the selected zone/group in _on_tree_select.

        # Clear device buttons when tree is repopulated
        # Removed: self._populate_device_buttons([]) # This was causing devices to disappear

    def _on_tree_select(self, event):
        """
        Handles selection events in the zone/group treeview.
        Populates the device buttons based on the selected zone or group.
        Manages selected device button state, preserving selection if device is still present.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Tree item selected...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        selected_items = self.zone_group_tree.selection()

        # Get the data for the newly selected tree item(s)
        selected_rows_data = []
        if selected_items:
            for item_id in selected_items:
                item_tags = self.zone_group_tree.item(item_id, 'tags')
                if 'zone' in item_tags:
                    zone_name = self.zone_group_tree.item(item_id, 'text')
                    for row in self.rows:
                        if row.get('ZONE', '').strip() == zone_name:
                            selected_rows_data.append(row)
                elif 'group' in item_tags:
                    group_name = self.zone_group_tree.item(item_id, 'text')
                    parent_id = self.zone_group_tree.parent(item_id)
                    zone_name = self.zone_group_tree.item(parent_id, 'text')
                    for row in self.rows:
                        if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == group_name:
                            selected_rows_data.append(row)

        # Check if the previously selected device is still in the new list of devices
        # If not, clear the stored selection
        if self.selected_device_unique_id:
            is_prev_selected_device_still_present = False
            for device_data in selected_rows_data:
                unique_device_id_candidate = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{device_data.get('FREQ', '')}"
                if unique_device_id_candidate == self.selected_device_unique_id:
                    is_prev_selected_device_still_present = True
                    break

            if not is_prev_selected_device_still_present:
                debug_log(f"Previously selected device (ID: {self.selected_device_unique_id}) is no longer in the displayed list. Clearing selection.",
                            file=current_file, version=current_version, function=current_function)
                if self.current_selected_device_button:
                    self.current_selected_device_button.config(style="DeviceButton.TButton") # Revert old button to neutral
                    debug_log(f"Resetting previously selected device button '{self.current_selected_device_button.cget('text').splitlines()[0]}' style to DeviceButton.TButton (Default Blue).",
                                file=current_file, version=current_version, function=current_function)
                self.current_selected_device_button = None
                self.selected_device_unique_id = None
                self.current_selected_device_data = None
        else:
            # If no device was previously selected, just ensure the visual state is clear
            if self.current_selected_device_button: # This should ideally be None if selected_device_unique_id is None
                self.current_selected_device_button.config(style="DeviceButton.TButton")
                self.current_selected_device_button = None
            self.current_selected_device_data = None # Ensure data is clear if no unique ID

        # Also reset Poke button style if it was selected, as tree selection implies
        # looking at specific devices, not a manual poke.
        if self.last_selected_poke_button:
            self.last_selected_poke_button.config(style="Markers.TButton")
            debug_log(f"Resetting POKE button style to Markers.TButton (Default Blue) due to tree selection change.",
                        file=current_file, version=current_version, function=current_function)
            self.last_selected_poke_button = None


        self._populate_device_buttons(selected_rows_data)

        # After populating, if a device was previously selected and is still in the new list,
        # its button should now be highlighted by _populate_device_buttons.
        # We also need to update the current settings display based on the *current* selected device,
        # which might be the one that was just re-highlighted.
        self._update_current_settings_display() # Call this to refresh the display based on potentially re-selected device.

    def _populate_device_buttons(self, devices_to_display):
        """
        Function Description:
        Populates the right-hand frame with clickable buttons for each device.
        Buttons will be approximately 50% of the device box width, and display
        NAME, DEVICE, and FREQ (in MHz) on three lines.
        Also handles visual feedback for selected and actively scanned devices.

        Inputs to this function:
        - devices_to_display (list): A list of dictionaries, each representing a device.

        Process of this function:
        1. Clears existing buttons.
        2. If no devices, displays a message.
        3. For each device:
            a. Creates a unique ID.
            b. Formats button text.
            c. Creates a button.
            d. Determines button style:
                - "ActiveScan.TButton" (green) if currently being scanned.
                - "Markers.SelectedButton.TButton" (new orange) if currently selected.
                - "DeviceButton.TButton" (default blue) otherwise.
            e. Grids the button.
        4. (Removed: Updates scroll region - no canvas)

        Outputs of this function:
        - Populates the device buttons frame with styled buttons.

        (2025-07-31 17:00) Change: Added logic to style buttons based on active scan status.
        (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
        (2025-07-31 23:50) Change: Removed canvas-related scrollregion updates.
        (2025-08-01 00:45) Change: Implemented dynamic column adjustment for device buttons.
                                If more than 20 devices, aims for 3 rows. Otherwise, 2 columns.
        (2025-08-01 00:50) Change: Corrected dynamic column adjustment to always be 3 columns if > 20 devices,
                                and 2 columns if <= 20 devices.
        (2025-08-01 2200.1) Change: Updated to use debug_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Populating device buttons with {len(devices_to_display)} devices...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear existing buttons
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()

        if not devices_to_display:
            ttk.Label(self.inner_buttons_frame, text="Select a zone or group from the left to display devices.",
                      background="#1e1e1e", foreground="#cccccc", style='Markers.TLabel').grid(row=0, column=0, columnspan=2, padx=5, pady=5)
            self.inner_buttons_frame.update_idletasks()
            return

        # Determine the number of columns based on the number of devices
        num_devices = len(devices_to_display)
        if num_devices > 20:
            num_columns = 3 # Always 3 columns if more than 20 devices
            debug_log(f"More than 20 devices ({num_devices}). Using 3 columns.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            num_columns = 2 # Default to 2 columns for 20 or fewer devices
            debug_log(f"20 or fewer devices ({num_devices}). Using 2 columns.",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        # Clear all previous column weights to ensure clean reconfiguration
        # Get the current maximum column index that might have a weight configured
        current_max_col = 0
        if self.inner_buttons_frame.grid_size():
            current_max_col = self.inner_buttons_frame.grid_size()[0]

        for i in range(current_max_col):
            self.inner_buttons_frame.grid_columnconfigure(i, weight=0) # Reset all to 0

        # Configure only the necessary columns with weight=1
        for i in range(num_columns):
            self.inner_buttons_frame.grid_columnconfigure(i, weight=1)


        row_idx = 0
        col_idx = 0
        self._current_displayed_devices = devices_to_display # Store for update_device_button_styles
        for i, device_data in enumerate(devices_to_display):
            name = device_data.get('NAME', '').strip()
            device = device_data.get('DEVICE', '').strip()
            freq_mhz = device_data.get('FREQ')

            if freq_mhz is not None:
                try:
                    # Create a unique ID for this device
                    unique_device_id = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{freq_mhz}"

                    # Format button text for three lines
                    display_name = name if name else "N/A Name"
                    display_device = device if device and device.lower() != "none - none - n/a" else "N/A Device"

                    # Format frequency for display without decimal if it's a whole number
                    display_freq_mhz = int(float(freq_mhz)) if float(freq_mhz) == int(float(freq_mhz)) else f"{float(freq_mhz):.3f}"
                    button_text = f"{display_name}\n{display_device}\n{display_freq_mhz} MHz"

                    # Use "DeviceButton.TButton" for the unselected state
                    btn = ttk.Button(self.inner_buttons_frame, text=button_text, style="DeviceButton.TButton",
                                     command=lambda d=device_data, btn_w=None: self._on_device_button_click(d, btn_w))

                    # Pass the button widget reference to the lambda after it's created
                    btn.configure(command=lambda d=device_data, u_id=unique_device_id, b_w=btn: self._on_device_button_click(d, b_w))

                    # --- NEW: Determine button style based on selection and active scan status ---
                    button_style = "DeviceButton.TButton" # Default style

                    is_currently_scanned = False
                    if self.app_instance and hasattr(self.app_instance, 'scanning_active_var') and self.app_instance.scanning_active_var.get():
                        if hasattr(self.app_instance, 'current_scanned_device_unique_id') and self.app_instance.current_scanned_device_unique_id.get() == unique_device_id:
                            is_currently_scanned = True

                    if is_currently_scanned:
                        button_style = "ActiveScan.TButton" # Green with black font for active scan
                        debug_log(f"Device button '{display_name}' (ID: {unique_device_id}) styled as ActiveScan.TButton (Green).",
                                    file=current_file, version=current_version, function=current_function)
                    elif unique_device_id == self.selected_device_unique_id:
                        button_style = "Markers.SelectedButton.TButton" # Use the new unified selected style
                        debug_log(f"Device button '{display_name}' (ID: {unique_device_id}) styled as Markers.SelectedButton.TButton (Orange).",
                                    file=current_file, version=current_version, function=current_function)
                        # Re-establish the reference to the currently selected button widget
                        self.current_selected_device_button = btn
                    else:
                        debug_log(f"Device button '{display_name}' (ID: {unique_device_id}) styled as DeviceButton.TButton (Default Blue).",
                                    file=current_file, version=current_version, function=current_function)

                    btn.config(style=button_style)
                    # --- END NEW ---

                    # Use sticky="nsew" to make buttons expand within their grid cells
                    btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

                    col_idx += 1
                    if col_idx >= num_columns: # Wrap to next row based on calculated columns
                        col_idx = 0
                        row_idx += 1
                except ValueError:
                    debug_log(f"Could not convert frequency '{freq_mhz}' to float for button. Skipping. This bugger is a pain in the ass!",
                                file=current_file,
                                version=current_version,
                                function=current_function)
            else:
                debug_log(f"Frequency not found for device '{name}'. Skipping button. What the hell?!",
                            file=current_file,
                            version=current_version,
                            function=current_function)

        # Ensure rows also expand if needed, though buttons will dictate row height
        for r in range(row_idx + 1):
            self.inner_buttons_frame.grid_rowconfigure(r, weight=1)


        self.inner_buttons_frame.update_idletasks() # Ensure layout is updated before calculating scrollregion

    def _reset_span_button_styles(self, exclude_button=None):
        """Resets the style of all span buttons to default, except for the excluded one."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Resetting span button styles...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        for btn in self.span_buttons.values():
            if btn != exclude_button:
                btn.config(style="Markers.TButton")
        self.last_selected_span_button = exclude_button

    def _reset_rbw_button_styles(self, exclude_button=None):
        """Resets the style of all RBW buttons to default, except for the excluded one."""
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Resetting RBW button styles...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        for btn in self.rbw_buttons.values():
            if btn != exclude_button:
                btn.config(style="Markers.TButton")
        self.last_selected_rbw_button = exclude_button

    def _reset_device_button_styles(self, exclude_button=None):
        """
        Resets the style of all device buttons to default, except for the excluded one.
        This function is called BEFORE _populate_device_buttons to ensure a clean slate,
        or when a different control group (like POKE) is activated.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Resetting device button styles...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Iterate over all currently displayed buttons and reset their style
        for widget in self.inner_buttons_frame.winfo_children():
            if isinstance(widget, ttk.Button): # Only process buttons
                widget.config(style="DeviceButton.TButton")
                # Safely get button text for logging
                button_text_lines = widget.cget('text').splitlines()
                button_display_name = button_text_lines[0] if button_text_lines else "Unknown Button"
                debug_log(f"Resetting device button '{button_display_name}' style to DeviceButton.TButton (Default Blue).",
                            file=current_file, version=current_version, function=current_function)


        # Note: self.current_selected_device_button, self.selected_device_unique_id,
        # and self.current_selected_device_data are NOT cleared here.
        # They are managed by _on_tree_select or _on_device_button_click.


    def _on_device_button_click(self, device_data, clicked_button_widget):
        """
        Function Description:
        Callback for device buttons. Sets the instrument's center frequency and span,
        then sets the marker, and finally applies the trace modes.
        Manages button selection state.

        Inputs to this function:
        - device_data (dict): Dictionary containing the marker data (e.g., 'FREQ', 'NAME').
        - clicked_button_widget (ttk.Button): The Tkinter button widget that was clicked.

        Process of this function:
        1. Extracts frequency and name from `device_data`.
        2. Manages the visual selection state of the device buttons.
        3. If instrument is connected:
            a. Stores current trace mode states (Live, Max Hold, Min Hold).
            b. Blanks Max Hold and Min Hold traces if they were active.
            c. Sets the instrument's center frequency using `set_frequency_logic`.
            d. Sets the instrument's span using `set_span_logic` (based on `self.current_span_hz`).
            e. Sets the marker using `set_marker_logic` (which no longer reads back).
            f. Restores trace modes (Live, Max Hold, Min Hold) to their original states.
        4. Updates the GUI's current settings display.

        Outputs of this function:
        - Controls instrument frequency, span, marker, and trace modes.
        - Updates GUI display.

        (2025-07-31 16:30) Change: Implemented blanking and restoration of hold traces before/after freq/span change.
        (2025-07-31 17:00) Change: Updated to display selected device info in the settings box.
        (2025-07-31 23:00) Change: Refined button style management to avoid global resets.
        (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
        (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)

        freq_hz = float(device_data.get('FREQ')) * MHZ_TO_HZ
        name = device_data.get('NAME', '').strip() # Ensure name is stripped for display
        device_type = device_data.get('DEVICE', '').strip() # Get device type
        unique_device_id = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{device_data.get('FREQ', '')}"

        # Format frequency for display without decimal if it's a whole number
        display_freq_mhz = int(freq_hz / MHZ_TO_HZ) if (freq_hz / MHZ_TO_HZ) == int(freq_hz / MHZ_TO_HZ) else f"{freq_hz / MHZ_TO_HZ:.3f}"
        console_log(f"\nSetting instrument to '{name}' at {display_freq_mhz} MHz...", function=current_function)
        debug_log(f"Device button clicked: {name} at {freq_hz} Hz (ID: {unique_device_id})",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear only previous device selection and poke button
        self._reset_device_button_styles(exclude_button=clicked_button_widget)
        if self.last_selected_poke_button: # Reset poke button if it was active
            self.last_selected_poke_button.config(style="Markers.TButton")
            debug_log(f"POKE button style reset to Markers.TButton (Default Blue).",
                        file=current_file, version=current_version, function=current_function)
            self.last_selected_poke_button = None

        # Set new device selection
        clicked_button_widget.config(style="Markers.SelectedButton.TButton") # Select new button (orange)
        debug_log(f"Device button '{name}' (ID: {unique_device_id}) style set to Markers.SelectedButton.TButton (Orange).",
                    file=current_file, version=current_version, function=current_function)
        self.current_selected_device_button = clicked_button_widget
        self.selected_device_unique_id = unique_device_id
        self.current_selected_device_data = device_data # Store the full device data

        # --- NEW: Update displayed device info ---
        self.current_displayed_device_name_var.set(name if name else "N/A")
        self.current_displayed_device_type_var.set(device_type if device_type else "N/A")
        self.current_displayed_center_freq_var.set(display_freq_mhz)
        # --- END NEW ---

        if self.app_instance and self.app_instance.inst:
            inst = self.app_instance.inst

            # Store current trace mode states
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()

            # Blank Max Hold and Min Hold traces if they were active
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log) # Passed console_log

            # 1. Set Frequency
            set_frequency_logic(inst, freq_hz, console_log) # Passed console_log

            # 2. Set Span (using the currently selected span or default)
            span_to_use_hz = self.current_span_hz if self.current_span_hz is not None else \
                             float(self.app_instance.desired_default_focus_width_var.get()) * MHZ_TO_HZ
            set_span_logic(inst, span_to_use_hz, console_log) # Passed console_log

            # 3. Set Marker (no read back)
            set_marker_logic(inst, freq_hz, name, console_log) # Passed console_log

            # 4. Restore Trace Modes to their original states
            set_trace_modes_logic(inst,
                                  original_live_mode,
                                  original_max_hold_mode,
                                  original_min_hold_mode,
                                  console_log) # Passed console_log

            self._update_current_settings_display() # Update display after all commands
        else:
            console_log("⚠️ Warning: Cannot set focus frequency: Instrument not connected.", function=current_function)
            debug_log(f"Cannot set focus frequency: Instrument not connected. Fucking useless!",
                        file=current_file,
                        version=current_version,
                        function=current_function)


    def _on_span_button_click(self, span_hz, button_widget, button_text_key):
        """
        Function Description:
        Callback for span control buttons. Changes the instrument's span and
        then applies the current trace modes. Toggles button color/font.

        Inputs to this function:
        - span_hz (float): The desired span in Hz.
        - button_widget (ttk.Button): The Tkinter button widget that was clicked.
        - button_text_key (str): The text key associated with the button (e.g., "Normal", "Wide").

        Process of this function:
        1. Updates the stored internal `self.current_span_hz`.
        2. Toggles the visual style of the span buttons.
        3. If instrument is connected:
            a. Stores current trace mode states (Live, Max Hold, Min Hold).
            b. Blanks Max Hold and Min Hold traces if they were active.
            c. Sets the instrument's span using `set_span_logic`.
            d. Optionally re-centers the frequency if a device is selected.
            e. Restores trace modes (Live, Max Hold, Min Hold) to their original states.
        4. Updates the GUI's current settings display.

        Outputs of this function:
        - Controls instrument span and trace modes.
        - Updates GUI display.

        (2025-07-31 16:30) Change: Implemented blanking and restoration of hold traces before/after span change.
        (2025-07-31 23:00) Change: Refined button style management to avoid global resets.
        (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
        (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        console_log(f"Setting span to {span_hz / MHZ_TO_HZ:.3f} MHz...", function=current_function)
        debug_log(f"Span button clicked: Setting span to {span_hz} Hz (Button: {button_text_key})",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear only other span button selections
        self._reset_span_button_styles(exclude_button=button_widget)

        # Update the stored current span
        self.current_span_hz = span_hz

        # Toggle button styles for visual feedback (orange/blue accordingly)
        button_widget.config(style="Markers.SelectedButton.TButton") # Use the new unified selected style
        self.last_selected_span_button = button_widget


        # If the instrument is connected, send the commands
        if self.app_instance and self.app_instance.inst:
            inst = self.app_instance.inst

            # Store current trace mode states
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()

            # Blank Max Hold and Min Hold traces if they are active
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log) # Passed console_log

            # 1. Set Span
            set_span_logic(inst, span_hz, console_log) # Passed console_log

            # Optional: Re-center if a device is currently selected
            if self.current_selected_device_data:
                try:
                    center_freq_to_use = float(self.current_selected_device_data.get('FREQ')) * MHZ_TO_HZ
                    set_frequency_logic(inst, center_freq_to_use, console_log) # Passed console_log
                    console_log(f"Re-centering on selected device at {center_freq_to_use / MHZ_TO_HZ:.3f} MHz with new span.", function=current_function)
                except ValueError:
                    debug_log(f"Could not convert selected device frequency to float for re-centering. What a fumbling idiot of a bug!",
                                file=current_file,
                                version=current_version,
                                function=current_function)

            # 2. Restore Trace Modes to their original states
            set_trace_modes_logic(inst,
                                  original_live_mode,
                                  original_max_hold_mode,
                                  original_min_hold_mode,
                                  console_log) # Passed console_log

            self._update_current_settings_display() # Update display after span change
        else:
            console_log("⚠️ Warning: Cannot set span: Instrument not connected.", function=current_function)
            debug_log(f"Cannot set span: Instrument not connected. What the hell is this thing doing?!",
                        file=current_file,
                        version=current_version,
                        function=current_function)


    # --- NEW: RBW Button Click Handler ---
    # (2025-07-31 17:15) Change: Added new RBW button click handler.
    # (2025-07-31 23:00) Change: Refined button style management to avoid global resets.
    # (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
    # (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
    def _on_rbw_button_click(self, rbw_hz, button_widget, button_text_key):
        """
        Callback for RBW control buttons. Changes the instrument's RBW.
        Toggles button color/font (radio-button like behavior).

        Inputs to this function:
        - rbw_hz (float): The desired RBW in Hz.
        - button_widget (ttk.Button): The Tkinter button widget that was clicked.
        - button_text_key (str): The text key associated with the button (e.g., "1 MHz").

        Process of this function:
        1. Updates the stored internal `self.current_rbw_var`.
        2. Toggles the visual style of the RBW buttons (only one selected at a time).
        3. If the instrument is connected:
            a. Stores current trace mode states.
            b. Blanks Max Hold and Min Hold traces if they were active.
            c. Sets the instrument's RBW using `set_rbw_logic`.
            d. Restores trace modes.
        4. Updates the GUI's current settings display.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        console_log(f"Setting RBW to {button_text_key}...", function=current_function)
        debug_log(f"RBW button clicked: Setting RBW to {rbw_hz} Hz (Button: {button_text_key})",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear only other RBW button selections
        self._reset_rbw_button_styles(exclude_button=button_widget)

        # Update the stored current RBW
        self.current_rbw_var.set(button_text_key)

        # Toggle button styles for visual feedback (orange/blue accordingly)
        button_widget.config(style="Markers.SelectedButton.TButton") # Use the new unified selected style
        self.last_selected_rbw_button = button_widget # Store reference to the newly selected button

        # If the instrument is connected, send the commands
        if self.app_instance and self.app_instance.inst:
            inst = self.app_instance.inst

            # Store current trace mode states
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()

            # Blank Max Hold and Min Hold traces if they are active
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log) # Passed console_log

            # Set RBW
            set_rbw_logic(inst, rbw_hz, console_log) # Passed console_log

            # Restore Trace Modes to their original states
            set_trace_modes_logic(inst,
                                  original_live_mode,
                                  original_max_hold_mode,
                                  original_min_hold_mode,
                                  console_log) # Passed console_log

            self._update_current_settings_display() # Update display after RBW change
        else:
            console_log("⚠️ Warning: Cannot set RBW: Instrument not connected.", function=current_function)
            debug_log(f"Cannot set RBW: Instrument not connected. What the hell is this thing doing?!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
    # --- END NEW ---

    # --- NEW: Poke Button Click Handler ---
    # (2025-07-31 17:15) Change: Added new poke button click handler.
    # (2025-07-31 23:00) Change: Refined button style management to avoid global resets.
    # (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style and fix POKE display.
    # (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
    def _on_poke_button_click(self):
        """
        Callback for the POKE button. Sets the instrument's center frequency
        based on the manual input, treating it like a 'wild device'.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        manual_freq_str = self.manual_freq_entry_var.get().strip()

        if not manual_freq_str:
            console_log("⚠️ Warning: Please enter a frequency in the manual control box.", function=current_function)
            debug_log(f"Manual frequency input is empty. You gotta put something in, you know?",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        try:
            manual_freq_mhz = float(manual_freq_str)
            freq_hz = manual_freq_mhz * MHZ_TO_HZ
        except ValueError:
            console_log("❌ Error: Invalid frequency entered. Please enter a numerical value in MHz.", function=current_function)
            debug_log(f"Invalid manual frequency input: '{manual_freq_str}'. What the hell is this garbage?!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            return

        console_log(f"\nPOKE: Setting instrument frequency to {manual_freq_mhz:.3f} MHz (Manual Input)...", function=current_function)
        debug_log(f"POKE button clicked: Setting frequency to {freq_hz} Hz from manual input.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Clear existing device selection and reset its style
        self._reset_device_button_styles(exclude_button=None) # Ensure no device button is selected

        # Reset previously selected POKE button if it was different
        if self.last_selected_poke_button and self.last_selected_poke_button != self.poke_button:
            self.last_selected_poke_button.config(style="Markers.TButton")
            debug_log(f"Previous POKE button style reset to Markers.TButton (Default Blue).",
                        file=current_file, version=current_version, function=current_function)


        # Highlight the POKE button
        self.poke_button.config(style="Markers.SelectedButton.TButton") # Use the new unified selected style
        debug_log(f"POKE button style set to Markers.SelectedButton.TButton (Orange).",
                    file=current_file, version=current_version, function=current_function)
        self.last_selected_poke_button = self.poke_button


        if self.app_instance and self.app_instance.inst:
            inst = self.app_instance.inst

            # Store current trace mode states
            original_live_mode = self.live_mode_var.get()
            original_max_hold_mode = self.max_hold_mode_var.get()
            original_min_hold_mode = self.min_hold_mode_var.get()

            # Blank Max Hold and Min Hold traces if they were active
            if original_max_hold_mode or original_min_hold_mode:
                blank_hold_traces_logic(inst, console_log) # Passed console_log

            # Set Frequency (like a wild device, no span or marker change implied by 'poke')
            set_frequency_logic(inst, freq_hz, console_log) # Passed console_log

            # Restore Trace Modes to their original states
            set_trace_modes_logic(inst,
                                  original_live_mode,
                                  original_max_hold_mode,
                                  original_min_hold_mode,
                                  console_log) # Passed console_log

            # Update the displayed selected frequency to reflect the manually set one
            self.current_displayed_center_freq_var.set(f"{manual_freq_mhz:.3f}")
            # FIX: Corrected string formatting for POKE display
            self.current_displayed_device_name_var.set(f"POKE: {manual_freq_mhz:.3f}") # Set to "POKE: [freq]" as requested
            self.current_displayed_device_type_var.set("N/A") # Clear device type for manual input

            self._update_current_settings_display() # Update display after all commands
        else:
            console_log("⚠️ Warning: Cannot POKE frequency: Instrument not connected.", function=current_function)
            debug_log(f"Cannot POKE frequency: Instrument not connected. Fucking useless!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
    # --- END NEW ---


    def _on_trace_mode_button_click(self, mode_name):
        """
        Function Description:
        Callback for trace mode buttons. Toggles the state of the clicked button's
        associated BooleanVar and then updates the instrument's trace modes.

        Inputs to this function:
        - mode_name (str): The name of the trace mode (e.g., "Live", "Max Hold").

        Process of this function:
        1. Toggles the internal BooleanVar for the clicked mode.
        2. Updates the visual style of the trace mode buttons.
        3. If instrument is connected:
            a. Applies the updated trace modes using `set_trace_modes_logic`.
        4. Updates the GUI's current settings display.

        Outputs of this function:
        - Controls instrument trace modes.
        - Updates GUI display.

        (2025-07-31 16:15) Change: Modified to only apply trace modes.
                                Removed span and frequency setting from here.
        (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
        (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Trace mode button clicked: {mode_name}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Toggle the state of the clicked button's variable
        # Since these are independent toggles, just invert the current state
        if mode_name == "Live":
            self.live_mode_var.set(not self.live_mode_var.get())
        elif mode_name == "Max Hold":
            self.max_hold_mode_var.set(not self.max_hold_mode_var.get())
        elif mode_name == "Min Hold":
            self.min_hold_mode_var.set(not self.min_hold_mode_var.get())

        # Update button styles
        self._update_trace_mode_button_styles()

        # If instrument is connected, send the updated trace mode commands
        if self.app_instance and self.app_instance.inst:
            inst = self.app_instance.inst
            # Apply Trace Modes
            set_trace_modes_logic(inst,
                                  self.live_mode_var.get(),
                                  self.max_hold_mode_var.get(),
                                  self.min_hold_mode_var.get(),
                                  console_log) # Passed console_log
            self._update_current_settings_display() # NEW: Update display after trace mode change
        else:
            console_log("⚠️ Warning: Cannot set trace mode: Instrument not connected.", function=current_function)
            debug_log(f"Cannot set trace mode: Instrument not connected. This is a fucking joke!",
                        file=current_file,
                        version=current_version,
                        function=current_function)


    def _update_trace_mode_button_styles(self):
        """
        Updates the visual style of the trace mode buttons based on their BooleanVar states.
        (2025-07-31 23:30) Change: Updated to use new 'Markers.SelectedButton.TButton' style.
        (2025-08-01 2200.1) Change: Updated to use debug_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Updating trace mode button styles...",
                    file=current_file,
                    version=current_version,
                    function=current_function)
        for mode_name, data in self.trace_mode_buttons.items():
            button = data["button"]
            var = data["var"]
            if var.get():
                button.config(style="Markers.SelectedButton.TButton") # Use the new unified selected style
                debug_log(f"Trace mode button '{mode_name}' style set to Markers.SelectedButton.TButton (Orange).",
                            file=current_file, version=current_version, function=current_function)
            else:
                button.config(style="Markers.TButton") # Use default blue for unselected
                debug_log(f"Trace mode button '{mode_name}' style set to Markers.TButton (Default Blue).",
                            file=current_file, version=current_version, function=current_function)

    def _update_current_settings_display(self):
        """
        Function Description:
        Updates the labels in the "Current Instrument Settings" display box.
        This function now only updates the GUI based on internal state,
        it does NOT query the instrument. It also displays the selected device's
        name, type, frequency, and the current RBW.

        Inputs to this function:
        - None (uses internal Tkinter StringVars and self.current_selected_device_data)

        Process of this function:
        1. Updates the Span, Trace Modes, and RBW labels based on internal state.
        2. Updates the Selected Name, Selected Device, and Selected Freq labels
           based on `self.current_selected_device_data` or manual input. If no device
           is selected, these will display "N/A".

        Outputs of this function:
        - Updates the read-only entry fields and labels in the GUI.

        (2025-07-31 17:00) Change: Added logic to display selected device information.
        (2025-07-31 17:15) Change: Added RBW display.
        (2025-07-31 23:30) Change: Ensured POKE display is correct.
        (2025-08-01 2200.1) Change: Updated to use debug_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Updating current settings display (GUI only, no instrument query)...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Update Span Display
        display_span = "N/A"
        if self.current_span_hz is not None:
            if self.current_span_hz == 0.0: # Full Span case
                display_span = "Full Span"
            elif self.current_span_hz >= MHZ_TO_HZ:
                display_span = f"{self.current_span_hz / MHZ_TO_HZ:.3f} MHz"
            else:
                display_span = f"{self.current_span_hz / 1000:.0f} KHz"
        self.current_span_var.set(display_span)
        debug_log(f"Displaying Span: {display_span}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Update Trace Modes Display
        active_modes = []
        if self.live_mode_var.get():
            active_modes.append("Live")
        if self.max_hold_mode_var.get():
            active_modes.append("Max Hold")
        if self.min_hold_mode_var.get():
            active_modes.append("Min Hold")

        if active_modes:
            self.current_trace_modes_var.set(', '.join(active_modes))
            debug_log(f"Displaying Trace Modes: {', '.join(active_modes)}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            self.current_trace_modes_var.set("None Active")
            debug_log(f"Displaying Trace Modes: None Active",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        # Update RBW Display
        # self.current_rbw_var is already updated by _on_rbw_button_click
        # No need to re-calculate here, just ensure it's set.
        debug_log(f"Displaying RBW: {self.current_rbw_var.get()}",
                    file=current_file,
                    version=current_version,
                    function=current_function)


        # Update Selected Device Info Display
        # Prioritize POK if it's the last selected control
        if self.last_selected_poke_button and self.last_selected_poke_button.cget("style") == "Markers.SelectedButton.TButton":
            try:
                manual_freq_mhz = float(self.manual_freq_entry_var.get())
                self.current_displayed_device_name_var.set(f"POKE: {manual_freq_mhz:.3f}") # Corrected POKE display
                self.current_displayed_center_freq_var.set(f"{manual_freq_mhz:.3f}")
            except ValueError:
                self.current_displayed_device_name_var.set("POKE: Invalid Freq")
                self.current_displayed_center_freq_var.set("Invalid Freq")
            self.current_displayed_device_type_var.set("N/A")
            debug_log(f"Displaying Selected Device Info (POKE): Name='{self.current_displayed_device_name_var.get()}', Type='{self.current_displayed_device_type_var.get()}', Freq='{self.current_displayed_center_freq_var.get()}'",
                        file=current_file, version=current_version, function=current_function)
        elif self.current_selected_device_data:
            name = self.current_selected_device_data.get('NAME', '').strip()
            device_type = self.current_selected_device_data.get('DEVICE', '').strip()
            freq_mhz = self.current_selected_device_data.get('FREQ')

            display_name = name if name else "N/A"
            display_device = device_type if device_type else "N/A"
            display_freq = "N/A"
            if freq_mhz is not None:
                try:
                    display_freq = int(float(freq_mhz)) if float(freq_mhz) == int(float(freq_mhz)) else f"{float(freq_mhz):.3f}"
                except ValueError:
                    display_freq = "Invalid Freq"

            self.current_displayed_device_name_var.set(display_name)
            self.current_displayed_device_type_var.set(display_device)
            self.current_displayed_center_freq_var.set(display_freq)
            debug_log(f"Displaying Selected Device Info (Device Button): Name='{self.current_displayed_device_name_var.get()}', Type='{self.current_displayed_device_type_var.get()}', Freq='{self.current_displayed_center_freq_var.get()}'",
                        file=current_file, version=current_version, function=current_function)
        else:
            # If no device is selected and POKE is not active, clear display
            self.current_displayed_device_name_var.set("N/A")
            self.current_displayed_device_type_var.set("N/A")
            self.current_displayed_center_freq_var.set("N/A")
            debug_log(f"Displaying Selected Device Info: N/A (No device button clicked or POKE active).",
                        file=current_file, version=current_version, function=current_function)


    # Function Description:
    # This function is called by the Report Converter tab (or main app) to update
    # the marker data displayed in this tab's Treeview and device buttons.
    #
    # Inputs to this function:
    #   new_headers (list): A list of strings representing the new column headers.
    #   new_rows (list): A list of dictionaries, where each dictionary represents
    #                    a row of marker data with keys matching the headers.
    #
    # Process of this function:
    # 1. Update the instance's headers and rows with the new data.
    # 2. Re-populate the zone and group treeview based on the updated data.
    # 3. Clear and re-populate the device buttons to reflect the new data.
    #
    # Outputs of this function:
    #   None
    #
    # (2025-08-01 00:30) Change: Added public method to update marker data from external sources.
    # (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
    def update_marker_data(self, new_headers, new_rows):
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Received request to update marker data. Number of rows: {len(new_rows)}",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        self.headers = new_headers
        self.rows = new_rows
        self._populate_zone_group_tree() # This will clear and rebuild the tree
        # After populating the tree, the _on_tree_select event will handle populating the device buttons
        # if a zone/group is selected. If no selection is made, device buttons will remain empty, which is correct.
        # We need to re-evaluate if the previously selected device is still present after data update.
        if self.selected_device_unique_id:
            is_prev_selected_device_still_present = False
            for device_data in new_rows: # Check against the new_rows directly
                unique_device_id_candidate = f"{device_data.get('ZONE', '')}-{device_data.get('GROUP', '')}-{device_data.get('DEVICE', '')}-{device_data.get('NAME', '')}-{device_data.get('FREQ', '')}"
                if unique_device_id_candidate == self.selected_device_unique_id:
                    is_prev_selected_device_still_present = True
                    break
            if not is_prev_selected_device_still_present:
                debug_log(f"Previously selected device (ID: {self.selected_device_unique_id}) is no longer in the updated marker data. Clearing selection.",
                            file=current_file, version=current_version, function=current_function)
                self.current_selected_device_button = None
                self.selected_device_unique_id = None
                self.current_selected_device_data = None
        else:
            self.current_selected_device_button = None
            self.selected_device_unique_id = None
            self.current_selected_device_data = None

        self._populate_device_buttons([]) # Explicitly clear device buttons until a new selection is made by tree or click
        console_log(f"✅ Markers Display Tab updated with {len(new_rows)} markers.", function=current_function)


    def load_markers_from_file(self):
        """
        Function Description:
        Loads marker data from the MARKERS.CSV file located in the main app's
        internal MARKERS_FILE_PATH and updates the display. This method is designed to be
        called externally (e.g., by the main application instance) when the
        MARKERS.CSV file has changed.

        Inputs to this function:
        - None (relies on self.app_instance and its MARKERS_FILE_PATH)

        Process of this function:
        1. Dynamically determines the path to MARKERS.CSV using MARKERS_FILE_PATH.
        2. Checks if the file exists.
        3. If it exists, reads the CSV data (headers and rows).
        4. Calls `update_markers_data` to refresh the GUI with the new data.
        5. Handles file not found or loading errors, clearing the display if necessary.

        Outputs of this function:
        - Updates the GUI's marker display.
        - Prints messages to the console.

        (2025-07-31) Change: New method to allow external triggering of data loading.
        (2025-08-01) Change: Modified to use app_instance.MARKERS_FILE_PATH.
        (2025-08-01 2200.1) Change: Updated to use debug_log and console_log consistently.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        console_log("Attempting to load MARKERS.CSV to refresh display...", function=current_function)
        debug_log(f"load_markers_from_file called.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        markers_file_path = None
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            markers_file_path = self.app_instance.MARKERS_FILE_PATH
            debug_log(f"Determined MARKERS.CSV path: {markers_file_path}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            console_log("⚠️ Warning: App instance or MARKERS_FILE_PATH not available. Cannot load MARKERS.CSV.", function=current_function)
            debug_log(f"App instance or MARKERS_FILE_PATH not available. Cannot load MARKERS.CSV. This is a fucking mess!",
                        file=current_file,
                        version=current_version,
                        function=current_function)

        if markers_file_path and os.path.exists(markers_file_path):
            debug_log(f"MARKERS.CSV found at: {markers_file_path}",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            try:
                headers = []
                rows = []
                with open(markers_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    headers = reader.fieldnames
                    for row_data in reader:
                        rows.append(row_data)

                if headers and rows:
                    debug_log(f"Loaded {len(rows)} markers from MARKERS.CSV.",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    self.update_marker_data(headers, rows)
                    console_log(f"✅ Loaded {len(rows)} markers from MARKERS.CSV.", function=current_function)
                else:
                    debug_log(f"MARKERS.CSV is empty or has no data rows. Fucking useless!",
                                file=current_file,
                                version=current_version,
                                function=current_function)
                    console_log("ℹ️ Info: The MARKERS.CSV file was found but contains no data.", function=current_function)
                    self.update_marker_data([], []) # Clear any existing display
            except Exception as e:
                debug_log(f"Error loading MARKERS.CSV: {e}. This bugger is a pain in the ass!",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                console_log(f"❌ Error Loading Markers: An error occurred while loading MARKERS.CSV: {e}", function=current_function)
                self.update_marker_data([], []) # Clear any existing display on error
        else:
            debug_log(f"MARKERS.CSV not found or path not determined. Path: {markers_file_path}. What the hell?!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
            console_log("ℹ️ Info: MARKERS.CSV not found. Please generate a report first.", function=current_function)
            self.update_marker_data([], []) # Ensure display is clear if file doesn't exist

        self._update_current_settings_display() # Always update display based on internal state

    def _on_tab_selected(self, event):
        """
        Callback when this tab is selected. It now primarily ensures the display
        reflects the current state and triggers a load if the file exists.
        It no longer queries the instrument automatically.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        console_log("MarkersDisplayTab selected. Refreshing display.", function=current_function)
        debug_log(f"MarkersDisplayTab selected. Refreshing display.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Instead of loading directly, we'll call the dedicated load method.
        # This allows for external triggers to use the same loading logic.
        self.load_markers_from_file()

        # Always update display on tab selection, but based on internal state, not instrument query
        self._update_current_settings_display()

    # --- NEW: Method to update device button styles based on external scan status ---
    # (2025-07-31 17:00) Change: Added method to refresh device button styles.
    # (2025-08-01 2200.1) Change: Updated to use debug_log consistently.
    def update_device_button_styles(self):
        """
        Refreshes the styles of all device buttons based on current selection
        and active scanning status. This should be called by the main app
        when the scanning status changes.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__) # Changed to os.path.basename(__file__)
        debug_log(f"Refreshing device button styles due to external status change...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Re-call _populate_device_buttons with the last known list of devices
        # This will iterate through all displayed buttons and apply the correct style
        # based on self.selected_device_unique_id and the app_instance's scanning state.
        if hasattr(self, '_current_displayed_devices'):
            # Clear existing styles before repopulating to ensure correct state
            self._reset_device_button_styles(exclude_button=None) # Ensure all device buttons are reset
            self._populate_device_buttons(self._current_displayed_devices)
        else:
            # If for some reason _current_displayed_devices is not set (e.g., tab just loaded),
            # we can try to re-trigger the tree selection to rebuild the buttons.
            if self.zone_group_tree.selection():
                self._on_tree_select(None) # Re-trigger selection to force button re-population
            else:
                self._populate_device_buttons([]) # Clear if nothing selected
    # --- END NEW ---
