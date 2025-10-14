# Before_main.py
#
# A standalone script to verify the installation of all critical external
# dependencies before launching the main application. This script will attempt to
# uninstall and then reinstall external packages to ensure version freshness.
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
# Version 20251013.213500.1 

import sys
import inspect
import datetime
import os
import subprocess 

# --- Global Scope Variables (as per Protocol 4.4) ---
# W: 20251013, X: 213500, Y: 1
current_version = "20251013.213500.1"
# The hash calculation drops the leading zero from the hour (21 -> 21)
current_version_hash = (20251013 * 213500 * 1)
current_file = f"{os.path.basename(__file__)}"

# --- Mock Logging Functions (for standalone operation before app logger is active) ---
def _mock_console_log(message):
    """Prints a user-facing message."""
    print(message)

def _mock_debug_log(message, file, version, function, console_print_func):
    """Prints a detailed debug log entry."""
    if "--debug" in sys.argv:
        print(f"DEBUG: {message} | {file} | {version} Function: {function}")
        
# --- Constants (No Magic Numbers) ---
# Dictionary structure: { "Friendly Name": ("Python Import Name", "PyPI Install Name") }
EXTERNAL_PACKAGES_MAP = {
    "pyvisa": ("pyvisa", "pyvisa"),
    "paho-mqtt": ("paho.mqtt.client", "paho-mqtt"),
    "pandas": ("pandas", "pandas"),
    "numpy": ("numpy", "numpy"),
    "matplotlib": ("matplotlib", "matplotlib"),
    "pdfplumber": ("pdfplumber", "pdfplumber"),
    "beautifulsoup4 (bs4)": ("bs4", "beautifulsoup4"), # Using full PyPI name for safety
    # --- INSTRUMENT PROTOCOL DEPENDENCIES ---
    "pyusb": ("usb.core", "pyusb"),
    "python-usbtmc": ("usbtmc", "python-usbtmc"),
    "python-vxi11": ("vxi11", "python-vxi11"),
    "pyserial": ("serial", "pyserial"),
    "python-gpib": ("Gpib", "python-gpib"), 
    # --- PyVISA-py Backend Dependencies ---
    "psutil": ("psutil", "psutil"),
    "zeroconf": ("zeroconf", "zeroconf"),
}
# Packages that are generally built-in and only require an import check
BUILTIN_PACKAGES = {
    "python-csv": "csv",
    "python-threading": "threading",
    "python-subprocess": "subprocess",
    "python-tkinter": "tkinter" # Tkinter/Tcl is crucial for GUI and needs explicit check
}

def _execute_pip_command(action, package_name, console_print_func):
    """Safely executes a pip install or uninstall command."""
    command = [sys.executable, "-m", "pip", action, package_name]
    
    # MANDATORY FIX: Add the flag to override system package management (PEP 668)
    command.append("--break-system-packages") 

    if action == "uninstall":
        command.append("-y") # Assume yes for uninstall
        
    log_message = f"🛠️ Running 'pip {action}' for {package_name}..."
    console_print_func(log_message)
    _mock_debug_log(
        message=f"🛠️🟢 Running pip command: {' '.join(command)}",
        file=current_file,
        version=current_version,
        function="_execute_pip_command",
        console_print_func=console_print_func
    )

    try:
        # Capture output for debugging but suppress standard output
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            console_print_func(f"✅ Pip {action} successful for {package_name}.")
            return True
        else:
            # Suppress "Package not installed" errors for uninstall, but report others
            if action == "uninstall" and "not installed" in result.stderr.lower():
                console_print_func(f"🟡 {package_name} was not installed. Skipping uninstall.")
                return True
            else:
                console_print_func(f"❌ Pip {action} failed for {package_name}. Error: {result.stderr.strip()}")
                return False

    except FileNotFoundError:
        console_print_func("❌ Error: pip command not found. Ensure Python and pip are correctly installed and in PATH.")
        return False
    except Exception as e:
        console_print_func(f"❌ An unexpected error occurred during pip operation for {package_name}: {e}")
        return False


