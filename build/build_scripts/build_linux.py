# build/build_scripts/build_linux.py
#
# The hash calculation drops the leading zero from the hour (e.g., 08 -> 8)
# As the current hour is 20, no change is needed.

Current_Date = 20251129  ##Update on the day the change was made
Current_Time = 120000  ## update at the time it was edited and compiled
Current_iteration = 1 ## a running version number - incriments by one each time 

current_version = f"{Current_Date}.{Current_Time}.{Current_iteration}"
current_version_hash = (Current_Date * Current_Time * Current_iteration)

import subprocess
import sys
import os

def build():
    """
    Builds the OPEN-AIR executable for Linux using PyInstaller.
    """
    print("Starting Linux build process...")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    venv_path = os.path.join(project_root, '.venv')
    
    if not os.path.exists(venv_path):
        print(f"ERROR: Virtual environment not found at '{venv_path}'")
        print("Please create a virtual environment and install the dependencies from requirements.txt")
        sys.exit(1)

    # Construct the path to the pyinstaller executable within the virtual environment
    pyinstaller_executable = os.path.join(venv_path, 'bin', 'pyinstaller')

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

    dist_path = os.path.join(project_root, 'build', 'dist')

    command = [
        pyinstaller_executable,
        spec_file,
        '--noconfirm', # Overwrite previous builds without asking
        '--distpath',
        dist_path
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
            print(f"Executable is available in the '{dist_path}' directory.")
        else:
            print(f"\nBuild failed with return code: {return_code}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
