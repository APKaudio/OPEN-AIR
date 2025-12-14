# workers/Showtime/worker_showtime_tune.py
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
from display.logger import debug_log, console_log
from workers.active.worker_active_marker_tune_and_collect import Push_Marker_to_Center_Freq, Push_Marker_to_Start_Stop_Freq
from workers.markers.worker_marker_logic import calculate_frequency_range

Local_Debug_Enable = True

def console_log_switch(message):
    if Local_Debug_Enable:
        console_log(message)

def on_tune_request_from_selection(showtime_tab_instance):
    """
    Tunes the instrument based on the current selections.
    """
    current_function = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message="🛠️🟢 Initiating tuning request based on current selection.",
            file=showtime_tab_instance.current_file,
            version=showtime_tab_instance.current_version,
            function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
            console_print_func=console_log
        )
    
    if showtime_tab_instance.selected_device_button:
        # Case 1: A specific device is selected
        marker_data = showtime_tab_instance.selected_device_button.marker_data
        if Local_Debug_Enable:
            debug_log(
                message=f"🔍 Device button selected. Tuning to center frequency of {marker_data.get('NAME', 'N/A')}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        Push_Marker_to_Center_Freq(mqtt_controller=showtime_tab_instance.mqtt_util, marker_data=marker_data)
    elif showtime_tab_instance.selected_group:
        # Case 2: A group is selected, but no device
        if Local_Debug_Enable:
            debug_log(
                message=f"🔍 No device selected. Tuning to start/stop frequency of selected Group: {showtime_tab_instance.selected_group}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        group_devices = showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone][showtime_tab_instance.selected_group]
        # UPDATED: Use the imported utility function
        min_freq, max_freq = calculate_frequency_range(group_devices)
        
        if min_freq is not None and max_freq is not None:
            mock_marker_data = {'FREQ_MHZ': (min_freq + max_freq) / 2}
            Push_Marker_to_Start_Stop_Freq(mqtt_controller=showtime_tab_instance.mqtt_util, marker_data=mock_marker_data, buffer=(max_freq - min_freq) * 1e6)
        else:
            console_log_switch("❌ Failed to tune: No valid frequencies found in selected group.")
            
    elif showtime_tab_instance.selected_zone:
        # Case 3: A zone is selected, but no group or device
        if Local_Debug_Enable:
            debug_log(
                message=f"🔍 No group selected. Tuning to start/stop frequency of selected Zone: {showtime_tab_instance.selected_zone}.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{showtime_tab_instance.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        all_zone_devices = []
        for group_name in showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone]:
            all_zone_devices.extend(showtime_tab_instance.grouped_markers[showtime_tab_instance.selected_zone][group_name])
        # UPDATED: Use the imported utility function
        min_freq, max_freq = calculate_frequency_range(all_zone_devices)
        
        if min_freq is not None and max_freq is not None:
            mock_marker_data = {'FREQ_MHZ': (min_freq + max_freq) / 2}
            Push_Marker_to_Start_Stop_Freq(mqtt_controller=showtime_tab_instance.mqtt_util, marker_data=mock_marker_data, buffer=(max_freq - min_freq) * 1e6)
        else:
            console_log_switch("❌ Failed to tune: No valid frequencies found in selected zone.")
    else:
        # Case 4: No filters selected, tune to all markers
        if Local_Debug_Enable:
            debug_log(
                message="🔍 No filters selected. Tuning to start/stop frequency of all markers.",
                file=showtime_tab_instance.current_file,
                version=showtime_tab_instance.current_version,
                function=f"{self.__class__.__name__}.{current_function}",
                console_print_func=console_log
            )
        # UPDATED: Use the imported utility function
        min_freq, max_freq = calculate_frequency_range(showtime_tab_instance.marker_data)
        
        if min_freq is not None and max_freq is not None:
            mock_marker_data = {'FREQ_MHZ': (min_freq + max_freq) / 2}
            Push_Marker_to_Start_Stop_Freq(mqtt_controller=showtime_tab_instance.mqtt_util, marker_data=mock_marker_data, buffer=(max_freq - min_freq) * 1e6)
        else:
            console_log_switch("❌ Failed to tune: No valid frequencies found in marker data.")