def action_check_dependancies():
    # Checks for required external library dependencies and forces a reinstall if found.
    current_function_name = inspect.currentframe().f_code.co_name
    _mock_debug_log(
        message=f"🖥️🟢 Ah, good, we're entering '{current_function_name}' to examine and refresh the raw materials, shall we?",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=_mock_console_log
    )
    
    # NEW: Determine if the script is running in 'fresh' mode
    is_fresh_mode = any("fresh" in arg.lower() for arg in sys.argv)
    
    _mock_console_log(f"🔍 Starting dependency check ({len(EXTERNAL_PACKAGES_MAP) + len(BUILTIN_PACKAGES)} modules required). Fresh Mode: {is_fresh_mode}")
    
    missing_packages = []

    try:
        # --- 1. Process External Packages (Conditional Refresh) ---
        _mock_console_log("\n--- Checking/Refreshing External Packages ---")
        for friendly_name, (import_name, pypi_name) in EXTERNAL_PACKAGES_MAP.items():
            
            # 1a. Check installation status using the import name
            try:
                __import__(import_name if '.' not in import_name else import_name.split('.')[0])
                is_installed = True
            except ImportError:
                is_installed = False
            
            
            if is_installed and is_fresh_mode:
                # Scenario A: Installed, running in fresh mode -> Force uninstall/reinstall
                _mock_console_log(f"✅ Found '{friendly_name}'. Forcing refresh...")
                
                # Uninstall using the PyPI name
                _execute_pip_command("uninstall", pypi_name, _mock_console_log)
                
                # Reinstall using the PyPI name
                if not _execute_pip_command("install", pypi_name, _mock_console_log):
                    missing_packages.append(friendly_name) 

            elif not is_installed:
                # Scenario B: Not installed -> Attempt install
                _mock_console_log(f"❌ '{friendly_name}' is missing. Attempting install...")
                
                # Install using the PyPI name
                if not _execute_pip_command("install", pypi_name, _mock_console_log):
                    missing_packages.append(friendly_name)
            
            elif is_installed and not is_fresh_mode:
                # Scenario C: Installed, not in fresh mode -> Skip, treat as success
                _mock_console_log(f"✅ Found '{friendly_name}'. Skipping refresh (Non-fresh mode).")


        # --- 2. Process Built-in Packages (Simple Check) ---
        _mock_console_log("\n--- Checking Standard Python Modules ---")
        for friendly_name, import_name in BUILTIN_PACKAGES.items():
            try:
                __import__(import_name)
                _mock_console_log(f"✅ Found '{friendly_name}'.")
            except ImportError:
                missing_packages.append(friendly_name)

        # --- 3. Final Result ---
        if missing_packages:
            _mock_console_log("\n" + "="*50)
            _mock_console_log("❌ CRITICAL FAILURE: Missing/Failed Dependencies!")
            _mock_console_log("The following critical packages failed to install or are missing:")
            for pkg in missing_packages:
                if pkg == "python-tkinter":
                    _mock_console_log(f" - {pkg} (GUI): Requires OS-level package (e.g., 'sudo apt install python3-tk').")
                else:
                    _mock_console_log(f" - {pkg}")
            _mock_console_log("\nManual installation may be required.")
            _mock_console_log("="*50 + "\n")
            
            # Allow the main application to handle the error
            return False

        
        # --- Celebration of Success ---
        _mock_console_log("\n✅ A most glorious success! All critical dependencies are verified and refreshed.")
        _mock_debug_log(
            message="🖥️✅ All raw materials secured! Proceeding to next phase.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=_mock_console_log
        )
        return True

    except Exception as e:
        _mock_console_log(f"\n❌ UNEXPECTED FATAL ERROR during dependency check: {e}")
        _mock_debug_log(
            message=f"🖥️🔴 Heavens to Betsy! An unknown error has torpedoed the dependency check! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=_mock_console_log
        )
        # Allows the main application to handle the error
        return False


if __name__ == "__main__":
    # When run directly, force a system exit on failure
    if not action_check_dependancies():
        sys.exit(1)
