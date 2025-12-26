# workers/builder/dynamic_gui_create_gui_listbox.py
#
# This file (dynamic_gui_create_gui_listbox.py) provides the GuiListboxCreatorMixin class for dynamically creating Listbox widgets in the GUI.
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


import tkinter as tk
from tkinter import ttk
import os
import inspect
from decimal import Decimal, InvalidOperation # Add InvalidOperation
# --- Module Imports ---
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      

# --- Global Scope Variables ---
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

        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to materialize a listbox for '{label}'.",
              **_get_log_args()
                


            )

        try:
            sub_frame = ttk.Frame(parent_frame)

            label_widget = ttk.Label(sub_frame, text=label)
            label_widget.pack(anchor='w', padx=DEFAULT_PAD_X, pady=2)

            listbox_frame = ttk.Frame(sub_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
            listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, exportselection=False, selectmode=tk.SINGLE)
            
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            options_map = config.get('options', {})
            selected_option_var = tk.StringVar(sub_frame)
            
            def rebuild_options_for_listbox(lb, cfg, current_selection_var):
                # Rebuilds the option list for the listbox based on a new configuration.
                lb.delete(0, tk.END)
                options_map_local = cfg.get('options', {})
                
                active_options = {k: v for k, v in options_map_local.items() if str(v.get('active', 'false')).lower() in ['true', 'yes']}
                
                def sort_key(item):
                    value = item[1].get('value')
                    return str(value)

                sorted_options = sorted(active_options.items(), key=sort_key)

                current_selection_label = ""
                for key, opt in sorted_options:
                    lb.insert(tk.END, opt.get('label_active', key))
                    if str(opt.get('selected', 'no')).lower() in ['yes', 'true']:
                        current_selection_label = opt.get('label_active', key)

                if current_selection_label:
                    if current_selection_label in lb.get(0, tk.END):
                        idx = lb.get(0, tk.END).index(current_selection_label)
                        lb.select_set(idx)
                        lb.see(idx)
                        current_selection_var.set(current_selection_label) # Update the StringVar

            rebuild_options_for_listbox(listbox, config, selected_option_var)
            self._last_selected_option_listbox = selected_option_var.get() # Initialize from var

            def update_listbox_from_var(*args):
                new_selection_label = selected_option_var.get()
                if new_selection_label:
                    if new_selection_label in listbox.get(0, tk.END):
                        idx = listbox.get(0, tk.END).index(new_selection_label)
                        listbox.select_clear(0, tk.END) # Clear previous selections
                        listbox.select_set(idx)
                        listbox.see(idx)
                        if app_constants.LOCAL_DEBUG_ENABLE:
                            debug_log(
                                message=f"⚡ fluxing... Listbox '{label}' updated visually to '{new_selection_label}' from MQTT.",
                                **_get_log_args()
                            )
                elif new_selection_label == "": # Handle case where selection is cleared
                    listbox.select_clear(0, tk.END)

            selected_option_var.trace_add("write", update_listbox_from_var)

            def on_select(event):
                widget = event.widget
                selection_indices = widget.curselection()
                if not selection_indices:
                    return

                selected_index = selection_indices[0]
                selected_label = widget.get(selected_index)
                
                try:
                    selected_key = next((key for key, opt in options_map.items() if opt.get('label_active', key) == selected_label), None)
                    
                    if selected_key:
                        # Iterate over all options to enforce single selection
                        for key, opt in options_map.items():
                            is_selected = (key == selected_key)
                            topic_path = f"{path}/options/{key}/selected"
                            self._transmit_command(widget_name=topic_path, value=str(is_selected).lower())
                        
                        selected_option_var.set(selected_label) # Update the GUI

                        if app_constants.LOCAL_DEBUG_ENABLE: 
                            debug_log(
                                message=f"GUI ACTION: Publishing selection for '{selected_key}' to path '{path}'.",
                                **_get_log_args()
                            )
                except (ValueError, StopIteration):
                    debug_log(message="❌ Invalid selection in listbox.")

            listbox.bind("<<ListboxSelect>>", on_select)

            if path and self.state_mirror_engine:
                # Register the StringVar with the StateMirrorEngine for MQTT updates
                self.state_mirror_engine.register_widget(path, selected_option_var, self.tab_name)
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬 Widget '{label}' ({path}) registered with StateMirrorEngine (StringVar: {selected_option_var.get()}).",
                        **_get_log_args()
                    )

            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"✅ SUCCESS! The listbox '{label}' has been successfully generated!",
**_get_log_args()
                )
            return sub_frame

        except Exception as e:
            debug_log(message=f"❌ Error in {current_function_name} for '{label}': {e}")
            if app_constants.LOCAL_DEBUG_ENABLE: 
                debug_log(
                    message=f"💥 KABOOM! The listbox for '{label}' has vanished into a different dimension! Error: {e}",
                    **_get_log_args()
                )
            return None