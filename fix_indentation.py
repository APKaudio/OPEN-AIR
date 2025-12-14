import textwrap

def fix_indentation(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_class = False
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith('class ShowtimeTab'):
            in_class = True
            new_lines.append(line)
        elif in_class and (stripped_line.startswith('def _') or stripped_line.startswith('def _on_')) :
             new_lines.append('    ' + line)
        else:
            new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

fix_indentation('/home/anthony/Documents/OPEN-AIR/display/left_50/top_100/3_markers/1_showtime/gui_showtime.py')