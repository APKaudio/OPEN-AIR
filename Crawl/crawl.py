# crawl.py ##
#
# This script recursively traverses the directory it is run from,
# listing all files and subdirectories in a Tkinter GUI window.
# It now also deletes all '__pycache__' directories and their contents as it crawls.
# For any Python (.py) files encountered, it will also parse the
# file to extract and display the names of all defined functions
# and classes, as well as imported modules. All output is also saved to a 'Crawl.log' file.
# It now now generates a 'MAP.txt' file with a tree-like structure
# of the discovered files and functions, with each line commented out.
# Additionally, it creates an 'EVERYTHING.py.LOG' file containing the
# concatenated content of all Python, CSV, and INI files found.
# The script now starts by prompting the user for a directory to crawl.
# All log and output files are now saved to a new directory
# with a YYYYMMDDHHSS timestamp.
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
#
# Version 20250813.233738.3 (version change)


import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import ast # Module to parse Python code into an Abstract Syntax Tree
import inspect # For getting current function name for logging (optional, but good practice)
import threading
import datetime # For timestamping the log file
import subprocess # For opening files
import shutil # For deleting directories

# --- Global Version Information ---
current_version = "20250813.233738.3"
current_version_hash = (20250813 * 233738 * 3)

# --- Logging and Console Output Functions (Simplified for standalone script) ---
def debug_log(message, file, function, **kwargs):
    """A simplified debug logging function."""
    print(f"DEBUG: {file} - {function} - {message} - Version: {current_version}")

def console_log(message):
    """A simplified console output function for the GUI."""
    pass # Suppress direct console prints, will use GUI text widget


