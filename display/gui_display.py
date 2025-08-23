# display/gui_display.py
#
# A script that dynamically builds the application's Tkinter GUI based on the
# predefined directory structure. It acts as the "orchestrator," recursively
# traversing a folder hierarchy to construct the user interface, now with
# support for "tear-off" tabs that can become their own windows.
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
# Version 20250822.230500.2

# 📚 Python's standard library modules are our trusty sidekicks!
# os: Provides a way to interact with the operating system, like getting file names.
import os
# inspect: Allows us to "look inside" live objects, which is crucial for dynamic introspection.
import inspect
# datetime: Handles dates and times, used here for our versioning system.
import datetime
# tkinter: The foundational GUI toolkit for Python.
import tkinter as tk
# ttk: The "themed Tkinter" module, providing a more modern, stylable set of widgets.
from tkinter import ttk
# importlib.util: A powerful module for dynamic, programmatic importing of Python files.
import importlib.util
# sys: Provides access to system-specific parameters and functions, including the module search path.
import sys
# pathlib: A modern, object-oriented way to handle filesystem paths, making our code cleaner and more robust.
import pathlib

# --- Module Imports ---
# We no longer need to add the parent directory to the path as this is handled in main.py
from display.styling.style import THEMES, DEFAULT_THEME
from datasets.logging import debug_log, console_log
from workers.mqtt_controller_util import MqttControllerUtility


# --- Global Scope Variables ---
# ⏰ As requested, the version is now hardcoded to the time this file was generated.
# The version strings and numbers below are static and will not change at runtime.
# This represents the date (YYYYMMDD) of file creation.
CURRENT_DATE = 20250822
# This represents the time (HHMMSS) of file creation.
CURRENT_TIME = 230500
# This is a numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 230500
# Our project's current revision number, which is manually incremented.
REVISION_NUMBER = 2
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250822.230500.2"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs, ensuring it's always accurate.
current_file = f"{os.path.basename(__file__)}"


