
import inspect
from workers.logger.logger import  debug_logger
from workers.logger.log_utils import _get_log_args
from workers.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      
from workers.Showtime.worker_showtime_tune import on_tune_request_from_selection

def on_zone_toggle(showtime_tab_instance, zone_name):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
        debug_logger(
            message=f"🟢️️️🔵 Zone toggle clicked for: {zone_name}. Current selection: {showtime_tab_instance.selected_zone}.",
            **_get_log_args()
            


        )
    if showtime_tab_instance.selected_zone == zone_name:
        showtime_tab_instance.selected_zone = None
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
            debug_logger(
                message="🟢️️️🟡 Deselected Zone. Clearing Group selection.",
                **_get_log_args()
                


            )
    else:
        showtime_tab_instance.selected_zone = zone_name
        showtime_tab_instance.selected_group = None
        if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
            debug_logger(
                message=f"🟢️️️🟢 Selected new Zone: {showtime_tab_instance.selected_zone}. Clearing Group selection.",
                **_get_log_args()
                


            )
    
    showtime_tab_instance._create_zone_buttons()
    showtime_tab_instance._create_group_buttons()
    showtime_tab_instance._create_device_buttons()
    
    on_tune_request_from_selection(showtime_tab_instance)
