
import inspect
import tkinter as tk
from tkinter import ttk
from display.logger import debug_log, console_log

def create_device_buttons(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message="🛠️🟢 Creating Device buttons.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    
    if showtime_tab_instance.selected_device_button:
        showtime_tab_instance.selected_device_button.config(style='Custom.TButton')
    showtime_tab_instance.selected_device_button = None

    for widget in showtime_tab_instance.device_frame.winfo_children():
        widget.destroy()
    
    filtered_devices = []
    if showtime_tab_instance.selected_zone and showtime_tab_instance.selected_group:
        filtered_devices = showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone][showtime_tab_instance.selected_group]
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message=f"🔍 Showing devices for Zone: {showtime_tab_instance.selected_zone} and Group: {showtime_tab_instance.selected_group}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    elif showtime_tab_instance.selected_zone:
        for group_name in showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone]:
            filtered_devices.extend(showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone][group_name])
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message=f"🔍 Showing all devices for selected Zone: {showtime_tab_instance.selected_zone}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    else:
        filtered_devices = showtime_tab_instance.marker_data
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message="🔍 Showing all devices from MARKERS.csv.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )

    for i, row_data in enumerate(filtered_devices):
        button_text = (
                       f"{row_data.get('NAME', 'N/A')}\n"
                       f"{row_data.get('DEVICE', 'N/A')}\n"
                       f"{row_data.get('FREQ_MHZ', 'N/A')} MHz\n"
                       f"[********************]"
                      )
        
        button = ttk.Button(
            showtime_tab_instance.device_frame,
            text=button_text,
            style='Custom.TButton'
        )
        # Store data directly on the button object
        button.marker_data = row_data
        button.configure(command=lambda b=button: showtime_tab_instance._on_marker_button_click(b))
        
        row = i // 4
        col = i % 4
        button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message=f"✅ Created {len(filtered_devices)} device buttons.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
