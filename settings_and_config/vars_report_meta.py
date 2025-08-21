# settings_and_config/vars_report_meta.py
#
# This module defines and initializes Tkinter variables for scan report metadata,
# including operator, venue, and location details.
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
# Version 20250821.220500.1
# NEW: Created a new file to house report and metadata variables.

import tkinter as tk
import inspect
import os
from display.debug_logic import debug_log
from ref.ref_program_default_values import DEFAULT_CONFIG

# --- Version Information ---
current_version = "20250821.220500.1"
current_version_hash = (20250821 * 220500 * 1)
current_file = f"{os.path.basename(__file__)}"

def setup_report_meta_vars(app_instance):
    """
    Initializes all the Tkinter variables for scan report metadata.
    """
    current_function = inspect.currentframe().f_code.co_name
    debug_log(f"⚙️ 🟢 Entering {current_function} to set up report meta variables. 📝",
                file=current_file,
                version=current_version,
                function=current_function)

    # --- Report Variables ---
    app_instance.operator_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_name'])
    app_instance.operator_contact_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['operator_contact'])
    app_instance.venue_name_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_name'])
    app_instance.address_field_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['address_field'])
    app_instance.city_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['city'])
    app_instance.province_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['province'])
    app_instance.venue_postal_code_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['venue_postal_code'])
    app_instance.notes_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['notes'])
    app_instance.scanner_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Report']['scanner_type'])
    
    # --- Antenna Variables ---
    app_instance.selected_antenna_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['selected_antenna_type'])
    app_instance.antenna_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_description'])
    app_instance.antenna_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_use'])
    app_instance.antenna_mount_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_mount'])
    app_instance.antenna_amplifier_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Antenna']['antenna_amplifier'])

    # --- Amplifier Variables ---
    app_instance.selected_amplifier_type_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['selected_amplifier_type'])
    app_instance.amplifier_description_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_description'])
    app_instance.amplifier_use_var = tk.StringVar(app_instance, value=DEFAULT_CONFIG['Amplifier']['amplifier_use'])
    
    debug_log(f"⚙️ ✅ Exiting {current_function}",
                file=current_file,
                version=current_version,
                function=current_function)