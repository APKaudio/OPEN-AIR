# workers/builder/dynamic_gui_builder.py
#
# A recursive GUI engine that builds functional tkinter interfaces from JSON configurations.
# Version 20251223.235500.9 (OPTIMIZED)
#
# UPDATES:
# 1. HASH CHECK IMPLEMENTED: Prevents rebuilding GUI if JSON content hasn't changed.
# 2. CHANGED DEFAULT: 'layout_columns' now defaults to 1 (Vertical Stack).

import os
import orjson
import hashlib  # ⚡ Added for optimization
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import inspect
import time

# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.styling.style import THEMES, DEFAULT_THEME
from workers.builder.input.dynamic_gui_mousewheel_mixin import MousewheelScrollMixin
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.utils.topic_utils import get_topic
from workers.utils.log_utils import _get_log_args 

# --- Widget Creator Mixins ---
from .text.dynamic_gui_create_label_from_config import LabelFromConfigCreatorMixin
from .text.dynamic_gui_create_label import LabelCreatorMixin
from .text.dynamic_gui_create_value_box import ValueBoxCreatorMixin
from .input.dynamic_gui_create_gui_slider_value import SliderValueCreatorMixin
from .input.dynamic_gui_create_gui_button_toggle import GuiButtonToggleCreatorMixin
from .input.dynamic_gui_create_gui_button_toggler import GuiButtonTogglerCreatorMixin
from .text.dynamic_gui_create_gui_dropdown_option import GuiDropdownOptionCreatorMixin
from .input.dynamic_gui_create_gui_actuator import GuiActuatorCreatorMixin
from .input.dynamic_gui_create_gui_checkbox import GuiCheckboxCreatorMixin
from .text.dynamic_gui_create_gui_listbox import GuiListboxCreatorMixin
from .graphical.dynamic_gui_create_progress_bar import ProgressBarCreatorMixin
from .text.dynamic_gui_create_text_input import TextInputCreatorMixin
from .text.dynamic_gui_create_web_link import WebLinkCreatorMixin
from .graphical.dynamic_gui_create_image_display import ImageDisplayCreatorMixin
from .graphical.dynamic_gui_create_animation_display import AnimationDisplayCreatorMixin
from .audio.dynamic_gui_create_vu_meter import VUMeterCreatorMixin
from .input.dynamic_gui_create_fader import FaderCreatorMixin
from .audio.dynamic_gui_create_knob import KnobCreatorMixin
from .input.dynamic_gui_create_inc_dec_buttons import IncDecButtonsCreatorMixin
from .input.dynamic_gui_create_directional_buttons import DirectionalButtonsCreatorMixin
from .audio.dynamic_gui_create_custom_fader import CustomFaderCreatorMixin
from .audio.dynamic_gui_create_needle_vu_meter import NeedleVUMeterCreatorMixin
from .audio.dynamic_gui_create_panner import PannerCreatorMixin

# --- Protocol Global Variables ---
CURRENT_DATE = 20251223
CURRENT_TIME = 235500
CURRENT_ITERATION = 9

current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{CURRENT_ITERATION}"
current_version_hash = (CURRENT_DATE * CURRENT_TIME * CURRENT_ITERATION)
current_file = f"{os.path.basename(__file__)}"

