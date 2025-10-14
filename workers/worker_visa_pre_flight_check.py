# workers/worker_visa_pre_flight_check.py
#
# A standalone utility script to scan all available VISA resources (USB, TCP/IP, Serial, etc.)
# and list them for diagnostic purposes.
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
# Version 20251013.202759.4 (Added full dependency status report for USB/TCPIP components)

import os
import inspect
import datetime
import pyvisa
import sys

# --- Check Optional Dependencies for PyVISA-py ---
# PyVISA-py relies on these optional packages for full functionality.
try:
    import usb.core
    USB_SUPPORT = True
except ImportError:
    USB_SUPPORT = False
    
try:
    import psutil
    NETWORK_ALL_INTERFACES_SUPPORT = True
except ImportError:
    NETWORK_ALL_INTERFACES_SUPPORT = False

try:
    import zeroconf
    NETWORK_HISLIP_SUPPORT = True
except ImportError:
    NETWORK_HISLIP_SUPPORT = False


# --- Global Scope Variables (as per Protocol 4.4) ---
# W: 20251013, X: 202759, Y: 4
current_version = "20251013.202759.4"
# The hash calculation drops the leading zero from the hour (20 -> 20)
current_version_hash = (20251013 * 202759 * 4)
current_file = f"{os.path.basename(__file__)}"

# --- Mock Logging Functions (for standalone operation) ---
def console_log(message):
    """Prints a user-facing message."""
    print(f"[PRE-FLIGHT] {message}")

def debug_log(message, file, version, function, console_print_func):
    """Prints a detailed debug log entry (mocked for simplicity)."""
    if "--debug" in sys.argv:
        print(f"DEBUG: {message} | {file} | {version} Function: {function}")

def list_visa_resources():
    # Lists all available VISA resources using PyVISA.
    current_function_name = inspect.currentframe().f_code.co_name
    debug_log(
        message="🖥️🟢 Entering list_visa_resources. Initiating full system resource scan.",
        file=current_file,
        version=current_version,
        function=current_function_name,
        console_print_func=console_log
    )

    # Determine which backend to try. We prioritize the pure-Python backend (@py).
    backend_to_use = '@py'
    
    try:
        # Initialize the Resource Manager, explicitly using the pure-Python backend.
        rm = pyvisa.ResourceManager(backend_to_use) 
        
        # Safely determine the loaded backend description
        try:
            # This path is generally only available for vendor backends (like NI-VISA)
            library_path = rm.library.path
            backend_info = f"{library_path}"
        except AttributeError:
            # If .library is not available, assume the pure-Python backend is loaded.
            backend_info = "PyVISA-py (pure Python backend)"

        console_log("Scanning all available VISA resources (USB, TCPIP, GPIB, ASRL/Serial)...")
        console_log(f"Using VISA Backend: {backend_info}")
        
        console_log("-" * 40)
        
        # --- Dependency Status Report ---
        console_log("Dependency Status Report:")
        
        # 1. USB Dependency Check
        if USB_SUPPORT:
            console_log("✅ USB Dependency (pyusb) is installed.")
        else:
            console_log("❌ USB Dependency (pyusb) is MISSING. USB device discovery may fail.")
            console_log("   Action: Run 'pip install pyusb' and ensure 'libusb' is installed on your OS.")
            
        # 2. TCP/IP Interface Discovery Check
        if NETWORK_ALL_INTERFACES_SUPPORT:
            console_log("✅ Network Dependency (psutil) is installed (enables all interface scanning).")
        else:
            console_log("🟡 Network Dependency (psutil) is MISSING. Discovery limited to default interface.")
            console_log("   Action: Run 'pip install psutil'.")

        # 3. HiSLIP (mDNS/ZeroConf) Dependency Check
        if NETWORK_HISLIP_SUPPORT:
            console_log("✅ HiSLIP Dependency (zeroconf) is installed.")
        else:
            console_log("🟡 HiSLIP Dependency (zeroconf) is MISSING. HiSLIP resource discovery is disabled.")
            console_log("   Action: Run 'pip install zeroconf'.")
            
        console_log("-" * 40)
        
        # list_resources() performs the actual scan.
        resources = rm.list_resources()

        if resources:
            console_log(f"✅ Found {len(resources)} VISA Resource(s):")
            for i, resource in enumerate(resources, 1):
                # Attempt to determine resource type from the resource string
                resource_type = resource.split("::")[0]
                console_log(f"  {i}. {resource} ({resource_type})")
        else:
            console_log("🟡 No VISA resources found on the system.")
            console_log("Note: If devices are connected, check device power and physical connection.")
        
        console_log("-" * 40)
        console_log("✅ Scan complete.")
        return resources

    except pyvisa.errors.LibraryError as e:
        console_log(f"❌ Error: PyVISA backend library failed to load with '{backend_to_use}'.")
        console_log("  Ensure 'pyvisa-py' is installed and its dependencies (like 'pyusb') are met.")
        console_log(f"  Details: {e}")
    except Exception as e:
        console_log(f"❌ UNEXPECTED ERROR during VISA scan: {type(e).__name__}: {e}")
        debug_log(
            message=f"🖥️🔴 VISA scan failed: {e}",
            file=current_file,
            version=current_version,
            function=current_function_name,
            console_print_func=console_log
        )
    return []

if __name__ == "__main__":
    # Execute the scan function when the script is run directly.
    list_visa_resources()
