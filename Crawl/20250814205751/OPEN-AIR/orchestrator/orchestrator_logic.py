# FolderName/orchestrator_logic.py
#
# This file contains the core logic for the application's orchestrator,
# managing the main operational state (running, paused, stopped).
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250814.121000.2

current_version = "20250814.121000.2"
current_version_hash = (20250814 * 121000 * 2)

import inspect
import os
from display.console_logic import console_log
from display.debug_logic import debug_log

class OrchestratorLogic:
    def __init__(self, app_instance, gui):
        self.app_instance = app_instance
        self.gui = gui
        self.is_running = False
        self.is_paused = False

    def get_status(self):
        # A brief, one-sentence description of the function's purpose.
        # Returns the current status of the orchestrator.
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused
        }

    def start_orchestrator(self):
        # Starts the main application orchestrator.
        if self.is_running:
            console_log("✅ Orchestrator is already running.")
            return

        self.is_running = True
        self.is_paused = False
        self.gui.update_button_states()
        console_log("✅ Orchestrator started. The symphony begins! 🎶")
        
        if self.app_instance.orchestrator_tasks_tab:
            self.app_instance.orchestrator_tasks_tab.update_status_display(self.is_running, self.is_paused)
            self.log_task_event(source_file=__file__, event="Orchestrator Started")

    def stop_orchestrator(self):
        # Stops the main application orchestrator.
        if not self.is_running:
            console_log("✅ Orchestrator is already stopped.")
            return

        self.is_running = False
        self.gui.update_button_states()
        console_log("✅ Orchestrator stopped. The music fades... 🤫")
        
        if self.app_instance.orchestrator_tasks_tab:
            self.app_instance.orchestrator_tasks_tab.update_status_display(self.is_running, self.is_paused)
            self.log_task_event(source_file=__file__, event="Orchestrator Stopped")

    def toggle_pause(self):
        # Toggles the paused state of the orchestrator.
        if not self.is_running:
            console_log("ℹ️ Cannot pause, orchestrator is not running.")
            return

        self.is_paused = not self.is_paused
        self.gui.update_button_states()
        state = "paused" if self.is_paused else "resumed"
        console_log(f"✅ Orchestrator {state}. A brief intermission. ⏸️")

        if self.app_instance.orchestrator_tasks_tab:
            self.app_instance.orchestrator_tasks_tab.update_status_display(self.is_running, self.is_paused)
            self.log_task_event(source_file=__file__, event=f"Orchestrator {state.capitalize()}")

    def log_check_in(self, source_file):
        # Allows other modules to log that they have checked the orchestrator status.
        self.log_task_event(source_file=source_file, event="Checked In")

    def log_task_event(self, source_file, event):
        # [A brief, one-sentence description of the function's purpose.]
        # Logs a specific event from a source module to the orchestrator tasks tab.
        try:
            if self.app_instance.orchestrator_tasks_tab:
                self.app_instance.orchestrator_tasks_tab.log_event(source=source_file, event=event)
        except Exception as e:
            # Avoid a logging loop by printing directly
            print(f"ERROR: Could not log task event from {source_file}: {e}")