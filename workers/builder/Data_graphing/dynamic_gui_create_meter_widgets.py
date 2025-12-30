# workers/builder/Data_graphing/dynamic_gui_create_meter_widgets.py

from .Meter_to_display_units import HorizontalMeterWithText, VerticalMeter
from workers.logger.logger import debug_logger
from workers.setup.config_reader import Config
from workers.utils.log_utils import _get_log_args

class MeterWidgetsCreatorMixin:
    def _create_horizontal_meter(self, parent_frame, label: str, config: dict, path: str, base_mqtt_topic_from_path: str, state_mirror_engine, subscriber_router) -> HorizontalMeterWithText:
        """
        Factory method for creating a HorizontalMeterWithText widget.
        """
        meter_widget = HorizontalMeterWithText(parent_frame, 
                                               config=config,
                                               subscriber_router=subscriber_router,
                                               state_mirror_engine=state_mirror_engine,
                                               base_mqtt_topic_from_path=base_mqtt_topic_from_path,
                                               widget_id=path)
        return meter_widget

    def _create_vertical_meter(self, parent_frame, label: str, config: dict, path: str, base_mqtt_topic_from_path: str, state_mirror_engine, subscriber_router) -> VerticalMeter:
        """
        Factory method for creating a VerticalMeter widget.
        """
        meter_widget = VerticalMeter(parent_frame, 
                                           config=config,
                                           subscriber_router=subscriber_router,
                                           state_mirror_engine=state_mirror_engine,
                                           base_mqtt_topic_from_path=base_mqtt_topic_from_path,
                                           widget_id=path)
        return meter_widget
