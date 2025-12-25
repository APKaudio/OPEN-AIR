# workers/utils/topic_utils.py

def get_topic(base_topic: str, tab_name: str, widget_id: str) -> str:
    """
    Generates a standardized MQTT topic string.
    """
    return f"{base_topic}/{tab_name}/{widget_id}"
