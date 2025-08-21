# src/program_shared_values.py
#
# This module centralizes the definition and initialization of all Tkinter variables
# used throughout the RF Spectrum Analyzer Controller application. It provides a
# single source for managing application-wide settings, instrument parameters,
# scan configurations, and plotting preferences.
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
# Version 20250821.220500.2
# FIXED: Initialized app_instance.visa_resource_var, app_instance.band_vars,
#        and app_instance.collected_scans_dataframes to prevent AttributeErrors.

import tkinter as tk
import inspect
import os
from datetime import datetime
from tkinter import StringVar

from display.debug_logic import debug_log
from ref.ref_frequency_bands import SCAN_BAND_RANGES

# --- Version Information ---
current_version = "20250821.220500.2"
current_version_hash = (20250821 * 220500 * 2)
current_file = f"{os.path.basename(__file__)}"


# Import modular variable setup functions
from settings_and_config.vars_app_and_debug import setup_app_and_debug_vars
from settings_and_config.vars_marker_tab import setup_marker_tab_vars
from settings_and_config.vars_instrument import setup_instrument_vars
from settings_and_config.vars_scan_config import setup_scan_config_vars
from settings_and_config.vars_report_meta import setup_report_meta_vars
from settings_and_config.vars_plotting import setup_plotting_vars


def setup_shared_values(app_instance):
    """
    Initializes all the shared Tkinter variables for the application.
    This function should be called once during program initialization.
    
    Args:
        app_instance: The main application instance (tk.Tk()).
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Setting up shared values with the force! ✨",
                file=os.path.basename(__file__),
                version=current_version,
                function=current_function)

    # Call the modular setup functions
    setup_app_and_debug_vars(app_instance)
    setup_marker_tab_vars(app_instance)
    setup_instrument_vars(app_instance)
    setup_scan_config_vars(app_instance)
    setup_report_meta_vars(app_instance)
    setup_plotting_vars(app_instance)
    
    # --- Other shared values that don't fit in a category ---
    app_instance.selected_bands_levels = []
    app_instance.connected_instrument_instance = None # Placeholder for the VISA connection object
    
    # NEW FIX: Initializing these variables to prevent AttributeErrors
    app_instance.visa_resource_var = StringVar(value="")
    app_instance.band_vars = {}
    app_instance.collected_scans_dataframes = {}

    debug_log(f"⚙️ ✅ Exiting {current_function}",
              file=os.path.basename(__file__),
              version=current_version,
              function=current_function)