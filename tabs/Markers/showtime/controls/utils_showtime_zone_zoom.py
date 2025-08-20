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
# Version 20250821.120300.3
# NEW: The utility functions now update the shared state variables for the UI labels
#      directly after calculation, centralizing the label update logic.
# REFACTORED: The logic now correctly handles the `update_labels` flag to prevent redundant
#             UI updates when called from other functions.
# FIXED: `set_span_to_device` now correctly uses the device's center frequency to set the instrument,
#        and the span is derived from the Span tab's current setting.
# FIXED: Corrected versioning to adhere to project standards.
# FIXED: All `set_span_to_...` functions now take only the `showtime_tab_instance` as a single argument
#        and retrieve all other required data from the shared state via that instance.

import inspect
import os
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ
from process_math.math_frequency_translation import format_hz

# Import the YakBeg handlers for direct instrument control
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

# --- Versioning ---
w = 20250821
x = 120300
y = 3
current_version = f"Version {w}.{x}.{y}"
current_version_hash = (w * x * y)
current_file = file=f"{os.path.basename(__file__)}"

def _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz):
    # [Calculates the buffered start and stop frequencies based on a given buffer value.]
    debug_log(f"Entering _buffer_start_stop_frequencies with start: {start_freq_mhz}, stop: {stop_freq_mhz}, buffer: {buffer_mhz}", file=f"{os.path.basename(__file__)}", version=current_version, function="_buffer_start_stop_frequencies")
    
    buffered_start_freq_mhz = start_freq_mhz - buffer_mhz
    buffered_stop_freq_mhz = stop_freq_mhz + buffer_mhz
    
    debug_log(f"Exiting _buffer_start_stop_frequencies with buffered start: {buffered_start_freq_mhz}, buffered stop: {buffered_stop_freq_mhz}", file=f"{os.path.basename(__file__)}", version=current_version, function="_buffer_start_stop_frequencies")
    
    return buffered_start_freq_mhz, buffered_stop_freq_mhz

def set_span_to_all_markers(showtime_tab_instance):
    # [Calculates the required span to view all markers and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"Entering {current_function}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")
    
    # Get necessary info from the shared state and zgd_frame
    all_devices = showtime_tab_instance.zgd_frame._get_all_devices_in_zone(showtime_tab_instance.zgd_frame.structured_data, None)
    
    if not all_devices:
        showtime_tab_instance.console_print_func("⚠️ No markers loaded. Cannot set span to all markers.")
        return
        
    freqs = [float(d['CENTER']) for d in all_devices if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
    if not freqs:
        showtime_tab_instance.console_print_func("⚠️ No valid frequencies found in markers. Cannot set span.")
        return
    
    start_freq_mhz = min(freqs)
    stop_freq_mhz = max(freqs)
    number_of_markers = len(freqs)

    try:
        buffer_mhz = 0
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to all markers: {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        
        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)

        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set("All Markers")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq_mhz:.3f} MHz ({number_of_markers} Devices)")
        
    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_all_markers: {e}")
        debug_log(f"Shiver me timbers, setting span to all markers has failed! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")

