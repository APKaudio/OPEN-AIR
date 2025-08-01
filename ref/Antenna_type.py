# ref/Antenna_type.py
#
# This file contains a Python list of dictionaries, each describing a type of antenna.
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

antenna_types = [
    {
        "Type": "Omnidirectional (Dipole)",
        "Description": "Radiates and receives signals equally well in all horizontal directions. Simple and widely used.",
        "Use": "FM radio, Wi-Fi routers, short-range communication, general broadcasting."
    },
    {
        "Type": "Omnidirectional (Ground Plane)",
        "Description": "A vertical radiator with horizontal radials acting as a ground plane, providing omnidirectional coverage.",
        "Use": "VHF/UHF communication, amateur radio, base stations for mobile radio."
    },
    {
        "Type": "Directional (Yagi-Uda)",
        "Description": "Consists of a driven element, a reflector, and one or more directors. Highly directional with good gain.",
        "Use": "TV reception, amateur radio, point-to-point communication, long-distance communication."
    },
    {
        "Type": "Directional (Parabolic Dish)",
        "Description": "A large, curved reflector that focuses electromagnetic waves to or from a feed antenna at its focal point, providing very high gain and narrow beamwidth.",
        "Use": "Satellite communication, radar, radio astronomy, microwave links."
    },
    {
        "Type": "Loop Antenna",
        "Description": "A closed-loop conductor. Can be small (resonant) or large (non-resonant), with varying directional properties depending on size and configuration.",
        "Use": "AM radio reception, RFID, direction finding, amateur radio (especially for lower frequencies)."
    },
    {
        "Type": "Patch Antenna",
        "Description": "A flat, rectangular or circular metal patch mounted over a ground plane. Compact and low-profile.",
        "Use": "GPS devices, mobile phones, satellite communication, Wi-Fi access points."
    },
    {
        "Type": "Horn Antenna",
        "Description": "A flared metal waveguide, used for directing radio waves in a beam. High gain and good impedance matching.",
        "Use": "Microwave communication, radar, satellite tracking, measurement systems."
    }
]

# Example of how to access data:
# for antenna in antenna_types:
#     print(f"Type: {antenna['Type']}")
#     print(f"Description: {antenna['Description']}")
#     print(f"Use: {antenna['Use']}\n")
