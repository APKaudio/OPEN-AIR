# tabs/Scanning/tab_scanning_child_scan_meta_data.py
#
# This file defines the ScanMetaDataTab, a Tkinter Frame that contains the Scan Meta Data settings.
# This includes operator, venue, equipment, and general notes. It provides interactive elements
# like a postal code lookup and dynamic updates for antenna and amplifier descriptions.
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
# Version 20250802.0011.3 (Fixed TclError: unknown option "-style_obj" by explicitly filtering it from kwargs.)

current_version = "20250802.0011.3" # this variable should always be defined below the header to make the debugging better
current_version_hash = 20250802 * 11 * 3 # Example hash, adjust as needed

import tkinter as tk
from tkinter import ttk, scrolledtext
import inspect
import os # For os.path.exists and os.makedirs
import subprocess # For opening folders

# Updated imports for new logging functions
from src.debug_logic import debug_log
from src.console_logic import console_log

from src.settings_and_config.config_manager import save_config

# Import new modules for functionality - CORRECTED PATHS
from process_math.google_maps_lookup import get_location_from_google_maps
from ref.Antenna_type import antenna_types
from ref.antenna_amplifier_type import antenna_amplifier_types


class ScanMetaDataTab(ttk.Frame):
    """
    A Tkinter Frame that contains the Scan Meta Data settings.
    This includes operator, venue, equipment, and general notes.
    """
    def __init__(self, master=None, app_instance=None, console_print_func=None, style_obj=None, **kwargs):
        # This function description tells me what this function does
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
        #   style_obj (ttk.Style): The ttk.Style object for applying styles.
        #   **kwargs: Arbitrary keyword arguments passed to the ttk.Frame constructor.
        #
        # Process of this function
        #   1. Calls the superclass constructor (ttk.Frame).
        #   2. Stores references to app_instance, console_print_func, and style_obj.
        #   3. Initializes new Tkinter StringVars for postal code, address, province,
        #      selected antenna type, antenna description, antenna use, antenna mount,
        #      and selected amplifier type, amplifier description, and amplifier use.
        #   4. Calls _create_widgets to build the UI.
        #
        # Outputs of this function
        #   None. Initializes the Tkinter frame and its internal state.
        #
        # (2025-07-30) Change: Initialized new StringVars for regrouped fields, including new amplifier description/use.
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: Added missing widget attributes to allow external configuration.
        # (20250802.0011.2) Change: Fixed TclError by correctly handling style_obj in __init__.
        # (20250802.0011.3) Change: Fixed TclError by explicitly filtering style_obj from kwargs.
        
        # Filter out 'style_obj' from kwargs before passing to super().__init__
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'style_obj'}
        super().__init__(master, style='Dark.TFrame', **filtered_kwargs) # Pass style string, and filtered kwargs

        self.app_instance = app_instance
        self.console_print_func = console_print_func if console_print_func else console_log # Use console_log as default
        self.style_obj = style_obj # Store the style object

        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Initializing ScanMetaDataTab. Version: {current_version}. Setting up meta data fields!",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        self._create_widgets()

        debug_log(f"ScanMetaDataTab initialized. Version: {current_version}. Meta data interface ready!",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _create_widgets(self):
        # This function description tells me what this function does
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: Assigned widgets to self attributes for external access.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Creating ScanMetaDataTab widgets... Building the meta data input form! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

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

        ttk.Label(personnel_frame, text="Operator Name:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.operator_name_entry = ttk.Entry(personnel_frame, textvariable=self.app_instance.operator_name_var, style='TEntry')
        self.operator_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(personnel_frame, text="Operator Contact:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.operator_contact_entry = ttk.Entry(personnel_frame, textvariable=self.app_instance.operator_contact_var, style='TEntry')
        self.operator_contact_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")


        # --- Location Box ---
        location_frame = ttk.LabelFrame(self, text="Location", style='Dark.TLabelframe')
        location_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        location_frame.grid_columnconfigure(1, weight=1) # Allow entry widgets to expand

        ttk.Label(location_frame, text="Venue Name:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.venue_name_entry = ttk.Entry(location_frame, textvariable=self.app_instance.venue_name_var, style='TEntry')
        self.venue_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="Venue Postal Code:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.postal_code_entry = ttk.Entry(location_frame, textvariable=self.app_instance.venue_postal_code_var, style='TEntry')
        self.postal_code_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # Button for calling the postal code lookup function
        self.lookup_location_button = ttk.Button(location_frame, text="Lookup Location", command=self._lookup_postal_code, style='Blue.TButton')
        self.lookup_location_button.grid(row=1, column=2, padx=5, pady=2, sticky="e")

        ttk.Label(location_frame, text="Address Field:", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        self.address_field_entry = ttk.Entry(location_frame, textvariable=self.app_instance.address_field_var, style='TEntry')
        self.address_field_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="City:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        self.city_entry = ttk.Entry(location_frame, textvariable=self.app_instance.city_var, style='TEntry')
        self.city_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(location_frame, text="Province:", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: Removed state='readonly'
        self.province_entry = ttk.Entry(location_frame, textvariable=self.app_instance.province_var, style='TEntry')
        self.province_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=2, sticky="ew")


        # --- Equipment Used Box ---
        equipment_frame = ttk.LabelFrame(self, text="Equipment Used", style='Dark.TLabelframe')
        equipment_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        equipment_frame.grid_columnconfigure(1, weight=1) # Allow entry/combobox to expand

        ttk.Label(equipment_frame, text="Scanner Type:", style='TLabel').grid(row=0, column=0, padx=5, pady=2, sticky="w")
        # Renamed to equipment_used_entry to match scan_logic.py's expectation
        self.equipment_used_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.scanner_type_var, style='TEntry')
        self.equipment_used_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Type:", style='TLabel').grid(row=1, column=0, padx=5, pady=2, sticky="w")
        # Renamed to antenna_type_dropdown to match scan_logic.py's expectation
        self.antenna_type_dropdown = ttk.Combobox(
            equipment_frame,
            textvariable=self.app_instance.selected_antenna_type_var,
            values=[ant["Type"] for ant in antenna_types],
            state="readonly", # This remains readonly as it's a selection from a predefined list
            style='TCombobox'
        )
        self.antenna_type_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.antenna_type_dropdown.bind("<<ComboboxSelected>>", self._on_antenna_type_selected)

        ttk.Label(equipment_frame, text="Antenna Description:", style='TLabel').grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.antenna_description_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_description_var, state='normal', style='TEntry')
        self.antenna_description_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Use:", style='TLabel').grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.antenna_use_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_use_var, state='normal', style='TEntry')
        self.antenna_use_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Mount:", style='TLabel').grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.antenna_mount_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.antenna_mount_var, style='TEntry')
        self.antenna_mount_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # Spacer
        ttk.Separator(equipment_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Label(equipment_frame, text="Antenna Amplifier Type:", style='TLabel').grid(row=6, column=0, padx=5, pady=2, sticky="w")
        # Renamed to antenna_amplifier_dropdown to match scan_logic.py's expectation
        self.antenna_amplifier_dropdown = ttk.Combobox(
            equipment_frame,
            textvariable=self.app_instance.selected_amplifier_type_var,
            values=[amp["Type"] for amp in antenna_amplifier_types],
            state="readonly", # This remains readonly as it's a selection from a predefined list
            style='TCombobox'
        )
        self.antenna_amplifier_dropdown.grid(row=6, column=1, padx=5, pady=2, sticky="ew")
        self.antenna_amplifier_dropdown.bind("<<ComboboxSelected>>", self._on_amplifier_type_selected)

        # NEW: Amplifier Description and Use fields
        ttk.Label(equipment_frame, text="Amplifier Description:", style='TLabel').grid(row=7, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.amplifier_description_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.amplifier_description_var, state='normal', style='TEntry')
        self.amplifier_description_entry.grid(row=7, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(equipment_frame, text="Amplifier Use:", style='TLabel').grid(row=8, column=0, padx=5, pady=2, sticky="w")
        # CHANGED: state='readonly' to state='normal'
        self.amplifier_use_entry = ttk.Entry(equipment_frame, textvariable=self.app_instance.amplifier_use_var, state='normal', style='TEntry')
        self.amplifier_use_entry.grid(row=8, column=1, padx=5, pady=2, sticky="ew")


        # --- Notes ---
        notes_frame = ttk.LabelFrame(self, text="Notes", style='Dark.TLabelframe')
        notes_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        notes_frame.grid_columnconfigure(0, weight=1) # Allow notes widget to expand
        notes_frame.grid_rowconfigure(0, weight=1) # Allow notes widget to expand

        # Renamed to notes_text to match scan_logic.py's expectation
        self.notes_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, width=40, height=5)
        self.notes_text.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
        self.notes_text.bind("<KeyRelease>", self._on_notes_change)

        debug_log(f"ScanMetaDataTab widgets created. Meta data form is complete! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _on_notes_change(self, event=None):
        # This function description tells me what this function does
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: Updated to use self.notes_text.
        """Updates the Tkinter notes_var from the ScrolledText widget and saves config."""
        self.app_instance.notes_var.set(self.notes_text.get("1.0", tk.END).strip())
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Notes updated: {self.app_instance.notes_var.get()}. Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
        # Corrected call to save_config with all required arguments
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)


    def _on_tab_selected(self, event):
        # This function description tells me what this function does
        # Called when this tab is selected in the notebook.
        # This can be used to refresh data or update UI elements specific to this tab.
        #
        # Inputs to this function
        #   event (tkinter.Event): The event object that triggered the call.
        #
        # Process of this function
        #   1. Prints a debug message indicating the tab selection.
        #   2. Ensures the notes widget reflects the current value of `app_instance.notes_var`.
        #   3. Populates the `antenna_type_dropdown` and `antenna_amplifier_dropdown`
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: Updated to use new widget attribute names.
        """
        Called when this tab is selected in the notebook.
        This can be used to refresh data or update UI elements specific to this tab.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Scan Meta Data Tab selected. Refreshing all fields! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        # When the tab is selected, ensure the notes widget reflects the app_instance's variable
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", self.app_instance.notes_var.get())

        # Explicitly set the values for all Entry widgets from their associated StringVars
        # This is a robust way to ensure the UI is in sync with the model (app_instance variables)
        self.operator_name_entry.config(textvariable=self.app_instance.operator_name_var)
        self.operator_contact_entry.config(textvariable=self.app_instance.operator_contact_var)
        self.venue_name_entry.config(textvariable=self.app_instance.venue_name_var)
        self.postal_code_entry.config(textvariable=self.app_instance.venue_postal_code_var)
        self.address_field_entry.config(textvariable=self.app_instance.address_field_var)
        self.city_entry.config(textvariable=self.app_instance.city_var)
        self.province_entry.config(textvariable=self.app_instance.province_var)
        self.equipment_used_entry.config(textvariable=self.app_instance.scanner_type_var) # Corrected
        self.antenna_mount_entry.config(textvariable=self.app_instance.antenna_mount_var)
        
        # For comboboxes, set their value and then trigger their selection handler
        # This will ensure their associated description/use fields are also updated
        if self.app_instance.selected_antenna_type_var.get():
            self.antenna_type_dropdown.set(self.app_instance.selected_antenna_type_var.get())
            self._on_antenna_type_selected(None) # Trigger update of description/use
        else: # If no antenna type is selected, clear the description/use fields
            self.app_instance.antenna_description_var.set("")
            self.app_instance.antenna_use_var.set("")

        if self.app_instance.selected_amplifier_type_var.get():
            self.antenna_amplifier_dropdown.set(self.app_instance.selected_amplifier_type_var.get())
            self._on_amplifier_type_selected(None) # Trigger update of amplifier description/use
        else: # If no amplifier type is selected, clear the description/use fields
            self.app_instance.amplifier_description_var.set("")
            self.app_instance.amplifier_use_var.set("")

        debug_log(f"Scan Meta Data Tab refreshed. All fields are up-to-date! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _lookup_postal_code(self):
        # This function description tells me what this function does
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: No functional changes.
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Attempting postal code lookup using Google Maps API. Let's find this location! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        postal_code = self.app_instance.venue_postal_code_var.get().strip()
        if not postal_code:
            self.console_print_func("⚠️ Please enter a postal code to look up. Don't leave it blank!")
            self.app_instance.address_field_var.set("")
            self.app_instance.city_var.set("")
            self.app_instance.province_var.set("")
            # Corrected call to save_config with all required arguments
            save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
            debug_log(f"Postal code was empty. Lookup aborted. Version: {current_version}",
                        file=__file__,
                        version=current_version,
                        function=current_function)
            return

        # CHANGED: Call get_location_from_google_maps instead of get_location_from_text
        city, province, street_address = get_location_from_google_maps(postal_code, self.console_print_func)

        self.app_instance.address_field_var.set(street_address if street_address else "") # Changed N/A to empty string
        self.app_instance.city_var.set(city if city else "") # Changed N/A to empty string
        self.app_instance.province_var.set(province if province else "") # Changed N/A to empty string
        
        # Corrected call to save_config with all required arguments
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        self.console_print_func("✅ Postal code lookup complete and fields updated. Location found!")
        debug_log(f"Postal code lookup complete and fields updated. Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _on_antenna_type_selected(self, event):
        # This function description tells me what this function does
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: No functional changes.
        """
        Event handler for when an antenna type is selected from the dropdown.
        It updates the 'Antenna Description' and 'Antenna Use' text boxes
        based on the selected antenna type's data from `antenna_types`.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Antenna type selected. Updating description and use! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        selected_type = self.app_instance.selected_antenna_type_var.get()
        found_antenna = next((ant for ant in antenna_types if ant["Type"] == selected_type), None)

        if found_antenna:
            self.app_instance.antenna_description_var.set(found_antenna["Description"])
            self.app_instance.antenna_use_var.set(found_antenna["Use"])
            debug_log(f"Updated antenna description and use for: {selected_type}. Details loaded!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.app_instance.antenna_description_var.set("")
            self.app_instance.antenna_use_var.set("")
            debug_log(f"No description/use found for selected antenna type: {selected_type}. Fields cleared!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        
        # Corrected call to save_config with all required arguments
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        debug_log(f"Antenna type updated and config saved. Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)


    def _on_amplifier_type_selected(self, event):
        # This function description tells me what this function does
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
        # (20250801.2330.1) Change: Refactored debug_print to use debug_log and console_log.
        # (20250802.0011.1) Change: No functional changes.
        """
        Event handler for when an amplifier type is selected from the dropdown.
        It updates the `app_instance.antenna_amplifier_var` to reflect the
        selected amplifier type, and also populates the `Amplifier Description`
        and `Amplifier Use` text boxes based on the selected type's data.
        """
        current_function = inspect.currentframe().f_code.co_name
        debug_log(f"Amplifier type selected. Getting details for this amplifier! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)

        selected_type = self.app_instance.selected_amplifier_type_var.get()
        # The original antenna_amplifier_var was an Entry, now it's effectively linked to the Combobox selection
        self.app_instance.antenna_amplifier_var.set(selected_type)
        
        # NEW: Populate amplifier description and use
        found_amplifier = next((amp for amp in antenna_amplifier_types if amp["Type"] == selected_type), None)

        if found_amplifier:
            self.app_instance.amplifier_description_var.set(found_amplifier["Description"])
            self.app_instance.amplifier_use_var.set(found_amplifier["Use"])
            debug_log(f"Updated amplifier description and use for: {selected_type}. Details loaded!",
                        file=__file__,
                        version=current_version,
                        function=current_function)
        else:
            self.app_instance.amplifier_description_var.set("")
            self.app_instance.amplifier_use_var.set("")
            debug_log(f"No description/use found for selected amplifier type: {selected_type}. Fields cleared!",
                        file=__file__,
                        version=current_version,
                        function=current_function)

        # Corrected call to save_config with all required arguments
        save_config(self.app_instance.config, self.app_instance.CONFIG_FILE_PATH, self.console_print_func, self.app_instance)
        debug_log(f"Updated antenna amplifier to: {selected_type}. Config saved! Version: {current_version}",
                    file=__file__,
                    version=current_version,
                    function=current_function)
