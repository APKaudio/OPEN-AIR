# OPEN AIR
OPEN AIR - 🌐📡🗺️ - Zone Awareness Processor


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
    B -- "Read/Write Data" --> D
    B -- "High-Level Commands\n(e.g., 'Get Center Freq')" --> C
    C -- "Reads Command Definitions" --> C2
    C -- "Low-Level VISA Protocol\n(e.g., 'FREQuency:CENTer?')" --> E
    E -- "Data Response" --> C
    C -- "Translated Data" --> B