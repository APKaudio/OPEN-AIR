# ref/ref_scanner_setting_lists.py
#
# This file contains predefined lists of settings for various scanner parameters.
# These lists are used to populate dropdown menus in the GUI, providing users
# with a selection of common or recommended values along with descriptive text.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 20250802.2015.1 (Standardized data structures to use 'label', 'value', and 'description'.)
# Version 20250803.1820.0 (ADDED: Missing dropdown lists for instrument settings.)
# Version 20250803.1830.0 (ADDED: Display functions for each dropdown list and placeholder lists.)

current_version = "20250802.2015.1" # this variable should always be defined below the header to make the debugging better


graph_quality_drop_down = [
    {
        "label": "Ultra Low",
        "value": 1_000_000,
        "description": "Blocky enough to be Minecraft."
    },
    {
        "label": "Low",
        "value": 100_000,
        "description": "VHS quality RF — nostalgic but fuzzy."
    },
    {
        "label": "Medium",
        "value": 10_000,
        "description": "Standard definition, good balance of detail and speed."
    },
    {
        "label": "High",
        "value": 1_000,
        "description": "High definition RF — crisp and clear."
    },
    {
        "label": "Ultra High",
        "value": 100,
        "description": "4K RF — every detail, but takes time."
    }
]

attenuation_levels = [
    {"label": "0 dB", "value": 0, "description": "No attenuation"},
    {"label": "5 dB", "value": 5, "description": "5 dB attenuation"},
    {"label": "10 dB", "value": 10, "description": "10 dB attenuation"},
    {"label": "15 dB", "value": 15, "description": "15 dB attenuation"},
    {"label": "20 dB", "value": 20, "description": "20 dB attenuation"},
    {"label": "25 dB", "value": 25, "description": "25 dB attenuation"},
    {"label": "30 dB", "value": 30, "description": "30 dB attenuation"},
    {"label": "35 dB", "value": 35, "description": "35 dB attenuation"},
    {"label": "40 dB", "value": 40, "description": "40 dB attenuation"},
    {"label": "45 dB", "value": 45, "description": "45 dB attenuation"},
    {"label": "50 dB", "value": 50, "description": "50 dB attenuation"},
]

frequency_shifts = [
    {"label": "0 Hz", "value": 0, "description": "No shift"},
    {"label": "100 kHz", "value": 100000, "description": "100 kHz frequency shift"},
    {"label": "200 kHz", "value": 200000, "description": "200 kHz frequency shift"},
    {"label": "500 kHz", "value": 500000, "description": "500 kHz frequency shift"},
    {"label": "1 MHz", "value": 1000000, "description": "1 MHz frequency shift"},
    {"label": "5 MHz", "value": 5000000, "description": "5 MHz frequency shift"},
    {"label": "10 MHz", "value": 10000000, "description": "10 MHz frequency shift"},
]

# --- NEW DROPDOWN LISTS FOR INSTRUMENT SETTINGS ---

ref_level_drop_down = [
    {"label": "-10 dBm", "value": -10.0, "description": "Reference level at -10 dBm."},
    {"label": "-20 dBm", "value": -20.0, "description": "Reference level at -20 dBm."},
    {"label": "-30 dBm", "value": -30.0, "description": "Reference level at -30 dBm."},
    {"label": "-40 dBm", "value": -40.0, "description": "Reference level at -40 dBm."},
    {"label": "-50 dBm", "value": -50.0, "description": "Reference level at -50 dBm."},
    {"label": "0 dBm", "value": 0.0, "description": "Reference level at 0 dBm."},
    {"label": "10 dBm", "value": 10.0, "description": "Reference level at 10 dBm."},
]

rbw_drop_down = [
    {"label": "10 Hz", "value": 10.0, "description": "Resolution Bandwidth: 10 Hz."},
    {"label": "100 Hz", "value": 100.0, "description": "Resolution Bandwidth: 100 Hz."},
    {"label": "1 kHz", "value": 1000.0, "description": "Resolution Bandwidth: 1 kHz."},
    {"label": "10 kHz", "value": 10000.0, "description": "Resolution Bandwidth: 10 kHz."},
    {"label": "100 kHz", "value": 100000.0, "description": "Resolution Bandwidth: 100 kHz."},
    {"label": "1 MHz", "value": 1000000.0, "description": "Resolution Bandwidth: 1 MHz."},
]

span_drop_down = [
    {"label": "10 kHz", "value": 0.01, "description": "Span: 10 kHz."},
    {"label": "100 kHz", "value": 0.1, "description": "Span: 100 kHz."},
    {"label": "1 MHz", "value": 1.0, "description": "Span: 1 MHz."},
    {"label": "10 MHz", "value": 10.0, "description": "Span: 10 MHz."},
    {"label": "100 MHz", "value": 100.0, "description": "Span: 100 MHz."},
    {"label": "1 GHz", "value": 1000.0, "description": "Span: 1 GHz."},
]

center_freq_drop_down = [
    {"label": "100 MHz", "value": 100.0, "description": "Center Frequency: 100 MHz."},
    {"label": "500 MHz", "value": 500.0, "description": "Center Frequency: 500 MHz."},
    {"label": "1 GHz", "value": 1000.0, "description": "Center Frequency: 1 GHz."},
    {"label": "2.4 GHz", "value": 2400.0, "description": "Center Frequency: 2.4 GHz."},
    {"label": "5.8 GHz", "value": 5800.0, "description": "Center Frequency: 5.8 GHz."},
]

preamp_drop_down = [
    {"label": "On", "value": True, "description": "Preamplifier is enabled."},
    {"label": "Off", "value": False, "description": "Preamplifier is disabled."},
]

