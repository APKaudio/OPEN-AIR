# main.py
#
# This file serves as the main entry point for the application, orchestrating startup checks and GUI launch.
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
# Version 20250821.235900.1

import os
import inspect
import datetime
import sys
import pathlib

# Add the project's root directory to the system path to allow for imports from
# all sub-folders (e.g., 'configuration' and 'display').
if str(pathlib.Path(__file__).resolve().parent) not in sys.path:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent))

# Import core application modules
from configuration.logging import console_log, debug_log
from display.gui_display import Application


# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"


def action_check_dependancies():
    # Checks for required system and library dependencies.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🖥️🟢 Ah, good, we're entering '{current_function_name}'! Let's examine the raw materials, shall we?",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # --- Function logic goes here ---
        # Placeholder for dependency checking logic
        console_log("✅ A most glorious success! Dependencies are in order.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"🖥️🔴 Heavens to Betsy! We've hit a snag in the dependencies! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return False

def action_check_configuration():
    # Validates the application's configuration files.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🖥️🟢 Ahem, commencing the configuration validation experiment in '{current_function_name}'.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # --- Function logic goes here ---
        # Placeholder for configuration validation
        console_log("✅ Excellent! The configuration is quite, quite brilliant.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"🖥️🔴 By Jove! The configuration is in shambles! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return False

def action_open_display():
    # Initializes and opens the main graphical user interface.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message=f"🖥️🟢 The final step! Activating the main display in '{current_function_name}'!",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    try:
        # --- Function logic goes here ---
        app = Application()
        app.mainloop()
        console_log("✅ The grand spectacle begins! GUI is now open.")
        return True

    except Exception as e:
        console_log(f"❌ Error in {current_function_name}: {e}")
        debug_log(
            message=f"🖥️🔴 Blast and barnacles! The display has failed to materialize! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
        return False

def main():
    """The main execution function for the application."""
    console_log(f"🚀 Launch sequence initiated for version {current_version}.")

    if action_check_dependancies():
        if action_check_configuration():
            action_open_display()
        else:
            console_log("❌ Halting startup due to configuration errors.")
    else:
        console_log("❌ Halting startup due to missing dependencies.")


if __name__ == "__main__":
    main()

