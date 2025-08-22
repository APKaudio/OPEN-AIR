# src/program_check_dependancies.py
#
# This file checks for and installs necessary Python dependencies.
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
# Version 20250821.220200.1

import subprocess
import sys
import inspect
import os
from datetime import datetime

# --- Version Information ---
current_version = "20250821.220200.1"
current_version_hash = 20250821 * 220200 * 1
current_file = os.path.basename(__file__)

def check_and_install_dependencies():
    """
    Checks for necessary packages and installs missing ones automatically.
    The interactive upgrade prompt has been removed.
    """
    current_function = inspect.currentframe().f_code.co_name
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - 🟢 Checking for required Python packages.")

    required_dependencies = {
        "numpy": "numpy",
        "pandas": "pandas",
        "scipy": "scipy",
        "pyvisa": "pyvisa",
        "matplotlib": "matplotlib",
        "plotly": "plotly",
        "openpyxl": "openpyxl",
        "pyserial": "serial",
        "Pillow": "PIL",
        "tk": "tk"
    }
    
    missing_dependencies = []
    
    for package_name, import_name in required_dependencies.items():
        try:
            if import_name == "tk":
                __import__("tkinter")
            else:
                __import__(import_name)
            
            print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ Dependency '{package_name}' found.")
        except ImportError:
            # Don't add 'tk' to the list for pip operations
            if package_name != "tk":
                missing_dependencies.append(package_name)
            print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ❌ Dependency '{package_name}' missing.")

    # --- Step 1: Install any missing dependencies ---
    if missing_dependencies:
        missing_str = ", ".join(missing_dependencies)
        
        print(f"\n--- Missing Dependencies ---")
        print(f"The following Python packages are missing: {missing_str}.")
        print("Attempting to install them now...")

        try:
            print(f"Attempting to install missing packages: {missing_str}. Hold on tight!")
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_dependencies])
            print("Required packages installed successfully. Please restart the application.")
            sys.exit(0)
        except Exception as e:
            print(f"\n--- Installation Failed ---")
            print(f"Failed to install packages: {e}. Please install them manually and try again.")
            sys.exit(1)
    
    # --- Step 2: Confirmation ---
    else:
        print(f"💻 [{timestamp}]-[{current_version}]-[{current_file}]-[{current_function}] - ✅ All required dependencies are installed.")