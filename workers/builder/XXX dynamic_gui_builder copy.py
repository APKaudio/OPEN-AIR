# workers/builder/dynamic_gui_builder.py
#
# This dynamic GUI builder component (dynamic_gui_builder.py) orchestrates building widgets based on a JSON data structure received via MQTT.
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 44 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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


import os
import sys
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt
import pathlib # CRITICAL FIX: Missing import

# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME
from .dynamic_gui_MQTT_subscriber import MqttSubscriberMixin
from .dynamic_gui_config_loader import get_json_filepath_from_base_topic # NEW IMPORT
from .dynamic_gui_mousewheel_mixin import MousewheelScrollMixin # NEW IMPORT

# --- Widget Creator Mixin Imports ---
from .dynamic_gui_create_label import LabelCreatorMixin
from .dynamic_gui_create_label_from_config import LabelFromConfigCreatorMixin
from .dynamic_gui_create_value_box import ValueBoxCreatorMixin
from .dynamic_gui_create_gui_slider_value import SliderValueCreatorMixin
from .dynamic_gui_create_gui_button_toggle import GuiButtonToggleCreatorMixin
from .dynamic_gui_create_gui_button_toggler import GuiButtonTogglerCreatorMixin
from .dynamic_gui_create_gui_dropdown_option import GuiDropdownOptionCreatorMixin
from .dynamic_gui_create_gui_actuator import GuiActuatorCreatorMixin
from .dynamic_gui_create_gui_checkbox import GuiCheckboxCreatorMixin
from .dynamic_gui_create_gui_listbox import GuiListboxCreatorMixin


# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
DEFAULT_FRAME_PAD = 5
BUTTON_PADDING_MULTIPLIER = 5
BUTTON_BORDER_MULTIPLIER = 2
LOCAL_DEBUG_ENABLE = False # This flag is checked by the updated debug_log and  functions
TITLE_FONT = ('Helvetica', 12, 'bold')
SECTION_FONT = ('Helvetica', 11, 'bold')


# The wrapper functions debug_log and _switch are removed
# as the core debug_log and  now directly handle LOCAL_DEBUG_ENABLE.

