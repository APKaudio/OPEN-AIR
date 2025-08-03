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
        "value": 50_000,
        "description": "A decent balance of speed and detail."
    },
    {
        "label": "High",
        "value": 10_000,
        "description": "Crisp and clear, like a freshly pressed suit."
    },
    {
        "label": "Ultra High",
        "value": 1_000,
        "description": "Every pixel counts. For the detail-obsessed."
    }
]

dwell_time_drop_down = [
    {
        "label": "Fast (0.1s)",
        "value": 0.1,
        "description": "Quick sweeps, minimal dwell time."
    },
    {
        "label": "Normal (0.5s)",
        "value": 0.5,
        "description": "Standard dwell for general purpose scanning."
    },
    {
        "label": "Medium (1s)",
        "value": 1.0,
        "description": "Slightly longer dwell for more stable readings."
    },
    {
        "label": "Slow (2s)",
        "value": 2.0,
        "description": "Extended dwell, good for capturing transient signals."
    },
    {
        "label": "Very Slow (5s)",
        "value": 5.0,
        "description": "Maximum dwell, for detailed analysis of stable signals."
    }
]

cycle_wait_time_presets = [
    {
        "label": "None (0s)",
        "value": 0,
        "description": "No wait time between scan cycles."
    },
    {
        "label": "Short (0.5s)",
        "value": 0.5,
        "description": "A brief pause between cycles."
    },
    {
        "label": "Medium (1s)",
        "value": 1.0,
        "description": "A moderate pause to allow for instrument settling."
    },
    {
        "label": "Long (2s)",
        "value": 2.0,
        "description": "An extended pause for more stable measurements."
    },
    {
        "label": "Very Long (5s)",
        "value": 5.0,
        "description": "A significant pause for critical measurements or external events."
    }
]

reference_level_drop_down = [
    {"label": "Auto", "value": "Auto", "description": "Automatically adjusts reference level."},
    {"label": "10 dBm", "value": 10, "description": "High signal levels."},
    {"label": "0 dBm", "value": 0, "description": "Common reference for many signals."},
    {"label": "-10 dBm", "value": -10, "description": "For slightly weaker signals."},
    {"label": "-20 dBm", "value": -20, "description": "For typical signal analysis."},
    {"label": "-30 dBm", "value": -30, "description": "For weaker signals."},
    {"label": "-40 dBm", "value": -40, "description": "For very weak signals."},
    {"label": "-50 dBm", "value": -50, "description": "For extremely weak signals."},
    {"label": "-60 dBm", "value": -60, "description": "For noise floor measurements."},
    {"label": "-70 dBm", "value": -70, "description": "Deep noise floor."},
    {"label": "-80 dBm", "value": -80, "description": "Ultra-low signal detection."},
    {"label": "-90 dBm", "value": -90, "description": "Near instrument noise floor."},
    {"label": "-100 dBm", "value": -100, "description": "Lowest measurable signal."}
]

frequency_shift_presets = [
    {"label": "None (0 Hz)", "value": 0, "description": "No frequency offset."},
    {"label": "100 kHz", "value": 100_000, "description": "100 kHz offset."},
    {"label": "1 MHz", "value": 1_000_000, "description": "1 MHz offset."},
    {"label": "10 MHz", "value": 10_000_000, "description": "10 MHz offset."},
    {"label": "Custom", "value": "Custom", "description": "Enter a custom frequency shift."}
]

number_of_scans_presets = [
    {
        "label": "Single Shot",
        "value": 1,
        "description": "One and done — quick and dirty."
    },
    {
        "label": "A Few",
        "value": 5,
        "description": "Just enough to get a feel for it."
    },
    {
        "label": "A Handful",
        "value": 10,
        "description": "Getting serious now."
    },
    {
        "label": "A Dozen",
        "value": 12,
        "description": "A baker's dozen of data."
    },
    {
        "label": "A Score",
        "value": 20,
        "description": "A good solid number."
    },
    {
        "label": "A Bushel",
        "value": 50,
        "description": "A good harvest of data."
    },
    {
        "label": "A Shwack",
        "value": 75,
        "description": "A hefty pile — things are serious now."
    },
    {
        "label": "A Ton",
        "value": 100,
        "description": "A solid chunk of scanning."
    },
    {
        "label": "A Tone",
        "value": 1_000,
        "description": "A big, noisy tone of scans."
    },
    {
        "label": "Never-Ending Story",
        "value": 99_999_999,
        "description": "Until you say stop or the program crashes spectacularly."
    }
]

rbw_presets = [
    {
        "label": "SLOW",
        "value": 1_000,
        "description": "Very fine resolution, for distinguishing closely spaced signals. Slowest scan."
    },
    {
        "label": "3 kHz",
        "value": 3_000,
        "description": "Good for narrow-band signals like voice communications."
    },
    {
        "label": "10 kHz",
        "value": 10_000,
        "description": "A wider filter, good for faster sweeps or broader signals."
    },
    {
        "label": "30 kHz",
        "value": 30_000,
        "description": "General purpose RBW, common for many applications."
    },
    {
        "label": "100 kHz",
        "value": 100_000,
        "description": "For wideband signals or very fast sweeps."
    },
    {
        "label": "300 kHz",
        "value": 300_000,
        "description": "Very wide filter, for extremely fast scans or very broad signals."
    },
    {
        "label": "1 MHz",
        "value": 1_000_000,
        "description": "Maximum RBW, for fastest possible sweeps, sacrificing resolution."
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
    {"label": "100 kHz", "value": 100000, "description": "100 kHz shift"},
    {"label": "1 MHz", "value": 1000000, "description": "1 MHz shift"},
    {"label": "10 MHz", "value": 10000000, "description": "10 MHz shift"},
]

scan_modes = [
    {"label": "Normal", "value": "NORMAL", "description": "Normal sweep mode"},
    {"label": "Max Hold", "value": "MAX_HOLD", "description": "Max hold trace mode"},
    {"label": "Min Hold", "value": "MIN_HOLD", "description": "Min hold trace mode"},
]