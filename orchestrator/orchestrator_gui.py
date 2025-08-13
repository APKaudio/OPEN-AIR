# Orchestrator/orchestrator_gui.py
#
# This file defines the GUI component for the run control buttons (Start, Pause, Stop).
# It creates the visual elements and links them to the core run control logic.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-runner/
# Source Code: https://github.com/APKaudio/
# Feature Requests can be emailed to i @ like . audio
#
#
# Version 20250813.153752.1

import tkinter as tk
from tkinter import ttk
import threading

# Import the LOGIC functions from the renamed logic file
from .orchestrator_logic import toggle_pause_resume_logic, stop_run_logic
from display.console_logic import console_log
# NEW: Import the function that creates and starts the run thread
from tabs.Running.utils_run_instrument import initiate_run_thread

class OrchestratorGUI(ttk.Frame):
    """
    GUI Frame for the Start, Pause/Resume, and Stop run buttons.
    The conductor's podium for the run process.
    """
    def __init__(self, parent, app_instance):
        super().__init__(parent, style='TFrame')
        self.app = app_instance
        self.app.orchestrator_gui = self # Make this instance accessible from the main app

        # Threading events to control the run
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
        self.is_blinking = False
        self.is_running = False # A flag to track the running state
        self.is_paused = False # A flag to track the paused state

        self._create_widgets()
        self._update_button_states()

    def _create_widgets(self):
        """Creates and packs the control buttons."""
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ttk.Button(self, text="Start", command=self._start_run_action, style="StartRun.TButton")
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.pause_resume_button = ttk.Button(self, text="Pause", command=self._toggle_pause_resume_action, style="PauseRun.TButton")
        self.pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.stop_button = ttk.Button(self, text="Stop", command=self._stop_run_action, style="StopRun.TButton")
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def _start_run_action(self):
        """Action to start the run."""
        if not self.is_running:
            # Tell the running utility to start the run thread
            if initiate_run_thread(self.app, console_log, self.stop_event, self.pause_event, self._update_progress):
                self.is_running = True
                self.is_paused = False
                self._update_button_states()

    def _toggle_pause_resume_action(self):
        """Action to pause or resume the run."""
        # Toggle the local flag and tell the logic layer to signal the thread.
        if self.is_running:
            self.is_paused = not self.is_paused
            toggle_pause_resume_logic(self.app, console_log, self.pause_event)
            self._update_button_states()

    def _stop_run_action(self):
        """Action to stop the run."""
        # Tell the logic layer to signal the thread to stop.
        stop_run_logic(self.app, console_log, self.stop_event, self.pause_event)
        self.is_running = False
        self.is_paused = False
        self.app.after(0, self._update_button_states)
        
    def _update_progress(self, current, total, a, b, c):
        """Placeholder for progress bar updates."""
        # This can be expanded to update a progress bar widget if you add one
        pass

    def _update_button_states(self):
        """Enables/disables buttons based on the run state."""
        # Use the local `is_running` and `is_paused` flags for button logic.
        if self.is_running:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.pause_resume_button.config(state='normal')
            if self.is_paused:
                self.pause_resume_button.config(text="Resume Run")
                if not self.is_blinking:
                    self.is_blinking = True
                    self._blink_resume_button()
            else:
                self.is_blinking = False
                self.pause_resume_button.config(text="Pause Run", style="PauseRun.TButton")
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.pause_resume_button.config(state='disabled', text="Pause Run")
            self.is_blinking = False
            
    def _blink_resume_button(self):
        """Toggles the style of the resume button to create a blinking effect."""
        if not self.is_blinking:
            self.pause_resume_button.config(style="PauseRun.TButton")
            return
        
        current_style = self.pause_resume_button.cget('style')
        new_style = "ResumeRun.Blink.TButton" if current_style == "PauseRun.TButton" else "PauseRun.TButton"
        self.pause_resume_button.config(style=new_style)
        self.app.after(500, self._blink_resume_button)