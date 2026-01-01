import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import time
from typing import Dict, Any, List
import inspect
import orjson # Ensure orjson is imported

from workers.logger.logger import debug_logger
from workers.setup.config_reader import Config
from workers.logger.log_utils import _get_log_args
from workers.mqtt.mqtt_publisher_service import publish_payload
from workers.mqtt.mqtt_topic_utils import get_topic

app_constants = Config.get_instance()

# Globals
current_version = "20251230.180641.1"
current_version_hash = 20251230 * 180641 * 1

class FluxPlotter(tk.Frame):
    """
    A Tkinter-compatible Matplotlib graph widget that dynamically renders
    plots with multiple datasets based on a JSON configuration.
    
    Integrated with StateMirrorEngine to ensure 'instance_id' and standard 
    payload wrapping are applied to all transmissions.
    """

    def __init__(self, parent, config: Dict[str, Any], base_mqtt_topic_from_path: str, widget_id: str, **kwargs):
        self.subscriber_router = kwargs.pop('subscriber_router', None)
        self.state_mirror_engine = kwargs.pop('state_mirror_engine', None)
        super().__init__(parent, **kwargs)
        self.config = config
        self.base_mqtt_topic_from_path = base_mqtt_topic_from_path
        self.widget_id = widget_id
        self.plot_mode = config.get('plot_mode', 'time_domain')
        self.buffer_size = config.get('buffer_size', 100)

        # 🧪 Temporal Alignment: Fetch the GUID from the Engine!
        self.instance_id = "UNKNOWN_GUID"
        if self.state_mirror_engine and hasattr(self.state_mirror_engine, 'instance_id'):
            self.instance_id = self.state_mirror_engine.instance_id

        self.lines: Dict[str, Any] = {}
        self.x_data: Dict[str, deque] = {}
        self.y_data: Dict[str, deque] = {}
        self.datasets_config: Dict[str, Any] = {}

        # Introduce tk.StringVar for state management of all plot data
        # Stores JSON string of {"ds_id": {"x_data": [...], "y_data": [...]}}
        self.plot_data_var = tk.StringVar(value=orjson.dumps({}).decode())

        self._process_dataset_config()
        self._initialize_plot()
        self._load_all_initial_data() # This populates self.x_data and self.y_data

        # Bind trace to plot_data_var for visual updates and publishing
        self.plot_data_var.trace_add("write", self._on_plot_data_var_change)
        
        # 🚀 Register with StateMirrorEngine (handles subscription automatically)
        if self.state_mirror_engine:
            self.state_mirror_engine.register_widget(self.widget_id, self.plot_data_var, self.base_mqtt_topic_from_path, self.config)
            self.state_mirror_engine.initialize_widget_state(self.widget_id) # Restore/broadcast initial state

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 FluxPlotter '{self.widget_id}' initialized! Mode: {self.plot_mode}. Instance ID: {self.instance_id}",
                **_get_log_args()
            )

    def _on_plot_data_var_change(self, *args):
        """Callback for when plot_data_var changes (from internal or MQTT)."""
        new_plot_data_json = self.plot_data_var.get()
        try:
            new_plot_data = orjson.loads(new_plot_data_json)
            if not isinstance(new_plot_data, dict):
                raise ValueError("Expected dictionary of plot data.")

            for ds_id, data in new_plot_data.items():
                if ds_id in self.lines and 'x_data' in data and 'y_data' in data:
                    self.load_initial_data(ds_id, data['x_data'], data['y_data'])
            
            # Publish Standardized State (only if initiated by user interaction, not self-echo)
            # The _silent_update mechanism in StateMirrorEngine handles preventing echoes
            if self.state_mirror_engine and not self.state_mirror_engine._silent_update:
                base_topic = self.state_mirror_engine.base_topic if self.state_mirror_engine else "OPEN-AIR"
                topic = get_topic(base_topic, self.base_mqtt_topic_from_path, self.widget_id)
                
                payload = {
                    "val": new_plot_data,
                    "ts": time.time(),
                    "instance_id": self.instance_id,
                    "src": "FluxPlotter"
                }
                publish_payload(topic, orjson.dumps(payload), retain=True)

        except (orjson.JSONDecodeError, ValueError, TypeError) as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error processing plot_data_var change: {e}", **_get_log_args())


    def _process_dataset_config(self):
        """Processes the 'datasets' from config or adapts old single-dataset format."""
        if 'datasets' in self.config and isinstance(self.config['datasets'], list):
            for ds_config in self.config['datasets']:
                ds_id = ds_config.get('id')
                if ds_id:
                    self.datasets_config[ds_id] = ds_config
        else:
            # Adapt old single-dataset format for backward compatibility
            ds_id = self.config.get('id', 'default_dataset')
            self.datasets_config[ds_id] = {
                "id": ds_id,
                "initial_csv_data": self.config.get('initial_csv_data'),
                "style": self.config.get('style', {})
            }

    def _initialize_plot(self):
        """Initializes the matplotlib figure, axes, and canvas."""
        self.fig = Figure(figsize=(
            self.config.get('layout', {}).get('width', 5) / 100,
            self.config.get('layout', {}).get('height', 4) / 100
        ), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        bg_color = self.config.get('style', {}).get('background_color', 'black')
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        for ds_id, ds_config in self.datasets_config.items():
            style = ds_config.get('style', {})
            line, = self.ax.plot([], [],
                                 color=style.get('line_color', 'cyan'),
                                 linewidth=style.get('line_width', 1),
                                 label=ds_config.get('label', ds_id))
            self.lines[ds_id] = line
            self.x_data[ds_id] = deque(maxlen=self.buffer_size)
            self.y_data[ds_id] = deque(maxlen=self.buffer_size)
        
        if len(self.datasets_config) > 1:
            legend = self.ax.legend()
            if legend:
                legend.get_frame().set_facecolor(bg_color)
                for text in legend.get_texts():
                    text.set_color("white")

        x_axis_config = self.config.get('axis', {}).get('x', {})
        y_axis_config = self.config.get('axis', {}).get('y', {})
        self.ax.set_xlabel(x_axis_config.get('label', 'X-axis'), color=x_axis_config.get('color', 'white'))
        self.ax.set_ylabel(y_axis_config.get('label', 'Y-axis'), color=y_axis_config.get('color', 'white'))
        self.ax.set_title(self.config.get('title', 'Plot'), color=self.config.get('style', {}).get('title_color', 'white'))
        self.ax.tick_params(axis='x', colors=x_axis_config.get('color', 'white'))
        self.ax.tick_params(axis='y', colors=y_axis_config.get('color', 'white'))
        self.ax.grid(True, color=self.config.get('style', {}).get('grid_color', 'darkgrey'))

        if x_axis_config.get('scale') == 'log': self.ax.set_xscale('log')
        if y_axis_config.get('scale') == 'log': self.ax.set_yscale('log')

        if self.plot_mode in ['time_domain', 'frequency_domain']:
            self.ax.set_xlim(x_axis_config.get('min', 0), x_axis_config.get('max', 1))
            self.ax.set_ylim(y_axis_config.get('min', 0), y_axis_config.get('max', 1))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _load_all_initial_data(self):
        """Loads initial data for all configured datasets."""
        current_plot_data = {}
        for ds_id, ds_config in self.datasets_config.items():
            csv_data = ds_config.get('initial_csv_data')
            if csv_data:
                try:
                    x_values, y_values = [], []
                    lines = csv_data.strip().split('\n')
                    # Skip header if present
                    if lines and not lines[0].replace('.', '', 1).replace('-', '', 1).replace(',', '').isdigit():
                        lines = lines[1:]
                    for line in lines:
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            x_values.append(float(parts[0]))
                            y_values.append(float(parts[1]))
                    self.load_initial_data(ds_id, x_values, y_values)
                    current_plot_data[ds_id] = {"x_data": list(self.x_data[ds_id]), "y_data": list(self.y_data[ds_id])}
                except Exception as e:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"❌ Error loading initial CSV for dataset '{ds_id}': {e}", **_get_log_args())
        self.plot_data_var.set(orjson.dumps(current_plot_data).decode())


    def load_initial_data(self, dataset_id: str, x_values: List[float], y_values: List[float]):
        """Loads a complete set of initial data points for a specific dataset."""
        if dataset_id not in self.lines: return

        self.x_data[dataset_id].clear()
        self.y_data[dataset_id].clear()
        self.x_data[dataset_id].extend(x_values)
        self.y_data[dataset_id].extend(y_values)
        
        self.lines[dataset_id].set_data(list(self.x_data[dataset_id]), list(self.y_data[dataset_id]))
        self._autoscale_and_redraw()

    # REMOVED _publish_initial_data as it's handled by plot_data_var trace

    def _publish_current_data(self, dataset_id: str):
        """
        Updates the plot_data_var with the current data for a specific dataset.
        The trace on plot_data_var will then handle publishing to MQTT.
        """
        if dataset_id not in self.lines: return

        current_plot_data = orjson.loads(self.plot_data_var.get())
        current_plot_data[dataset_id] = {
            "x_data": list(self.x_data[dataset_id]),
            "y_data": list(self.y_data[dataset_id])
        }
        self.plot_data_var.set(orjson.dumps(current_plot_data).decode())

    # REMOVED _subscribe_to_data_topics as it's handled by StateMirrorEngine
    
    def _on_data_update(self, topic, payload, dataset_id):
        """
        Callback to handle incoming data from MQTT for a specific dataset.
        Handles both raw data and 'StateMirror' enveloped data.
        """
        try:
            data = orjson.loads(payload)
            
            # 🕵️ Unwrap the envelope if present
            if 'val' in data and 'instance_id' in data:
                # 🛑 Infinite Loop Protection: Don't process our own echoes!
                if data.get('instance_id') == self.instance_id:
                    return
                # Extract the inner value
                data = data['val']

            # Process the data and update the tk.StringVar
            if isinstance(data, dict):
                current_plot_data = orjson.loads(self.plot_data_var.get())
                current_plot_data[dataset_id] = {"x_data": data.get('x_data', []), "y_data": data.get('y_data', [])}
                self.plot_data_var.set(orjson.dumps(current_plot_data).decode())
            
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error processing MQTT update for dataset '{dataset_id}': {e}", **_get_log_args())

    def update_plot(self, dataset_id: str, x_new: float, y_new: float):
        if dataset_id not in self.lines: return

        if self.plot_mode == 'trend_logger':
            self.x_data[dataset_id].append(x_new)
            self.y_data[dataset_id].append(y_new)
        else:
            if len(self.x_data[dataset_id]) < self.buffer_size:
                self.x_data[dataset_id].append(x_new)
                self.y_data[dataset_id].append(y_new)
            else:
                self.x_data[dataset_id].rotate(-1)
                self.y_data[dataset_id].rotate(-1)
                self.x_data[dataset_id][-1] = x_new
                self.y_data[dataset_id][-1] = y_new
        
        # Update plot_data_var, which will trigger redraw and MQTT publish
        self._publish_current_data(dataset_id) # Call the function that updates plot_data_var
    
    def clear_plot(self, dataset_id: str = None):
        """Clears data from a specific dataset or all datasets."""
        current_plot_data = orjson.loads(self.plot_data_var.get())
        if dataset_id and dataset_id in self.lines:
            self.x_data[dataset_id].clear()
            self.y_data[dataset_id].clear()
            self.lines[dataset_id].set_data([], [])
            current_plot_data[dataset_id] = {"x_data": [], "y_data": []}
        else: # Clear all
            for ds_id in self.lines:
                self.x_data[ds_id].clear()
                self.y_data[ds_id].clear()
                self.lines[ds_id].set_data([], [])
                current_plot_data[ds_id] = {"x_data": [], "y_data": []}
        
        self.plot_data_var.set(orjson.dumps(current_plot_data).decode())
        self._autoscale_and_redraw()

# Example usage (for testing, if needed)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("FluxPlotter Test")

    # Time Domain Config
    time_config = {
        "id": "test_time_domain",
        "type": "plot_widget",
        "plot_mode": "time_domain",
        "title": "Oscilloscope - Test",
        "layout": { "row": 0, "col": 0, "width": 600, "height": 400 },
        "axis": {
            "x": { "label": "Time (s)", "scale": "linear", "min": 0, "max": 0.1, "color": "white" },
            "y": { "label": "Voltage (V)", "scale": "linear", "min": -1, "max": 1, "color": "yellow" }
        },
        "style": {
            "background_color": "black",
            "grid_color": "darkgrey",
            "line_color": "cyan",
            "line_width": 2
        }
    }

    plotter = FluxPlotter(root, time_config, "TEST/PATH", "plot1")
    plotter.pack(fill=tk.BOTH, expand=True)
    root.mainloop()