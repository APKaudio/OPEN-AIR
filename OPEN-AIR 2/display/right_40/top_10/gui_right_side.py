# app/main_prototype_tkinter.py
#
# A standalone Tkinter GUI prototype demonstrating button-driven logging. This file
# serves as a test bed for the core application framework and logging protocol.
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
# Version 20250822.190800.1

# 📚 Importing our necessary Python modules to build the application.
import os
import inspect
import datetime
import tkinter as tk
# We'll use the ttk version of Frame for better styling consistency.
from tkinter import ttk

# We assume this is imported from a central logging utility, as per the protocol.
from configuration.logging import debug_log, console_log

# --- Global Scope Variables ---
# ⏰ As requested, the version is now hardcoded to the time this file was generated.
# The following variables are static and will not change at runtime.
# W: This represents the date (YYYYMMDD) of file creation.
CURRENT_DATE = 20250822
# X: This represents the time (HHMMSS) of file creation.
CURRENT_TIME = 190800
# A numeric hash of the time, useful for unique IDs.
CURRENT_TIME_HASH = 190800
# Y: Our project's current revision number for this file.
REVISION_NUMBER = 1
# Assembling the full version string as per the protocol (W.X.Y).
current_version = "20250822.190800.1"
# Creating a unique integer hash for the current version for internal tracking.
current_version_hash = (CURRENT_DATE * CURRENT_TIME_HASH * REVISION_NUMBER)
# Getting the name of the current file to use in our logs, ensuring it's always accurate.
current_file = f"{os.path.basename(__file__)}"


class Start_stop(ttk.Frame):
    """
    A class that simulates a GUI frame with two buttons.
    
    It adheres to the "GUI" layer principles of your protocol, handling display and
    user interaction, but delegating any core logic to other components (simulated here
    by the log and debug functions).
    """
    def __init__(self, parent):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 We log the entry into the function with the "mad scientist" personality.
        debug_log(
            message="🖥️🟢 Initializing the GUI frame. The framework is taking shape!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            # We call the parent class's constructor, passing in the parent widget.
            super().__init__(parent)
            # We use pack() to arrange the frame within its parent widget.
            self.pack(padx=20, pady=20)
            
            # Create a label for the frame to give it a clear purpose and title.
            frame_label = tk.Label(self, text="Application Frame", font=("Arial", 16))
            frame_label.pack(pady=10)
            
            # Button 1: Log
            # 💡 We pass arguments by name, as required by the protocol.
            self.log_button = tk.Button(
                master=self,
                text="Log",
                command=self.log_button_press
            )
            # We pack the button on the left side of the frame.
            self.log_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Button 2: Debug
            # 💡 We pass arguments by name, as required by the protocol.
            self.debug_button = tk.Button(
                master=self,
                text="Debug",
                command=self.debug_button_press
            )
            # We pack the button on the left side of the frame, next to the first button.
            self.debug_button.pack(side=tk.LEFT, padx=10, pady=10)

            # ✅ A celebratory log message for a successful initialization!
            console_log("✅ Celebration of success!")

        except Exception as e:
            # ❌ If an error occurs, we catch it here to prevent the application from crashing.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # We log a detailed error message with our "mad scientist" personality.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def log_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        # This function is triggered when the "Log" button is clicked.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 Entry log with the appropriate emoji prefix.
        debug_log(
            message="🖥️🟢 Entering 'log_button_press' from the GUI layer.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            console_log("Left button was clicked. Initiating a standard log entry.")
            
            # ✅ Success!
            console_log("✅ Log entry recorded successfully!")

        except Exception as e:
            # ❌ Error handling for this specific function.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # Detailed debug log with the error message.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def debug_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        # This function is triggered when the "Debug" button is clicked.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # 🟢 Entry log with the appropriate emoji prefix.
        debug_log(
            message="🖥️🟢 Entering 'debug_button_press' from the GUI layer.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            # 🔍🔵 We add a specific debug log to show a deeper inspection is taking place.
            debug_log(
                message="🔍🔵 The right button was clicked! Time for a deeper inspection!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            
            # ✅ Success!
            console_log("✅ Debug entry recorded successfully!")

        except Exception as e:
            # ❌ Error handling for this specific function.
            console_log(f"❌ Error in {current_function_name}: {e}")
            # Detailed debug log with the error message.
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

# 🏃 This is the standard entry point for a Python script.
# The code inside this block only runs when the script is executed directly.
if __name__ == "__main__":
    # We create the root window of the application.
    root = tk.Tk()
    root.title("Logging Prototype")
    
    # We create an instance of our Start_stop class and pass the root window as the parent.
    # We pass the argument by name as required.
    app_frame = Start_stop(parent=root)
    
    # This call starts the Tkinter event loop, which listens for user actions and keeps the window open.
    root.mainloop()
