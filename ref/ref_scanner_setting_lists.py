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
# Version 20250802.1815.1 (Ensured all required dropdown lists are present and updated version.)

current_version = "20250802.1815.1" # this variable should always be defined below the header to make the debugging better

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

dwell_time_drop_down = [
    {
        "label": "Fast (0.1s)",
        "time_sec": 0.1,
        "description": "Quick sweeps, minimal dwell time."
    },
    {
        "label": "Normal (0.5s)",
        "time_sec": 0.5,
        "description": "Standard dwell for general purpose scanning."
    },
    {
        "label": "Medium (1s)",
        "time_sec": 1.0,
        "description": "Slightly longer dwell for more stable readings."
    },
    {
        "label": "Slow (2s)",
        "time_sec": 2.0,
        "description": "Extended dwell, good for capturing transient signals."
    },
    {
        "label": "Very Slow (5s)",
        "time_sec": 5.0,
        "description": "Maximum dwell, for detailed analysis of stable signals."
    }
]

cycle_wait_time_presets = [
    {
        "label": "None (0s)",
        "time_sec": 0,
        "description": "No wait time between scan cycles."
    },
    {
        "label": "Short (0.5s)",
        "time_sec": 0.5,
        "description": "A brief pause between cycles."
    },
    {
        "label": "Medium (1s)",
        "time_sec": 1.0,
        "description": "A moderate pause to allow for instrument settling."
    },
    {
        "label": "Long (2s)",
        "time_sec": 2.0,
        "description": "An extended pause for more stable measurements."
    },
    {
        "label": "Very Long (5s)",
        "time_sec": 5.0,
        "description": "A significant pause for critical measurements or external events."
    }
]

reference_level_drop_down = [
    {"label": "Auto", "level_dbm": "Auto", "description": "Automatically adjusts reference level."},
    {"label": "10 dBm", "level_dbm": 10, "description": "High signal levels."},
    {"label": "0 dBm", "level_dbm": 0, "description": "Common reference for many signals."},
    {"label": "-10 dBm", "level_dbm": -10, "description": "For slightly weaker signals."},
    {"label": "-20 dBm", "level_dbm": -20, "description": "For typical signal analysis."},
    {"label": "-30 dBm", "level_dbm": -30, "description": "For weaker signals."},
    {"label": "-40 dBm", "level_dbm": -40, "description": "For very weak signals."},
    {"label": "-50 dBm", "level_dbm": -50, "description": "For extremely weak signals."},
    {"label": "-60 dBm", "level_dbm": -60, "description": "For noise floor measurements."},
    {"label": "-70 dBm", "level_dbm": -70, "description": "Deep noise floor."},
    {"label": "-80 dBm", "level_dbm": -80, "description": "Ultra-low signal detection."},
    {"label": "-90 dBm", "level_dbm": -90, "description": "Near instrument noise floor."},
    {"label": "-100 dBm", "level_dbm": -100, "description": "Lowest measurable signal."}
]

frequency_shift_presets = [
    {"label": "None (0 Hz)", "shift_hz": 0, "description": "No frequency offset."},
    {"label": "100 kHz", "shift_hz": 100_000, "description": "100 kHz offset."},
    {"label": "1 MHz", "shift_hz": 1_000_000, "description": "1 MHz offset."},
    {"label": "10 MHz", "shift_hz": 10_000_000, "description": "10 MHz offset."},
    {"label": "Custom", "shift_hz": "Custom", "description": "Enter a custom frequency shift."}
]

number_of_scans_presets = [
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
        "description": "A wider filter, good for faster sweeps or broader signals."
    },
    {
        "label": "30 kHz",
        "rbw_hz": 30_000,
        "description": "General purpose RBW, common for many applications."
    },
    {
        "label": "100 kHz",
        "rbw_hz": 100_000,
        "description": "For wideband signals or very fast sweeps."
    },
    {
        "label": "300 kHz",
        "rbw_hz": 300_000,
        "description": "Very wide filter, for extremely fast scans or very broad signals."
    },
    {
        "label": "1 MHz",
        "rbw_hz": 1_000_000,
        "description": "Maximum RBW, for fastest possible sweeps, sacrificing resolution."
    }
]

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

frequency_shifts = [
    {"Value": 0, "Description": "0 Hz - No shift"},
    {"Value": 100000, "Description": "100 kHz shift"},
    {"Value": 1000000, "Description": "1 MHz shift"},
    {"Value": 10000000, "Description": "10 MHz shift"},
]

scan_modes = [
    {"Value": "NORMAL", "Description": "Normal sweep mode"},
    {"Value": "MAX_HOLD", "Description": "Max hold trace mode"},
    {"Value": "MIN_HOLD", "Description": "Min hold trace mode"},
]
