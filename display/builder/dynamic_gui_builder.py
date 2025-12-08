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
# Version 20251127.000000.1

import os
import sys
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
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
from display.builder.dynamic_gui_create_gui_listbox import GuiListboxCreatorMixin


# --- Global Scope Variables ---
current_version = "20251127.000000.1"
current_version_hash = 20251127 * 0 * 1
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
DEFAULT_FRAME_PAD = 5
BUTTON_PADDING_MULTIPLIER = 5
BUTTON_BORDER_MULTIPLIER = 2
Local_Debug_Enable = False # This flag is checked by the updated debug_log and console_log functions
TITLE_FONT = ('Helvetica', 12, 'bold')
SECTION_FONT = ('Helvetica', 11, 'bold')


# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.

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

            self.bind("<Map>", lambda event: self._rebuild_gui())

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

    def _on_mousewheel(self, event):
        # Platform-specific mouse wheel scrolling
        if sys.platform == "linux":
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event):
        # Bind mousewheel scrolling when the mouse enters the scrollable area
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        # Unbind mousewheel scrolling when the mouse leaves the scrollable area
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _transmit_command(self, relative_topic, payload, retain=False):
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
            self.mqtt_util.publish_message(topic=self.base_topic, subtopic=relative_topic, value=payload, retain=retain)
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

            rebuild_button = ttk.Button(self.config_frame, text="Rebuild GUI")
            rebuild_button.pack(pady=10)
            rebuild_button.configure(command=self._rebuild_gui)

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
                        nested_frame = ttk.Frame(parent_frame)
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=(DEFAULT_FRAME_PAD, DEFAULT_FRAME_PAD * 2))
                        label_widget = ttk.Label(nested_frame, text=label_text, font=TITLE_FONT)
                        label_widget.pack(anchor='w', padx=DEFAULT_PAD_X, pady=2)
                        separator = ttk.Separator(nested_frame, orient='horizontal')
                        separator.pack(fill='x', pady=2)
                        new_path_prefix = f"{current_path}{TOPIC_DELIMITER}fields"
                        self._create_dynamic_widgets(nested_frame, value.get("fields", {}), path_prefix=new_path_prefix)
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
        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")

    def _update_widget_value(self, relative_topic, payload):
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
            console_log(f"❌ Error updating widget for topic '{relative_topic}': {e}")


    def _on_receive_command_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        try:
            
            if topic.startswith(self.base_topic):
                relative_topic = topic[len(self.base_topic):].strip(TOPIC_DELIMITER)

                if not relative_topic:
                    try:
                        full_config = json.loads(payload)
                        if isinstance(full_config, dict):
                            self.config_data = full_config
                            self.after(0, self._rebuild_gui)
                            self.gui_built = True
                            return
                    except (json.JSONDecodeError, TypeError):
                        pass

                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)

                if self.gui_built:
                    self.after(0, self._update_widget_value, relative_topic, payload)

        except Exception as e:
            console_log(f"❌ Error in _on_receive_command_message: {e}")