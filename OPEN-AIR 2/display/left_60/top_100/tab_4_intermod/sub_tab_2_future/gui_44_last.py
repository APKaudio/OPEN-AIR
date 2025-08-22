# app/main_prototype_tkinter.py
#
# A standalone Tkinter GUI prototype demonstrating button-driven logging.
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
# Version 20250821.234400.1

import os
import inspect
import datetime
import tkinter as tk

# --- Global Scope Variables ---
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
CURRENT_TIME = datetime.datetime.now().strftime("%H%M%S")
# Note: For hashing, any leading zero in the hour is dropped (e.g., 083015 becomes 83015).
CURRENT_TIME_HASH = int(datetime.datetime.now().strftime("%H%M%S"))
REVISION_NUMBER = 1
current_version = f"{CURRENT_DATE}.{CURRENT_TIME}.{REVISION_NUMBER}"
current_version_hash = (int(CURRENT_DATE) * CURRENT_TIME_HASH * REVISION_NUMBER)
current_file = f"{os.path.basename(__file__)}"

from configuration.logging import debug_log, console_log


class GUIFrame(tk.Frame):
    """
    A class that simulates a GUI frame with two buttons.
    It adheres to the "GUI" layer principles of your protocol.
    """
    def __init__(self, parent):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        debug_log(
            message="🖥️🟢 Initializing the GUI frame. The framework is taking shape!",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )
        
        try:
            # --- Function logic goes here ---
            super().__init__(parent)
            self.pack(padx=20, pady=20)
            
            # Create a label for the frame
            frame_label = tk.Label(self, text="44 Application Frame", font=("Arial", 16))
            frame_label.pack(pady=10)
            
            # Button 1: Log
            self.log_button = tk.Button(
                self, 
                text="Log", 
                command=self.log_button_press
            )
            self.log_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Button 2: Debug
            self.debug_button = tk.Button(
                self, 
                text="Debug", 
                command=self.debug_button_press
            )
            self.debug_button.pack(side=tk.LEFT, padx=10, pady=10)

            console_log("✅ Celebration of success!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def log_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Entry log
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
            console_log("✅ Log entry recorded successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

    def debug_button_press(self):
        # A brief, one-sentence description of the function's purpose.
        current_function_name = inspect.currentframe().f_code.co_name
        
        # Entry log
        debug_log(
            message="🖥️🟢 Entering 'debug_button_press' from the GUI layer.",
            file=current_file,
            version=current_version,
            function=f"{self.__class__.__name__}.{current_function_name}",
            console_print_func=console_log
        )

        try:
            # --- Function logic goes here ---
            debug_log(
                message="🔍🔵 The right button was clicked! Time for a deeper inspection!",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )
            console_log("✅ Debug entry recorded successfully!")

        except Exception as e:
            console_log(f"❌ Error in {current_function_name}: {e}")
            debug_log(
                message=f"❌🔴 Arrr, the code be capsized! The error be: {e}",
                file=current_file,
                version=current_version,
                function=f"{self.__class__.__name__}.{current_function_name}",
                console_print_func=console_log
            )

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Logging Prototype")
    
    app_frame = GUIFrame(parent=root)
    
    root.mainloop()
