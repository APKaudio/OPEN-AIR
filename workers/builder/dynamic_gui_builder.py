# workers/builder/dynamic_gui_builder.py
#
# A recursive GUI engine that builds functional tkinter interfaces from JSON configurations.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20251217.231500.2

import os
import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import inspect

# --- Module Imports ---
from workers.logger.logger import  debug_log
from display.styling.style import THEMES, DEFAULT_THEME
## from .dynamic_gui_MQTT_subscriber import MqttSubscriberMixin
from .dynamic_gui_mousewheel_mixin import MousewheelScrollMixin
import workers.setup.app_constants as app_constants

# --- Widget Creator Mixins ---
from .dynamic_gui_create_label_from_config import LabelFromConfigCreatorMixin
from .dynamic_gui_create_label import LabelCreatorMixin
from .dynamic_gui_create_value_box import ValueBoxCreatorMixin
from .dynamic_gui_create_gui_slider_value import SliderValueCreatorMixin
from .dynamic_gui_create_gui_button_toggle import GuiButtonToggleCreatorMixin
from .dynamic_gui_create_gui_button_toggler import GuiButtonTogglerCreatorMixin
from .dynamic_gui_create_gui_dropdown_option import GuiDropdownOptionCreatorMixin
from .dynamic_gui_create_gui_actuator import GuiActuatorCreatorMixin
from .dynamic_gui_create_gui_checkbox import GuiCheckboxCreatorMixin
from .dynamic_gui_create_gui_listbox import GuiListboxCreatorMixin
from .dynamic_gui_create_progress_bar import ProgressBarCreatorMixin
from .dynamic_gui_create_text_input import TextInputCreatorMixin
from .dynamic_gui_create_web_link import WebLinkCreatorMixin
from .dynamic_gui_create_image_display import ImageDisplayCreatorMixin
from .dynamic_gui_create_animation_display import AnimationDisplayCreatorMixin
from .dynamic_gui_create_vu_meter import VUMeterCreatorMixin
from .dynamic_gui_create_fader import FaderCreatorMixin
from .dynamic_gui_create_knob import KnobCreatorMixin
from .dynamic_gui_create_inc_dec_buttons import IncDecButtonsCreatorMixin
from .dynamic_gui_create_directional_buttons import DirectionalButtonsCreatorMixin
from .dynamic_gui_create_custom_fader import CustomFaderCreatorMixin
from .dynamic_gui_create_needle_vu_meter import NeedleVUMeterCreatorMixin

# --- Protocol Global Variables ---
CURRENT_DATE = 20251217
CURRENT_TIME = 231500
CURRENT_ITERATION = 2

current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{CURRENT_ITERATION}"
current_version_hash = (CURRENT_DATE * CURRENT_TIME * CURRENT_ITERATION)
current_file = f"{os.path.basename(__file__)}"

