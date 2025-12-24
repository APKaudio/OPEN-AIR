# display/utils/window_manager.py

import tkinter as tk
from tkinter import ttk
import inspect
import os
import sys
import pathlib
import workers.setup.app_constants as app_constants # Import app_constants
from workers.logger.logger import debug_log # Import the global debug_log
from workers.utils.log_utils import _get_log_args

class WindowManager:
    """
    Manages Toplevel windows for tear-off tabs and handles window management protocols.
    """
    def __init__(self, application_instance): # Removed current_version, LOCAL_DEBUG_ENABLE, debug_log_func
        self.application = application_instance # Reference to the main Application class
        # self.current_version = app_constants.current_version # No longer needed
        # self.LOCAL_DEBUG_ENABLE = app_constants.LOCAL_DEBUG_ENABLE # No longer needed
        # self.debug_log = debug_log # No longer needed
        self.torn_off_windows = {} # To keep track of torn-off windows

    def tear_off_tab(self, event):
        """
        Handles the tear-off functionality for a notebook tab.
        When Ctrl + Left Click is detected on a tab, it detaches that tab
        into its own Toplevel window.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️🟢 Initiating 'tear_off_tab'! Preparing to detach a fragment of the GUI for independent exploration!",
                **_get_log_args()
            )

        notebook = event.widget
        
        # Ensure the event is a Control-Left-Button click
        if not (event.state & 4 and event.num == 1): # 4 is Control mask, 1 is Left Button
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🖥️🟡 A mere distraction! Event is not a Control-Left-Button click. Ignoring the urge to tear off.",
                    **_get_log_args()
                )
            return

        try:
            # Get the currently selected tab
            selected_tab_id = notebook.select()
            if not selected_tab_id:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message="🖥️🟡 The canvas is empty! No tab selected to tear off. My powers are limited!",
                        **_get_log_args()
                    )               
                return

            # The widget associated with the selected tab_id is the *container frame* for that tab's content.
            tab_content_frame = notebook.nametowidget(selected_tab_id)
            tab_text = notebook.tab(selected_tab_id, "text")
            
            # Check if the tab content is already a Toplevel (shouldn't happen if logic is correct)
            if isinstance(tab_content_frame, tk.Toplevel):
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message="🖥️🟡 A paradox! Selected tab is already a Toplevel window. My tearing magic is redundant!",
                        **_get_log_args()
                    )                
                return

            # Create a new Toplevel window
            tear_off_window = tk.Toplevel(notebook.winfo_toplevel())
            tear_off_window.title(f"{tab_text} - Detached")
            
            # Configure the Toplevel window's close button protocol
            # We pass the notebook widget and the original tab ID to the close handler
            tear_off_window.protocol("WM_DELETE_WINDOW", lambda: self._on_tear_off_window_close(tear_off_window, selected_tab_id, notebook))
            
            # Detach the selected tab's frame from the notebook
            # The frame needs to be removed from the notebook's internal management
            # and then reparented to the Toplevel window.
            
            # Remove the frame from the notebook's children and pack it into the Toplevel
            tab_content_frame.pack_forget() # Remove from current parent (notebook tab's internal frame)
            
            # The exact way to remove a widget from a ttk.Notebook's internal structure might vary.
            # Using notebook.forget(selected_tab_id) is the standard way to remove the tab from the UI.
            # This also detaches the associated frame.
            notebook.forget(selected_tab_id) 
            
            # Reparent the widget to the new Toplevel
            tab_content_frame.pack(in_=tear_off_window, fill=tk.BOTH, expand=True)

            # Store the torn-off window and its original tab ID/notebook
            self.torn_off_windows[selected_tab_id] = {
                "window": tear_off_window,
                "original_tab_widget": tab_content_frame, # Store the content frame
                "original_notebook": notebook,
                "original_tab_id": selected_tab_id,
                "tab_text": tab_text
            }
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🖥️✅ Eureka! Tab '{tab_text}' has been liberated into its own Toplevel window!",
                    **_get_log_args()
                )

        except Exception as e:
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🖥️🔴 A glitch in the matrix! Error tearing off tab: {e}. The experiment encountered unexpected resistance!",
                    **_get_log_args()
                )

    def _on_tear_off_window_close(self, top_level_window, original_tab_id, original_notebook):
        """
        Handles the closing of a tear-off Toplevel window.
        Currently, it destroys the window and removes it from tracking.
        Re-attachment logic would be added here.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️🟢 Observing the closing ritual! '_on_tear_off_window_close' for window {original_tab_id}.",
                **_get_log_args()
            )

        if original_tab_id in self.torn_off_windows:
            tab_info = self.torn_off_windows[original_tab_id]
            tab_text = tab_info.get("tab_text", "Unknown Tab")
            
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🖥️🟡 The detached entity '{tab_text}' has vanished! Re-attachment protocols are still in the experimental phase.",
                    **_get_log_args()
                )
            
            # Destroy the Toplevel window
            top_level_window.destroy()
            
            # Remove from tracking
            del self.torn_off_windows[original_tab_id]
        else:
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message="🖥️🟡 A phantom closure! Tear-off window closed, but its tracking data is elusive. Vanishing it!",
                    **_get_log_args()
                )
            top_level_window.destroy()

    def re_attach_tab(self, torn_off_window_id):
        """
        Re-attaches a torn-off tab back to its original notebook or a new one.
        This is a placeholder and requires significant logic to implement fully.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="🖥️🟡 Re-attaching tab functionality is currently a theoretical construct. Implementation pending further research!",
                **_get_log_args()
            )

# Example of how to integrate into gui_display.py:
# In Application.__init__:
# self.window_manager = WindowManager(self, app_constants.current_version, app_constants.LOCAL_DEBUG_ENABLE,  debug_log)
#
# In Application._build_from_directory (when creating a notebook):
# notebook.bind('<Control-Button-1>', self.window_manager.tear_off_tab)
#
# The exact widget handling for reparenting may require careful adjustment
# based on the internal structure of ttk.Notebook and how frames are managed.
