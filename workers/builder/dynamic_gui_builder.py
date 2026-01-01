# workers/builder/dynamic_gui_builder.py
#
# A recursive GUI engine that builds functional tkinter interfaces from JSON configurations.
# Version 20251230.1830.2 (FIXED: Integrated Plot & Meter Creators)

import os
import orjson
import hashlib
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import inspect
import time
import traceback 

# --- Module Imports ---
from workers.logger.logger import  debug_logger
from workers.styling.style import THEMES, DEFAULT_THEME
from workers.builder.input.dynamic_gui_mousewheel_mixin import MousewheelScrollMixin
from workers.setup.config_reader import Config
from workers.setup.path_initializer import GLOBAL_PROJECT_ROOT
from workers.mqtt.mqtt_publisher_service import publish_payload

app_constants = Config.get_instance()
from workers.mqtt.mqtt_topic_utils import get_topic, generate_topic_path_from_filepath, TOPIC_DELIMITER
from workers.logger.log_utils import _get_log_args 
from typing import Dict, Any

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
from .images.dynamic_gui_create_progress_bar import ProgressBarCreatorMixin

from .text.dynamic_gui_create_text_input import TextInputCreatorMixin
from .text.dynamic_gui_create_web_link import WebLinkCreatorMixin
from .images.dynamic_gui_create_image_display import ImageDisplayCreatorMixin
from .images.dynamic_gui_create_animation_display import AnimationDisplayCreatorMixin
from .audio.dynamic_gui_create_vu_meter import VUMeterCreatorMixin
from .input.dynamic_gui_create_fader import FaderCreatorMixin
from .audio.dynamic_gui_create_knob import KnobCreatorMixin
from .input.dynamic_gui_create_inc_dec_buttons import IncDecButtonsCreatorMixin
from .input.dynamic_gui_create_directional_buttons import DirectionalButtonsCreatorMixin
from .audio.dynamic_gui_create_custom_fader import CustomFaderCreatorMixin
from .audio.dynamic_gui_create_needle_vu_meter import NeedleVUMeterCreatorMixin
from .audio.dynamic_gui_create_panner import PannerCreatorMixin
from .audio.dynamic_gui_create_custom_horizontal_fader import CustomHorizontalFaderCreatorMixin
from .audio.dynamic_gui_create_trapezoid_button import TrapezoidButtonCreatorMixin
from .audio.dynamic_gui_create_trapezoid_toggler import TrapezoidButtonTogglerCreatorMixin

# 🧪 NEW: Direct Imports of the Widget Classes (No Mixins needed)
from .data_graphing.dynamic_graph import FluxPlotter
from .data_graphing.Meter_to_display_units import HorizontalMeterWithText, VerticalMeter

# --- Protocol Global Variables ---
CURRENT_DATE = 20251230
CURRENT_TIME = 183000
CURRENT_ITERATION = 2

current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{CURRENT_ITERATION}"
current_version_hash = (CURRENT_DATE * CURRENT_TIME * CURRENT_ITERATION)
current_file = f"{os.path.basename(__file__)}"

