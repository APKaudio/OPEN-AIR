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
# Version 20250814.164500.2 (REFACTORED: The GUI now uses a boolean flag to decouple state from logic, fixing the KeyError and removing direct thread control.)

current_version = "20250814.164500.2"

import tkinter as tk
from tkinter import ttk
import threading

# Import the LOGIC functions, not the GUI
from .scan_control_logic import start_scan_logic, toggle_pause_resume_logic, stop_scan_logic
from display.console_logic import console_log

class ScanControlTab(ttk.Frame):
    """
    GUI Frame for the Start, Pause/Resume, and Stop scan buttons.
    """
    def __init__(self, parent, app_instance):
        super().__init__(parent, style='TFrame')
        self.app = app_instance
        self.app.scan_control_tab = self # Make this instance accessible from the main app

        # Threading events to control the scan
        # REMOVED: These thread events are now managed by the logic layer.
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        
        self.is_blinking = False
        self.is_scanning = False # A flag to track the scanning state
        self.is_paused = False # A flag to track the paused state

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
        if not self.is_scanning:
            # Tell the logic layer to start the scan and get the result.
            if start_scan_logic(self.app, console_log, self.stop_event, self.pause_event, self._update_progress):
                self.is_scanning = True
                self.is_paused = False
                self._update_button_states()

    def _toggle_pause_resume_action(self):
        """Action to pause or resume the scan."""
        # Toggle the local flag and tell the logic layer what to do.
        if self.is_scanning:
            self.is_paused = not self.is_paused
            toggle_pause_resume_logic(self.app, console_log, self.pause_event)
            self._update_button_states()

    def _stop_scan_action(self):
        """Action to stop the scan."""
        stop_scan_logic(self.app, console_log, self.stop_event, self.pause_event)
        self.is_scanning = False
        self.is_paused = False
        self.app.after(0, self._update_button_states)
        
    def _update_progress(self, current, total, a, b, c):
        """Placeholder for progress bar updates."""
        # This can be expanded to update a progress bar widget if you add one
        pass

    def _update_button_states(self):
        """Enables/disables buttons based on the scan state."""
        # Use the local `is_scanning` and `is_paused` flags for button logic.
        if self.is_scanning:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.pause_resume_button.config(state='normal')
            if self.is_paused:
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
            self.pause_resume_button.config(style="PauseScan.TButton")
            return
        
        current_style = self.pause_resume_button.cget('style')
        new_style = "ResumeScan.Blink.TButton" if current_style == "PauseScan.TButton" else "PauseScan.TButton"
        self.pause_resume_button.config(style=new_style)
        self.app.after(500, self._blink_resume_button)
