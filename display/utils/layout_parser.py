# display/utils/layout_parser.py

import os
import inspect
import pathlib
import tkinter as tk # Import tk for HORIZONTAL and VERTICAL constants
from tkinter import ttk # ttk is still needed for widget classes if referenced
from workers.utils.log_utils import _get_log_args 

class LayoutParser:
    """
    Parses directory structures to determine the GUI layout (e.g., PanedWindow, Notebook).
    This is a stateless utility class.
    """
    def __init__(self, current_version, LOCAL_DEBUG_ENABLE, debug_log_func):
        self.current_version = current_version
        self.LOCAL_DEBUG_ENABLE = LOCAL_DEBUG_ENABLE
        self.debug_log = debug_log_func if debug_log_func else (lambda message, **kwargs: None)
            
    def parse_directory(self, path: pathlib.Path):
        """
        Analyzes a directory path to determine its intended GUI layout structure.
        Returns a dictionary describing the layout and relevant parsed data.
        Expected layout types: 'horizontal_split', 'vertical_split', 'notebook', 'monitors', 'recursive_build', 'error'.
        """
        current_function_name = inspect.currentframe().f_code.co_name
        self.debug_log(
            message=f"Parsing directory: '{path}'",
            **_get_log_args()
        )

        try:
            sub_dirs = sorted([d for d in path.iterdir() if d.is_dir()])
        except FileNotFoundError:
            self.debug_log(
                message=f"❌ Error: Directory not found for parsing: {path}",
                **_get_log_args()
            )
            return {'type': 'error', 'data': {'error_message': 'Directory not found.'}}

        layout_dirs = [d for d in sub_dirs if d.name.split('_')[0] in ['left', 'right', 'top', 'bottom']]
        potential_tab_dirs = [d for d in sub_dirs if d.name and d.name[0].isdigit()]

        layout_type = 'unknown'
        layout_data = {}

        if layout_dirs:
            is_horizontal = any(d.name.startswith('left_') or d.name.startswith('right_') for d in layout_dirs)
            is_vertical = any(d.name.startswith('top_') or d.name.startswith('bottom_') for d in layout_dirs)

            if is_horizontal and is_vertical:
                self.debug_log(
                    message=f"❌ Layout Error: Cannot mix horizontal and vertical layouts in '{path}'.",
                    **_get_log_args()
                )
                layout_type = 'error'
                layout_data['error_message'] = "Mixed horizontal and vertical layouts."
            elif is_horizontal:
                layout_type = 'horizontal_split'
                # Sort by 'left', 'right' order
                sort_order = ['left', 'right']
                sorted_layout_dirs = sorted(layout_dirs, key=lambda d: sort_order.index(d.name.split('_')[0]))
                
                layout_data['orientation'] = tk.HORIZONTAL # Corrected: Use tk.HORIZONTAL
                layout_data['panels'] = []
                percentages = []
                for sub_dir in sorted_layout_dirs:
                    if sub_dir.name.split('_')[0] not in ['left', 'right']: continue # Ensure it's a horizontal panel dir
                    try:
                        percentage = int(sub_dir.name.split('_')[1])
                        percentages.append(percentage)
                        layout_data['panels'].append({'name': sub_dir.name, 'path': sub_dir, 'weight': percentage})
                    except (IndexError, ValueError) as e:
                        self.debug_log(
                            message=f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'. Error: {e}",
                            **_get_log_args()
                        )
                layout_data['panel_percentages'] = percentages
            elif is_vertical:
                layout_type = 'vertical_split'
                # Sort by 'top', 'bottom' order
                sort_order = ['top', 'bottom']
                sorted_layout_dirs = sorted(layout_dirs, key=lambda d: sort_order.index(d.name.split('_')[0]))

                layout_data['orientation'] = tk.VERTICAL # Corrected: Use tk.VERTICAL
                layout_data['panels'] = []
                percentages = []
                for sub_dir in sorted_layout_dirs:
                    if sub_dir.name.split('_')[0] not in ['top', 'bottom']: continue # Ensure it's a vertical panel dir
                    try:
                        percentage = int(sub_dir.name.split('_')[1])
                        percentages.append(percentage)
                        layout_data['panels'].append({'name': sub_dir.name, 'path': sub_dir, 'weight': percentage})
                    except (IndexError, ValueError) as e:
                        self.debug_log(
                            message=f"⚠️ Warning: Could not parse percentage from folder name '{sub_dir.name}'. Error: {e}",
                            **_get_log_args()
                        )
                layout_data['panel_percentages'] = percentages
            else:
                 # This case should ideally not be reached if layout_dirs is not empty and logic is sound
                self.debug_log(
                    message=f"Found layout_dirs but no clear orientation detected in '{path}'.",
                    **_get_log_args()
                )

        elif potential_tab_dirs:
            layout_type = 'notebook'
            # Filter for actual tab directories (starting with a digit) and sort them numerically.
            tab_dirs = sorted([d for d in sub_dirs if d.name and d.name[0].isdigit()], 
                              key=lambda d: int(d.name.split('_')[0]))
            layout_data['tabs'] = []
            for tab_dir in tab_dirs:
                parts = tab_dir.name.split('_')
                # Find the first numeric part to determine sorting. Assumes format like '1_TabName', '02_AnotherTab'
                digit_part_index = -1
                for i, part in enumerate(parts):
                    if part.isdigit():
                        digit_part_index = i
                        break
                
                display_name = " ".join(parts[digit_part_index + 1:]).title() if digit_part_index != -1 else tab_dir.name
                layout_data['tabs'].append({'name': tab_dir.name, 'path': tab_dir, 'display_name': display_name})
        
        elif "2_monitors" in str(path): # Special case for monitors directory from original code
            layout_type = 'monitors'
            layout_data['gui_files'] = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])

        else: # Default case: look for child containers or GUI files
            layout_type = 'recursive_build'
            layout_data['child_containers'] = [d for d in sub_dirs if d.name.startswith("child_")]
            layout_data['gui_files'] = sorted([f for f in path.iterdir() if f.is_file() and f.name.startswith("gui_") and f.suffix == '.py'])

        self.debug_log(
            message=f"Parsed layout for '{path}': Type='{layout_type}', Data={layout_data}",
            **_get_log_args()
        )
        return {'type': layout_type, 'data': layout_data}

