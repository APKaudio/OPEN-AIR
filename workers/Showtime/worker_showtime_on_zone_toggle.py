
import inspect
from display.logger import debug_log, console_log
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection

def on_zone_toggle(showtime_tab_instance, zone_name):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message=f"🛠️🔵 Zone toggle clicked for: {zone_name}. Current selection: {showtime_tab_instance.selected_zone}.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    if showtime_tab_instance.selected_zone == zone_name:
        showtime_tab_instance.selected_zone = None
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message="🛠️🟡 Deselected Zone. Clearing Group selection.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    else:
        showtime_tab_instance.selected_zone = zone_name
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.Local_Debug_Enable:
            debug_log(
                message=f"🛠️🟢 Selected new Zone: {showtime_tab_instance.selected_zone}. Clearing Group selection.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
    
    showtime_tab_instance._create_zone_buttons()
    showtime_tab_instance._create_group_buttons()
    showtime_tab_instance._create_device_buttons()
    
    on_tune_request_from_selection(showtime_tab_instance)
