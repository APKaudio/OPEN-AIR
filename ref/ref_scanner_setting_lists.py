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
# Version 20250815.151240.13
# REFACTOR: Moved presets without handlers to a new file, ref_scanning_setting.py.

current_version = "20250815.151240.13" # this variable should always be defined below the header to make the debugging better

# --- UI Constants ---
MHZ_TO_HZ = 1_000_000  # Assumed constant for converting MHz to Hz

PRESET_SWEEP_TIME = [
    {
        "value": 0.5,
        "label": "Crazy Fast",
        "description": "Blink and you’ll miss it. Best for wideband sweeps with minimal detail.",
        "handler": "set_sweep_time" 
    },
    {
        "value": 1.0,
        "label": "Very Fast",
        "description": "Great for active scanning with basic detection.",
        "handler": "set_sweep_time"
    },
    {
        "value": 2.0,
        "label": "Standard",
        "description": "Balanced scan — enough time for most signals to show.",
        "handler": "set_sweep_time"
    },
    {
        "value": 3.0,
        "label": "Long",
        "description": "Allows time to catch short bursts or weak signals.",
        "handler": "set_sweep_time"
    },
    {
        "value": 5.0,
        "label": "Very Long",
        "description": "Camped out. Good for quiet bands or deep listening.",
        "handler": "set_sweep_time"
    },
    {
        "value": 10.0,
        "label": "Glacier Mode",
        "description": "For scientists, spies, and patient people. 🧊",
        "handler": "set_sweep_time"
    }
]
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
]

PRESET_FREQUENCY_SPAN = [
    {
        "value": 100_000_000,
        "label": "Ultra Wide",
        "description": "A very broad span for finding signals over a large frequency range. It's like scanning with a wide-angle lens.",
        "handler": "set_span_frequency"
    },
    {
        "value": 10_000_000,
        "label": "Wide",
        "description": "A broad, digestible view of the spectrum, great for general reconnaissance.",
        "handler": "set_span_frequency"
    },
    {
        "value": 1_000_000,
        "label": "Normal",
        "description": "The standard span, a balanced diet for most common analysis.",
        "handler": "set_span_frequency"
    },
    {
        "value": 100_000,
        "label": "Tight",
        "description": "A narrow, focused view for getting up close and personal with signals.",
        "handler": "set_span_frequency"
    },
    {
        "value": 10_000,
        "label": "Microscope",
        "description": "So tight you'll feel like a cellular biologist examining a single-cell waveform.",
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
