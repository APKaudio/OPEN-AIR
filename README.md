# OPEN AIR
OPEN AIR - 🌐📡🗺️ - Zone Awareness Processor


```mermaid
flowchart TD
    subgraph A [Presentation Layer (GUI)]
        A1("main_app.py (tk.Tk Root)")
        A2("<b>tabs/</b> (Parent & Child Tabs for UI)")
        A3("<b>display/</b> (Monitor, Console, Debug Panes)")
        A4("<b>orchestrator/orchestrator_gui.py</b> (Start/Stop/Pause)")
    end

    subgraph B [Service & Logic Layer]
        B1("<b>orchestrator/orchestrator_logic.py</b><br/>(Scan Lifecycle: Start, Stop, Pause)")
        B2("<b>tabs/Scanning/utils_scan_instrument.py</b><br/>(Main Scan Thread & Sweep Logic)")
        B3("<b>process_math/</b><br/>(Averaging, Stitching, Intermod, Plotting)")
        B4("<b>tabs/.../utils_*.py</b><br/>(Event Handlers for Markers, Presets, etc.)")
        B5("<b>src/</b><br/>(Initialization, Config, Dependencies)")
    end

    subgraph C [Integration Layer (Translator)]
        C1("<b>tabs/Instrument/Yakety_Yak.py</b><br/>(High-level command abstraction: YakGet, YakSet, YakDo)")
        C2("<b>DATA/visa_commands.csv</b><br/>(Command Lookup Table)")
        C3("<b>tabs/Instrument/utils_yak_visa.py</b><br/>(Low-level PyVISA wrappers: write_safe, query_safe)")
    end

    subgraph D [Data Layer (Persistence)]
        D1("<b>DATA/</b> Directory")
        D2("config.ini, PRESETS.CSV, MARKERS.CSV")
        D3("Output Scan Folders (*.csv)")
    end
    
    subgraph E [Hardware Layer]
        E1("Spectrum Analyzer (Device)")
    end

    A -- "User Actions<br/>(e.g., Button Clicks)" --> B
    B -- "GUI Updates<br/>(e.g., Plot Data, Console Text)" --> A
    B -- "Read/Write Data" --> D
    B -- "High-Level Commands<br/>(e.g., 'Get Center Freq')" --> C
    C -- "Reads Command Definitions" --> C2
    C -- "Low-Level VISA Protocol<br/>(e.g., 'FREQuency:CENTer?')" --> E
    E -- "Data Response" --> C
    C -- "Translated Data" --> B
```