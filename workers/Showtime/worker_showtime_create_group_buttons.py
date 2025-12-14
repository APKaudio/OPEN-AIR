
import inspect
import tkinter as tk
from tkinter import ttk
from display.logger import debug_log, console_log
from workers.markers.worker_marker_logic import calculate_frequency_range

def create_group_buttons(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message="🛠️🟢 Creating Group filter buttons.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    
    for widget in showtime_tab_instance.group_frame.winfo_children():
        widget.destroy()
    
    if showtime_tab_instance.selected_zone:
        showtime_tab_instance.group_frame.configure(text=f"GROUPS")
        showtime_tab_instance.group_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        sorted_groups = sorted(showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone].keys())
        for i, group_name in enumerate(sorted_groups):
            is_selected = showtime_tab_instance.selected_group == group_name

            group_devices = showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone][group_name]
            # UPDATED: Use the imported utility function
            min_freq, max_freq = calculate_frequency_range(group_devices)
            
            freq_range_text = ""
            if min_freq is not None and max_freq is not None:
                freq_range_text = f"\n{min_freq} MHz - {max_freq} MHz"
            
            button_text = f"{group_name}{freq_range_text}"
            
            button = ttk.Button(
                showtime_tab_instance.group_frame,
                text=button_text,
                command=lambda g=group_name: showtime_tab_instance._on_group_toggle(g),
                style='Custom.TButton' if not is_selected else 'Custom.Selected.TButton'
            )
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
    else:
        showtime_tab_instance.group_frame.grid_remove()
        
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message=f"✅ Group buttons updated for selected zone.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
