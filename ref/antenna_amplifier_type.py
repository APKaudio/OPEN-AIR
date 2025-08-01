# ref/antenna_amplifier_type.py
#
# This file contains a Python list of dictionaries, each describing a type of antenna amplifier.
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
# Version 1.0 (Initial version)

antenna_amplifier_types = [
    {
        "Type": "In-line Amplifier (Line Amplifier)",
        "Description": "Designed to boost signal strength directly in the cable run, often near the antenna or at various points in a long cable.",
        "Use": "Compensating for cable loss, boosting weak signals before they reach the receiver or distribution system."
    },
    {
        "Type": "Mast-Mounted Amplifier (Preamplifier)",
        "Description": "Installed as close as possible to the antenna (e.g., on the mast) to amplify weak signals before noise is added by the cable or receiver. Often includes filtering.",
        "Use": "Improving signal-to-noise ratio for very weak signals, especially in TV or radio reception, or for remote sensing applications."
    },
    {
        "Type": "Distribution Amplifier (Booster)",
        "Description": "Used to split and amplify a signal for distribution to multiple outlets or devices, ensuring adequate signal strength at each point.",
        "Use": "Home TV systems (multiple TVs from one antenna), large building distribution networks, commercial AV systems."
    },
    {
        "Type": "Broadband Amplifier",
        "Description": "Amplifies signals across a wide range of frequencies without significant filtering, useful for multi-band applications.",
        "Use": "General purpose signal boosting, systems where multiple frequency bands need amplification simultaneously."
    },
    {
        "Type": "Band-Specific Amplifier",
        "Description": "Designed to amplify signals only within a specific frequency band, often incorporating built-in filters to reject out-of-band interference.",
        "Use": "Targeted amplification for specific TV channels, cellular bands, or radio services, where interference from other bands is a concern."
    },
    {
        "Type": "Low Noise Amplifier (LNA)",
        "Description": "A type of amplifier designed to amplify very low-power signals without significantly degrading the signal-to-noise ratio. Typically used at the very front end of a receiver.",
        "Use": "Satellite receivers, radio astronomy, high-sensitivity communication systems, GPS."
    },
    {
        "Type": "Power Amplifier (PA)",
        "Description": "Designed to increase the power of a signal, typically for transmission. It's the final stage before the antenna in a transmitter.",
        "Use": "Radio transmitters, cellular base stations, radar systems, broadcast stations."
    }
]

# Example of how to access data:
# for amplifier in antenna_amplifier_types:
#     print(f"Type: {amplifier['Type']}")
#     print(f"Description: {amplifier['Description']}")
#     print(f"Use: {amplifier['Use']}\n")
