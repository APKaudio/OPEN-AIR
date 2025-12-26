# workers/utils/topic_utils.py

def get_topic(*args: str) -> str:
    """
    Generates a standardized MQTT topic string by joining non-empty arguments with '/'.
    """
    return "/".join(arg for arg in args if arg)
