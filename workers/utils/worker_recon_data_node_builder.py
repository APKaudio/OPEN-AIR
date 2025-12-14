# workers/recon_data_publisher.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


# A script to generate and publish MQTT topics from a CSV file,
# simulating a detailed frequency scan for the 'Recon' module.
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
# Version 20250901.195300.3

import os
import inspect
import datetime
import csv
import json
import time
import re

# --- Module Imports ---
from workers.mqtt.worker_mqtt_controller_util import MqttControllerUtility
from display.logger import debug_log, console_log, log_visa_command
import workers.utils.worker_project_paths

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 3
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"
Local_Debug_Enable = True

# --- Constants ---
MQTT_ROOT_TOPIC = "OPEN-AIR/recon"
CSV_FILE_PATH = workers.worker_project_paths.GLOBAL_PROJECT_ROOT / "DATA" / "ThisIsMyScan_RBW10K_HOLD3_Offset0_20250729_091431.csv"


def recon_data_publisher(mqtt_util_instance, console_log_func):
    """
    Reads frequency and amplitude data from a CSV file and publishes it to
    MQTT topics with a predefined hierarchical structure.
    """
    current_function_name = inspect.currentframe().f_code.co_name
    if Local_Debug_Enable:
        debug_log(
            message=f"🛠️🟢 Entering '{current_function_name}' to begin publishing data from CSV.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log_func
        )

    try:
        if not mqtt_util_instance:
            console_log_func("❌ MQTT utility instance is not available. Cannot publish topics.")
            return
            
        if not os.path.exists(CSV_FILE_PATH):
            console_log_func(f"❌ Error: CSV file not found at '{CSV_FILE_PATH}'.")
            return

        with open(CSV_FILE_PATH, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # Skip the header row if it exists
            header_row = next(csv_reader, None)
            if header_row and not re.match(r'^\d', header_row[0]):
                 console_log_func("ℹ️ Skipping CSV header row.")
            else:
                # If there's no header, reset the reader to the start of the file
                csv_file.seek(0)
            
            i = 0
            for row in csv_reader:
                try:
                    freq_mhz = float(row[0])
                    value_dbm = float(row[1])
                    
                    # Calculate frequency components directly from MHz
                    ghz = int(freq_mhz // 1000)
                    mhz_remainder = freq_mhz % 1000
                    
                    # Breakdown MHz into hundreds, tens, and ones
                    mhz_hundreds = int(mhz_remainder // 100)
                    mhz_tens = int((mhz_remainder % 100) // 10)
                    mhz_ones = int(mhz_remainder % 10)
                    
                    # Breakdown kHz into hundreds, tens, and ones
                    khz_total = int(round((mhz_remainder - int(mhz_remainder)) * 1000, 0))
                    khz_hundreds = int(khz_total // 100)
                    khz_tens = int((khz_total % 100) // 10)
                    khz_ones = int(khz_total % 10)
                    
                    # Construct the topic in an ordered sequence
                    topic_path = f"GHz/{ghz}/Mhz/{mhz_hundreds}/{mhz_tens}/{mhz_ones}/khz/{khz_hundreds}/{khz_tens}/{khz_ones}"
                    full_topic = f"{MQTT_ROOT_TOPIC}/{topic_path}"

                    # Generate the JSON payload
                    payload = {
                        "Value": value_dbm,
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Device": 0
                    }

                    # Publish the message with the retain flag set to True
                    mqtt_util_instance.publish_message(
                        topic=full_topic,
                        subtopic="",
                        value=json.dumps(payload),
                        retain=True
                    )
                    
                    i += 1

                    # Display progress every 1000 messages
                    if i % 1000 == 0:
                        console_log_func(f"🔵 Progress: {i} topics published from CSV.")
                
                except (ValueError, IndexError) as e:
                    console_log_func(f"❌ Error processing row: {row}. Skipping. Error: {e}")
                    continue

        console_log_func(f"✅ Celebration of success! Published {i} topics from '{CSV_FILE_PATH}'.")

    except Exception as e:
        console_log_func(f"❌ Error in {current_function_name}: {e}")
        if Local_Debug_Enable:
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=current_function_name,
                console_print_func=console_log_func
            )

# Example Usage
if __name__ == "__main__":
    # In a real application, MqttControllerUtility would be passed from a parent
    # For this example, we'll create a mock utility that just prints to console
    class MockMqttUtility:
        def publish_message(self, topic, subtopic, value, retain=False):
            full_topic = f"{topic}/{subtopic}" if subtopic else topic
            console_log(f"Published (Retain={retain}) Topic: {full_topic}\nPayload: {value}\n")

    mock_mqtt_util = MockMqttUtility()
    recon_data_publisher(mock_mqtt_util, console_log)