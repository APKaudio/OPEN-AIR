# managers/Visa_Fleet_Manager/manager_visa_known_types.py
#
# Centralized knowledge base for known VISA instrument types and their notes.
#
# Author: Gemini Agent
#

# Maps Model Number -> {Type, Notes}
KNOWN_DEVICES = {
    "33220A": {"type": "generator", "notes": "20 MHz Arbitrary Waveform"},
    "33210A": {"type": "generator", "notes": "10 MHz Arbitrary Waveform"},
    "34401A": {"type": "dmm",   "notes": "6.5 Digit Benchtop Standard"},
    "54641D": {"type": "oscilloscope",       "notes": "Mixed Signal (2 Ana + 16 Dig)"},
    "DS1104Z": {"type": "oscilloscope",       "notes": "100 MHz, 4 Channel Digital"},
    "66000A": {"type": "power",    "notes": "Modular System (8 Slots)"},
    "66101A": {"type": "power",    "notes": "8V / 16A (128W)"},
    "66102A": {"type": "power",    "notes": "20V / 7.5A (150W)"},
    "66103A": {"type": "power",    "notes": "35V / 4.5A (150W)"},
    "66104A": {"type": "power",    "notes": "60V / 2.5A (150W)"},
    "6060B":  {"type": "load",    "notes": "DC Load (300 Watt)"},
    "3235":   {"type": "router",        "notes": "High-perf Switching Matrix"},
    "3235A":  {"type": "router",        "notes": "High-perf Switching Matrix"},
    "N9340B": {"type": "spectrum",  "notes": "Handheld (100 kHz - 3 GHz)"}
}