class DynamicGuiBuilder(
    ttk.Frame,
    MqttSubscriberMixin,
    MousewheelScrollMixin, # NEW MIXIN
    LabelCreatorMixin,
    LabelFromConfigCreatorMixin,
    ValueBoxCreatorMixin,
    SliderValueCreatorMixin,
    GuiButtonToggleCreatorMixin,
    GuiButtonTogglerCreatorMixin,
    GuiDropdownOptionCreatorMixin,
    GuiActuatorCreatorMixin,
    GuiCheckboxCreatorMixin,
    GuiListboxCreatorMixin
):
    """
    Dynamically builds GUI widgets based on a JSON data structure received via MQTT.
    """
    def __init__(self, parent, mqtt_util, config, *args, **kwargs):
        # Initializes the GUI builder, sets up the layout, and subscribes to the MQTT topic.
        current_function_name = inspect.currentframe().f_code.co_name
        self.current_class_name = self.__class__.__name__

        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🟢 Eureka! The grand experiment begins! Initializing the {self.current_class_name} for topic '{config.get('base_topic')}'.",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}"
                


            )
        try:
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

            self.mqtt_util = mqtt_util
            self.config = config
            self.base_topic = config.get("base_topic")
            self.topic_widgets = {}

            self.config_data = {}
            self.gui_built = False # Flag to track if GUI has been built.
            self.log_text = None
            
            self.widget_factory = {
                "_sliderValue": self._create_slider_value,
                "_GuiButtonToggle": self._create_gui_button_toggle,
                "_buttonToggle": self._create_gui_button_toggle,
                "_GuiDropDownOption": self._create_gui_dropdown_option,
                "_DropDownOption": self._create_gui_dropdown_option,
                "_GuiButtonToggler": self._create_gui_button_toggler,
                "_Value": self._create_value_box,
                "_Label": self._create_label_from_config,
                "_GuiActuator": self._create_gui_actuator,
                "_GuiCheckbox": self._create_gui_checkbox,
                "_GuiListbox": self._create_gui_listbox
            }

            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])

            self.main_content_frame = ttk.Frame(self)
            self.main_content_frame.pack(fill=tk.BOTH, expand=True)

            self.canvas = tk.Canvas(self.main_content_frame, borderwidth=0, highlightthickness=0, background=colors["bg"])
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

            scrollbar = ttk.Scrollbar(self.main_content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            self.config_frame = ttk.Frame(self.scroll_frame)
            self.config_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)

            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # --- Bind Mousewheel Scrolling ---
            self.scroll_frame.bind("<Enter>", self._bind_mousewheel)
            self.scroll_frame.bind("<Leave>", self._unbind_mousewheel)

            # Attempt to load initial configuration from a JSON file
            json_filepath = get_json_filepath_from_base_topic(
                base_topic=self.base_topic,
                class_name=self.current_class_name,
                calling_file=current_file,
                calling_version=current_version,
                


            )
            if json_filepath and json_filepath.is_file():
                try:
                    with open(json_filepath, 'r') as f:
                        self.config_data = json.load(f)
                    debug_log(
                        message=f"🖥️🔵 Successfully loaded initial configuration from {json_filepath}.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.current_class_name}.{current_function_name}"
                        


                    )
                    # Perform initial GUI build from the loaded JSON data
                    self._rebuild_gui()
                    self.gui_built = True # Mark GUI as built after initial load
                except Exception as e:
                    (f"❌ Error loading initial config from {json_filepath}: {e}")
                    if app_constants.LOCAL_DEBUG_ENABLE: 
                        debug_log(
                            message=f"🖥️🔴 Failed to load initial config from {json_filepath}. Error: {e}",
                            file=current_file,
                            version=current_version,
                            function=f"{self.current_class_name}.{current_function_name}"
                            


                        )
            else:
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"⚠️ Warning: No initial JSON config file found for base_topic: {self.base_topic}. GUI will build upon first MQTT message.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.current_class_name}.{current_function_name}"
                        


                    )

            self.bind("<Map>", self._on_map_event)

            if self.base_topic:
                self.mqtt_util.add_subscriber(topic_filter=f"{self.base_topic}/#", callback_func=self._on_receive_command_message)

            ("✅ The Dynamic GUI builder did initialize successfully!")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🟢 Exiting {self.current_class_name}.__init__().",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

        except Exception as e:
            (f"❌ Error in {current_function_name}: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔴 The monster is throwing a tantrum! GUI rebuild failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

    def _on_map_event(self, event=None):
        """Builds the GUI if it hasn't been built yet."""
        current_function_name = inspect.currentframe().f_code.co_name
        if not self.gui_built:
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔵 First time mapping event for {self.base_topic}. Building GUI.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )
            self._rebuild_gui()
            self.gui_built = True
        else:
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔵 GUI for {self.base_topic} already built. Skipping rebuild on map event.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )



    def _transmit_command(self, relative_topic, payload, retain=False):
        """
        A helper function to publish a command to the MQTT broker.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"MQTT TX: Publishing '{payload}' to '{relative_topic}' (retain={retain}).",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
                


            )
        self.mqtt_util.publish_message(topic=relative_topic, subtopic="", value=payload, retain=retain)


    def _update_nested_dict(self, path_parts, value):
        # Recursively traverses the dictionary structure and sets the value at the final key.
        current_level = self.config_data
        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})

        final_value = value
        if isinstance(value, str):
            try:
                data = json.loads(value)
                if isinstance(data, dict) and 'value' in data:
                    final_value = data['value']
            except (json.JSONDecodeError, TypeError):
                pass

        if isinstance(final_value, str):
            try:
                final_value = json.loads(final_value)
            except (json.JSONDecodeError, TypeError):
                pass

        if isinstance(final_value, str):
            if final_value.lower() == 'true':
                final_value = True
            elif final_value.lower() == 'false':
                final_value = False

        last_key = path_parts[-1]
        parent_dict = current_level.get(path_parts[-2]) if len(path_parts) > 1 else self.config_data

        if isinstance(parent_dict, dict) and parent_dict.get('type') == '_GuiButtonToggle':
            is_on = final_value
            if 'options' in parent_dict:
                for option_key, option_config in parent_dict['options'].items():
                    if option_key.upper() == 'ON':
                        option_config['selected'] = is_on
                    elif option_key.upper() == 'OFF':
                        option_config['selected'] = not is_on
        elif isinstance(parent_dict, dict) and parent_dict.get('type') == '_GuiCheckbox':
            parent_dict['value'] = final_value
        else:
            current_level[last_key] = final_value

    def _rebuild_gui(self):
        # Clears the main frame and rebuilds all widgets from the current config_data.
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🔵 It's alive! Rebuilding the GUI with the latest configuration data.",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}"
                


            )
        try:
            for widget in self.config_frame.winfo_children():
                widget.destroy()
            self.topic_widgets.clear()
            self._create_dynamic_widgets(parent_frame=self.config_frame, data=self.config_data)

            rebuild_button = ttk.Button(self.config_frame, text="Rebuild GUI")
            rebuild_button.pack(pady=10)
            rebuild_button.configure(command=self._rebuild_gui)

            ("✅ The GUI did rebuild itself from the aggregated data!")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔵 Exiting _rebuild_gui(). GUI rebuild completed.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )
        except Exception as e:
            (f"❌ Error in {current_function_name}: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔴 The monster is throwing a tantrum! GUI rebuild failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

    def _apply_styles(self, theme_name):
        # Applies the specified theme to the GUI elements using ttk.Style.
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"▶️ {current_function_name} with arguments: {theme_name}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}"
                


            )
        try:
            colors = THEMES.get(theme_name, THEMES["dark"])
            style = ttk.Style(self)
            style.theme_use("clam")

            # Get button-specific colors from the new, centralized dictionary
            # FIX: We are no longer using button_style, but rather the specific
            # dictionaries defined in style.py
            actuator_colors = colors["button_style_actuator"]
            toggle_colors = colors["button_style_toggle"]
            toggler_colors = colors["button_style_toggler"]

            style.configure('TFrame', background=colors["bg"])
            style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
            style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])

            # --- Corrected Button Styling for all three types ---
            # Define a custom style for the actuator buttons
            style.configure('Custom.TButton',
                            background=actuator_colors["background"],
                            foreground=actuator_colors["foreground"],
                            padding=colors["padding"] * BUTTON_PADDING_MULTIPLIER,
                            relief=colors["relief"],
                            borderwidth=0,
                            justify=tk.CENTER)

            style.map('Custom.TButton',
                      background=[('pressed', actuator_colors["Button_Pressed_Bg"]),
                                  ('active', actuator_colors["Button_Hover_Bg"])],
                      foreground=[('pressed', toggle_colors["Button_Selected_Fg"])])

            # Configure a separate style for the selected/toggled-on state
            style.configure('Custom.Selected.TButton',
                            background=toggle_colors["Button_Selected_Bg"],
                            foreground=toggle_colors["Button_Selected_Fg"],
                            padding=colors["padding"] * BUTTON_PADDING_MULTIPLIER,
                            relief=tk.SUNKEN,
                            borderwidth=0,
                            justify=tk.CENTER)
            
            style.map('Custom.Selected.TButton',
                      background=[('pressed', toggle_colors["Button_Pressed_Bg"]),
                                  ('active', toggle_colors["Button_Hover_Bg"])],
                      foreground=[('pressed', toggle_colors["Button_Selected_Fg"])])
            # --- End Corrected Button Styling ---

            style.configure('Debug.TLabel', background=colors["bg"], foreground=colors["fg_alt"])

            textbox_style = colors["textbox_style"]
            style.configure('Custom.TEntry',
                                      font=(textbox_style["Textbox_Font"], textbox_style["Textbox_Font_size"]),
                                 foreground=textbox_style["Textbox_Font_colour"],
                                 background=textbox_style["Textbox_BG_colour"],
                                 fieldbackground=textbox_style["Textbox_BG_colour"],
                                 bordercolor=textbox_style["Textbox_border_colour"])
            ("✅ The styles did apply themselves beautifully!")

        except Exception as e:
            (f"❌ Error in {current_function_name}: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔴 By Jove, the style potion has curdled! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix=""):
        # Recursively creates widgets, tracking the topic path.
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE: 
            debug_log(
                message=f"🖥️🔵 Entering _create_dynamic_widgets() for path_prefix: '{path_prefix}'.",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}"
                


            )
        try:
            if not isinstance(data, dict):
                if app_constants.LOCAL_DEBUG_ENABLE: 
                    debug_log(
                        message=f"⚠️ Skipping _create_dynamic_widgets as data is not a dict for path_prefix: '{path_prefix}'.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}"
                        


                    )
                return

            for key, value in data.items():
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass

                safe_key = key.replace(TOPIC_DELIMITER, '_')
                current_path = f"{path_prefix}{TOPIC_DELIMITER}{safe_key}" if path_prefix else safe_key

                if isinstance(value, dict):
                    widget_type = value.get("type")
                    label_text = value.get("label", key.replace('_', ' ').title())

                    if widget_type == "OcaBlock":
                        nested_frame = ttk.Frame(parent_frame)
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=(DEFAULT_FRAME_PAD, DEFAULT_FRAME_PAD * 2))
                        label_widget = ttk.Label(nested_frame, text=label_text, font=TITLE_FONT)
                        label_widget.pack(anchor='w', padx=DEFAULT_PAD_X, pady=2)
                        separator = ttk.Separator(nested_frame, orient='horizontal')
                        separator.pack(fill='x', pady=2)
                        self._create_dynamic_widgets(nested_frame, value.get("fields", {}), path_prefix=current_path)
                        continue

                    creation_func = self.widget_factory.get(widget_type)
                    if creation_func:
                        if 'value' in value:
                            creation_func(parent_frame=parent_frame, label=label_text, config=value, path=f"{current_path}{TOPIC_DELIMITER}value")
                        else:
                            creation_func(parent_frame=parent_frame, label=label_text, config=value, path=current_path)
                        continue

                    nested_frame = ttk.Frame(parent_frame)
                    nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=(DEFAULT_FRAME_PAD, DEFAULT_FRAME_PAD * 2))
                    label_widget = ttk.Label(nested_frame, text=label_text, font=TITLE_FONT)
                    label_widget.pack(anchor='w', padx=DEFAULT_PAD_X, pady=2)
                    separator = ttk.Separator(nested_frame, orient='horizontal')
                    separator.pack(fill='x', pady=2)
                    self._create_dynamic_widgets(nested_frame, value, path_prefix=current_path)
                else:
                    self._create_label(parent_frame=parent_frame, label=key.replace('_', ' ').title(), value=value, path=current_path)
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"🖥️🔵 Exiting _create_dynamic_widgets() for path_prefix: '{path_prefix}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.current_class_name}.{current_function_name}"
                    


                )
        except Exception as e:
            (f"❌ Error in {current_function_name}: {e}")

    def _update_widget_value(self, relative_topic, payload):
        current_function_name = inspect.currentframe().f_code.co_name
        # Finds the correct widget and updates its state from an MQTT message.
        try:
            widget_info = self.topic_widgets.get(relative_topic)
            if not widget_info:
                if '/options/' in relative_topic:
                    parts = relative_topic.split('/options/')
                    base_path = parts[0]
                    widget_info_at_base = self.topic_widgets.get(f"{base_path}")

                    if widget_info_at_base and isinstance(widget_info_at_base, tuple):
                        # FIX: Differentiate between Listbox and Combobox (Dropdown)
                        # Check if it's a Listbox by checking the widget type
                        if isinstance(widget_info_at_base[0], tk.Listbox):
                            listbox, rebuild_method, _ = widget_info_at_base
                            # Traverse the config to get the updated config for this listbox
                            listbox_config = self.config_data
                            for part in base_path.split('/'):
                                if 'fields' in listbox_config:
                                    listbox_config = listbox_config['fields']
                                listbox_config = listbox_config.get(part, {})
                            # Call the rebuild method with the correct widget and config
                            if "options" in listbox_config:
                                rebuild_method(lb=listbox, cfg=listbox_config)
                            return
                        
                        # Check if it's a Combobox (Dropdown)
                        elif len(widget_info_at_base) == 3 and isinstance(widget_info_at_base[1], ttk.Combobox):
                            str_var, dropdown, rebuild_method = widget_info_at_base
                            dropdown_config = self.config_data
                            for part in base_path.split('/'):
                                if 'fields' in dropdown_config:
                                    dropdown_config = dropdown_config['fields']
                                dropdown_config = dropdown_config.get(part, {})
                            
                            if "options" in dropdown_config:
                                rebuild_method(dropdown=dropdown, config=dropdown_config)
                                parent_topic_path = '/'.join(base_path.split('/'))
                                parent_config_data = self.config_data
                                for part in parent_topic_path.split('/'):
                                    parent_config_data = parent_config_data.get(part, {})
                                if 'value' in parent_config_data:
                                    dropdown.set(parent_config_data['value'])
                            return
                return

            payload_value = payload
            if isinstance(payload, str):
                try:
                    data = json.loads(payload)
                    if isinstance(data, dict) and 'value' in data:
                        payload_value = data['value']
                except (json.JSONDecodeError, TypeError):
                    pass

            if isinstance(payload_value, str):
                try:
                    payload_value = json.loads(payload_value)
                except (json.JSONDecodeError, TypeError):
                    pass

            if isinstance(payload_value, str):
                if payload_value.lower() == 'true':
                    payload_value = True
                elif payload_value.lower() == 'false':
                    payload_value = False

            if isinstance(widget_info, ttk.Entry):
                widget_info.delete(0, tk.END)
                widget_info.insert(0, payload_value)
            elif isinstance(widget_info, tuple):
                if isinstance(widget_info[0], tk.BooleanVar) and isinstance(widget_info[1], ttk.Button):
                    bool_var, update_func = widget_info
                    new_state = bool(payload_value)
                    if bool_var.get() != new_state:
                        bool_var.set(new_state)
                        update_func()
                elif isinstance(widget_info[0], tk.BooleanVar) and isinstance(widget_info[1], ttk.Checkbutton):
                    bool_var, checkbutton = widget_info
                    new_state = bool(payload_value)
                    bool_var.set(new_state)
                elif isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], ttk.Scale):
                    str_var, slider = widget_info
                    str_var.set(f"{float(payload_value):.2f}")
                    slider.set(float(payload_value))
                elif isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], ttk.Combobox) and len(widget_info) == 3:
                    str_var, dropdown, rebuild_method = widget_info
                    str_var.set(str(payload_value))
                elif isinstance(widget_info[0], tk.Listbox) and len(widget_info) == 3:
                    listbox, rebuild_method, options_map = widget_info
                    
                    selected_key = next((key for key, opt in options_map.items() if str(opt.get('value', key)) == str(payload_value)), None)
                    if selected_key:
                        selected_label = options_map[selected_key].get('label_active', selected_key)
                        all_items = listbox.get(0, tk.END)
                        if selected_label in all_items:
                            idx = all_items.index(selected_label)
                            listbox.selection_clear(0, tk.END)
                            listbox.select_set(idx)
                            listbox.see(idx)
                elif isinstance(widget_info[0], tk.StringVar):
                    str_var, update_func = widget_info
                    str_var.set(str(payload_value))
                    update_func()
            elif isinstance(widget_info, ttk.Label):
                widget_info.config(text=f"{widget_info['text'].split(':')[0]}: {payload_value}")

        except Exception as e:
            (f"❌ Error updating widget for topic '{relative_topic}': {e}")


    def _on_receive_command_message(self, topic, payload):
        current_function_name = inspect.currentframe().f_code.co_name
        # The main callback function that processes incoming MQTT messages.
        try:
            
            if topic.startswith(self.base_topic):
                relative_topic = topic[len(self.base_topic):].strip(TOPIC_DELIMITER)

                if not relative_topic:
                    try:
                        full_config = json.loads(payload)
                        if isinstance(full_config, dict):
                            # Update config_data, but don't automatically rebuild GUI
                            # GUI structure is now primarily driven by local JSON files.
                            self.config_data = full_config
                            if app_constants.LOCAL_DEBUG_ENABLE: 
                                debug_log(
                                    message=f"🖥️🔵 Received full config via MQTT for {self.base_topic}. Updated config_data but did not auto-rebuild GUI (local JSON is authoritative).",
                                    file=current_file,
                                    version=current_version,
                                    function=f"{self.current_class_name}.{current_function_name}"
                                    


                                )
                            return
                    except (json.JSONDecodeError, TypeError):
                        pass

                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)

                if self.gui_built:
                    self.after(0, self._update_widget_value, relative_topic, payload)

        except Exception as e:
            (f"❌ Error in _on_receive_command_message: {e}")