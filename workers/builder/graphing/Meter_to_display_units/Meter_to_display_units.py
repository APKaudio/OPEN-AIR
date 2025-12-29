# Based on the Visual Basic files provided, specifically MeterTest.Designer.vb and MeterTest.vb, I have recreated the functionality in Python using the Pygame library.


# This script, Meter_to_display_units.py, replicates the two custom controls found in your VB project:

# Horizontal_Meter_With_Text: Handles the "Orders of Magnitude" display. I have designed this to break a number down into powers of 10 (100s, 10s, 1s, 0.1s) to visualize the magnitude. It also implements the specific logic found in your designer file: "if the number is -ve it should go right to left".


# Vertical_Meter: Handles the 4-channel plotting logic (Plot_V1 through Plot_V4) controlled by the trackbars in the VB code.


# File: Meter_to_display_units.py
#Python