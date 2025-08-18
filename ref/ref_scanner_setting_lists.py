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
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250816.224500.1
# UPDATED: Rebuilt the PRESET_BANDWIDTH_VIDEO list with a correct handler value.

current_version = "20250816.224500.1" # this variable should always be defined below the header to make the debugging better

# --- UI Constants ---
MHZ_TO_HZ = 1_000_000  # Assumed constant for converting MHz to Hz

PRESET_AMPLITUDE_REFERENCE_LEVEL = [
    {
        "value": -120,
        "label": "Extremely Low",
        "description": "The lowest possible reference level for hunting the weakest signals imaginable.",
        "handler": "set_reference_level"
    },
    {
        "value": -115,
        "label": "Very Low",
        "description": "Deep noise floor — ideal for weak signal hunting.",
        "handler": "set_reference_level"
    },
    {
        "value": -110,
        "label": "Very Low",
        "description": "Deep noise floor — ideal for weak signal hunting.",
        "handler": "set_reference_level"
    },
    {
        "value": -105,
        "label": "Low",
        "description": "Below typical ambient RF noise — for sensitive receivers.",
        "handler": "set_reference_level"
    },
    {
        "value": -100,
        "label": "Low",
        "description": "Below typical ambient RF noise — for sensitive receivers.",
        "handler": "set_reference_level"
    },
    {
        "value": -95,
        "label": "Low",
        "description": "Below typical ambient RF noise — for sensitive receivers.",
        "handler": "set_reference_level"
    },
    {
        "value": -90,
        "label": "Low",
        "description": "Below typical ambient RF noise — for sensitive receivers.",
        "handler": "set_reference_level"
    },
    {
        "value": -85,
        "label": "Medium Low",
        "description": "Quiet environment, low-level signals clearly visible.",
        "handler": "set_reference_level"
    },
    {
        "value": -80,
        "label": "Medium Low",
        "description": "Quiet environment, low-level signals clearly visible.",
        "handler": "set_reference_level"
    },
    {
        "value": -75,
        "label": "Medium Low",
        "description": "Quiet environment, low-level signals clearly visible.",
        "handler": "set_reference_level"
    },
    {
        "value": -70,
        "label": "Medium Low",
        "description": "Quiet environment, low-level signals clearly visible.",
        "handler": "set_reference_level"
    },
    {
        "value": -65,
        "label": "Medium",
        "description": "Good general-purpose reference level.",
        "handler": "set_reference_level"
    },
    {
        "value": -60,
        "label": "Medium",
        "description": "Good general-purpose reference level.",
        "handler": "set_reference_level"
    },
    {
        "value": -55,
        "label": "Medium",
        "description": "Good general-purpose reference level.",
        "handler": "set_reference_level"
    },
    {
        "value": -50,
        "label": "Medium",
        "description": "Good general-purpose reference level.",
        "handler": "set_reference_level"
    },
    {
        "value": -45,
        "label": "Medium High",
        "description": "Stronger signals, moderate local RF traffic.",
        "handler": "set_reference_level"
    },
    {
        "value": -40,
        "label": "Medium High",
        "description": "Stronger signals, moderate local RF traffic.",
        "handler": "set_reference_level"
    },
    {
        "value": -35,
        "label": "Medium High",
        "description": "Stronger signals, moderate local RF traffic.",
        "handler": "set_reference_level"
    },
    {
        "value": -30,
        "label": "Medium High",
        "description": "Stronger signals, moderate local RF traffic.",
        "handler": "set_reference_level"
    },
    {
        "value": -25,
        "label": "High",
        "description": "For strong broadcast transmitters or test signals.",
        "handler": "set_reference_level"
    },
    {
        "value": -20,
        "label": "High",
        "description": "For strong broadcast transmitters or test signals.",
        "handler": "set_reference_level"
    },
    {
        "value": -15,
        "label": "High",
        "description": "For strong broadcast transmitters or test signals.",
        "handler": "set_reference_level"
    },
    {
        "value": -10,
        "label": "High",
        "description": "For strong broadcast transmitters or test signals.",
        "handler": "set_reference_level"
    },
    {
        "value": -5,
        "label": "Very High",
        "description": "Max headroom — use with caution to avoid clipping.",
        "handler": "set_reference_level"
    },
    {
        "value": 0,
        "label": "Very High",
        "description": "Max headroom — use with caution to avoid clipping.",
        "handler": "set_reference_level"
    }
]

PRESET_AMPLITUDE_PREAMP_STATE = [
    {
        "value": "ON",
        "label": "PREAMP ON",
        "description": "Turns on the pre-amplifier. A monstrous gain for weak signals.",
        "handler": "toggle_preamp"
    },
    {
        "value": "OFF",
        "label": "PREAMP OFF",
        "description": "Turns off the pre-amplifier. The scanner returns to its natural, less monstrous state.",
        "handler": "toggle_preamp"
    }
]

