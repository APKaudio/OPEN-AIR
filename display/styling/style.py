# styling/style.py
#
# Defines the color palettes for different UI themes, providing a centralized
# source for application-wide style configurations.
# This version corrects a SyntaxError caused by a leading zero in a numeric literal.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250823.212500.1

# Standard library import for the global variables.
import os

# --- Global Scope Variables ---
# The date of the chat session in YYYYMMDD format.
CURRENT_DATE = 20250823
# The time of the chat session in HHMMSS format.
CURRENT_TIME = 212500
# A numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 212500
# The revision number within the current session.
REVISION_NUMBER = 1
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250823.212500.1"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs.
current_file = f"{os.path.basename(__file__)}"

# THEMES is a dictionary that holds all our color palettes.
THEMES = {
    # The "dark" theme, inspired by dark IDE color schemes.
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#dcdcdc",
        "primary": "#3c3f41",
        "secondary": "#4e5254",
        "accent": "#cc5c00",
        "text": "#ffffff",
        "border": "#555555",
        "relief": "solid",
        "border_width": 0,
        "padding": 1,
        "tab_content_padding": 1,
        # --- New Styling Variables for Tables and Entries ---
        "table_bg": "#3c3f41",
        "table_fg": "#dcdcdc",
        "table_heading_bg": "#4e5254",
        "table_border": "#555555",
        "entry_bg": "#4e5254",
        "entry_fg": "#dcdcdc",
        # ----------------------------------------------------
        "accent_colors": [
            "#996633",  # 1. Brown
            "#c75450",  # 2. Red
            "#d18616",  # 3. Orange
            "#dcdcaa",  # 4. Yellow
            "#6a9955",  # 5. Green
            "#007acc",  # 6. Blue
            "#6464a3",  # 7. Violet
            "#ce9178",  # 8. Tan
            "#b5cea8",  # 9. Gray-Green
        ]
    },
    # The "light" theme, providing a high-contrast alternative.
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "primary": "#ffffff",
        "secondary": "#e0e0e0",
        "accent": "#0078d7",
        "text": "#000000",
        "border": "#ababab",
        "relief": "groove",
        "border_width": 0,
        "padding": 1,
        "tab_content_padding": 1,
        # --- New Styling Variables for Tables and Entries ---
        "table_bg": "#ffffff",
        "table_fg": "#000000",
        "table_heading_bg": "#e0e0e0",
        "table_border": "#ababab",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        # ----------------------------------------------------
        "accent_colors": [
            "#A0522D",  # 1. Brown (Sienna)
            "#D22B2B",  # 2. Red (Firebrick)
            "#FF8C00",  # 3. Orange (DarkOrange)
            "#FFD700",  # 4. Yellow (Gold)
            "#228B22",  # 5. Green (ForestGreen)
            "#4169E1",  # 6. Blue (RoyalBlue)
            "#8A2BE2",  # 7. Violet (BlueViolet)
            "#D2691E",  # 8. Tan (Chocolate)
            "#556B2F",  # 9. Gray-Green (DarkOliveGreen)
        ]
    }
}

# The default theme to use. This can be changed here to easily switch the entire application's style.
DEFAULT_THEME = "dark"