class DynamicGuiBuilder(
    ttk.Frame,  # Inject ttk.Frame as the base widget class
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
    PannerCreatorMixin,
    CustomHorizontalFaderCreatorMixin,
    TrapezoidButtonTogglerCreatorMixin
):
    def __init__(self, parent, json_path=None, tab_name=None, *args, **kwargs):
        config = kwargs.pop('config', {})
        super().__init__(master=parent)
        self.tab_name = tab_name
        self.state_mirror_engine = config.get('state_mirror_engine')
        self.subscriber_router = config.get('subscriber_router')
        current_function_name = "__init__"
        self.current_class_name = self.__class__.__name__
        self.last_build_hash = None

        if app_constants.global_settings['debug_enabled']:
             debug_logger(
                 message=f"🖥️🟢 Igniting the DynamicGuiBuilder v{current_version}",
                 **_get_log_args()
             )

        if json_path is None:
            self.json_filepath = None
            self.config_data = {}
        else:
            self.json_filepath = Path(json_path)
            self.config_data = {}

        self.pack(fill=tk.BOTH, expand=True)
        self.topic_widgets = {}
        self.gui_built = False
        self.tk_vars = {} 

        if self.json_filepath is None:
            self.base_mqtt_topic_from_path = "GENERIC_GUI_TOPIC"
        elif GLOBAL_PROJECT_ROOT is None:
            debug_logger(message="❌ GLOBAL_PROJECT_ROOT not initialized.", **_get_log_args())
            self.base_mqtt_topic_from_path = "FALLBACK_TOPIC"
        else:
            self.base_mqtt_topic_from_path = generate_topic_path_from_filepath(self.json_filepath, GLOBAL_PROJECT_ROOT)
        
        if self.state_mirror_engine and not hasattr(self.state_mirror_engine, 'base_topic'):
             self.state_mirror_engine.base_topic = app_constants.get_mqtt_base_topic()

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
            "_CustomHorizontalFader": self._create_custom_horizontal_fader,
            "_NeedleVUMeter": self._create_needle_vu_meter,
            "_Panner": self._create_panner,
            "_TrapezoidButton": self._create_trapezoid_button,
            "_TrapezoidButtonToggler": self._create_trapezoid_button_toggler,
            
            # 🧪 Mapped to the new local adapter methods
            "plot_widget": self._create_plot_widget,
            "_HorizontalMeterWithText": self._create_horizontal_meter,
            "_VerticalMeter": self._create_vertical_meter
        }

        # --- INIT GUI STRUCTURE ---
        try:
            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
            
            self.main_content_frame = ttk.Frame(self)
            self.main_content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.canvas = tk.Canvas(self.main_content_frame, background=colors["bg"], borderwidth=0, highlightthickness=0)
            self.scroll_frame = ttk.Frame(self.canvas)
            self.scrollbar = ttk.Scrollbar(self.main_content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            self.scroll_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.button_frame = ttk.Frame(self)
            self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 10), padx=10)

            ttk.Button(self.button_frame, text="Reload Config", command=self._force_rebuild_gui).pack(side=tk.LEFT, pady=10)

            if self.json_filepath is not None:
                self._load_and_build_from_file()
            else:
                self._rebuild_gui()
                self.gui_built = True

        except Exception as e:
            debug_logger(message=f"❌ Error in __init__: {e}", **_get_log_args())

    # --- ADAPTER METHODS FOR NEW WIDGETS ---
    
    def _create_plot_widget(self, parent_frame, config, base_mqtt_topic_from_path, state_mirror_engine, subscriber_router, **kwargs):
        """Adapter to create FluxPlotter from the Builder"""
        widget_id = config.get("id", "plot_widget")
        return FluxPlotter(
            parent=parent_frame,
            config=config,
            base_mqtt_topic_from_path=base_mqtt_topic_from_path,
            widget_id=widget_id,
            state_mirror_engine=state_mirror_engine,
            subscriber_router=subscriber_router
        )

    def _create_horizontal_meter(self, parent_frame, config, base_mqtt_topic_from_path, state_mirror_engine, subscriber_router, **kwargs):
        """Adapter to create HorizontalMeterWithText"""
        widget_id = config.get("id", "h_meter")
        return HorizontalMeterWithText(
            parent=parent_frame,
            config=config,
            base_mqtt_topic_from_path=base_mqtt_topic_from_path,
            widget_id=widget_id,
            state_mirror_engine=state_mirror_engine,
            subscriber_router=subscriber_router
        )

    def _create_vertical_meter(self, parent_frame, config, base_mqtt_topic_from_path, state_mirror_engine, subscriber_router, **kwargs):
        """Adapter to create VerticalMeter"""
        widget_id = config.get("id", "v_meter")
        return VerticalMeter(
            parent=parent_frame,
            config=config,
            base_mqtt_topic_from_path=base_mqtt_topic_from_path,
            widget_id=widget_id,
            state_mirror_engine=state_mirror_engine,
            subscriber_router=subscriber_router
        )

    # --- STYLING & CORE LOGIC ---

    def _apply_styles(self, theme_name):
        style = ttk.Style()
        colors = THEMES.get(theme_name, THEMES["dark"])

        bg = colors.get("bg", "#2b2b2b")
        fg = colors.get("fg", "#dcdcdc")
        entry_bg = colors.get("entry_bg", "#dcdcdc")
        entry_fg = colors.get("entry_fg", "#000000")
        accent = colors.get("accent", "#f4902c")

        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=fg)

        style.configure('TEntry', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"))
        style.map('TEntry', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                             background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])

        style.configure('Custom.TEntry', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"))
        style.map('Custom.TEntry', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                                   background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])

        style.configure('TCombobox', fieldbackground=entry_bg, background=bg, foreground=entry_fg, bordercolor=colors.get("border", "#555555"), selectbackground=accent, selectforeground=entry_fg)
        style.map('TCombobox', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                             background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])
        
        style.configure("TCombobox.Listbox", background=entry_bg, foreground=entry_fg, selectbackground=accent, selectforeground=fg)
        
        style.configure('BlackText.TCombobox', foreground=entry_fg)
        style.map('BlackText.TCombobox', fieldbackground=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))],
                                   background=[('readonly', entry_bg), ('disabled', colors.get("fg_alt", "#888888"))])
        
        tab_style_config = colors.get("tab_style", {}).get("tab_base_style", {})
        style.configure('TNotebook', background=bg, borderwidth=0)
        style.configure('TNotebook.Tab', 
                        background=tab_style_config.get("background", colors.get("primary", bg)),
                        foreground=tab_style_config.get("foreground", fg),
                        font=tab_style_config.get("font", ("Helvetica", 10)),
                        padding=tab_style_config.get("padding", [5, 2]),
                        borderwidth=tab_style_config.get("borderwidth", 0),
                        relief=tab_style_config.get("relief", "flat"))
        style.map('TNotebook.Tab',
                  background=[('selected', accent), ('!selected', colors.get("secondary", bg))],
                  foreground=[('selected', fg), ('!selected', fg)])

        # Custom Button Style
        style.configure('Custom.TButton', background=colors.get('secondary'), foreground=colors.get('fg'))
        style.map('Custom.TButton',
                  background=[('pressed', accent), ('active', colors.get('hover_blue'))])

        # Custom Selected Button Style (for ON state)
        style.configure('Custom.Selected.TButton', background=accent, foreground=colors.get('fg'))
        style.map('Custom.Selected.TButton',
                  background=[('pressed', accent), ('active', colors.get('hover_blue'))])

    def _transmit_command(self, widget_name: str, value):
        if self.state_mirror_engine:
            if self.state_mirror_engine.is_widget_registered(widget_name):
                self.state_mirror_engine.broadcast_gui_change_to_mqtt(widget_name)
            else:
                topic = get_topic(self.state_mirror_engine.base_topic, self.base_mqtt_topic_from_path, widget_name)
                payload = {
                    "val": value,
                    "src": "gui",
                    "ts": time.time(),
                    "GUID": self.state_mirror_engine.GUID
                }
                self.state_mirror_engine.publish_command(topic, orjson.dumps(payload))
        elif app_constants.global_settings['debug_enabled']:
            debug_logger(message=f"[DUMMY] _transmit_command called for {widget_name} with value {value}", **_get_log_args())

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def _force_rebuild_gui(self):
        self.last_build_hash = None
        self._load_and_build_from_file()

    def _load_and_build_from_file(self):
        if self.json_filepath is None:
            self._rebuild_gui() 
            self.gui_built = True
            return

        try:
            if self.json_filepath.exists():
                with open(self.json_filepath, 'r') as f:
                    raw_content = f.read()
                
                current_hash = hashlib.md5(raw_content.encode('utf-8')).hexdigest()
                if self.last_build_hash == current_hash:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"⚡ Config unchanged for {self.json_filepath.name}. Skipping GUI rebuild.", **_get_log_args())
                    return

                self.last_build_hash = current_hash
                self.config_data = orjson.loads(raw_content)
                self._rebuild_gui()
                self.gui_built = True
            else:
                debug_logger(message=f"🟡 Warning: Config file missing at {self.json_filepath}", **_get_log_args())
                if not self.config_data:
                    self.config_data = {}
                self._rebuild_gui()
                self.gui_built = True
        except Exception as e:
            debug_logger(message=f"❌ Error in _load_and_build_from_file: {e}", **_get_log_args())

    def _rebuild_gui(self):
        try:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(message="🖥️🔁 Tearing down the old world to build a new one!", **_get_log_args())
            
            self.pack_forget()
            
            for child in self.scroll_frame.winfo_children():
                child.destroy()
            self.topic_widgets.clear()
            self.update_idletasks() 

            widget_configs = list(self.config_data.items())
            self._create_widgets_in_batches(self.scroll_frame, widget_configs)
            
        except Exception as e:
            debug_logger(message=f"❌ Error in _rebuild_gui setup: {e}", **_get_log_args())
            self.pack(fill=tk.BOTH, expand=True)

    def _create_widgets_in_batches(self, parent_frame, widget_configs, path_prefix="", override_cols=None, start_index=0, row_offset=0):
        try:
            batch_size = 5
            index = start_index
            
            col = 0
            row = row_offset
            max_cols = int(self.config_data.get("layout_columns", 1) if override_cols is None else override_cols)
            
            current_data = self.config_data if override_cols is None else widget_configs[start_index][1]
            column_sizing = current_data.get("column_sizing", [])

            for col_idx in range(max_cols):
                sizing_info = column_sizing[col_idx] if col_idx < len(column_sizing) else {}
                weight = sizing_info.get("weight", 1)
                minwidth = sizing_info.get("minwidth", 0)
                parent_frame.grid_columnconfigure(col_idx, weight=weight, minsize=minwidth)

            while index < len(widget_configs) and index < start_index + batch_size:
                key, value = widget_configs[index]
                current_path = f"{path_prefix}/{key}".strip("/")

                if isinstance(value, dict):
                    widget_type = value.get("type")
                    layout = value.get("layout", {})
                    col_span = int(layout.get("col_span", 1))
                    row_span = int(layout.get("row_span", 1))
                    sticky = layout.get("sticky", "nsew")

                    target_frame = None

                    if widget_type == "OcaBlock":
                        block_cols = value.get("layout_columns", None)
                        target_frame = ttk.LabelFrame(parent_frame, text=key, borderwidth=0, relief="flat")
                        self._create_dynamic_widgets(parent_frame=target_frame, data=value.get("fields", {}), path_prefix=current_path, override_cols=block_cols)
                    
                    elif widget_type in self.widget_factory:
                        factory_kwargs = {
                            "parent_frame": parent_frame,
                            "label": value.get("label_active", key),
                            "config": value,
                            "path": current_path,
                            "base_mqtt_topic_from_path": self.base_mqtt_topic_from_path,
                            "state_mirror_engine": self.state_mirror_engine,
                            "subscriber_router": self.subscriber_router
                        }

                        try:
                            target_frame = self.widget_factory[widget_type](**factory_kwargs)
                        except Exception as e:
                            debug_logger(message=f"❌ Error creating widget '{key}' of type '{widget_type}': {e}", **_get_log_args())
                            target_frame = None
                    else:
                        debug_logger(message=f"❓ Unknown or missing widget 'type' for widget '{key}'. Skipping.", **_get_log_args())

                    if target_frame:
                        tk_var = self.tk_vars.get(current_path)
                        target_frame.grid(row=row, column=col, columnspan=col_span, rowspan=row_span, padx=5, pady=5, sticky=sticky)
                        parent_frame.grid_rowconfigure(row, weight=1)
                        col += col_span
                        if col >= max_cols:
                            col = 0
                            row += row_span
                
                index += 1

            if index < len(widget_configs):
                self.after(5, lambda: self._create_widgets_in_batches(parent_frame, widget_configs, path_prefix, override_cols, index, row))
            else:
                self._on_frame_configure()
                self.pack(fill=tk.BOTH, expand=True)

                app_constants.PERFORMANCE_MODE = False
                
                if app_constants.global_settings['debug_enabled']:
                    debug_logger(message="✅ Batch processing complete! All widgets built.", **_get_log_args())

        except Exception as e:
            tb = traceback.format_exc()
            debug_logger(message=f"❌🔥 CRITICAL BATCH PROCESSOR FAILURE! {e}\n{tb}", **_get_log_args())
            self.pack(fill=tk.BOTH, expand=True)

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix="", override_cols=None):
        try:
            if not isinstance(data, dict):
                return

            col = 0
            row = 0
            max_cols = int(data.get("layout_columns", 1) if override_cols is None else override_cols)
            column_sizing = data.get("column_sizing", [])

            for col_idx in range(max_cols):
                sizing_info = column_sizing[col_idx] if col_idx < len(column_sizing) else {}
                weight = sizing_info.get("weight", 1)
                minwidth = sizing_info.get("minwidth", 0)
                parent_frame.grid_columnconfigure(col_idx, weight=weight, minsize=minwidth)

            for key, value in data.items():
                current_path = f"{path_prefix}/{key}".strip("/")
                
                if isinstance(value, dict):
                    widget_type = value.get("type")
                    layout = value.get("layout", {})
                    col_span = int(layout.get("col_span", 1))
                    row_span = int(layout.get("row_span", 1))
                    sticky = layout.get("sticky", "nsew")

                    target_frame = None

                    if widget_type == "OcaBlock":
                        block_cols = value.get("layout_columns", None)
                        target_frame = ttk.LabelFrame(parent_frame, text=key, borderwidth=0, relief="flat")
                        self._create_dynamic_widgets(parent_frame=target_frame, data=value.get("fields", {}), path_prefix=current_path, override_cols=block_cols)
                    
                    elif widget_type in self.widget_factory:
                        factory_kwargs = {
                            "parent_frame": parent_frame,
                            "label": value.get("label_active", key),
                            "config": value,
                            "path": current_path,
                            "base_mqtt_topic_from_path": self.base_mqtt_topic_from_path,
                            "state_mirror_engine": self.state_mirror_engine,
                            "subscriber_router": self.subscriber_router
                        }

                        try:
                            target_frame = self.widget_factory[widget_type](**factory_kwargs)
                        except Exception as e:
                            debug_logger(message=f"❌ Error creating synchronous widget '{key}' of type '{widget_type}': {e}", **_get_log_args())
                            target_frame = None
                    else:
                        debug_logger(message=f"❓ Unknown or missing widget 'type' for widget '{key}' in synchronous builder. Skipping.", **_get_log_args())

                    if target_frame:
                        tk_var = self.tk_vars.get(current_path)
                        target_frame.grid(row=row, column=col, columnspan=col_span, rowspan=row_span, padx=5, pady=5, sticky=sticky)
                        parent_frame.grid_rowconfigure(row, weight=1)
                        col += col_span
                        if col >= max_cols:
                            col = 0
                            row += row_span

        except Exception as e:
            debug_logger(message=f"❌ Error in synchronous _create_dynamic_widgets: {e}", **_get_log_args())