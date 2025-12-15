
import inspect
from display.logger import debug_log, console_log
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection

def on_marker_button_click(showtime_tab_instance, button):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message="🛠️🔵 Device button clicked. Toggling selection.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    marker_data = button.marker_data
    
    if showtime_tab_instance.selected_device_button == button:
        showtime_tab_instance.selected_device_button.config(style='Custom.TButton')
        showtime_tab_instance.selected_device_button = None
        console_log(f"🟡 Deselected device: {marker_data.get('NAME', 'N/A')}.")
    else:
        if showtime_tab_instance.selected_device_button:
            showtime_tab_instance.selected_device_button.config(style='Custom.TButton')
        
        showtime_tab_instance.selected_device_button = button
        showtime_tab_instance.selected_device_button.config(style='Custom.Selected.TButton')
        console_log(f"✅ Selected device: {marker_data.get('NAME', 'N/A')} at {marker_data.get('FREQ_MHZ', 'N/A')} MHz.")
    
    on_tune_request_from_selection(showtime_tab_instance)
