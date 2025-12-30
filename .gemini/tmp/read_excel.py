import pandas as pd
import sys
import json
import re

file_path = "/home/anthony/Downloads/ROUTING.AES70.audio - HP 3235 - Programming and routing plan (1).xlsx"

def infer_header_row_and_data(df, max_rows_to_check=5, specific_headers_list=None):
    """
    Infers the header row and returns the headers and the data DataFrame.
    If specific_headers_list is provided, it prioritizes finding a row that contains all of them.
    """
    best_row_idx = -1
    max_string_uniqueness = -1
    inferred_headers = []

    for i in range(min(max_rows_to_check, len(df))):
        row = df.iloc[i]
        row_values_str = [str(cell).strip() for cell in row if pd.notna(cell) and str(cell).strip()]

        # Priority 1: Check for explicit header match
        if specific_headers_list and len(row_values_str) >= len(specific_headers_list):
            specific_headers_lower = [sh.lower() for sh in specific_headers_list]
            if all(any(sh == rv.lower() for rv in row_values_str) for sh in specific_headers_lower):
                best_row_idx = i
                inferred_headers = [str(cell).strip() for cell in row if pd.notna(cell)]
                break 

        # Priority 2: General heuristic for header row
        string_count = 0
        numeric_count = 0
        unique_strings = set()

        for cell in row:
            if pd.isna(cell):
                continue
            cell_str = str(cell).strip()
            if cell_str:
                try:
                    float(cell_str)
                    numeric_count += 1
                except ValueError:
                    string_count += 1
                    unique_strings.add(cell_str)
        
        score = len(unique_strings) * 2 - numeric_count 
        
        if score > max_string_uniqueness and string_count > 0:
            max_string_uniqueness = score
            best_row_idx = i
            
    if best_row_idx != -1:
        inferred_headers = [str(cell).strip() for cell in df.iloc[best_row_idx] if pd.notna(cell)]
        df_data = df.iloc[best_row_idx + 1:].reset_index(drop=True)
    else:
        df_data = df.reset_index(drop=True)
        
    return inferred_headers, df_data


