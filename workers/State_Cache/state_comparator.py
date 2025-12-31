# workers/State_Cache/state_comparator.py
#
# Version 20251230.230100.1
#
# Author: Gemini
#
# The Judge: Pure logic comparison.

import inspect
from typing import Dict, Any, Optional

from workers.logger.logger import debug_logger
from workers.utils.log_utils import _get_log_args

current_version = "20251230.230100.1"
current_version_hash = (20251230 * 230100 * 1)


def should_update(incoming_topic: str, incoming_payload: Dict, cached_state: Dict) -> bool:
    """
    Compare timestamps (ts). If incoming > cached, return True.
    If ts is missing, compare val.
    If identical, return False.
    """
    debug_logger(message=f"Great Scott! Comparing timelines for topic: {incoming_topic}", **_get_log_args())
    cached_payload = cached_state.get(incoming_topic)
    if not cached_payload:
        debug_logger(message="It's a new event in the timeline! Updating.", **_get_log_args())
        return True  # Not in cache, so it's new

    incoming_ts = incoming_payload.get('ts')
    cached_ts = cached_payload.get('ts')

    if incoming_ts and cached_ts:
        debug_logger(message=f"Comparing timestamps: Incoming '{incoming_ts}' vs Cached '{cached_ts}'", **_get_log_args())
        if incoming_ts > cached_ts:
            debug_logger(message="The future has arrived! Updating.", **_get_log_args())
            return True
        elif incoming_ts == cached_ts:
            debug_logger(message="Timestamps are identical. No change in the timeline.", **_get_log_args())
            return False

    debug_logger(message="No timestamps. Falling back to value comparison.", **_get_log_args())
    incoming_val = incoming_payload.get('val')
    cached_val = cached_payload.get('val')
    if incoming_val != cached_val:
        debug_logger(message=f"Values have changed! Incoming '{incoming_val}' vs Cached '{cached_val}'. Updating.", **_get_log_args())
        return True

    debug_logger(message="No changes detected in the timeline.", **_get_log_args())
    return False
