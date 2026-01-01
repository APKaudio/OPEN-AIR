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
    
    Each dataset is exposed as its own MQTT topic for external updates.
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

        self.instance_id = "UNKNOWN_GUID"
        if self.state_mirror_engine and hasattr(self.state_mirror_engine, 'instance_id'):
            self.instance_id = self.state_mirror_engine.instance_id

        self.lines: Dict[str, Any] = {}
        self.x_data: Dict[str, deque] = {}
        self.y_data: Dict[str, deque] = {}
        self.datasets_config: Dict[str, Any] = {}
        self.dataset_vars: Dict[str, tk.StringVar] = {}

        self._process_dataset_config()
        self._initialize_plot()
        self._load_all_initial_data()

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 FluxPlotter '{self.widget_id}' initialized! Mode: {self.plot_mode}. Instance ID: {self.instance_id}",
                **_get_log_args()
            )

    def _on_dataset_var_change(self, dataset_id, *args):
        """Callback for when an individual dataset's StringVar changes."""
        if dataset_id not in self.dataset_vars:
            return
            
        csv_data = self.dataset_vars[dataset_id].get()
        try:
            x_values, y_values = [], []
            lines = csv_data.strip().split('\n')
            if lines and 'x' in lines[0].lower() and 'y' in lines[0].lower(): # Simple header check
                lines = lines[1:]
            for line in lines:
                if not line.strip(): continue
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    x_values.append(float(parts[0]))
                    y_values.append(float(parts[1]))
            
            self.load_initial_data(dataset_id, x_values, y_values)

        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error processing CSV data for dataset '{dataset_id}': {e}", **_get_log_args())

    def _process_dataset_config(self):
        """Processes 'datasets', creates StringVars, and registers them for MQTT."""
        if 'datasets' in self.config and isinstance(self.config['datasets'], list):
            for ds_config in self.config['datasets']:
                ds_id = ds_config.get('id')
                if ds_id:
                    self.datasets_config[ds_id] = ds_config
                    
                    dataset_var = tk.StringVar()
                    self.dataset_vars[ds_id] = dataset_var
                    
                    if self.state_mirror_engine:
                        dataset_path = f"{self.widget_id}/datasets/{ds_id}"
                        register_config = {
                            "type": "_PlotDataset",
                            "id": ds_id,
                            "value_default": ds_config.get("initial_csv_data", "")
                        }
                        self.state_mirror_engine.register_widget(dataset_path, dataset_var, self.base_mqtt_topic_from_path, register_config)
                        
                        callback = lambda *args, ds_id=ds_id: self._on_dataset_var_change(ds_id, *args)
                        dataset_var.trace_add("write", callback)
                        
                        self.state_mirror_engine.initialize_widget_state(dataset_path)

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
        """Loads initial data for all configured datasets by setting the StringVars."""
        for ds_id, ds_config in self.datasets_config.items():
            csv_data = ds_config.get('initial_csv_data')
            if csv_data and ds_id in self.dataset_vars:
                self.dataset_vars[ds_id].set(csv_data)

    def load_initial_data(self, dataset_id: str, x_values: List[float], y_values: List[float]):
        """Loads a complete set of initial data points for a specific dataset."""
        if dataset_id not in self.lines: return

        self.x_data[dataset_id].clear()
        self.y_data[dataset_id].clear()
        self.x_data[dataset_id].extend(x_values)
        self.y_data[dataset_id].extend(y_values)
        
        self.lines[dataset_id].set_data(list(self.x_data[dataset_id]), list(self.y_data[dataset_id]))
        self._autoscale_and_redraw()

    def update_plot(self, dataset_id: str, x_new: float, y_new: float):
        """Updates a dataset with a new data point and publishes the change."""
        if dataset_id not in self.lines: return

        if self.plot_mode == 'trend_logger':
            self.x_data[dataset_id].append(x_new)
            self.y_data[dataset_id].append(y_new)
        else: # time_domain or frequency_domain
            if len(self.x_data[dataset_id]) < self.buffer_size:
                self.x_data[dataset_id].append(x_new)
                self.y_data[dataset_id].append(y_new)
            else:
                self.x_data[dataset_id].popleft()
                self.y_data[dataset_id].popleft()
                self.x_data[dataset_id].append(x_new)
                self.y_data[dataset_id].append(y_new)

        new_csv_data = "x,y\n" + "\n".join([f"{x},{y}" for x, y in zip(self.x_data[dataset_id], self.y_data[dataset_id])])
        self.dataset_vars[dataset_id].set(new_csv_data)
    
    def clear_plot(self, dataset_id: str = None):
        """Clears data from a specific dataset or all datasets."""
        if dataset_id and dataset_id in self.dataset_vars:
            self.dataset_vars[dataset_id].set("x,y\n")
        else:
            for ds_id in self.dataset_vars:
                self.dataset_vars[ds_id].set("x,y\n")

    def _autoscale_and_redraw(self):
        """Autoscales axes and redraws the canvas."""
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

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