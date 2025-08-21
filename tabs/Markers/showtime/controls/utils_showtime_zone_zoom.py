# tabs/Markers/showtime/controls/utils_showtime_zone_zoom.py
#
# This utility file provides the backend logic for the Zone Zoom tab in the ControlsFrame.
# It contains functions to calculate and set the instrument's span based on
# selected zones, groups, devices, or all markers by calling YakBeg handlers.
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
#
# Version 20250822.100800.1
# UPDATED: set_span_to_zone and set_span_to_group now read min/max frequencies and device count
#          from the shared state, ensuring consistency between the UI state and calculations.
# UPDATED: All debug logs now include the correct emoji prefixes.
# UPDATED: Versioning and file header adhere to new standards.

import inspect
import os
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ
from process_math.math_frequency_translation import format_hz

# Import the YakBeg handlers for direct instrument control
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

# --- Versioning ---
w = 20250822
x_str = '100800'
x = int(x_str) if not x_str.startswith('0') else int(x_str[1:])
y = 1
current_version = f"Version {w}.{x_str}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"


def _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz):
    # [Calculates the buffered start and stop frequencies based on a given buffer value.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️ 🟢 Entering {current_function} with start: {start_freq_mhz}, stop: {stop_freq_mhz}, buffer: {buffer_mhz}", file=current_file, version=current_version, function=current_function)
    
    buffered_start_freq_mhz = start_freq_mhz - buffer_mhz
    buffered_stop_freq_mhz = stop_freq_mhz + buffer_mhz
    
    debug_log(message=f"🛠️ 🟢 Exiting {current_function} with buffered start: {buffered_start_freq_mhz}, buffered stop: {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
    
    return buffered_start_freq_mhz, buffered_stop_freq_mhz

def set_span_to_all_markers(showtime_tab_instance, zone_zoom_tab):
    # [Calculates the required span to view all markers and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️ 🟢 Entering {current_function}", file=current_file, version=current_version, function="set_span_to_all_markers")
    
    # Get necessary info from the shared state and zgd_frame
    all_devices = showtime_tab_instance.zgd_frame._get_all_devices_in_zone(showtime_tab_instance.zgd_frame.structured_data, None)
    
    if not all_devices:
        showtime_tab_instance.console_print_func("⚠️ No markers loaded. Cannot set span to all markers.")
        debug_log(message=f"🛠️ 🚫 No markers found.", file=current_file, version=current_version, function=current_function)
        return
        
    freqs = [float(d['CENTER']) for d in all_devices if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
    if not freqs:
        showtime_tab_instance.console_print_func("⚠️ No valid frequencies found in markers. Cannot set span.")
        debug_log(message=f"🛠️ 🚫 No valid frequencies found in markers.", file=current_file, version=current_version, function=current_function)
        return
    
    start_freq_mhz = min(freqs)
    stop_freq_mhz = max(freqs)
    number_of_markers = len(freqs)

    try:
        # 📖 Read Data: Retrieve buffer value.
        buffer_mhz = float(showtime_tab_instance.shared_state.buffer_var.get())
        debug_log(message=f"📖 Reading shared state: buffer_var = {buffer_mhz} MHz", file=current_file, version=current_version, function=current_function)

        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)
        
        # 📝 Write Data: Store the buffered frequencies in the shared state.
        debug_log(message=f"📝 Writing shared state: buffered_start_var = {buffered_start_freq_mhz}, buffered_stop_var = {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
        showtime_tab_instance.shared_state.buffered_start_var.set(buffered_start_freq_mhz)
        showtime_tab_instance.shared_state.buffered_stop_var.set(buffered_stop_freq_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to all markers: {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        
        # FIXED: Calling the handler here after the values are calculated
        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)

        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set("All Markers")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"({number_of_markers} Devices)")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz\nStop: {buffered_stop_freq_mhz:.3f} MHz")
        
        # Trigger UI sync on ZoneZoomTab
        zone_zoom_tab._sync_ui_from_state()
        debug_log(message=f"🛠️ ✅ Successfully updated all markers span and UI.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_all_markers: {e}")
        debug_log(message=f"🛠️ 🧨 Shiver me timbers, setting span to all markers has failed! The error be: {e}", file=current_file, version=current_version, function="set_span_to_all_markers")

def set_span_to_zone(showtime_tab_instance, zone_zoom_tab):
    # [Calculates the required span for a zone and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️ 🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)

    zone_info = showtime_tab_instance.shared_state.selected_zone_info
    zone_name = showtime_tab_instance.shared_state.selected_zone

    if not zone_name:
        showtime_tab_instance.console_print_func("⚠️ No zone selected. Cannot set span to zone.")
        debug_log(message=f"🛠️ 🚫 No zone selected.", file=current_file, version=current_version, function=current_function)
        return
    
    start_freq_mhz = zone_info.get('min_freq')
    stop_freq_mhz = zone_info.get('max_freq')
    number_of_markers = zone_info.get('device_count')
    
    if number_of_markers == 0:
        showtime_tab_instance.console_print_func(f"⚠️ No valid frequencies found in zone '{zone_name}'. Cannot set span.")
        debug_log(message=f"🛠️ 🚫 No valid frequencies found in zone '{zone_name}'.", file=current_file, version=current_version, function=current_function)
        return
    
    debug_log(message=f"🛠️ 🔍 Reading shared state: zone_info = {zone_info}", file=current_file, version=current_version, function=current_function)
    
    try:
        # 📖 Read Data: Retrieve buffer value.
        buffer_mhz = float(showtime_tab_instance.shared_state.buffer_var.get())
        debug_log(message=f"📖 Reading shared state: buffer_var = {buffer_mhz} MHz", file=current_file, version=current_version, function=current_function)

        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)

        # 📝 Write Data: Store the buffered frequencies in the shared state.
        debug_log(message=f"📝 Writing shared state: buffered_start_var = {buffered_start_freq_mhz}, buffered_stop_var = {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
        showtime_tab_instance.shared_state.buffered_start_var.set(buffered_start_freq_mhz)
        showtime_tab_instance.shared_state.buffered_stop_var.set(buffered_stop_freq_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to zone '{zone_name}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        
        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set(f"Zone ({number_of_markers} Devices)")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Name: {zone_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz\nStop: {buffered_stop_freq_mhz:.3f} MHz")
        
        zone_zoom_tab._sync_ui_from_state()
        debug_log(message=f"🛠️ ✅ Successfully updated zone span and UI.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_zone: {e}")
        debug_log(message=f"🛠️ 🧨 Arrr, the code be capsized! The error be: {e}", file=current_file, version=current_version, function="set_span_to_zone")

def set_span_to_group(showtime_tab_instance, zone_zoom_tab):
    # [Calculates the required span for a group and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️ 🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    group_info = showtime_tab_instance.shared_state.selected_group_info
    group_name = showtime_tab_instance.shared_state.selected_group
    
    if not group_name:
        showtime_tab_instance.console_print_func("⚠️ No group selected. Cannot set span to group.")
        debug_log(message=f"🛠️ 🚫 No group selected.", file=current_file, version=current_version, function=current_function)
        return
        
    start_freq_mhz = group_info.get('min_freq')
    stop_freq_mhz = group_info.get('max_freq')
    number_of_markers = group_info.get('device_count')

    if number_of_markers == 0:
        showtime_tab_instance.console_print_func(f"⚠️ No valid frequencies found in group '{group_name}'. Cannot set span.")
        debug_log(message=f"🛠️ 🚫 No valid frequencies found in group '{group_name}'.", file=current_file, version=current_version, function=current_function)
        return

    debug_log(message=f"🛠️ 🔍 Reading shared state: group_info = {group_info}", file=current_file, version=current_version, function=current_function)
    
    try:
        # 📖 Read Data: Retrieve buffer value.
        buffer_mhz = float(showtime_tab_instance.shared_state.buffer_var.get())
        debug_log(message=f"📖 Reading shared state: buffer_var = {buffer_mhz} MHz", file=current_file, version=current_version, function=current_function)

        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)

        # 📝 Write Data: Store the buffered frequencies in the shared state.
        debug_log(message=f"📝 Writing shared state: buffered_start_var = {buffered_start_freq_mhz}, buffered_stop_var = {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
        showtime_tab_instance.shared_state.buffered_start_var.set(buffered_start_freq_mhz)
        showtime_tab_instance.shared_state.buffered_stop_var.set(buffered_stop_freq_mhz)
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to group '{group_name}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")

        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set(f"Group ({number_of_markers} Devices)")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Name: {group_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz\nStop: {buffered_stop_freq_mhz:.3f} MHz")
        
        zone_zoom_tab._sync_ui_from_state()
        debug_log(message=f"🛠️ ✅ Successfully updated group span and UI.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_group: {e}")
        debug_log(message=f"🛠️ 🧨 Great Scott! The group span calculation has failed! The error is: {e}", file=current_file, version=current_version, function="set_span_to_group")
        
def set_span_to_device(showtime_tab_instance, zone_zoom_tab):
    # [Sets the instrument's span to focus on a single device using a center-span command.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(message=f"🛠️ 🟢 Entering {current_function}", file=current_file, version=current_version, function=current_function)
    
    device_info = showtime_tab_instance.shared_state.selected_device_info
    
    if not device_info:
        showtime_tab_instance.console_print_func("⚠️ No device selected. Cannot set span to device.")
        debug_log(message=f"🛠️ 🚫 No device selected.", file=current_file, version=current_version, function=current_function)
        return

    device_name = device_info.get('NAME')
    center_freq_mhz = device_info.get('CENTER')
    
    debug_log(message=f"🛠️ 🔍 Reading shared state: device_name={device_name}, center_freq_mhz={center_freq_mhz}", file=current_file, version=current_version, function=current_function)
    
    try:
        # 📖 Read Data: Retrieve buffer value.
        buffer_mhz = float(showtime_tab_instance.shared_state.buffer_var.get())
        debug_log(message=f"📖 Reading shared state: buffer_var = {buffer_mhz} MHz", file=current_file, version=current_version, function=current_function)

        center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
        
        # FIXED: Check if the value contains 'M' and convert it to a float.
        span_str = showtime_tab_instance.shared_state.span_var.get()
        if 'M' in span_str:
            span_mhz = float(span_str.replace('M', ''))
        else:
            span_mhz = float(span_str)
            
        span_hz = int(span_mhz * MHZ_TO_HZ)
        
        # Calculate start and stop with the buffer for display purposes
        buffered_span = span_mhz + (2 * buffer_mhz)
        buffered_start_freq_mhz = center_freq_mhz - (buffered_span / 2)
        buffered_stop_freq_mhz = center_freq_mhz + (buffered_span / 2)
        
        # 📝 Write Data: Store the buffered frequencies in the shared state.
        debug_log(message=f"📝 Writing shared state: buffered_start_var = {buffered_start_freq_mhz}, buffered_stop_var = {buffered_stop_freq_mhz}", file=current_file, version=current_version, function=current_function)
        showtime_tab_instance.shared_state.buffered_start_var.set(buffered_start_freq_mhz)
        showtime_tab_instance.shared_state.buffered_stop_var.set(buffered_stop_freq_mhz)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to device '{device_name}': Center={center_freq_mhz:.3f} MHz, Span={format_hz(span_hz)}.")

        handle_freq_center_span_beg(app_instance=showtime_tab_instance.app_instance, center_freq=center_freq_hz, span_freq=span_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(False)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set(f"Device: {device_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Name: {device_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Center: {center_freq_mhz:.3f} MHz\nSpan: {span_mhz:.3f} MHz\nStart: {buffered_start_freq_mhz:.3f} MHz\nStop: {buffered_stop_freq_mhz:.3f} MHz")
        
        zone_zoom_tab._sync_ui_from_state()
        debug_log(message=f"🛠️ ✅ Successfully updated device span and UI.", file=current_file, version=current_version, function=current_function)

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_device: {e}")
        debug_log(message=f"🛠️ 🧨 It's madness! The device span function has gone haywire! The error is: {e}", file=current_file, version=current_version, function="set_span_to_device")

