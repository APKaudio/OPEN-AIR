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
# Version 20250818.214500.1

current_version = "20250818.214500.1"
current_version_hash = (20250818 * 214500 * 1)

import inspect
import os
from display.debug_logic import debug_log
from display.console_logic import console_log
from ref.frequency_bands import MHZ_TO_HZ


def format_hz(hz_value):
    """
    Formats a frequency in Hz to a human-readable string (e.g., 1.2M, 300k, 50Hz).
    """
    try:
        hz_value = float(hz_value)
        if hz_value >= 1_000_000:
            return f"{hz_value / 1_000_000:.1f}M"
        elif hz_value >= 1_000:
            return f"{hz_value / 1_000:.0f}k"
        else:
            return f"{hz_value}Hz"
    except (ValueError, TypeError):
        return "N/A"



# Import the YakBeg handlers for direct instrument control
from yak.utils_yakbeg_handler import handle_freq_start_stop_beg, handle_freq_center_span_beg

def set_span_to_all_markers(self, NumberOfMarkers, StartFreq, StopFreq, selected):
    # [Calculates the required span to view all markers and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_all_markers", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")
    try:
        start_freq_hz = int(StartFreq * MHZ_TO_HZ)
        stop_freq_hz = int(StopFreq * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to all markers: {StartFreq:.3f} MHz to {StopFreq:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_all_markers: {e}")
        debug_log(f"Shiver me timbers, setting span to all markers has failed! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")

def set_span_to_zone(self, ZoneName, NumberOfMarkers, StartFreq, StopFreq, selected):
    # [Calculates the required span for a zone and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_zone for Zone: {ZoneName}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")
    try:
        start_freq_hz = int(StartFreq * MHZ_TO_HZ)
        stop_freq_hz = int(StopFreq * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to zone '{ZoneName}': {StartFreq:.3f} MHz to {StopFreq:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_zone: {e}")
        debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")

def set_span_to_group(self, GroupName, NumberOfMarkers, StartFreq, StopFreq):
    # [Calculates the required span for a group and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_group for Group: {GroupName}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")
    try:
        start_freq_hz = int(StartFreq * MHZ_TO_HZ)
        stop_freq_hz = int(StopFreq * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to group '{GroupName}': {StartFreq:.3f} MHz to {StopFreq:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_group: {e}")
        debug_log(f"Great Scott! The group span calculation has failed! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")

def set_span_to_device(self, DeviceName, CenterFreq):
    # [Sets the instrument's span to focus on a single device using a center-span command.]
    debug_log(f"Entering set_span_to_device for Device: {DeviceName}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")
    try:
        center_freq_hz = int(CenterFreq * MHZ_TO_HZ)
        span_hz = int(float(self.span_var.get()))
        self.console_print_func(f"✅ Setting span to device '{DeviceName}': Center={CenterFreq:.3f} MHz, Span={format_hz(span_hz)}.")
        handle_freq_center_span_beg(self.app_instance, center_freq_hz, span_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_device: {e}")
        debug_log(f"It's madness! The device span function has gone haywire! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_device")