OpenAir: Dynamic Instrument Control System

OpenAir is an open-source, Python-based framework designed to revolutionize the control and monitoring of test and measurement instruments, such as RF spectrum analyzers.

Unlike traditional instrument software with rigid, hard-coded interfaces, OpenAir utilizes a filesystem-driven dynamic GUI and a decoupled, message-driven architecture. This allows engineers to reorganize the user interface simply by renaming folders and to extend functionality without modifying the core codebase.

⚡ Key Features

Dynamic GUI Generation: The interface is built at runtime by scanning the display directory. Layouts (tabs, split panes) are defined by folder names, not code.

Decoupled Architecture: Components (UI, Logic, Hardware) communicate asynchronously via an MQTT message bus, ensuring system stability and modularity.

Hardware Agnostic: The system uses a command abstraction protocol. You send high-level instructions (e.g., "Set Freq"), and the managers translate them into instrument-specific SCPI commands.

Extensible: Add new features by simply dropping new "Manager" or "Worker" scripts into their respective directories.

🏗️ System Architecture

The system operates on a "Triad" of components connected by a central MQTT Message Bus:

graph TD
    GUI[Display / GUI] <-->|MQTT| BUS((MQTT Bus))
    MGR[Managers] <-->|MQTT| BUS
    WRK[Workers] <-->|MQTT| BUS
    WRK <-->|SCPI/VISA| HW[Instrument Hardware]


Display (GUI): Dynamically generated from the file structure. It sends user commands to the bus and visualizes data streams.

Managers (State): Passive components that manage instrument settings (e.g., FrequencyManager). They react to GUI commands and maintain the "desired state".

Workers (Data): Active background processes that continuously poll hardware (e.g., PeakPublisher) and publish data to the bus.

🚀 Installation & Setup

Prerequisites

Python 3.x

MQTT Broker: You must have an MQTT broker running locally (e.g., Mosquitto).

VISA Libraries: Required for hardware communication (e.g., NI-VISA or PyVISA-py).

Installation Steps

Clone the Repository:

git clone [https://github.com/APKaudio/OpenAir.git](https://github.com/APKaudio/OpenAir.git)
cd OpenAir


Install Dependencies:

pip install -r requirements.txt


Start the MQTT Broker:
Ensure your Mosquitto (or equivalent) service is running on the default port 1883.

Running the Application

Execute the main entry point to launch the system:

python OpenAir.py


Note: OpenAir.py handles the orchestration of the GUI, Managers, and Workers, establishing the MQTT links between them.

📂 Component Directory Structure

The project is organized to enforce the decoupled architecture. Here is a high-level overview of the component directories found in the root:

1. display/ (The Dynamic UI)

This directory is the user interface. The system recursively scans this folder to build the window.

Structure:

Folders named tab_Name create Tabs.

Folders named left_50, top_10, etc., create Split Panes (vertical/horizontal).

Python files inside these folders are loaded as widgets.

Customization: To change the layout, simply move or rename these folders. No coding required.

2. managers/ (State & Logic)

Contains the "Brains" of the operation. These scripts manage the state of the application.

manager_launcher.py: Enumerates and starts all manager classes.

YaketyYak: The translation layer that converts abstract commands into hardware-specific SCPI strings.

Role: Subscribes to GUI commands, validates them, and instructs Workers.

3. workers/ (Hardware Interaction)

Contains the "Muscle". These scripts handle the heavy lifting of data acquisition.

Worker_Launcher.py: Enumerates and starts background worker processes.

Role: They subscribe to state updates from Managers and publish raw data (e.g., spectrum traces, peak values) back to the GUI.

4. assets/ & datasets/

assets/: Images, icons, and static resources used by the GUI.

datasets/: Storage for recorded session data or simulation files.

🤝 Contributing

We welcome contributions!

New Hardware? Write a new Worker script.

New Visualization? Create a widget and drop it into the display/ folder.

New Logic? Add a Manager to handle the state.

License

Open Source. Free to use, modify, and fork.
