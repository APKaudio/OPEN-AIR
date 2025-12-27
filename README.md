# OpenAir: Dynamic Instrument Control System

**OpenAir** is an open-source, Python-based framework designed to revolutionize the control and monitoring of test and measurement instruments, such as RF spectrum analyzers.

Unlike traditional instrument software with rigid, hard-coded interfaces, OpenAir utilizes a **filesystem-driven dynamic GUI** and a **decoupled, message-driven architecture**. This allows engineers to reorganize the user interface simply by renaming folders and to extend functionality without modifying the core codebase.

## ⚡ Key Features

* **Dynamic GUI Generation**: The interface is built at runtime by scanning the `display` directory. Layouts (tabs, split panes) are defined by folder names, not code.
* **Decoupled Architecture**: Components (UI, Logic, Hardware) communicate asynchronously via an MQTT message bus, ensuring system stability and modularity.
* **Hardware Agnostic**: The system uses a command abstraction protocol. You send high-level instructions (e.g., "Set Freq"), and the managers translate them into instrument-specific SCPI commands.
* **Extensible**: Add new features by simply dropping new "Manager" or "Worker" scripts into their respective directories.

---

## 🏗️ System Architecture

The system operates on a "Triad" of components connected by a central MQTT Message Bus:

```mermaid
graph TD
    GUI[Display / GUI] <-->|MQTT| BUS((MQTT Bus))
    MGR[Managers] <-->|MQTT| BUS
    WRK[Workers] <-->|MQTT| BUS
    WRK <-->|SCPI/VISA| HW[Instrument Hardware]
