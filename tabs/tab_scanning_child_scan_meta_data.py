# src/tab_scan_meta_data.py
#
# This file contains the Tkinter Frame for controlling spectrum scans,
# including starting, pausing, and stopping scans, as well as managing
# post-scan processing and plotting. It orchestrates the threading
# for the scan operation to keep the GUI responsive.
#
# Author: Anthony Peter Kuzub
# Blog: www.Like.audio (Contributor to this project)
#
# Professional services for customizing and tailoring this software to your specific
# application can be negotiated. There is no change to use, modify, or fork this software.
#
# Build Log: https://like.audio/category/software/spectrum-scanner/
# Source Code: https://github.com/APKaudio/
#
#
# Version 1.4 (Made antenna/amplifier description/use fields editable; added explicit population on tab select)

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os # For os.path.exists and os.makedirs
import subprocess # For opening folders

from utils.utils_instrument_control import debug_print
from src.config_manager import save_config

# Import new modules for functionality
from process_math.google_maps_lookup import get_location_from_google_maps
from ref.Antenna_type import antenna_types
from ref.antenna_amplifier_type import antenna_amplifier_types


class ScanMetaDataTab(ttk.Frame):
    """
    A Tkinter Frame that contains the Scan Meta Data settings.
    This includes operator, venue, equipment, and general notes.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, **kwargs):
        # This function descriotion tells me what this function does
        # Initializes the ScanMetaDataTab, setting up the UI frame,
        # linking to the main application instance, and preparing
        # Tkinter variables for meta data fields.
        #
        # Inputs to this function
        #   master (tk.Widget): The parent widget, typically a ttk.Notebook.
        #   app_instance (object): Reference to the main application instance
        #                          to access shared variables and methods.
        #   console_print_func (function): A function to print messages to the
        #                                  application's console output.
        #   **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.
        #
        # Process of this function
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to app_instance and console_print_func.
        #   3. Initializes new Tkinter StringVars for postal code, address, province,
        #      selected antenna type, antenna description, antenna use, antenna mount,
        #      and selected amplifier type, amplifier description, and amplifier use.
        #   4. Calls _create_widgets to build the UI.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        #
        # (2025-07-30) Change: Initialized new StringVars for regrouped fields, including new amplifier description/use.
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else print

        # Initialize new Tkinter variables for location and equipment
        # These variables are initialized in main_app.py and linked here via app_instance
        # self.app_instance.venue_postal_code_var = tk.StringVar(value="") # Initialized in main_app.py
        # self.app_instance.address_field_var = tk.StringVar(value="")     # Initialized in main_app.py
        # self.app_instance.province_var = tk.StringVar(value="")          # Initialized in main_app.py

        # self.app_instance.selected_antenna_type_var = tk.StringVar(value="") # Initialized in main_app.py
        # self.app_instance.antenna_description_var = tk.StringVar(value="")   # Initialized in main_app.py
        # self.app_instance.antenna_use_var = tk.StringVar(value="")           # Initialized in main_app.py
        # self.app_instance.antenna_mount_var = tk.StringVar(value="")         # Initialized in main_app.py

        # self.app_instance.selected_amplifier_type_var = tk.StringVar(value="") # Initialized in main_app.py
        # self.app_instance.amplifier_description_var = tk.StringVar(value="")   # Initialized in main_app.py
        # self.app_instance.amplifier_use_var = tk.StringVar(value="")           # Initialized in main_app.py


        self._create_widgets()

    def _create_widgets(self):
        # This function descriotion tells me what this function does
        # Creates and arranges the widgets for the Scan Meta Data tab,
        # grouping them into Personnel, Location, Equipment Used, and Notes sections.
        # It includes interactive elements like a postal code lookup button and
        # dropdowns for antenna and amplifier types with dynamic description updates.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Creates main LabelFrames for Personnel, Location, Equipment Used, and Notes.
        #   3. Populates each frame with appropriate Labels, Entry widgets,
        #      Buttons, and Comboboxes, linking them to app_instance variables.
        #   4. Configures grid layouts for each section to ensure proper alignment and resizing.
        #   5. Binds events for the postal code lookup button and Combobox selections
        #      to their respective handler methods.
        #   6. Initializes the notes ScrolledText widget and binds its key release event.
        #
        # Outputs of this function
        #   None. Modifies the Tkinter frame by adding and arranging widgets.
        #
        # (2025-07-30) Change: Made location fields editable; added amplifier description/use fields.
        # (2025-07-30) Change: Made antenna/amplifier description/use fields editable.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Creating ScanMetaDataTab widgets...", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # Main grid configuration for the tab
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Personnel
        self.grid_rowconfigure(1, weight=0) # Location
        self.grid_rowconfigure(2, weight=0) # Equipment
        self.grid_rowconfigure(3, weight=1) # Notes (allow to expand)


        # --- Personnel Box ---
        personnel_frame = ttk.LabelFrame(self, text="Personnel", style='Dark.TLabelframe')
        personnel_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        personnel_frame.grid_columnconfigure(1, weight=1) # Allow entry widgets to expand

        ttk.Label(personnel_frame, text="Operator Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(personnel_frame, textvariable=self.app_instance.operator_name_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(personnel_frame, text="Operator Contact:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(personnel_frame, textvariable=self.app_instance.operator_contact_var).grid(row=1, column=1, padx=5, pady=2, sticky="ew")


        # --- Location Box ---
        location_frame = ttk.LabelFrame(self, text="Location", style='Dark.TLabelframe')
        location_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        location_frame.grid_columnconfigure(1, weight=1) # Allow entry widgets to expand

        ttk.Label(location_frame, text="Venue Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(location_frame, textvariable=self.app_instance.venue_name_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="Venue Postal Code:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        postal_code_entry = ttk.Entry(location_frame, textvariable=self.app_instance.venue_postal_code_var)
        postal_code_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # Button for calling the postal code lookup function
        ttk.Button(location_frame, text="Lookup Location", command=self._lookup_postal_code, style='Blue.TButton').grid(row=1, column=2, padx=5, pady=2, sticky="e")

        ttk.Label(location_frame, text="Address Field:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        ttk.Entry(location_frame, textvariable=self.app_instance.address_field_var).grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="City:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        ttk.Entry(location_frame, textvariable=self.app_instance.city_var).grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="Province:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        ttk.Entry(location_frame, textvariable=self.app_instance.province_var).grid(row=4, column=1, columnspan=2, padx=5, pady=2, sticky="ew")


        # --- Equipment Used Box ---
        equipment_frame = ttk.LabelFrame(self, text="Equipment Used", style='Dark.TLabelframe')
        equipment_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        equipment_frame.grid_columnconfigure(1, weight=1) # Allow entry/combobox to expand

        ttk.Label(equipment_frame, text="Scanner Type:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(equipment_frame, textvariable=self.app_instance.scanner_type_var).grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Type:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.antenna_type_combobox = ttk.Combobox(
            equipment_frame,
            textvariable=self.app_instance.selected_antenna_type_var,
            values=[ant["Type"] for ant in antenna_types],
            state="readonly" # This remains readonly as it's a selection from a predefined list
        )
        self.antenna_type_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.antenna_type_combobox.bind("<<ComboboxSelected>>", self._on_antenna_type_selected)

        ttk.Label(equipment_frame, text="Antenna Description:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.antenna_description_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_description_var, state='normal')
        self.antenna_description_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Use:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.antenna_use_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_use_var, state='normal')
        self.antenna_use_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Mount:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_mount_var).grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # Spacer
        ttk.Separator(equipment_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Amplifier Type:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.amplifier_type_combobox = ttk.Combobox(
            equipment_frame,
            textvariable=self.app_instance.selected_amplifier_type_var,
            values=[amp["Type"] for amp in antenna_amplifier_types],
            state="readonly" # This remains readonly as it's a selection from a predefined list
        )
        self.amplifier_type_combobox.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        self.amplifier_type_combobox.bind("<<ComboboxSelected>>", self._on_amplifier_type_selected)

        # NEW: Amplifier Description and Use fields
        ttk.Label(equipment_frame, text="Amplifier Description:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.amplifier_description_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.amplifier_description_var, state='normal')
        self.amplifier_description_entry.grid(row=7, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Amplifier Use:").grid(row=8, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.amplifier_use_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.amplifier_use_var, state='normal')
        self.amplifier_use_entry.grid(row=8, column=1, padx=5, pady=2, sticky="ew")


        # --- Notes ---
        notes_frame = ttk.LabelFrame(self, text="Notes", style='Dark.TLabelframe')
        notes_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        notes_frame.grid_columnconfigure(0, weight=1) # Allow notes widget to expand
        notes_frame.grid_rowconfigure(0, weight=1) # Allow notes widget to expand

        self.notes_text_widget = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, width=40, height=5)
        self.notes_text_widget.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
        self.notes_text_widget.bind("<KeyRelease>", self._on_notes_change)

        debug_print("ScanMetaDataTab widgets created.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_notes_change(self, event=None):
        # This function descriotion tells me what this function does
        # Updates the Tkinter notes_var from the ScrolledText widget and saves config.
        #
        # Inputs to this function
        #   event (tkinter.Event, optional): The event object that triggered the call.
        #
        # Process of this function
        #   1. Retrieves the current text from the ScrolledText widget.
        #   2. Sets the `app_instance.notes_var` with the retrieved text.
        #   3. Prints a debug message with the updated notes.
        #   4. Calls `save_config` to persist the changes.
        #
        # Outputs of this function
        #   None. Updates an internal Tkinter variable and saves application configuration.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """Updates the Tkinter notes_var from the ScrolledText widget and saves config."""
        self.app_instance.notes_var.set(self.notes_text_widget.get("1.0", tk.END).strip())
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print(f"Notes updated: {self.app_instance.notes_var.get()}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        save_config(self.app_instance) # Save config immediately on notes change


    def _on_tab_selected(self, event):
        # This function descriotion tells me what this function does
        # Called when this tab is selected in the notebook.
        # This can be used to refresh data or update UI elements specific to this tab.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message indicating the tab selection.
        #   2. Ensures the notes widget reflects the current value of `app_instance.notes_var`.
        #   3. Populates the `antenna_type_combobox` and `amplifier_type_combobox`
        #      with their respective values from `app_instance` if they are set.
        #   4. Triggers the update of antenna description and use based on the current selection.
        #   5. Explicitly populates all other text entry fields from their `app_instance` variables
        #      to ensure they reflect the loaded config values when the tab is selected.
        #
        # Outputs of this function
        #   None. Refreshes the UI elements on tab selection.
        #
        # (2025-07-30) Change: Added logic to refresh comboboxes and associated fields on tab selection.
        # (2025-07-30) Change: Added explicit population of all text entry fields from app_instance variables.
        """
        Called when this tab is selected in the notebook.
        This can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Scan Meta Data Tab selected.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        # When the tab is selected, ensure the notes widget reflects the app_instance's variable
        self.notes_text_widget.delete("1.0", tk.END)
        self.notes_text_widget.insert("1.0", self.app_instance.notes_var.get())

        # Explicitly set the values for all Entry widgets from their associated StringVars
        # This is a robust way to ensure the UI is in sync with the model (app_instance variables)
        self.app_instance.operator_name_var.set(self.app_instance.operator_name_var.get())
        self.app_instance.operator_contact_var.set(self.app_instance.operator_contact_var.get())
        self.app_instance.venue_name_var.set(self.app_instance.venue_name_var.get())
        self.app_instance.venue_postal_code_var.set(self.app_instance.venue_postal_code_var.get())
        self.app_instance.address_field_var.set(self.app_instance.address_field_var.get())
        self.app_instance.city_var.set(self.app_instance.city_var.get())
        self.app_instance.province_var.set(self.app_instance.province_var.get())
        self.app_instance.scanner_type_var.set(self.app_instance.scanner_type_var.get())
        self.app_instance.antenna_mount_var.set(self.app_instance.antenna_mount_var.get())
        
        # For comboboxes, set their value and then trigger their selection handler
        # This will ensure their associated description/use fields are also updated
        if self.app_instance.selected_antenna_type_var.get():
            self.antenna_type_combobox.set(self.app_instance.selected_antenna_type_var.get())
            self._on_antenna_type_selected(None) # Trigger update of description/use
        else: # If no antenna type is selected, clear the description/use fields
            self.app_instance.antenna_description_var.set("")
            self.app_instance.antenna_use_var.set("")

        if self.app_instance.selected_amplifier_type_var.get():
            self.amplifier_type_combobox.set(self.app_instance.selected_amplifier_type_var.get())
            self._on_amplifier_type_selected(None) # Trigger update of amplifier description/use
        else: # If no amplifier type is selected, clear the description/use fields
            self.app_instance.amplifier_description_var.set("")
            self.app_instance.amplifier_use_var.set("")


    def _lookup_postal_code(self):
        # This function descriotion tells me what this function does
        # Initiates a lookup of the venue postal code using the Google Maps Geocoding API.
        # It retrieves the postal code from the associated Tkinter variable,
        # calls the `get_location_from_google_maps` function, and updates the
        # address, city, and province Tkinter variables with the results.
        #
        # Inputs to this function
        #   None (operates on self).
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the postal code from `app_instance.venue_postal_code_var`.
        #   3. Checks if the postal code is empty. If so, prints a warning and clears fields.
        #   4. Calls `get_location_from_google_maps` with the postal code.
        #   5. Updates `app_instance.address_field_var`, `app_instance.city_var`,
        #      and `app_instance.province_var` with the returned values.
        #   6. Calls `save_config` to persist the updated location data.
        #
        # Outputs of this function
        #   None. Updates Tkinter variables and saves configuration.
        #
        # (2025-07-30) Change: Updated to use `get_location_from_google_maps`.
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Attempting postal code lookup using Google Maps API.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        postal_code = self.app_instance.venue_postal_code_var.get().strip()
        if not postal_code:
            self.console_print_func("⚠️ Please enter a postal code to look up.")
            self.app_instance.address_field_var.set("")
            self.app_instance.city_var.set("")
            self.app_instance.province_var.set("")
            save_config(self.app_instance)
            return

        # CHANGED: Call get_location_from_google_maps instead of get_location_from_text
        city, province, street_address = get_location_from_google_maps(postal_code, self.console_print_func)

        self.app_instance.address_field_var.set(street_address if street_address else "") # Changed N/A to empty string
        self.app_instance.city_var.set(city if city else "") # Changed N/A to empty string
        self.app_instance.province_var.set(province if province else "") # Changed N/A to empty string
        
        save_config(self.app_instance) # Save config after updating location data
        debug_print("Postal code lookup complete and fields updated.", file=current_file, function=current_function, console_print_func=self.console_print_func)


    def _on_antenna_type_selected(self, event):
        # This function descriotion tells me what this function does
        # Event handler for when an antenna type is selected from the dropdown.
        # It updates the 'Antenna Description' and 'Antenna Use' text boxes
        # based on the selected antenna type's data from `antenna_types`.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the currently selected antenna type from `selected_antenna_type_var`.
        #   3. Iterates through the `antenna_types` list to find a matching entry.
        #   4. If a match is found, updates `antenna_description_var` and `antenna_use_var`
        #      with the corresponding description and use.
        #   5. If no match is found, clears the description and use fields.
        #   6. Calls `save_config` to persist the selected antenna type.
        #
        # Outputs of this function
        #   None. Updates Tkinter variables and saves configuration.
        #
        # (2025-07-30) Change: No functional change, just updated header.
        """
        Event handler for when an antenna type is selected from the dropdown.
        It updates the 'Antenna Description' and 'Antenna Use' text boxes
        based on the selected antenna type's data from `antenna_types`.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Antenna type selected.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        selected_type = self.app_instance.selected_antenna_type_var.get()
        found_antenna = next((ant for ant in antenna_types if ant["Type"] == selected_type), None)

        if found_antenna:
            self.app_instance.antenna_description_var.set(found_antenna["Description"])
            self.app_instance.antenna_use_var.set(found_antenna["Use"])
            debug_print(f"Updated antenna description and use for: {selected_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.app_instance.antenna_description_var.set("")
            self.app_instance.antenna_use_var.set("")
            debug_print(f"No description/use found for selected antenna type: {selected_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        
        save_config(self.app_instance) # Save config immediately on selection


    def _on_amplifier_type_selected(self, event):
        # This function descriotion tells me what this function does
        # Event handler for when an amplifier type is selected from the dropdown.
        # It updates the `app_instance.antenna_amplifier_var` to reflect the
        # selected amplifier type, and also populates the `Amplifier Description`
        # and `Amplifier Use` text boxes based on the selected type's data.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message.
        #   2. Retrieves the currently selected amplifier type from `selected_amplifier_type_var`.
        #   3. Sets the `app_instance.antenna_amplifier_var` with the selected type.
        #   4. Iterates through the `antenna_amplifier_types` list to find a matching entry.
        #   5. If a match is found, updates `amplifier_description_var` and `amplifier_use_var`
        #      with the corresponding description and use.
        #   6. If no match is found, clears the description and use fields.
        #   7. Calls `save_config` to persist the selected amplifier type and its details.
        #
        # Outputs of this function
        #   None. Updates Tkinter variables and saves configuration.
        #
        # (2025-07-30) Change: Populated amplifier description and use fields, and updated header.
        """
        Event handler for when an amplifier type is selected from the dropdown.
        It updates the `app_instance.antenna_amplifier_var` to reflect the
        selected amplifier type, and also populates the `Amplifier Description`
        and `Amplifier Use` text boxes based on the selected type's data.
        """
        current_function = inspect.currentframe().f_code.co_name
        current_file = __file__
        debug_print("Amplifier type selected.", file=current_file, function=current_function, console_print_func=self.console_print_func)

        selected_type = self.app_instance.selected_amplifier_type_var.get()
        # The original antenna_amplifier_var was an Entry, now it's effectively linked to the Combobox selection
        self.app_instance.antenna_amplifier_var.set(selected_type)
        
        # NEW: Populate amplifier description and use
        found_amplifier = next((amp for amp in antenna_amplifier_types if amp["Type"] == selected_type), None)

        if found_amplifier:
            self.app_instance.amplifier_description_var.set(found_amplifier["Description"])
            self.app_instance.amplifier_use_var.set(found_amplifier["Use"])
            debug_print(f"Updated amplifier description and use for: {selected_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)
        else:
            self.app_instance.amplifier_description_var.set("")
            self.app_instance.amplifier_use_var.set("")
            debug_print(f"No description/use found for selected amplifier type: {selected_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)

        save_config(self.app_instance) # Save config immediately on selection
        debug_print(f"Updated antenna amplifier to: {selected_type}", file=current_file, function=current_function, console_print_func=self.console_print_func)
