# workers/builder/dynamic_gui_builder.py
#
# A recursive GUI engine that builds functional tkinter interfaces from JSON configurations.
# Version 20251223.213000.8
#
# UPDATES:
# 1. CHANGED DEFAULT: 'layout_columns' now defaults to 1 (Vertical Stack).
#    Use "layout_columns": N to create horizontal grids explicitly.

import os
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import inspect

# --- Module Imports ---
from workers.logger.logger import  debug_log
from display.styling.style import THEMES, DEFAULT_THEME
from workers.builder.input.dynamic_gui_mousewheel_mixin import MousewheelScrollMixin
import workers.setup.app_constants as app_constants
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
CURRENT_TIME = 213000
CURRENT_ITERATION = 8

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
    def __init__(self, parent, json_path=None, *args, **kwargs):
        _ = kwargs.pop('config', None) 
        super().__init__(parent, *args, **kwargs)
        current_function_name = "__init__"
        self.current_class_name = self.__class__.__name__

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
        self.mqtt_callbacks = {}

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
            
            # Canvas and Scrollbar Setup
            self.canvas = tk.Canvas(self, background=colors["bg"], borderwidth=0, highlightthickness=0)
            self.scroll_frame = ttk.Frame(self.canvas)
            self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Event Bindings for Scrolling
            self.scroll_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self._load_and_build_from_file()
            ttk.Button(self, text="Reload Config", command=self._rebuild_gui).pack(side=tk.BOTTOM, pady=10)

        except Exception as e:
            debug_log(message=f"❌ Error in __init__: {e}")

    def _transmit_command(self, *args, **kwargs):
        debug_log(message="[DUMMY] _transmit_command called", **_get_log_args())

    def _apply_styles(self, theme_name):
        pass

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def _load_and_build_from_file(self):
        try:
            if self.json_filepath.exists():
                with open(self.json_filepath, 'r') as f:
                    self.config_data = json.load(f)
                self._rebuild_gui()
                self.gui_built = True
            else:
                debug_log(message=f"🟡 Warning: Config file missing at {self.json_filepath}")
        except Exception as e:
            debug_log(message=f"❌ Error in _load_and_build_from_file: {e}")

    def _rebuild_gui(self):
        try:
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(message="🖥️🔁 Tearing down the old world to build a new one!", **_get_log_args())
            
            self.update_idletasks()
            for child in self.scroll_frame.winfo_children():
                child.destroy()
            self.topic_widgets.clear()
            self.update_idletasks()

            self._create_dynamic_widgets(parent_frame=self.scroll_frame, data=self.config_data)
            
            self._on_frame_configure()
            
            debug_log(message="✅ GUI Reconstruction complete!")
        except Exception as e:
            debug_log(message=f"❌ Error in _rebuild_gui: {e}")

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix="", override_cols=None):
        try:
            if not isinstance(data, dict):
                return

            col = 0
            row = 0
            
            if override_cols is not None:
                max_cols = int(override_cols)
            else:
                # ⚡ DEFAULT CHANGED TO 1 ⚡
                # This ensures vertical stacking by default.
                max_cols = int(data.get("layout_columns", 1))

            for key, value in data.items():
                current_path = f"{path_prefix}/{key}".strip("/")
                
                if isinstance(value, dict):
                    widget_type = value.get("type")
                    
                    layout = value.get("layout", {})
                    col_span = int(layout.get("col_span", 1))
                    row_span = int(layout.get("row_span", 1))
                    sticky = layout.get("sticky", "nw")
                    req_width = layout.get("width", None)
                    req_height = layout.get("height", None)
                    weight_x = int(layout.get("weight_x", 0))
                    weight_y = int(layout.get("weight_y", 0))

                    target_frame = None

                    if widget_type == "OcaBlock":
                        block_cols = value.get("layout_columns", None)
                        target_frame = ttk.LabelFrame(parent_frame, text=key)
                        
                        self._create_dynamic_widgets(
                            parent_frame=target_frame, 
                            data=value.get("fields", {}), 
                            path_prefix=current_path,
                            override_cols=block_cols 
                        )
                    
                    elif widget_type in self.widget_factory:
                        target_frame = self.widget_factory[widget_type](
                            parent_frame=parent_frame,
                            label=value.get("label_active", key),
                            config=value,
                            path=current_path
                        )

                    if target_frame:
                        if req_width or req_height:
                            if isinstance(target_frame, (tk.Frame, ttk.Frame, ttk.LabelFrame, tk.Canvas)):
                                target_frame.pack_propagate(False) 
                                target_frame.grid_propagate(False)
                            if req_width: target_frame.config(width=req_width)
                            if req_height: target_frame.config(height=req_height)

                        target_frame.grid(
                            row=row, 
                            column=col, 
                            columnspan=col_span,
                            rowspan=row_span,
                            padx=5, 
                            pady=5, 
                            sticky=sticky
                        )
                        
                        if weight_x > 0:
                            parent_frame.grid_columnconfigure(col, weight=weight_x)
                        if weight_y > 0:
                            parent_frame.grid_rowconfigure(row, weight=weight_y)

                        col += col_span
                        if col >= max_cols:
                            col = 0
                            row += row_span

            for i in range(max_cols):
                if parent_frame.grid_columnconfigure(i)['weight'] == 0:
                     parent_frame.grid_columnconfigure(i, weight=1)

        except Exception as e:
            debug_log(message=f"❌ Error in _create_dynamic_widgets: {e}")