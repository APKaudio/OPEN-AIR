# tabs/__init__.py
#
# This file serves as the main entry point for the 'tabs' package,
# organizing and importing various sub-modules related to instrument control,
# scanning, plotting, markers, presets, and experiments.
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
# Version 20250801.0938.1

current_version = "20250801.0938.1" # This variable should always be defined below the header to make the debugging better

# tabs
#     tabs.Instrument
#         __init__.py
#         tab_instrument_child_connection.py
#         tab_instrument_child_visa_interpreter.py
#         TAB_INSTRUMENT_PARENT.py
#         utils_instrument_control.py
#         utils_yak_visa.py
#     tabs.Scanning
#         __init__.py
#         tab_scanning_child_scan_configuration.py
#         tab_scanning_child_scan_meta_data.py
#         TAB_SCANNING_PARENT.py
#         utils_scan_instrument.py
#     tabs.Plotting
#         __init__.py
#         tab_plotting_child_3D.py
#         tab_plotting_child_average.py
#         tab_plotting_child_Single.py
#         TAB_PLOTTING_PARENT.py
#         utils_plotting_runs_over_time.py
#         utils_plotting.py
#     tabs.Markers
#         __init__.py
#         tab_markers_child_display.py
#         tab_markers_child_import_and_edit.py
#         TAB_MARKERS_PARENT.py
#         utils_markers.py
#     tabs.Presets
#         __init__.py
#         tab_presets_child_initial_configuration.py
#         tab_presets_child_preset.py
#         TAB_PRESETS_PARENT.py
#         utils_preset.py
#     tabs.Experiments
#         __init__.py
#         tab_experiments_child_intermod.py
#         tab_experiments_child_JSON_api.py
#         TAB_EXPERIMENTS_PARENT.py
#     __init__.py
