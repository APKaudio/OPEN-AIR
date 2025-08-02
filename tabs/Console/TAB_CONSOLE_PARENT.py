# tabs/Console/TAB_CONSOLE_PARENT.py
#
# This file defines the TAB_CONSOLE_PARENT class, which serves as a container
# for the ConsoleTab. It integrates the console and logging controls into the
# main application's two-layer tab structure.
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
# Version 20250802.0070.1 (Initial creation of TAB_CONSOLE_PARENT.)

current_version = "20250802.0070.1"

import tkinter as tk
from tkinter import ttk
import inspect
import os

# Import the child tab
from tabs.Console.tab_console import ConsoleTab

# Import debug_log
from src.debug_logic import debug_log

class TAB_CONSOLE_PARENT(ttk.Frame):
    """
    Parent tab for Console and Logging functionalities.
    Contains the ConsoleTab.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        """
        Initializes the TAB_CONSOLE_PARENT.

        Inputs:
            master (tk.Widget): The parent notebook widget.
            app_instance (App): The main application instance.
            console_print_func (function): Function to print messages to the GUI console.
            **kwargs: Arbitrary keyword arguments for Tkinter Frame.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Initializing TAB_CONSOLE_PARENT...",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        # self.console_print_func = console_print_func # Not directly used here, passed to child

        self._create_widgets()


    def _create_widgets(self):
        """
        Creates the child notebook and adds the ConsoleTab to it.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Creating TAB_CONSOLE_PARENT widgets.",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Configure grid for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a child notebook for this parent tab
        self.child_notebook = ttk.Notebook(self, style='Child.TNotebook')
        self.child_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Get the color for this parent tab from app_instance
        parent_tab_name = "CONSOLE" # Assuming this will be the tab name in main_app
        bg_color = self.app_instance.parent_tab_colors.get(parent_tab_name, {}).get("active", "#333333")
        
        # Apply background color to the child notebook frame
        self.child_notebook.configure(style=f'Child.TNotebook.{parent_tab_name}.TNotebook')
        self.style = ttk.Style()
        self.style.configure(f'Child.TNotebook.{parent_tab_name}.TNotebook', background=bg_color)
        self.style.map(f'Child.TNotebook.{parent_tab_name}.TNotebook.Tab',
                       background=[('selected', bg_color), ('active', bg_color)],
                       foreground=[('selected', 'white'), ('active', 'white')])

        # Instantiate and add the ConsoleTab
        self.console_tab = ConsoleTab(self.child_notebook, app_instance=self.app_instance)
        self.child_notebook.add(self.console_tab, text="Console & Debug")

        # Bind child tab selection event
        self.child_notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)

        debug_log(f"TAB_CONSOLE_PARENT widgets created.",
                    file=current_file,
                    version=current_version,
                    function=current_function)


    def _on_tab_selected(self, event):
        """
        Handles tab change events within the child notebook of the Console tab,
        propagating the selection event to the active child tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = os.path.basename(__file__)
        debug_log(f"Console Child Tab changed. Time to update the display!",
                    file=current_file,
                    version=current_version,
                    function=current_function)

        # Get the currently selected tab widget
        selected_child_tab_id = self.child_notebook.select()
        selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)

        # If the selected child tab has an _on_tab_selected method, call it
        if hasattr(selected_child_tab_widget, '_on_tab_selected'):
            selected_child_tab_widget._on_tab_selected(event)
            debug_log(f"Propagated _on_tab_selected to active child tab: {selected_child_tab_widget.winfo_name()}.",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        else:
            debug_log(f"Active child tab {selected_child_tab_widget.winfo_name()} has no _on_tab_selected method. Fucking useless!",
                        file=current_file,
                        version=current_version,
                        function=current_function)

