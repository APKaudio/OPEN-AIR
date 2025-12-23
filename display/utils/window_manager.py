# display/utils/window_manager.py

import tkinter as tk
from tkinter import ttk
import inspect
import os
import sys
import pathlib

class WindowManager:
    """
    Manages Toplevel windows for tear-off tabs and handles window management protocols.
    """
    def __init__(self, application_instance, current_version, LOCAL_DEBUG_ENABLE, debug_log_func):
        self.application = application_instance # Reference to the main Application class
        self.current_version = current_version
        self.LOCAL_DEBUG_ENABLE = LOCAL_DEBUG_ENABLE
        self.debug_log = debug_log_func 
        self.torn_off_windows = {} # To keep track of torn-off windows

    def tear_off_tab(self, event):
        """
        Handles the tear-off functionality for a notebook tab.
        When Ctrl + Left Click is detected on a tab, it detaches that tab
        into its own Toplevel window.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self.debug_log(
            message=f"▶️ '{current_function_name}' for event.",
            file=os.path.basename(__file__),
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}"
           
        )

        notebook = event.widget
        
        # Ensure the event is a Control-Left-Button click
        if not (event.state & 4 and event.num == 1): # 4 is Control mask, 1 is Left Button
            self.debug_log(
                message=f"Event not a Control-Left-Button click, ignoring.",
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
               
            )
            return

        try:
            # Get the currently selected tab
            selected_tab_id = notebook.select()
            if not selected_tab_id:
                self.debug_log(
                    message="No tab selected, cannot tear off.",
                    file=os.path.basename(__file__),
                    version=self.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                   
                )
                return

            # The widget associated with the selected tab_id is the *container frame* for that tab's content.
            tab_content_frame = notebook.nametowidget(selected_tab_id)
            tab_text = notebook.tab(selected_tab_id, "text")
            
            # Check if the tab content is already a Toplevel (shouldn't happen if logic is correct)
            if isinstance(tab_content_frame, tk.Toplevel):
                self.debug_log(
                    message="Selected tab is already a Toplevel, ignoring tear-off.",
                    file=os.path.basename(__file__),
                    version=self.current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}"
                   
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
            
            self.debug_log(
                message=f"✅ Tab '{tab_text}' torn off into a new window.",
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
               
            )

        except Exception as e:
            self.debug_log(
                message=f"❌ Error tearing off tab: {e}",
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
               
            )

    def _on_tear_off_window_close(self, top_level_window, original_tab_id, original_notebook):
        """
        Handles the closing of a tear-off Toplevel window.
        Currently, it destroys the window and removes it from tracking.
        Re-attachment logic would be added here.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self.debug_log(
            message=f"▶️ '_on_tear_off_window_close' for window {original_tab_id}.",
            file=os.path.basename(__file__),
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}"
           
        )

        if original_tab_id in self.torn_off_windows:
            tab_info = self.torn_off_windows[original_tab_id]
            tab_text = tab_info.get("tab_text", "Unknown Tab")
            
            self.debug_log(
                message=f"Tear-off window for '{tab_text}' closed. Re-attachment not yet implemented.",
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
               
            )
            
            # Destroy the Toplevel window
            top_level_window.destroy()
            
            # Remove from tracking
            del self.torn_off_windows[original_tab_id]
        else:
            self.debug_log(
                message="Tear-off window closed, but not found in tracking. Destroying.",
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{current_function_name}"
               
            )
            top_level_window.destroy()

    def re_attach_tab(self, torn_off_window_id):
        """
        Re-attaches a torn-off tab back to its original notebook or a new one.
        This is a placeholder and requires significant logic to implement fully.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self.debug_log(
            message="Re-attaching tab functionality is not yet implemented.",
            file=os.path.basename(__file__),
            version=self.current_version,
            function=f"{self.__class__.__name__}.{current_function_name}"
           
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
