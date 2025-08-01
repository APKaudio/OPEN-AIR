import csv
import subprocess
import sys
import xml.etree.ElementTree as ET
import os
import re
from bs4 import BeautifulSoup # BeautifulSoup is imported here, no need for try-except block in this file
import pdfplumber # Import pdfplumber for PDF conversion
import inspect # Import inspect module for debug_print

# Import debug_print from instrument_control
# This is crucial for directing messages to the main console if debug mode is enabled globally
from utils.utils_instrument_control import debug_print 


# --- Removed BeautifulSoup Installation Check (now handled in main_app.py) ---

# --- Removed PDFPlumber Installation Check (now handled in main_app.py) ---


def convert_html_report_to_csv(html_content, console_print_func=None):
    """
    Converts the HTML frequency coordination report into a list of dictionaries
    suitable for CSV output, handling multiple zones. This version is based on
    the IAS HTML to CSV.py prototype for accurate extraction.
    All frequencies are converted to MHz for consistency.

    Inputs:
        html_content (str): The full H TML content of the report.
        console_print_func (function, optional): A function to use for printing messages
                                                 to the console. If None, uses standard print.

    Returns:
        tuple: A tuple containing:
               - list: A list of strings representing the CSV headers.
               - list: A list of dictionaries, where each dictionary represents a row
                       in the CSV and keys are column headers.
    """
    _print = console_print_func if console_print_func else print
    _print("Starting HTML report conversion...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    csv_headers = [
        "ZONE",
        "GROUP",
        "DEVICE",
        "NAME",
        "FREQ"
    ]
    
    data_rows = []

    # Find the main content area within the HTML, based on the IAS prototype.
    main_content_container = None
    
    first_zone_p = soup.find('p', style=lambda value: value and 'font-size: large' in value and 'text-decoration: underline' in value)

    if first_zone_p:
        main_content_container = first_zone_p.find_parent('span')
        _print(f"Found main content container based on first zone paragraph.")
    
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
                    _print(f"Found main content container based on MainTable structure.")
    
    if not main_content_container:
        _print("Warning: Could not find the main content container. No data will be extracted.")
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
                _print(f"Processing Zone: {current_zone_type}")
        
        elif element.name == 'table' and 'Assignment' in element.get('class', []):
            table = element
            
            device_name_tag = table.find('th')
            current_group_name = device_name_tag.get_text(strip=True) if device_name_tag else ""
            _print(f"  Processing Group: {current_group_name}")

            rows_in_table = table.find_all('tr')[1:] # Skip the first row as it contains the <th> (device_name)
            _print(f"    Found {len(rows_in_table)} rows in current table.")

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
                            freq_mhz = "N/A"
                            try:
                                freq_match = re.search(r'(\d+(\.\d+)?)\s*(kHz|MHz|GHz)', channel_frequency_str, re.IGNORECASE)
                                if freq_match:
                                    value = float(freq_match.group(1))
                                    unit = freq_match.group(3).lower()
                                    if unit == 'mhz':
                                        freq_mhz = value
                                    elif unit == 'ghz':
                                        freq_mhz = value * 1000 # GHz to MHz
                                    elif unit == 'khz':
                                        freq_mhz = value / 1000 # kHz to MHz
                                    debug_print(f"      HTML Freq conversion: '{channel_frequency_str}' -> {freq_mhz} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                                else:
                                    # Fallback if regex doesn't match, assume MHz
                                    freq_mhz = float(channel_frequency_str) # Assume it's already in MHz
                                    _print(f"WARNING (HTML): No unit found for '{channel_frequency_str}'. Assuming MHz.")
                                    debug_print(f"      HTML Freq conversion (fallback): '{channel_frequency_str}' -> {freq_mhz} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                            except ValueError:
                                _print(f"WARNING (HTML): Could not convert frequency '{channel_frequency_str}' to float. Setting to 'Invalid Frequency'.")
                                debug_print(f"      HTML Freq conversion error: '{channel_frequency_str}'", file=__file__, function=inspect.currentframe().f_code.co_name)
                                freq_mhz = "Invalid Frequency"

                            row_data = {
                                "ZONE": current_zone_type,
                                "GROUP": current_group_name,
                                "DEVICE": band_type,
                                "NAME": channel_name,
                                "FREQ": freq_mhz # Store in MHz
                            }
                            if band_type or channel_frequency_str or channel_name:
                                data_rows.append(row_data)
                                debug_print(f"        Added HTML row: {row_data}", file=__file__, function=inspect.currentframe().f_code.co_name)
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
                        freq_mhz = "N/A"
                        try:
                            freq_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:(k|m|g)?hz)?', channel_frequency_str, re.IGNORECASE)
                            if freq_match:
                                value = float(freq_match.group(1))
                                unit_group = freq_match.group(3)
                                if unit_group:
                                    unit = unit_group.lower()
                                    if unit == 'm': # MHz
                                        freq_mhz = value
                                    elif unit == 'g': # GHz
                                        freq_mhz = value * 1000
                                    elif unit == 'k': # kHz
                                        freq_mhz = value / 1000
                                else: # No unit specified, assume MHz
                                    freq_mhz = value
                                debug_print(f"      HTML Freq conversion (direct td): '{channel_frequency_str}' -> {freq_mhz} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                            else:
                                # Fallback if regex doesn't match, assume MHz
                                freq_mhz = float(channel_frequency_str) # Assume it's already in MHz
                                _print(f"WARNING (HTML): No unit found for '{channel_frequency_str}'. Assuming MHz.")
                                debug_print(f"      HTML Freq conversion (direct td, fallback): '{channel_frequency_str}' -> {freq_mhz} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                        except ValueError:
                            _print(f"WARNING (HTML): Could not convert frequency '{channel_frequency_str}' to float. Setting to 'Invalid Frequency'.")
                            debug_print(f"      HTML Freq conversion error (direct td): '{channel_frequency_str}'", file=__file__, function=inspect.currentframe().f_code.co_name)
                            freq_mhz = "Invalid Frequency"

                        row_data = {
                            "ZONE": current_zone_type,
                            "GROUP": current_group_name,
                            "DEVICE": band_type,
                            "NAME": channel_name,
                            "FREQ": freq_mhz # Store in MHz
                        }
                        if band_type or channel_frequency_str or channel_name:
                            data_rows.append(row_data)
                            debug_print(f"        Added HTML row (direct td): {row_data}", file=__file__, function=inspect.currentframe().f_code.co_name)
    _print(f"Finished HTML report conversion. Extracted {len(data_rows)} rows.")
    return csv_headers, data_rows


def generate_csv_from_shw(xml_file_path, console_print_func=None):
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
    _print = console_print_func if console_print_func else print
    _print(f"Starting SHW report conversion for '{os.path.basename(xml_file_path)}'...")
    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ"]
    csv_data = []

    try:
        with open(xml_file_path, 'r', encoding='utf-8') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        _print("XML file parsed successfully.")

        # Iterate through 'freq_entry' elements
        for i, freq_entry in enumerate(root.findall('.//freq_entry')):
            if i % 100 == 0: # Print progress every 100 entries
                _print(f"  Processing SHW entry {i}...")

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
                
                debug_print(f"DEBUG (SHW): Processing freq_str: '{freq_str}' for device '{name}'", file=__file__, function=inspect.currentframe().f_code.co_name)

                try:
                    # Convert kHz to MHz as per user's clarification
                    freq_mhz = float(freq_str) / 1000.0 
                    debug_print(f"  SHW Freq conversion: '{freq_str}' kHz -> {freq_mhz} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                except ValueError:
                    _print(f"WARNING (SHW): Could not convert SHW frequency value '{freq_str}' to float. Setting to 'Invalid Frequency'.")
                    debug_print(f"  SHW Freq conversion error: '{freq_str}'", file=__file__, function=inspect.currentframe().f_code.co_name)
                    freq_mhz = "Invalid Frequency"

            csv_data.append({
                "ZONE": zone,
                "GROUP": group,
                "DEVICE": device,
                "NAME": name,
                "FREQ": freq_mhz # Store in MHz
            })
        _print(f"Finished SHW report conversion. Extracted {len(csv_data)} rows.")
        return headers, csv_data

    except FileNotFoundError:
        _print(f"Error: The file '{xml_file_path}' was not found.")
        raise FileNotFoundError(f"The file '{xml_file_path}' was not found.")
    except ET.ParseError as e:
        _print(f"Error: Malformed XML (SHW) file '{xml_file_path}': {e}")
        raise ET.ParseError(f"Error parsing XML (SHW) file '{xml_file_path}': {e}")
    except Exception as e:
        _print(f"Error during SHW conversion data extraction: {e}")
        raise

def convert_pdf_report_to_csv(pdf_file_path, console_print_func=None):
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
    _print = console_print_func if console_print_func else print
    _print(f"Starting PDF report conversion for '{os.path.basename(pdf_file_path)}'...")
    headers = ["ZONE", "GROUP", "DEVICE", "NAME", "FREQ"]
    csv_data = []

    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            last_known_group = "Uncategorized" # Default group if not found
            _print(f"Opened PDF with {len(pdf.pages)} pages.")

            for page_num, page in enumerate(pdf.pages):
                _print(f"  Processing Page {page_num + 1}...")
                # Extract text for group headers
                lines = page.extract_text().splitlines()
                lines = [line.strip() for line in lines if line.strip()]

                group_headers = [(i, line) for i, line in enumerate(lines)
                                 if re.match(r".+\(\d+ frequencies\)", line)]

                tables = page.extract_tables()
                _print(f"    Found {len(tables)} tables on Page {page_num + 1}.")

                group_index = 0
                for table_num, table in enumerate(tables):
                    if group_index < len(group_headers):
                        last_known_group = group_headers[group_index][1]
                        group_index += 1

                    current_zone = last_known_group # PDF Group -> CSV ZONE
                    _print(f"      Processing Table {table_num + 1} for Zone: {current_zone}")

                    for row_num, row in enumerate(table):
                        if not row or all(cell is None or cell.strip() == "" for cell in row):
                            continue

                        if "Model" in row[0] and "Frequency" in row[-1]: # Skip header rows
                            debug_print(f"        Skipping header row: {row}", file=__file__, function=inspect.currentframe().f_code.co_name)
                            continue

                        clean_row = [cell.replace("\n", " ").strip() if cell else "" for cell in row]
                        # Ensure row has at least 6 elements to unpack safely
                        while len(clean_row) < 6:
                            clean_row.append("")

                        model_pdf, band_pdf, name_pdf, preset_pdf, spacing_pdf, frequency_pdf_str = clean_row

                        if model_pdf.strip() == current_zone.strip(): # Skip rows that mistakenly repeat the group name
                            debug_print(f"        Skipping duplicate group name row: {row}", file=__file__, function=inspect.currentframe().f_code.co_name)
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

                        freq_mhz_csv = "N/A"
                        try:
                            # The frequency is already in MHz, so no conversion needed
                            freq_mhz_csv = float(frequency_pdf_str)
                            debug_print(f"          PDF Freq conversion: '{frequency_pdf_str}' -> {freq_mhz_csv} MHz", file=__file__, function=inspect.currentframe().f_code.co_name)
                        except ValueError:
                            _print(f"WARNING (PDF): Could not convert PDF frequency value '{frequency_pdf_str}' to float (MHz). Setting to 'Invalid Frequency'.")
                            debug_print(f"          PDF Freq conversion error: '{frequency_pdf_str}'", file=__file__, function=inspect.currentframe().f_code.co_name)
                            freq_mhz_csv = "Invalid Frequency"

                        csv_data.append({
                            "ZONE": zone_csv,
                            "GROUP": group_csv,
                            "DEVICE": device_csv,
                            "NAME": name_csv,
                            "FREQ": freq_mhz_csv
                        })
                        debug_print(f"          Added PDF row: {csv_data[-1]}", file=__file__, function=inspect.currentframe().f_code.co_name)
        _print(f"Finished PDF report conversion. Extracted {len(csv_data)} rows.")
        return headers, csv_data

    except FileNotFoundError:
        _print(f"Error: The file '{pdf_file_path}' was not found.")
        raise FileNotFoundError(f"The file '{pdf_file_path}' was not found.")
    except Exception as e:
        _print(f"Error during PDF conversion data extraction: {e}")
        raise
