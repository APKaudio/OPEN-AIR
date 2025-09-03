# display/builder/dynamic_gui_builder.py
#
# A dynamic GUI component that orchestrates building widgets based on a JSON data structure received via MQTT.
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
#
# Version 20250903.102000.12
# FIXED: The _update_widget_value function now correctly checks for changes to a dropdown's options and calls a new 'rebuild_options' method to dynamically update the widget's content without a full GUI rebuild.

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME
from display.builder.dynamic_gui_MQTT_subscriber import MqttSubscriberMixin

# --- Widget Creator Mixin Imports ---
from display.builder.dynamic_gui_create_label import LabelCreatorMixin
from display.builder.dynamic_gui_create_label_from_config import LabelFromConfigCreatorMixin
from display.builder.dynamic_gui_create_value_box import ValueBoxCreatorMixin
from display.builder.dynamic_gui_create_gui_slider_value import SliderValueCreatorMixin
from display.builder.dynamic_gui_create_gui_button_toggle import GuiButtonToggleCreatorMixin
from display.builder.dynamic_gui_create_gui_button_toggler import GuiButtonTogglerCreatorMixin
from display.builder.dynamic_gui_create_gui_dropdown_option import GuiDropdownOptionCreatorMixin
from display.builder.dynamic_gui_create_gui_actuator import GuiActuatorCreatorMixin
from display.builder.dynamic_gui_create_gui_checkbox import GuiCheckboxCreatorMixin

# --- Global Scope Variables ---
current_version = "20250903.102000.12"
# Hash: (20250903 * 102000 * 12)
current_version_hash = (20250903 * 102000 * 12)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
DEFAULT_FRAME_PAD = 5
BUTTON_PADDING_MULTIPLIER = 5
BUTTON_BORDER_MULTIPLIER = 2
DEBUG_MODE = True
TITLE_FONT = ('Helvetica', 12, 'bold')
SECTION_FONT = ('Helvetica', 11, 'bold')


