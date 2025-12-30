# workers/builder/Data_graphing/dynamic_gui_create_plot_widget.py

from .dynamic_graph import FluxPlotter
from workers.logger.logger import debug_logger
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args
import orjson

app_constants = Config.get_instance()

class PlotWidgetCreatorMixin:
    def _create_plot_widget(self, parent_frame, label: str, config: dict, path: str, base_mqtt_topic_from_path: str, state_mirror_engine, subscriber_router) -> FluxPlotter:
        """
        Factory method for creating a FluxPlotter (graph) widget.
        """
        if app_constants.global_settings['debug_enabled']:
            debug_logger(
                message=f"📊 Creating FluxPlotter: {label} ({path})",
                **_get_log_args()
            )
        
        try:
            plot_widget = FluxPlotter(parent_frame, 
                                      config=config,
                                      base_mqtt_topic_from_path=base_mqtt_topic_from_path,
                                      widget_id=path,
                                      state_mirror_engine=state_mirror_engine,
                                      subscriber_router=subscriber_router)
        except Exception as e:
            debug_logger(message=f"❌ Failed to initialize FluxPlotter: {e}", **_get_log_args())
            raise e

        return plot_widget
