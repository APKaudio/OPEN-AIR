# display/display_child_console.py
#
# This file defines the ConsoleTab, a Tkinter Frame that provides the application's
# console output area. It includes a scrolled text widget for displaying messages
# and a button to clear the console output. This tab is designed to be a child
# of the new TAB_DISPLAY_PARENT.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250810.220500.3 (FIXED: Corrected a race condition by initializing the console_text widget before other setup logic in the __init__ method, resolving the AttributeError.)

current_version = "20250810.220500.3" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250810 * 220500 * 3 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os

# Import the console and GUI redirector functions
from display.console_logic import console_log, set_gui_console_redirector, set_clear_console_func
from display.debug_logic import debug_log # CORRECTED: Import debug_log from src, not display
from src.gui_elements import TextRedirector # Import TextRedirector class

class ConsoleTab(ttk.Frame):
    """
    A Tkinter Frame that provides the application's console output area and controls.
    """
    def __init__(self, master=None, app_instance=None, **kwargs):
        # This function description tells me what this function does
        # Initializes the ConsoleTab, creating a dedicated frame for console output.
        # It sets up a ScrolledText widget and redirects stdout/stderr to it.
        # It also registers a function to clear the console output.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): A reference to the main application instance
        #                          to access shared variables and methods.
        #   **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        #
        # Process of this function
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores a reference to the main app instance.
        #   3. Initializes the console text widget and assigns it to app_instance.
        #   4. Calls `_create_widgets` to build the rest of the UI.
        #   5. Sets up the console redirection.
        #   6. Registers the clear console action.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ConsoleTab...",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        
        # CRITICAL FIX: The console text widget MUST be created here before it's used by other functions.
        # This fixes the AttributeError that was happening.
        self.console_text = scrolledtext.ScrolledText(self, wrap="word", bg="#2b2b2b", fg="#cccccc", insertbackground="white")
        self.app_instance.console_text = self.console_text
        self.console_text.config(state=tk.DISABLED)

        self._create_widgets()

        # FUCKING IMPORTANT: Set the console redirector here, after console_text is created.
        # This ensures all future print() and console_log calls go to this widget.
        if self.app_instance.console_text: # Ensure the app_instance's console_text is set to this widget
            set_gui_console_redirector(TextRedirector(self.app_instance.console_text, "stdout"),
                                       TextRedirector(self.app_instance.console_text, "stderr"))
            console_log(f"Console output redirected to GUI. Version: {current_version}", function=current_function)
            debug_log(f"GUI console redirector set to ConsoleTab's scrolled text widget.",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"ERROR: app_instance.console_text not set to ConsoleTab's widget. Console redirection failed!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)
        
        # NEW: Register the clear console action with console_logic
        set_clear_console_func(self._clear_applications_console_action)
        
        debug_log(f"ConsoleTab initialized. The new console is ready for action!",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        # This function description tells me what this function does
        # Creates and arranges the widgets for the Console tab.
        # This includes the scrolled text area for output and the button to clear it.
        #
        # Inputs to this function
        #   None.
        #
        # Outputs of this function
        #   None. Populates the tab with GUI elements.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ConsoleTab widgets.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        self.grid_rowconfigure(0, weight=1) # Console text area
        self.grid_rowconfigure(1, weight=0) # Clear Console button
        self.grid_columnconfigure(0, weight=1)

        # Console ScrolledText
        # The widget is created in __init__ now. We just need to place it.
        self.console_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        # The state will be managed by console_log itself when writing.

        # Clear Applications Console Button
        self.clear_applications_console_button = ttk.Button(self, text="Clear Applications Console",
                                                            command=self._clear_applications_console_action,
                                                            style='Red.TButton')
        self.clear_applications_console_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        debug_log(f"ConsoleTab widgets created.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)


    def _clear_applications_console_action(self):
        # This function description tells me what this function does
        # Clears the entire content of the ScrolledText widget for the application console.
        #
        # Inputs to this function
        #   None.
        #
        # Process of this function
        #   1. Checks if `app_instance.console_text` exists.
        #   2. If it exists, it deletes all text from the widget.
        #   3. Calls `console_log` to confirm the action.
        #   4. If the widget is not found, it logs an error.
        #
        # Outputs of this function
        #   None. Clears the contents of the console display.
        current_function = inspect.currentframe().f_code.co_name
        if self.app_instance.console_text:
            self.app_instance.console_text.delete("1.0", tk.END)
            console_log(f"Applications console cleared.", function=current_function)
        else:
            debug_log(f"ERROR: Cannot clear applications console, console_text widget not found. Fucking useless!",
                        file=f"{os.path.basename(__file__)} - {current_version}",
                        version=current_version,
                        function=current_function)


    def _on_tab_selected(self, event):
        # This function description tells me what this function does
        # Placeholder for actions to be taken when the Console tab is selected.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object.
        #
        # Outputs of this function
        #   None.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"ConsoleTab selected. No specific refresh action needed.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
