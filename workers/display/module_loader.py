# display/utils/module_loader.py

import os
import inspect
import sys
import importlib.util
import pathlib
from tkinter import ttk, Frame
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.logger.logger import debug_log # Import the global debug_log
from workers.utils.log_utils import _get_log_args

# Attempt to import PIL/ImageTk, setting a flag if successful.
# This addresses the "Critical Fix" for suppressing PIL/ImageTk errors.
try:
    from PIL import ImageTk, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # Define dummy classes if PIL is not available to avoid NameErrors
    # if they are expected in some contexts.
    class ImageTk: pass
    class Image: pass

class ModuleLoader:
    """
    Handles dynamic loading of Python modules and instantiation of GUI classes.
    Includes logic for suppressing common import errors like PIL/ImageTk.
    """
    def __init__(self, theme_colors, state_mirror_engine=None, subscriber_router=None):
        self.theme_colors = theme_colors
        self.state_mirror_engine = state_mirror_engine
        self.subscriber_router = subscriber_router

    def _load_module(self, module_path: pathlib.Path, module_name: str):
        """
        Dynamically loads a Python module from a given path.
        Returns the module object. Handles potential import errors.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬🟢 Preparing to awaken a module! Loading from '{module_path}' with name '{module_name}'.",
                **_get_log_args()
            )
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            if spec is None:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🔴 Catastrophic failure! Could not forge a module spec for '{module_path}'. Aborting mission!",
                        **_get_log_args()
                    )
                return None
                
            module = importlib.util.module_from_spec(spec)
            
            # Add module to sys.modules to ensure it's discoverable by other imports.
            if module_name in sys.modules:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🟡 Temporal anomaly detected! Module '{module_name}' already exists. Overwriting with extreme prejudice (and a warning!).",
                        **_get_log_args()
                    )
            sys.modules[module_name] = module
            
            spec.loader.exec_module(module)
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🔬✅ Module '{module_name}' from '{module_path}' has sprung to life! The experiment progresses!",
                    **_get_log_args()
                )
            return module
        except Exception as e:
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🔬🔴 The module, it resists! Error loading module '{module_path}': {e}. A setback, but not defeat!",
                    **_get_log_args()
                )
            return None

    def instantiate_gui_class(self, module, parent_widget, class_filter=None):
        """
        Finds and instantiates the first suitable GUI class (ttk.Frame or tk.Frame subclass)
        found in the given module. If class_filter is provided, it attempts to find that specific class.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬🟢 Preparing to conjure a GUI class from module '{module.__name__}' for parent {parent_widget}!",
                **_get_log_args()
            )
        
        target_class = None
        for name, obj in inspect.getmembers(module):
            # Check if it's a class, is a subclass of ttk.Frame or tk.Frame,
            # and is defined within this module (not imported from elsewhere).
            if inspect.isclass(obj) and \
               (issubclass(obj, (ttk.Frame, Frame)) and obj.__module__ == module.__name__):
                
                if class_filter is None: # If no specific class name is requested, take the first one found
                    target_class = obj
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(
                            message=f"🔬✅ A suitable vessel found! GUI class: '{name}'. Designating as default.",
                            **_get_log_args()
                        )
                    break 
                elif name == class_filter: # If a specific class name is requested and found
                    target_class = obj
                    if app_constants.LOCAL_DEBUG_ENABLE:
                        debug_log(
                            message=f"🔬✅ Target acquired! Found explicitly requested GUI class: '{name}'.",
                            **_get_log_args()
                        )
                    break # Found the exact class, no need to search further

        if target_class:
            try:
                config_dict = {
                    "theme_colors": self.theme_colors,
                    "state_mirror_engine": self.state_mirror_engine,
                    "subscriber_router": self.subscriber_router
                }
                
                # Instantiate the class, passing the config_dict explicitly
                instance = target_class(parent_widget, config=config_dict)
                
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬✅ Class '{target_class.__name__}' materialized for parent '{parent_widget}'. The creation ritual is complete!",
                        **_get_log_args()
                    )
                return instance
            except Exception as e:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🔴 The magic falters! Error instantiating class '{target_class.__name__}': {e}. A design flaw, perhaps?",
                        **_get_log_args()
                    )
                return None
        else:
            if class_filter:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🟡 The desired specimen is elusive! GUI class '{class_filter}' not found in module '{module.__name__}'.",
                        **_get_log_args()
                    )
            else:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🟡 No suitable blueprint found! No GUI class (subclass of Frame) in module '{module.__name__}'.",
                        **_get_log_args()
                    )
            return None

    def load_and_instantiate_gui(self, path: pathlib.Path, parent_widget, class_filter=None):
        """
        Loads a module from a given path (directory or Python file)
        and instantiates the first found GUI class within it, optionally filtered by class_filter.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        if app_constants.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🔬🟢 Entering '{current_function_name}'. Preparing to transmogrify a GUI from path: '{path}'!",
                **_get_log_args()
            )

        module_path = None
        module_name = None

        if path.is_dir():
            gui_files_in_dir = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])
            if gui_files_in_dir:
                module_path = gui_files_in_dir[0] # Load the first found gui_*.py
                module_name = module_path.stem
            else:
                if app_constants.LOCAL_DEBUG_ENABLE:
                    debug_log(
                        message=f"🔬🟡 The directory '{path}' is barren! No 'gui_*.py' files found. Skipping this segment.",
                        **_get_log_args()
                    )
                return None
        elif path.is_file() and path.name.startswith("gui_") and path.suffix == '.py':
            module_path = path
            module_name = path.stem
        else:
            if app_constants.LOCAL_DEBUG_ENABLE:
                debug_log(
                    message=f"🔬🔴 Path '{path}' is a conundrum! Not a valid directory or 'gui_*.py' file for module loading. My sensors are baffled!",
                    **_get_log_args()
                )
            return None
        
        if module_path and module_name:
            # Load the.module
            module = self._load_module(module_path, module_name)
            
            if module:
                # Instantiate the GUI class from the loaded module
                instance = self.instantiate_gui_class(module, parent_widget, class_filter=class_filter)
                return instance
        
        return None