class DynamicGuiBuilder(
    ttk.Frame,
    ## MqttSubscriberMixin,
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
    NeedleVUMeterCreatorMixin
):
    """
    Manages the dynamic generation of GUI elements based on OcaBlock definitions.
    """
    def __init__(self, parent, json_path=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        current_function_name = "__init__"
        self.current_class_name = self.__class__.__name__

        if app_constants.LOCAL_DEBUG_ENABLE: 
             debug_log(
                 message=f"🖥️🟢 Eureka! Igniting the DynamicGuiBuilder with json_path: {json_path}",
                 file=current_file,
                 version=current_version,
                 function=f"{self.current_class_name}.{current_function_name}"
                 


             )

        # Validation: Ensure critical arguments are present to prevent crashes
        if json_path is None:
            caller_frame = inspect.stack()[1]
            caller_filename = caller_frame.filename
            debug_log(message=f"❌ Error in __init__: Missing critical argument: json_path. Called from {caller_filename}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔴 Blast! The builder was summoned without its required artifacts! Called from {caller_filename}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )
            # We continue but don't build to avoid hard recursion errors in the dynamic loader
            return

        self.pack(fill=tk.BOTH, expand=True)

        ## self.mqtt_util = mqtt_util
        ## self.base_topic = base_topic
        self.json_filepath = Path(json_path)
        self.topic_widgets = {}
        self.config_data = {}
        self.gui_built = False
        self.mqtt_callbacks = {}


        # Protocol: No Magic Numbers - Widget Factory Mapping
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
            "_NeedleVUMeter": self._create_needle_vu_meter
        }

        try:
            # --- Layout Initialization ---
            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])
            
            self.canvas = tk.Canvas(self, background=colors["bg"], borderwidth=0, highlightthickness=0)
            self.scroll_frame = ttk.Frame(self.canvas)
            self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Build immediately from the authoritative file
            self._load_and_build_from_file()

            # Manual Rebuild Trigger
            ttk.Button(self, text="Reload Config", command=self._rebuild_gui).pack(side=tk.BOTTOM, pady=10)

            ## Connect MQTT for state updates
            ## if self.mqtt_util and self.base_topic:
            ##     self.mqtt_util.add_subscriber(
            ##         topic=f"{self.base_topic}/#", 
            ##         callback=self._on_receive_command_message
            ##     )
            


        except Exception as e:
            debug_log(message=f"❌ Error in __init__: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔴 Arrr, the gears of the builder be jammed! {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

    def _apply_styles(self, theme_name):
        """
        Applies styling configuration to the frame.
        Note: Per protocol, logic for 'how' to style should reside in Utility files.
        """
        current_function_name = "_apply_styles"
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🔍 Inspecting the aesthetics for theme: {theme_name}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}"
                


            )
        # Placeholder for style application logic
        pass

    def _load_and_build_from_file(self):
        """Builds GUI structure strictly from local JSON."""
        current_function_name = "_load_and_build_from_file"
        
        try:
            if self.json_filepath.exists():
                with open(self.json_filepath, 'r') as f:
                    self.config_data = json.load(f)
                
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"🖥️📂 Reading the sacred scrolls at {self.json_filepath}",
                        file=current_file,
                        version=current_version,
                        function=f"{self.current_class_name}.{current_function_name}"
                        


                    )
                    
                self._rebuild_gui()
                self.gui_built = True
                debug_log(message=f"✅ Success! Loaded config: {self.json_filepath.name}")
            else:
                debug_log(message=f"🟡 Warning: Config file missing at {self.json_filepath}")

        except Exception as e:
            debug_log(message=f"❌ Error in _load_and_build_from_file: {e}")

    def _rebuild_gui(self):
        """Clears frame and builds dynamic structure."""
        current_function_name = "_rebuild_gui"
        
        try:
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message="🖥️🔁 Tearing down the old world to build a new one!",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

            for child in self.scroll_frame.winfo_children():
                child.destroy()
            
            self.topic_widgets.clear()
            self._create_dynamic_widgets(parent_frame=self.scroll_frame, data=self.config_data)
            
            debug_log(message="✅ GUI Reconstruction complete!")

        except Exception as e:
            debug_log(message=f"❌ Error in _rebuild_gui: {e}")

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix=""):
        """Recursive parser for OcaBlocks and fields that now uses a grid layout for wrapping."""
        current_function_name = "_create_dynamic_widgets"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(message=f"Creating widgets in {parent_frame} with data: {data}", file=current_file, version=current_version, function=current_function_name 

)
        
        try:
            if not isinstance(data, dict):
                return

            # --- Grid Layout Variables ---
            col = 0
            row = 0
            # Set a default and allow override from config if present
            max_cols = data.get("layout_columns", 4) 

            for key, value in data.items():
                current_path = f"{path_prefix}/{key}".strip("/")
                
                if isinstance(value, dict):
                    widget_type = value.get("type")
                    
                    if widget_type == "OcaBlock":
                        # OcaBlocks act as major sections and will span the full width.
                        # If we are in the middle of a row, move to the next one.
                        if col != 0:
                            row += 1
                            col = 0
                        
                        block_frame = ttk.LabelFrame(parent_frame, text=key)
                        # Use grid for the block itself
                        block_frame.grid(row=row, column=0, columnspan=max_cols, sticky="ew", padx=10, pady=5)
                        row += 1 # The next set of widgets will be on the row below the block label

                        # Recursively call to build the widgets *inside* this block
                        self._create_dynamic_widgets(
                            parent_frame=block_frame, 
                            data=value.get("fields", {}), 
                            path_prefix=current_path
                        )
                        continue # Finished processing this block
                    
                    elif widget_type in self.widget_factory:
                        if app_constants.LOCAL_DEBUG_ENABLE:
                            debug_log(
                                message=f"🖥️🔵 Fabricating a {widget_type} widget for {current_path}",
                                file=current_file,
                                version=current_version,
                                function=f"{self.current_class_name}.{current_function_name}"
                                


                            )
                        
                        # The creation function now RETURNS the widget frame instead of packing it.
                        widget_frame = self.widget_factory[widget_type](
                            parent_frame=parent_frame, # Pass the direct parent
                            label=value.get("label_active", key),
                            config=value,
                            path=current_path
                        )

                        if widget_frame:
                            # Place the returned frame into our grid
                            widget_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
                            
                            # Update grid position
                            col += 1
                            if col >= max_cols:
                                col = 0
                                row += 1
                        continue

            # Configure column weights for the parent frame to allow expansion
            for i in range(max_cols):
                parent_frame.grid_columnconfigure(i, weight=1)

        except Exception as e:
            debug_log(message=f"❌ Error in _create_dynamic_widgets: {e}")