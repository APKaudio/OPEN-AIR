
import inspect
from display.logger import debug_log, console_log
from workers.Showtime.worker_showtime_create_group_buttons import create_group_buttons
from workers.Showtime.worker_showtime_create_device_buttons import create_device_buttons
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection

def on_group_toggle(showtime_tab_instance, group_name):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message=f"🛠️🔵 Group toggle clicked for: {group_name}. Current selection: {showtime_tab_instance.selected_group}.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    if showtime_tab_instance.selected_group == group_name:
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message="🛠️🟡 Deselected Group. Showing all devices for the current Zone.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    else:
        showtime_tab_instance.selected_group = group_name
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Selected new Group: {showtime_tab_instance.selected_group}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    
    create_group_buttons(showtime_tab_instance)
    create_device_buttons(showtime_tab_instance)
    
    on_tune_request_from_selection(showtime_tab_instance)
