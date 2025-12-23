
import os
import re

def fix_debug_log_calls(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                
                # This regex is the most important part of the script.
                # It will need to be very robust to handle all the different ways
                # that debug_log can be called.
                new_content = re.sub(
                    r"debug_log\((.*)\)",
                    r"debug_log(\1, file=__file__, version=current_version, function=inspect.currentframe().f_code.co_name)",
                    content
                )
                
                if content != new_content:
                    with open(filepath, "w") as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")

if __name__ == "__main__":
    fix_debug_log_calls(".")
