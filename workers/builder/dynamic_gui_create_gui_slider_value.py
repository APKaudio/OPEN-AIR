# workers/builder/dynamic_gui_create_gui_slider_value.py
#
# This file (dynamic_gui_create_gui_slider_value.py) provides the SliderValueCreatorMixin class for creating slider widgets with text entry in the GUI.
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
import tkinter as tk
from tkinter import ttk
import inspect

# --- Module Imports ---
from workers.logger.logger import debug_log, console_log, log_visa_command


Local_Debug_Enable = True





# --- Global Scope Variables ---
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2

class SliderValueCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    slider widget combined with a text entry box.
    """
    def _create_slider_value(self, parent_frame, label, config, path):
        # Creates a slider and an entry box for a numerical value.
        current_function_name = inspect.currentframe().f_code.co_name

        if Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Entering '{current_function_name}' to create a slider and value box for '{label}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

        try:
            sub_frame = ttk.Frame(parent_frame)
            sub_frame.pack(fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            # --- Layout Refactor: Start ---
            # Line 1: Label
            label_widget = ttk.Label(sub_frame, text=f"{label}:")
            label_widget.pack(side=tk.TOP, fill=tk.X, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X), pady=(0, DEFAULT_PAD_Y))

            # Line 2: Slider
            min_val = float(config.get('min', '0'))
            max_val = float(config.get('max', '100'))
            
            # 🛠️ New fix: Create a custom style for a thicker slider
            style = ttk.Style(sub_frame)
            style_name = 'Thicker.Horizontal.TScale'
            style.configure(style_name, sliderlength=40)
            slider = ttk.Scale(sub_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, style=style_name)
            
            slider.pack(side=tk.TOP, fill=tk.X, expand=True, padx=DEFAULT_PAD_X, pady=(0, DEFAULT_PAD_Y))

            # Line 3: Textbox and Units
            value_unit_frame = ttk.Frame(sub_frame)
            value_unit_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

            units_label = ttk.Label(value_unit_frame, text=config.get('units', ''))
            units_label.pack(side=tk.RIGHT, padx=(DEFAULT_PAD_X, DEFAULT_PAD_X))

            entry_value = tk.StringVar(value=config.get('value', '0'))
            entry = ttk.Entry(value_unit_frame, width=7, style="Custom.TEntry", textvariable=entry_value, justify=tk.RIGHT)
            entry.pack(side=tk.RIGHT, padx=(DEFAULT_PAD_X, 0))
            
            try:
                initial_val = float(entry_value.get())
                slider.set(initial_val)
            except (ValueError, tk.TclError):
                slider.set(min_val)
            # --- Layout Refactor: End ---

            def on_slider_move(val):
                entry_value.set(f"{float(val):.2f}")

            def on_slider_release(event):
                new_val = float(slider.get())
                if Local_Debug_Enable:
                    debug_log(
                        message=f"GUI ACTION: Publishing to '{path}' with value '{new_val}'",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                self._transmit_command(relative_topic=path, payload=new_val)

            def on_entry_change(event):
                try:
                    new_val = float(entry.get())
                    if min_val <= new_val <= max_val:
                        slider.set(new_val)
                        if Local_Debug_Enable:
                            debug_log(
                                message=f"GUI ACTION: Publishing to '{path}' with value '{new_val}'",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                        self._transmit_command(relative_topic=path, payload=new_val)
                except ValueError:
                    console_log("Invalid input, please enter a number.")

            slider.config(command=on_slider_move)
            slider.bind("<ButtonRelease-1>", on_slider_release)
            entry.bind("<FocusOut>", on_entry_change)
            entry.bind("<Return>", on_entry_change)

            if path:
                self.topic_widgets[path] = (entry_value, slider)

            console_log("✅ Celebration of success! The slider value box did appear.")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🟢 Exiting '{current_function_name}'. Slider '{label}' created.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            if Local_Debug_Enable:
                debug_log(
                    message=f"🛠️🔴 Arrr, the code be capsized! The slider value box creation has failed! The error be: {e}",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
            return None