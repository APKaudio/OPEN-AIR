# styling/style.py
#
# Defines the color palettes for different UI themes.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio

THEMES = {
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#dcdcdc",
        "primary": "#3c3f41",
        "secondary": "#4e5254",
        "accent": "#007acc",
        "text": "#ffffff", # Brighter text for better contrast on colored tabs
        "border": "#555555",
        "relief": "flat",
        # NEW: Rainbow accent colors for tabs
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
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "primary": "#ffffff",
        "secondary": "#e0e0e0",
        "accent": "#d75600",
        "text": "#000000",
        "border": "#ababab",
        "relief": "groove",
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

# The default theme to use
DEFAULT_THEME = "dark"
