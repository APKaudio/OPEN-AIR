# tabs/Experiments/TAB_EXPERIMENTS_PARENT.py
#
# This file defines the parent tab for Experiment-related functionalities.
# It acts as a container for child tabs such as "Intermod", "JSON API", and now "Credits".
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
# Version 20250820.102100.3 (UPDATED: Added a new child tab for Credits and made it the first tab.)
# Version 20250818.193400.1 (UPDATED: Added a new child tab for YakBeg functionality.)
# Version 20250818.193500.1 (FIXED: Moved YakBegTab import inside __init__ to resolve circular import error.)

current_version = "Version 20250820.102100.3"
current_version_hash = 20250820 * 102100 * 3

import tkinter as tk
from tkinter import ttk
import inspect
import os
from datetime import datetime
from display.debug_logic import debug_log # For logging and debugging
from display.console_logic import console_log # For user-facing messages

# Import the child tabs
from tabs.Experiments.tab_experiments_credits import CreditsTab # NEW: Import CreditsTab
from tabs.Experiments.tab_experiments_child_intermod import InterModTab
from tabs.Experiments.tab_experiments_child_JSON_api import JsonApiTab
from tabs.Experiments.tab_experiments_colouring import ColouringTab
from tabs.Experiments.tab_experiments_child_initial_configuration import InitialConfigurationTab
# Removed: from tabs.Experiments.tab_experiments_child_YakBeg import YakBegTab
from tabs.Experiments.tab_experiments_child_YakBeg import YakBegTab

class ExperimentsParentTab(tk.Frame):
    """
    This is the parent tab for all experiment-related functionalities. It is a container
    for multiple child tabs that each handle a specific experiment or process.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, *args, **kwargs):
        # [A brief, one-sentence description of the function's purpose.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering ExperimentsParentTab.__init__.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        try:
            super().__init__(parent_notebook, **kwargs)
            self.app_instance = app_instance
            self.console_print_func = console_print_func
            self.parent_notebook = parent_notebook

            # Create a Notebook to hold the child tabs
            self.child_notebook = ttk.Notebook(self)
            self.child_notebook.pack(expand=True, fill="both")

            # Initialize and add child tabs to the notebook
            self.credits_tab = CreditsTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.credits_tab, text="Credits")
            
            self.intermod_tab = InterModTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.intermod_tab, text="Intermod")

            self.json_api_tab = JsonApiTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.json_api_tab, text="JSON API")

            self.colouring_tab = ColouringTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.colouring_tab, text="Colouring")

            self.initial_config_tab = InitialConfigurationTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.initial_config_tab, text="Initial Config")

            self.yakbeg_tab = YakBegTab(self.child_notebook, self.app_instance, self.console_print_func)
            self.child_notebook.add(self.yakbeg_tab, text="YakBeg") # NEW: Add the YakBegTab

            self.child_notebook.bind("<<NotebookTabChanged>>", self._on_child_tab_selected)

            debug_log(f"ExperimentsParentTab initialized with {self.child_notebook.tabs()} child tabs. All set to go! 🛡️",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)

        except Exception as e:
            console_log(f"❌ Error in ExperimentsParentTab initialization: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)
            raise

    def _on_child_tab_selected(self, event):
        """Handles tab change events within this parent's child notebook."""
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)

    def _on_parent_tab_selected(self, event):
        # Function Description
        # Handles the event when this parent tab is selected. It now also switches the display
        # pane to the "Debug" tab automatically.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Experiments Parent tab selected. Forcing display view to Debug.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        # Switch the display parent to the Debug tab
        if hasattr(self.app_instance, 'display_parent_tab'):
            self.app_instance.display_parent_tab.notebook.select(self.app_instance.display_parent_tab.debug_tab)
            debug_log(f"Forced display tab to Debug. A captain must always know the state of his ship! 🧭",
                        file=f"{os.path.basename(__file__)}",
                        version=current_version,
                        function=current_function)
        
        # Check if a child tab is already selected and call its handler
        selected_child_tab_id = self.child_notebook.select()
        if selected_child_tab_id:
            selected_child_tab_widget = self.child_notebook.nametowidget(selected_child_tab_id)
            if hasattr(selected_child_tab_widget, '_on_tab_selected'):
                selected_child_tab_widget._on_tab_selected(event)