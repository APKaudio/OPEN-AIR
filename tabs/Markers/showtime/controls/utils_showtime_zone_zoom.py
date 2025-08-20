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
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250821.005500.1
# NEW: Added a dedicated function `_buffer_start_stop_frequencies` to handle buffering logic.
# FIXED: All `set_span_to...` functions were updated to correctly use the buffer,
#        access the `span_var` from the parent, and pass the correct instance.

current_version = "20250821.005500.1"
current_version_hash = (20250821 * 5500 * 1)

import inspect
import os
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ
from process_math.math_frequency_translation import format_hz

# Import the YakBeg handlers for direct instrument control
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

def _buffer_start_stop_frequencies(start_freq_mhz, stop_freq_mhz, buffer_mhz):
    # [Calculates the buffered start and stop frequencies based on a given buffer value.]
    debug_log(f"Entering _buffer_start_stop_frequencies with start: {start_freq_mhz}, stop: {stop_freq_mhz}, buffer: {buffer_mhz}", file=f"{os.path.basename(__file__)}", version=current_version, function="_buffer_start_stop_frequencies")
    
    buffered_start_freq_mhz = start_freq_mhz - buffer_mhz
    buffered_stop_freq_mhz = stop_freq_mhz + buffer_mhz
    
    debug_log(f"Exiting _buffer_start_stop_frequencies with buffered start: {buffered_start_freq_mhz}, buffered stop: {buffered_stop_freq_mhz}", file=f"{os.path.basename(__file__)}", version=current_version, function="_buffer_start_stop_frequencies")
    
    return buffered_start_freq_mhz, buffered_stop_freq_mhz

def set_span_to_all_markers(zone_zoom_tab_instance, NumberOfMarkers, StartFreq, StopFreq, selected, buffer_mhz=0):
    # [Calculates the required span to view all markers and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_all_markers with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")
    try:
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(StartFreq, StopFreq, buffer_mhz)
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        zone_zoom_tab_instance.controls_frame.console_print_func(f"✅ Setting span to all markers: {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        
        handle_freq_start_stop_beg(zone_zoom_tab_instance.controls_frame.app_instance, start_freq_hz, stop_freq_hz, zone_zoom_tab_instance.controls_frame.console_print_func)

        zone_zoom_tab_instance.controls_frame.follow_zone_span_var.set(True)
    except Exception as e:
        zone_zoom_tab_instance.controls_frame.console_print_func(f"❌ Error in set_span_to_all_markers: {e}")
        debug_log(f"Shiver me timbers, setting span to all markers has failed! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")

def set_span_to_zone(zone_zoom_tab_instance, ZoneName, NumberOfMarkers, StartFreq, StopFreq, selected, buffer_mhz=0):
    # [Calculates the required span for a zone and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_zone for Zone: {ZoneName} with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")
    try:
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(StartFreq, StopFreq, buffer_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        zone_zoom_tab_instance.controls_frame.console_print_func(f"✅ Setting span to zone '{ZoneName}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(zone_zoom_tab_instance.controls_frame.app_instance, start_freq_hz, stop_freq_hz, zone_zoom_tab_instance.controls_frame.console_print_func)
        
        zone_zoom_tab_instance.controls_frame.follow_zone_span_var.set(True)
    except Exception as e:
        zone_zoom_tab_instance.controls_frame.console_print_func(f"❌ Error in set_span_to_zone: {e}")
        debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")

def set_span_to_group(zone_zoom_tab_instance, GroupName, NumberOfMarkers, StartFreq, StopFreq, buffer_mhz=0):
    # [Calculates the required span for a group and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_group for Group: {GroupName} with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")
    try:
        buffered_start_freq_mhz, buffered_stop_freq_mhz = _buffer_start_stop_frequencies(StartFreq, StopFreq, buffer_mhz)

        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        zone_zoom_tab_instance.controls_frame.console_print_func(f"✅ Setting span to group '{GroupName}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(zone_zoom_tab_instance.controls_frame.app_instance, start_freq_hz, stop_freq_hz, zone_zoom_tab_instance.controls_frame.console_print_func)
        
        zone_zoom_tab_instance.controls_frame.follow_zone_span_var.set(True)
    except Exception as e:
        zone_zoom_tab_instance.controls_frame.console_print_func(f"❌ Error in set_span_to_group: {e}")
        debug_log(f"Great Scott! The group span calculation has failed! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")

def set_span_to_device(zone_zoom_tab_instance, DeviceName, CenterFreq):
    # [Sets the instrument's span to focus on a single device using a center-span command.]
    debug_log(f"Entering set_span_to_device for Device: {DeviceName}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")
    try:
        center_freq_hz = int(CenterFreq * MHZ_TO_HZ)
        span_hz = int(float(zone_zoom_tab_instance.controls_frame.span_var.get()))
        zone_zoom_tab_instance.controls_frame.console_print_func(f"✅ Setting span to device '{DeviceName}': Center={CenterFreq:.3f} MHz, Span={format_hz(span_hz)}.")
        handle_freq_center_span_beg(zone_zoom_tab_instance.controls_frame.app_instance, center_freq_hz, span_hz, zone_zoom_tab_instance.controls_frame.console_print_func)
        
        zone_zoom_tab_instance.controls_frame.follow_zone_span_var.set(False)
    except Exception as e:
        zone_zoom_tab_instance.controls_frame.console_print_func(f"❌ Error in set_span_to_device: {e}")
        debug_log(f"It's madness! The device span function has gone haywire! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")