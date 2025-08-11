# ref/ref_visa_commands.py
#
# This module provides a single, centralized list of default VISA commands
# for the application's interpreter. The data structure has been updated to
# include a 'Manufacturer' field to support the new column in the VISA Interpreter.
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
# Version 20250811.151008.0 (NEW: Added a 'Manufacturer' field to the command data structure.)

def get_default_commands():
    """
    Returns a list of default VISA commands.
    Each entry is a tuple: (Manufacturer, Model, Command Type, Action, VISA Command, Default Value for Variable, Validated).
    """
    default_raw_commands = [
        # System/Identification
        ("Keysight Technologies", "*", "System/ID", "GET", "*IDN", "?", ""),
        ("Keysight Technologies", "*", "System/Reset", "DO", "*RST", "", ""),
        ("Keysight Technologies", "*", "System/Errors", "GET", ":SYSTem:ERRor", "?", ""),
        ("Keysight Technologies", "*", "System/Display Update", "DO", ":SYSTem:DISPlay:UPDate", "", ""),
        ("Rohde & Schwarz", "*", "System/ID", "GET", "*IDN", "?", ""),
        ("Rohde & Schwarz", "*", "System/Reset", "DO", "*RST", "", ""),
        ("Rohde & Schwarz", "*", "System/Errors", "GET", ":SYSTem:ERRor", "?", ""),
        ("Rohde & Schwarz", "*", "System/Display Update", "DO", ":SYSTem:DISPlay:UPDate", "", ""),
        # Frequency/Span/Sweep
        ("Keysight Technologies", "*", "Frequency/Center", "SET", ":SENSe:FREQuency:CENTer", "1000", ""),
        ("Keysight Technologies", "*", "Frequency/Center", "GET", ":SENSe:FREQuency:CENTer", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Span", "SET", ":SENSe:FREQuency:SPAN", "1000", ""),
        ("Keysight Technologies", "*", "Frequency/Span", "GET", ":SENSe:FREQuency:SPAN", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Start", "GET", ":FREQuency:STARt", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Start", "SET", ":FREQuency:STARt", "100000", ""),
        ("Keysight Technologies", "*", "Frequency/Stop", "GET", ":FREQuency:STOP", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Stop", "SET", ":FREQuency:STOP", "200000", ""),
        ("Keysight Technologies", "*", "Frequency/Sweep/Points", "GET", ":SENSe:SWEep:POINts", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Sweep/Time", "SET", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Frequency/Sweep/Spacing", "SET", ":SENSe:X:SPACing LINear", "LINear", ""),
        ("Keysight Technologies", "*", "Frequency/Offset", "GET", ":FREQuency:OFFSet", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Shift", "GET", ":INPut:RFSense:FREQuency:SHIFt", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Shift", "SET", ":INPut:RFSense:FREQuency:SHIFt", "0", ""),

        # Bandwidth (RBW/VBW)
        ("Keysight Technologies", "*", "Bandwidth/Resolution", "SET", ":SENSe:BANDwidth:RESolution", "1000", ""),
        ("Keysight Technologies", "*", "Bandwidth/Resolution", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video", "SET", ":SENSe:BANDwidth:VIDeo", "100", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),
        ("Keysight Technologies", "*", "Bandwidth/Resolution/Auto", "SET", ":SENSe:BANDwidth:RESolution:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video/Auto", "SET", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),

        # Amplitude/Reference Level/Attenuation/Gain
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "SET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-20", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto", "SET", ":INPut:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto", "GET", ":INPut:ATTenuation:AUTO", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Gain/State", "SET", ":INPut:GAIN:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Gain/State", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/Auto", "SET", ":POWer:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/0dB", "SET", ":POWer:ATTenuation", "0", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/10dB", "SET", ":POWer:ATTenuation", "10", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/On", "SET", ":POWer:GAIN", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/Off", "SET", ":POWer:GAIN", "OFF", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/1", "SET", ":POWer:GAIN", "1", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/High Sensitive/On", "SET", ":POWer:HSENsitive", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/High Sensitive/Off", "SET", ":POWer:HSENsitive", "OFF", ""),

        # Trace/Display - Expanded for 4 traces
        # Trace Data Query
        ("Keysight Technologies", "N9342CN", "Trace/1/Data", "GET", ":TRACe:DATA? TRACE1", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/2/Data", "GET", ":TRACe:DATA? TRACE2", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/3/Data", "GET", ":TRACe:DATA? TRACE3", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/4/Data", "GET", ":TRACe:DATA? TRACE4", "", ""),

        ("Keysight Technologies", "N9340B", "Trace/1/Data", "GET", ":TRAC1:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/2/Data", "GET", ":TRAC2:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/3/Data", "GET", ":TRAC3:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/4/Data", "GET", ":TRAC4:DATA", "?", ""),

        # Trace Mode Write
        ("Keysight Technologies", "*", "Trace/1/Mode/Write", "SET", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/Write", "SET", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/Write", "SET", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/Write", "SET", ":TRAC4:MODE", "WRITe", ""),

        # Trace Mode MaxHold
        ("Keysight Technologies", "*", "Trace/1/Mode/MaxHold", "SET", ":TRAC1:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/MaxHold", "SET", ":TRAC2:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/MaxHold", "SET", ":TRAC3:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/MaxHold", "SET", ":TRAC4:MODE", "MAXHold", ""),

        # Trace Mode Average
        ("Keysight Technologies", "*", "Trace/1/Mode/Average", "SET", ":TRAC1:MODE", "AVERage", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/Average", "SET", ":TRAC2:MODE", "AVERage", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/Average", "SET", ":TRAC3:MODE", "AVERage", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/Average", "SET", ":TRAC4:MODE", "AVERage", ""),

        # Trace Mode MinHold
        ("Keysight Technologies", "*", "Trace/1/Mode/MinHold", "SET", ":TRAC1:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/MinHold", "SET", ":TRAC2:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/MinHold", "SET", ":TRAC3:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/MinHold", "SET", ":TRAC4:MODE", "MINHold", ""),

        ("Keysight Technologies", "*", "Trace/Display/Type", "GET", ":DISPlay:WINDow:TRACe:TYPE", "?", ""),
        ("Keysight Technologies", "*", "Trace/Display/Y Scale/Spacing", "SET", ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing", "LOGarithmic", ""),
        ("Keysight Technologies", "N9342CN", "Trace/Format/Data/ASCII (*)", "SET", ":TRACe:FORMat:DATA", "ASCii", ""), # For *
        ("Keysight Technologies", "N9342CN", "Trace/Format/Data/ASCII (General)", "SET", ":FORMat:DATA", "ASCii", ""), # General

        # Marker - Expanded for 6 markers
        # Marker Calculate Max
        ("Keysight Technologies", "*", "Marker/1/Calculate/Max", "DO", ":CALCulate:MARKer1:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/Max", "DO", ":CALCulate:MARKer2:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/Max", "DO", ":CALCulate:MARKer3:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/Max", "DO", ":CALCulate:MARKer4:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/Max", "DO", ":CALCulate:MARKer5:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/Max", "DO", ":CALCulate:MARKer6:MAX", "", ""),

        # Marker Calculate State
        ("Keysight Technologies", "*", "Marker/1/Calculate/State", "SET", ":CALCulate:MARKer1:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/State", "SET", ":CALCulate:MARKer2:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/State", "SET", ":CALCulate:MARKer3:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/State", "SET", ":CALCulate:MARKer4:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/State", "SET", ":CALCulate:MARKer5:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/State", "SET", ":CALCulate:MARKer6:STATe", "ON", ""),

        # Marker Calculate X (Frequency)
        ("Keysight Technologies", "*", "Marker/1/Calculate/X", "GET", ":CALCulate:MARKer1:X", "?", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/X", "GET", ":CALCulate:MARKer2:X", "?", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/X", "GET", ":CALCulate:MARKer3:X", "?", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/X", "GET", ":CALCulate:MARKer4:X", "?", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/X", "GET", ":CALCulate:MARKer5:X", "?", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/X", "GET", ":CALCulate:MARKer6:X", "?", ""),

        # Marker Calculate Y (Amplitude)
        ("Keysight Technologies", "*", "Marker/1/Calculate/Y", "GET", ":CALCulate:MARKer1:Y", "?", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/Y", "GET", ":CALCulate:MARKer2:Y", "?", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/Y", "GET", ":CALCulate:MARKer3:Y", "?", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/Y", "GET", ":CALCulate:MARKer4:Y", "?", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/Y", "GET", ":CALCulate:MARKer5:Y", "?", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/Y", "GET", ":CALCulate:MARKer6:Y", "?", ""),

        # Memory/Preset
        ("Keysight Technologies", "*", "Memory/Preset/Catalog", "GET", ":MMEMory:CATalog:STATe", "?", ""),
        ("Keysight Technologies", "*", "Memory/Preset/Load", "SET", ":MMEMory:LOAD:STATe", "0", ""),
        ("Keysight Technologies", "*", "Memory/Preset/Store", "SET", ":MMEMory:STORe:STATe", "0", ""),
    ]
    return default_raw_commands