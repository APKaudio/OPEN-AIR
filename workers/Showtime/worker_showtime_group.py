# workers/Showtime/worker_showtime_group.py
#
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#

import inspect
from collections import defaultdict
from workers.logger.logger import  debug_log
from workers.utils.log_utils import _get_log_args
from workers.mqtt.setup.config_reader import Config # Import the Config class                                                                          

app_constants = Config.get_instance() # Get the singleton instance      


def process_and_sort_markers(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(
            message="🟢️️️🔵 Processing and sorting marker data by Zone, Group, and Device.",
            **_get_log_args()
            


        )

    showtime_tab_instance.grouped_markers = defaultdict(lambda: defaultdict(list))
    
    for row in showtime_tab_instance.marker_data:
        zone = row.get('ZONE', 'N/A')
        group = row.get('GROUP', 'N/A')
        showtime_tab_instance.grouped_markers[zone][group].append(row)
    
    for zone, groups in showtime_tab_instance.grouped_markers.items():
        for group, devices in groups.items():
            devices.sort(key=lambda x: x.get('NAME', ''))
    
    if app_constants.LOCAL_DEBUG_ENABLE: 
        debug_log(
            message="✅ Markers grouped and sorted successfully.",
            **_get_log_args()
            


        )