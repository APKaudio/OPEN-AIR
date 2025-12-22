# workers/Showtime/worker_showtime_read.py
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
from workers.logger.logger import  debug_log, console_log
from workers.importers.worker_marker_file_import_handling import maker_file_check_for_markers_file

Local_Debug_Enable = True



def load_marker_data(showtime_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message="🛠️🟢 Loading raw marker data from file.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    
    raw_headers, raw_data = maker_file_check_for_markers_file()
    
    if not raw_data:
        showtime_tab_instance.marker_data = []
        showtime_tab_instance.column_headers = []
        console_log("🟡 No marker data found in MARKERS.csv. No buttons will be created.")
        return

    showtime_tab_instance.marker_data = [dict(zip(raw_headers, row)) for row in raw_data if len(row) == len(raw_headers)]
    showtime_tab_instance.column_headers = raw_headers

    if Local_Debug_Enable:
        debug_log(
            message=f"✅ Loaded {len(showtime_tab_instance.marker_data)} rows. Converted to dictionaries for sorting and display.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )