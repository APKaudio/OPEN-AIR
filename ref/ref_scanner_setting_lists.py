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
# Version 20250802.0700.1 (Moved scan_modes into this file from its own module.)

current_version = "20250802.0700.1" # this variable should always be defined below the header to make the debugging better

graph_quality_drop_down = [
    {
        "label": "Ultra Low",
        "resolution_hz": 1_000_000,
        "description": "Blocky enough to be Minecraft."
    },
    {
        "label": "Low",
        "resolution_hz": 100_000,
        "description": "VHS quality RF — nostalgic but fuzzy."
    },
    {
        "label": "Medium",
        "resolution_hz": 50_000,
        "description": "A decent balance of speed and detail."
    },
    {
        "label": "High",
        "resolution_hz": 10_000,
        "description": "Crisp and clear, like a freshly pressed suit."
    },
    {
        "label": "Ultra High",
        "resolution_hz": 1_000,
        "description": "Every pixel counts. For the detail-obsessed."
    }
]

num_scan_cycles_drop_down = [
    {
        "label": "Single Shot",
        "scans": 1,
        "description": "One and done — quick and dirty."
    },
    {
        "label": "A Few",
        "scans": 5,
        "description": "Just enough to get a feel for it."
    },
    {
        "label": "A Handful",
        "scans": 10,
        "description": "Getting serious now."
    },
    {
        "label": "A Dozen",
        "scans": 12,
        "description": "A baker's dozen of data."
    },
    {
        "label": "A Score",
        "scans": 20,
        "description": "A good solid number."
    },
    {
        "label": "A Bushel",
        "scans": 50,
        "description": "A good harvest of data."
    },
    {
        "label": "A Shwack",
        "scans": 75,
        "description": "A hefty pile — things are serious now."
    },
    {
        "label": "A Ton",
        "scans": 100,
        "description": "A solid chunk of scanning."
    },
    {
        "label": "A Tone",
        "scans": 1_000,
        "description": "A big, noisy tone of scans."
    },
    {
        "label": "Never-Ending Story",
        "scans": 99_999_999,
        "description": "Until you say stop or the program crashes spectacularly."
    }
]

# NEW: Placeholder for rbw_presets
rbw_presets = [
    {
        "label": "SLOW",
        "rbw_hz": 1_000,
        "description": "Very fine resolution, for distinguishing closely spaced signals. Slowest scan."
    },
    {
        "label": "3 kHz",
        "rbw_hz": 3_000,
        "description": "Good for narrow-band signals like voice communications."
    },
    {
        "label": "10 kHz",
        "rbw_hz": 10_000,
        "description": "Standard resolution for general purpose measurements."
    },
    {
        "label": "30 kHz",
        "rbw_hz": 30_000,
        "description": "Faster scan, good for wider signals or quicker sweeps."
    },
    {
        "label": "100 kHz",
        "rbw_hz": 100_000,
        "description": "Even faster, useful for broad signals or spectrum overview."
    },
    {
        "label": "FAST",
        "rbw_hz": 300_000,
        "description": "Quickest scan, for capturing transient signals or very wide-band analysis."
    }
]

# NEW: Scan Modes (moved from ref/scan_modes.py)
scan_modes = [
    {"Mode": "Swept", "Description": "Standard swept measurement, good for general purpose spectrum analysis."},
    {"Mode": "FFT", "Description": "Fast Fourier Transform for real-time analysis, ideal for capturing intermittent signals."},
    {"Mode": "Zero Span", "Description": "Time domain analysis at a fixed frequency, useful for observing signal stability over time."},
]

# Reference Levels (moved from ref/reference_levels.py)
reference_levels = [
    {"Level": 0, "Description": "0 dBm"},
    {"Level": -10, "Description": "-10 dBm"},
    {"Level": -20, "Description": "-20 dBm"},
    {"Level": -30, "Description": "-30 dBm"},
    {"Level": -40, "Description": "-40 dBm"},
    {"Level": -50, "Description": "-50 dBm"},
    {"Level": -60, "Description": "-60 dBm"},
    {"Level": -70, "Description": "-70 dBm"},
    {"Level": -80, "Description": "-80 dBm"},
    {"Level": -90, "Description": "-90 dBm"},
    {"Level": -100, "Description": "-100 dBm"},
]

# Attenuation Levels (moved from ref/attenuation_levels.py)
attenuation_levels = [
    {"Value": 0, "Description": "0 dB - No attenuation"},
    {"Value": 5, "Description": "5 dB attenuation"},
    {"Value": 10, "Description": "10 dB attenuation"},
    {"Value": 15, "Description": "15 dB attenuation"},
    {"Value": 20, "Description": "20 dB attenuation"},
    {"Value": 25, "Description": "25 dB attenuation"},
    {"Value": 30, "Description": "30 dB attenuation"},
    {"Value": 35, "Description": "35 dB attenuation"},
    {"Value": 40, "Description": "40 dB attenuation"},
    {"Value": 45, "Description": "45 dB attenuation"},
    {"Value": 50, "Description": "50 dB attenuation"},
]

# Frequency Shifts (moved from ref/frequency_shifts.py)
frequency_shifts = [
    {"Shift": 0, "Description": "0 MHz - No frequency shift"},
    {"Shift": 0.5, "Description": "0.5 MHz shift"},
    {"Shift": 1, "Description": "1 MHz shift"},
    {"Shift": 5, "Description": "5 MHz shift"},
    {"Shift": 10, "Description": "10 MHz shift"},
    {"Shift": 20, "Description": "20 MHz shift"},
    {"Shift": 50, "Description": "50 MHz shift"},
    {"Shift": 100, "Description": "100 MHz shift"},
]
