# display/gui_display.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# Current time is 00:35, so the hash uses 35.
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
# Version 20251222.003501.1

import workers.setup.app_constants as app_constants

# 📚 Python's standard library modules are our trusty sidekicks!
import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import importlib.util
import sys
import pathlib
import traceback # Added for full traceback logging

# --- Module Imports ---
# Import our new utility classes for modularization
from display.utils.window_manager import WindowManager
from display.utils.module_loader import ModuleLoader
from display.utils.layout_parser import LayoutParser

# Import logger and styling utilities
from workers.logger.logger import debug_log
from workers.utils.log_utils import _get_log_args 
from display.styling.style import THEMES, DEFAULT_THEME

# The wrapper functions debug_log and _switch are removed
# as the core debug_log and  now directly handle LOCAL_DEBUG_ENABLE.

class Application(ttk.Frame):
    """
    The main application class that orchestrates the GUI build process.
    It now acts as a lean coordinator, delegating layout parsing and module loading
    to specialized utility classes.
    """
    def __init__(self, parent):
        current_function_name = inspect.currentframe().f_code.co_name
        
        super().__init__(parent)
        self.app_constants = app_constants

        if self.app_constants.LOCAL_DEBUG_ENABLE:
            debug_log( 
                message="🖥️🚦 The grand orchestrator is waking up! Let'S get this GUI built!", **_get_log_args()
            )
        # Initialize utility classes
        # The theme colors are needed by ModuleLoader and WindowManager for certain operations.
        # They are applied first to get the color dictionary.
        self.theme_colors = self._apply_styles(theme_name="DEFAULT_THEME")
        
        # WindowManager likely needs 'self' to manipulate the window
        self.window_manager = WindowManager(self)
        
        # FIX: LayoutParser is stateless and does not accept 'self' (the Application instance)
        self.layout_parser = LayoutParser(current_version=app_constants.current_version, LOCAL_DEBUG_ENABLE=self.app_constants.LOCAL_DEBUG_ENABLE, debug_log_func=debug_log)
        
        self.module_loader = ModuleLoader(self.theme_colors)

        # Initialize storage for notebooks and frames
        self._notebooks = {}
        self._frames_by_path = {}
        self.last_selected_tab_name = None

        try:
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log( 
                    message=f"🔍🔵 Applied theme: {DEFAULT_THEME}. The aesthetic enchantments are complete!",
                    **_get_log_args()
                )
            
            # Start the GUI build process using the root directory of the current file.
            self._build_from_directory(path=pathlib.Path(__file__).parent, parent_widget=self)
            
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log( 
                    message="🔍🔵 The architectural marvel is complete! Finished building GUI from directory structure. Behold!",
                    **_get_log_args()
                )
            
            # After the GUI is built, ensure initial tab selection is processed
            # This is important for notebooks to correctly display their first tab's content.
            self.after_idle(self._trigger_initial_tab_selection)

        except Exception as e:
            if self.app_constants.LOCAL_DEBUG_ENABLE: # Added LOCAL_DEBUG_ENABLE check
                debug_log(
                    message=f"❌ Critical Error during application initialization: {e}. The grand experiment has encountered a catastrophic anomaly!\nFull Traceback:\n{traceback.format_exc()}",
                    **_get_log_args()
                )


    def _trigger_initial_tab_selection(self):
        """
        Triggers the _on_tab_change event for the initially selected tab of each notebook.
        This ensures that the content of the first tab is initialized even if the 
        <<NotebookTabChanged>> event doesn't fire on startup.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message="🔍🔵 Triggering initial tab selection for all notebooks.",
                            **_get_log_args()
                        )        
        notebooks_to_process = list(self._notebooks.items()) # Process notebooks iteratively
        if self.app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"📑🔍 A grand collection! Found {len(notebooks_to_process)} notebooks awaiting their inaugural tab selection ritual.",
                **_get_log_args()
            )
        for notebook_path, notebook_widget in notebooks_to_process:
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"📑🔍 Preparing the stage for notebook at: {notebook_path}.",
                    **_get_log_args()
                )
        try:
                # Create a dummy event object for consistency, mimicking Tkinter's event structure.
                # The event.widget property is particularly important for _on_tab_change.
                dummy_event = type('Event', (object,), {'widget': notebook_widget})()
                
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"📑🔄 Invoking '_on_tab_change' for notebook {notebook_path}. The wheels of fate turn!",
                        **_get_log_args()
                    )
                self._on_tab_change(dummy_event) # Call _on_tab_change
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"📑✅ Operation complete! '_on_tab_change' has returned for notebook {notebook_path}.",
                        **_get_log_args()
                    )

                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log( 
                        message=f"✅ The initial tab selection for notebook at {notebook_path} has been successfully triggered. A perfect start!",
                        **_get_log_args()
                    )           
        except Exception as e:
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Arrr, the code be capsized! Critical error during initial tab selection for notebook {notebook_path}: {e}. A tempest in a teacup!",
                    **_get_log_args()
                )               
        if self.app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="✅ All initial tab selections triggered. The prophecy has been fulfilled!",
                **_get_log_args()
            )


    def _apply_styles(self, theme_name: str):
        """Applies the specified theme to the entire application using ttk.Style."""
        current_function_name = inspect.currentframe().f_code.co_name
        if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message=f"🔍🔵 Applying styles for theme: {theme_name}.",
                            **_get_log_args()
                        )        
        colors = THEMES.get(theme_name, THEMES["dark"]) # Default to dark theme if not found
        style = ttk.Style(self)
        style.theme_use("clam") # Use a theme that allows for more customization
        
        # Configure default widget styles
        style.configure('.',
                        background=colors["bg"],
                        foreground=colors["fg"],
                        font=('Helvetica', 10),
                        padding=colors["padding"],
                        borderwidth=colors["border_width"])

        style.configure('TFrame', background=colors["bg"])

        # Configure Notebook and Tab styles
        style.configure('TNotebook',
                        background=colors["primary"],
                        borderwidth=0)
        
        # Corrected line: Changed 'fg конкурса' to 'fg' and removed the extra parenthesis.
        style.map('TNotebook.Tab',
                  background=[('selected', colors["accent"]), ('!selected', colors["secondary"])],
                  foreground=[('selected', colors["text"]), ('!selected', colors["fg"])]) 

        tab_padding = [colors["padding"] * 10, colors["padding"] * 5]
        style.configure('TNotebook.Tab',
                        padding=tab_padding,
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=0)

        if self.app_constants.LOCAL_DEBUG_ENABLE:
            debug_log( 
                message=f"🔍🔵 Exiting '_apply_styles'. Theme: {theme_name} has been meticulously applied. The canvas is ready!",
                **_get_log_args()
            )       
        return colors


    def _build_from_directory(self, path: pathlib.Path, parent_widget):
        """
        Recursively builds the GUI by parsing directory structure and delegating
        layout creation and module loading to specialized utility classes.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        # Corrected call: Replaced self._log_debug with the imported debug_log function.
        debug_log( 
            message=f"▶️ _build_from_directory for path: '{path}'. Parent widget: {parent_widget}.",
            **_get_log_args()
        )

        # Use the LayoutParser to understand the directory's intended structure
        layout_info = self.layout_parser.parse_directory(path)
        layout_type = layout_info['type']
        layout_data = layout_info['data']

        if self.app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"📊🔍 LayoutParser returned: type='{layout_type}', data='{layout_data}'.",
                **_get_log_args()
            )

        if layout_type == 'error':
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Layout parsing failed for {path}: {layout_data.get('error_message')}. The architectural plans are flawed!",
                    **_get_log_args()
                )
            return # Stop processing this path if there's a layout error

        try:
            if layout_type == 'horizontal_split' or layout_type == 'vertical_split':
                orientation = layout_data['orientation']
                paned_window = ttk.PanedWindow(parent_widget, orient=orientation)
                paned_window.pack(fill=tk.BOTH, expand=True)

                # Sash drag event binding to update tasks, can be used for logging or state updates
                def on_sash_drag(event):
                    # Original code had a debug log here, can be uncommented if needed for debugging
                    # self._log_debug(f"Sash dragged to {paned_window.sashpos(0)}", current_function_name) # This would be a problem if it were self._log_debug
                    self.update_idletasks() # Ensure UI updates after drag
                paned_window.bind("<B1-Motion>", on_sash_drag)

                percentages = layout_data.get('panel_percentages', [])
                for panel_info in layout_data['panels']:
                    sub_dir_path = panel_info['path']
                    weight = panel_info['weight']
                    
                    # Create a frame for each panel within the PanedWindow
                    new_frame = ttk.Frame(paned_window, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                    paned_window.add(new_frame, weight=weight)

                    # Corrected call: Replaced self._log_debug with the imported debug_log function.
                    if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message=f"✅🔨 Constructing a magnificent '{layout_type}' pane for '{panel_info['name']}' with a formidable weight of {weight}.",
                            **_get_log_args()
                        )
                    
                    # Recursively build the content of this panel
                    self._build_from_directory(path=sub_dir_path, parent_widget=new_frame)

                # Configure sash position after children are added and configured
                def configure_sash(event):
                    total_percentage = sum(percentages)
                    if len(percentages) > 1 and total_percentage > 0:
                        # Calculate sash position based on event geometry and total percentage
                        sash_pos = int(event.width * (percentages[0] / total_percentage)) if orientation == tk.HORIZONTAL else int(event.height * (percentages[0] / total_percentage))
                        paned_window.tk.call(paned_window._w, 'sashpos', 0, sash_pos)
                        paned_window.unbind("<Configure>") # Unbind after initial configuration to prevent multiple calls

                paned_window.bind("<Configure>", configure_sash)

            elif layout_type == 'notebook':
                notebook = ttk.Notebook(parent_widget)
                notebook.pack(fill=tk.BOTH, expand=True)
                self._notebooks[path] = notebook # Store notebook instance for later access (e.g., initial tab selection)
                
                # Bind tear-off functionality using the WindowManager
                notebook.bind('<Control-Button-1>', self.window_manager.tear_off_tab)
                notebook.bind('<<NotebookTabChanged>>', self._on_tab_change) # Event for tab switching
                # Corrected call: Replaced self._log_debug with the imported debug_log function.
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log( 
                        message=f"✅🔨 A grand tome takes shape! ttk.Notebook for path '{path}'. Tear-off and tab change events are now bound, ready for dynamic interaction!",
                        **_get_log_args()
                    )
                
                for tab_info in layout_data['tabs']:
                    tab_dir_path = tab_info['path']
                    display_name = tab_info['display_name']
                    
                    # Create a frame for each tab content. This frame will hold the GUI elements for the tab.
                    tab_frame = ttk.Frame(notebook)
                    # Ensure the tab_frame expands to fill the notebook's allocated space
                    tab_frame.grid_rowconfigure(0, weight=1)
                    tab_frame.grid_columnconfigure(0, weight=1)
                    # Place the frame in the notebook area using grid (as per original code)
                    tab_frame.grid(row=0, column=0, sticky="nsew") 
                    
                    self._frames_by_path[tab_dir_path] = tab_frame # Store frame by path for reference
                    
                    notebook.add(tab_frame, text=display_name)
                    # Corrected call: Replaced self._log_debug with the imported debug_log function.
                    if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message=f"📑📑 Behold! Tab '{display_name}' added to the notebook. Another chapter unfolds!",
                            **_get_log_args()
                        )
                    
                    # Recursively build the content of this tab frame
                    self._build_from_directory(path=tab_dir_path, parent_widget=tab_frame)

            elif layout_type == 'monitors': # Special case handling for '2_monitors' from original code structure
                # Corrected call: Replaced self._log_debug with the imported debug_log function.
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log( 
                        message=f"📊🔍 Engaging 'monitors' layout for path: '{path}'. Preparing for visual surveillance!",
                        **_get_log_args()
                    )
                # Configure the parent widget to allow grid expansion for the monitor frames
                parent_widget.grid_rowconfigure(0, weight=1)
                parent_widget.grid_rowconfigure(1, weight=1)
                parent_widget.grid_rowconfigure(2, weight=1)
                parent_widget.grid_columnconfigure(0, weight=1)
                
                # Use ModuleLoader to instantiate GUI components found in the 'gui_*.py' files
                for i, gui_file_path in enumerate(layout_data['gui_files']):
                    frame_instance = self.module_loader.load_and_instantiate_gui(
                        path=gui_file_path, 
                        parent_widget=parent_widget
                        # ModuleLoader automatically passes theme colors and handles finding the class.
                    )
                    if frame_instance:
                        # Grid the instance as done in the original code
                        frame_instance.grid(row=i, column=0, sticky="nsew")
                        # Corrected call: Replaced self._log_debug with the imported debug_log function.
                        if self.app_constants.LOCAL_DEBUG_ENABLE:
                            debug_log(message=f"📊✅ A new viewport! Instantiated and gridded '{frame_instance.__class__.__name__}' from '{gui_file_path.name}'.",**_get_log_args())                    
                    else:
                        if self.app_constants.LOCAL_DEBUG_ENABLE:
                            debug_log(
                                message=f"❌🔴 A creation deferred! Failed to instantiate GUI from {gui_file_path.name}. Back to the drawing board!",
                                **_get_log_args()
                            )

            elif layout_type == 'recursive_build':
                # Handle 'child_' directories: these are treated as modules to load from.
                for child_dir_path in layout_data['child_containers']:
                    # Corrected call: Replaced self._log_debug with the imported debug_log function.
                    if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message=f"🧱🟢 Assembling a miniature world! Building child container directory: '{child_dir_path.name}'.",
                            **_get_log_args()
                        )
                    self.module_loader.load_and_instantiate_gui(
                        path=child_dir_path, 
                        parent_widget=parent_widget
                    )
                
                # Handle GUI files directly within this directory.
                for gui_file_path in layout_data['gui_files']:
                    # Corrected call: Replaced self._log_debug with the imported debug_log function.
                    if self.app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log( 
                            message=f"🧱🟢 Summoning a GUI from: '{gui_file_path.name}'. Let the visual enchantments begin!",
                            **_get_log_args()
                        )
                    instance = self.module_loader.load_and_instantiate_gui(
                        path=gui_file_path, 
                        parent_widget=parent_widget
                    )
                    if instance:
                        instance.pack(fill=tk.BOTH, expand=True)
            
            else: # Fallback for any unhandled directory structures or empty folders.
                # Corrected call: Replaced self._log_debug with the imported debug_log function.
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log( 
                        message=f"🖥️🟡 A puzzle! No specific layout type matched for '{path}'. Initiating a general recursive build.",
                        **_get_log_args()
                    )
                # This part might be redundant if 'recursive_build' covers all cases but is kept as a safety net.
                
                sub_dir = None # Initialize sub_dir to None to prevent 'unbound local variable' errors if the loop doesn't run.

                # Recursively build any subdirectories not explicitly handled as layouts.
                sub_dirs = sorted([d for d in path.iterdir() if d.is_dir()])
                for sub_dir in sub_dirs:
                    # Avoid reprocessing directories already handled by specific layout types
                    dir_prefix = sub_dir.name.split('_')[0]
                    if not (dir_prefix in ['left', 'right', 'top', 'bottom'] or 
                            dir_prefix.isdigit() or 
                            sub_dir.name.startswith("child_")):
                        self._build_from_directory(path=sub_dir, parent_widget=parent_widget)

                # Load any 'gui_*.py' files found directly in this directory.
                py_files = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])
                for py_file in py_files:
                    self.module_loader.load_and_instantiate_gui(path=py_file, parent_widget=parent_widget)

                # Corrected call: Replaced self._log_debug with the imported debug_log function.
                if self.app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log( 
                        message=f"⏹️ The architectural process concludes! '_build_from_directory' for path: '{path}'.",
                        **_get_log_args()
                    )
        except Exception as e:
            if self.app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"❌🔴 Catastrophic structural failure in '_build_from_directory' for {path}: {e}. The foundations are crumbling!",
                    **_get_log_args()
                )



    def print_to_console(self, message: str):
        """
        Placeholder method to print messages to a GUI console.
        This routes all console output through the debug_log system for centralized handling.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🖥️💬 Observer's Log: {message}. What fascinating data has surfaced now?",
                **_get_log_args()
            )

    def _on_tab_change(self, event):
        import workers.setup.app_constants as app_constants # Temporary import for debugging
        """Logs a debug message when a tab is selected or deselected and triggers tab-specific actions."""
        current_function_name = inspect.currentframe().f_code.co_name
        # Corrected call: Replaced self._log_debug with the imported debug_log function.
        debug_log( 
            message=f"▶️ '{current_function_name}' to log a tab change.",
            **_get_log_args()
        )
        
        try:
            notebook = event.widget
            newly_selected_tab_id = notebook.select() # Get the internal ID of the selected tab
            newly_selected_tab_name = notebook.tab(newly_selected_tab_id, "text") # Get the display text of the tab

            # Log tab deselection if there was a previously selected tab
            if self.last_selected_tab_name:
                # Corrected call: Replaced self._log_debug with the imported debug_log function.
                debug_log( 
                    message=f"📘🟡 Tab '{self.last_selected_tab_name}' deselected!",
                    **_get_log_args()
                )

            # Corrected call: Replaced self._log_debug with the imported debug_log function.
            debug_log( 
                message=f"📘🟢 Tab '{newly_selected_tab_name}' selected!",
                **_get_log_args()
            )
            
            self.last_selected_tab_name = newly_selected_tab_name
            
            # Get the actual frame widget associated with the newly selected tab
            selected_tab_frame = notebook.nametowidget(newly_selected_tab_id)
            
            # Find the primary content widget within the tab frame (assuming it's the first child)
            # This allows dynamically loaded tab content to react to tab selection.
            if selected_tab_frame.winfo_children():
                content_widget = selected_tab_frame.winfo_children()[0]
                # Check if the content widget has a method to handle tab selection and call it.
                if hasattr(content_widget, '_on_tab_selected') and callable(getattr(content_widget, '_on_tab_selected')):
                    
                    debug_log( 
                        message=f"Calling _on_tab_selected for {content_widget.__class__.__name__}.",
                        **_get_log_args()
                    )
                    content_widget._on_tab_selected(event) # Pass the event object
                   
            
            # Corrected call: Replaced self._log_debug with the imported debug_log function.
            debug_log( 
                message=f"Tab change logged successfully. New tab: '{newly_selected_tab_name}'.",
                **_get_log_args()
            )
            # Corrected call: Replaced self._log_debug with the imported debug_log function.
            debug_log( 
                message=f"⏹️_on_tab_change().",
                **_get_log_args()
            )

        except Exception as e:
            debug_log(
                message=f"❌ Error in _on_tab_change: {e}",
                **_get_log_args()
            )