DEFAULT_SETTINGS_STRUCTURE = {
        'GLOBAL__window_geometry': '1700x800+100+100',
        'GLOBAL__debug_enabled': 'False',
        'GLOBAL__log_visa_commands_enabled': 'False',
        'GLOBAL__paned_window_sash_position': '700', # NEW: Default sash position

        'instrument_connection__visa_resource': 'N/A',

        'scan_configuration__scan_name': 'ThisIsMyScan',
        'scan_configuration__scan_directory': 'scan_data',
        'scan_configuration__num_scan_cycles': '1',
        'scan_configuration__rbw_step_size_hz': '10000',
        'scan_configuration__cycle_wait_time_seconds': '0.5',
        'scan_configuration__maxhold_time_seconds': '3',
        'scan_configuration__scan_rbw_hz': '10000',
        'scan_configuration__reference_level_dbm': '-40',
        'scan_configuration__freq_shift_hz': '0',
        'scan_configuration__maxhold_enabled': 'True',
        'scan_configuration__sensitivity': 'True', # Renamed from high_sensitivity
        'scan_configuration__preamp_on': 'True',
        'scan_configuration__scan_rbw_segmentation': '1000000.0',
        'scan_configuration__default_focus_width': '10000.0',
        # 'scan_configuration__selected_bands' is dynamically generated below

        'scan_meta_data__operator_name': 'Anthony Peter Kuzub',
        'scan_meta_data__contact': 'I@Like.audio',
        'scan_meta_data__name': 'Garage', # Renamed from venue_name
        
        # NEW: Default values for postal code lookup and new antenna/amplifier fields
        'scan_meta_data__venue_postal_code': '',
        'scan_meta_data__address_field': '',
        'scan_meta_data__city': 'Whitby', # Still used for City
        'scan_meta_data__province': '', # NEW: For Province
        # Removed: 'scan_meta_data__map_location': '',

        'scan_meta_data__scanner_type': 'Unknown',
        
        # NEW: Default values for antenna and amplifier dropdowns
        'scan_meta_data__selected_antenna_type': '', # Default to empty, will be set on first selection
        'scan_meta_data__antenna_description': '',
        'scan_meta_data__antenna_use': '',
        'scan_meta_data__antenna_mount': '',
        'scan_meta_data__selected_amplifier_type': '', # Default to empty, will be set on first selection
        'scan_meta_data__antenna_amplifier': '', # This will store the final selected amplifier name
        'scan_meta_data__amplifier_description': '', # NEW: Default for amplifier description
        'scan_meta_data__amplifier_use': '',         # NEW: Default for amplifier use

        'scan_meta_data__notes': '',

        'plotting__scan_markers_to_plot__include_gov_markers': 'True',
        'plotting__scan_markers_to_plot__include_tv_markers': 'True',
        'plotting__scan_markers_to_plot__include_markers': 'True',
        'plotting__scan_markers_to_plot__include_intermod_markers': 'False', # NEW
        'plotting__scan_markers_to_plot__open_html_after_complete': 'True',
        'plotting__scan_markers_to_plot__create_html': 'True', # New plotting setting

        'plotting__average_markers_to_plot__include_gov_markers': 'True',
        'plotting__average_markers_to_plot__include_tv_markers': 'True',
        'plotting__average_markers_to_plot__include_tv_markers': 'True', # Duplicated, keeping for now as per original
        'plotting__average_markers_to_plot__include_markers': 'True',
        'plotting__average_markers_to_plot__include_intermod_markers': 'False', # NEW
        'plotting__average_markers_to_plot__math_average': 'True',
        'plotting__average_markers_to_plot__math_median': 'True',
        'plotting__average_markers_to_plot__math_range': 'True',
        'plotting__average_markers_to_plot__math_standard_deviation': 'True',
        'plotting__average_markers_to_plot__math_variance': 'True',
        'plotting__average_markers_to_plot__math_psd': 'True',
    }

def display_default_settings_structure():
    """
    Prints the content of DEFAULT_SETTINGS_STRUCTURE in a readable format.
    """
    print("\n--- DEFAULT SETTINGS STRUCTURE ---")
    for key, value in DEFAULT_SETTINGS_STRUCTURE.items():
        print(f"{key}: {value}")