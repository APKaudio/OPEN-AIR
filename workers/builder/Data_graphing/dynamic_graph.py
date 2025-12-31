# display/dynamic_graph.py
#
# A Tkinter-compatible Matplotlib graph widget that dynamically renders
# plots with multiple datasets based on a JSON configuration.
# Now fully integrated with the State Mirror Engine for standardized MQTT publishing.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no charge to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
# Version 20251230.180641.1

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import time
from typing import Dict, Any, List
import inspect

from workers.logger.logger import debug_logger
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args
from workers.mqtt.mqtt_publisher_service import publish_payload
from workers.utils.topic_utils import get_topic
import orjson

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

        self._process_dataset_config()
        self._initialize_plot()
        self._load_all_initial_data()
        
        # 🚀 Initialization Sequence
        self._publish_initial_data()
        self._subscribe_to_data_topics()

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"🧪 FluxPlotter '{self.widget_id}' initialized! Mode: {self.plot_mode}. Instance ID: {self.instance_id}",
                **_get_log_args()
            )

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
                except Exception as e:
                    if app_constants.global_settings['debug_enabled']:
                        debug_logger(message=f"❌ Error loading initial CSV for dataset '{ds_id}': {e}", **_get_log_args())

    def load_initial_data(self, dataset_id: str, x_values: List[float], y_values: List[float]):
        """Loads a complete set of initial data points for a specific dataset."""
        if dataset_id not in self.lines: return

        self.x_data[dataset_id].clear()
        self.y_data[dataset_id].clear()
        self.x_data[dataset_id].extend(x_values)
        self.y_data[dataset_id].extend(y_values)
        
        self.lines[dataset_id].set_data(list(self.x_data[dataset_id]), list(self.y_data[dataset_id]))
        self._autoscale_and_redraw()

    def _autoscale_and_redraw(self):
        """Autoscales axes based on all visible data and redraws the canvas."""
        if self.plot_mode not in ['time_domain', 'frequency_domain']:
            x_axis_config = self.config.get('axis', {}).get('x', {})
            y_axis_config = self.config.get('axis', {}).get('y', {})
            
            if x_axis_config.get('auto_scroll', False):
                min_x, max_x = float('inf'), float('-inf')
                for x_deq in self.x_data.values():
                    if x_deq:
                        min_x = min(min_x, x_deq[0])
                        max_x = max(max_x, x_deq[-1])
                if min_x != float('inf'): self.ax.set_xlim(min_x, max_x)

            if y_axis_config.get('auto_scale', False):
                min_y, max_y = float('inf'), float('-inf')
                for y_deq in self.y_data.values():
                    if y_deq:
                        min_y = min(min_y, min(y_deq))
                        max_y = max(max_y, max(y_deq))
                if min_y != float('inf'):
                    padding = (max_y - min_y) * 0.1 if max_y != min_y else 1.0
                    self.ax.set_ylim(min_y - padding, max_y + padding)

        self.fig.canvas.draw_idle()

    def _publish_initial_data(self):
        """Publishes the initial data of all datasets to MQTT."""
        for ds_id in self.datasets_config:
            self._publish_current_data(ds_id)

    def _publish_current_data(self, dataset_id: str):
        """
        Publishes the current data for a specific dataset to MQTT using the standardized envelope.
        Format: {"val": {...}, "ts": <timestamp>, "instance_id": <guid>}
        """
        try:
            # Construct the topic correctly. 
            # Note: We append the dataset_id to keep the tree clean.
            topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, dataset_id, "data")
            
            # The actual value payload
            data_val = {
                "x_data": list(self.x_data[dataset_id]),
                "y_data": list(self.y_data[dataset_id])
            }
            
            # 🧪 Standardizing the Envelope!
            # We wrap it just like StateMirrorEngine does.
            payload = {
                "val": data_val,
                "ts": time.time(),
                "instance_id": self.instance_id,  # 🔑 The Key!
                "src": "FluxPlotter"
            }
            
            publish_payload(topic, orjson.dumps(payload), retain=True)
            
        except Exception as e:
             if app_constants.global_settings['debug_enabled']:
                debug_logger(f"❌ Error publishing data for dataset '{dataset_id}': {e}", **_get_log_args())

    def _subscribe_to_data_topics(self):
        if self.subscriber_router:
            for ds_id in self.datasets_config:
                try:
                    # Subscribe to the same topic structure we publish to
                    input_topic = get_topic(self.base_mqtt_topic_from_path, self.widget_id, ds_id, "data")
                    self.subscriber_router.subscribe_to_topic(input_topic, lambda t, p, ds=ds_id: self._on_data_update(t, p, ds))
                except Exception as e:
                     if app_constants.global_settings['debug_enabled']:
                        debug_logger(f"❌ Error subscribing to topic for dataset '{ds_id}': {e}", **_get_log_args())
    
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

            # Process the data
            if 'x_data' in data and 'y_data' in data:
                self.load_initial_data(dataset_id, data['x_data'], data['y_data'])
            elif 'x' in data and 'y' in data:
                self.update_plot(dataset_id, data['x'], data['y'])
                
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
        
        self.lines[dataset_id].set_data(list(self.x_data[dataset_id]), list(self.y_data[dataset_id]))
        self._autoscale_and_redraw()
    
    def clear_plot(self, dataset_id: str = None):
        """Clears data from a specific dataset or all datasets."""
        if dataset_id and dataset_id in self.lines:
            self.x_data[dataset_id].clear()
            self.y_data[dataset_id].clear()
            self.lines[dataset_id].set_data([], [])
        else: # Clear all
            for ds_id in self.lines:
                self.x_data[ds_id].clear()
                self.y_data[ds_id].clear()
                self.lines[ds_id].set_data([], [])
        
        self.fig.canvas.draw_idle()

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