class Application(tk.Tk):
    """
    The main application class that orchestrates the GUI build process.
    
    This class inherits from `tk.Tk`, making it the root of our application's GUI.
    It's responsible for setting up the main window and kicking off the dynamic
    GUI construction based on the folder structure. It now manages the state
    of detached tabs.
    """
    def __init__(self):
        """
        The constructor for our main application.
        
        It sets up the main window, applies styling, and starts the recursive
        process of building the GUI. It's the first function called upon app launch.
        """
        # We grab the name of the current function for our debug logs.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🚀 A celebratory log message to mark the start of our journey!
        debug_log(
            message="🖥️ 🟢 The grand orchestrator is waking up! Let's get this GUI built!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        # --- NEW: State management dictionaries for tear-off tabs ---
        # We need a way to track which frames belong to which notebooks.
        self._notebooks = {}
        self._frames_by_path = {}
        self._detached_windows = {}
        # We'll store the name of the last selected tab for logging purposes.
        self.last_selected_tab_name = None

        try:
            # We must first call the parent class's constructor to initialize the Tkinter window.
            super().__init__()
            # Setting the title of our application window, which appears in the title bar.
            self.title("OPEN-AIR 2")
            # Defining the initial size of the window in pixels.
            self.geometry("1000x700")

            # --- NEW: Apply the selected theme ---
            # We call a helper method to apply our chosen theme and store the color palette.
            self.theme_colors = self._apply_styles(theme_name=DEFAULT_THEME)

            # --- NEW: Initialize a single MQTT utility instance here (Orchestration Layer) ---
            self.mqtt_util = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
            self.mqtt_util.connect_mqtt()

            # 🏗️ Let the dynamic building begin! We call our recursive builder function,
            # starting from the directory where this script resides.
            self._build_from_directory(path=pathlib.Path(__file__).parent, parent_widget=self)
            
            # 🎉 A final cheer for a job well done!
            console_log("✅ Celebration of success! The application's core has been built.")

        except Exception as e:
            # 🆘 Oh no, an error! We catch it here to prevent the app from crashing.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # We log the detailed error message for easier debugging.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the entire application using ttk.Style.
        
        This method configures the look and feel of various `ttk` widgets based on
        the color and style information loaded from our `style` module.
        
        Args:
            theme_name (str): The name of the theme to apply.
            
        Returns:
            dict: The dictionary of colors from the applied theme.
        """
        # We grab the colors from our theme dictionary, defaulting to 'dark' if the theme isn't found.
        colors = THEMES.get(theme_name, THEMES["dark"])
        
        style = ttk.Style(self)
        style.theme_use("clam")

        # --- Configure widget styles ---
        # We configure the default style for all widgets ('.').
        # UPDATED: We use values from our theme for padding and borderwidth, making our styles consistent.
        style.configure('.',
                        background=colors["bg"],
                        foreground=colors["fg"],
                        font=('Helvetica', 10),
                        padding=colors["padding"],
                        borderwidth=colors["border_width"])

        # Specific configurations for `TFrame` widgets.
        style.configure('TFrame',
                        background=colors["bg"])

        # Specific configurations for `TNotebook` widgets (the container for our tabs).
        style.configure('TNotebook',
                        background=colors["primary"],
                        borderwidth=0)
        
        # This is a 'map' configuration, which defines how a widget's style changes
        # based on its state (e.g., 'selected' or not).
        style.map('TNotebook.Tab',
                  background=[('selected', colors["accent"]), ('!selected', colors["secondary"])],
                  foreground=[('selected', colors["text"]), ('!selected', colors["fg"])])

        # UPDATED: Applying padding from the theme to notebook tabs.
        # We calculate the tab padding based on our base padding value from the theme.
        tab_padding = [colors["padding"] * 10, colors["padding"] * 5]
        style.configure('TNotebook.Tab',
                        padding=tab_padding,
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=0)

        # UPDATED: Applying padding and border_width from the theme to buttons.
        # We make the buttons' padding and border more prominent.
        style.configure('TButton',
                        background=colors["accent"],
                        foreground=colors["text"],
                        padding=colors["padding"] * 5,
                        relief=colors["relief"],
                        borderwidth=colors["border_width"] * 2)
        
        style.map('TButton',
                  background=[('active', colors["secondary"])])

        # --- Configure the main window background ---
        # We apply the main background color to the root window itself.
        self.configure(background=colors["bg"])
        
        # We return the color dictionary so other methods can access the theme's colors.
        return colors


    def _build_from_directory(self, path: pathlib.Path, parent_widget):
        """
        Recursively builds the GUI based on folder structure, supporting percentage-based layouts.
        
        This is the heart of the dynamic builder. It inspects a directory and decides
        what kind of Tkinter widget to create based on the folder naming convention.
        
        Args:
            path (pathlib.Path): The path to the current directory being processed.
            parent_widget: The Tkinter widget that will be the parent for new widgets.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # We first get all the subdirectories and sort them for a consistent build order.
            sub_dirs = sorted([d for d in path.iterdir() if d.is_dir()])
            
            # We identify directories that define a layout (e.g., 'left_50', 'top_30').
            layout_dirs = [d for d in sub_dirs if d.name.split('_')[0] in ['left', 'right', 'top', 'bottom']]
            
            # If we find layout directories, we process them first. This is a top-down approach.
            if layout_dirs:
                # We check if the layout is horizontal or vertical.
                is_horizontal = any(d.name.startswith('left_') or d.name.startswith('right_') for d in layout_dirs)
                is_vertical = any(d.name.startswith('top_') or d.name.startswith('bottom_') for d in layout_dirs)

                # We log an error if a developer tries to mix horizontal and vertical layouts.
                if is_horizontal and is_vertical:
                    console_log(f"❌ Layout Error: Cannot mix horizontal and vertical layouts in '{path}'.")
                    return

                # We define a strict sort order to ensure 'left' is before 'right', 'top' before 'bottom', etc.
                sort_order = ['left', 'top', 'right', 'bottom']
                # We sort the layout directories according to our defined order.
                sorted_layout_dirs = sorted(layout_dirs, key=lambda d: sort_order.index(d.name.split('_')[0]))
                
                # --- Horizontal Layout Processing ---
                if is_horizontal:
                    # We keep track of the current horizontal position (relx).
                    current_relx = 0.0
                    for sub_dir in sorted_layout_dirs:
                        # We only process 'left' and 'right' directories in this block.
                        if sub_dir.name.split('_')[0] not in ['left', 'right']: continue
                        try:
                            # We parse the percentage from the folder name (e.g., 'left_50' gives us 50).
                            percentage = int(sub_dir.name.split('_')[1])
                            # We convert the percentage to a relative width.
                            rel_width = percentage / 100.0
                            # We create a new `ttk.Frame`, which is stylable.
                            # UPDATED: We use the theme's border and relief settings.
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            # We use `.place()` to position the frame with relative coordinates and size.
                            new_frame.place(relx=current_relx, rely=0, relwidth=rel_width, relheight=1.0)
                            # 🔄 We recursively call this function to build the contents of the new frame.
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            # We update the horizontal position for the next frame.
                            current_relx += rel_width
                        except (IndexError, ValueError):
                            # A helpful warning if the folder name is not formatted correctly.
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'.")
                
                # --- Vertical Layout Processing ---
                elif is_vertical:
                    # We keep track of the current vertical position (rely).
                    current_rely = 0.0
                    for sub_dir in sorted_layout_dirs:
                        # We only process 'top' and 'bottom' directories in this block.
                        if sub_dir.name.split('_')[0] not in ['top', 'bottom']: continue
                        try:
                            # We parse the percentage from the folder name.
                            percentage = int(sub_dir.name.split('_')[1])
                            # We convert the percentage to a relative height.
                            rel_height = percentage / 100.0
                            # We create a new `ttk.Frame`.
                            # UPDATED: We use the theme's border and relief settings.
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            # We use `.place()` to position the frame with relative coordinates and size.
                            new_frame.place(relx=0, rely=current_rely, relwidth=1.0, relheight=rel_height)
                            # 🔄 We recursively call this function to build the contents of the new frame.
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            # We update the vertical position for the next frame.
                            current_rely += rel_height
                        except (IndexError, ValueError):
                            # A helpful warning if the folder name is not formatted correctly.
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'.")
                # If we've processed a layout, we stop here.
                return

            # We check for directories that are meant to be a tab container.
            is_tab_container = any(d.name.startswith("tab_") or d.name.startswith("sub_tab_") for d in sub_dirs)
            if is_tab_container:
                # If it's a tab container, we create a `ttk.Notebook` widget.
                notebook = ttk.Notebook(parent_widget)
                # We use `.pack()` to make the notebook fill the entire parent widget.
                notebook.pack(fill=tk.BOTH, expand=True)
                
                # --- NEW: We register this notebook for tear-off functionality.
                notebook.bind('<Control-Button-1>', self._tear_off_tab)
                # 🛠️ We bind a new event to handle tab change logging.
                notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)
                
                tab_dirs = [d for d in sub_dirs if d.name.startswith("tab_") or d.name.startswith("sub_tab_")]
                for tab_dir in tab_dirs:
                    # We create a new frame for each tab's content.
                    tab_frame = ttk.Frame(notebook)
                    
                    # --- NEW: We store a reference to this frame.
                    self._frames_by_path[tab_dir] = tab_frame
                    
                    # We parse the folder name to create a user-friendly display name for the tab.
                    # e.g., 'tab_1_main_page' becomes 'Main Page'.
                    parts = tab_dir.name.split('_')
                    start_index = next((i for i, part in enumerate(parts) if part.isdigit()), -1)
                    display_name = " ".join(parts[start_index + 1:]).title() if start_index != -1 else tab_dir.name
                    # We add the new frame as a tab to the notebook.
                    notebook.add(tab_frame, text=display_name)
                    # 🔄 We recursively build the contents of this new tab.
                    self._build_from_directory(path=tab_dir, parent_widget=tab_frame)
                # If we've processed tabs, we stop here.
                return

            # If no layout or tab directories were found, we look for child components.
            for sub_dir in sub_dirs:
                # We identify directories that contain a child component (e.g., 'child_1_button_panel').
                if sub_dir.name.startswith("child_"):
                    self._build_child_container(path=sub_dir, parent_widget=parent_widget)

            # We also look for direct Python files that define GUI components (e.g., 'gui_1_button_panel.py').
            py_files = [f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py']
            for py_file in py_files:
                self._build_child_container(path=py_file, parent_widget=parent_widget)

        except Exception as e:
            # Another safety net for errors during the recursive build process.
            console_log(f"❌ Error in {current_function_name} for path {path}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _build_child_container(self, path: pathlib.Path, parent_widget):
        """
        Dynamically imports and instantiates a GUI component from a Python file.
        
        This method is responsible for finding a Python file that defines a GUI component,
        importing it into memory, and then creating an instance of the component to
        add to the application's GUI hierarchy.
        
        Args:
            path (pathlib.Path): The path to the directory or file containing the component.
            parent_widget: The Tkinter widget that will be the parent for the new component.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # We determine if the path is a directory or a direct file.
            if path.is_dir():
                # If it's a directory, we search for the 'gui_*.py' file inside it.
                gui_file = next(f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py')
            else:
                # If it's a file, we use the path directly.
                gui_file = path

            # 🪄 This is the magical part where we dynamically import the module.
            # We get the name of the module from the file's stem (e.g., 'gui_1_button_panel').
            module_name = gui_file.stem
            # We create a 'spec' which tells Python how to load our module.
            spec = importlib.util.spec_from_file_location(module_name, gui_file)
            # We create the module object from the spec.
            module = importlib.util.module_from_spec(spec)
            # We add our new module to the system's modules dictionary to make it accessible.
            sys.modules[module_name] = module
            # We execute the module, which runs its code and defines its functions and classes.
            spec.loader.exec_module(module)

            # --- 🎯 REFACTORED: The "hardcoded part" you wanted to change! ---
            # We now iterate through all members (classes, functions, etc.) of the imported module.
            for name, obj in inspect.getmembers(module):
                # First, we check if the member is a class.
                if inspect.isclass(obj):
                    # We check if this class is a subclass of `ttk.Frame`.
                    # This is much more flexible than hardcoding a specific class name like "GUIFrame"!
                    if issubclass(obj, ttk.Frame):
                        # If we find a matching class, we instantiate it with the `parent_widget`.
                        # We pass the shared mqtt_util instance here!
                        frame_instance = obj(parent_widget, mqtt_util=self.mqtt_util)
                        # We pack the new frame to make it visible and fill its parent.
                        frame_instance.pack(fill=tk.BOTH, expand=True)
                        # We've found our class and built the frame, so we can break the loop and return.
                        return

                # We also check for functions that build the GUI.
                # This provides backward compatibility with the old naming convention.
                elif inspect.isfunction(obj):
                    # We check if the function's name matches our known component-building function.
                    if name == "create_yo_button_frame":
                        obj(parent_widget)
                        return # We've found and run the function, so we're done here.
            # 🚨 If we get here, it means we couldn't find a valid class or function in the imported module.
            raise AttributeError(f"Module '{module_name}' needs a class that inherits from 'ttk.Frame' or a 'create_yo_button_frame' function.")

        except Exception as e:
            # A final safety net for any errors during the import or execution of a child component.
            console_log(f"❌ Error importing or executing module at {path}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _tear_off_tab(self, event):
        """
        Tears a tab off of its Notebook and places it into a new Toplevel window.
        
        This method is triggered by a <Control-Button-1> event on a tab.
        It moves the selected tab's frame from the Notebook to its own new window.
        
        Args:
            event: The Tkinter event object.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            # We determine which notebook widget was clicked.
            notebook = event.widget
            # We use the event coordinates to find the tab that was clicked.
            tab_id = notebook.identify(event.x, event.y)
            if not tab_id:
                return # No tab was clicked, so we do nothing.
            # 🎯 FIX: We need to use the `id` of the widget, not its text label.
            # This is the unique internal identifier for the tab's content frame.
            frame_id = notebook.tab(tab_id, "id")
            
            # We get the title of the tab to use for the new window.
            tab_title = notebook.tab(tab_id, "text")
            
            # If the frame is already detached, we do nothing.
            if frame_id in self._detached_windows:
                console_log(f"⚠️ Tab '{tab_title}' is already in a detached window.")
                return

            # We create a new top-level window.
            new_window = tk.Toplevel(self)
            new_window.title(tab_title)
            
            # We move the frame from the notebook to the new window.
            notebook.hide(tab_id)
            frame_id.pack(in_=new_window, fill=tk.BOTH, expand=True)
            
            # We store a reference to the detached window.
            self._detached_windows[frame_id] = {
                "window": new_window,
                "notebook": notebook,
                "tab_title": tab_title
            }
            
            # We bind the new window's close button to our re-attachment function.
            new_window.protocol("WM_DELETE_WINDOW", lambda: self._re_attach_tab(frame_id))

            console_log(f"✅ Celebration of success! Tab '{tab_title}' has been detached and is now a new window.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _re_attach_tab(self, frame):
        """
        Re-attaches a detached frame back to its original Notebook.
        
        This method is called when the user closes the detached Toplevel window.
        It moves the frame back to its original notebook and destroys the window.
        
        Args:
            frame: The Tkinter frame object that was detached.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            if frame not in self._detached_windows:
                return # Frame is not detached, so we do nothing.
            # We retrieve the notebook and title from our state dictionary.
            state = self._detached_windows[frame]
            notebook = state["notebook"]
            tab_title = state["tab_title"]
            window = state["window"]
            
            # We re-parent the frame back to its original notebook.
            frame.pack_forget()
            frame.pack(in_=notebook, fill=tk.BOTH, expand=True)
            
            # We add the tab back to the notebook at the same position.
            notebook.add(frame, text=tab_title)
            
            # We clean up our state dictionary and destroy the Toplevel window.
            del self._detached_windows[frame]
            window.destroy()
            
            console_log(f"✅ Celebration of success! Tab '{tab_title}' has been re-attached.")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
    def _on_tab_change(self, event):
        """
        Logs a debug message when a tab is selected or deselected.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🔍🔵 Entering '{current_function_name}' to log a tab change.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        try:
            notebook = event.widget
            newly_selected_tab_id = notebook.select()
            newly_selected_tab_name = notebook.tab(newly_selected_tab_id, "text")

            if self.last_selected_tab_name:
                debug_log(
                    message=f"📘🔴 Tab '{self.last_selected_tab_name}' deselected!",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )

            debug_log(
                message=f"📘🟢 Tab '{newly_selected_tab_name}' selected!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            self.last_selected_tab_name = newly_selected_tab_name
            
            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


# 🏃 This is the standard entry point for a Python script.
# The code inside this block only runs when the script is executed directly.
if __name__ == "__main__":
    # A friendly message to signal the start of the application.
    console_log("--- Initializing the Dynamic GUI Builder ---")
    
    # We create an instance of our main Application class.
    app = Application()
    # This call starts the Tkinter event loop, which handles all user interactions and keeps the window open.
    app.mainloop()
    # Once the mainloop exits (e.g., the user closes the window), this message is printed.
    console_log("--- Application closed. ---")