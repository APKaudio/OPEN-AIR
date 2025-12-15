# workers/Importer/worker_importer_loader.py
#
# A complete and comprehensive pre-amble that describes the file and the functions within.
# The purpose is to provide clear documentation and versioning.
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251213
Current_Time = 120000
Current_iteration = 44

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)


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

import inspect
from tkinter import filedialog
from display.logger import debug_log, console_log
from workers.importers.worker_marker_file_import_handling import (
    maker_file_load_markers_file,
    maker_file_load_ias_html,
    maker_file_load_wwb_shw,
    maker_file_load_sb_pdf,
)
from workers.importers.worker_marker_file_import_converter import (
    Marker_convert_wwb_zip_report_to_csv,
    Marker_convert_SB_v2_PDF_File_report_to_csv
)
from workers.Importer.worker_importer_saver import save_markers_file_internally

Local_Debug_Enable = True

def load_markers_file_action(importer_tab_instance):
    headers, data = maker_file_load_markers_file()
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)

def load_ias_html_action(importer_tab_instance):
    headers, data = maker_file_load_ias_html()
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)

def load_wwb_shw_action(importer_tab_instance):
    headers, data = maker_file_load_wwb_shw()
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)

def load_wwb_zip_action(importer_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".zip",
        filetypes=[("Shure Wireless Workbench files", "*.zip"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load WWB.zip' action cancelled by user.",
            file=importer_tab_instance.current_file,
            version=importer_tab_instance.current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return
    headers, data = Marker_convert_wwb_zip_report_to_csv(file_path=file_path)
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)

def load_sb_pdf_action(importer_tab_instance):
    headers, data = maker_file_load_sb_pdf()
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)

def load_sb_v2_pdf_action(importer_tab_instance):
    current_function = inspect.currentframe().f_code.co_name
    file_path = filedialog.askopenfilename(
        defaultextension=".pdf",
        filetypes=[("Sound Base V2 PDF files", "*.pdf"), ("All files", "*.*")]
    )
    if not file_path:
        debug_log(
            message="🛠️🟡 'Load SB V2.pdf' action cancelled by user.",
            file=importer_tab_instance.current_file,
            version=importer_tab_instance.current_version,
            function=f"{current_function}",
            console_print_func=console_log
        )
        return
    headers, data = Marker_convert_SB_v2_PDF_File_report_to_csv(pdf_file_path=file_path)
    if headers and data:
        importer_tab_instance.tree_headers = headers
        importer_tab_instance.tree_data = data
        importer_tab_instance._update_treeview()
        save_markers_file_internally(importer_tab_instance)
