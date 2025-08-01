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
#
#
# Version 20250801.2 (Removed all Tkinter dependencies. Dependency checks now
#                     use print() for output and input() for user confirmation,
#                     making it a pure command-line operation. Updated debug_print
#                     fallback for early execution.)

import subprocess
import sys
import inspect # For debug_print
import os # For debug_print

# Import debug_print from utils.utils_instrument_control
# We need a way to print debug messages before the main app's console is ready.
# For this specific function, we'll use a fallback print if debug_print isn't available yet.
try:
    from utils.utils_instrument_control import debug_print
except ImportError:
    # Fallback debug_print if the utility module isn't available yet
    def debug_print(message, file="", function="", console_print_func=None):
        # In this very early stage, console_print_func won't be available,
        # so we just print directly to stdout/stderr.
        print(f"🚫🐛 [DEBUG] {file} - {function}: {message}")


def check_and_install_dependencies(current_version):
    # Function Description:
    # Checks for necessary Python packages (pyvisa, pandas, beautifulsoup4, pdfplumber, requests)
    # and attempts to install them if missing. If packages are missing and the user agrees,
    # it installs them and then exits the application, prompting for a restart.
    # This function is designed to be called *before* the main Tkinter application
    # is initialized, ensuring all dependencies are met. It operates purely via
    # command-line interaction (print/input) without any GUI elements.
    #
    # Inputs:
    #   current_version (str): The current version string of the application for logging.
    #
    # Process:
    #   1. Defines a dictionary of required dependencies (import name: package name).
    #   2. Iterates through the dependencies, attempting to import each.
    #   3. If an ImportError occurs, adds the package name to a `missing_dependencies` list.
    #   4. If `missing_dependencies` is not empty, prompts the user to install them
    #      via command-line `input()`.
    #   5. If the user agrees, attempts to install using `pip`.
    #   6. Prints success/failure messages to the console and exits the application
    #      if installation occurs or if the user declines installation/installation fails.
    #
    # Outputs:
    #   None. May exit the application if dependencies are missing or installed.
    #
    # (2025-08-01) Change: Removed Tkinter dependencies. Now uses print() and input()
    #                      for all user interaction.
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__)
    
    debug_print(f"Checking and installing dependencies. Version: {current_version}",
                file=current_file, function=current_function)

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
            debug_print(f"Dependency '{package_name}' ({import_name}) found.",
                        file=current_file, function=current_function)
        except ImportError:
            missing_dependencies.append(package_name)
            debug_print(f"Dependency '{package_name}' ({import_name}) missing.",
                        file=current_file, function=current_function)

    if missing_dependencies:
        missing_str = ", ".join(missing_dependencies)
        
        print(f"\n--- Missing Dependencies ---")
        print(f"The following Python packages are missing: {missing_str}.")
        response = input("Do you want to install them now? (yes/no): ").strip().lower()

        if response == 'yes':
            try:
                debug_print(f"Attempting to install missing packages: {missing_str}",
                            file=current_file, function=current_function)
                print(f"Installing packages: {missing_str}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
                print("Required packages installed successfully. Please restart the application.")
                sys.exit(0) # Exit to restart application
            except Exception as e:
                print(f"\n--- Installation Failed ---")
                print(f"Failed to install packages: {e}")
                print(f"Please install them manually using 'pip install {missing_str}'")
                sys.exit(1) # Exit if installation fails
        else:
            print("\n--- Dependencies Missing ---")
            print("Application may not function correctly without required packages. Exiting.")
            sys.exit(1) # Exit if user chooses not to install
    else:
        debug_print("All required dependencies are installed.",
                    file=current_file, function=current_function)

