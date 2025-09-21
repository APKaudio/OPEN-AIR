# worker/worker_marker_report_converter.py
#
# This file contains utility functions for converting various spectrum analyzer
# report formats (HTML, SHW, Soundbase PDF) into a standardized CSV format.
# This version specifically restores the logic from the previously provided
# 'old_report_converter_utils.py' and adapts it to the new logging system.
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
# Version 20250815.200000.3 (FIXED: The headers for CSV conversions now include a "Peak" column with a placeholder value to prevent data loss.)

import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import re
from bs4 import BeautifulSoup
import pdfplumber
import inspect
import numpy as np

# Updated imports for new logging functions
from workers.worker_logging import debug_log, console_log


def convert_html_report_to_csv(html_content):
    """
    Converts the HTML frequency coordination report into a list of dictionaries
    suitable for CSV output, handling multiple zones. This version is based on
    the IAS HTML to CSV.py prototype for accurate extraction.
    All frequencies are converted to MHz for consistency.

    Inputs:
        html_content (str): The full HTML content of the report.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.

    Returns:
        tuple: A tuple containing:
               - list: A list of strings representing the CSV headers.
               - list: A list of dictionaries, where each dictionary represents a row
                       in the CSV and keys are column headers.
    """
    
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__) # Get current file name for debug_log

    
    debug_log("Starting HTML report conversion.", file=current_file, function=current_function)

    soup = BeautifulSoup(html_content, 'html.parser')
    
    csv_headers = [
        "ZONE",
        "GROUP",
        "DEVICE",
        "NAME",
        "FREQ",
        "Peak" # NEW: Added Peak header
    ]
    
    data_rows = []

    # Find the main content area within the HTML, based on the IAS prototype.
    main_content_container = None
    
    first_zone_p = soup.find('p', style=lambda value: value and 'font-size: large' in value and 'text-decoration: underline' in value)

    if first_zone_p:
        main_content_container = first_zone_p.find_parent('span')
        
        debug_log(f"Found main content container based on first zone paragraph.", file=current_file, function=current_function)
    
    if not main_content_container:
        main_table = soup.find('table', class_='MainTable')
        if main_table:
            main_table_trs = main_table.find_all('tr')
            if len(main_table_trs) > 1:
                second_tr_td = main_table_trs[1].find('td')
                if second_tr_td:
                    potential_span_wrapper = second_tr_td.find('span')
                    if potential_span_wrapper:
                        main_content_container = potential_span_wrapper
                    else:
                        main_content_container = second_tr_td
                    
                    debug_log(f"Found main content container based on MainTable structure.", file=current_file, function=current_function)
    
    if not main_content_container:
        
        debug_log("Warning: Could not find the main content container. No data will be extracted.", file=current_file, function=current_function)
        return csv_headers, data_rows

    current_zone_type = ""
    # Iterate through the children of the identified main content container
    for element in main_content_container.children:
        if element.name == 'p' and element.get('style') and \
           'font-size: large' in element.get('style') and \
           'text-decoration: underline' in element.get('style'):
            zone_text = element.get_text(strip=True)
            if zone_text.startswith("Zone:"):
                current_zone_type = zone_text.replace("Zone:", "").strip()
        
                debug_log(f"Processing Zone: {current_zone_type}", file=current_file, function=current_function)
        
        elif element.name == 'table' and 'Assignment' in element.get('class', []):
            table = element
            
            device_name_tag = table.find('th')
            current_group_name = device_name_tag.get_text(strip=True) if device_name_tag else ""
        
            debug_log(f"Processing Group: {current_group_name}", file=current_file, function=current_function)

            rows_in_table = table.find_all('tr')[1:] # Skip the first row as it contains the <th> (device_name)
            debug_log(f"Found {len(rows_in_table)} rows in current table.", file=current_file, function=current_function)

            for row in rows_in_table:
                data_spans = row.find_all('span')
                
                if data_spans:
                    for data_span in data_spans:
                        cells = data_span.find_all('td')
                        if len(cells) >= 4:
                            band_type = cells[0].get_text(strip=True)
                            
                            channel_frequency_tag = cells[3].find('b')
                            channel_frequency_str = channel_frequency_tag.get_text(strip=True) if channel_frequency_tag else ""

                            channel_name = cells[1].get_text(strip=True)
                            if not channel_name:
                                channel_name = cells[2].get_text(strip=True)
                            
                            # Convert frequency string to MHz
                            freq_MHz = "N/A"
                            try:
                                freq_match = re.search(r'(\d+(\.\d+)?)\s*(kHz|MHz|GHz)', channel_frequency_str, re.IGNORECASE)
                                if freq_match:
                                    value = float(freq_match.group(1))
                                    unit = freq_match.group(3).lower()
                                    if unit == 'mhz':
                                        freq_MHz = value
                                    elif unit == 'ghz':
                                        freq_MHz = value * 1000 # GHz to MHz
                                    elif unit == 'khz':
                                        freq_MHz = value / 1000 # kHz to MHz
                                    debug_log(f"HTML Freq conversion: '{channel_frequency_str}' -> {freq_MHz} MHz", file=current_file, function=current_function)
                                else:
                                    # Fallback if regex doesn't match, assume MHz
                                    freq_MHz = float(channel_frequency_str) # Assume it's already in MHz
    
                                    debug_log(f"HTML Freq conversion (fallback): '{channel_frequency_str}' -> {freq_MHz} MHz", file=current_file, function=current_function)
                            except ValueError:
    
                                debug_log(f"HTML Freq conversion error: '{channel_frequency_str}'", file=current_file, function=current_function)
                                freq_MHz = "Invalid Frequency"

                            row_data = {
                                "ZONE": current_zone_type,
                                "GROUP": current_group_name,
                                "DEVICE": band_type,
                                "NAME": channel_name,
                                "FREQ": freq_MHz, # Store in MHz
                                "Peak": np.nan # NEW: Added Peak column
                            }
                            if band_type or channel_frequency_str or channel_name:
                                data_rows.append(row_data)
                                debug_log(f"Added HTML row: {row_data}", file=current_file, function=current_function)
                else:
                    # Process rows that have <td>s directly (e.g., blank rows or specific structures without inner spans)
                    cells = row.find_all('td')
                    if len(cells) >= 4: 
                        band_type = cells[0].get_text(strip=True)
                        channel_frequency_tag = cells[3].find('b')
                        channel_frequency_str = channel_frequency_tag.get_text(strip=True) if channel_frequency_tag else ""
                        
                        channel_name = cells[1].get_text(strip=True)
                        if not channel_name:
                            channel_name = cells[2].get_text(strip=True)

                        # Convert frequency string to MHz
                        freq_MHz = "N/A"
                        try:
                            freq_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:(k|m|g)?hz)?', channel_frequency_str, re.IGNORECASE)
                            if freq_match:
                                value = float(freq_match.group(1))
                                unit_group = freq_match.group(3)
                                if unit_group:
                                    unit = unit_group.lower()
                                    if unit == 'm': # MHz
                                        freq_MHz = value
                                    elif unit == 'g': # GHz
                                        freq_MHz = value * 1000
                                    elif unit == 'k': # kHz
                                        freq_MHz = value / 1000
                                else: # No unit specified, assume MHz
                                    freq_MHz = value
                                debug_log(f"HTML Freq conversion (direct td): '{channel_frequency_str}' -> {freq_MHz} MHz", file=current_file, function=current_function)
                            else:
                                # Fallback if regex doesn't match, assume MHz
                                freq_MHz = float(channel_frequency_str) # Assume it's already in MHz
    
                                debug_log(f"HTML Freq conversion (direct td, fallback): '{channel_frequency_str}' -> {freq_MHz} MHz", file=current_file, function=current_function)
                        except ValueError:
    
                            debug_log(f"HTML Freq conversion error (direct td): '{channel_frequency_str}'", file=current_file, function=current_function)
                            freq_MHz = "Invalid Frequency"

                        row_data = {
                            "ZONE": current_zone_type,
                            "GROUP": current_group_name,
                            "DEVICE": band_type,
                            "NAME": channel_name,
                            "FREQ": freq_MHz, # Store in MHz
                            "Peak": np.nan # NEW: Added Peak column
                        }
                        if band_type or channel_frequency_str or channel_name:
                            data_rows.append(row_data)
                            debug_log(f"Added HTML row (direct td): {row_data}", file=current_file, function=current_function)
    
    debug_log(f"Finished HTML report conversion. Extracted {len(data_rows)} rows.", file=current_file, function=current_function)
    return csv_headers, data_rows


