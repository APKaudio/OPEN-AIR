
import inspect
from workers.logger.logger import  debug_log
from workers.utils.log_utils import _get_log_args
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      

def clear_group_buttons(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if showtime_tab_instance.LOCAL_DEBUG_ENABLE:
        debug_log(
            message="🟢️️️🔵 Clearing group buttons.",
            **_get_log_args()
            


        )
    for widget in showtime_tab_instance.group_frame.winfo_children():
        widget.destroy()