class FolderCrawlerApp:
    """
    Function Description:
    A Tkinter application that crawls a specified directory (defaulting to the
    script's directory) and displays its contents. It identifies Python files
    and lists their functions and classes. All output is also written to 'Crawl.log'.
    It now now generates a 'MAP.txt' file with a tree-like structure
    of the discovered files and functions, with each line commented out.
    A third file, 'EVERYTHING.py.LOG', is created with the content of all found Python,
    CSV, and INI files. The script now starts by prompting the user for a directory to crawl.
    All output files are now saved to a new, timestamped directory.

    Inputs:
        root (tk.Tk): The root Tkinter window.
        start_directory (str): The initial directory to crawl, provided by the user.

    Process:
        1. Initializes the main application window and widgets.
        2. Sets up a scrolled text area for displaying results.
        3. Provides buttons to start the crawling process and open log/map/crawl folder files.
        4. Creates a new directory for all output files with a timestamp (YYYYMMDDHHSS).
        5. Opens a log file ('Crawl.log'), a map file ('MAP.txt'), and an
           everything log file ('EVERYTHING.py.LOG') for writing, inside the new directory.
        6. Implements the `_crawl_directory` method to recursively scan folders,
           now deleting '__pycache__' directories on the fly and ignoring others
           starting with a dot.
        7. Implements the `_analyze_python_file` method to parse Python files
           and extract function and class definitions and imports using the `ast` module,
           ignoring '__init__.py' files.
        8. Displays all collected information in the scrolled text area and writes to log file.
        9. Generates a tree-like map in 'MAP.txt' with commented lines and
           nested function/class representation.
        10. Writes the full content of each Python, CSV, and INI file to
           'EVERYTHING.py.LOG' with a separator.

    Outputs:
        A Tkinter GUI application, a timestamped 'Crawl.log' file, a timestamped 'MAP.txt' file,
        and a timestamped 'EVERYTHING.py.LOG' file, all saved in a new, timestamped directory.
    """
    def __init__(self, root, start_directory):
        self.root = root
        self.root.title("Folder and Python File Analyzer - crawl.py")
        self.root.geometry("800x600")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.current_file = os.path.basename(__file__)
        self.current_version = current_version

        self.directory_path_var = tk.StringVar(value=start_directory)
        self.log_file = None # Initialize log file handle
        self.map_file = None # Initialize map file handle
        self.everything_log_file = None # New file handle
        self.output_dir = None # New variable for the output directory

        # --- UI Elements ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1) # Makes the entry field stretch

        ttk.Label(control_frame, text=f"Crawling: {start_directory}").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.crawl_button = ttk.Button(control_frame, text="Start Crawl", command=self._start_crawl)
        self.crawl_button.grid(row=0, column=2, padx=5, pady=5)

        self.open_log_button = ttk.Button(control_frame, text="Open Log", command=self._open_log_file)
        self.open_log_button.grid(row=0, column=3, padx=5, pady=5)

        self.open_map_button = ttk.Button(control_frame, text="Open Map", command=self._open_map_file)
        self.open_map_button.grid(row=0, column=4, padx=5, pady=5)

        # New button for EVERYTHING.py.LOG
        self.open_everything_log_button = ttk.Button(control_frame, text="Open All Code", command=self._open_everything_log_file)
        self.open_everything_log_button.grid(row=0, column=5, padx=5, pady=5)

        # New button to open the folder where crawl.py is
        self.open_crawl_folder_button = ttk.Button(control_frame, text="Open Crawl Folder", command=self._open_crawl_folder)
        self.open_crawl_folder_button.grid(row=0, column=6, padx=5, pady=5)


        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=25,
                                                   font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4",
                                                   insertbackground="#d4d4d4")
        self.text_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.text_area.tag_configure("dir", foreground="#6a9955") # Green for directories
        self.text_area.tag_configure("file", foreground="#569cd6") # Blue for files
        self.text_area.tag_configure("python_file", foreground="#cc7832") # Orange for Python files
        self.text_area.tag_configure("function", foreground="#ffc66d") # Yellow for functions
        self.text_area.tag_configure("class", foreground="#da70d6") # Purple for classes
        self.text_area.tag_configure("import", foreground="#4ec9b0") # Teal for imports
        self.text_area.tag_configure("header", foreground="#9cdcfe", font=("Consolas", 12, "bold")) # Light blue for headers

        # Ensure log and map files are closed on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        # function_name()
        # Function Description:
        # Handles the window closing event, ensuring the log, map, and everything log files are properly closed.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Closing application. Goodbye! 🚪",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.log_file:
            self.log_file.close()
            debug_log(f"Crawl.log closed. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.map_file:
            self.map_file.close()
            debug_log(f"MAP.txt closed. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.everything_log_file:
            self.everything_log_file.close()
            debug_log(f"EVERYTHING.py.LOG closed. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        self.root.destroy()

    def _open_crawl_folder(self):
        # function_name()
        # Function Description:
        # Opens the directory where the crawl.py script is located.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Ahoy there, matey! I'll be openin' the folder where we keep the treasure map! 🏴‍☠️",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)
        self._open_file(os.path.dirname(os.path.abspath(__file__)), "Crawl Folder")

    def _start_crawl(self):
        # function_name()
        # Function Description:
        # Initiates the crawling process in a separate thread to keep the GUI responsive.
        # Opens both 'Crawl.log', 'MAP.txt', and 'EVERYTHING.py.LOG' files with timestamps,
        # in a newly created directory.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Starting crawl. Let's explore! 🧭",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)

        self.text_area.delete(1.0, tk.END) # Clear previous output

        # Create a new directory for output files
        timestamp_dir = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), timestamp_dir)
        try:
            os.makedirs(self.output_dir)
            self._append_to_text_area(f"✅ Created new output directory: {self.output_dir}", "header")
            debug_log(f"Created output directory: {self.output_dir}. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        except OSError as e:
            self._append_to_text_area(f"❌ Error creating directory {self.output_dir}: {e}\n", "header")
            debug_log(f"Error creating directory: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
            self.root.after(0, lambda: self.crawl_button.config(state=tk.NORMAL))
            return

        log_file_path = os.path.join(self.output_dir, "Crawl.log")
        map_file_path = os.path.join(self.output_dir, "MAP.txt")
        everything_log_file_path = os.path.join(self.output_dir, "EVERYTHING.py.LOG")

        # Open the log file
        try:
            self.log_file = open(log_file_path, "w", encoding="utf-8")
            self._append_to_text_area(f"--- Crawl Log Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n", "header")
            self.log_file.write(f"--- Crawl Log Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
            debug_log(f"Crawl.log opened at {log_file_path}. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        except Exception as e:
            self._append_to_text_area(f"❌ Error opening Crawl.log: {e}\n", "header")
            debug_log(f"Error opening Crawl.log: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
            self.log_file = None # Ensure log_file is None if opening fails

        # Open the MAP.txt file and write its header
        try:
            self.map_file = open(map_file_path, "w", encoding="utf-8")
            map_header = f"""# Program Map:
# This section outlines the directory and file structure of the OPEN-AIR RF Spectrum Analyzer Controller application,
# providing a brief explanation for each component.
#
# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
"""
            self.map_file.write(map_header)
            debug_log(f"MAP.txt opened at {map_file_path}. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        except Exception as e:
            self._append_to_text_area(f"❌ Error opening MAP.txt: {e}\n", "header")
            debug_log(f"Error opening MAP.txt: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
            self.map_file = None # Ensure map_file is None if opening fails

        # Open the EVERYTHING.py.LOG file
        try:
            self.everything_log_file = open(everything_log_file_path, "w", encoding="utf-8")
            everything_header = f"""# ====================================================================================
# EVERYTHING.py.LOG
# This file contains the complete content of all Python, CSV, and INI files found during the crawl.
# Each file's content is separated by its path and a dashed line.
#
# Log started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ====================================================================================\n\n"""
            self.everything_log_file.write(everything_header)
            debug_log(f"EVERYTHING.py.LOG opened at {everything_log_file_path}. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        except Exception as e:
            self._append_to_text_area(f"❌ Error opening EVERYTHING.py.LOG: {e}\n", "header")
            debug_log(f"Error opening EVERYTHING.py.LOG: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
            self.everything_log_file = None

        self.crawl_button.config(state=tk.DISABLED)
        self.open_log_button.config(state=tk.DISABLED)
        self.open_map_button.config(state=tk.DISABLED)
        self.open_everything_log_button.config(state=tk.DISABLED)

        # Run the crawl in a separate thread to prevent GUI from freezing
        threading.Thread(target=self._crawl_directory_thread, daemon=True).start()

    def _crawl_directory_thread(self):
        # function_name()
        # Function Description:
        # Worker function for `_start_crawl`. Performs the actual directory traversal
        # and Python file analysis. Deletes __pycache__ folders. Updates the GUI
        # on the main thread and writes to log file.
        # Also builds the tree structure for MAP.txt and concatenates files for EVERYTHING.py.LOG.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Wild scientist here! The crawler is a-rumblin' and a-roarin', diving deep into the filesystem! We're about to make some discoveries! 🧪",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)

        target_directory = self.directory_path_var.get()
        if not os.path.isdir(target_directory):
            self._append_to_text_area(f"❌ Error: '{target_directory}' is not a valid directory.", "header")
            self.root.after(0, lambda: self.crawl_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_log_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_map_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_everything_log_button.config(state=tk.NORMAL))
            if self.log_file:
                self.log_file.write(f"Error: '{target_directory}' is not a valid directory.\n")
                self.log_file.close()
                self.log_file = None
            if self.map_file:
                self.map_file.write(f"Error: '{target_directory}' is not a valid directory.\n")
                self.map_file.close()
                self.map_file = None
            if self.everything_log_file:
                self.everything_log_file.write(f"Error: '{target_directory}' is not a valid directory.\n")
                self.everything_log_file.close()
                self.everything_log_file = None
            return

        self._append_to_text_area(f"Crawling directory: {target_directory}\n", "header")
        if self.log_file:
            self.log_file.write(f"Crawling directory: {target_directory}\n\n")

        map_output_lines = []

        try:
            # Simulate the root directory (e.g., OPEN-AIR/)
            root_dir_name = os.path.basename(target_directory)
            map_output_lines.append(f"# └── {root_dir_name}/\n")

            for root, dirs, files in os.walk(target_directory, topdown=True):
                # Delete __pycache__ folders as they are encountered
                if '__pycache__' in dirs:
                    cache_path = os.path.join(root, '__pycache__')
                    try:
                        self._append_to_text_area(f"  [DELETING] Found and deleted __pycache__ directory: {cache_path}", "header")
                        shutil.rmtree(cache_path)
                        dirs.remove('__pycache__') # Remove from the list to prevent walking into it
                        debug_log(f"Arr, matey! Found the cursed treasure of the __pycache__ and sent it to Davy Jones' Locker! ☠️",
                                    file=f"{self.current_file} - {self.current_version}", function=current_function)
                    except Exception as e:
                        self._append_to_text_area(f"  ❌ Error deleting __pycache__ at {cache_path}: {e}", "header")
                        debug_log(f"Aaargh! Couldn't sink the __pycache__ ship! The error be: {e}",
                                    file=f"{self.current_file} - {self.current_version}", function=current_function)

                # Ignore folders starting with a dot
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                relative_root = os.path.relpath(root, target_directory)
                if relative_root == ".":
                    # This is the base directory, already handled above
                    current_indent_level = 0
                else:
                    current_indent_level = relative_root.count(os.sep) + 1 # +1 for the initial root dir

                # Display current directory in GUI log
                if relative_root != ".": # Avoid re-logging the base directory
                    display_root = relative_root + os.sep
                    self._append_to_text_area(f"\nDirectory: {display_root}", "dir")
                    if self.log_file:
                        self.log_file.write(f"\nDirectory: {display_root}\n")

                all_items = sorted(dirs) + sorted(files)
                for i, item in enumerate(all_items):
                    is_last_item_in_current_level = (i == len(all_items) - 1)
                    prefix = "└── " if is_last_item_in_current_level else "├── "
                    indent_str = "    " * current_indent_level

                    if item in dirs:
                        map_output_lines.append(f"#{indent_str}{prefix}{item}/\n")
                        # Display subdirectories in GUI log
                        self._append_to_text_area(f"  {indent_str}{prefix}{item}", "dir")
                        if self.log_file:
                            self.log_file.write(f"  {indent_str}{prefix}{item}\n")
                    elif item in files:
                        file_path = os.path.join(root, item)
                        map_output_lines.append(f"#{indent_str}{prefix}{item}\n")
                        # Display files in GUI log
                        self._append_to_text_area(f"  {indent_str}{prefix}{item}", "file")
                        if self.log_file:
                            self.log_file.write(f"  {indent_str}{prefix}{item}\n")

                        # Handle different file types for EVERYTHING.py.LOG
                        if item.lower().endswith(('.py', '.csv', '.ini')) and item.lower() != "__init__.py":
                            if item.lower().endswith(".py"):
                                # Analyze Python file and get its functions/classes for MAP.txt
                                py_analysis_lines = self._analyze_python_file(file_path, current_indent_level + 1)
                                for line in py_analysis_lines:
                                    map_output_lines.append(line + "\n")

                            # Write the content of the file to EVERYTHING.py.LOG
                            if self.everything_log_file:
                                try:
                                    with open(file_path, "r", encoding="utf-8") as generic_file:
                                        file_content = generic_file.read()
                                    self.everything_log_file.write(
                                        f"#####################################\n"
                                        f"### File: {file_path}\n"
                                        f"#####################################\n"
                                        f"{file_content}\n\n"
                                    )
                                    debug_log(f"Wrote content of {item} to EVERYTHING.py.LOG. ✅",
                                                file=f"{self.current_file} - {self.current_version}", function=current_function)
                                except Exception as e:
                                    debug_log(f"Wild scientist here! I tried to read that file but it seems the data got lost in transit! The error says: {e} ❌",
                                                file=f"{self.current_file} - {self.current_version}", function=current_function)

                        elif item.lower() == "__init__.py":
                            # Log that __init__.py is being ignored
                            ignore_message = f"    [INFO] Ignoring __init__.py: {item}"
                            self._append_to_text_area(ignore_message, "file")
                            if self.log_file:
                                self.log_file.write(ignore_message + "\n")


        except Exception as e:
            error_message = f"\n❌ An error occurred during crawling: {e}"
            self._append_to_text_area(error_message, "header")
            if self.log_file:
                self.log_file.write(error_message + "\n")
            if self.map_file:
                self.map_file.write(error_message + "\n")
            if self.everything_log_file:
                self.everything_log_file.write(error_message + "\n")
            debug_log(f"Error during crawl: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        finally:
            final_message = f"\n--- Crawl complete for {target_directory}. 👍 ---"
            self._append_to_text_area(final_message, "header")
            if self.log_file:
                self.log_file.write(final_message + "\n")
                self.log_file.close()
                self.log_file = None # Reset file handle after closing

            # Write all collected map lines to MAP.txt
            if self.map_file:
                for line in map_output_lines:
                    self.map_file.write(line)
                self.map_file.close()
                self.map_file = None # Reset file handle after closing

            if self.everything_log_file:
                self.everything_log_file.close()
                self.everything_log_file = None # Reset file handle after closing

            self.root.after(0, lambda: self.crawl_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_log_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_map_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_everything_log_button.config(state=tk.NORMAL))
            debug_log(f"Crawl finished. ✅",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)


    def _analyze_python_file(self, file_path, indent_level):
        # function_name()
        # Function Description:
        # Parses a Python file and extracts function, class, import, and now, function parameter definitions.
        # Returns a list of formatted strings for MAP.txt and also updates the GUI log.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Analyzing Python file: {file_path}. Parsing! 🧐",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)

        analysis_lines = []
        indent_str = "    " * indent_level # Indentation for the file itself
        inner_item_indent_prefix = indent_str + "    |   "

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            imports_found = set() # Use a set to avoid duplicates
            functions_found = []
            classes_found = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports_found.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports_found.add(node.module)
                elif isinstance(node, ast.FunctionDef):
                    # Extract parameter names
                    params = [a.arg for a in node.args.posonlyargs] + \
                             [a.arg for a in node.args.args] + \
                             [a.arg for a in node.args.kwonlyargs]

                    # Format the function name with its parameters
                    function_signature = f"{node.name}({', '.join(params)})"
                    functions_found.append(function_signature)

                elif isinstance(node, ast.ClassDef):
                    classes_found.append(node.name)

            if functions_found or classes_found or imports_found:
                # Add to GUI log
                self._append_to_text_area(f"    [PY] Analysis for {os.path.basename(file_path)}:", "python_file")
                if self.log_file:
                    self.log_file.write(f"    [PY] Analysis for {os.path.basename(file_path)}:\n")

                if imports_found:
                    import_line_gui = f"      Imports: {', '.join(sorted(list(imports_found)))}"
                    self._append_to_text_area(import_line_gui, "import")
                    if self.log_file:
                        self.log_file.write(import_line_gui + "\n")
                    for imp_name in sorted(list(imports_found)):
                        analysis_lines.append(f"#{inner_item_indent_prefix}-> Import: {imp_name}")

                if classes_found:
                    class_line_gui = f"      Classes: {', '.join(sorted(classes_found))}"
                    self._append_to_text_area(class_line_gui, "class")
                    if self.log_file:
                        self.log_file.write(class_line_gui + "\n")
                    for cls_name in sorted(classes_found):
                        analysis_lines.append(f"#{inner_item_indent_prefix}-> Class: {cls_name}")

                if functions_found:
                    function_line_gui = f"      Functions: {', '.join(sorted(functions_found))}"
                    self._append_to_text_area(function_line_gui, "function")
                    if self.log_file:
                        self.log_file.write(function_line_gui + "\n")
                    for func_signature in sorted(functions_found):
                        analysis_lines.append(f"#{inner_item_indent_prefix}-> Function: {func_signature}")
            else:
                no_defs_line = f"    [PY] No functions, classes, or imports found in {os.path.basename(file_path)}"
                self._append_to_text_area(no_defs_line, "python_file")
                if self.log_file:
                    self.log_file.write(no_defs_line + "\n")
                # If no definitions, still add a commented line to MAP.txt
                analysis_lines.append(f"#{indent_str}    - No functions, classes, or imports found.")

        except SyntaxError as e:
            syntax_error_line = f"    ❌ [PY] Syntax Error in {os.path.basename(file_path)}: {e}"
            self._append_to_text_area(syntax_error_line, "python_file")
            if self.log_file:
                self.log_file.write(syntax_error_line + "\n")
            analysis_lines.append(f"#{indent_str}    - Syntax Error: {e}")
            debug_log(f"Error! The syntax is all jumbled! It's an unholy mess! My instruments are screaming! 😵‍💫 Error in {file_path}: {e}.",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        except Exception as e:
            general_error_line = f"    ❌ [PY] Error analyzing {os.path.basename(file_path)}: {e}"
            self._append_to_text_area(general_error_line, "python_file")
            if self.log_file:
                self.log_file.write(general_error_line + "\n")
            analysis_lines.append(f"#{indent_str}    - Error analyzing: {e}")
            debug_log(f"Error analyzing {file_path}: {e}. ❌",
                        file=f"{self.current_file} - {self.current_version}", function=current_function)
        return analysis_lines


    def _append_to_text_area(self, text, tag=None):
        # function_name()
        # Function Description:
        # Appends text to the scrolled text area, ensuring the update happens on the main thread.
        # Also writes the text to the log file if it's open.
        self.root.after(0, lambda: self.text_area.insert(tk.END, text + "\n", tag))
        self.root.after(0, lambda: self.text_area.see(tk.END))

        # Write to log file
        if self.log_file:
            try:
                self.log_file.write(text + "\n")
            except Exception as e:
                # This error handling is for the log file writing itself
                debug_log(f"Error writing to Crawl.log: {e}. ❌",
                            file=f"{self.current_file} - {self.current_version}", function=inspect.currentframe().f_code.co_name)

    def _open_file(self, file_path, file_description):
        # function_name()
        # Function Description:
        # Opens a specified file or directory using the default system application.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting to open {file_description}: {file_path}. 📁",
                    file=f"{self.current_file} - {self.current_version}", function=current_function)

        if not os.path.exists(file_path):
            message = f"❌ Error: {file_description} not found at {file_path}"
            self._append_to_text_area(message, "header")
            debug_log(message, file=f"{self.current_file} - {self.current_version}", function=current_function)
            return

        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.uname().sysname == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', file_path], check=True)
            self._append_to_text_area(f"✅ Opened {file_description}: {file_path}", "header")
        except FileNotFoundError:
            message = f"❌ Error: Could not find application to open {file_description}."
            self._append_to_text_area(message, "header")
            debug_log(message, file=f"{self.current_file} - {self.current_version}", function=current_function)
        except Exception as e:
            message = f"❌ Error opening {file_description}: {e}"
            self._append_to_text_area(message, "header")
            debug_log(message, file=f"{self.current_file} - {self.current_version}", function=current_function)

    def _open_log_file(self):
        # function_name()
        # Function Description:
        # Command for the "Open Log" button. Opens the most recent Crawl.log file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                  file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.output_dir and os.path.isdir(self.output_dir):
            log_file_path = os.path.join(self.output_dir, "Crawl.log")
            self._open_file(log_file_path, "Crawl Log")
        else:
            crawl_dir = os.path.dirname(os.path.abspath(__file__))
            log_dirs = sorted([d for d in os.listdir(crawl_dir) if d.startswith("20") and len(d) == 14], reverse=True)
            if log_dirs:
                latest_log_dir = os.path.join(crawl_dir, log_dirs[0])
                log_file_path = os.path.join(latest_log_dir, "Crawl.log")
                self._open_file(log_file_path, "Crawl Log")
            else:
                messagebox.showinfo("File Not Found", "No crawl log directory or file found.")

    def _open_map_file(self):
        # function_name()
        # Function Description:
        # Command for the "Open Map" button. Opens the most recent MAP.txt file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                  file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.output_dir and os.path.isdir(self.output_dir):
            map_file_path = os.path.join(self.output_dir, "MAP.txt")
            self._open_file(map_file_path, "Program Map")
        else:
            crawl_dir = os.path.dirname(os.path.abspath(__file__))
            log_dirs = sorted([d for d in os.listdir(crawl_dir) if d.startswith("20") and len(d) == 14], reverse=True)
            if log_dirs:
                latest_log_dir = os.path.join(crawl_dir, log_dirs[0])
                map_file_path = os.path.join(latest_log_dir, "MAP.txt")
                self._open_file(map_file_path, "Program Map")
            else:
                messagebox.showinfo("File Not Found", "No map directory or file found.")

    def _open_everything_log_file(self):
        # function_name()
        # Function Description:
        # Command for the "Open All Code" button. Opens the most recent EVERYTHING.py.LOG file.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}",
                  file=f"{self.current_file} - {self.current_version}", function=current_function)
        if self.output_dir and os.path.isdir(self.output_dir):
            everything_log_file_path = os.path.join(self.output_dir, "EVERYTHING.py.LOG")
            self._open_file(everything_log_file_path, "Everything Log")
        else:
            crawl_dir = os.path.dirname(os.path.abspath(__file__))
            log_dirs = sorted([d for d in os.listdir(crawl_dir) if d.startswith("20") and len(d) == 14], reverse=True)
            if log_dirs:
                latest_log_dir = os.path.join(crawl_dir, log_dirs[0])
                everything_log_file_path = os.path.join(latest_log_dir, "EVERYTHING.py.LOG")
                self._open_file(everything_log_file_path, "Everything Log")
            else:
                messagebox.showinfo("File Not Found", "No everything log directory or file found.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide the main window initially

    selected_directory = filedialog.askdirectory(title="What directory do you want to crawl?")

    if selected_directory:
        # Destroy the temporary root window and create a new one for the app
        root.destroy()
        root = tk.Tk()
        app = FolderCrawlerApp(root, selected_directory)
        app._start_crawl() # Automatically start the crawl with the selected directory
        root.mainloop()
    else:
        print("No directory selected, exiting.")
        root.destroy()
