# workers/Showtime/worker_showtime_group.py
#
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213
Current_Time = 120000
Current_iteration = 44

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
from workers.logger.logger import  debug_log, console_log

Local_Debug_Enable = True



def process_and_sort_markers(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message="🛠️🔵 Processing and sorting marker data by Zone, Group, and Device.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )

    showtime_tab_instance.grouped_markers = defaultdict(lambda: defaultdict(list))
    
    for row in showtime_tab_instance.marker_data:
        zone = row.get('ZONE', 'N/A')
        group = row.get('GROUP', 'N/A')
        showtime_tab_instance.grouped_markers[zone][group].append(row)
    
    for zone, groups in showtime_tab_instance.grouped_markers.items():
        for group, devices in groups.items():
            devices.sort(key=lambda x: x.get('NAME', ''))
    
    if Local_Debug_Enable:
        debug_log(
            message="✅ Markers grouped and sorted successfully.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )