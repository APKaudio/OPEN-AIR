# Orchestrator/orchestrator_gui.py
#
# This file defines the GUI component for the process control buttons (Start, Pause, Stop).
# It creates the visual elements and links them to the core orchestrator logic.
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
# Version 20250813.165000.1

import tkinter as tk
from tkinter import ttk
import threading
import os
import inspect

# Import the LOGIC functions from the logic file
from .orchestrator_logic import toggle_pause_resume, stop_logic
from display.console_logic import console_log
from display.debug_logic import debug_log
# The orchestrator is now a simple state machine and does not import the scanning threads.
# from tabs.Scanning.utils_scan_instrument import initiate_scan_thread

# --- Version Information ---
current_version = "20250813.165000.1"
current_version_hash = (20250813 * 165000 * 1)

class OrchestratorGUI(ttk.Frame):
    """
    GUI Frame for the Start, Pause/Resume, and Stop control buttons.
    The conductor's podium for the running process.
    """
    def __init__(self, parent, app_instance):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Initializing Orchestrator GUI.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        super().__init__(parent, style='TFrame')
        self.app = app_instance
        self.app.orchestrator_gui = self

        # Threading events to control the process
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
        self.is_blinking = False
        self.is_running = False
        self.is_paused = False

        self._create_widgets()
        self._update_button_states()

    def _create_widgets(self):
        """Creates and packs the control buttons."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Creating control buttons.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ttk.Button(self, text="Start", command=self._start_action, style="StartScan.TButton")
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.pause_resume_button = ttk.Button(self, text="Pause", command=self._toggle_pause_resume_action, style="PauseScan.TButton")
        self.pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.stop_button = ttk.Button(self, text="Stop", command=self._stop_action, style="StopScan.TButton")
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        debug_log(f"Exiting {current_function}. Buttons created. 👍",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)

    def _start_action(self):
        """
        Action to start the process.
        This no longer initiates the scan thread, it only sets the running state flag.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Start button clicked.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self._update_button_states()
            console_log("▶️ Start flag set. Waiting for scanner to pick up the signal...")
            debug_log(f"Orchestrator state set to running. Waiting for a listener. ✅",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function)

    def _toggle_pause_resume_action(self):
        """Action to pause or resume the process."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Pause/Resume button clicked. Toggling pause state.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        if self.is_running:
            self.is_paused = not self.is_paused
            toggle_pause_resume(self.app, console_log, self.pause_event)
            self._update_button_states()
        else:
            debug_log(f"Pause/Resume clicked, but no process is running. Fucking useless!",
                      file=f"{os.path.basename(__file__)} - {current_version}",
                      version=current_version,
                      function=current_function)

    def _stop_action(self):
        """Action to stop the process."""
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering {current_function}. Stop button clicked. Signaling process to stop.",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
        stop_logic(self.app, console_log, self.stop_event, self.pause_event)
        self.is_running = False
        self.is_paused = False
        self.app.after(0, self._update_button_states)
        
        debug_log(f"Process stop signal sent. Final button state update pending. ✅",
                  file=f"{os.path.basename(__file__)} - {current_version}",
                  version=current_version,
                  function=current_function)
        
    def _update_progress(self, current, total, a, b, c):
        """Placeholder for progress bar updates."""
        pass

    def _update_button_states(self):
        """Enables/disables buttons based on the running state."""
        # Use the local `is_running` and `is_paused` flags for button logic.
        if self.is_running:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.pause_resume_button.config(state='normal')
            if self.is_paused:
                self.pause_resume_button.config(text="Resume")
                if not self.is_blinking:
                    self.is_blinking = True
                    self._blink_resume_button()
            else:
                self.is_blinking = False
                self.pause_resume_button.config(text="Pause", style="PauseScan.TButton")
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.pause_resume_button.config(state='disabled', text="Pause")
            self.is_blinking = False
            
    def _blink_resume_button(self):
        """Toggles the style of the resume button to create a blinking effect."""
        if not self.is_blinking:
            self.pause_resume_button.config(style="PauseScan.TButton")
            return
        
        current_style = self.pause_resume_button.cget('style')
        new_style = "ResumeScan.Blink.TButton" if current_style == "PauseScan.TButton" else "PauseScan.TButton"
        self.pause_resume_button.config(style=new_style)
        self.app.after(500, self._blink_resume_button)