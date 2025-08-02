# process_math/report_converter_utils.py
#
# This module provides utility functions for converting wireless microphone
# frequency coordination reports from various formats (HTML, PDF, SHW) into a
# standardized CSV format. It extracts relevant frequency, zone, and device
# information, making it suitable for further analysis and intermodulation calculations.
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
# Version 20250802.0125.1 (Added generate_csv_from_shw function.)

current_version = "20250802.0125.1" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 125 * 1 # Example hash, adjust as needed

import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import re
from bs4 import BeautifulSoup # BeautifulSoup is imported here, no need for try-except block in this file
import pdfplumber # Import pdfplumber for PDF conversion
import inspect # Import inspect module for debug_log

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log # Added for console_print_func


def convert_html_report_to_csv(html_content, console_print_func=None):
    """
    Function Description:
    Converts the HTML frequency coordination report into a list of dictionaries
    suitable for CSV output, handling multiple zones. This version is based on
    the IAS HTML to CSV.py prototype for accurate extraction.
    All frequencies are converted to MHz for consistency.

    Inputs:
        html_content (str): The full HTML content of the report.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. Defaults to console_log if None.

    Returns:
        tuple: A tuple containing:
               - list: A list of strings representing the CSV headers.
               - list: A list of dictionaries, where each dictionary represents a row
                       with keys matching the headers.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Converting HTML report to CSV. Parsing the web!",
                file=current_file, version=current_version, function=current_function)

    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ"]
    csv_data = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables with the specific class
        tables = soup.find_all('table', class_='table table-striped table-bordered table-condensed')

        if not tables:
            console_print_func("⚠️ No tables with class 'table table-striped table-bordered table-condensed' found in HTML. Is this the right format?")
            debug_log("No target tables found in HTML. HTML parsing failed!",
                        file=current_file, version=current_version, function=current_function)
            return headers, []

        for table_idx, table in enumerate(tables):
            debug_log(f"Processing table {table_idx + 1}/{len(tables)}.",
                        file=current_file, version=current_version, function=current_function)
            
            # Extract zone name from the preceding h4 tag, if available
            zone_name_tag = table.find_previous_sibling('h4')
            current_zone = zone_name_tag.text.strip() if zone_name_tag else f"Zone_{table_idx + 1}"
            debug_log(f"  Identified Zone: {current_zone}. Zone found!",
                        file=current_file, version=current_version, function=current_function)

            rows = table.find_all('tr')
            # Skip header row if present (assuming the first tr is header)
            data_rows = rows[1:] if rows and rows[0].find('th') else rows

            for row_idx, row in enumerate(data_rows):
                cols = row.find_all('td')
                if len(cols) >= 4: # Expect at least 4 columns: Group, Device, Name, Frequency
                    group_csv = cols[0].text.strip()
                    device_csv = cols[1].text.strip()
                    name_csv = cols[2].text.strip()
                    freq_html_str = cols[3].text.strip()

                    # Extract numeric frequency and unit (MHz, kHz, GHz)
                    freq_match = re.match(r'([\d.]+)\s*([MGTK]?Hz)', freq_html_str, re.IGNORECASE)
                    freq_mhz_csv = "Invalid Frequency"
                    if freq_match:
                        value = float(freq_match.group(1))
                        unit = freq_match.group(2).lower()
                        if unit == 'mhz':
                            freq_mhz_csv = round(value, 3)
                        elif unit == 'khz':
                            freq_mhz_csv = round(value / 1000, 3)
                        elif unit == 'ghz':
                            freq_mhz_csv = round(value * 1000, 3)
                        else:
                            debug_log(f"    Unknown frequency unit '{unit}' for value '{freq_html_str}'. Assuming MHz. Unit problem!",
                                        file=current_file, version=current_version, function=current_function)
                            freq_mhz_csv = round(value, 3) # Default to MHz if unit unknown
                    else:
                        debug_log(f"    Could not parse frequency string '{freq_html_str}'. Setting to 'Invalid Frequency'. Parse error!",
                                    file=current_file, version=current_version, function=current_function)

                    csv_data.append({
                        "ZONE": current_zone,
                        "GROUP": group_csv,
                        "DEVICE": device_csv,
                        "NAME": name_csv,
                        "FREQ": freq_mhz_csv
                    })
                    debug_log(f"    Added HTML row: Zone={current_zone}, Device={device_csv}, Freq={freq_mhz_csv} MHz. Row processed!",
                                file=current_file, version=current_version, function=current_function)
                else:
                    debug_log(f"    Skipping row {row_idx + 1} in table {table_idx + 1}: Insufficient columns ({len(cols)}). Incomplete data!",
                                file=current_file, version=current_version, function=current_function)

        console_print_func(f"Finished HTML report conversion. Extracted {len(csv_data)} rows. All done!")
        debug_log(f"Exiting {current_function}. HTML conversion complete! Extracted {len(csv_data)} rows. Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return headers, csv_data

    except Exception as e:
        error_msg = f"❌ Error during HTML conversion: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise # Re-raise to allow higher-level error handling


def convert_pdf_report_to_csv(pdf_file_path, console_print_func=None):
    """
    Function Description:
    Converts a PDF frequency coordination report into a list of dictionaries
    suitable for CSV output. It attempts to extract tabular data from the PDF.
    All frequencies are converted to MHz for consistency.

    Inputs:
        pdf_file_path (str): The full path to the PDF report file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. Defaults to console_log if None.

    Returns:
        tuple: A tuple containing:
               - list: A list of strings representing the CSV headers.
               - list: A list of dictionaries, where each dictionary represents a row
                       with keys matching the headers.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Converting PDF report to CSV: {pdf_file_path}. Reading the document!",
                file=current_file, version=current_version, function=current_function)

    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ"]
    csv_data = []

    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            debug_log(f"Opened PDF file: {pdf_file_path}. Total pages: {len(pdf.pages)}. Document ready!",
                        file=current_file, version=current_version, function=current_function)
            
            for page_idx, page in enumerate(pdf.pages):
                debug_log(f"  Processing page {page_idx + 1}/{len(pdf.pages)}.",
                            file=current_file, version=current_version, function=current_function)
                
                # Extract text to find zone names or other identifiers
                page_text = page.extract_text()
                zone_match = re.search(r'Zone:\s*(.+?)\n', page_text, re.IGNORECASE)
                current_zone = zone_match.group(1).strip() if zone_match else f"Page_{page_idx + 1}"
                debug_log(f"    Identified Zone (from text): {current_zone}. Zone found!",
                            file=current_file, version=current_version, function=current_function)

                tables = page.extract_tables()
                if not tables:
                    debug_log(f"    No tables found on page {page_idx + 1}.",
                                file=current_file, version=current_version, function=current_function)
                    continue

                for table_idx, table in enumerate(tables):
                    debug_log(f"      Processing table {table_idx + 1}/{len(tables)} on page {page_idx + 1}.",
                                file=current_file, version=current_version, function=current_function)
                    
                    # Assuming the first row of each extracted table might be headers
                    # We'll try to find "GROUP", "DEVICE", "NAME", "FREQ"
                    table_headers = table[0] if table else []
                    data_rows = table[1:] if len(table) > 1 and any(h in ["GROUP", "DEVICE", "NAME", "FREQ"] for h in table_headers) else table
                    
                    # Find column indices
                    try:
                        group_col_idx = table_headers.index('GROUP') if 'GROUP' in table_headers else 0
                        device_col_idx = table_headers.index('DEVICE') if 'DEVICE' in table_headers else 1
                        name_col_idx = table_headers.index('NAME') if 'NAME' in table_headers else 2
                        freq_col_idx = table_headers.index('FREQ') if 'FREQ' in table_headers else 3
                        debug_log(f"        Identified column indices: Group={group_col_idx}, Device={device_col_idx}, Name={name_col_idx}, Freq={freq_col_idx}. Columns mapped!",
                                    file=current_file, version=current_version, function=current_function)
                    except ValueError:
                        debug_log(f"        Could not find expected headers in table {table_idx + 1} on page {page_idx + 1}. Attempting to use default column order. Header problem!",
                                    file=current_file, version=current_version, function=current_function)
                        # Fallback to fixed indices if headers not found or incomplete
                        group_col_idx, device_col_idx, name_col_idx, freq_col_idx = 0, 1, 2, 3


                    for row_idx, row in enumerate(data_rows):
                        # Ensure row has enough columns
                        if len(row) > max(group_col_idx, device_col_idx, name_col_idx, freq_col_idx):
                            group_csv = row[group_col_idx].strip() if row[group_col_idx] else ""
                            device_csv = row[device_col_idx].strip() if row[device_col_idx] else ""
                            name_csv = row[name_col_idx].strip() if row[name_col_idx] else ""
                            frequency_pdf_str = row[freq_col_idx].strip() if row[freq_col_idx] else ""

                            # Clean frequency string (remove commas, extra spaces)
                            frequency_pdf_str = frequency_pdf_str.replace(',', '').strip()

                            freq_mhz_csv = "Invalid Frequency"
                            if frequency_pdf_str:
                                # Regex to extract numeric frequency and unit (MHz, kHz, GHz)
                                freq_match = re.match(r'([\d.]+)\s*([MGTK]?Hz)?', frequency_pdf_str, re.IGNORECASE)
                                if freq_match:
                                    value = float(freq_match.group(1))
                                    unit = freq_match.group(2) # Can be None if no unit specified
                                    if unit:
                                        unit = unit.lower()
                                    
                                    if unit == 'mhz' or unit is None: # Assume MHz if no unit
                                        freq_mhz_csv = round(value, 3)
                                    elif unit == 'khz':
                                        freq_mhz_csv = round(value / 1000, 3)
                                    elif unit == 'ghz':
                                        freq_mhz_csv = round(value * 1000, 3)
                                    else:
                                        debug_log(f"          Unknown frequency unit '{unit}' for value '{frequency_pdf_str}'. Assuming MHz. Unit problem!",
                                                    file=current_file, version=current_version, function=current_function)
                                        freq_mhz_csv = round(value, 3) # Default to MHz if unit unknown
                                else:
                                    # Try direct conversion if regex fails (e.g., just a number)
                                    try:
                                        freq_mhz_csv = round(float(frequency_pdf_str), 3)
                                        debug_log(f"          PDF Freq direct conversion: '{frequency_pdf_str}' -> {freq_mhz_csv} MHz",
                                                    file=current_file, version=current_version, function=current_function)
                                    except ValueError:
                                        console_print_func(f"WARNING (PDF): Could not convert PDF frequency value '{frequency_pdf_str}' to float (MHz). Setting to 'Invalid Frequency'.")
                                        debug_log(f"          PDF Freq conversion error: '{frequency_pdf_str}'. Bad number!",
                                                    file=current_file, version=current_version, function=current_function)
                                        freq_mhz_csv = "Invalid Frequency"
                            else:
                                debug_log(f"          Empty frequency string in PDF row. Setting to 'Invalid Frequency'. Empty data!",
                                            file=current_file, version=current_version, function=current_function)
                                freq_mhz_csv = "Invalid Frequency"


                            csv_data.append({
                                "ZONE": current_zone,
                                "GROUP": group_csv,
                                "DEVICE": device_csv,
                                "NAME": name_csv,
                                "FREQ": freq_mhz_csv
                            })
                            debug_log(f"          Added PDF row: Zone={current_zone}, Device={device_csv}, Freq={freq_mhz_csv} MHz. Row processed!",
                                        file=current_file, version=current_version, function=current_function)
                        else:
                            debug_log(f"          Skipping row {row_idx + 1} in PDF table: Insufficient columns ({len(row)}). Incomplete data!",
                                        file=current_file, version=current_version, function=current_function)
        console_print_func(f"Finished PDF report conversion. Extracted {len(csv_data)} rows. All done!")
        debug_log(f"Exiting {current_function}. PDF conversion complete! Extracted {len(csv_data)} rows. Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return headers, csv_data

    except FileNotFoundError:
        error_msg = f"❌ Error: The file '{pdf_file_path}' was not found. Check the path!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise FileNotFoundError(f"The file '{pdf_file_path}' was not found.")
    except pdfplumber.PDFSyntaxError as e:
        error_msg = f"❌ PDF Syntax Error: The file '{pdf_file_path}' might be corrupted or malformed: {e}. Bad PDF!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise
    except Exception as e:
        error_msg = f"❌ Error during PDF conversion data extraction: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise # Re-raise to allow higher-level error handling


def generate_csv_from_shw(xml_file_path, console_print_func=None):
    """
    Parses an SHW (XML) file and extracts frequency data, converting it
    into a standardized CSV format. This version is based on the SHOW to CSV.py
    prototype for accurate extraction of ZONE and GROUP.
    All frequencies are converted to MHz for consistency.

    Inputs:
        xml_file_path (str): The full path to the SHW (XML) file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses console_log.
    Outputs:
        tuple: A tuple containing:
                - headers (list): A list of strings representing the CSV header row.
                - csv_data (list): A list of dictionaries, where each dictionary
                                   represents a row of data with keys matching the headers.
    Raises:
        FileNotFoundError: If the specified XML file does not exist.
        xml.etree.ElementTree.ParseError: If the XML file is malformed.
        Exception: For other parsing or data extraction errors.
    """
    console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
    current_function = inspect.currentframe().f_code.co_name
    current_file = __file__
    debug_log(f"Entering {current_function}. Starting SHW report conversion for '{os.path.basename(xml_file_path)}'. Parsing XML!",
                file=current_file, version=current_version, function=current_function)

    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ"]
    csv_data = []

    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        console_print_func("XML file parsed successfully.")
        debug_log("XML file parsed successfully. Ready for data extraction!",
                    file=current_file, version=current_version, function=current_function)

        # Iterate through 'freq_entry' elements
        for i, freq_entry in enumerate(root.findall('.//freq_entry')):
            if i % 100 == 0: # Print progress every 100 entries
                console_print_func(f"  Processing SHW entry {i}...")
                debug_log(f"  Processing SHW entry {i}.",
                            file=current_file, version=current_version, function=current_function)

            # Reverting ZONE and GROUP extraction to match SHOW to CSV.py prototype
            zone_element = freq_entry.find('compat_key/zone')
            zone = zone_element.text if zone_element is not None else "N/A"

            group = freq_entry.get('tag', "N/A") # Extract GROUP from the 'tag' attribute of freq_entry
            
            # Extract DEVICE (manufacturer, model, band)
            manufacturer = freq_entry.find('manufacturer').text if freq_entry.find('manufacturer') is not None else "N/A"
            model = freq_entry.find('model').text if freq_entry.find('model') is not None else "N/A"
            band_element = freq_entry.find('compat_key/band') 
            band = band_element.text if band_element is not None else "N/A"
            device = f"{manufacturer} - {model} - {band}"

            # Extract NAME
            name_element = freq_entry.find('source_name')
            name = name_element.text if name_element is not None else "N/A"

            # Extract FREQ from value. User states SHW files contain markers in KHZ.
            freq_element = freq_entry.find('value')
            freq_mhz = "N/A"
            if freq_element is not None and freq_element.text is not None:
                freq_str = freq_element.text 
                
                debug_log(f"DEBUG (SHW): Processing freq_str: '{freq_str}' for device '{name}'",
                            file=current_file, version=current_version, function=current_function)

                try:
                    # Convert kHz to MHz as per user's clarification
                    freq_mhz = float(freq_str) / 1000.0 
                    debug_log(f"  SHW Freq conversion: '{freq_str}' kHz -> {freq_mhz} MHz",
                                file=current_file, version=current_version, function=current_function)
                except ValueError:
                    console_print_func(f"WARNING (SHW): Could not convert SHW frequency value '{freq_str}' to float. Setting to 'Invalid Frequency'.")
                    debug_log(f"  SHW Freq conversion error: '{freq_str}'. Bad number!",
                                file=current_file, version=current_version, function=current_function)
                    freq_mhz = "Invalid Frequency"

            csv_data.append({
                "ZONE": zone,
                "GROUP": group,
                "DEVICE": device,
                "NAME": name,
                "FREQ": freq_mhz # Store in MHz
            })
            debug_log(f"  Added SHW row: Zone={zone}, Device={device}, Freq={freq_mhz} MHz. Row processed!",
                        file=current_file, version=current_version, function=current_function)
        console_print_func(f"Finished SHW report conversion. Extracted {len(csv_data)} rows. All done!")
        debug_log(f"Exiting {current_function}. SHW conversion complete! Extracted {len(csv_data)} rows. Version: {current_version}",
                    file=current_file, version=current_version, function=current_function)
        return headers, csv_data

    except FileNotFoundError:
        error_msg = f"❌ Error: The file '{xml_file_path}' was not found. Check the path!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise FileNotFoundError(f"The file '{xml_file_path}' was not found.")
    except ET.ParseError as e:
        error_msg = f"❌ Error: Malformed XML (SHW) file '{xml_file_path}': {e}. XML parse error!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise ET.ParseError(f"Error parsing XML (SHW) file '{xml_file_path}': {e}")
    except Exception as e:
        error_msg = f"❌ Error during SHW conversion data extraction: {e}. This is a disaster!"
        console_print_func(error_msg)
        debug_log(error_msg,
                    file=current_file, version=current_version, function=current_function)
        raise # Re-raise to allow higher-level error handling
