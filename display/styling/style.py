# styling/style.py
#
# Defines the color palettes for different UI themes, providing a centralized
# source for application-wide style configurations.
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
# Version 20250904.010551.1

import os

# --- Global Scope Variables ---
current_version = "20250904.010551.1"
current_version_hash = (20250904 * 10551 * 1)
current_file = f"{os.path.basename(__file__)}"

# The default theme to use. This can be changed here to easily switch the entire application's style.
DEFAULT_THEME = "dark"

# THEMES is a dictionary that holds all our color palettes.
THEMES = {
    # The "dark" theme, inspired by dark IDE color schemes.
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#dcdcdc",
        "fg_alt": "#888888",  # Added missing key for alternate/debug text
        "primary": "#3c3f41",
        "secondary": "#4e5254",
        "accent": "#cc5c00",
        "text": "#ffffff",
        "border": "#555555",
        "relief": "solid",
        "border_width": 0,
        "padding": 1,
        "tab_content_padding": 1,
        # --- Styling Variables for Tables and Entries ---
        "table_bg": "#3c3f41",
        "table_fg": "#dcdcdc",
        "table_heading_bg": "#4e5254",
        "table_border": "#555555",
        "entry_bg": "#4e5254",
        "entry_fg": "#dcdcdc",
        # ----------------------------------------------------
        "textbox_style": {
            "Textbox_Font": "Segoe UI",
            "Textbox_Font_size": 9,
            "Textbox_Font_colour": "#ffffff",
            "Textbox_border_colour": "#555555",
            "Textbox_BG_colour": "#4e5254"
        },
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
        "fg_alt": "#555555",  # Added missing key for alternate/debug text
        "primary": "#ffffff",
        "secondary": "#e0e0e0",
        "accent": "#0078d7",
        "text": "#000000",
        "border": "#ababab",
        "relief": "groove",
        "border_width": 0,
        "padding": 1,
        "tab_content_padding": 1,
        # --- Styling Variables for Tables and Entries ---
        "table_bg": "#ffffff",
        "table_fg": "#000000",
        "table_heading_bg": "#e0e0e0",
        "table_border": "#ababab",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        # ----------------------------------------------------
        "textbox_style": {
            "Textbox_Font": "Segoe UI",
            "Textbox_Font_size": 9,
            "Textbox_Font_colour": "#000000",
            "Textbox_border_colour": "#ababab",
            "Textbox_BG_colour": "#ffffff"
        },
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
