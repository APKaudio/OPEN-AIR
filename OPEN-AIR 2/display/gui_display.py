# display/gui_display.py
#
# A script that dynamically builds the application's Tkinter GUI based on the
# predefined directory structure.
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
# Version 20250822.010900.8

import os
import inspect
import datetime
import tkinter as tk
from tkinter import ttk
import importlib.util
import sys
import pathlib

# --- Style Import ---
# We need to add the parent directory to the path for this import to work
if str(pathlib.Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from styling.style import THEMES, DEFAULT_THEME


# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 8 # Incremented revision
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"

# --- Dummy Logging Functions ---
def console_log(message: str):
    print(f"[CONSOLE] {message}")

def debug_log(message: str, file: str, version: str, function: str, console_print_func):
    log_message = f"MAD SCIENTIST LOG: {message} (File: {file}, v{version}, Func: {function})"
    console_print_func(log_message)


class Application(tk.Tk):
    """
    The main application class that orchestrates the GUI build process.
    """
    def __init__(self):
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message="🖥️🟢 The grand orchestrator is waking up! Let's get this GUI built!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            super().__init__()
            self.title("OPEN-AIR 2")
            self.geometry("1000x700")

            # --- NEW: Apply the selected theme ---
            # Storing the theme colors as an instance variable for access by other methods
            self.theme_colors = self._apply_styles(theme_name=DEFAULT_THEME)

            self._build_from_directory(path=pathlib.Path(__file__).parent, parent_widget=self)
            
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

    def _apply_styles(self, theme_name: str):
        """
        Applies the specified theme to the entire application using ttk.Style.
        """
        colors = THEMES.get(theme_name, THEMES["dark"]) # Fallback to dark theme
        
        style = ttk.Style(self)
        style.theme_use("clam") # A good base theme for customization

        # --- Configure widget styles ---
        # UPDATED: Applying padding and border_width from the theme to general widgets
        style.configure('.',
                        background=colors["bg"],
                        foreground=colors["fg"],
                        font=('Helvetica', 10),
                        padding=colors["padding"],
                        borderwidth=colors["border_width"])

        style.configure('TFrame',
                        background=colors["bg"])

        style.configure('TNotebook',
                        background=colors["primary"],
                        borderwidth=0)
        
        style.map('TNotebook.Tab',
                  background=[('selected', colors["accent"]), ('!selected', colors["secondary"])],
                  foreground=[('selected', colors["text"]), ('!selected', colors["fg"])])

        # UPDATED: Applying padding from the theme to notebook tabs
        tab_padding = [colors["padding"] * 10, colors["padding"] * 5]
        style.configure('TNotebook.Tab',
                        padding=tab_padding,
                        font=('Helvetica', 11, 'bold'),
                        borderwidth=0)

        # UPDATED: Applying padding and border_width from the theme to buttons
        style.configure('TButton',
                        background=colors["accent"],
                        foreground=colors["text"],
                        padding=colors["padding"] * 5, # Buttons need more padding
                        relief=colors["relief"],
                        borderwidth=colors["border_width"] * 2) # Buttons need a more prominent border
        
        style.map('TButton',
                  background=[('active', colors["secondary"])])

        # --- Configure the main window background ---
        self.configure(background=colors["bg"])
        
        return colors


    def _build_from_directory(self, path: pathlib.Path, parent_widget):
        """
        Recursively builds the GUI based on folder structure, supporting percentage-based layouts.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            sub_dirs = sorted([d for d in path.iterdir() if d.is_dir()])
            layout_dirs = [d for d in sub_dirs if d.name.split('_')[0] in ['left', 'right', 'top', 'bottom']]
            
            if layout_dirs:
                is_horizontal = any(d.name.startswith('left_') or d.name.startswith('right_') for d in layout_dirs)
                is_vertical = any(d.name.startswith('top_') or d.name.startswith('bottom_') for d in layout_dirs)

                if is_horizontal and is_vertical:
                    console_log(f"❌ Layout Error: Cannot mix horizontal and vertical layouts in '{path}'.")
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
                            # Use ttk.Frame for styling
                            # UPDATED: Using borderwidth and relief from the theme
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            new_frame.place(relx=current_relx, rely=0, relwidth=rel_width, relheight=1.0)
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            current_relx += rel_width
                        except (IndexError, ValueError):
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'.")
                
                elif is_vertical:
                    current_rely = 0.0
                    for sub_dir in sorted_layout_dirs:
                        if sub_dir.name.split('_')[0] not in ['top', 'bottom']: continue
                        try:
                            percentage = int(sub_dir.name.split('_')[1])
                            rel_height = percentage / 100.0
                            # Use ttk.Frame for styling
                            # UPDATED: Using borderwidth and relief from the theme
                            new_frame = ttk.Frame(parent_widget, borderwidth=self.theme_colors["border_width"], relief=self.theme_colors["relief"])
                            new_frame.place(relx=0, rely=current_rely, relwidth=1.0, relheight=rel_height)
                            self._build_from_directory(path=sub_dir, parent_widget=new_frame)
                            current_rely += rel_height
                        except (IndexError, ValueError):
                            console_log(f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'.")
                return

            is_tab_container = any(d.name.startswith("tab_") or d.name.startswith("sub_tab_") for d in sub_dirs)
            if is_tab_container:
                notebook = ttk.Notebook(parent_widget)
                notebook.pack(fill=tk.BOTH, expand=True)
                
                tab_dirs = [d for d in sub_dirs if d.name.startswith("tab_") or d.name.startswith("sub_tab_")]
                for tab_dir in tab_dirs:
                    # Use ttk.Frame for styling
                    tab_frame = ttk.Frame(notebook)
                    parts = tab_dir.name.split('_')
                    start_index = next((i for i, part in enumerate(parts) if part.isdigit()), -1)
                    display_name = " ".join(parts[start_index + 1:]).title() if start_index != -1 else tab_dir.name
                    notebook.add(tab_frame, text=display_name)
                    self._build_from_directory(path=tab_dir, parent_widget=tab_frame)
                return

            for sub_dir in sub_dirs:
                if sub_dir.name.startswith("child_"):
                    self._build_child_container(path=sub_dir, parent_widget=parent_widget)

            py_files = [f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py']
            for py_file in py_files:
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
        current_function_name = inspect.currentframe().f_code.co_name
        
        try:
            if path.is_dir():
                gui_file = next(f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py')
            else:
                gui_file = path

            module_name = gui_file.stem
            spec = importlib.util.spec_from_file_location(module_name, gui_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module, "create_yo_button_frame"):
                module.create_yo_button_frame(parent_widget)
            elif hasattr(module, "GUIFrame"):
                frame_instance = module.GUIFrame(parent_widget)
                frame_instance.pack(fill=tk.BOTH, expand=True)
            else:
                raise AttributeError(f"Module '{module_name}' needs a 'create_yo_button_frame' function or 'GUIFrame' class.")

        except Exception as e:
            console_log(f"❌ Error importing or executing module at {path}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )


if __name__ == "__main__":
    console_log("--- Initializing the Dynamic GUI Builder ---")
    
    app = Application()
    app.mainloop()
    console_log("--- Application closed. ---")
