<<<<<<< Updated upstream
import subprocess
import sys
import os

def build():
    """
    Builds the OPEN-AIR executable for Windows using PyInstaller.
    
    IMPORTANT: This script must be run on a Windows machine with a properly
               configured Python environment and all project dependencies installed.
    """
    print("Starting Windows build process...")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    venv_path = os.path.join(project_root, '.venv')

    if not os.path.exists(venv_path):
        print(f"ERROR: Virtual environment not found at '{venv_path}'")
        sys.exit(1)

    # Construct the path to the pyinstaller executable within the virtual environment
    pyinstaller_executable = os.path.join(venv_path, 'Scripts', 'pyinstaller.exe')

    if not os.path.exists(pyinstaller_executable):
        print(f"ERROR: PyInstaller command not found at '{pyinstaller_executable}'. Make sure PyInstaller is installed in your virtual environment.")
        sys.exit(1)

    # Path to the spec file
    spec_file = os.path.join(project_root, 'OPEN-AIR.spec')

    if not os.path.exists(spec_file):
        print(f"ERROR: Could not find spec file at {spec_file}")
        sys.exit(1)
        
    print(f"Using PyInstaller from: {pyinstaller_executable}")
    print(f"Using spec file: {spec_file}")

    # Note: The OPEN-AIR.spec file will need to be adjusted for Windows.
    # Specifically, the 'datas' section for tcl/tk libraries will need
    # to point to the correct paths in your Windows Python environment.
    # For example:
    # datas=[
    #     ('C:\Users\YourUser\AppData\Local\Programs\Python\Python39\tcl\tcl8.6', 'tcl'),
    #     ('C:\Users\YourUser\AppData\Local\Programs\Python\Python39\tcl\tk8.6', 'tk')
    # ],
    print("IMPORTANT: Ensure the tcl/tk paths in OPEN-AIR.spec are correct for your Windows environment.")

    command = [
        pyinstaller_executable,
        spec_file,
        '--noconfirm' # Overwrite previous builds without asking
    ]

    print(f"Running command: {' '.join(command)}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip(), flush=True)
        
        return_code = process.poll()

        if return_code == 0:
            print("\nBuild completed successfully!")
            print(f"Executable is available in the '{os.path.join(project_root, 'dist')}' directory.")
        else:
            print(f"\nBuild failed with return code: {return_code}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
=======
from workers.active.worker_active_logging import debug_log, console_log
ENABLE_DEBUG = False

def debug_log_switch(message, file, version, function, console_print_func):
    if ENABLE_DEBUG:
        debug_log_switch(message, file, version, function, console_print_func)

def console_log_switch(message):
    if ENABLE_DEBUG:
        console_log_switch(message)

>>>>>>> Stashed changes
