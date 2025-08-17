# ref/ref_scanning_setting.py
#
# This file contains predefined lists of settings that are primarily used
# for UI configuration and do not have a direct handler for instrument control.
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
# NEW: Created a new file to house UI-specific scanner presets.

current_version = "20250815.151240.13" # this variable should always be defined below the header to make the debugging better

PRESET_DISPLAY_GRAPH_QUALITY = [
    {
        "value": 1_000_000,
        "label": "Ultra Low",
        "description": "Blocky enough to be Minecraft.",
        "handler": None
    },
    {
        "value": 100_000,
        "label": "Low",
        "description": "VHS quality RF — nostalgic but fuzzy.",
        "handler": None
    },
    {
        "value": 50_000,
        "label": "Medium",
        "description": "Standard definition TV of frequency.",
        "handler": None
    },
    {
        "value": 25_000,
        "label": "Medium Well",
        "description": "Almost gourmet, but still quick-cook.",
        "handler": None
    },
    {
        "value": 10_000,
        "label": "High",
        "description": "RF with Wi-Fi smoothness.",
        "handler": None
    },
    {
        "value": 5_000,
        "label": "Ultra High",
        "description": "Retina display for radio.",
        "handler": None
    },
    {
        "value": 1_000,
        "label": "Ludacris",
        "description": "So fine, even Ludacris said “Damn.”",
        "handler": None
    },
    {
        "value": 500,
        "label": "Ridonkulous",
        "description": "“I can see the atoms in your waveform.”",
        "handler": None
    },
    {
        "value": 100,
        "label": "Quantum Foam",
        "description": "Where reality and noise floor blur.",
        "handler": None
    },
    {
        "value": 10,
        "label": "This is Fine",
        "description": "The scanner cries, but it's worth it. 🔥",
        "handler": None
    }
]

PRESET_CYCLE_WAIT_TIME = [
    {
        "value": 15,
        "label": "Hold Your Horses",
        "description": "Just a moment — enough time to sneeze twice.",
        "handler": None
    },
    {
        "value": 30,
        "label": "Wait-a-Second",
        "description": "Half a minute of suspense. Elevator music optional.",
        "handler": None
    },
    {
        "value": 60,
        "label": "Microwave Dinner",
        "description": "One full minute — perfect for impatient people.",
        "handler": None
    },
    {
        "value": 300,
        "label": "Coffee Break",
        "description": "Five minutes — time to stretch or grab caffeine.",
        "handler": None
    },
    {
        "value": 900,
        "label": "Quarter of Shame",
        "description": "15 minutes of contemplation. Or buffering.",
        "handler": None
    },
    {
        "value": 1800,
        "label": "Netflix Warmup",
        "description": "30 minutes — just long enough to not commit to a show.",
        "handler": None
    },
    {
        "value": 3600,
        "label": "Full Commitment",
        "description": "1 hour — a true test of patience and faith in the process.",
        "handler": None
    },
    {
        "value": 10800,
        "label": "Eternal Watcher",
        "description": "3 hours — were you expecting a callback?",
        "handler": None
    }
]

PRESET_FREQUENCY_SHIFT = [
    {
        "value": 0,
        "label": "No Shift",
        "description": "don't touch that dial — stay put.",
        "handler": None
    },
    {
        "value": 1_000,
        "label": "A Wee Bit",
        "description": "Just a nudge — like adjusting your hat slightly.",
        "handler": None
    },
    {
        "value": 5_000,
        "label": "A Nudge",
        "description": "A gentle push up or down the dial.",
        "handler": None
    },
    {
        "value": 10_000,
        "label": "A Whap",
        "description": "Noticeable thump — not subtle, not wild.",
        "handler": None
    },
    {
        "value": 25_000,
        "label": "A Scooch",
        "description": "Just enough to dodge interference or hop channels.",
        "handler": None
    },
    {
        "value": 50_000,
        "label": "A Chunk",
        "description": "A meaty move — shift the neighborhood.",
        "handler": None
    },
    {
        "value": 100_000,
        "label": "A Jump",
        "description": "You're not walking anymore — you're airborne.",
        "handler": None
    },
    {
        "value": 250_000,
        "label": "A Leap",
        "description": "Covering ground like a gazelle on caffeine.",
        "handler": None
    },
    {
        "value": 500_000,
        "label": "A Yeet",
        "description": "Full send across the spectrum — no regrets.",
        "handler": None
    },
    {
        "value": 1_000_000,
        "label": "A Warp",
        "description": "Fold space and reappear in another RF galaxy.",
        "handler": None
    }
]

PRESET_NUMBER_OF_SCANS = [
    {
        "value": 1,
        "label": "Just a Test",
        "description": "See how she goes — one and done.",
        "handler": None
    },
    {
        "value": 2,
        "label": "A Whiff",
        "description": "A quick sniff around the spectrum.",
        "handler": None
    },
    {
        "value": 10,
        "label": "A Bunch",
        "description": "Enough to get a good feel.",
        "handler": None
    },
    {
        "value": 50,
        "label": "A Bushel",
        "description": "A good harvest of data.",
        "handler": None
    },
    {
        "value": 75,
        "label": "A Shwack",
        "description": "A hefty pile — things are serious now.",
        "handler": None
    },
    {
        "value": 100,
        "label": "A Ton",
        "description": "A solid chunk of scanning.",
        "handler": None
    },
    {
        "value": 1_000,
        "label": "A Tone",
        "description": "A big, noisy tone of scans.",
        "handler": None
    },
    {
        "value": 99_999_999,
        "label": "Never-Ending Story",
        "description": "Until you say stop or the program crashes spectacularly.",
        "handler": None
    }
]

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