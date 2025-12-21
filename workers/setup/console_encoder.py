# workers/setup/console_encoder.py

import os
import sys

def configure_console_encoding(watchdog_instance):
    # This block ensures the console can handle UTF-8 characters, preventing encoding errors.
    if os.name == 'nt':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # Fallback for older Python versions that don't have reconfigure
            pass
    watchdog_instance.pet("initialize_app: console reconfigured")
