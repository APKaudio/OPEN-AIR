# OPEN AIR
OPEN AIR - 🌐📡🗺️ - Zone Awareness Processor



Of course. Here is a text-based breakdown of the OPEN-AIR software architecture based on the provided code.

## OPEN-AIR Software Architecture
The application is built on a layered architecture that separates the user interface from the core logic, data storage, and hardware communication.

## 1. Presentation Layer (GUI)
This is the user interface, built with Tkinter. It is responsible for displaying information and capturing user input.


main_app.py: The main application entry point that creates the root window and assembles the primary layout .


tabs/: This directory contains all the major user-facing functional tabs, such as TAB_INSTRUMENT_PARENT , 

TAB_SCANNING_PARENT , and 

TAB_PLOTTING_PARENT. Each parent tab manages its own set of child tabs for specific tasks.


display/: Manages the right-hand pane of the UI, which includes the real-time Scan Monitor plots, the application Console, and the Debug output area.





orchestrator/orchestrator_gui.py: Provides the primary Start, Stop, and Pause/Resume buttons that control the main scanning process .


## 2. Service & Logic Layer
This is the brain of the application. It contains the business logic, performs calculations, and manages the application's state in response to user actions.


orchestrator/orchestrator_logic.py: Manages the lifecycle of a scan (start, stop, pause) by controlling threading events .


tabs/Scanning/utils_scan_instrument.py: Contains the main _scan_thread_target function that executes the entire scan process, looping through frequency bands and collecting data from the instrument.

process_math/: A collection of modules for data analysis, including:


averaging_utils.py: Calculates statistics on scan data .


scan_stitch.py: Stitches multiple scan segments into a single cohesive file .


calculate_intermod.py: Calculates intermodulation distortion products .

utils_*.py files: Located within the tabs subdirectories, these files act as handlers for UI events. For example, 

tabs/Markers/utils_markers.py contains the logic to set a frequency on the instrument when a marker button is clicked.

## 3. Integration Layer (Translator)
This layer translates high-level application commands into the specific low-level commands required by the hardware. This abstraction allows the application to support different instrument models.

tabs/Instrument/Yakety_Yak.py: The core of the translator. It defines high-level functions like 

YakGet, YakSet, and YakDo .

DATA/visa_commands.csv: This file acts as a lookup table. 

Yakety_Yak.py uses it to find the correct VISA command string for a specific action (e.g., "FREQUENCY/CENTER") based on the connected instrument's model.


tabs/Instrument/utils_yak_visa.py: Contains the lowest-level wrapper functions, write_safe and query_safe, which directly use the pyvisa library to send commands and receive data from the device.



## 4. Data Layer (Persistence)
This layer is responsible for storing and retrieving data from files on the disk.

DATA/ directory: This is the central location for configuration and data files.


config.ini: Stores user preferences and the application's last state, such as window size and debug settings.


PRESETS.CSV, MARKERS.CSV: Store user-defined instrument presets and frequency markers.



Scan Output Folders: Raw .csv data files generated from scans are saved in a user-defined output folder, typically within DATA/SCANS.

## 5. Hardware Layer
This layer represents the physical Spectrum Analyzer device itself, which is controlled by the application via the Integration Layer.



---
config:
  layout: fixed
  use https://mermaid.live/ to view
---
flowchart TD
 subgraph A["Presentation Layer (GUI)"]
        A1("main_app.py (tk.Tk Root)")
        A2("tabs/ (Parent & Child Tabs for UI)")
        A3("display/ (Monitor, Console, Debug Panes)")
        A4("orchestrator/orchestrator_gui.py (Start/Stop/Pause)")
  end
 subgraph B["Service & Logic Layer"]
        B1("orchestrator/orchestrator_logic.py\n(Scan Lifecycle: Start, Stop, Pause)")
        B2("tabs/Scanning/utils_scan_instrument.py\n(Main Scan Thread & Sweep Logic)")
        B3("process_math/\n(Averaging, Stitching, Intermod, Plotting)")
        B4("tabs/.../utils_*.py\n(Event Handlers for Markers, Presets, etc.)")
        B5("src/\n(Initialization, Config, Dependencies)")
  end
 subgraph C["Integration Layer (Translator)"]
        C1("tabs/Instrument/Yakety_Yak.py\n(High-level command abstraction: YakGet, YakSet, YakDo)")
        C2("DATA/visa_commands.csv\n(Command Lookup Table)")
        C3("tabs/Instrument/utils_yak_visa.py\n(Low-level PyVISA wrappers: write_safe, query_safe)")
  end
 subgraph D["Data Layer (Persistence)"]
        D1("DATA/ Directory")
        D2("config.ini, PRESETS.CSV, MARKERS.CSV")
        D3("Output Scan Folders (*.csv)")
  end
 subgraph E["Hardware Layer"]
        E1("Spectrum Analyzer (Device)")
  end
    A -- "User Actions\n(e.g., Button Clicks)" --> B
    B -- "GUI Updates\n(e.g., Plot Data, Console Text)" --> A
    B -- Read/Write Data --> D
    B -- "High-Level Commands\n(e.g., 'Get Center Freq')" --> C
    C -- Reads Command Definitions --> C2
    C -- "Low-Level VISA Protocol\n(e.g., 'FREQuency:CENTer?')" --> E
    E -- Data Response --> C
    C -- Translated Data --> B
