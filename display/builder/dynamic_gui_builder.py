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
# Version 20250827.200000.1

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import paho.mqtt.client as mqtt

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Widget Creator Mixin Imports ---
from display.builder.dynamic_gui_create_label import LabelCreatorMixin
from display.builder.dynamic_gui_create_label_from_config import LabelFromConfigCreatorMixin
from display.builder.dynamic_gui_create_value_box import ValueBoxCreatorMixin
from display.builder.dynamic_gui_create_slider_value import SliderValueCreatorMixin
from display.builder.dynamic_gui_create_gui_button_toggle import GuiButtonToggleCreatorMixin
from display.builder.dynamic_gui_create_gui_button_toggler import GuiButtonTogglerCreatorMixin
from display.builder.dynamic_gui_create_gui_dropdown_option import GuiDropdownOptionCreatorMixin

# --- Global Scope Variables ---
current_version = "20250827.200000.1"
current_version_hash = (20250827 * 200000 * 1)
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
    LabelCreatorMixin,
    LabelFromConfigCreatorMixin,
    ValueBoxCreatorMixin,
    SliderValueCreatorMixin,
    GuiButtonToggleCreatorMixin,
    GuiButtonTogglerCreatorMixin,
    GuiDropdownOptionCreatorMixin
):
    """
    Dynamically builds GUI widgets based on a JSON data structure received via MQTT.
    """
    def __init__(self, parent, mqtt_util, config, *args, **kwargs):
        """
        Initializes the GUI builder.
        """
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
            self._log_to_gui = config.get('log_to_gui_console', console_log)

            self.widget_factory = {
                "_sliderValue": self._create_slider_value,
                "_GuiButtonToggle": self._create_gui_button_toggle,
                "_buttonToggle": self._create_gui_button_toggle,
                "_GuiDropDownOption": self._create_gui_dropdown_option,
                "_DropDownOption": self._create_gui_dropdown_option,
                "_GuiButtonToggler": self._create_gui_button_toggler,
                "_Value": self._create_value_box,
                "_Label": self._create_label_from_config
            }

            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])

            self.main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            self.left_frame = ttk.Frame(self.main_paned_window)
            
            rebuild_button = ttk.Button(self.left_frame, text="Rebuild GUI", command=self._rebuild_gui)
            rebuild_button.pack(pady=5)

            self.canvas = tk.Canvas(self.left_frame, borderwidth=0, highlightthickness=0, background=colors["bg"])
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            
            scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            self.main_frame = ttk.LabelFrame(self.scroll_frame, text=f"MQTT Configuration: {self.base_topic}")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)

            if DEBUG_MODE:
                self.right_frame = ttk.LabelFrame(self.main_paned_window, text="MQTT Message Log")
                self.log_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, bg=colors["bg"], fg=colors["fg"])
                self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                self.log_text.configure(state='disabled')
            
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.main_paned_window.add(self.left_frame, weight=3)
            if DEBUG_MODE:
                self.main_paned_window.add(self.right_frame, weight=2)
            
            self.main_paned_window.pack(fill=tk.BOTH, expand=True)
            
            # --- FIX: Subscribing to the base topic is now done by the pusher file.
            
            console_log("✅ Celebration of success! The Dynamic GUI builder did initialize successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 Arrr, the code be capsized! The GUI construction has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _log_to_gui(self, message):
        # Appends a message to the GUI log text widget if it exists.
        if hasattr(self, 'log_text'):
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, message + "\n\n")
            self.log_text.configure(state='disabled')
            self.log_text.see(tk.END)

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

        current_level[path_parts[-1]] = final_value

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
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            self.topic_widgets.clear()
            self._create_dynamic_widgets(parent_frame=self.main_frame, data=self.config_data)
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
            function=f"{self.__class__.__name__}.{current_function_name}",
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
                function=f"{self.__class__.__name__}.{current_function_name}",
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

                if key == 'fields' and isinstance(value, dict):
                    self._create_dynamic_widgets(parent_frame, value, path_prefix)
                    continue

                safe_key = key.replace(TOPIC_DELIMITER, '_')
                current_path = f"{path_prefix}{TOPIC_DELIMITER}{safe_key}" if path_prefix else safe_key

                if isinstance(value, dict):
                    widget_type = value.get("type")
                    label_text = value.get("label", key.replace('_', ' ').title())
                    
                    if widget_type == "OcaBlock":
                        nested_frame = ttk.LabelFrame(parent_frame, text=label_text)
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)
                        self._create_dynamic_widgets(nested_frame, value.get("fields", {}), path_prefix=current_path)
                        continue

                    creation_func = self.widget_factory.get(widget_type)
                    if creation_func:
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
                if isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], ttk.Scale): # Slider
                    str_var, slider = widget_info
                    str_var.set(f"{float(payload_value):.2f}")
                    slider.set(float(payload_value))
                elif isinstance(widget_info[0], tk.BooleanVar): # Toggle Button
                    bool_var, update_func = widget_info
                    new_state = str(payload_value).upper() == 'ON'
                    bool_var.set(new_state)
                    update_func()
                elif isinstance(widget_info[0], tk.StringVar) and isinstance(widget_info[1], list): # Dropdown
                    str_var, options, values = widget_info
                    try:
                        idx = values.index(str(payload_value))
                        str_var.set(options[idx])
                    except (ValueError, IndexError):
                        pass
                elif isinstance(widget_info[0], tk.StringVar): # Button Toggler
                    str_var, update_func = widget_info
                    str_var.set(str(payload_value))
                    update_func()

        except Exception as e:
            console_log(f"❌ Error updating widget for topic '{relative_topic}': {e}")


    def _on_commands_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        try:
            if DEBUG_MODE:
                self.after(0, self._log_to_gui, f"Topic: {topic}\nPayload: {payload}")

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
            console_log(f"❌ Error in _on_commands_message: {e}")