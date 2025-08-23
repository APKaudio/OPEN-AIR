# tabs/Experiments/tab_experiments_credits.py
#
# This file defines the CreditsTab, a Tkinter Frame that provides
# a button to open the project's GitHub page for credits and contribution details.
# It also displays the project's logo.
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
# Version W.X.Y
#

current_version = "Version 20250820.102600.4"
current_version_hash = 20250820 * 102600 * 4

import tkinter as tk
from tkinter import ttk
import inspect
import os
import webbrowser # For opening the GitHub link
from display.debug_logic import debug_log
from display.console_logic import console_log
from src.program_style import COLOR_PALETTE
from PIL import Image, ImageTk # For handling images

class CreditsTab(tk.Frame):
    """
    A Tkinter Frame for displaying credits, the project logo, and a link to the GitHub repository.
    """
    def __init__(self, parent_notebook, app_instance, console_print_func, *args, **kwargs):
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering CreditsTab.__init__.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        try:
            super().__init__(parent_notebook, **kwargs)
            self.app_instance = app_instance
            self.console_print_func = console_print_func
            self.parent_notebook = parent_notebook

            self.configure(background=COLOR_PALETTE["background"])
            
            # Load and display the logo image
            try:
                # Construct the path to the image
                script_dir = os.path.dirname(__file__)
                logo_path = os.path.join(script_dir, '..', '..', 'display', 'logo.png')
                
                # Check if the file exists before trying to open it
                if os.path.exists(logo_path):
                    original_image = Image.open(logo_path)
                    
                    self.logo_image = ImageTk.PhotoImage(original_image)
                    logo_label = tk.Label(self, image=self.logo_image, background=COLOR_PALETTE["background"])
                    logo_label.pack(pady=(20, 10))
                else:
                    self.console_print_func(f"❌ Logo image not found at: {logo_path}")
                    debug_log(f"Arrr, the logo be missing! The path be: {logo_path}",
                                file=f"{os.path.basename(__file__)}",
                                version=current_version,
                                function=current_function)
            except Exception as e:
                self.console_print_func(f"❌ Error loading logo image: {e}")
                debug_log(f"A curse on these image files! Error loading logo: {e}",
                            file=f"{os.path.basename(__file__)}",
                            version=current_version,
                            function=current_function)

            # Label for title
            ttk.Label(
                self,
                text="Project Credits",
                font=('Helvetica', 14, 'bold'),
                background=COLOR_PALETTE["background"],
                foreground=COLOR_PALETTE["foreground"]
            ).pack(pady=(10, 5))

            # Button to open GitHub page
            open_github_button = tk.Button(
                self,
                text="Open on GitHub",
                font=('Helvetica', 13, 'bold'),
                bg=COLOR_PALETTE['blue_btn'],
                fg=COLOR_PALETTE['white'],
                activebackground=COLOR_PALETTE['blue_btn_active'],
                activeforeground=COLOR_PALETTE['white'],
                compound="left",
                command=self._open_github_link
            )
            open_github_button.pack(pady=10, padx=10)

            console_print_func("✅ Credits Tab initialized successfully.")
            debug_log(f"All components for CreditsTab are up and running! 🚀",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)
        except Exception as e:
            console_print_func(f"❌ Error in CreditsTab initialization: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)
            raise

    def _open_github_link(self):
        # [A brief, one-sentence description of the function's purpose.]
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _open_github_link with arguments: N/A",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)

        try:
            github_url = "https://github.com/APKaudio/Spectrum-Automation---ZAP"
            webbrowser.open_new_tab(url=github_url)
            self.console_print_func("✅ Opening GitHub page in browser.")
            debug_log(f"Opening GitHub link: {github_url}. Anchors aweigh! ⛵",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)

            console_log("✅ Celebration of success!")
        except Exception as e:
            self.console_print_func(f"❌ Error opening GitHub link: {e}")
            debug_log(f"Arrr, the code be capsized! The error be: {e}",
                      file=f"{os.path.basename(__file__)}",
                      version=current_version,
                      function=current_function)


    def _on_tab_selected(self, event):
        """
        Handles the event when this child tab is selected.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Entering _on_tab_selected.",
                  file=f"{os.path.basename(__file__)}",
                  version=current_version,
                  function=current_function)
        
        # No specific actions needed for this tab on selection.
        console_log("✅ Celebration of success!")