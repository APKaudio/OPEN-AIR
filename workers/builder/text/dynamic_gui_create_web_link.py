# workers/builder/dynamic_gui_create_web_link.py

import tkinter as tk
from tkinter import ttk
import webbrowser
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
import os

class WebLinkCreatorMixin:
    def _create_web_link(self, parent_frame, label, config, path):
        """Creates a web link widget."""
        current_function_name = "_create_web_link"
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬⚡️ Entering '{current_function_name}' to open a portal (web link) for '{label}'.",
**_get_log_args()
                


            )

        frame = ttk.Frame(parent_frame)

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
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"Opening URL: {url}", file=os.path.basename(__file__), function="_open_url")
                    webbrowser.open_new(url)
                except Exception as e:
                    debug_log(message=f"🔴 ERROR opening URL: {e}")
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(message=f"🔴 ERROR opening URL: {e}", file=os.path.basename(__file__), function="_open_url", 

)


            link_label.bind("<Button-1>", _open_url)

            self.topic_widgets[path] = {"widget": link_label}

            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"✅ SUCCESS! The portal to '{label}' has been opened!",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                    


                )
            return frame
        except Exception as e:
            debug_log(message=f"💥 KABOOM! The web link for '{label}' has collapsed into a singularity! Error: {e}")
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"💥 KABOOM! The web link for '{label}' has collapsed into a singularity! Error: {e}",
                    file=os.path.basename(__file__),
                    version=app_constants.CURRENT_VERSION,
                    function=current_function_name
                    


                )
            return None