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
    filtering out structural directories and numerical prefixes.

    Example:
    file_path = /home/anthony/Documents/OPEN-AIR/display/left_50/top_100/1_Connection/4_YAK/0_Frequency/gui_yak_frequency.py
    project_root = /home/anthony/Documents/OPEN-AIR
    Result: Connection/YAK/Frequency
    """
    try:
        # Get relative path from project root
        relative_path = file_path.relative_to(project_root)
        
        # Split into components and filter out irrelevant ones
        # Irrelevant components are 'display', 'left_50', 'top_100'
        # The first meaningful component should typically be the tab name or block name.
        
        # Consider only directory parts, exclude the filename itself
        path_parts = list(relative_path.parts)
        if file_path.is_file():
            path_parts = path_parts[:-1] # Remove the filename

        filtered_parts = []
        for part in path_parts:
            # Filter out structural elements like 'display', 'left_50', 'top_100'
            if part in ["display", "left_50", "top_100", "GUI", "gui"]: # Added "GUI" and "gui" if they appear as folder names
                continue
            
            # Remove numerical prefixes (e.g., "1_Connection" -> "Connection")
            processed_part = re.sub(r'^\d+_', '', part)
            
            # Ensure it's not empty after processing
            if processed_part:
                filtered_parts.append(processed_part)
        
        # Join with TOPIC_DELIMITER
        return TOPIC_DELIMITER.join(filtered_parts)
    except ValueError:
        # If file_path is not relative to project_root, handle gracefully
        return ""
    except Exception as e:
        # Log any other exceptions
        # debug_logger is not available here, so print for now.
        print(f"Error generating topic path from filepath {file_path}: {e}")
        return ""