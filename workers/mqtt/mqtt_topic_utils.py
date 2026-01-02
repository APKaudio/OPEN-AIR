# workers/utils/topic_utils.py
import re
from pathlib import Path

TOPIC_DELIMITER = "/"

def get_topic(*args: str) -> str:
    """
    Generates a standardized MQTT topic string by joining non-empty arguments with '/'.
    """
    return TOPIC_DELIMITER.join(arg for arg in args if arg)

def generate_topic_path_from_filepath(file_path: Path, project_root: Path) -> str:
    """
    Generates a hierarchical MQTT topic path from a given file path,
    filtering out structural directories and handling component transformations.
    """
    try:
        relative_path = file_path.relative_to(project_root)
        path_parts = list(relative_path.parts)
        if file_path.is_file():
            path_parts = path_parts[:-1] # Remove the filename

        filtered_parts = []
        for part in path_parts:
            # Filter out structural elements
            if part in ["display", "GUI", "gui"] or \
               part.startswith("left_") or \
               part.startswith("right_") or \
               part.startswith("top_") or \
               part.startswith("bottom_"):
                continue

            # --- REVISED LOGIC FOR CONSISTENCY AND ROBUSTNESS ---
            # The function applies specific rules for certain components based on previous requirements:
            # - "8_experiments" is preserved as is.
            # - "5_Control_Elements" is transformed to "5_control_elements".
            # - "2_Graphing" has its prefix removed, but casing is preserved.
            #
            # For all other components, a general rule is applied: remove numerical prefixes,
            # clean spaces, and convert to lowercase. This addresses the user's query about
            # differing treatments and ensures robustness against unusual characters like spaces.

            processed_part = part # Default to original part

            if part == "8_experiments":
                processed_part = part # Preserve "8_experiments" exactly.
            elif part == "5_Control_Elements":
                # Specific transformation for control elements to "5_control_elements".
                processed_part = "5_control_elements"
            elif part == "2_Graphing":
                # Specific handling for graphing: remove numerical prefix, preserve casing.
                processed_part = re.sub(r'^\d+_', '', part)
            else:
                # General rule for all other parts:
                # 1. Remove numerical prefix (e.g., "1_", "3_").
                # 2. Replace spaces with underscores for better topic structure.
                # 3. Convert to lowercase.
                cleaned_part = re.sub(r'^\d+_', '', part)
                processed_part = cleaned_part.replace(" ", "_") # Removed .lower()

            # Ensure the processed part is not empty after transformations
            if processed_part:
                filtered_parts.append(processed_part)
        
        # Join the processed parts to form the MQTT topic path
        return TOPIC_DELIMITER.join(filtered_parts)
    except ValueError:
        # Handle cases where file_path is not relative to project_root
        return ""
    except Exception as e:
        # Log any other unexpected errors during path processing
        print(f"Error generating topic path from filepath {file_path}: {e}")
        return ""