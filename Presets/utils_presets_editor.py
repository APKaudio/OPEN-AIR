# tabs/Presets/utils_presets_editor.py
#
# This file provides utility functions and classes for managing user-defined
# presets. It handles loading, saving, importing, exporting, and manipulating
# presets data in a decoupled way from the GUI elements.
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
#
# Version 20250814.162500.1 (REBUILT: Extracted all logic from PresetEditorTab to separate data from the GUI.)

current_version = "20250814.162500.1"
current_version_hash = 20250814 * 162500 * 1

import inspect
import os
import csv
from datetime import datetime
import shutil
import pandas as pd
import numpy as np

from display.debug_logic import debug_log
from display.console_logic import console_log
from .utils_preset_csv_process import (
    get_presets_csv_path,
    load_user_presets_from_csv,
    overwrite_user_presets_csv
)
from Instrument.connection.instrument_logic import query_current_settings_logic
from ref.ref_file_paths import PRESETS_FILE_PATH

class PresetEditorLogic:
    def __init__(self, app_instance, console_print_func, columns):
        self.app_instance = app_instance
        self.console_print_func = console_print_func
        self.columns = columns
        self.presets_data = []
        self.has_unsaved_changes = False

    def load_presets(self):
        """Loads presets from the CSV file into memory."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Loading presets from CSV into memory.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        self.presets_data = load_user_presets_from_csv(PRESETS_FILE_PATH, self.console_print_func)
        self.has_unsaved_changes = False

    def save_presets(self):
        """Saves the current presets in memory to the CSV file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Saving all presets from memory to PRESETS.CSV.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        fieldnames_for_save = [col.split(' ')[0] for col in self.columns]
        if overwrite_user_presets_csv(self.app_instance.CONFIG_FILE_PATH, self.presets_data, self.console_print_func, fieldnames=fieldnames_for_save):
            self.has_unsaved_changes = False
            return True
        return False

    def add_current_settings(self):
        """Queries current instrument settings and adds them as a new preset."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Attempting to add current settings.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not self.app_instance.inst:
            self.console_print_func("❌ No instrument connected. Cannot get current settings. Connect first!")
            return False

        current_settings = query_current_settings_logic(self.app_instance, self.console_print_func)
        if current_settings:
            timestamp_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamp_nickname = datetime.now().strftime('%Y%m%d %H%M')

            center_freq_mhz = current_settings.get('center_freq_mhz')
            span_mhz = current_settings.get('span_mhz')
            start_freq_mhz = center_freq_mhz - (span_mhz / 2) if center_freq_mhz is not None and span_mhz is not None else ''
            stop_freq_mhz = center_freq_mhz + (span_mhz / 2) if center_freq_mhz is not None and span_mhz is not None else ''

            new_preset = {
                'Filename': f"USER_{timestamp_filename}.STA",
                'NickName': f"Device {timestamp_nickname}",
                'Start': f"{start_freq_mhz:.3f}" if isinstance(start_freq_mhz, (int, float)) else '',
                'Stop': f"{stop_freq_mhz:.3f}" if isinstance(stop_freq_mhz, (int, float)) else '',
                'Center': f"{center_freq_mhz:.3f}" if isinstance(center_freq_mhz, (int, float)) else '',
                'Span': f"{span_mhz:.3f}" if isinstance(span_mhz, (int, float)) else '',
                'RBW': f"{current_settings.get('rbw_hz'):.0f}" if isinstance(current_settings.get('rbw_hz'), (int, float)) else '',
                'VBW': f"{current_settings.get('vbw_hz'):.0f}" if isinstance(current_settings.get('vbw_hz'), (int, float)) else '',
                'RefLevel': f"{current_settings.get('ref_level_dbm'):.1f}" if isinstance(current_settings.get('ref_level_dbm'), (int, float)) else '',
                'Attenuation': f"{current_settings.get('attenuation_db'):.0f}" if isinstance(current_settings.get('attenuation_db'), (int, float)) else '',
                'MaxHold': 'ON' if current_settings.get('maxhold_enabled') else 'OFF',
                'HighSens': 'ON' if current_settings.get('high_sensitivity_on') else 'OFF',
                'PreAmp': 'ON' if current_settings.get('preamp_on') else 'OFF',
                'Trace1Mode': current_settings.get('trace1_mode', ''),
                'Trace2Mode': current_settings.get('trace2_mode', ''),
                'Trace3Mode': current_settings.get('trace3_mode', ''),
                'Trace4Mode': current_settings.get('trace4_mode', ''),
                'Marker1Max': 'WRITE' if current_settings.get('marker1_calc_max') else '',
                'Marker2Max': 'WRITE' if current_settings.get('marker2_calc_max') else '',
                'Marker3Max': 'WRITE' if current_settings.get('marker3_calc_max') else '',
                'Marker4Max': 'WRITE' if current_settings.get('marker4_calc_max') else '',
                'Marker5Max': 'WRITE' if current_settings.get('marker5_calc_max') else '',
                'Marker6Max': 'WRITE' if current_settings.get('marker6_calc_max') else '',
            }
            self.presets_data.append(new_preset)
            self.has_unsaved_changes = True
            self.console_print_func("✅ Current instrument settings added as a new preset. Remember to save your changes!")
            return True
        else:
            self.console_print_func("❌ Failed to query all current settings from instrument. Some values were missing.")
            return False

    def add_new_empty_row(self):
        """Adds a new empty row to the presets list with default values."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log("Adding new empty row.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        new_empty_preset = {col.split(' ')[0]: '' for col in self.columns}
        new_empty_preset['Filename'] = f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}.STA"
        new_empty_preset['NickName'] = "New Preset"
        new_empty_preset['Start'] = "100.0"
        new_empty_preset['Stop'] = "200.0"
        new_empty_preset['Center'] = "150.0"
        new_empty_preset['Span'] = "100.0"
        new_empty_preset['RBW'] = "100000.0"
        self.presets_data.append(new_empty_preset)
        self.has_unsaved_changes = True
        self.console_print_func("✅ New empty row added. Remember to save your changes!")
        return True

    def delete_presets(self, selected_filenames):
        """Deletes selected presets from the list."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Deleting presets: {selected_filenames}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        initial_len = len(self.presets_data)
        self.presets_data = [p for p in self.presets_data if p.get('Filename') not in selected_filenames]
        deleted_count = initial_len - len(self.presets_data)
        
        if deleted_count > 0:
            self.has_unsaved_changes = True
            self.console_print_func(f"✅ Deleted {deleted_count} preset(s). Automatically saving changes...")
            return True
        return False
        
    def update_preset_value(self, filename, column_name, new_value):
        """Updates a single value in a preset."""
        current_function = inspect.currentframe().f_code.co_name
        for preset in self.presets_data:
            if preset.get('Filename') == filename:
                if str(preset.get(column_name, '')) != new_value:
                    preset[column_name] = new_value
                    self.has_unsaved_changes = True
                    self.console_print_func(f"✅ Updated '{column_name}' for '{preset.get('NickName', filename)}' to '{new_value}'. Automatically saving changes!")
                    return True
        return False

    def import_presets(self, file_path):
        """Imports presets from a CSV file, replacing current data."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Importing presets from {file_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        try:
            df_imported = pd.read_csv(file_path)
            imported_presets = df_imported.to_dict(orient='records')
            
            for preset in imported_presets:
                for key, value in preset.items():
                    if pd.isna(value):
                        preset[key] = ''
                    elif isinstance(value, (float, np.float64)) and value.is_integer():
                        preset[key] = str(int(value))
                    else:
                        preset[key] = str(value)
            
            self.presets_data = imported_presets
            self.has_unsaved_changes = True
            self.console_print_func(f"✅ Successfully imported {len(imported_presets)} presets. Automatically saving changes...")
            return True
        except Exception as e:
            self.console_print_func(f"❌ Error importing presets: {e}. Check file format.")
            return False

    def export_presets(self, file_path):
        """Exports the current presets data to a new CSV file."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Exporting presets to {file_path}.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        if not self.presets_data:
            self.console_print_func("⚠️ No presets to export. Add some first!")
            return False

        try:
            fieldnames = [col.split(' ')[0] for col in self.columns]
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for preset in self.presets_data:
                    row_to_write = {field: preset.get(field, '') for field in fieldnames}
                    writer.writerow(row_to_write)
            self.console_print_func(f"✅ Successfully exported {len(self.presets_data)} presets to {os.path.basename(file_path)}.")
            return True
        except Exception as e:
            self.console_print_func(f"❌ Error exporting presets: {e}. This is a disaster!")
            return False
            
    def move_preset_up(self, filename):
        """Moves a preset one position up."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Moving preset '{filename}' up.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)
        
        for i, p in enumerate(self.presets_data):
            if p.get('Filename') == filename:
                if i > 0:
                    self.presets_data[i-1], self.presets_data[i] = self.presets_data[i], self.presets_data[i-1]
                    self.has_unsaved_changes = True
                    return True
                break
        return False

    def move_preset_down(self, filename):
        """Moves a preset one position down."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Moving preset '{filename}' down.",
                    file=f"{os.path.basename(__file__)} - {current_version}",
                    version=current_version,
                    function=current_function)

        for i, p in enumerate(self.presets_data):
            if p.get('Filename') == filename:
                if i < len(self.presets_data) - 1:
                    self.presets_data[i], self.presets_data[i+1] = self.presets_data[i+1], self.presets_data[i]
                    self.has_unsaved_changes = True
                    return True
                break
        return False