def generate_csv_from_shw(xml_file_path):
    """
    Parses an SHW (XML) file and extracts frequency data, converting it
    into a standardized CSV format. This version is based on the SHOW to CSV.py
    prototype for accurate extraction of ZONE and GROUP.
    All frequencies are converted to MHz for consistency.

    Inputs:
        xml_file_path (str): The full path to the SHW (XML) file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.
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
    
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__)

    
    debug_log(f"Starting SHW report conversion for '{os.path.basename(xml_file_path)}'.", file=current_file, function=current_function)

    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ", "Peak"] # NEW: Added Peak header
    csv_data = []

    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        
        debug_log("XML file parsed successfully.", file=current_file, function=current_function)

        # Iterate through 'freq_entry' elements
        for i, freq_entry in enumerate(root.findall('.//freq_entry')):
            if i % 100 == 0: # Print progress every 100 entries
                
                debug_log(f"Processing SHW entry {i}...", file=current_file, function=current_function)

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
            freq_MHz = "N/A"
            if freq_element is not None and freq_element.text is not None:
                freq_str = freq_element.text 
                
                debug_log(f"DEBUG (SHW): Processing freq_str: '{freq_str}' for device '{name}'", file=current_file, function=current_function)

                try:
                    # Convert kHz to MHz as per user's clarification
                    freq_MHz = float(freq_str) / 1000.0 
                    debug_log(f"SHW Freq conversion: '{freq_str}' kHz -> {freq_MHz} MHz", file=current_file, function=current_function)
                except ValueError:
    
                    debug_log(f"SHW Freq conversion error: '{freq_str}'", file=current_file, function=current_function)
                    freq_MHz = "Invalid Frequency"

            csv_data.append({
                "ZONE": zone,
                "GROUP": group,
                "DEVICE": device,
                "NAME": name,
                "FREQ": freq_MHz, # Store in MHz
                "Peak": np.nan # NEW: Added Peak column
            })
    
        debug_log(f"Finished SHW report conversion. Extracted {len(csv_data)} rows.", file=current_file, function=current_function)
        return headers, csv_data

    except FileNotFoundError:
    
        debug_log(f"Error: The file '{xml_file_path}' was not found.", file=current_file, function=current_function)
        raise FileNotFoundError(f"The file '{xml_file_path}' was not found.")
    except ET.ParseError as e:
    
        debug_log(f"Error: Malformed XML (SHW) file '{xml_file_path}': {e}", file=current_file, function=current_function)
        raise ET.ParseError(f"Error parsing XML (SHW) file '{xml_file_path}': {e}")
    except Exception as e:
    
        debug_log(f"Error during SHW conversion data extraction: {e}", file=current_file, function=current_function)
        raise

def convert_pdf_report_to_csv(pdf_file_path):
    """
    Parses a PDF file (Sound Base format) and extracts frequency data, converting it
    into a standardized CSV format. This function maps PDF fields to the MARKERS.CSV
    structure as follows:
    - PDF 'Group' -> CSV 'ZONE'
    - PDF 'Model' -> CSV 'GROUP'
    - PDF 'Name' -> CSV 'NAME'
    - PDF 'Frequency' -> CSV 'FREQ' (in MHz)
    - CSV 'DEVICE' is constructed from PDF 'Model', 'Band', and 'Preset'.

    Inputs:
        pdf_file_path (str): The full path to the PDF file.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.
    Outputs:
        tuple: A tuple containing:
               - headers (list): A list of strings representing the CSV header row.
               - csv_data (list): A list of dictionaries, where each dictionary
                                  represents a row of data with keys matching the headers.
    Raises:
        FileNotFoundError: If the specified PDF file does not exist.
        Exception: For other parsing or data extraction errors.
    """
    
    current_function = inspect.currentframe().f_code.co_name
    current_file = os.path.basename(__file__)

    
    debug_log(f"Starting PDF report conversion for '{os.path.basename(pdf_file_path)}'.", file=current_file, function=current_function)

    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ", "Peak"] # NEW: Added Peak header
    csv_data = []

    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            last_known_group = "Uncategorized" # Default group if not found
            
            debug_log(f"Opened PDF with {len(pdf.pages)} pages.", file=current_file, function=current_function)

            for page_num, page in enumerate(pdf.pages):
        
                debug_log(f"Processing Page {page_num + 1}...", file=current_file, function=current_function)
                # Extract text for group headers
                lines = page.extract_text().splitlines()
                lines = [line.strip() for line in lines if line.strip()]

                group_headers = [(i, line) for i, line in enumerate(lines)
                                 if re.match(r".+\(\d+ frequencies\)", line)]

                tables = page.extract_tables()
                debug_log(f"Found {len(tables)} tables on Page {page_num + 1}.", file=current_file, function=current_function)

                group_index = 0
                for table_num, table in enumerate(tables):
                    if group_index < len(group_headers):
                        last_known_group = group_headers[group_index][1]
                        group_index += 1

                    current_zone = last_known_group # PDF Group -> CSV ZONE
        
                    debug_log(f"Processing Table {table_num + 1} for Zone: {current_zone}", file=current_file, function=current_function)

                    for row_num, row in enumerate(table):
                        if not row or all(cell is None or cell.strip() == "" for cell in row):
                            continue

                        if "Model" in row[0] and "Frequency" in row[-1]: # Skip header rows
                            debug_log(f"Skipping header row: {row}", file=current_file, function=current_function)
                            continue

                        clean_row = [cell.replace("\n", " ").strip() if cell else "" for cell in row]
                        # Ensure row has at least 6 elements to unpack safely
                        while len(clean_row) < 6:
                            clean_row.append("")

                        model_pdf, band_pdf, name_pdf, preset_pdf, spacing_pdf, frequency_pdf_str = clean_row

                        if model_pdf.strip() == current_zone.strip(): # Skip rows that mistakenly repeat the group name
                            debug_log(f"Skipping duplicate group name row: {row}", file=current_file, function=current_function)
                            continue

                        # Map PDF fields to CSV fields
                        zone_csv = current_zone
                        group_csv = model_pdf # PDF Model -> CSV GROUP

                        # Construct DEVICE from PDF Model, Band, Preset
                        device_csv = f"{model_pdf}"
                        if band_pdf:
                            device_csv += f" - {band_pdf}"
                        if preset_pdf:
                            device_csv += f" - {preset_pdf}"
                        
                        name_csv = name_pdf # PDF Name -> CSV NAME

                        freq_MHz_csv = "N/A"
                        try:
                            # The frequency is already in MHz, so no conversion needed
                            freq_MHz_csv = float(frequency_pdf_str)
                            debug_log(f"PDF Freq conversion: '{frequency_pdf_str}' -> {freq_MHz_csv} MHz", file=current_file, function=current_function)
                        except ValueError:
        
                            debug_log(f"PDF Freq conversion error: '{frequency_pdf_str}'", file=current_file, function=current_function)
                            freq_MHz_csv = "Invalid Frequency"

                        csv_data.append({
                            "ZONE": zone_csv,
                            "GROUP": group_csv,
                            "DEVICE": device_csv,
                            "NAME": name_csv,
                            "FREQ": freq_MHz_csv,
                            "Peak": np.nan # NEW: Added Peak column
                        })
                        debug_log(f"Added PDF row: {csv_data[-1]}", file=current_file, function=current_function)
        
        debug_log(f"Finished PDF report conversion. Extracted {len(csv_data)} rows.", file=current_file, function=current_function)
        return headers, csv_data

    except FileNotFoundError:
        
        debug_log(f"Error: The file '{pdf_file_path}' was not found.", file=current_file, function=current_function)
        raise FileNotFoundError(f"The file '{pdf_file_path}' was not found.")
    except Exception as e:
        
        debug_log(f"Error during PDF conversion data extraction: {e}", file=current_file, function=current_function)
        raise
