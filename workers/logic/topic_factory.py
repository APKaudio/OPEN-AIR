# workers/logic/topic_factory.py
#
# Purpose: Generates standardized topic strings so we don't have hardcoded strings everywhere.
# Key Function: generate_base_topic(module_name: str) -> str (e.g., OPEN-AIR/yak/bandwidth)
# Key Function: generate_widget_topic(base_topic: str, widget_id: str) -> str

def generate_base_topic(module_name: str) -> str:
    """
    Generates a standardized base topic string.
    e.g., OPEN-AIR/yak/bandwidth
    """
    # module_name could be something like "yak/bandwidth", so we just prepend OPEN-AIR
    return f"OPEN-AIR/{module_name}"

def generate_widget_topic(base_topic: str, widget_id: str) -> str:
    """
    Generates a standardized widget topic string from a base topic and a widget ID.
    """
    return f"{base_topic}/{widget_id}"
