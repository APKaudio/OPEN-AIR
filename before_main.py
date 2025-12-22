# OPEN-AIR/before_main.py
#
import workers.setup.app_constants as app_constants
import os
import sys
import inspect
import subprocess

current_file = f"{os.path.basename(__file__)}"
current_version = app_constants.current_version


        
# --- Constants (No Magic Numbers) ---
# Packages that require pip install/uninstall/reinstall
EXTERNAL_PACKAGES = {
    # --- CORE PROJECT DEPENDENCIES ---
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "Pillow (for Matplotlib/Tkinter image support)": "PIL", 
    ## "paho-mqtt": "paho.mqtt.client",
    "pdfplumber": "pdfplumber",
    "beautifulsoup4 (bs4)": "bs4",
    # --- VISA/SCPI DEPENDENCIES (PyVISA-py backend requires all of these) ---
    "pyvisa": "pyvisa",
    "pyusb": "usb.core",
    "python-usbtmc": "usbtmc",
    "python-vxi11": "vxi11",
    "pyserial": "serial",
   
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


def _execute_pip_command(action, package_name, console_log_func, debug_log_func, current_file, current_version):
    """Safely executes a pip install or uninstall command."""
    current_function_name = inspect.currentframe().f_code.co_name
    command = [sys.executable, "-m", "pip", action, package_name]
    
    # MANDATORY FIX: Add the flag to override system package management (PEP 668)
    command.append(FLAG_BREAK_SYSTEM_PACKAGES) 

    if action == ACTION_UNINSTALL:
        command.append(FLAG_ASSUME_YES) # Assume yes for uninstall
        
    log_message = f"🛠️ Running 'pip {action}' for {package_name}..."
    console_log_func(log_message)
    debug_log_func(
        message=f"🛠️🟢 Running pip command: {' '.join(command)}",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log_func
    )

    try:
        # Capture output for debugging but suppress standard output
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            console_log_func(f"✅ Pip {action} successful for {package_name}.")
            return True
        else:
            # Suppress "Package not installed" errors for uninstall, but report others
            if action == ACTION_UNINSTALL and ERROR_NOT_INSTALLED in result.stderr.lower():
                console_log_func(f"🟡 {package_name} was not installed. Skipping uninstall.")
                return True
            else:
                console_log_func(f"❌ Pip {action} failed for {package_name}. Error: {result.stderr.strip()}")
                return False

    except FileNotFoundError:
        console_log_func("❌ Error: pip command not found. Ensure Python and pip are correctly installed and in PATH.")
        return False
    except Exception as e:
        console_log_func(f"❌ An unexpected error occurred during pip operation for {package_name}: {e}")
        return False


def action_check_dependancies(console_log_func, debug_log_func, should_clean_install=False): # Add argument with default
    # Checks for required external library dependencies and forces a reinstall if found.
    current_function_name = inspect.currentframe().f_code.co_name
    current_file = f"{os.path.basename(__file__)}" # Define current_file locally for this function

    debug_log_func(
        message=f"🖥️🟢 Ah, good, we're entering '{current_function_name}' to examine and refresh the raw materials, shall we?",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log_func
    )
    
    console_log_func(f"🔍 Starting dependency check ({len(EXTERNAL_PACKAGES) + len(BUILTIN_PACKAGES)} modules required). Clean Install Mode: {should_clean_install}")
    
    missing_packages = []

    try:
        # --- 1. Process External Packages (Conditional Refresh) ---
        console_log_func("\n--- Checking/Refreshing External Packages ---")
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
     
            
            if is_installed and should_clean_install: # Use should_clean_install here
                # Scenario A: Installed, running in fresh mode -> Force uninstall/reinstall
                console_log_func(f"✅ Found '{friendly_name}'. Forcing refresh...")
                
                _execute_pip_command(ACTION_UNINSTALL, package_name_for_pip, console_log_func, debug_log_func, current_file, current_version)
                
                if not _execute_pip_command(ACTION_INSTALL, package_name_for_pip, console_log_func, debug_log_func, current_file, current_version):
                    missing_packages.append(friendly_name) 

            elif not is_installed:
                # Scenario B: Not installed -> Attempt install
                console_log_func(f"❌ '{friendly_name}' is missing. Attempting install...")
                if not _execute_pip_command(ACTION_INSTALL, package_name_for_pip, console_log_func, debug_log_func, current_file, current_version):
                    missing_packages.append(friendly_name)
            
            elif is_installed and not should_clean_install: # Use should_clean_install here
                # Scenario C: Installed, not in fresh mode -> Skip, treat as success
                console_log_func(f"✅ Found '{friendly_name}'. Skipping refresh (Non-fresh mode).")


        # --- 2. Process Built-in Packages (Simple Check) ---
        console_log_func("\n--- Checking Standard Python Modules ---")
        for friendly_name, import_name in BUILTIN_PACKAGES.items():
            try:
                __import__(import_name)
                console_log_func(f"✅ Found '{friendly_name}'.")
            except ImportError:
                missing_packages.append(friendly_name)

        # --- 3. Final Result ---
        if missing_packages:
            console_log_func("\n" + "="*50)
            console_log_func(CRITICAL_FAILURE_MESSAGE)
            console_log_func("The following critical packages failed to install or are missing:")
            for pkg in missing_packages:
                console_log_func(f" - {pkg}")
            
            # --- INCORPORATED USER'S REQUESTED MESSAGE HERE ---
            console_log_func(MANUAL_INSTALL_INSTRUCTION)
            # --- END INCORPORATED MESSAGE ---
            
            console_log_func("="*50 + "\n")
            
            # Allow the main application to handle the error
            return False

        
        # --- Celebration of Success ---
        console_log_func("\n✅ A most glorious success! All critical dependencies are verified and refreshed.")
        debug_log_func(
            message="🖥️✅ All raw materials secured! Proceeding to next phase.",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log_func
        )
        return True

    except Exception as e:
        console_log_func(f"\n❌ UNEXPECTED FATAL ERROR during dependency check: {e}")
        debug_log_func(
            message=f"🖥️🔴 Heavens to Betsy! An unknown error has torpedoed the dependency check! The error be: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log_func
        )
        # Allows the main application to handle the error
        return False


def run_interactive_pre_check(console_log_func, debug_log_func):
    console_log_func("🚀 Starting dependency pre-check for OPEN-AIR. 🚀")
    
    # Prompt user for action
    user_choice = input("Do you want to [C]lean install (uninstall and reinstall all external libraries) or just [V]erify and install missing ones? (C/V): ").strip().lower()

    should_clean_install = False
    if user_choice == 'c':
        should_clean_install = True
        console_log_func("💡 Clean install mode selected. All external libraries will be reinstalled.")
    else:
        console_log_func("💡 Verify and install missing libraries mode selected.")

    # Pass should_clean_install to the dependency check function
    if not action_check_dependancies(console_log_func, debug_log_func, should_clean_install):
        sys.exit(1)

if __name__ == "__main__":
    # When run directly, use simple print statements as mock loggers
    def _standalone_console_log(message):
        print(message)
    def _standalone_debug_log(message, *args, **kwargs):
        if "--debug" in sys.argv:
            print(f"DEBUG (standalone): {message}")

    run_interactive_pre_check(_standalone_console_log, _standalone_debug_log)