high_sensitivity_drop_down = [
    {"label": "On", "value": True, "description": "High sensitivity mode is enabled."},
    {"label": "Off", "value": False, "description": "High sensitivity mode is disabled."},
]

trace_mode_drop_down = [
    {"label": "Clear Write", "value": "WRIT", "description": "Trace mode: Clear Write."},
    {"label": "Max Hold", "value": "MAXH", "description": "Trace mode: Max Hold."},
    {"label": "Min Hold", "value": "MINH", "description": "Trace mode: Min Hold."},
    {"label": "Average", "value": "AVER", "description": "Trace mode: Average."},
    {"label": "View", "value": "VIEW", "description": "Trace mode: View."},
]

display_scale_drop_down = [
    {"label": "10 dB/div", "value": 10.0, "description": "Display scale: 10 dB per division."},
    {"label": "5 dB/div", "value": 5.0, "description": "Display scale: 5 dB per division."},
    {"label": "2 dB/div", "value": 2.0, "description": "Display scale: 2 dB per division."},
    {"label": "1 dB/div", "value": 1.0, "description": "Display scale: 1 dB per division."},
]

sweep_time_drop_down = [
    {"label": "Auto", "value": "AUTO", "description": "Sweep time: Automatic."},
    {"label": "10 ms", "value": 0.01, "description": "Sweep time: 10 milliseconds."},
    {"label": "100 ms", "value": 0.1, "description": "Sweep time: 100 milliseconds."},
    {"label": "1 s", "value": 1.0, "description": "Sweep time: 1 second."},
    {"label": "10 s", "value": 10.0, "description": "Sweep time: 10 seconds."},
]

data_format_drop_down = [
    {"label": "ASCII", "value": "ASC", "description": "Data format: ASCII."},
    {"label": "Binary", "value": "REAL", "description": "Data format: Binary (Real)."},
]

# --- Placeholder lists for functions requested by user ---
dwell_time_drop_down = [
    {"label": "10 ms", "value": 0.01, "description": "Dwell time: 10 milliseconds."},
    {"label": "100 ms", "value": 0.1, "description": "Dwell time: 100 milliseconds."},
    {"label": "1 s", "value": 1.0, "description": "Dwell time: 1 second."},
    {"label": "Auto", "value": "AUTO", "description": "Dwell time: Automatic."},
]
  
cycle_wait_time_presets = [
    {"label": "0.1 s", "value": 0.1, "description": "Wait 0.1 seconds between cycles."},
    {"label": "0.5 s", "value": 0.5, "description": "Wait 0.5 seconds between cycles."},
    {"label": "1 s", "value": 1.0, "description": "Wait 1 second between cycles."},
    {"label": "5 s", "value": 5.0, "description": "Wait 5 seconds between cycles."},
]

number_of_scans_presets = [
    {"label": "1 Cycle", "value": 1, "description": "Perform 1 scan cycle."},
    {"label": "5 Cycles", "value": 5, "description": "Perform 5 scan cycles."},
    {"label": "10 Cycles", "value": 10, "description": "Perform 10 scan cycles."},
    {"label": "Continuous", "value": 0, "description": "Perform scans continuously."},
]

scan_modes = [
    {"label": "Sweep", "value": "SWEEP", "description": "Perform a standard frequency sweep."},
    {"label": "Zero Span", "value": "ZSP", "description": "Perform a zero span measurement."},
    {"label": "Power Meter", "value": "PMET", "description": "Operate as a power meter."},
]


# --- Functions to display content of dropdown lists ---

def display_graph_quality_drop_down():
    """
    Prints the content of graph_quality_drop_down in a readable format.
    """
    print("\n--- GRAPH QUALITY OPTIONS ---")
    for item in graph_quality_drop_down:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_dwell_time_drop_down():
    """
    Prints the content of dwell_time_drop_down in a readable format.
    """
    print("\n--- DWELL TIME OPTIONS ---")
    for item in dwell_time_drop_down:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_cycle_wait_time_presets():
    """
    Prints the content of cycle_wait_time_presets in a readable format.
    """
    print("\n--- CYCLE WAIT TIME PRESETS ---")
    for item in cycle_wait_time_presets:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_reference_level_drop_down():
    """
    Prints the content of ref_level_drop_down (renamed from reference_level_drop_down) in a readable format.
    """
    print("\n--- REFERENCE LEVEL OPTIONS ---")
    for item in ref_level_drop_down:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_frequency_shift_presets():
    """
    Prints the content of frequency_shifts (renamed from frequency_shift_presets) in a readable format.
    """
    print("\n--- FREQUENCY SHIFT PRESETS ---")
    for item in frequency_shifts:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_number_of_scans_presets():
    """
    Prints the content of number_of_scans_presets in a readable format.
    """
    print("\n--- NUMBER OF SCANS PRESETS ---")
    for item in number_of_scans_presets:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_rbw_presets():
    """
    Prints the content of rbw_drop_down (renamed from rbw_presets) in a readable format.
    """
    print("\n--- RBW PRESETS ---")
    for item in rbw_drop_down:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_attenuation_levels():
    """
    Prints the content of attenuation_levels in a readable format.
    """
    print("\n--- ATTENUATION LEVELS ---")
    for item in attenuation_levels:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_frequency_shifts():
    """
    Prints the content of frequency_shifts in a readable format.
    """
    print("\n--- FREQUENCY SHIFTS ---")
    for item in frequency_shifts:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")

def display_scan_modes():
    """
    Prints the content of scan_modes in a readable format.
    """
    print("\n--- SCAN MODES ---")
    for item in scan_modes:
        print(f"Label: {item['label']}, Value: {item['value']}, Description: {item['description']}")