PRESET_AMPLITUDE_HIGH_SENSITIVITY_STATE = [
    {
        "value": "ON",
        "label": "HIGH SENSITIVITY ON",
        "description": "Activates high-sensitivity mode. The scanner now listens for the whispers of the universe.",
        "handler": "toggle_high_sensitivity"
    },
    {
        "value": "OFF",
        "label": "HIGH SENSITIVITY OFF",
        "description": "Deactivates high-sensitivity mode. The scanner's ears are no longer superhuman.",
        "handler": "toggle_high_sensitivity"
    }
]

PRESET_AMPLITUDE_POWER_ATTENUATION = [
    {
        "value": 0,
        "label": "0 dB",
        "description": "No attenuation. Full power! Use with caution.",
        "handler": "set_power_attenuation"
    },
    {
        "value": 10,
        "label": "10 dB",
        "description": "A light filter, for when the signal is just a bit too spicy.",
        "handler": "set_power_attenuation"
    },
    {
        "value": 20,
        "label": "20 dB",
        "description": "A good, solid filter for moderate signals.",
        "handler": "set_power_attenuation"
    },
    {
        "value": 30,
        "label": "30 dB",
        "description": "A strong filter for powerful signals. Like wearing sunglasses to the beach.",
        "handler": "set_power_attenuation"
    },
    {
        "value": 40,
        "label": "40 dB",
        "description": "A heavy filter for blaringly strong signals. It's like wearing a blindfold on a sunny day.",
        "handler": "set_power_attenuation"
    },
    {
        "value": 50,
        "label": "50 dB",
        "description": "Extreme attenuation for signals that could damage the instrument.",
        "handler": "set_power_attenuation"
    }

]

PRESET_BANDWIDTH_RBW = [
    {
        "value": 1_000_000,
        "label": "Fast",
        "description": "Like a race car: fast sweep, low detail. Best for catching fleeting signals.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 300_000,
        "label": "Brisk",
        "description": "A jog through the spectrum; quick enough to see the sights without missing much.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 100_000,
        "label": "Deliberate",
        "description": "The perfect balance of speed and fidelity. Not too fast, not too slow.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 30_000,
        "label": "Steady",
        "description": "A calm stroll, giving you time to appreciate the finer signal details.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 10_000,
        "label": "Leisurely",
        "description": "A slow saunter through the noise floor, where every waveform is a work of art.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 3_000,
        "label": "Unhurried",
        "description": "For the patient scientist. You'll see things nobody else can, but it'll take a while.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 1_000,
        "label": "Slothlike",
        "description": "So slow you can practically see the electrons move. The highest fidelity, but you'll miss any quick events.",
        "handler": "set_resolution_bandwidth"
    },
    {
        "value": 300,
        "label": "Slothlike",
        "description": "So slow you can practically see the electrons move. The highest fidelity, but you'll miss any quick events.",
        "handler": "set_resolution_bandwidth"
    },
]



PRESET_BANDWIDTH_VIDEO = [
    {
        "value": 1_000_000,
        "label": "Ultra Fast",
        "description": "A lightning-fast sweep. Filters are wide open, letting everything through.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 300_000,
        "label": "Very Fast",
        "description": "A quick pass through the spectrum, ideal for fast-changing signals.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 100_000,
        "label": "Fast",
        "description": "A balanced speed for general purpose monitoring and signal capture.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 30_000,
        "label": "Normal",
        "description": "The standard filter setting for most common analysis tasks. Not too much, not too little.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 10_000,
        "label": "Slow",
        "description": "A gentle filter, giving you more time to appreciate the finer details of a waveform.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 3_000,
        "label": "Very Slow",
        "description": "For the meticulous scientist. You'll filter out fast noise and jitter, but at the cost of speed.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 1_000,
        "label": "Ultra Slow",
        "description": "A meditative pace. So slow you can practically see the electrons move, offering maximum stability and noise reduction.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 300,
        "label": "Glacial",
        "description": "A slow crawl. Good for very detailed analysis of continuous signals and filtering out transient noise.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 100,
        "label": "Glacial",
        "description": "A slow crawl. Good for very detailed analysis of continuous signals and filtering out transient noise.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 30,
        "label": "Sub-Glacial",
        "description": "The scanner cries, but it's worth it. Filters out almost all random noise, giving you a crystal-clear, steady line.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 10,
        "label": "Sub-Glacial",
        "description": "The scanner cries, but it's worth it. Filters out almost all random noise, giving you a crystal-clear, steady line.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 3,
        "label": "Crazy Slow",
        "description": "Time seems to stop. For the most patient scientists and signals with incredible stability. The ultimate low-pass filter.",
        "handler": "set_video_bandwidth"
    },
    {
        "value": 1,
        "label": "Crazy Slow",
        "description": "Time seems to stop. For the most patient scientists and signals with incredible stability. The ultimate low-pass filter.",
        "handler": "set_video_bandwidth"
    },
]



