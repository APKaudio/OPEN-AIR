import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import time
from typing import Dict, Any, List

from workers.logger.logger import debug_logger
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args

app_constants = Config.get_instance()

class FluxPlotter(tk.Frame):
    """
    A Tkinter-compatible Matplotlib graph widget that dynamically renders
    time domain, frequency domain, or trend logger plots based on a JSON configuration.
    """

    def __init__(self, parent, config: Dict[str, Any], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config = config
        self.plot_mode = config.get('plot_mode', 'time_domain')
        self.buffer_size = config.get('buffer_size', 100) # For trend_logger
        self.data_source = config.get('data_source', None)

        self.x_data: deque = deque(maxlen=self.buffer_size)
        self.y_data: deque = deque(maxlen=self.buffer_size)

        self._initialize_plot()

        # Load initial CSV data if provided
        if 'initial_csv_data' in self.config:
            self.load_initial_data_from_csv_string(self.config['initial_csv_data'])

        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"⚡ Plotter initialized! Mode: {self.plot_mode}, ID: {self.config.get('id', 'N/A')}",
                **_get_log_args()
            )

    def _initialize_plot(self):
        """Initializes the matplotlib figure, axes, and canvas."""
        # Figure and Axes setup
        self.fig = Figure(figsize=(
            self.config.get('layout', {}).get('width', 5) / 100,
            self.config.get('layout', {}).get('height', 4) / 100
        ), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Apply styles
        self.fig.patch.set_facecolor(self.config.get('style', {}).get('background_color', 'black'))
        self.ax.set_facecolor(self.config.get('style', {}).get('background_color', 'black'))

        self.line, = self.ax.plot([], [],
                                  color=self.config.get('style', {}).get('line_color', 'cyan'),
                                  linewidth=self.config.get('style', {}).get('line_width', 1))

        # Configure axes
        x_axis_config = self.config.get('axis', {}).get('x', {})
        y_axis_config = self.config.get('axis', {}).get('y', {})

        self.ax.set_xlabel(x_axis_config.get('label', 'X-axis'), color=x_axis_config.get('color', 'white'))
        self.ax.set_ylabel(y_axis_config.get('label', 'Y-axis'), color=y_axis_config.get('color', 'white'))
        self.ax.set_title(self.config.get('title', 'Plot'), color=self.config.get('style', {}).get('line_color', 'white')) # Use line_color for title

        self.ax.tick_params(axis='x', colors=x_axis_config.get('color', 'white'))
        self.ax.tick_params(axis='y', colors=y_axis_config.get('color', 'white'))
        self.ax.grid(True, color=self.config.get('style', {}).get('grid_color', 'darkgrey'))


        # Apply scales
        if x_axis_config.get('scale') == 'log':
            self.ax.set_xscale('log')
        if y_axis_config.get('scale') == 'log':
            self.ax.set_yscale('log')

        # Apply limits for fixed scales (time_domain, frequency_domain)
        if self.plot_mode in ['time_domain', 'frequency_domain']:
            self.ax.set_xlim(x_axis_config.get('min', 0), x_axis_config.get('max', 1))
            self.ax.set_ylim(y_axis_config.get('min', 0), y_axis_config.get('max', 1))

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def load_initial_data_from_csv_string(self, csv_data_string: str):
        """
        Parses a CSV string and loads the data into the plotter.
        Assumes the first column is x and the second is y.
        """
        x_values = []
        y_values = []
        try:
            lines = csv_data_string.strip().split('\n')
            # Skip header if present (check for non-numeric first line after strip)
            if lines and not lines[0].replace('.', '', 1).replace('-', '', 1).isdigit():
                lines = lines[1:]

            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    x_values.append(float(parts[0]))
                    y_values.append(float(parts[1]))
            
            self.load_initial_data(x_values, y_values)
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"📊 Initial CSV data loaded for plot '{self.config.get('id', 'N/A')}'",
                    **_get_log_args()
                )
        except Exception as e:
            if app_constants.global_settings['debug_enabled']:
                debug_logger(
                    message=f"❌ Error loading initial CSV data for plot '{self.config.get('id', 'N/A')}': {e}",
                    **_get_log_args()
                )

    def load_initial_data(self, x_values: List[float], y_values: List[float]):
        """
        Loads a complete set of initial data points into the plot.
        This is for static initial data, not for dynamic updates.
        """
        self.x_data.clear()
        self.y_data.clear()
        self.x_data.extend(x_values)
        self.y_data.extend(y_values)
        
        # Adjust x and y limits based on initial data if not fixed
        x_axis_config = self.config.get('axis', {}).get('x', {})
        y_axis_config = self.config.get('axis', {}).get('y', {})

        if self.plot_mode not in ['time_domain', 'frequency_domain']: # Only for trend_logger or modes without fixed limits
             if len(x_values) > 1 and x_axis_config.get('auto_scroll', False):
                self.ax.set_xlim(min(x_values), max(x_values))
             if len(y_values) > 1 and y_axis_config.get('auto_scale', False):
                min_y, max_y = min(y_values), max(y_values)
                padding_y = (max_y - min_y) * 0.1 # 10% padding
                self.ax.set_ylim(min_y - padding_y, max_y + padding_y)
        
        self.line.set_data(list(self.x_data), list(self.y_data))
        self.fig.canvas.draw_idle()

    def update_plot(self, x_new: float, y_new: float):
        """
        Updates the plot with new data points.
        For trend_logger, it appends data and handles auto-scrolling/scaling.
        For other modes, it updates the data for the fixed window.
        """
        if self.plot_mode == 'trend_logger':
            self.x_data.append(x_new)
            self.y_data.append(y_new)
        else: # For fixed window plots, just update the current data
            # This needs more sophisticated handling if it's truly "fixed window" like an oscilloscope.
            # For simplicity now, we'll just replace the data or append if it's small.
            # A true oscilloscope would often just update the existing data in place or shift.
            if len(self.x_data) < self.buffer_size:
                self.x_data.append(x_new)
                self.y_data.append(y_new)
            else:
                self.x_data.rotate(-1)
                self.y_data.rotate(-1)
                self.x_data[-1] = x_new
                self.y_data[-1] = y_new

        self.line.set_data(list(self.x_data), list(self.y_data))

        # Handle auto-scrolling and auto-scaling for trend_logger
        if self.plot_mode == 'trend_logger':
            x_axis_config = self.config.get('axis', {}).get('x', {})
            y_axis_config = self.config.get('axis', {}).get('y', {})

            if x_axis_config.get('auto_scroll', False) and len(self.x_data) > 1:
                self.ax.set_xlim(self.x_data[0], self.x_data[-1])
            
            if y_axis_config.get('auto_scale', False) and len(self.y_data) > 1:
                min_y, max_y = min(self.y_data), max(self.y_data)
                padding_y = (max_y - min_y) * 0.1 # 10% padding
                self.ax.set_ylim(min_y - padding_y, max_y + padding_y)
            elif 'min' in y_axis_config and 'max' in y_axis_config: # Fallback to fixed if auto_scale is false or no data
                 self.ax.set_ylim(y_axis_config.get('min'), y_axis_config.get('max'))

            self.fig.canvas.draw_idle()
            # self.fig.canvas.flush_events() # Might be needed for very fast updates

        else: # For fixed plots, redraw without relim
            self.fig.canvas.draw_idle()
    
    def clear_plot(self):
        """Clears all data from the plot."""
        self.x_data.clear()
        self.y_data.clear()
        self.line.set_data([], [])
        self.fig.canvas.draw_idle()
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"📊 Plot with ID '{self.config.get('id', 'N/A')}' cleared.",
                **_get_log_args()
            )


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

    # Trend Logger Config
    trend_config = {
        "id": "test_trend_logger",
        "type": "plot_widget",
        "plot_mode": "trend_logger",
        "title": "Voltage Drift Over Time - Test",
        "buffer_size": 200,
        "layout": { "row": 0, "col": 0, "width": 600, "height": 400 },
        "axis": {
            "x": { "label": "Timestamp", "auto_scroll": True, "color": "white" },
            "y": { "label": "Measured (V)", "auto_scale": True, "color": "red", "min": 0, "max": 5 } # min/max here are fallback if auto_scale is off or no data yet
        },
        "style": {
            "background_color": "white",
            "grid_color": "lightgrey",
            "line_color": "red",
            "line_width": 1
        }
    }

    plotter = FluxPlotter(root, time_config)
    plotter.pack(fill=tk.BOTH, expand=True)

    # Example update function for time domain
    import math
    _time = 0.0
    def update_time_plot():
        global _time
        _time += 0.005
        y_val = math.sin(_time * 100) * 0.8
        plotter.update_plot(_time, y_val)
        root.after(50, update_time_plot)

    # plotter_trend = FluxPlotter(root, trend_config)
    # plotter_trend.pack(fill=tk.BOTH, expand=True)

    # _trend_time = 0
    # def update_trend_plot():
    #     global _trend_time
    #     _trend_time += 1
    #     y_val = math.sin(_trend_time * 0.1) + (_trend_time * 0.01)
    #     plotter_trend.update_plot(_trend_time, y_val)
    #     root.after(100, update_trend_plot)
    
    # update_time_plot()
    # update_trend_plot() # Uncomment to test trend plotter

    root.mainloop()
