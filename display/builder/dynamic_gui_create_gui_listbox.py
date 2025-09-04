# display/builder/dynamic_gui_create_gui_listbox.py
#
# A mixin class for the DynamicGuiBuilder that handles the creation of a listbox menu.
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
# Version 20250903.221737.1

import os
import tkinter as tk
from tkinter import ttk
import inspect
from decimal import Decimal

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250903.221737.1"
current_version_hash = (20250903 * 221737 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants ---
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 2


class GuiListboxCreatorMixin:
    """
    A mixin class that provides the functionality for creating a
    Listbox widget.
    """
    def _create_gui_listbox(self, parent_frame, label, config, path):
        # Creates a listbox menu for multiple choice options.
        current_function_name = inspect.currentframe().f_code.co_name

        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to create a listbox for '{label}'.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            sub_frame = ttk.LabelFrame(parent_frame, text=label)
            sub_frame.pack(fill=tk.BOTH, expand=True, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

            listbox_frame = ttk.Frame(sub_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
            listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, exportselection=False, selectmode=tk.SINGLE)
            
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            options_map = config.get('options', {})

            def rebuild_options_for_listbox(lb, cfg):
                # Rebuilds the option list for the listbox based on a new configuration.
                lb.delete(0, tk.END)
                options_map_local = cfg.get('options', {})
                
                active_options = {k: v for k, v in options_map_local.items() if str(v.get('active', 'false')).lower() in ['true', 'yes']}
                
                try:
                    sorted_options = sorted(active_options.items(), key=lambda item: Decimal(item[1].get('value')))
                except:
                    sorted_options = sorted(active_options.items(), key=lambda item: item[1].get('value', item[0]))

                for key, opt in sorted_options:
                    lb.insert(tk.END, opt.get('label_active', key))

                initial_selected_key = next((key for key, opt in options_map_local.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)
                if initial_selected_key:
                    initial_label = options_map_local[initial_selected_key].get('label_active', initial_selected_key)
                    if initial_label in lb.get(0, tk.END):
                        idx = lb.get(0, tk.END).index(initial_label)
                        lb.select_set(idx)
                        lb.see(idx)

            rebuild_options_for_listbox(listbox, config)
            self._last_selected_option_listbox = next((key for key, opt in options_map.items() if str(opt.get('selected', 'no')).lower() in ['yes', 'true']), None)

            def on_select(event):
                widget = event.widget
                selection_indices = widget.curselection()
                if not selection_indices:
                    return

                selected_index = selection_indices[0]
                selected_label = widget.get(selected_index)
                
                try:
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label_active', key) == selected_label), None)
                    
                    if selected_key and selected_key != self._last_selected_option_listbox:
                        # Deselect the previous option
                        if self._last_selected_option_listbox:
                            old_path = f"{path}/options/{self._last_selected_option_listbox}/selected"
                            self._transmit_command(relative_topic=old_path, payload='false')

                        # Select the new option
                        new_path = f"{path}/options/{selected_key}/selected"
                        self._transmit_command(relative_topic=new_path, payload='true')
                        
                        self._last_selected_option_listbox = selected_key

                    debug_log(
                        message=f"GUI ACTION: Publishing selection for '{selected_key}' to path '{path}'.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                except (ValueError, StopIteration):
                    console_log("❌ Invalid selection in listbox.")

            listbox.bind("<<ListboxSelect>>", on_select)

            if path:
                self.topic_widgets[path] = (listbox, rebuild_options_for_listbox, options_map)

            console_log("✅ Celebration of success! The listbox menu did appear.")
            return sub_frame

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for '{label}': {e}")
            debug_log(
                message=f"🛠️🔴 Arrr, the code be capsized! The listbox creation has failed! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            return None