class DynamicGuiBuilder(
    ttk.Frame,
    MqttSubscriberMixin,
    LabelCreatorMixin,
    LabelFromConfigCreatorMixin,
    ValueBoxCreatorMixin,
    SliderValueCreatorMixin,
    GuiButtonToggleCreatorMixin,
    GuiButtonTogglerCreatorMixin,
    GuiDropdownOptionCreatorMixin,
    GuiActuatorCreatorMixin,
    GuiCheckboxCreatorMixin
):
    """
    Dynamically builds GUI widgets based on a JSON data structure received via MQTT.
    """
    def __init__(self, parent, mqtt_util, config, *args, **kwargs):
        # Initializes the GUI builder, sets up the layout, and subscribes to the MQTT topic.
        current_function_name = inspect.currentframe().f_code.co_name
        self.current_class_name = self.__class__.__name__

        debug_log(
            message=f"🖥️🟢 Eureka! The grand experiment begins! Initializing the {self.current_class_name} for topic '{config.get('base_topic')}'.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

            self.mqtt_util = mqtt_util
            self.config = config
            self.base_topic = config.get("base_topic")
            self.topic_widgets = {}

       #     console_log(f"🟠🟠🟠🟠🟠 self.base_topic: {self.base_topic}")
            self.config_data = {}
            self.gui_built = False
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
                "_GuiCheckbox": self._create_gui_checkbox
            }

            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])

            # This frame is a container for the entire content, filling 100% of the parent.
            self.main_content_frame = ttk.Frame(self)
            self.main_content_frame.pack(fill=tk.BOTH, expand=True)

            # The rebuild button and config frame are no longer created here.
            # The config_frame will be a simple Frame now, and the rebuild button will be added later.
            self.canvas = tk.Canvas(self.main_content_frame, borderwidth=0, highlightthickness=0, background=colors["bg"])
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

            scrollbar = ttk.Scrollbar(self.main_content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            # The config_frame is now packed into the scrollable frame
            self.config_frame = ttk.Frame(self.scroll_frame)
            self.config_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)

            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # The original conditional `if DEBUG_MODE:` section for the log pane has been removed
            # to ensure the main frame is always 100% wide.

            # Bind the <Map> event to trigger the initial GUI build
            self.bind("<Map>", lambda event: self._rebuild_gui())

            # Subscribing to the base topic via the new Mixin
            if self.base_topic:
                self.mqtt_util.add_subscriber(topic_filter=f"{self.base_topic}/#", callback_func=self._on_receive_command_message)

            console_log("✅ Celebration of success! The Dynamic GUI builder did initialize successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The monster is throwing a tantrum! GUI rebuild failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _transmit_command(self, relative_topic, payload):
        # Publishes a command to the MQTT broker.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 Preparing to transmit! The payload is '{payload}' for topic '{relative_topic}'.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            full_topic = f"{self.base_topic}{TOPIC_DELIMITER}{relative_topic}"
           # console_log(f"🟠🟠🟠🟠🟠 full_topic: {full_topic}")

            # This is the corrected line, passing the base topic and subtopic separately.
            self.mqtt_util.publish_message(topic=self.base_topic, subtopic=relative_topic, value=payload)

            console_log(f"✅ Victory! The command has been published to '{full_topic}'.")
        except Exception as e:
            console_log(f"❌ Error publishing command to topic '{relative_topic}': {e}")
            debug_log(
                message=f"🖥️🔴 The transmission portal is malfunctioning! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _update_nested_dict(self, path_parts, value):
        # Recursively traverses the dictionary structure and sets the value at the final key.
        
    #    console_log(f"🟠🟠🟠🟠🟠 nested: {path_parts}")
        
        current_level = self.config_data
        for part in path_parts[:-1]:
            current_level = current_level.setdefault(part, {})
            #console_log(f"🟠🟠🟠🟠🟠 current_level: {current_level}")
        
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

        # --- START OF FIX: Handle _GuiButtonToggle and _GuiCheckbox explicitly ---
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

        # --- END OF FIX ---

    def _rebuild_gui(self):
        # Clears the main frame and rebuilds all widgets from the current config_data.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🖥️🔵 It's alive! Rebuilding the GUI with the latest configuration data.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            for widget in self.config_frame.winfo_children():
                widget.destroy()
            self.topic_widgets.clear()
            self._create_dynamic_widgets(parent_frame=self.config_frame, data=self.config_data)
            
            # The rebuild gui button is now at the bottom
            rebuild_button = ttk.Button(self.config_frame, text="Rebuild GUI", command=self._rebuild_gui)
            rebuild_button.pack(pady=10)

            self.gui_built = True
            console_log("✅ Celebration of success! The GUI did rebuild itself from the aggregated data!")
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The monster is throwing a tantrum! GUI rebuild failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name):
        # Applies the specified theme to the GUI elements using ttk.Style.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {theme_name}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            colors = THEMES.get(theme_name, THEMES["dark"])
            style = ttk.Style(self)
            style.theme_use("clam")

            style.configure('TFrame', background=colors["bg"])
            style.configure('TLabel', background=colors["bg"], foreground=colors["fg"])
            style.configure('TLabelframe', background=colors["bg"], foreground=colors["fg"])
            
            style.configure('TButton', background=colors["accent"], foreground=colors["text"], padding=colors["padding"] * BUTTON_PADDING_MULTIPLIER, relief=colors["relief"], borderwidth=colors["border_width"] * BUTTON_BORDER_MULTIPLIER, justify=tk.CENTER)

            style.map('TButton', background=[('active', colors["secondary"])])

            style.configure('Selected.TButton', background=colors["secondary"], relief=tk.SUNKEN)
            
            style.configure('Debug.TLabel', background=colors["bg"], foreground=colors["fg_alt"])

            textbox_style = colors["textbox_style"]
            style.configure('Custom.TEntry',
                                      font=(textbox_style["Textbox_Font"], textbox_style["Textbox_Font_size"]),
                                 foreground=textbox_style["Textbox_Font_colour"],
                                 background=textbox_style["Textbox_BG_colour"],
                                 fieldbackground=textbox_style["Textbox_BG_colour"],
                                 bordercolor=textbox_style["Textbox_border_colour"])
            console_log("✅ Celebration of success! The styles did apply themselves beautifully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 By Jove, the style potion has curdled! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _create_dynamic_widgets(self, parent_frame, data, path_prefix=""):
        # Recursively creates widgets, tracking the topic path.
        current_function_name = inspect.currentframe().f_code.co_name
        try:
            if not isinstance(data, dict):
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
                        nested_frame = ttk.LabelFrame(parent_frame, text=label_text)
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)
                        # The `fields` key needs to be explicitly appended to the path here
                        new_path_prefix = f"{current_path}{TOPIC_DELIMITER}fields"
                        self._create_dynamic_widgets(nested_frame, value.get("fields", {}), path_prefix=new_path_prefix)
                        continue

                    creation_func = self.widget_factory.get(widget_type)
                    if creation_func:
                        # For widgets with a 'value' node, append it to the path.
                        if 'value' in value:
                            # The path now includes the 'value' key
                            creation_func(parent_frame=parent_frame, label=label_text, config=value, path=f"{current_path}{TOPIC_DELIMITER}value")
                        else:
                            creation_func(parent_frame=parent_frame, label=label_text, config=value, path=current_path)
                        continue

                    nested_frame = ttk.LabelFrame(parent_frame, text=label_text)
                    nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)
                    self._create_dynamic_widgets(nested_frame, value, path_prefix=current_path)
                else:
                    self._create_label(parent_frame=parent_frame, label=key.replace('_', ' ').title(), value=value, path=current_path)
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")

    def _update_widget_value(self, relative_topic, payload):
        # Finds the correct widget and updates its state from an MQTT message.
        try:
            widget_info = self.topic_widgets.get(relative_topic)
            if not widget_info:
                # FIX START
                # Handle cases where the message is for a sub-topic of a dropdown's options
                # (e.g., /options/1/label_active)
                if '/options/' in relative_topic:
                    # The topic is for an option, not the dropdown itself.
                    # Find the base path of the dropdown.
                    parts = relative_topic.split('/options/')
                    base_path = parts[0]
                    # Get the widget info for the entire dropdown.
                    dropdown_widget_info = self.topic_widgets.get(f"{base_path}") # The widget info is stored at the base path
                    
                    if dropdown_widget_info and len(dropdown_widget_info) == 3: # Correct length is 3 for this case
                         # Unpack the stored values.
                         str_var, dropdown, rebuild_method = dropdown_widget_info
                         # Rebuild the options list in the dropdown widget.
                         # We navigate the config data tree to the dropdown's location.
                         dropdown_config = self.config_data
                         for part in base_path.split('/'):
                            # Need to handle potential KeyError if path is not found
                            if 'fields' in dropdown_config:
                                dropdown_config = dropdown_config['fields']
                            dropdown_config = dropdown_config.get(part, {})

                         # If the configuration data for the dropdown is found, rebuild it.
                         if "options" in dropdown_config:
                             rebuild_method(dropdown=dropdown, config=dropdown_config)

                             # After rebuilding, check if the value from the parent topic is already set
                             # and set the dropdown to that value.
                             parent_topic_path = '/'.join(base_path.split('/'))
                             parent_config_data = self.config_data
                             for part in parent_topic_path.split('/'):
                                 parent_config_data = parent_config_data.get(part, {})
                             
                             if 'value' in parent_config_data:
                                 dropdown.set(parent_config_data['value'])
                         return
                # FIX END
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
                # Check for GuiButtonToggle: (BooleanVar, update_function)
                if isinstance(widget_info[0], tk.BooleanVar) and isinstance(widget_info[1], ttk.Button):
                    bool_var, update_func = widget_info
                    new_state = bool(payload_value) # Directly convert payload to boolean
                    if bool_var.get() != new_state:
                        bool_var.set(new_state)
                        update_func()
                # Checkbox: (BooleanVar, Checkbutton)
                elif isinstance(widget_info[0], tk.BooleanVar) and isinstance(widget_info[1], ttk.Checkbutton):
                    bool_var, checkbutton = widget_info
                    new_state = bool(payload_value)
                    bool_var.set(new_state)
                # Slider: (StringVar, Scale)
                elif isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], ttk.Scale):
                    str_var, slider = widget_info
                    str_var.set(f"{float(payload_value):.2f}")
                    slider.set(float(payload_value))
                # Dropdown: (StringVar, Combobox, rebuild_method)
                elif isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], ttk.Combobox) and len(widget_info) == 3:
                    # The widget info stores the rebuild method directly.
                    str_var, dropdown, rebuild_method = widget_info
                    # Update the StringVar to trigger the dropdown's display update
                    str_var.set(str(payload_value))
                # Button Toggler: (StringVar, update_function)
                elif isinstance(widget_info[0], tk.StringVar):
                    str_var, update_func = widget_info
                    str_var.set(str(payload_value))
                    update_func()
            elif isinstance(widget_info, ttk.Label):
                # Update label text directly
                widget_info.config(text=f"{widget_info['text'].split(':')[0]}: {payload_value}")

        except Exception as e:
            console_log(f"❌ Error updating widget for topic '{relative_topic}': {e}")


    def _on_receive_command_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        try:
            
            if topic.startswith(self.base_topic):
                relative_topic = topic[len(self.base_topic):].strip(TOPIC_DELIMITER)

                if not relative_topic:
                    # Case 1: The full configuration JSON is received on the base topic.
                    try:
                        full_config = json.loads(payload)
                        if isinstance(full_config, dict):
                            self.config_data = full_config
                            self.after(0, self._rebuild_gui)
                            self.gui_built = True
                            return
                    except (json.JSONDecodeError, TypeError):
                        pass

                # Case 2: An incremental update is received on a subtopic.
                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)

                # Only update the widget if the GUI has already been built.
                if self.gui_built:
                    self.after(0, self._update_widget_value, relative_topic, payload)

        except Exception as e:
            console_log(f"❌ Error in _on_receive_command_message: {e}")