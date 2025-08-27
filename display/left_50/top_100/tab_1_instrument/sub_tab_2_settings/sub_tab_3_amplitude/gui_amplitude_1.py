MQTT_TOPIC_FILTER = "OPEN-AIR/configuration/instrument/Instrument_Settings/Amplitude_Settings"
# display/tabs/dynamic_gui_builder.py
#
# A dynamic GUI component for building widgets based on a JSON data structure received via MQTT.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can benegotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250827.010500.8

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import pathlib
import json

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME

# --- Global Scope Variables ---
current_version = "20250827.010500.8"
current_version_hash = (20250827 * 10500 * 8)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
TOPIC_DELIMITER = "/"
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2
DEFAULT_FRAME_PAD = 5
BUTTON_PADDING_MULTIPLIER = 5
BUTTON_BORDER_MULTIPLIER = 2
DEBUG_MODE = True # Set to False to hide the debug log panel


class DynamicGuiBuilder(ttk.Frame):
    """
    A dynamic GUI component for building widgets based on a JSON data structure
    received via MQTT. It can handle various control types, including labels,
    sliders, buttons, and dropdowns, and correctly maps them to AES70 classes.
    """
    def __init__(self, parent, mqtt_util, *args, **kwargs):
        # Initializes the GUI builder, sets up the layout, and subscribes to the MQTT topic.
        current_function_name = inspect.currentframe().f_code.co_name
        self.current_class_name = self.__class__.__name__

        debug_log(
            message=f"🖥️🟢 Eureka! The grand experiment begins! Initializing the {self.current_class_name}.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            super().__init__(parent, *args, **kwargs)
            self.pack(fill=tk.BOTH, expand=True)

            self.mqtt_util = mqtt_util
            self.topic_widgets = {}
            self.config_data = {}
            self.gui_built = False

            self._apply_styles(theme_name=DEFAULT_THEME)
            colors = THEMES.get(DEFAULT_THEME, THEMES["dark"])

            # --- Main PanedWindow for split view ---
            main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            main_paned_window.pack(fill=tk.BOTH, expand=True)

            # --- Left Frame for Dynamic Widgets ---
            left_frame = ttk.Frame(main_paned_window)
            main_paned_window.add(left_frame, weight=3) # 60% weight

            rebuild_button = ttk.Button(left_frame, text="Rebuild GUI", command=self._rebuild_gui)
            rebuild_button.pack(pady=5)

            self.canvas = tk.Canvas(left_frame, borderwidth=0, highlightthickness=0, background=colors["bg"])
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
            
            scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            self.main_frame = ttk.LabelFrame(self.scroll_frame, text="MQTT Configuration")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)

            # --- Right Frame for MQTT Log (Conditional) ---
            if DEBUG_MODE:
                right_frame = ttk.LabelFrame(main_paned_window, text="MQTT Message Log")
                main_paned_window.add(right_frame, weight=2) # 40% weight
                
                self.log_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, bg=colors["bg"], fg=colors["fg"])
                self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                self.log_text.configure(state='disabled')

            # Subscribe to the entire topic tree
            self.mqtt_util.add_subscriber(topic_filter=f"{MQTT_TOPIC_FILTER}/#", callback_func=self._on_commands_message)

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
            self._create_dynamic_widgets(self.main_frame, self.config_data)
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

    def _create_label(self, parent_frame, label, value, units=None):
        # Creates a read-only label widget.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {parent_frame}, {label}, {value}, {units}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_text = f"{label}: {value}"
            if units:
                label_text += f" {units}"

            label_widget = ttk.Label(sub_frame, text=label_text)
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            console_log(f"✅ Celebration of success! The label '{label}' did get created.")
            return label_widget, sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The label-making machine has gone haywire! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None, None

    def _create_value_box(self, parent_frame, label, config):
        # Creates an editable text box (_Value).
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {parent_frame}, {label}, {config}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            entry_value = tk.StringVar(value=config.get('value', ''))
            entry = ttk.Entry(sub_frame, textvariable=entry_value, style="Custom.TEntry")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=DEFAULT_PAD_X)

            if config.get('units'):
                units_label = ttk.Label(sub_frame, text=config['units'])
                units_label.pack(side=tk.LEFT, padx=(0, DEFAULT_PAD_X))

            def on_entry_change(event):
                new_val = entry_value.get()
                topic = f"{MQTT_TOPIC_FILTER}/{label.replace(' ', '_').lower()}"
                self.mqtt_util.publish_message(topic=topic, value=new_val)

            entry.bind("<FocusOut>", on_entry_change)
            self.topic_widgets[label] = entry
            
            console_log(f"✅ Celebration of success! The value box '{label}' did materialize.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The value box contraption has exploded! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None
            
    def _create_slider_value(self, parent_frame, label, config):
        # Creates a slider and an entry box for a numerical value.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {parent_frame}, {label}, {config}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            entry_value = tk.StringVar(value=config.get('value', '0'))
            entry = ttk.Entry(sub_frame, width=10, style="Custom.TEntry", textvariable=entry_value)
            entry.pack(side=tk.RIGHT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            units_label = ttk.Label(sub_frame, text=config.get('units', ''))
            units_label.pack(side=tk.RIGHT, padx=(0, DEFAULT_PAD_X))

            min_val = float(config.get('min', '0'))
            max_val = float(config.get('max', '100'))
            slider = ttk.Scale(sub_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL)
            slider.set(float(entry_value.get()))
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=DEFAULT_PAD_X)

            def on_slider_move(val):
                entry_value.set(f"{float(val):.2f}")

            def on_entry_change(event):
                try:
                    new_val = float(entry.get())
                    if min_val <= new_val <= max_val:
                        slider.set(new_val)
                        topic = f"{MQTT_TOPIC_FILTER}/{label.replace(' ', '_').lower()}"
                        self.mqtt_util.publish_message(topic=topic, value=new_val)
                except ValueError:
                    console_log("Invalid input, please enter a number.")

            slider.config(command=on_slider_move)
            entry.bind("<FocusOut>", on_entry_change)

            self.topic_widgets[label] = (entry, slider)
            
            console_log(f"✅ Celebration of success! The slider '{label}' did slide into existence.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The slider mechanism is stuck! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None

    def _create_gui_button_toggle(self, parent_frame, label, config):
        # This function creates a single button that toggles between two states (e.g., ON/OFF).
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} to create a binary toggle button for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            options = config.get('options', {})
            on_config = options.get('ON', {})
            off_config = options.get('OFF', {})

            is_on = str(on_config.get('selected', 'false')).lower() in ['true', 'yes']
            
            state_var = tk.BooleanVar(value=is_on)
            
            button = ttk.Button(sub_frame)
            button.pack(fill=tk.X, expand=True)

            def update_button_state():
                # Updates the button's appearance based on its current state.
                current_state = state_var.get()
                if current_state: # State is ON
                    button.config(text=on_config.get('label', 'ON'), style='Selected.TButton')
                else: # State is OFF
                    button.config(text=off_config.get('label', 'OFF'), style='TButton')

            def toggle_command():
                # Flips the state, updates the button, and publishes the change.
                new_state = not state_var.get()
                state_var.set(new_state)
                update_button_state()
                publish_value = 'ON' if new_state else 'OFF'
                topic = f"{MQTT_TOPIC_FILTER}/{label.replace(' ', '_').lower()}"
                self.mqtt_util.publish_message(topic=topic, value=publish_value)

            button.config(command=toggle_command)
            update_button_state() # Set initial text and style

            self.topic_widgets[label] = button
            
            console_log(f"✅ Celebration of success! The toggle button '{label}' did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The toggle switch is sparking furiously! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None


    def _create_gui_dropdown_option(self, parent_frame, label, config):
        # Creates a dropdown menu for multiple choice options.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {parent_frame}, {label}, {config}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.LEFT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            options = [opt['label'] for opt in config.get('options', {}).values()]
            values = [opt['value'] for opt in config.get('options', {}).values()]
            
            selected_option_value = next((opt['value'] for key, opt in config.get('options', {}).items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)

            selected_value = tk.StringVar(value=selected_option_value)

            def on_select(event):
                selected_label = selected_value.get()
                selected_index = options.index(selected_label)
                selected_option_val = values[selected_index]
                topic = f"{MQTT_TOPIC_FILTER}/{label.replace(' ', '_').lower()}"
                self.mqtt_util.publish_message(topic=topic, value=selected_option_val)

            dropdown = ttk.Combobox(sub_frame, textvariable=selected_value, values=options, state="readonly")
            dropdown.bind("<<ComboboxSelected>>", on_select)
            dropdown.pack(side=tk.LEFT, padx=DEFAULT_PAD_X)

            self.topic_widgets[label] = dropdown
            
            console_log(f"✅ Celebration of success! The dropdown '{label}' did drop down.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The dropdown has dropped off! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None

    def _create_gui_button_toggler(self, parent_frame, label, config):
        # Creates a set of custom buttons that behave like radio buttons ("bucket of buttons").
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} to create a bucket of buttons for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            group_frame = ttk.LabelFrame(parent_frame, text=label)
            group_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
            
            button_container = ttk.Frame(group_frame)
            button_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            options_data = config.get('options', {})
            buttons = {}
            
            selected_key = next((key for key, opt in options_data.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
            selected_var = tk.StringVar(value=selected_key)

            def update_button_styles():
                current_selection = selected_var.get()
                for key, button_widget in buttons.items():
                    if key == current_selection:
                        button_widget.config(style='Selected.TButton')
                    else:
                        button_widget.config(style='TButton')

            def create_command(key):
                def command():
                    selected_var.set(key)
                    update_button_styles()
                    self.mqtt_util.publish_message(topic=f"{MQTT_TOPIC_FILTER}/{label.replace(' ', '_').lower()}", value=key)
                return command

            max_cols = 4 
            row_num = 0
            col_num = 0

            for option_key, option_data in options_data.items():
                button_text = f"{option_data.get('label', '')}\n{option_data.get('value', '')} {option_data.get('units', '')}"
                
                button = ttk.Button(
                    button_container,
                    text=button_text,
                    command=create_command(option_key)
                )
                button.grid(row=row_num, column=col_num, padx=2, pady=2, sticky="ew")
                button_container.grid_columnconfigure(col_num, weight=1)
                buttons[option_key] = button

                col_num += 1
                if col_num >= max_cols:
                    col_num = 0
                    row_num += 1

            update_button_styles()
            self.topic_widgets[label] = group_frame
            
            console_log(f"✅ Celebration of success! The button toggler '{label}' did toggle into view.")
            return group_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The button toggler is refusing to toggle! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
            return None


    def _create_dynamic_widgets(self, parent_frame, data):
        # Recursively creates widgets based on the JSON structure.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {parent_frame}, {data}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            for key, value in data.items():
                if isinstance(value, dict):
                    widget_type = value.get("type")
                    label_text = value.get("label", key.replace('_', ' ').title())
                    
                    if widget_type == "OcaBlock":
                        nested_frame = ttk.LabelFrame(parent_frame, text=label_text)
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)
                        self._create_dynamic_widgets(nested_frame, value.get("fields", {}))
                    elif widget_type == "_sliderValue":
                        self._create_slider_value(parent_frame=parent_frame, label=label_text, config=value)
                    elif widget_type in ("_GuiButtonToggle", "_buttonToggle"):
                        self._create_gui_button_toggle(parent_frame=parent_frame, label=label_text, config=value)
                    elif widget_type in ("_GuiDropDownOption", "_DropDownOption"):
                        self._create_gui_dropdown_option(parent_frame=parent_frame, label=label_text, config=value)
                    elif widget_type == "_GuiButtonToggler":
                        self._create_gui_button_toggler(parent_frame=parent_frame, label=label_text, config=value)
                    elif widget_type == "_Value":
                        self._create_value_box(parent_frame=parent_frame, label=label_text, config=value)
                    elif widget_type == "_Label":
                        self._create_label(parent_frame=parent_frame, label=label_text, value=value.get("value"), units=value.get("units"))
                    else:
                        nested_frame = ttk.LabelFrame(parent_frame, text=key.replace('_', ' ').title())
                        nested_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_FRAME_PAD, pady=DEFAULT_FRAME_PAD)
                        self._create_dynamic_widgets(nested_frame, value)
                else:
                    self._create_label(parent_frame=parent_frame, label=key.replace('_', ' ').title(), value=value)
            
            console_log("✅ Celebration of success! The dynamic widgets did assemble themselves!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The widget creation-ray has misfired! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )

    def _on_commands_message(self, topic, payload):
        # The main callback function that processes incoming MQTT messages.
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"Entering {current_function_name} with arguments: {topic}, {payload}",
            file=current_file,
            version=current_version,
            function=f"{self.current_class_name}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            if DEBUG_MODE:
                self.after(0, self._log_to_gui, f"Topic: {topic}\nPayload: {payload}")

            # Reconstruct the nested dictionary from the topic path
            base_topic = MQTT_TOPIC_FILTER
            if topic.startswith(base_topic):
                relative_topic = topic[len(base_topic):].strip(TOPIC_DELIMITER)
                if not relative_topic:
                    return
                path_parts = relative_topic.split(TOPIC_DELIMITER)
                self._update_nested_dict(path_parts, payload)

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"🖥️🔴 The MQTT message has caused a paradox! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.current_class_name}.{current_function_name}",
                console_print_func=console_log
            )
