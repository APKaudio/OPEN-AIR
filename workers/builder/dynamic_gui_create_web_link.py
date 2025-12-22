# workers/builder/dynamic_gui_create_web_link.py

import tkinter as tk
from tkinter import ttk
import webbrowser
import workers.setup.app_constants as app_constants
from workers.logger.logger import debug_log, console_log
import os

class WebLinkCreatorMixin:
    def _create_web_link(self, parent_frame, label, config, path):
        """Creates a web link widget."""
        current_function_name = "_create_web_link"
        if app_constants.Local_Debug_Enable:
            debug_log(message=f"Creating web link for {label}", file=os.path.basename(__file__), function=current_function_name)

        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)

        try:
            url = config.get("url", "#")
            link_label = ttk.Label(
                frame, 
                text=label, 
                foreground="blue", 
                cursor="hand2"
            )
            link_label.pack(side=tk.LEFT)
            
            def _open_url(event):
                try:
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"Opening URL: {url}", file=os.path.basename(__file__), function="_open_url")
                    webbrowser.open_new(url)
                except Exception as e:
                    console_log(f"🔴 ERROR opening URL: {e}")
                    if app_constants.Local_Debug_Enable:
                        debug_log(message=f"🔴 ERROR opening URL: {e}", file=os.path.basename(__file__), function="_open_url", console_print_func=console_log)


            link_label.bind("<Button-1>", _open_url)

            self.topic_widgets[path] = {"widget": link_label}
        except Exception as e:
            console_log(f"🔴 ERROR creating web link: {e}")
            if app_constants.Local_Debug_Enable:
                debug_log(message=f"🔴 ERROR creating web link: {e}", file=os.path.basename(__file__), function=current_function_name, console_print_func=console_log)