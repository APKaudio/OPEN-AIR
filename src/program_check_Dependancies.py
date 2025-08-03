# src/check_Dependancies.py
#
# This file contains a standalone function to check for and install necessary
# Python dependencies. It is designed to be run as the very first step
# when the application starts, ensuring the environment is ready before
# the GUI or any other modules are loaded.
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
# Version 20250802.0005.1 (Refactored debug_print to debug_log with expanded parameters; added flair.)

current_version = "20250802.0005.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 5 * 1 # Example hash, adjust as needed

import subprocess
import sys
import inspect # For debug_log
import os # For debug_log

# Import the debug logic module to use debug_log
from src.debug_logic import set_debug_mode, set_log_visa_commands_mode, set_debug_to_terminal_mode, debug_log


def check_and_install_dependencies(current_app_version):
    """
    Function Description:
    Checks for necessary Python packages (pyvisa, pandas, beautifulsoup4, pdfplumber, requests)
    and attempts to install them if missing. If packages are missing and the user agrees,
    it installs them and then exits the application, prompting for a restart.
    This function is designed to be called *before* the main Tkinter application
    is initialized, ensuring all dependencies are met. It operates purely via
    command-line interaction (print/input) without any GUI elements.

    Inputs:
    - current_app_version (str): The current version string of the application for logging.

    Process of this function:
    1. Defines a dictionary of required dependencies (import name: package name).
    2. Iterates through the dependencies, attempting to import each.
    3. If an ImportError occurs, adds the package name to a `missing_dependencies` list.
    4. If `missing_dependencies` is not empty, prompts the user to install them
       via command-line `input()`.
    5. If the user agrees, attempts to install using `pip`.
    6. Prints success/failure messages to the console and exits the application
       if installation occurs or if the user declines installation/installation fails.

    Outputs of this function:
    - None. May exit the application if dependencies are missing or installed.
    """
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__ # Use __file__ for the full path

    debug_log(f"Checking and installing dependencies. Application Version: {current_app_version}. Let's get this show on the road!",
                file=current_file,
                version=current_version, # Use this module's version for debug log
                function=current_function)

    dependencies = {
        "pyvisa": "pyvisa",
        "pandas": "pandas",
        "bs4": "beautifulsoup4", # For BeautifulSoup
        "pdfplumber": "pdfplumber",
        "requests": "requests" # Added requests to the dependency check
    }
    missing_dependencies = []

    for import_name, package_name in dependencies.items():
        try:
            __import__(import_name)
            debug_log(f"Dependency '{package_name}' ({import_name}) found. Excellent!",
                        file=current_file,
                        version=current_version,
                        function=current_function)
        except ImportError:
            missing_dependencies.append(package_name)
            debug_log(f"Dependency '{package_name}' ({import_name}) missing. Uh oh!",
                        file=current_file,
                        version=current_version,
                        function=current_function)

    if missing_dependencies:
        missing_str = ", ".join(missing_dependencies)
        
        print(f"\n--- Missing Dependencies ---")
        print(f"The following Python packages are missing: {missing_str}.")
        response = input("Do you want to install them now? (yes/no): ").strip().lower()

        if response == 'yes':
            try:
                debug_log(f"Attempting to install missing packages: {missing_str}. Hold on tight!",
                            file=current_file,
                            version=current_version,
                            function=current_function)
                print(f"Installing packages: {missing_str}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
                print("Required packages installed successfully. Please restart the application. You're good to go!")
                sys.exit(0) # Exit to restart application
            except Exception as e:
                print(f"\n--- Installation Failed ---")
                print(f"Failed to install packages: {e}. This is a disaster!")
                print(f"Please install them manually using 'pip install {missing_str}' and try again.")
                sys.exit(1) # Exit if installation fails
        else:
            print("\n--- Dependencies Missing ---")
            print("Application may not function correctly without required packages. Exiting. What a shame!")
            sys.exit(1) # Exit if user chooses not to install
    else:
        debug_log("All required dependencies are installed. Fantastic!",
                    file=current_file,
                    version=current_version,
                    function=current_function)
