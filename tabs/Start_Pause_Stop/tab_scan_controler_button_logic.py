# tabs/Start_Pause_Stop/tab_scan_controler_button_logic.py
#
# This file defines the GUI component for the scan control buttons (Start, Pause, Stop).
# It creates the visual elements and links them to the core scan control logic.
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
# Version 20250803.221500.0 (REBUILT: Created the ScanControlTab class to define the GUI, fixing the ImportError.)

current_version = "20250803.221500.0"

import tkinter as tk
from tkinter import ttk
import threading

# Import the LOGIC functions, not the GUI
from .scan_control_logic import start_scan_logic, toggle_pause_resume_logic, stop_scan_logic
from src.console_logic import console_log

class ScanControlTab(ttk.Frame):
    """
    GUI Frame for the Start, Pause/Resume, and Stop scan buttons.
    """
    def __init__(self, parent, app_instance):
        super().__init__(parent, style='TFrame')
        self.app = app_instance
        self.app.scan_control_tab = self # Make this instance accessible from the main app

        # Threading events to control the scan
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
        self.is_blinking = False

        self._create_widgets()
        self._update_button_states()

    def _create_widgets(self):
        """Creates and packs the control buttons."""
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ttk.Button(self, text="Start Scan", command=self._start_scan_action, style="StartScan.TButton")
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.pause_resume_button = ttk.Button(self, text="Pause Scan", command=self._toggle_pause_resume_action, style="PauseScan.TButton")
        self.pause_resume_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.stop_button = ttk.Button(self, text="Stop Scan", command=self._stop_scan_action, style="StopScan.TButton")
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def _start_scan_action(self):
        """Action to start the scan."""
        if start_scan_logic(self.app, console_log, self.stop_event, self.pause_event, self._update_progress):
            self._update_button_states()

    def _toggle_pause_resume_action(self):
        """Action to pause or resume the scan."""
        toggle_pause_resume_logic(self.app, console_log, self.pause_event)
        self._update_button_states()

    def _stop_scan_action(self):
        """Action to stop the scan."""
        stop_scan_logic(self.app, console_log, self.stop_event, self.pause_event)
        # The thread itself will call _update_button_states in its finally block
        
    def _update_progress(self, current, total, a, b, c):
        """Placeholder for progress bar updates."""
        # This can be expanded to update a progress bar widget if you add one
        pass

    def _update_button_states(self):
        """Enables/disables buttons based on the scan state."""
        scan_is_running = self.app.scan_thread and self.app.scan_thread.is_alive()
        is_paused = self.pause_event.is_set()

        if scan_is_running:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.pause_resume_button.config(state='normal')
            if is_paused:
                self.pause_resume_button.config(text="Resume Scan")
                if not self.is_blinking:
                    self.is_blinking = True
                    self._blink_resume_button()
            else:
                self.is_blinking = False
                self.pause_resume_button.config(text="Pause Scan", style="PauseScan.TButton")
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.pause_resume_button.config(state='disabled', text="Pause Scan")
            self.is_blinking = False
            
    def _blink_resume_button(self):
        """Toggles the style of the resume button to create a blinking effect."""
        if not self.is_blinking:
            self.pause_resume_button.config(style="PauseScan.TButton") # Revert to normal when blinking stops
            return
        
        current_style = self.pause_resume_button.cget('style')
        new_style = "ResumeScan.Blink.TButton" if current_style == "PauseScan.TButton" else "PauseScan.TButton"
        self.pause_resume_button.config(style=new_style)
        self.app.after(500, self._blink_resume_button)