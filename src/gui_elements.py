# src/gui_elements.py
import tkinter as tk
import sys
from tkinter import scrolledtext, TclError
import inspect # Added for debug_print

# Assuming debug_print is available globally or passed in some way.
# For this file, we'll make a local version or assume it's imported.
# In a real application, you'd ensure debug_print is properly imported or passed.
# For now, let's define a dummy if it's not explicitly imported to prevent errors.
try:
    from utils.utils_instrument_control import debug_print
except ImportError:
    # Define a dummy debug_print if it cannot be imported, for standalone testing
    def debug_print(message, file="", function="", console_print_func=None):
        if console_print_func:
            console_print_func(f"[DEBUG_DUMMY] {file}:{function}: {message}")
        else:
            print(f"[DEBUG_DUMMY] {file}:{function}: {message}")


class TextRedirector(object):
    """
    A class to redirect standard output (stdout) and standard error (stderr)
    to a Tkinter scrolled text widget. This allows all print statements and
    error messages from the application's backend to be displayed directly
    within the GUI's console area, providing real-time feedback to the user.
    """
    def __init__(self, widget, tag="stdout"):
        """
        Initializes the TextRedirector.

        Inputs:
            widget (tk.scrolledtext.ScrolledText): The Tkinter scrolled text widget
                                                  where output will be displayed.
            tag (str, optional): A tag for text formatting within the widget. Defaults to "stdout".
        Process:
            1. Stores the provided `widget` and `tag`.
            2. Initializes `last_char_was_cr` to False, used for handling carriage returns for line overwriting.
            3. Configures a tag to control line spacing.
        Outputs: None
        """
        self.widget = widget
        self.tag = tag
        self.last_char_was_cr = False

        # Configure a tag to control line spacing
        # spacing1: extra space above a line
        # spacing3: extra space below a line
        # We set them to 0 to try and minimize perceived double-spacing.
        # This explicitly tells the Text widget to not add extra space between lines.
        self.widget.tag_configure(self.tag, spacing1=0, spacing3=0)


    def write(self, str_val):
        """
        Writes the given string value to the Tkinter scrolled text widget.
        It handles carriage returns for overwriting and inserts the string
        as-is, relying on the source (e.g., print function) to provide newlines.
        Crucially, it now enables the widget before writing and disables it after.

        Inputs:
            str_val (str): The string to write to the console.
        Process:
            1. Temporarily enables the widget.
            2. If the string contains a carriage return ('\r'), it's treated as an overwrite.
            3. Otherwise, the string is inserted directly.
            4. Scrolls to the end of the text widget to show the latest output.
            5. Updates Tkinter's idle tasks to ensure immediate display.
            6. Disables the widget again.
        Outputs: None
        """
        try:
            self.widget.config(state=tk.NORMAL) # Enable the widget for writing
            if '\r' in str_val:
                # Handle carriage return for overwriting the current line
                # This is typically for progress updates on the same line
                self.widget.delete("end - 1 lines", "end")
                self.widget.insert(tk.END, str_val.replace('\r', ''), self.tag)
                self.last_char_was_cr = True
            else:
                # Insert the string as-is. Python's print() adds a newline by default.
                # We rely on that or explicit newlines in the string.
                self.widget.insert(tk.END, str_val, self.tag)
                self.last_char_was_cr = False # Reset if not a carriage return line

            self.widget.see(tk.END) # Always scroll to the end
            self.widget.update_idletasks() # Ensure the display updates immediately
        except TclError as e:
            # This can happen if the widget is destroyed while still being referenced
            # during application shutdown, or if there's a deeper Tkinter issue.
            # Fallback to standard print in such cases.
            print(f"Error writing to GUI console: {e} - Message: {str_val}")
        finally:
            # Always attempt to disable the widget, even if an error occurred
            try:
                self.widget.config(state=tk.DISABLED)
            except TclError:
                pass # Widget might already be destroyed


    def flush(self):
        """
        Required for file-like objects. Ensures that output is processed.
        """
        pass # Tkinter widget updates are handled by .see(tk.END) and .update_idletasks()

def print_art():
    """
    Prints an ASCII art logo to the console output. This function is called
    during application startup to provide a visual brand element.

    Inputs: None
    Process:
        1. Uses a series of `print()` statements to output the multi-line ASCII art.
        2. Each `print()` call will now add its own newline by default,
           which `TextRedirector` will then insert directly.
    Outputs: None (prints to console)
    """


    ###https://patorjk.com/software/taag/#p=display&h=3&v=2&f=BlurVision%20ASCII&t=OPEN%20AIR%0A
    # Reverting to default print() behavior, letting it add newlines.
    # TextRedirector will now insert these newlines directly.
    print("") # First blank line
    print("") # Second blank line
    print("") # Third blank line
    print(" ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░        ░▒▓██████▓▒░░▒▓█▓▒░▒▓███████▓▒░  ")
    print("░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░▒▓█▓▒░▒▓███████▓▒░  ")
    print("░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ")
    print("░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ")
    print(" ░▒▓██████▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ")
                                                                                             

    print("") # First blank line
    print("") # Second blank line
    print("") # Third blank line

    print("                                               $              $$$$$                     $$ $$$$")
    print("                                               $$$            $$   $$$$$$               $$  $$ ")
    print("                                               $$$$           $$         $$$$$          $$ $$  ")
    print("                                  $$           $$ $$          $$             $$$$$      $$$$   ")
    print("                       $$$$$$$$$$$$            $$  $$$        $                  $$$    $$$$   ")
    print("             $$$$$$$$$        $$$              $$   $$$      $$                    $$   $$$    ")
    print("   $$$$$$$$$               $$$                 $$     $$     $$                $$$$     $$     ")
    print("                         $$$                   $$$$$$$$$$$   $$          $$$$$$         $$     ")
    print("                       $$$                     $$       $$$  $  $$$$$$$$                $      ")
    print("                     $$$                       $$         $$$$$                                ")
    print("                   $$$                         $$           $$                        $ $$     ")
    print("                 $$$                $$$$$$$                 $$                        $$$      ")
    print("              $$$$            $$$$$$                        $$                  $$$$$$$$$$     ")
    print("            $$$        $$$$$$$                                   $$$$$$$$$$$$$$                ")
    print("          $$$   $$$$$$$                             $$$$$$$$$$$                                ")
    print("        $$$$$$$$                  $$$$$$$$             $$$$                                    ")
    print("      $$$              $$$$$$$$$$  $$$$              $$$$$$$$                                  ")
    print("           $$$$$$$$$$$          $$$         $$$$$$$$                                           ")
    print(" $$$$$$$$$$                  $$$    $$$$$$$$                                                   ")
    print("                         $$$$$$$$$$                                                            ")
    print("                      $$$$$                        ")
    print("") # Blank line
    print("") # Blank line
    print("") # Blank line
    print("A Colaboration betweeen Ike Zimbel and Anthony P. Kuzub")
    print("") # Blank line
    print("https://zimbelaudio.com/ike-zimbel/    ")
    print("https://www.like.audio/")
    print("") # Blank line

    print("") # Blank line



