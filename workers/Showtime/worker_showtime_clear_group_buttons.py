
import inspect
from display.logger import debug_log, console_log

def clear_group_buttons(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.Local_Debug_Enable:
        debug_log(
            message="🛠️🔵 Clearing group buttons.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    for widget in showtime_tab_instance.group_frame.winfo_children():
        widget.destroy()
