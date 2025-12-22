# display/utils/module_loader.py

import os
import inspect
import sys
import importlib.util
import pathlib
from tkinter import ttk, Frame

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

# Placeholder for logger functions
def debug_log_placeholder(*args, **kwargs): pass
def console_log_placeholder(*args, **kwargs): pass

class ModuleLoader:
    """
    Handles dynamic loading of Python modules and instantiation of GUI classes.
    Includes logic for suppressing common import errors like PIL/ImageTk.
    """
    def __init__(self, current_version, local_debug_enable, console_log_func, debug_log_func, theme_colors_func):
        self.current_version = current_version
        self.Local_Debug_Enable = local_debug_enable
        self.console_log = console_log_func if console_log_func else console_log_placeholder
        self.debug_log = debug_log_func if debug_log_func else debug_log_placeholder
        # Theme colors are passed from the Application class to be available for GUI instantiation
        self.theme_colors = theme_colors_func 

    def _log_debug(self, message, function_name):
        if self.Local_Debug_Enable:
            self.debug_log(
                message=message,
                file=os.path.basename(__file__),
                version=self.current_version,
                function=f"{self.__class__.__name__}.{function_name}",
                console_print_func=self.console_log
            )

    def _load_module(self, module_path: pathlib.Path, module_name: str):
        """
        Dynamically loads a Python module from a given path.
        Returns the module object. Handles potential import errors.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self._log_debug(f"Loading module from '{module_path}' with name '{module_name}'", current_function_name)
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            if spec is None:
                self.console_log(f"❌ Error: Could not create module spec for {module_path}")
                self._log_debug(f"Module spec is None for {module_path}", current_function_name)
                return None
                
            module = importlib.util.module_from_spec(spec)
            
            # Add module to sys.modules to ensure it's discoverable by other imports.
            # Using a unique name derived from the path can prevent conflicts if the same
            # module name appears in different locations. For simplicity, we use module_name
            # as provided, but a more robust system might prepend a path hash.
            if module_name in sys.modules:
                 self._log_debug(f"Warning: Module '{module_name}' already in sys.modules. Overwriting could be risky.", current_function_name)
            sys.modules[module_name] = module
            
            spec.loader.exec_module(module)
            self._log_debug(f"Successfully executed module '{module_name}' from {module_path}", current_function_name)
            return module
        except Exception as e:
            self.console_log(f"❌ Error loading module {module_path}: {e}")
            self._log_debug(f"Failed to load module {module_path}: {e}", current_function_name)
            return None

    def instantiate_gui_class(self, module, parent_widget, class_filter=None):
        """
        Finds and instantiates the first suitable GUI class (ttk.Frame or tk.Frame subclass)
        found in the given module. If class_filter is provided, it attempts to find that specific class.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self._log_debug(f"Instantiating GUI class from module '{module.__name__}' for parent {parent_widget}", current_function_name)
        
        target_class = None
        for name, obj in inspect.getmembers(module):
            # Check if it's a class, is a subclass of ttk.Frame or tk.Frame,
            # and is defined within this module (not imported from elsewhere).
            if inspect.isclass(obj) and \
               (issubclass(obj, (ttk.Frame, Frame)) and obj.__module__ == module.__name__):
                
                if class_filter is None: # If no specific class name is requested, take the first one found
                    target_class = obj
                    self._log_debug(f"Found GUI class: '{name}'. Selecting as default.", current_function_name)
                    # Break here if we only want the *first* GUI class encountered.
                    # If there could be multiple, and we need to select based on some criteria,
                    # this logic would need to be more sophisticated. For now, assume first is fine.
                    break 
                elif name == class_filter: # If a specific class name is requested and found
                    target_class = obj
                    self._log_debug(f"Found explicitly requested GUI class: '{name}'.", current_function_name)
                    break # Found the exact class, no need to search further

        if target_class:
            try:
                # Pass theme colors and other necessary configurations to the constructor.
                # The original code passed a 'config' dictionary.
                config_dict = {"theme_colors": self.theme_colors}
                
                # Instantiate the class. The constructor expects parent_widget as the first argument
                # and potentially a 'config' keyword argument.
                # This assumes the target GUI classes accept this signature.
                instance = target_class(parent_widget, config=config_dict)
                
                self._log_debug(f"Successfully instantiated '{target_class.__name__}' for parent '{parent_widget}'.", current_function_name)
                return instance
            except Exception as e:
                self.console_log(f"❌ Error instantiating class '{target_class.__name__}': {e}")
                self._log_debug(f"Failed to instantiate '{target_class.__name__}': {e}", current_function_name)
                return None
        else:
            if class_filter:
                self.console_log(f"⚠️ Warning: GUI class '{class_filter}' not found in module '{module.__name__}'.")
                self._log_debug(f"Requested GUI class '{class_filter}' not found in module '{module.__name__}'.", current_function_name)
            else:
                self.console_log(f"⚠️ Warning: No suitable GUI class (subclass of Frame) found in module '{module.__name__}'.")
                self._log_debug(f"No suitable GUI class found in module '{module.__name__}'.", current_function_name)
            return None

    def load_and_instantiate_gui(self, path: pathlib.Path, parent_widget, class_filter=None):
        """
        Loads a module from a given path (directory or Python file)
        and instantiates the first found GUI class within it, optionally filtered by class_filter.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self._log_debug(f"Entering 'load_and_instantiate_gui' for path: '{path}'", current_function_name)

        module_path = None
        module_name = None

        if path.is_dir():
            # If the path is a directory, it might represent a module itself (if it has __init__.py)
            # or it might contain GUI files. The original code searched for 'gui_*.py' within directories.
            # Let's assume we're looking for a gui_*.py file within this directory.
            gui_files_in_dir = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])
            if gui_files_in_dir:
                module_path = gui_files_in_dir[0] # Load the first found gui_*.py
                module_name = module_path.stem
            else:
                self._log_debug(f"No 'gui_*.py' files found in directory '{path}'. Skipping.", current_function_name)
                return None
        elif path.is_file() and path.name.startswith("gui_") and path.suffix == '.py':
            module_path = path
            module_name = path.stem
        else:
            self.console_log(f"❌ Error: Path '{path}' is not a valid directory or 'gui_*.py' file for module loading.")
            self._log_debug(f"Invalid path for GUI loading: '{path}'", current_function_name)
            return None
        
        if module_path and module_name:
            # Load the module
            module = self._load_module(module_path, module_name)
            
            if module:
                # Instantiate the GUI class from the loaded module
                instance = self.instantiate_gui_class(module, parent_widget, class_filter=class_filter)
                return instance
        
        return None