def extract_data_from_sheet(df, sheet_name):
    sheet_elements = {}
    outputs = set()
    
    user_provided_headers = ["EDAC Pins", "Direction", "Channel", "Channel", "Bank", "Relay", "Bank / RElay"]
    
    inferred_headers, df_data = infer_header_row_and_data(df, specific_headers_list=user_provided_headers)
    
    final_headers = []
    channel_header_indices = []
    for i, h in enumerate(inferred_headers):
        if h.lower() == "channel":
            channel_header_indices.append(i)
            final_headers.append(f"Channel_{len(channel_header_indices)}") 
        else:
            final_headers.append(h)
    
    inferred_headers_map = {h.lower(): i for i, h in enumerate(final_headers)}

    for index, row in df_data.iterrows():
        mapped_row = {}
        # Populate mapped_row based on inferred headers or by column index if no headers
        if final_headers:
            for col_idx, header_name in enumerate(final_headers):
                if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                    mapped_row[header_name.lower()] = str(row.iloc[col_idx]).strip()
                else:
                    mapped_row[header_name.lower()] = "" 
        else: # Fallback if no headers found, use generic column names
            for col_idx, cell_value in enumerate(row):
                if pd.notna(cell_value):
                    mapped_row[f"col_{col_idx}"] = str(cell_value).strip()

        # Skip if the row is effectively empty or just numeric without clear context
        has_meaningful_content = any(val for key, val in mapped_row.items() if val and not re.fullmatch(r'^-?\d+(\.\d+)?$', val) and len(val) > 1 and not key.startswith("col_"))
        if not has_meaningful_content and not final_headers: # If no headers, check raw values for meaningful content
            if not any(val for val in mapped_row.values() if val and not re.fullmatch(r'^-?\d+(\.\d+)?$', val) and len(val) > 1):
                continue
        elif not has_meaningful_content and final_headers: # If headers, but no meaningful content in mapped row
            continue

        edac_pin = mapped_row.get("edac pins", "")
        direction = mapped_row.get("direction", "")
        channel_1 = mapped_row.get("channel_1", "")
        bank = mapped_row.get("bank", "")
        relay = mapped_row.get("relay", "")
        
        if not bank and not relay and mapped_row.get("bank / relay"):
            combined_br = mapped_row["bank / relay"].split('/')
            if len(combined_br) == 2:
                bank = combined_br[0].strip()
                relay = combined_br[1].strip()

        # Construct a meaningful toggler name
        toggler_name_parts = []
        if channel_1: toggler_name_parts.append(f"Ch{channel_1}")
        if edac_pin and edac_pin != channel_1: toggler_name_parts.append(f"Pin{edac_pin}") 
        if direction: toggler_name_parts.append(direction) 
        
        if not toggler_name_parts:
            descriptive_parts = []
            for key, value in mapped_row.items():
                if value and not re.fullmatch(r'^-?\d+(\.\d+)?$', value) and len(value) > 1 and \
                   key not in ["edac pins", "direction", "channel_1", "bank", "relay", "bank / relay"] and \
                   not key.startswith("col_"): # Exclude already used parts and generic col names
                    descriptive_parts.append(value)
            
            if descriptive_parts:
                base_toggler_name = "_".join(descriptive_parts[:3]) # Take up to three descriptive parts
            else:
                base_toggler_name = f"Row_{index}" # Ultimate fallback if nothing descriptive found
        else:
            base_toggler_name = "_".join(toggler_name_parts)

        sanitized_toggler_name = re.sub(r'[^a-zA-Z0-9_]', '', base_toggler_name).replace(' ', '')
        
        if not sanitized_toggler_name: # Handle case where sanitization results in an empty string
            sanitized_toggler_name = f"GenericToggle_{index}" 

        # Initialize the toggler
        if sanitized_toggler_name not in sheet_elements:
            sheet_elements[sanitized_toggler_name] = {
                "type": "_GuiButtonToggler",
                "options": [],
                "default_option": ""
            }
        
        options_to_add = set()
        if direction: options_to_add.add(direction)

        for key, value in mapped_row.items():
            if value and not re.fullmatch(r'^-?\d+(\.\d+)?$', value) and \
               value not in [edac_pin, direction, channel_1, bank, relay] and \
               len(value) > 1:
                options_to_add.add(value)
        
        current_options = sheet_elements[sanitized_toggler_name]["options"]
        for opt in sorted(list(options_to_add)):
            if opt not in current_options:
                current_options.append(opt)
        sheet_elements[sanitized_toggler_name]["options"] = sorted(current_options)
        
        if not sheet_elements[sanitized_toggler_name]["default_option"] and current_options:
            sheet_elements[sanitized_toggler_name]["default_option"] = sheet_elements[sanitized_toggler_name]["options"][0]

        associated_values = {}
        if bank: 
            try: associated_values["channel_bank"] = int(bank)
            except ValueError: associated_values["channel_bank"] = bank
        if relay: 
            try: associated_values["relay_id"] = int(relay)
            except ValueError: associated_values["relay_id"] = relay

        if associated_values:
            sheet_elements[sanitized_toggler_name]["associated_values"] = associated_values

        # Outputs - More aggressive detection
        # Collect all numbers in the row that are not explicitly identified as bank, relay, channel, or edac_pin
        current_row_numbers = set()
        identified_params = {str(bank), str(relay), str(channel_1), str(edac_pin)}
        for key, value in mapped_row.items():
            numeric_vals = re.findall(r'\b\d+\b', value)
            for num_str in numeric_vals:
                if num_str not in identified_params:
                    try:
                        current_row_numbers.add(int(num_str))
                    except ValueError:
                        pass
        
        is_output_related = direction.lower() == "out" or \
                            any("output" in k.lower() or "dest" in k.lower() for k in mapped_row.keys()) or \
                            any("output" in v.lower() or "dest" in v.lower() for v in mapped_row.values())

        if is_output_related and current_row_numbers:
            outputs.update(current_row_numbers)
        elif not final_headers and current_row_numbers: # If no headers AND numbers present, could be outputs
            outputs.update(current_row_numbers)

    return sheet_elements, list(sorted(list(outputs)))


try:
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    
    output_json = {}

    for sheet_name in sheet_names:
        print(f"Processing sheet: {sheet_name}")
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        if df.empty:
            output_json[sheet_name] = {}
            continue

        sheet_elements, outputs = extract_data_from_sheet(df, sheet_name)
        
        cleaned_sheet_elements = {name: config for name, config in sheet_elements.items() if config["options"]}

        output_json[sheet_name] = cleaned_sheet_elements
        
        if outputs:
            if output_json[sheet_name]:
                output_json[sheet_name]["Outputs"] = outputs
            else: 
                output_json[sheet_name] = {"Outputs": outputs}

    print(json.dumps(output_json, indent=2))

except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)