def set_span_to_zone(showtime_tab_instance):
    # [Calculates the required span for a zone and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    zone_name = showtime_tab_instance.shared_state.selected_zone
    if not zone_name:
        showtime_tab_instance.console_print_func("⚠️ No zone selected. Cannot set span to zone.")
        return

    # Get necessary info from the structured data
    all_devices_in_zone = showtime_tab_instance.zgd_frame._get_all_devices_in_zone(showtime_tab_instance.zgd_frame.structured_data, zone_name)
    freqs = [float(d['CENTER']) for d in all_devices_in_zone if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]
    
    if not freqs:
        showtime_tab_instance.console_print_func(f"⚠️ No valid frequencies found in zone '{zone_name}'. Cannot set span.")
        return
        
    start_freq_mhz = min(freqs)
    stop_freq_mhz = max(freqs)
    number_of_markers = len(freqs)
    
    debug_log(f"Entering {current_function} for Zone: {zone_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    try:
        buffer_mhz = 0
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to zone '{zone_name}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set(f"Zone: {zone_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq_mhz:.3f} MHz ({number_of_markers} Devices)")

        
    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_zone: {e}")
        debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")

def set_span_to_group(showtime_tab_instance):
    # [Calculates the required span for a group and sets the instrument using a start-stop command.]
    current_function = inspect.currentframe().f_code.co_name
    group_name = showtime_tab_instance.shared_state.selected_group
    zone_name = showtime_tab_instance.shared_state.selected_zone
    
    if not group_name:
        showtime_tab_instance.console_print_func("⚠️ No group selected. Cannot set span to group.")
        return
        
    devices_in_group = showtime_tab_instance.zgd_frame.structured_data.get(zone_name, {}).get(group_name, [])
    freqs = [float(d['CENTER']) for d in devices_in_group if d.get('CENTER') and isinstance(d.get('CENTER'), (int, float))]

    if not freqs:
        showtime_tab_instance.console_print_func(f"⚠️ No valid frequencies found in group '{group_name}'. Cannot set span.")
        return
    
    start_freq_mhz = min(freqs)
    stop_freq_mhz = max(freqs)
    number_of_markers = len(freqs)

    debug_log(f"Entering {current_function} for Group: {group_name}", file=f"{os.path.basename(__file__)}", version=current_version, function=current_function)
    try:
        buffer_mhz = 0
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        
        showtime_tab_instance.console_print_func(f"✅ Setting span to group '{group_name}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(app_instance=showtime_tab_instance.app_instance, start_freq=start_freq_hz, stop_freq=stop_freq_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(True)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set(f"Group: {group_name}")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Start: {buffered_start_freq_mhz:.3f} MHz")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Stop: {buffered_stop_freq_mhz:.3f} MHz ({number_of_markers} Devices)")

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_group: {e}")
        debug_log(f"Great Scott! The group span calculation has failed! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")
        
def set_span_to_device(showtime_tab_instance):
    # [Sets the instrument's span to focus on a single device using a center-span command.]
    current_function = inspect.currentframe().f_code.co_name
    device_info = showtime_tab_instance.shared_state.selected_device_info
    
    if not device_info:
        showtime_tab_instance.console_print_func("⚠️ No device selected. Cannot set span to device.")
        return

    device_name = device_info.get('NAME')
    center_freq_mhz = device_info.get('CENTER')
    
    debug_log(f"Entering {current_function} for Device: {device_name}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")
    try:
        buffer_mhz = 0
        center_freq_hz = int(center_freq_mhz * MHZ_TO_HZ)
        span_hz = int(float(showtime_tab_instance.shared_state.span_var.get()))
        
        # Calculate start and stop with the buffer for display purposes
        buffered_span = span_hz / MHZ_TO_HZ + (2 * buffer_mhz)
        start = center_freq_mhz - (buffered_span / 2)
        stop = center_freq_mhz + (buffered_span / 2)

        showtime_tab_instance.console_print_func(f"✅ Setting span to device '{device_name}': Center={center_freq_mhz:.3f} MHz, Span={format_hz(span_hz)}.")
        handle_freq_center_span_beg(app_instance=showtime_tab_instance.app_instance, center_freq=center_freq_hz, span_freq=span_hz, console_print_func=showtime_tab_instance.console_print_func)
        
        showtime_tab_instance.shared_state.follow_zone_span_var.set(False)

        showtime_tab_instance.shared_state.zone_zoom_label_left_var.set("Device:")
        showtime_tab_instance.shared_state.zone_zoom_label_center_var.set(f"Start: {start:.3f} MHz")
        showtime_tab_instance.shared_state.zone_zoom_label_right_var.set(f"Stop: {stop:.3f} MHz ({device_name})")

    except Exception as e:
        showtime_tab_instance.console_print_func(f"❌ Error in set_span_to_device: {e}")
        debug_log(f"It's madness! The device span function has gone haywire! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")