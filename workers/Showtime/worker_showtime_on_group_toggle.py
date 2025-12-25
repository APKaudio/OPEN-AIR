
import inspect
from workers.logger.logger import  debug_log
from workers.utils.log_utils import _get_log_args
from workers.mqtt.setup.config_reader import app_constants
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection

def on_group_toggle(showtime_tab_instance, group_name):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
        debug_log(
            message=f"🟢️️️🔵 Group toggle clicked for: {group_name}. Current selection: {showtime_tab_instance.selected_group}.",
            **_get_log_args()
            


        )
    if showtime_tab_instance.selected_group == group_name:
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
            debug_log(
                message="🟢️️️🟡 Deselected Group. Showing all devices for the current Zone.",
                **_get_log_args()
                


            )
    else:
        showtime_tab_instance.selected_group = group_name
        if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
            debug_log(
                message=f"🟢️️️🟢 Selected new Group: {showtime_tab_instance.selected_group}.",
                **_get_log_args()
                


            )
    
    showtime_tab_instance._create_group_buttons()
    showtime_tab_instance._create_device_buttons()
    
    on_tune_request_from_selection(showtime_tab_instance)
