# display/gui_display.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251127.000000.1 # REVISION NUMBER INCREASED
# FIXED: Added logic in _build_from_directory to ensure tab frames expand to fill the Notebook,
#        resolving the issue where child frames (like the Matplotlib plot) were not visible.
# FIXED: Added logic to suppress the implicit dependency on PIL/ImageTk during dynamic module loading,
#        resolving the persistent environmental error on application startup.

# 📚 Python's standard library modules are our trusty sidekicks!
import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import importlib.util
import sys
import pathlib

#// --- REQUIRED IMPORTS FOR PLOTTING INTEGRATION (FIX) ---
import numpy as np #// Needed for numerical base
import seaborn as sns# // Preload seaborn context and dependencies
import matplotlib.pyplot as plt #// Preload Matplotlib context
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#// --------------------------------------------------------

# --- Module Imports ---
from workers.worker_active_logging import debug_log, console_log
from workers.worker_mqtt_controller_util import MqttControllerUtility
from display.styling.style import THEMES, DEFAULT_THEME


Local_Debug_Enable = False

# The wrapper functions debug_log_switch and console_log_switch are removed
# as the core debug_log and console_log now directly handle Local_Debug_Enable.

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20251127.000000.1"
# The hash calculation drops the leading zero from the hour (23 -> 23)
current_version_hash = (20251127 * 0 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Constants (Pulled from old global state) ---
CURRENT_DATE = 20251127
CURRENT_TIME = 0
CURRENT_TIME_HASH = 0
REVISION_NUMBER = 1

class Application(tk.Tk):
    """
    The main application class that orchestrates the GUI build process.
    """
    def __init__(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message="🖥️ 🟢 The grand orchestrator is waking up! Let's get this GUI built!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        self._notebooks = {}
        self._frames_by_path = {}
        self._detached_windows = {}
        self.last_selected_tab_name = None

        try:
            # --- CRITICAL FIX: Explicitly disable PIL/ImageTk handling ---
            # This prevents the dynamic loader from failing on systems where the PIL binary link is broken/missing.
            try:
                # This should prevent Tkinter from attempting to load the problematic shared library during startup.
                del sys.modules['PIL.ImageTk']
            except (KeyError, AttributeError):
                pass
            
            super().__init__()
            self.title("OPEN-AIR 2")
            self.geometry("1600x1200")
            self.lift() # Bring window to front
            self.attributes('-topmost', True) # Keep window on top
            self.after_idle(self.attributes, '-topmost', False) # Release topmost after idle
            debug_log(
                message="🔍🔵 Tkinter main window created with title 'OPEN-AIR 2' and geometry '1600x1200'. Forced to foreground.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            self.theme_colors = self._apply_styles(theme_name="DEFAULT_THEME")
            debug_log(
                message=f"🔍🔵 Applied theme: {DEFAULT_THEME}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

            self.mqtt_util = MqttControllerUtility(print_to_gui_func=console_log, log_treeview_func=lambda *args: None)
            self.mqtt_util.connect_mqtt()

            self._build_from_directory(path=pathlib.Path(__file__).parent, parent_widget=self)
            debug_log(
                message="🔍🔵 Finished building GUI from directory structure.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _apply_styles(self, theme_name: str):
        """Applies the specified theme to the entire application using ttk.Style."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🔍🔵 Applying styles for theme: {theme_name}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        colors = THEMES.get(theme_name, THEMES["dark"])
        style = ttk.Style(self)
        style.theme_use("clam")
        
        style.configure('.',
                        background=colors["bg"],
                        foreground=colors["fg"],
                        font=('Helvetica', 10),
                        padding=colors["padding"],
                        borderwidth=colors["border_width"])

        style.configure('TFrame', background=colors["bg"])

        style.configure('TNotebook',
                        background=colors["primary"],
                        borderwidth=0)
        
        style.map('TNotebook.Tab',
                  background=[('selected', colors["accent"]), ('!selected', colors["secondary"])],
                  foreground=[('selected', colors["text"]), ('!selected', colors["fg"])])

        tab_padding = [colors["padding"] * 10, colors["padding"] * 5]
        style.configure('TNotebook.Tab',
                        padding=tab_padding,
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=0)

        self.configure(background=colors["bg"])
        debug_log(
            message=f"🔍🔵 Styles applied. Root window background set to {colors['bg']}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        return colors


    def _build_from_directory(self, path: pathlib.Path, parent_widget):
        """Recursively builds the GUI based on folder structure."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🔍🔵 Entering _build_from_directory for path: '{path}'. Parent widget: {parent_widget}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            sub_dirs = sorted([d for d in path.iterdir() if d.is_dir()])
            debug_log(
                message=f"🔍🔵 Found sub_dirs in '{path}': {[d.name for d in sub_dirs]}.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
  
            layout_dirs = [d for d in sub_dirs if d.name.split('_')[0] in ['left', 'right', 'top', 'bottom']]
            
            if layout_dirs:
                debug_log(
                    message=f"🔍🔵 Found layout_dirs in '{path}': {[d.name for d in layout_dirs]}. Applying layout logic.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                is_horizontal = any(d.name.startswith('left_') or d.name.startswith('right_') for d in layout_dirs)
                is_vertical = any(d.name.startswith('top_') or d.name.startswith('bottom_') for d in layout_dirs)

                if is_horizontal and is_vertical:
                    console_log(f"❌ Layout Error: Cannot mix horizontal and vertical layouts in '{path}'.")
                    debug_log(
                        message=f"❌🔴 Layout Error: Mixed horizontal and vertical layouts detected in '{path}'.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                    return

                sort_order = ['left', 'top', 'right', 'bottom']
                sorted_layout_dirs = sorted(layout_dirs, key=lambda d: sort_order.index(d.name.split('_')[0]))
                
                if is_horizontal:
                    current_relx = 0.0
                    for sub_dir in sorted_layout_dirs:
                        if sub_dir.name.split('_')[0] not in ['left', 'right']: continue
                        try:
                            percentage = int(sub_dir.name.split('_')[1])
                            rel_width = percentage / 100.0
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            new_frame.place(relx=current_relx, rely=0, relwidth=rel_width, relheight=1.0)
                            debug_log(
                                message=f"🔍🔵 Created horizontal frame for '{sub_dir.name}' placed at relx={current_relx}, relwidth={rel_width}.",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            current_relx += rel_width
                        except (IndexError, ValueError) as e:
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'. Error: {e}")
                            debug_log(
                                message=f"⚠️ Warning: Layout parsing failed for '{sub_dir.name}'. Error: {e}",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                
                elif is_vertical:
                    current_rely = 0.0
                    for sub_dir in sorted_layout_dirs:
                        if sub_dir.name.split('_')[0] not in ['top', 'bottom']: continue
                        try:
                            percentage = int(sub_dir.name.split('_')[1])
                            rel_height = percentage / 100.0
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            new_frame.place(relx=0, rely=current_rely, relwidth=1.0, relheight=rel_height)
                            debug_log(
                                message=f"🔍🔵 Created vertical frame for '{sub_dir.name}' placed at rely={current_rely}, relheight={rel_height}.",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            current_rely += rel_height
                        except (IndexError, ValueError) as e:
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'. Error: {e}")
                            debug_log(
                                message=f"⚠️ Warning: Layout parsing failed for '{sub_dir.name}'. Error: {e}",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                return

            is_tab_container = any(d.name.startswith("tab_") or d.name.startswith("sub_tab_") for d in sub_dirs)
 
            if is_tab_container:
                debug_log(
                    message=f"🔍🔵 Found tab container directories in '{path}'. Creating ttk.Notebook.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                notebook = ttk.Notebook(parent_widget)
                notebook.pack(fill=tk.BOTH, expand=True)
                debug_log(
                    message="🔍🔵 ttk.Notebook packed (fill=BOTH, expand=True).",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                
                notebook.bind('<Control-Button-1>', self._tear_off_tab)
                notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)
                
                tab_dirs = [d for d in sub_dirs if d.name.startswith("tab_") or d.name.startswith("sub_tab_")]
                for tab_dir in tab_dirs:
                    tab_frame = ttk.Frame(notebook)
                    
                    # FIX ADDED HERE: Ensure the tab_frame expands to fill the space allocated by the notebook.
                    # This prevents child frames (like the plot) from collapsing.
                    tab_frame.grid_rowconfigure(0, weight=1)
                    tab_frame.grid_columnconfigure(0, weight=1)
                    tab_frame.grid(row=0, column=0, sticky="nsew") # Place the frame in the notebook area
                    debug_log(
                        message=f"🔍🔵 Created tab frame for '{tab_dir.name}'. Grid configured and placed.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                    
                    self._frames_by_path[tab_dir] = tab_frame
                    
                    parts = tab_dir.name.split('_')
                    start_index = next((i for i, part in enumerate(parts) if part.isdigit()), -1)
                    display_name = " ".join(parts[start_index + 1:]).title() if start_index != -1 else tab_dir.name
                    notebook.add(tab_frame, text=display_name)
                    debug_log(
                        message=f"🔍🔵 Added tab '{display_name}' to notebook.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                    
                    # The recursive call will place the contents (like ScanViewGUIFrame) inside the tab_frame
                    self._build_from_directory(path=tab_dir, parent_widget=tab_frame)

            if "tab_2_monitors" in str(path):
                debug_log(
                    message=f"🔍🔵 Special handling for 'tab_2_monitors' in path: '{path}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                py_files = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])
                parent_widget.grid_rowconfigure(0, weight=1)
                parent_widget.grid_rowconfigure(1, weight=1)
                parent_widget.grid_rowconfigure(2, weight=1)
                parent_widget.grid_columnconfigure(0, weight=1)
                
                for i, py_file in enumerate(py_files):
                    module_name = py_file.stem
                    debug_log(
                        message=f"🔍🔵 Dynamically importing module '{module_name}' for monitor frame.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, (ttk.Frame, tk.Frame)) and obj.__module__ == module.__name__:
                            try:
                                config = {"theme_colors": self.theme_colors}
                                frame_instance = obj(parent_widget, mqtt_util=self.mqtt_util, config=config)
                                frame_instance.grid(row=i, column=0, sticky="nsew")
                                debug_log(
                                    message=f"🔍🔵 Instantiated and gridded '{name}' from '{py_file.name}'.",
                                    file=current_file,
                                    version=current_version,
                                    function=f"{self.__class__.__name__}.{current_function_name}",
                                    console_print_func=console_log
                                )
                            except Exception as e:
                                console_log(f"❌ Failed to instantiate '{name}' from '{py_file.name}': {e}")
                                debug_log(
                                    message=f"❌🔴 Error instantiating '{name}' from '{py_file.name}': {e}",
                                    file=current_file,
                                    version=current_version,
                                    function=f"{self.__class__.__name__}.{current_function_name}",
                                    console_print_func=console_log
                                )
                return
            else:
                debug_log(
                    message=f"🔍🔵 Applying general build logic for path: '{path}'.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                for sub_dir in sub_dirs:
                    if sub_dir.name.startswith("child_"):
                        debug_log(
                            message=f"🔍🔵 Building child container for subdirectory: '{sub_dir.name}'.",
                            file=current_file,
                            version=current_version,
                            function=f"{self.__class__.__name__}.{current_function_name}",
                            console_print_func=console_log
                        )
                        self._build_child_container(path=sub_dir, parent_widget=parent_widget)

                py_files = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])
                for py_file in py_files:
                    debug_log(
                        message=f"🔍🔵 Building child container for Python file: '{py_file.name}'.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )
                    self._build_child_container(path=py_file, parent_widget=parent_widget)

        except Exception as e:
            console_log(f"❌ Error in {current_function_name} for path {path}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


            
    def _build_child_container(self, path: pathlib.Path, parent_widget):
        """Dynamically imports and instantiates a GUI component from a Python file."""
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            if path.is_dir():
                gui_file = next(f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py')
            else:
                gui_file = path

            module_name = gui_file.stem
            
            debug_log(
                message=f"🔍🔵 Preparing to dynamically import module: '{module_name}' from path: '{gui_file}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
           
            spec = importlib.util.spec_from_file_location(module_name, gui_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # --- START FIXED, ROBUST INSTANTIATION LOGIC ---
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, (ttk.Frame, tk.Frame)) and obj.__module__ == module.__name__:
                    debug_log(
                        message=f"🔍🔵 Found a valid GUI class: '{name}'. Attempting safe instantiation.",
                        file=current_file,
                        version=current_version,
                        function=f"{self.__class__.__name__}.{current_function_name}",
                        console_print_func=console_log
                    )

                    frame_instance = None
                    try:
                        # Special handling for DynamicGuiBuilder
                        if name == "DynamicGuiBuilder" and hasattr(module, "MQTT_TOPIC_FILTER"):
                            config = {
                                "base_topic": module.MQTT_TOPIC_FILTER,
                                "log_to_gui_console": console_log,
                                "log_to_gui_treeview": None,
                                "theme_colors": self.theme_colors
                            }
                            frame_instance = obj(parent_widget, mqtt_util=self.mqtt_util, config=config)
                        else:
                            # General handling for other components
                            config = {"theme_colors": self.theme_colors}
                            try:
                                # 1. Attempt with config
                                frame_instance = obj(parent_widget, mqtt_util=self.mqtt_util, config=config)
                            except TypeError:
                                try:
                                    # 2. Fallback to standard
                                    frame_instance = obj(parent_widget, mqtt_util=self.mqtt_util)
                                except TypeError:
                                    # 3. Fallback to minimal
                                    frame_instance = obj(parent_widget)

                        # If instantiation was successful
                        if frame_instance:
                            frame_instance.pack(fill=tk.BOTH, expand=True)
                            debug_log(
                                message=f"🔍🔵 Successfully instantiated and packed '{name}'.",
                                file=current_file,
                                version=current_version,
                                function=f"{self.__class__.__name__}.{current_function_name}",
                                console_print_func=console_log
                            )
                            return
                        else:
                            raise RuntimeError(f"Instantiation failed for class '{name}'.")

                    except Exception as e:
                        console_log(f"❌ Failed to instantiate '{name}' from '{gui_file.name}': {e}")
                        debug_log(
                            message=f"❌🔴 Silent Crash Avoided: Instantiation of '{name}' failed. The error be: {e}",
                            file=current_file,
                            version=current_version,
                            function=f"{self.__class__.__name__}.{current_function_name}",
                            console_print_func=console_log
                        )
                        # Display an error message frame instead of leaving a blank spot
                        error_frame = ttk.Frame(parent_widget)
                        error_frame.pack(fill=tk.BOTH, expand=True)
                        ttk.Label(error_frame, text=f"ERROR LOADING: {gui_file.name}", foreground="red").pack(pady=10)
                        debug_log(
                            message=f"🔍🔵 Displayed error frame for '{gui_file.name}'.",
                            file=current_file,
                            version=current_version,
                            function=f"{self.__class__.__name__}.{current_function_name}",
                            console_print_func=console_log
                        )
                        return

            # If we iterate all members and find no class
            raise AttributeError(f"Module '{module_name}' needs a class that inherits from 'ttk.Frame' or 'tk.Frame'.")
            # --- END FIXED, ROBUST INSTANTIATION LOGIC ---

        except Exception as e:
            console_log(f"❌ Error importing or executing module at {path}: {e}")
            debug_log(
                message=f"❌🔴 Fatal error during dynamic load: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def _tear_off_tab(self, event):
        """Tears a tab off of its Notebook and places it into a new Toplevel window."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🔍🔵 Attempting to tear off tab from event: {event}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            notebook = event.widget
            tab_id = notebook.identify(event.x, event.y)
            if not tab_id:
                debug_log(
                    message="⚠️ No tab identified at click location.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                return 
            frame_id = notebook.tab(tab_id, "id")
            tab_title = notebook.tab(tab_id, "text")
            
            if frame_id in self._detached_windows:
                console_log(f"⚠️ Tab '{tab_title}' is already in a detached window.")
                debug_log(
                    message=f"⚠️ Tab '{tab_title}' is already detached.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                return

            new_window = tk.Toplevel(self)
            new_window.title(tab_title)
            debug_log(
                message=f"🔍🔵 Created new Toplevel window for detached tab '{tab_title}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            notebook.hide(tab_id)
            frame_id.pack(in_=new_window, fill=tk.BOTH, expand=True)
            debug_log(
                message=f"🔍🔵 Hid original tab and packed frame into new window.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            self._detached_windows[frame_id] = {
                "window": new_window,
                "notebook": notebook,
                "tab_title": tab_title
            }
            
            new_window.protocol("WM_DELETE_WINDOW", lambda: self._re_attach_tab(frame_id))

            console_log(f"✅ Celebration of success! Tab '{tab_title}' has been detached and is now a new window.")
            debug_log(
                message=f"✅ Tab '{tab_title}' successfully detached.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

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
        """Re-attaches a detached frame back to its original Notebook."""
        current_function_name = inspect.currentframe().f_code.co_name
        debug_log(
            message=f"🔍🔵 Attempting to re-attach tab for frame: {frame}.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
  
        try:
            if frame not in self._detached_windows:
                debug_log(
                    message=f"⚠️ Frame {frame} not found in detached windows.",
                    file=current_file,
                    version=current_version,
                    function=f"{self.__class__.__name__}.{current_function_name}",
                    console_print_func=console_log
                )
                return
            state = self._detached_windows[frame]
            notebook = state["notebook"]
            tab_title = state["tab_title"]
            window = state["window"]
            
            frame.pack_forget()
            frame.pack(in_=notebook, fill=tk.BOTH, expand=True)
            
            notebook.add(frame, text=tab_title)
            debug_log(
                message=f"🔍🔵 Re-packed frame into notebook and re-added tab '{tab_title}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
        
            del self._detached_windows[frame]
            window.destroy()
            debug_log(
                message=f"🔍🔵 Destroyed detached window for '{tab_title}'.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            console_log(f"✅ Celebration of success! Tab '{tab_title}' has been re-attached.")
            debug_log(
                message=f"✅ Tab '{tab_title}' successfully re-attached.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

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
        """Logs a debug message when a tab is selected or deselected."""
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
            debug_log(
                message="✅ Tab change logged successfully.",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )