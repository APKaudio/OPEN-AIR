# tabs/Markers/tab_markers_child_display.py
#
# This file manages the Markers Display tab in the GUI, handling
# the display of extracted frequency markers, span control, and trace mode selection.
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
# Version 20250811.130322.6 (FIXED: The _on_poke_action now starts the marker trace loop automatically after setting the frequency, mirroring the behavior of the device buttons.)

current_version = "20250811.130322.6"
current_version_hash = (20250811 * 130322 * 6)

import tkinter as tk
from tkinter import ttk
import os
import csv
import inspect

from tabs.Markers.utils_markers import SPAN_OPTIONS, RBW_OPTIONS, set_span_logic, set_frequency_logic, set_trace_modes_logic, set_marker_logic, set_rbw_logic
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ
from src.program_style import COLOR_PALETTE
from src.settings_and_config.config_manager import save_config
from tabs.Markers.utils_markers_get_traces import get_marker_traces

class MarkersDisplayTab(ttk.Frame):
    """
    A Tkinter Frame that displays extracted frequency markers and provides instrument control.
    """
    def __init__(self, master=None, headers=None, rows=None, app_instance=None, **kwargs):
        # Function Description:
        # Initializes the MarkersDisplayTab.
        #
        # Inputs:
        #   master (tk.Widget): The parent widget.
        #   headers (list): Headers for the marker data.
        #   rows (list): Rows of marker data.
        #   app_instance (object): Reference to the main application instance.
        #
        # Outputs:
        #   None. Initializes the Tkinter frame and its state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing the MarkersDisplayTab.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        super().__init__(master, **kwargs)
        self.headers = headers if headers is not None else []
        self.rows = rows if rows is not None else []
        self.app_instance = app_instance

        self.selected_device_unique_id = None
        self.selected_device_name = None
        self.selected_device_freq = None # NEW: Store selected device frequency
        self.marker_trace_loop_job = None

        # --- State Variables for Controls ---
        self.span_var = self.app_instance.span_var
        self.rbw_var = self.app_instance.rbw_var
        self.poke_freq_var = tk.StringVar()
        self.trace_live_mode = self.app_instance.trace_live_var
        self.trace_max_hold_mode = self.app_instance.trace_max_hold_var
        self.trace_min_hold_mode = self.app_instance.trace_min_hold_var
        self.loop_delay_var = tk.StringVar(value="200")
        self.loop_counter_var = tk.IntVar(value=0)

        # --- Dictionaries to hold control buttons for styling ---
        self.span_buttons = {}
        self.rbw_buttons = {}
        self.trace_buttons = {}
        self.loop_stop_button = None # The start button is removed

        self._create_widgets()
        self.after(100, self.load_markers_from_file)
        self.after(150, self._update_control_styles)

    def _create_widgets(self):
        # Function Description:
        # Creates the widgets for the Markers Display tab.
        #
        # Inputs:
        #   None.
        #
        # Outputs:
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating widgets for the Markers Display tab.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_split_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_split_frame.grid(row=0, column=0, sticky="nsew")

        # --- Left Pane: Zone/Group Tree ---
        tree_frame = ttk.LabelFrame(main_split_frame, text="Zones & Groups", padding=5, style='Dark.TLabelframe')
        main_split_frame.add(tree_frame, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.zone_group_tree = ttk.Treeview(tree_frame, show="tree")
        self.zone_group_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.zone_group_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.zone_group_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.zone_group_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # --- Right Pane: Devices and Controls ---
        right_pane_frame = ttk.Frame(main_split_frame, style='TFrame')
        main_split_frame.add(right_pane_frame, weight=3)
        right_pane_frame.grid_rowconfigure(0, weight=1)
        right_pane_frame.grid_rowconfigure(1, weight=0)
        right_pane_frame.grid_columnconfigure(0, weight=1)

        # --- Device Buttons Frame ---
        self.buttons_frame = ttk.LabelFrame(right_pane_frame, text="Devices", padding=5, style='Dark.TLabelframe')
        self.buttons_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(self.buttons_frame, bg=COLOR_PALETTE['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.buttons_frame, orient="vertical", command=canvas.yview)
        self.inner_buttons_frame = ttk.Frame(canvas, style='Dark.TFrame')

        self.button_frame_window = canvas.create_window((0, 0), window=self.inner_buttons_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.inner_buttons_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind('<Configure>', self._on_canvas_configure)
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- Controls Notebook (Bottom Right) ---
        self.controls_notebook = ttk.Notebook(right_pane_frame, style='Markers.Child.TNotebook')
        self.controls_notebook.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # --- Span Tab ---
        span_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(span_tab, text="Span")
        for i, (name, span_hz) in enumerate(SPAN_OPTIONS.items()):
            val_text = self._format_hz(span_hz)
            btn_text = f"{name}\n{val_text}"

            btn = ttk.Button(span_tab, text=btn_text, command=lambda s=span_hz: self._on_span_button_click(s))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

            self.span_buttons[str(span_hz)] = btn
            span_tab.grid_columnconfigure(i, weight=1)

        # --- RBW Tab ---
        rbw_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(rbw_tab, text="RBW")
        for i, (name, rbw_hz) in enumerate(RBW_OPTIONS.items()):
            btn_text = f"{name}\n{rbw_hz / 1000:.0f} kHz"
            btn = ttk.Button(rbw_tab, text=btn_text, command=lambda r=rbw_hz: self._on_rbw_button_click(r))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.rbw_buttons[str(rbw_hz)] = btn
            rbw_tab.grid_columnconfigure(i, weight=1)

        # --- Trace Tab ---
        trace_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(trace_tab, text="Trace")
        trace_modes = [("Live", self.trace_live_mode), ("Max Hold", self.trace_max_hold_mode), ("Min Hold", self.trace_min_hold_mode)]
        for i, (name, var) in enumerate(trace_modes):
            btn = ttk.Button(trace_tab, text=name, command=lambda v=var: self._on_trace_button_click(v))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.trace_buttons[name] = btn
            trace_tab.grid_columnconfigure(i, weight=1)

        # --- Poke Tab ---
        poke_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(poke_tab, text="Poke")
        poke_tab.grid_columnconfigure(0, weight=1)
        poke_tab.grid_columnconfigure(1, weight=1)
        ttk.Entry(poke_tab, textvariable=self.poke_freq_var).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(poke_tab, text="POKE", command=self._on_poke_action, style='DeviceButton.Active.TButton').grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- Loop Tab (NEW) ---
        loop_tab = ttk.Frame(self.controls_notebook, style='TFrame', padding=10)
        self.controls_notebook.add(loop_tab, text="Loop")
        loop_tab.grid_columnconfigure(0, weight=1)
        loop_tab.grid_columnconfigure(1, weight=1)
        loop_tab.grid_columnconfigure(2, weight=1)

        ttk.Label(loop_tab, text="Delay (ms):").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Entry(loop_tab, textvariable=self.loop_delay_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        ttk.Label(loop_tab, text="Loop Count:").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(loop_tab, textvariable=self.loop_counter_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        # Removed the "Start Loop" button as per new instructions.
        self.loop_stop_button = ttk.Button(loop_tab, text="Stop Loop", command=self._stop_loop_action, state=tk.DISABLED)
        self.loop_stop_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew", columnspan=3)

    def _on_canvas_configure(self, event):
        # Function Description:
        # Ensures the inner frame width matches the canvas width.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Configuring canvas width.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        canvas = event.widget
        canvas.itemconfig(self.button_frame_window, width=event.width)

    def _format_hz(self, hz_val):
        # Function Description:
        # Formats a frequency in Hz to a human-readable string in MHz or kHz.
        try:
            hz = float(hz_val)
            if hz == 100 * MHZ_TO_HZ: return "100 MHz"
            if hz >= MHZ_TO_HZ:
                return f"{hz / MHZ_TO_HZ:.1f}".replace('.0', '') + " MHz"
            elif hz >= 1000:
                return f"{hz / 1000:.1f}".replace('.0', '') + " kHz"
            else:
                return f"{hz} Hz"
        except (ValueError, TypeError):
            return "N/A"

    def _update_control_styles(self):
        # Function Description:
        # Updates the style of control buttons to reflect the current state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating control button styles.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        current_span_str = self.span_var.get()
        for span_val, button in self.span_buttons.items():
            style = 'ControlButton.Active.TButton' if float(span_val) == float(current_span_str) else 'ControlButton.Inactive.TButton'
            button.configure(style=style)

        current_rbw_str = self.rbw_var.get()
        for rbw_val, button in self.rbw_buttons.items():
            style = 'ControlButton.Active.TButton' if float(rbw_val) == float(current_rbw_str) else 'ControlButton.Inactive.TButton'
            button.configure(style=style)

        self.trace_buttons['Live'].configure(style='ControlButton.Active.TButton' if self.trace_live_mode.get() else 'ControlButton.Inactive.TButton')
        self.trace_buttons['Max Hold'].configure(style='ControlButton.Active.TButton' if self.trace_max_hold_mode.get() else 'ControlButton.Inactive.TButton')
        self.trace_buttons['Min Hold'].configure(style='ControlButton.Active.TButton' if self.trace_min_hold_mode.get() else 'ControlButton.Inactive.TButton')
        
        # NEW: Update loop button state
        if self.marker_trace_loop_job:
            self.loop_stop_button.config(state=tk.NORMAL)
        else:
            self.loop_stop_button.config(state=tk.DISABLED)

    def _populate_zone_group_tree(self):
        # Function Description:
        # Populates the zone/group tree view. Devices with no group appear under the zone root.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating the zone and group tree view.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.zone_group_tree.delete(*self.zone_group_tree.get_children())
        nested_data = {}
        for row in self.rows:
            zone = row.get('ZONE', 'Uncategorized').strip()
            group = row.get('GROUP', '').strip()
            if zone not in nested_data: nested_data[zone] = {}
            if group not in nested_data[zone]: nested_data[zone][group] = []
            nested_data[zone][group].append(row)

        for zone, groups in sorted(nested_data.items()):
            zone_id = self.zone_group_tree.insert("", "end", text=zone, open=True)
            for group in sorted(groups.keys()):
                if group:
                    self.zone_group_tree.insert(zone_id, "end", text=group, open=True)

    def _on_tree_select(self, event):
        # Function Description:
        # Handles the selection of a tree item.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Handling a tree view selection.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        selected_item = self.zone_group_tree.selection()
        if self.marker_trace_loop_job:
            self.after_cancel(self.marker_trace_loop_job)
            self.marker_trace_loop_job = None
            self.loop_counter_var.set(0)
            self._update_control_styles()

        if not selected_item: return
        item = selected_item[0]
        parent_id = self.zone_group_tree.parent(item)
        text = self.zone_group_tree.item(item, 'text')
        devices = []
        if not parent_id:
            for row in self.rows:
                if row.get('ZONE', '').strip() == text: devices.append(row)
        else:
            zone_name = self.zone_group_tree.item(parent_id, 'text')
            for row in self.rows:
                if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == text:
                    devices.append(row)
        self._populate_device_buttons(devices)

    def _populate_device_buttons(self, devices):
        # Function Description:
        # Populates the device buttons frame.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Populating device buttons. There be {len(devices)} devices in this zone!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        for widget in self.inner_buttons_frame.winfo_children():
            widget.destroy()
        if not devices:
            ttk.Label(self.inner_buttons_frame, text="Select a zone or group.").pack()
            return

        num_columns = 3 if len(devices) > 10 else 2
        for i in range(num_columns): self.inner_buttons_frame.grid_columnconfigure(i, weight=1)

        for i, data in enumerate(devices):
            freq = data.get('FREQ', 'N/A')
            uid = f"{data.get('NAME', '')}-{freq}"
            text = f"{data.get('NAME', 'N/A')}\n{data.get('DEVICE', 'N/A')}\n{freq} MHz"
            style = 'DeviceButton.Active.TButton' if uid == self.selected_device_unique_id else 'DeviceButton.Inactive.TButton'
            btn = ttk.Button(self.inner_buttons_frame, text=text, style=style, command=lambda d=data: self._on_device_button_click(d))
            btn.grid(row=i // num_columns, column=i % num_columns, padx=5, pady=5, sticky="ew")

    def _on_device_button_click(self, device_data):
        # Function Description:
        # Handles a device button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"A device button was clicked. Setting the frequency for the instrument! ⚡",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        freq_mhz = device_data.get('FREQ', 'N/A')
        device_name = device_data.get('NAME', 'N/A')
        self.selected_device_unique_id = f"{device_name}-{freq_mhz}"
        self.selected_device_name = device_name
        self.selected_device_freq = float(freq_mhz) * MHZ_TO_HZ # Store the frequency
        self.poke_freq_var.set(str(freq_mhz))

        self.controls_notebook.select(0)

        self._populate_device_buttons(self.get_current_displayed_devices())

        if self.app_instance and self.app_instance.inst:
            try:
                freq_hz = float(freq_mhz) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, console_log)
                set_marker_logic(self.app_instance.inst, freq_hz, device_name, console_log)
            except (ValueError, TypeError) as e:
                console_log(f"Error setting frequency: {e}")
        
        # FIXED: Start the loop automatically when a device button is clicked.
        if self.marker_trace_loop_job:
            self.after_cancel(self.marker_trace_loop_job)
        
        if self.app_instance and self.app_instance.inst:
            try:
                center_freq_hz = self.selected_device_freq
                span_hz = float(self.span_var.get())
                self.loop_counter_var.set(0)
                self._start_marker_trace_loop(center_freq_hz=center_freq_hz, span_hz=span_hz)
            except (ValueError, TypeError) as e:
                console_log(f"❌ Error starting marker trace loop: {e}")
                debug_log(f"Dastardly bug! A TypeError or ValueError has struck our brave loop! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function)


    def _stop_loop_action(self):
        # Function Description:
        # Handles the "Stop Loop" button action.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Stopping the loop! All systems, cease and desist!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

        if self.marker_trace_loop_job:
            self.after_cancel(self.marker_trace_loop_job)
            self.marker_trace_loop_job = None
            self.loop_counter_var.set(0)
            console_log("✅ Marker trace loop stopped.")
            self._update_control_styles()
        else:
            console_log("❌ No active loop to stop.")

    def _start_marker_trace_loop(self, center_freq_hz=None, span_hz=None):
        # Function Description:
        # Starts a recurring loop to fetch marker traces.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting the marker trace loop. Get ready for some data! 📈",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        if self.selected_device_name and self.app_instance and self.app_instance.inst and center_freq_hz is not None and span_hz is not None:
            get_marker_traces(app_instance=self.app_instance, console_print_func=console_log, center_freq_hz=center_freq_hz, span_hz=span_hz, device_name=self.selected_device_name)
            self.loop_counter_var.set(self.loop_counter_var.get() + 1)

            try:
                delay = int(self.loop_delay_var.get())
                self.marker_trace_loop_job = self.after(delay, lambda: self._start_marker_trace_loop(center_freq_hz=center_freq_hz, span_hz=span_hz))
            except ValueError:
                console_log("❌ Invalid loop delay. Please enter a valid number in the Loop tab.")
                debug_log(f"The loop delay is not a number! How can a clock run on words? The loop has been stopped by this absurdity!",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
        else:
            console_log("❌ Invalid parameters for marker trace loop. Cannot start.")
            debug_log(f"Invalid parameters! We need a center frequency and a span to begin our voyage! Parameters were: center_freq_hz={center_freq_hz}, span_hz={span_hz}",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function, special=True)

    def get_current_displayed_devices(self):
        # Function Description:
        # Returns a list of devices currently displayed.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Retrieving a list of currently displayed devices.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        selected_item = self.zone_group_tree.selection()
        if not selected_item: return []
        item = selected_item[0]
        parent_id = self.zone_group_tree.parent(item)
        text = self.zone_group_tree.item(item, 'text')
        devices = []
        if not parent_id:
            for row in self.rows:
                if row.get('ZONE', '').strip() == text: devices.append(row)
        else:
            zone_name = self.zone_group_tree.item(parent_id, 'text')
            for row in self.rows:
                if row.get('ZONE', '').strip() == zone_name and row.get('GROUP', '').strip() == text:
                    devices.append(row)
        return devices

    def update_marker_data(self, new_headers, new_rows):
        # Function Description:
        # Updates the marker data and repopulates the tree view.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Updating the marker data and repopulating the display.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.headers = new_headers if new_headers is not None else []
        self.rows = new_rows if new_rows is not None else []
        self._populate_zone_group_tree()
        first_item = self.zone_group_tree.get_children()
        if first_item:
            self.zone_group_tree.selection_set(first_item[0])
            self.zone_group_tree.focus(first_item[0])
            self._on_tree_select(None)

    def load_markers_from_file(self):
        # Function Description:
        # Loads marker data from a file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Loading markers from the CSV file. Time for some data wrangling! 🤠",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        if self.app_instance and hasattr(self.app_instance, 'MARKERS_FILE_PATH'):
            path = self.app_instance.MARKERS_FILE_PATH
            if os.path.exists(path):
                try:
                    with open(path, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.update_marker_data(list(reader.fieldnames or []), list(reader))
                except Exception as e:
                    console_log(f"Error loading MARKERS.CSV: {e}")
                    self.update_marker_data([], [])
                    debug_log(f"A file loading calamity! The MARKERS.CSV file couldn't be loaded. Error: {e}",
                              file=f"{os.path.basename(__file__)} - {current_version}",
                              version=current_version,
                              function=current_function, special=True)
            else: self.update_marker_data([], [])

    def _on_span_button_click(self, span_hz):
        # Function Description:
        # Handles a span button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"A span button has been clicked. Updating the instrument's span to {span_hz} Hz!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.span_var.set(str(span_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_span_logic(self.app_instance.inst, span_hz, console_log)
                # Restart the loop with the new span value if a device is selected
                if self.selected_device_freq is not None and self.marker_trace_loop_job:
                    self.after_cancel(self.marker_trace_loop_job)
                    self._start_marker_trace_loop(center_freq_hz=self.selected_device_freq, span_hz=span_hz)
            except (ValueError, TypeError) as e:
                debug_log(f"A ValueError or TypeError has corrupted our span logic! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
                pass
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

    def _on_rbw_button_click(self, rbw_hz):
        # Function Description:
        # Handles an RBW button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"An RBW button has been clicked. Setting the RBW to {rbw_hz} Hz!",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.rbw_var.set(str(rbw_hz))
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            try:
                set_rbw_logic(self.app_instance.inst, rbw_hz, console_log)
            except (ValueError, TypeError) as e:
                debug_log(f"An RBW ValueError or TypeError! It's a disaster! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
                pass
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

    def _on_trace_button_click(self, trace_var):
        # Function Description:
        # Handles a trace button click.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"A trace mode button has been toggled.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        trace_var.set(not trace_var.get())
        self._update_control_styles()
        if self.app_instance and self.app_instance.inst:
            set_trace_modes_logic(self.app_instance.inst, self.trace_live_mode.get(), self.trace_max_hold_mode.get(), self.trace_min_hold_mode.get(), console_log)
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, console_log, self.app_instance)

    def _on_poke_action(self):
        # Function Description:
        # Handles the Poke button action.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The 'Poke' button has been pressed! Prepare for a new frequency point! 🎯",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        if self.app_instance and self.app_instance.inst:
            try:
                freq_mhz = self.poke_freq_var.get()
                freq_hz = float(freq_mhz) * MHZ_TO_HZ
                set_frequency_logic(self.app_instance.inst, freq_hz, console_log)
                set_marker_logic(self.app_instance.inst, freq_hz, f"Poke {freq_mhz} MHz", console_log)
                self.selected_device_unique_id = None
                self.selected_device_name = None
                self.selected_device_freq = freq_hz # NEW: Store the poked frequency for the loop
                self._populate_device_buttons(self.get_current_displayed_devices())
                
                # FIXED: Start the loop after a manual poke
                if self.marker_trace_loop_job:
                    self.after_cancel(self.marker_trace_loop_job)
                
                try:
                    span_hz = float(self.span_var.get())
                    self.loop_counter_var.set(0)
                    self._start_marker_trace_loop(center_freq_hz=freq_hz, span_hz=span_hz)
                except (ValueError, TypeError) as e:
                    console_log(f"❌ Error starting marker trace loop after poke: {e}")
                    debug_log(f"Dastardly bug! A TypeError or ValueError has struck our brave poke loop! Error: {e}",
                              file=f"{os.path.basename(__file__)} - {current_version}",
                              version=current_version,
                              function=current_function)
            except (ValueError, TypeError) as e:
                console_log(f"Invalid POKE frequency: {e}")
                debug_log(f"Captain, the frequency given is gibberish! Error: {e}",
                          file=f"{os.path.basename(__file__)} - {current_version}",
                          version=current_version,
                          function=current_function, special=True)
    
    def _on_tab_selected(self, event):
        # Function Description:
        # Handles the tab selection event.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"The tab has been selected. Loading markers from the file.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        self.load_markers_from_file()