# REVERSED ORDERING. This is the way.
PRESET_FREQUENCY_SPAN = [
    {
        "value": 10_000,
        "label": "Microscope",
        "description": "So tight you'll feel like a cellular biologist examining a single-cell waveform.",
        "handler": "set_span_frequency"
    },
    {
        "value": 100_000,
        "label": "Tight",
        "description": "A narrow, focused view for getting up close and personal with signals.",
        "handler": "set_span_frequency"
    },
    {
        "value": 1_000_000,
        "label": "Normal",
        "description": "The standard span, a balanced diet for most common analysis.",
        "handler": "set_span_frequency"
    },
    {
        "value": 10_000_000,
        "label": "Wide",
        "description": "A broad, digestible view of the spectrum, great for general reconnaissance.",
        "handler": "set_span_frequency"
    },
    {
        "value": 100_000_000,
        "label": "Ultra Wide",
        "description": "A very broad span for finding signals over a large frequency range. It's like scanning with a wide-angle lens.",
        "handler": "set_span_frequency"
    },
        {
        "value": 500_000_000,
        "label": "From Space",
        "description": "A very broad span for finding signals over a large frequency range. It's like scanning with a wide-angle lens.",
        "handler": "set_span_frequency"
    },
            {
        "value": 1_000_000_000,
        "label": "From The Moon",
        "description": "A very broad span for finding signals over a large frequency range. It's like scanning with a wide-angle lens.",
        "handler": "set_span_frequency"
    },
]

PRESET_TRACE_MODES = [
    {
        "value": "WRITE",
        "label": "LIVE REALTIME",
        "description": "Captures and displays the trace in real time, like a hyperactive surveillance camera.",
        "handler": "handle_trace_modes_beg"
    },
    {
        "value": "MAXHOLD",
        "label": "MAX HOLD",
        "description": "Keeps the highest-level peaks on display, like a digital trophy case for signals.",
        "handler": "handle_trace_modes_beg"
    },
    {
        "value": "MINHOLD",
        "label": "MIN HOLD",
        "description": "Holds onto the lowest points, great for detecting signals that vanish in the noise.",
        "handler": "handle_trace_modes_beg"
    },
    {
        "value": "BLANK",
        "label": "BLANK",
        "description": "Clears the slate, preparing for a new scan. A zen state for the scanner.",
        "handler": "handle_trace_modes_beg"
    },
    {
        "value": "VIEW",
        "label": "VIEW",
        "description": "The standard mode, simply viewing the current sweep data.",
        "handler": "handle_trace_modes_beg"
    },
]

PRESET_CONTINUOUS_MODE = [
    {
        "value": "ON",
        "label": "CONTINUOUS ON",
        "description": "Turns on continuous sweep mode. The scanner never rests!",
        "handler": "set_continuous_initiate_mode"
    },
    {
        "value": "OFF",
        "label": "CONTINUOUS OFF",
        "description": "Turns off continuous sweep mode. The scanner will perform a single sweep and then rest.",
        "handler": "set_continuous_initiate_mode"
    }
]
PRESET_AVERAGING = [
    {
        "value": 0,
        "label": "Off",
        "description": "Just a raw, single sweep. Great for seeing fast changes and fleeting events, but the noise floor is high and the trace is very jittery.",
        "handler": "set_averaging"
    },
    {
        "value": 5,
        "label": "Light Filter",
        "description": "A very mild smoothing of the signal, removing some of the jitter. It’s like putting a slight damper on the noise, making the trace a little easier to read.",
        "handler": "set_averaging"
    },
    {
        "value": 10,
        "label": "Getting Clear",
        "description": "The trace becomes noticeably less fuzzy. The random spikes of the noise floor start to settle down, revealing more consistent signals.",
        "handler": "set_averaging"
    },
    {
        "value": 25,
        "label": "The Sweet Spot",
        "description": "A good balance of noise reduction and display speed. The noise floor is clean, and low-level, stable signals are clearly visible.",
        "handler": "set_averaging"
    },
    {
        "value": 50,
        "label": "Steady Hands",
        "description": "The noise floor is now very stable and appears as a thin line. You’re only seeing the most consistent signals and cutting out most of the random interference.",
        "handler": "set_averaging"
    },
    {
        "value": 75,
        "label": "Deep Dive",
        "description": "This setting is for serious analysis. It's a highly stable trace that filters out a large portion of the ambient RF noise, allowing for precise measurements of continuous signals.",
        "handler": "set_averaging"
    },
    {
        "value": 100,
        "label": "Scientific Grade",
        "description": "For when only the cleanest signal will do. This high level of averaging provides a virtually noise-free display, perfect for scientific or very low-level signal detection. 🔬",
        "handler": "set_averaging"
    },
    {
        "value": 200,
        "label": "Crystal Clear",
        "description": "A deep and thorough look at the spectrum. All but the most stable signals are averaged out, offering a truly pristine view of the fundamental RF environment.",
        "handler": "set_averaging"
    },
    {
        "value": 500,
        "label": "The Observer",
        "description": "An incredibly slow and deliberate pace. This is for long-term monitoring, allowing you to see the overall shape of the spectrum with almost all noise removed.",
        "handler": "set_averaging"
    },
    {
        "value": 1000,
        "label": "Meditative Mode",
        "description": "For the patient and the meticulous. This is the ultimate level of noise reduction, yielding an exceptionally smooth and stable trace for the most demanding analysis. 🧘‍♂️",
        "handler": "set_averaging"
    }
]