# workers/setup/app_constants.py
# Mock file for prototype purposes

current_version = "20251223.120000.proto"
PERFORMANCE_MODE = True

SKIP_DEP_CHECK = True

# --- New Debug Flags ---
ENABLE_DEBUG_MODE = False
ENABLE_DEBUG_FILE = False
ENABLE_DEBUG_SCREEN = False

# LOCAL_DEBUG_ENABLE controls debug output to the console/screen (used by SplashScreen)
LOCAL_DEBUG_ENABLE = ENABLE_DEBUG_SCREEN

# --- UI Layout Constants ---
UI_LAYOUT_SPLIT_EQUAL = 50
UI_LAYOUT_FULL_WEIGHT = 100

global_settings = {
    "general_debug_enabled": ENABLE_DEBUG_MODE,
    "debug_to_terminal": ENABLE_DEBUG_SCREEN,
    "debug_to_file": ENABLE_DEBUG_FILE,
    "log_truncation_enabled": False, # Setting to False for prototype to see full messages
}