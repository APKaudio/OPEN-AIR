# OPEN-AIR/before_main.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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
# Version 20251026.225541.2
import sys
import inspect
import datetime
import os
import subprocess 

# --- Global Scope Variables (as per Protocol 4.4) ---
current_version = "20251026.225541.2"
# The hash calculation drops the leading zero from the hour (22 -> 22)
current_version_hash = (20251026 * 225541 * 2)
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
# Packages that require pip install/uninstall/reinstall
EXTERNAL_PACKAGES = {
    # --- CORE PROJECT DEPENDENCIES ---
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "Pillow (for Matplotlib/Tkinter image support)": "PIL", 
    "paho-mqtt": "paho.mqtt.client",
    "pdfplumber": "pdfplumber",
    "beautifulsoup4 (bs4)": "bs4",
    # --- VISA/SCPI DEPENDENCIES (PyVISA-py backend requires all of these) ---
    "pyvisa": "pyvisa",
    "pyusb": "usb.core",
    "python-usbtmc": "usbtmc",
    "python-vxi11": "vxi11",
    "pyserial": "serial",
    "python-gpib": "Gpib", 
    "psutil": "psutil",
    "zeroconf": "zeroconf",
}
# Packages that are generally built-in and only require an import check
BUILTIN_PACKAGES = {
    "python-csv": "csv",
    "python-threading": "threading",
    "python-subprocess": "subprocess",
    "python-pathlib": "pathlib", 
    "python-json": "json" 
}

# --- PIP Command Actions ---
ACTION_INSTALL = "install"
ACTION_UNINSTALL = "uninstall"
FLAG_BREAK_SYSTEM_PACKAGES = "--break-system-packages"
FLAG_ASSUME_YES = "-y"
ERROR_NOT_INSTALLED = "not installed"
CRITICAL_FAILURE_MESSAGE = "❌ CRITICAL FAILURE: Missing/Failed Dependencies!"
MANUAL_INSTALL_INSTRUCTION = "\nManual installation may be required. Remember to use a virtual environment or the '--break-system-packages' flag."


def _execute_pip_command(action, package_name, console_print_func):
    """Safely executes a pip install or uninstall command."""
    current_function_name = inspect.currentframe().f_code.co_name
    command = [sys.executable, "-m", "pip", action, package_name]
    
    # MANDATORY FIX: Add the flag to override system package management (PEP 668)
    command.append(FLAG_BREAK_SYSTEM_PACKAGES) 

    if action == ACTION_UNINSTALL:
        command.append(FLAG_ASSUME_YES) # Assume yes for uninstall
        
    log_message = f"🛠️ Running 'pip {action}' for {package_name}..."
    console_print_func(log_message)
    _mock_debug_log(
        message=f"🛠️🟢 Running pip command: {' '.join(command)}",
        file=current_file,
        version=current_version,
        function=current_function_name,
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
            if action == ACTION_UNINSTALL and ERROR_NOT_INSTALLED in result.stderr.lower():
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
  
    _mock_console_log(f"🔍 Starting dependency check ({len(EXTERNAL_PACKAGES) + len(BUILTIN_PACKAGES)} modules required). Fresh Mode: {is_fresh_mode}")
    
    missing_packages = []

    try:
        # --- 1. Process External Packages (Conditional Refresh) ---
        _mock_console_log("\n--- Checking/Refreshing External Packages ---")
        for friendly_name, import_name in EXTERNAL_PACKAGES.items():
            
            # --- Dynamically Determine the PyPI Package Name ---
            package_name_for_pip = import_name.split('.')[0]
            
            # Overrides for cases where PyPI name differs from import root or module
            if friendly_name == "paho-mqtt":
                package_name_for_pip = "paho-mqtt"
            elif friendly_name == "python-usbtmc":
                package_name_for_pip = "python-usbtmc"
            elif friendly_name == "python-vxi11":
                package_name_for_pip = "python-vxi11"
            elif friendly_name == "python-gpib":
                package_name_for_pip = "python-gpib" 
            elif friendly_name == "pyserial":
                package_name_for_pip = "pyserial"
            elif friendly_name == "beautifulsoup4 (bs4)":
                 package_name_for_pip = "beautifulsoup4"
            elif friendly_name == "Pillow (for Matplotlib/Tkinter image support)":
                package_name_for_pip = "Pillow" 
            # --- End Overrides ---
            
            try:
                __import__(import_name)
                is_installed = True
            except ImportError:
                is_installed = False
     
            
            if is_installed and is_fresh_mode:
                # Scenario A: Installed, running in fresh mode -> Force uninstall/reinstall
                _mock_console_log(f"✅ Found '{friendly_name}'. Forcing refresh...")
                
                _execute_pip_command(ACTION_UNINSTALL, package_name_for_pip, _mock_console_log)
                
                if not _execute_pip_command(ACTION_INSTALL, package_name_for_pip, _mock_console_log):
                    missing_packages.append(friendly_name) 

            elif not is_installed:
                # Scenario B: Not installed -> Attempt install
                _mock_console_log(f"❌ '{friendly_name}' is missing. Attempting install...")
                if not _execute_pip_command(ACTION_INSTALL, package_name_for_pip, _mock_console_log):
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
            _mock_console_log(CRITICAL_FAILURE_MESSAGE)
            _mock_console_log("The following critical packages failed to install or are missing:")
            for pkg in missing_packages:
                _mock_console_log(f" - {pkg}")
            
            # --- INCORPORATED USER'S REQUESTED MESSAGE HERE ---
            _mock_console_log(MANUAL_INSTALL_INSTRUCTION)
            # --- END INCORPORATED MESSAGE ---
            
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