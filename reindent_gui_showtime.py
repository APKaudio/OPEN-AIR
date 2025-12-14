
import textwrap

def reindent_python_file(file_path, indent_size=4):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    indent_level = 0
    
    # Heuristics for basic indentation correction
    # This is not a full Python parser, but handles common cases
    for i, line in enumerate(lines):
        stripped_line = line.lstrip()
        leading_whitespace = len(line) - len(stripped_line)

        if not stripped_line or stripped_line.startswith('#'):
            new_lines.append(line)
            continue

        # Adjust indent level based on previous line's content
        if i > 0:
            prev_stripped = lines[i-1].lstrip()
            if prev_stripped.endswith(':'):
                indent_level += 1
            # Simple de-indentation for 'return', 'break', 'continue' or if block ends
            # This is very basic and might not catch all cases
            if stripped_line.startswith(('return', 'break', 'continue', 'pass')):
                 # If it's a standalone keyword, and we are already indented, de-indent
                if indent_level > 0:
                    indent_level -= 1
            # Check for block ending (e.g., else, elif, except, finally)
            elif stripped_line.startswith(('else:', 'elif ', 'except', 'finally:')) and indent_level > 0:
                indent_level -= 1
            # A 'def' or 'class' might indicate an outer block, if the previous line
            # was also a def/class or a comment, we might need to de-indent.
            elif (stripped_line.startswith(('def ', 'class ')) and 
                  (lines[i-1].strip().startswith(('def ', 'class ')) or 
                   lines[i-1].strip().startswith('#'))):
                if indent_level > 0:
                    indent_level -= 1
            # Further de-indent for blocks that are implicitly ending
            # E.g., if a new statement starts at a lower level than expected
            # This is a very rough heuristic
            while indent_level * indent_size > leading_whitespace + indent_size and indent_level > 0:
                indent_level -= 1

        # Apply the current indent level
        current_indent = ' ' * (indent_level * indent_size)
        new_lines.append(current_indent + stripped_line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

reindent_python_file('/home/anthony/Documents/OPEN-AIR/display/left_50/top_100/3_markers/1_showtime/gui_showtime.py')
