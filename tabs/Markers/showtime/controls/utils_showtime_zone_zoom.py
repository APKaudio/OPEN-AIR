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

def set_span_to_all_markers(self, NumberOfMarkers, StartFreq, StopFreq, selected, buffer_mhz=0):
    # [Calculates the required span to view all markers and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_all_markers with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")
    try:
        # MODIFIED: Apply the buffer to the start and stop frequencies
        buffered_start_freq_mhz = StartFreq - buffer_mhz
        buffered_stop_freq_mhz = StopFreq + buffer_mhz
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to all markers: {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_all_markers: {e}")
        debug_log(f"Shiver me timbers, setting span to all markers has failed! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_all_markers")

def set_span_to_zone(self, ZoneName, NumberOfMarkers, StartFreq, StopFreq, selected, buffer_mhz=0):
    # [Calculates the required span for a zone and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_zone for Zone: {ZoneName} with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")
    try:
        # MODIFIED: Apply the buffer to the start and stop frequencies
        buffered_start_freq_mhz = StartFreq - buffer_mhz
        buffered_stop_freq_mhz = StopFreq + buffer_mhz
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to zone '{ZoneName}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_zone: {e}")
        debug_log(f"Arrr, the code be capsized! The error be: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_zone")

def set_span_to_group(self, GroupName, NumberOfMarkers, StartFreq, StopFreq, buffer_mhz=0):
    # [Calculates the required span for a group and sets the instrument using a start-stop command.]
    debug_log(f"Entering set_span_to_group for Group: {GroupName} with a buffer of {buffer_mhz} MHz.", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")
    try:
        # MODIFIED: Apply the buffer to the start and stop frequencies
        buffered_start_freq_mhz = StartFreq - buffer_mhz
        buffered_stop_freq_mhz = StopFreq + buffer_mhz
        
        start_freq_hz = int(buffered_start_freq_mhz * MHZ_TO_HZ)
        stop_freq_hz = int(buffered_stop_freq_mhz * MHZ_TO_HZ)
        self.console_print_func(f"✅ Setting span to group '{GroupName}': {buffered_start_freq_mhz:.3f} MHz to {buffered_stop_freq_mhz:.3f} MHz.")
        handle_freq_start_stop_beg(self.app_instance, start_freq_hz, stop_freq_hz, self.console_print_func)
    except Exception as e:
        console_log(f"❌ Error in set_span_to_group: {e}")
        debug_log(f"Great Scott! The group span calculation has failed! The error is: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="set_span_to_group")

def set_span_to_device(self, DeviceName, CenterFreq):


    
    def _update_zone_zoom_button_styles(self):
        # [Updates the visual styles of the zone zoom buttons based on current selection.]
        debug_log(f"Entering _update_zone_zoom_button_styles", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")
        active_style = 'ControlButton.Active.TButton'
        inactive_style = 'ControlButton.Inactive.TButton'
        
        try:
            zgd_frame = self.app_instance.tabs_parent.tab_content_frames['Markers'].showtime_tab.zgd_frame
            selected_type = zgd_frame.last_selected_type
            
            # Update 'All Markers' button
            is_all_active = selected_type is None
            self.zone_zoom_buttons['All'].configure(style=active_style if is_all_active else inactive_style)
            
            # Update 'Zone' button
            is_zone_active = selected_type == 'zone'
            self.zone_zoom_buttons['Zone'].configure(style=active_style if is_zone_active else inactive_style)

            # Update 'Group' button
            is_group_active = selected_type == 'group'
            self.zone_zoom_buttons['Group'].configure(style=active_style if is_group_active else inactive_style)
            
            # Update 'Device' button
            is_device_active = selected_type == 'device'
            self.zone_zoom_buttons['Device'].configure(style=active_style if is_device_active else inactive_style)
            
            # Enable/disable buttons based on selection
            self.zone_zoom_buttons['Zone'].configure(state='!disabled' if zgd_frame.selected_zone else 'disabled')
            self.zone_zoom_buttons['Group'].configure(state='!disabled' if zgd_frame.selected_group else 'disabled')
            self.zone_zoom_buttons['Device'].configure(state='!disabled' if zgd_frame.selected_device_info else 'disabled')
            
        except Exception as e:
            debug_log(f"A ghost has possessed the zone zoom buttons! Error: {e}", file=f"{os.path.basename(__file__)}", version=current_version, function="_update_zone_zoom_button_styles")

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