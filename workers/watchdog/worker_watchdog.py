# workers/utils/worker_watchdog.py
#
# A watchdog utility to monitor the main thread for blocking calls during startup.
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
#
# Version 20251215.120000.2

import threading
import time
from display.logger import console_log

class Watchdog:
    def __init__(self, timeout=1):
        self.timeout = timeout
        self.last_pet_location = "init"
        self.last_pet_time = time.time()
        self.stopped = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.stopped = True

    def pet(self, location):
        self.last_pet_location = location
        self.last_pet_time = time.time()

    def _run(self):
        while not self.stopped:
            time.sleep(self.timeout)
            if time.time() - self.last_pet_time > self.timeout:
                console_log(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                console_log(f"!!! WATCHDOG ALERT: Main thread appears to be frozen!  !!!")
                console_log(f"!!! Last seen at: {self.last_pet_location}                  !!!")
                console_log(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                # Since the main thread is frozen, we might as well stop the watchdog.
                self.stopped = True
