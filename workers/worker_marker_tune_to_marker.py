# workers/worker_marker_tune_to_marker.py
#
# This worker module contains the logic for tuning an instrument to a selected marker's
# frequency. It handles the necessary data conversion and MQTT communication.
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
# Version 20250922.150000.1
import os
import inspect
import sys

# --- Module Imports ---
from workers.worker_logging import debug_log, console_log

# --- Global Scope Variables ---
current_version = "20250922.150000.1"
current_version_hash = (20250922 * 150000 * 1)
current_file = os.path.basename(__file__)

def Push_Marker_to_Center_Freq(mqtt_controller, marker_data):
    """
    Publishes MQTT messages to set the instrument's center frequency and span
    based on a selected marker, and then triggers the SCPI command.
    
    Args:
        mqtt_controller: The MQTT controller instance for publishing messages.
        marker_data (dict): A dictionary containing the selected marker's data.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(
        message="🛠️🟢 Received request to tune to marker. Processing data...",
        file=current_file,
        version=current_version,
        function=f"{current_function}",
        console_print_func=console_log
    )

    try:
        # Define the MQTT topics as constants
        CENTER_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_inputs/center_freq/"
        SPAN_FREQ_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_inputs/span_freq/"
        TRIGGER_TOPIC = "OPEN-AIR/repository/yak/Frequency/beg/Beg_freq_center_span/scpi_details/generic_model/trigger"
        
        default_span = 1e6 # 1 MHz
        
        # Get frequency from marker data and convert from MHz to Hz
        freq_mhz = marker_data.get('FREQ (MHZ)', None)
        if freq_mhz is None:
            debug_log(
                message="❌🔴 Error: Marker data is missing the 'FREQ (MHZ)' key.",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            console_log("❌ Failed to tune: Marker data is incomplete.")
            return

        # Handle potential string to float conversion issues
        try:
            freq_mhz = float(freq_mhz)
            center_freq_hz = freq_mhz * 1e6
        except (ValueError, TypeError) as e:
            debug_log(
                message=f"❌🔴 Error converting frequency to float: {e}",
                file=current_file,
                version=current_version,
                function=f"{current_function}",
                console_print_func=console_log
            )
            console_log("❌ Failed to tune: Invalid frequency value.")
            return

        debug_log(
            message=f"🔍 Freq from marker: {freq_mhz} MHz -> {center_freq_hz} Hz.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )

        # Set center frequency
        mqtt_controller.publish_message(topic=CENTER_FREQ_TOPIC, value=center_freq_hz)
        console_log(f"✅ Set CENTER_FREQ to {center_freq_hz} Hz.")
        
        # Set span frequency (default is 1 MHz)
        mqtt_controller.publish_message(topic=SPAN_FREQ_TOPIC, value=default_span)
        console_log(f"✅ Set SPAN_FREQ to {default_span} Hz.")
        
        # Trigger SCPI command
        mqtt_controller.publish_message(topic=TRIGGER_TOPIC, value=True)
        debug_log(
            message="🛠️🔵 Trigger set to True. Awaiting instrument response.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        
        # Reset the trigger
        mqtt_controller.publish_message(topic=TRIGGER_TOPIC, value=False)
        debug_log(
            message="🛠️🔵 Trigger reset to False. Command sequence complete.",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        
        console_log("✅ Tuning command sequence complete.")

    except Exception as e:
        debug_log(
            message=f"❌🔴 Critical error during marker tuning: {e}",
            file=current_file,
            version=current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        console_log(f"❌ An error occurred while tuning to the marker: {e}")