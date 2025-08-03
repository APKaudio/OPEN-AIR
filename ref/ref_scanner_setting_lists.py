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
# Version 20250803.183035.0 (Standardized all data structures to use 'label', 'value', 'description' keys.)


current_version = "20250803.183035.0" # this variable should always be defined below the header to make the debugging better

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
        "description": "Standard definition TV of frequency."
    },
    {
        "label": "Medium Well",
        "value": 25_000,
        "description": "Almost gourmet, but still quick-cook."
    },
    {
        "label": "High",
        "value": 10_000,
        "description": "RF with Wi-Fi smoothness."
    },
    {
        "label": "Ultra High",
        "value": 5_000,
        "description": "Retina display for radio."
    },
    {
        "label": "Ludacris",
        "value": 1_000,
        "description": "So fine, even Ludacris said “Damn.”"
    },
    {
        "label": "Ridonkulous",
        "value": 500,
        "description": "“I can see the atoms in your waveform.”"
    },
    {
        "label": "Quantum Foam",
        "value": 100,
        "description": "Where reality and noise floor blur."
    },
    {
        "label": "This is Fine",
        "value": 10,
        "description": "The scanner cries, but it's worth it. 🔥"
    }
]

dwell_time_drop_down = [
    {
        "label": "Crazy Fast",
        "value": 0.5,
        "description": "Blink and you’ll miss it. Best for wideband sweeps with minimal detail."
    },
    {
        "label": "Very Fast",
        "value": 1.0,
        "description": "Great for active scanning with basic detection."
    },
    {
        "label": "Standard",
        "value": 2.0,
        "description": "Balanced scan — enough time for most signals to show."
    },
    {
        "label": "Long",
        "value": 3.0,
        "description": "Allows time to catch short bursts or weak signals."
    },
    {
        "label": "Very Long",
        "value": 5.0,
        "description": "Camped out. Good for quiet bands or deep listening."
    },
    {
        "label": "Glacier Mode",
        "value": 10.0,
        "description": "For scientists, spies, and patient people. 🧊"
    }
]

cycle_wait_time_presets = [
    {
        "label": "Hold Your Horses",
        "value": 15,
        "description": "Just a moment — enough time to sneeze twice."
    },
    {
        "label": "Wait-a-Second",
        "value": 30,
        "description": "Half a minute of suspense. Elevator music optional."
    },
    {
        "label": "Microwave Dinner",
        "value": 60,
        "description": "One full minute — perfect for impatient people."
    },
    {
        "label": "Coffee Break",
        "value": 300,
        "description": "Five minutes — time to stretch or grab caffeine."
    },
    {
        "label": "Quarter of Shame",
        "value": 900,
        "description": "15 minutes of contemplation. Or buffering."
    },
    {
        "label": "Netflix Warmup",
        "value": 1800,
        "description": "30 minutes — just long enough to not commit to a show."
    },
    {
        "label": "Full Commitment",
        "value": 3600,
        "description": "1 hour — a true test of patience and faith in the process."
    },
    {
        "label": "Eternal Watcher",
        "value": 10800,
        "description": "3 hours — were you expecting a callback?"
    }
]

reference_level_drop_down = [
    {
        "label": "Very Low",
        "value": -110,
        "description": "Deep noise floor — ideal for weak signal hunting."
    },
    {
        "label": "Low",
        "value": -90,
        "description": "Below typical ambient RF noise — for sensitive receivers."
    },
    {
        "label": "Medium Low",
        "value": -70,
        "description": "Quiet environment, low-level signals clearly visible."
    },
    {
        "label": "Medium",
        "value": -50,
        "description": "Good general-purpose reference level."
    },
    {
        "label": "Medium High",
        "value": -30,
        "description": "Stronger signals, moderate local RF traffic."
    },
    {
        "label": "High",
        "value": -10,
        "description": "For strong broadcast transmitters or test signals."
    },
    {
        "label": "Very High",
        "value": 0,
        "description": "Max headroom — use with caution to avoid clipping."
    }
]

frequency_shift_presets = [
    {
        "label": "No Shift",
        "value": 0,
        "description": "don't touch that dial — stay put."
    },
    {
        "label": "A Wee Bit",
        "value": 1_000,
        "description": "Just a nudge — like adjusting your hat slightly."
    },
    {
        "label": "A Nudge",
        "value": 5_000,
        "description": "A gentle push up or down the dial."
    },
    {
        "label": "A Whap",
        "value": 10_000,
        "description": "Noticeable thump — not subtle, not wild."
    },
    {
        "label": "A Scooch",
        "value": 25_000,
        "description": "Just enough to dodge interference or hop channels."
    },
    {
        "label": "A Chunk",
        "value": 50_000,
        "description": "A meaty move — shift the neighborhood."
    },
    {
        "label": "A Jump",
        "value": 100_000,
        "description": "You're not walking anymore — you're airborne."
    },
    {
        "label": "A Leap",
        "value": 250_000,
        "description": "Covering ground like a gazelle on caffeine."
    },
    {
        "label": "A Yeet",
        "value": 500_000,
        "description": "Full send across the spectrum — no regrets."
    },
    {
        "label": "A Warp",
        "value": 1_000_000,
        "description": "Fold space and reappear in another RF galaxy."
    }
]

number_of_scans_presets = [
    {
        "label": "Just a Test",
        "value": 1,
        "description": "See how she goes — one and done."
    },
    {
        "label": "A Whiff",
        "value": 2,
        "description": "A quick sniff around the spectrum."
    },
    {
        "label": "A Bunch",
        "value": 10,
        "description": "Enough to get a good feel."
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
        "description": "Standard resolution for general-purpose scanning."
    },
    {
        "label": "30 kHz",
        "value": 30_000,
        "description": "Faster scan, suitable for wider signals or quicker sweeps."
    },
    {
        "label": "100 kHz",
        "value": 100_000,
        "description": "Fastest resolution, good for wideband signals or quick spectrum overviews."
    }
]