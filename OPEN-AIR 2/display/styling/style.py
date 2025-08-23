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
# Version 20250822.210500.1

# 📚 Standard library import for the global variables.
import os

# --- Global Scope Variables ---
# W: The date of the chat session in YYYYMMDD format.
CURRENT_DATE = 20250822
# X: The time of the chat session in HHMMSS format.
CURRENT_TIME = 210500
# A numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 210500
# Y: The revision number within the current session.
REVISION_NUMBER = 1
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250822.210500.1"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs.
current_file = f"{os.path.basename(__file__)}"

# 🎨 THEMES is a dictionary that holds all our color palettes.
THEMES = {
    # 🌑 The "dark" theme, inspired by dark IDE color schemes.
    "dark": {
        # "bg" (background): The main, default background color for the application.
        "bg": "#2b2b2b",
        # "fg" (foreground): The main, default text color for most elements.
        "fg": "#686868",
        # "primary": The background color for major containers and frames.
        "primary": "#3c3f41",
        # "secondary": A slightly lighter background color for nested containers or inactive tabs.
        "secondary": "#4e5254",
        # "accent": A bright color used for interactive elements like buttons and selected tabs.
        "accent": "#007acc",
        # "text": The color for text that appears on an accent color background.
        "text": "#ffffff",
        # "border": The color of borders around widgets and containers.
        "border": "#555555",
        # "relief": The style of the border, 'solid' works well with dark themes.
        "relief": "solid",
        # "border_width": The width of the border in pixels.
        "border_width": 1,
        # "padding": A base value for spacing around widgets.
        "padding": 1,
        # "tab_content_padding": Padding specifically for the content inside a tab.
        "tab_content_padding": 1,
        # "accent_colors": A list of colors for a dynamic accent palette, for use in graphs or custom widgets.
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
    # 🌞 The "light" theme, providing a high-contrast alternative.
    "light": {
        # "bg" (background): A light gray background for the overall application.
        "bg": "#f0f0f0",
        # "fg" (foreground): Black text for high readability.
        "fg": "#000000",
        # "primary": A clean white background for main content areas.
        "primary": "#ffffff",
        # "secondary": A lighter gray for minor elements or inactive tabs.
        "secondary": "#e0e0e0",
        # "accent": A vibrant blue for interactive elements.
        "accent": "#0078d7",
        # "text": A standard black for text on the accent color.
        "text": "#000000",
        # "border": A neutral gray for borders.
        "border": "#ababab",
        # "relief": The border style, 'groove' gives a slightly indented, classic look.
        "relief": "groove",
        # "border_width": The width of the border.
        "border_width": 1,
        # "padding": A base value for spacing.
        "padding": 1,
        # "tab_content_padding": Padding for content inside a tab.
        "tab_content_padding": 1,
        # "accent_colors": A separate list of vibrant colors for graphs and dynamic elements in the light theme.
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

# 🛠️ The default theme to use. This can be changed here to easily switch the entire application's style.
DEFAULT_THEME = "dark"