class DynamicGuiBuilder(
    ttk.Frame,
    MousewheelScrollMixin,
    LabelFromConfigCreatorMixin,
    LabelCreatorMixin,
    ValueBoxCreatorMixin,
    SliderValueCreatorMixin,
    GuiButtonToggleCreatorMixin,
    GuiButtonTogglerCreatorMixin,
    GuiDropdownOptionCreatorMixin,
    GuiActuatorCreatorMixin,
    GuiCheckboxCreatorMixin,
    GuiListboxCreatorMixin,
    ProgressBarCreatorMixin,
    TextInputCreatorMixin,
    WebLinkCreatorMixin,
    ImageDisplayCreatorMixin,
    AnimationDisplayCreatorMixin,
    VUMeterCreatorMixin,
    FaderCreatorMixin,
    KnobCreatorMixin,
    IncDecButtonsCreatorMixin,
    DirectionalButtonsCreatorMixin,
    CustomFaderCreatorMixin,
    NeedleVUMeterCreatorMixin,
    PannerCreatorMixin
):
    def __init__(self, parent, json_path=None, tab_name=None, *args, **kwargs):
        config = kwargs.pop('config', {})
        super().__init__(parent, *args, **kwargs)
        self.tab_name = tab_name
        self.state_mirror_engine = config.get('state_mirror_engine')
        self.subscriber_router = config.get('subscriber_router')
        current_function_name = "__init__"
        self.current_class_name = self.__class__.__name__
        self.last_build_hash = None # ⚡ Initialize Hash Tracker

        if app_constants.LOCAL_DEBUG_ENABLE: 
             debug_log(
                 message=f"🖥️🟢 Igniting the DynamicGuiBuilder v{current_version}",
                 file=current_file,
                 version=current_version,
                 function=f"{self.current_class_name}.{current_function_name}"
             )

        if json_path is None:
            debug_log(message=f"❌ Error in __init__: Missing critical argument: json_path.")
            return

        self.pack(fill=tk.BOTH, expand=True)
        self.json_filepath = Path(json_path)
        self.topic_widgets = {}
        self.config_data = {}
        self.gui_built = False
        #self.mqtt_callbacks = {}

        self.widget_factory = {
            "_sliderValue": self._create_slider_value,
            "_GuiButtonToggle": self._create_gui_button_toggle,
            "_GuiButtonToggler": self._create_gui_button_toggler,
            "_GuiDropDownOption": self._create_gui_dropdown_option,
            "_Value": self._create_value_box,
            "_Label": self._create_label_from_config,
            "_GuiActuator": self._create_gui_actuator,
            "_GuiCheckbox": self._create_gui_checkbox,
            "_GuiListbox": self._create_gui_listbox,
            "_ProgressBar": self._create_progress_bar,
            "_TextInput": self._create_text_input,
            "_WebLink": self._create_web_link,
            "_ImageDisplay": self._create_image_display,
            "_AnimationDisplay": self._create_animation_display,
            "_VUMeter": self._create_vu_meter,
            "_Fader": self._create_fader,
            "_Knob": self._create_knob,
            "_IncDecButtons": self._create_inc_dec_buttons,
            "_DirectionalButtons": self._create_directional_buttons,
            "_CustomFader": self._create_custom_fader,
            "_NeedleVUMeter": self._create_needle_vu_meter,
            "_Panner": self._create_panner
        }

        try:
            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
            
            # --- Main Content Frame (holds canvas and scrollbar) ---
            self.main_content_frame = ttk.Frame(self)
            self.main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Canvas and Scrollbar Setup
            self.canvas = tk.Canvas(self.main_content_frame, background=colors["bg"], borderwidth=0, highlightthickness=0)
            self.scroll_frame = ttk.Frame(self.canvas)
            self.scrollbar = ttk.Scrollbar(self.main_content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Event Bindings for Scrolling
            self.scroll_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # --- Button Frame (holds control buttons at the bottom) ---
            self.button_frame = ttk.Frame(self)
            self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 10), padx=10) # Add some padding

            ttk.Button(self.button_frame, text="Reload Config", command=self._force_rebuild_gui).pack(side=tk.LEFT, pady=10)

            self._load_and_build_from_file()

        except Exception as e:
            debug_log(message=f"❌ Error in __init__: {e}")

    def _transmit_command(self, widget_name: str, value):
        if self.state_mirror_engine:
            if self.state_mirror_engine.is_widget_registered(widget_name):
                # For stateful widgets, the engine will get the value from the tk_var
                self.state_mirror_engine.broadcast_gui_change_to_mqtt(widget_name)
            else:
                # For stateless commands like actuators
                topic = get_topic("OPEN-AIR", self.tab_name, widget_name)
                payload = {
                    "val": value,
                    "src": "gui",
                    "ts": time.time(),
                    "instance_id": self.state_mirror_engine.instance_id # Add instance ID
                }
                self.state_mirror_engine.publish_command(topic, orjson.dumps(payload))
        elif app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(message=f"[DUMMY] _transmit_command called for {widget_name} with value {value}", **_get_log_args())

    def _apply_styles(self, theme_name):
        style = ttk.Style()
        colors = THEMES.get(theme_name, THEMES["dark"]) # Fallback to dark theme

        # General colors
        bg = colors.get("bg", "#2b2b2b")
        fg = colors.get("fg", "#dcdcdc")
        entry_bg = colors.get("entry_bg", "#dcdcdc")
        entry_fg = colors.get("entry_fg", "#000000")
        accent = colors.get("accent", "#f4902c") # Use accent for selected/highlighted elements

        # Configure general theme elements (Frames, Labels)
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=fg)

        # Configure TEntry (for TextInput and general Entry widgets)
        style.configure('TEntry', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"))
        style.map('TEntry', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                             background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))]) # Apply background to the entire widget

        # Configure Custom.TEntry (for ValueBox)
        style.configure('Custom.TEntry', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"))
        style.map('Custom.TEntry', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                                   background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])

        # Configure TCombobox (for Dropdown)
        style.configure('TCombobox', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"), selectbackground=accent, selectforeground=entry_fg)
        style.map('TCombobox', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                             background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])
        
        # Configure the Listbox part of the Combobox (for dropdown options)
        style.configure("TCombobox.Listbox", background=entry_bg, foreground=entry_fg, selectbackground=accent, selectforeground=fg)
        
        # Configure the 'BlackText.TCombobox' style that was defined in dynamic_gui_create_gui_dropdown_option.py
        style.configure('BlackText.TCombobox', foreground=entry_fg)
        style.map('BlackText.TCombobox', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                                   background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])
        
        # --- Tab Styling ---
        tab_style_config = colors.get("tab_style", {}).get("tab_base_style", {})
        style.configure('TNotebook', background=bg, borderwidth=0) # General Notebook background
        style.configure('TNotebook.Tab', 
                        background=tab_style_config.get("background", colors.get("primary", bg)),
                        foreground=tab_style_config.get("foreground", fg),
                        font=tab_style_config.get("font", ("Helvetica", 10)),
                        padding=tab_style_config.get("padding", [5, 2]),
                        borderwidth=tab_style_config.get("borderwidth", 0),
                        relief=tab_style_config.get("relief", "flat"))
        style.map('TNotebook.Tab',
                  background=[('selected', accent), ('!selected', colors.get("secondary", bg))], # Orange when selected
                  foreground=[('selected', fg), ('!selected', fg)]) # White text for both selected/unselected tabs

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def _force_rebuild_gui(self):
        """Manually triggers a rebuild, bypassing the hash check."""
        self.last_build_hash = None
        self._load_and_build_from_file()

    def _load_and_build_from_file(self):
        try:
            if self.json_filepath.exists():
                # ⚡ OPTIMIZATION STEP 1: READ RAW & HASH ⚡
                with open(self.json_filepath, 'r') as f:
                    raw_content = f.read()
                
                # Calculate MD5 Hash of the file content
                current_hash = hashlib.md5(raw_content.encode('utf-8')).hexdigest()
                
                # Check if the file has changed since the last build
                if self.last_build_hash == current_hash:
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        # Use a simple message to avoid overhead
                        debug_log(message=f"⚡ Config unchanged for {self.json_filepath.name}. Skipping GUI rebuild.")
                    return

                # If changed, update hash and parse JSON
                self.last_build_hash = current_hash
                self.config_data = orjson.loads(raw_content)
                
                # Proceed to build
                self._rebuild_gui()
                self.gui_built = True
            else:
                debug_log(message=f"🟡 Warning: Config file missing at {self.json_filepath}")
        except Exception as e:
            debug_log(message=f"❌ Error in _load_and_build_from_file: {e}")

    def _rebuild_gui(self):
        # Solution B: Silent Running Protocol (Log Suppression)
        previous_debug_enable_state = app_constants.LOCAL_DEBUG_ENABLE
        app_constants.LOCAL_DEBUG_ENABLE = False

        previous_performance_mode = app_constants.PERFORMANCE_MODE
        app_constants.PERFORMANCE_MODE = True

        try:
            if previous_debug_enable_state:
                debug_log(message="🖥️🔁 Tearing down the old world to build a new one!", **_get_log_args())
            
            # Solution A: Layout Locking
            self.pack_forget() 

            for child in self.scroll_frame.winfo_children():
                child.destroy()
            self.topic_widgets.clear()
            self.update_idletasks() 

            # Replace synchronous call with asynchronous batch processing
            widget_configs = list(self.config_data.items())
            self._create_widgets_in_batches(self.scroll_frame, widget_configs)
            
        except Exception as e:
            app_constants.LOCAL_DEBUG_ENABLE = True
            debug_log(message=f"❌ Error in _rebuild_gui: {e}", **_get_log_args())
            app_constants.LOCAL_DEBUG_ENABLE = False
            
        finally:
            # Restore states in the final batch completion, not here.
            # The finalization (packing, restoring logs) will happen
            # at the end of the batch processing.
            pass

    def _create_widgets_in_batches(self, parent_frame, widget_configs, path_prefix="", override_cols=None, start_index=0, row_offset=0):
        """
        Creates widgets in batches to prevent freezing the GUI, implementing the 
        "Flux Dispersal" strategy.
        """
        batch_size = 5 # Process 5 widgets per event loop cycle
        index = start_index
        
        col = 0
        row = row_offset
        # max_cols is derived from self.config_data or override_cols (for sub-blocks)
        max_cols = int(self.config_data.get("layout_columns", 1) if override_cols is None else override_cols)
        
        # If processing a sub-block (override_cols is not None), then column_sizing
        # should come from the sub-block's config ('value' in the calling context).
        # Otherwise, for the top-level, it comes from self.config_data.
        current_data = self.config_data if override_cols is None else widget_configs[start_index][1] # Get 'value' for the current OcaBlock
        column_sizing = current_data.get("column_sizing", [])

        # Apply column sizing from JSON config
        for col_idx in range(max_cols):
            sizing_info = column_sizing[col_idx] if col_idx < len(column_sizing) else {}
            weight = sizing_info.get("weight", 1) # Default to 1 to allow expansion
            minwidth = sizing_info.get("minwidth", 0) # Default to 0 for no minimum width
            parent_frame.grid_columnconfigure(col_idx, weight=weight, minsize=minwidth)

        while index < len(widget_configs) and index < start_index + batch_size:
            key, value = widget_configs[index]
            current_path = f"{path_prefix}/{key}".strip("/")

            if isinstance(value, dict):
                widget_type = value.get("type")
                layout = value.get("layout", {})
                col_span = int(layout.get("col_span", 1))
                row_span = int(layout.get("row_span", 1))
                sticky = layout.get("sticky", "nw")

                target_frame = None

                if widget_type == "OcaBlock":
                    block_cols = value.get("layout_columns", None)
                    target_frame = ttk.LabelFrame(parent_frame, text=key)
                    # Recursively but synchronously build sub-blocks as they are usually small.
                    self._create_dynamic_widgets(parent_frame=target_frame, data=value.get("fields", {}), path_prefix=current_path, override_cols=block_cols)
                
                elif widget_type in self.widget_factory:
                    target_frame = self.widget_factory[widget_type](
                        parent_frame=parent_frame,
                        label=value.get("label_active", key),
                        config=value,
                        path=current_path
                    )

                if target_frame:
                    target_frame.grid(row=row, column=col, columnspan=col_span, rowspan=row_span, padx=5, pady=5, sticky=sticky)
                    col += col_span
                    if col >= max_cols:
                        col = 0
                        row += row_span
            
            index += 1

        if index < len(widget_configs):
            # Schedule the next batch
            self.after(5, lambda: self._create_widgets_in_batches(parent_frame, widget_configs, path_prefix, override_cols, index, row))
        else:
            # --- Finalization Step (at the end of the last batch) ---
            self._on_frame_configure()
            self.pack(fill=tk.BOTH, expand=True) # Re-show the parent now that all widgets are created

            # Restore logging state
            previous_debug_enable_state = getattr(self, '_previous_debug_state', True) # Retrieve saved state
            app_constants.LOCAL_DEBUG_ENABLE = previous_debug_enable_state
            app_constants.PERFORMANCE_MODE = False
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(message="✅ Batch processing complete! All widgets built.", **_get_log_args())

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix="", override_cols=None):
        """
        Synchronous legacy method for building widgets, now primarily used for sub-blocks.
        """
        try:
            if not isinstance(data, dict):
                return

            col = 0
            row = 0
            max_cols = int(data.get("layout_columns", 1) if override_cols is None else override_cols)
            column_sizing = data.get("column_sizing", [])

            # Apply column sizing from JSON config
            for col_idx in range(max_cols):
                sizing_info = column_sizing[col_idx] if col_idx < len(column_sizing) else {}
                weight = sizing_info.get("weight", 1) # Default to 1 to allow expansion
                minwidth = sizing_info.get("minwidth", 0) # Default to 0 for no minimum width
                parent_frame.grid_columnconfigure(col_idx, weight=weight, minsize=minwidth)

            for key, value in data.items():
                current_path = f"{path_prefix}/{key}".strip("/")
                
                if isinstance(value, dict):
                    widget_type = value.get("type")
                    layout = value.get("layout", {})
                    col_span = int(layout.get("col_span", 1))
                    row_span = int(layout.get("row_span", 1))
                    sticky = layout.get("sticky", "nw")

                    target_frame = None

                    if widget_type == "OcaBlock":
                        block_cols = value.get("layout_columns", None)
                        target_frame = ttk.LabelFrame(parent_frame, text=key)
                        self._create_dynamic_widgets(parent_frame=target_frame, data=value.get("fields", {}), path_prefix=current_path, override_cols=block_cols)
                    
                    elif widget_type in self.widget_factory:
                        target_frame = self.widget_factory[widget_type](
                            parent_frame=parent_frame,
                            label=value.get("label_active", key),
                            config=value,
                            path=current_path
                        )

                    if target_frame:
                        target_frame.grid(row=row, column=col, columnspan=col_span, rowspan=row_span, padx=5, pady=5, sticky=sticky)
                        col += col_span
                        if col >= max_cols:
                            col = 0
                            row += row_span

        except Exception as e:
            print(f"❌ Error in synchronous _create_dynamic_widgets: {e}")