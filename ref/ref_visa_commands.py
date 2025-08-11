# ref/ref_visa_commands.py
#
# This module provides a single, centralized list of default VISA commands
# for the application's interpreter.
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
# Version 20250811.141400.1 (NEW: Created to centralize the default VISA command list and refactor the command format for GET queries.)

def get_default_commands():
    """
    Returns a list of default VISA commands.
    Each entry is a tuple: (Model, Category, Action, VISA Command, Default Value for Variable, Validated).
    """
    default_raw_commands = [
        # System/Identification
        ("N9340B", "System/ID", "GET", "*IDN", "?", ""),
        ("N9340B", "System/Reset", "DO", "*RST", "", ""),
        ("N9340B", "System/Errors", "GET", ":SYSTem:ERRor", "?", ""),
        ("N9340B", "System/Display Update", "DO", ":SYSTem:DISPlay:UPDate", "", ""),

        # Frequency/Span/Sweep
        ("N9340B", "Frequency/Center", "SET", ":SENSe:FREQuency:CENTer", "1000", ""),
        ("N9340B", "Frequency/Center", "GET", ":SENSe:FREQuency:CENTer", "?", ""),
        ("N9340B", "Frequency/Span", "SET", ":SENSe:FREQuency:SPAN", "1000", ""),
        ("N9340B", "Frequency/Span", "GET", ":SENSe:FREQuency:SPAN", "?", ""),
        ("N9340B", "Frequency/Start", "GET", ":FREQuency:STARt", "?", ""),
        ("N9340B", "Frequency/Start", "SET", ":FREQuency:STARt", "100000", ""),
        ("N9340B", "Frequency/Stop", "GET", ":FREQuency:STOP", "?", ""),
        ("N9340B", "Frequency/Stop", "SET", ":FREQuency:STOP", "200000", ""),
        ("N9340B", "Frequency/Sweep/Points", "GET", ":SENSe:SWEep:POINts", "?", ""),
        ("N9340B", "Frequency/Sweep/Time", "SET", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("N9340B", "Frequency/Sweep/Spacing", "SET", ":SENSe:X:SPACing LINear", "LINear", ""),
        ("N9340B", "Frequency/Offset", "GET", ":FREQuency:OFFSet", "?", ""),
        ("N9340B", "Frequency/Shift", "GET", ":INPut:RFSense:FREQuency:SHIFt", "?", ""),
        ("N9340B", "Frequency/Shift", "SET", ":INPut:RFSense:FREQuency:SHIFt", "0", ""),


        # Bandwidth (RBW/VBW)
        ("N9340B", "Bandwidth/Resolution", "SET", ":SENSe:BANDwidth:RESolution", "1000", ""),
        ("N9340B", "Bandwidth/Resolution", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),
        ("N9340B", "Bandwidth/Video", "SET", ":SENSe:BANDwidth:VIDeo", "100", ""),
        ("N9340B", "Bandwidth/Video", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),
        ("N9340B", "Bandwidth/Resolution/Auto", "SET", ":SENSe:BANDwidth:RESolution:AUTO", "ON", ""),
        ("N9340B", "Bandwidth/Video/Auto", "SET", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),

        # Amplitude/Reference Level/Attenuation/Gain
        ("N9340B", "Amplitude/Reference Level", "SET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-20", ""),
        ("N9340B", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("N9340B", "Amplitude/Attenuation/Auto", "SET", ":INPut:ATTenuation:AUTO", "ON", ""),
        ("N9340B", "Amplitude/Attenuation/Auto", "GET", ":INPut:ATTenuation:AUTO", "?", ""),
        ("N9340B", "Amplitude/Gain/State", "SET", ":INPut:GAIN:STATe", "ON", ""),
        ("N9340B", "Amplitude/Gain/State", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("N9340B", "Amplitude/Power/Attenuation/Auto", "SET", ":POWer:ATTenuation:AUTO", "ON", ""),
        ("N9340B", "Amplitude/Power/Attenuation/0dB", "SET", ":POWer:ATTenuation", "0", ""),
        ("N9340B", "Amplitude/Power/Attenuation/10dB", "SET", ":POWer:ATTenuation", "10", ""),
        ("N9340B", "Amplitude/Power/Gain/On", "SET", ":POWer:GAIN", "ON", ""),
        ("N9340B", "Amplitude/Power/Gain/Off", "SET", ":POWer:GAIN", "OFF", ""),
        ("N9340B", "Amplitude/Power/Gain/1", "SET", ":POWer:GAIN", "1", ""),
        ("N9340B", "Amplitude/Power/High Sensitive/On", "SET", ":POWer:HSENsitive", "ON", ""),
        ("N9340B", "Amplitude/Power/High Sensitive/Off", "SET", ":POWer:HSENsitive", "OFF", ""),

        # Trace/Display - Expanded for 4 traces
        # Trace Data Query
        ("N9342CN", "Trace/1/Data", "GET", ":TRACe:DATA? TRACE1", "", ""),
        ("N9342CN", "Trace/2/Data", "GET", ":TRACe:DATA? TRACE2", "", ""),
        ("N9342CN", "Trace/3/Data", "GET", ":TRACe:DATA? TRACE3", "", ""),
        ("N9342CN", "Trace/4/Data", "GET", ":TRACe:DATA? TRACE4", "", ""),


               # Trace/Display - Expanded for 4 traces
        # Trace Data Query
        ("N9340B", "Trace/1/Data", "GET", ":TRAC1:DATA", "?", ""),
        ("N9340B", "Trace/2/Data", "GET", ":TRAC2:DATA", "?", ""),
        ("N9340B", "Trace/3/Data", "GET", ":TRAC3:DATA", "?", ""),
        ("N9340B", "Trace/4/Data", "GET", ":TRAC4:DATA", "?", ""),

        # Trace Mode Write
        ("N9340B", "Trace/1/Mode/Write", "SET", ":TRAC1:MODE", "WRITe", ""),
        ("N9340B", "Trace/2/Mode/Write", "SET", ":TRAC2:MODE", "WRITe", ""),
        ("N9340B", "Trace/3/Mode/Write", "SET", ":TRAC3:MODE", "WRITe", ""),
        ("N9340B", "Trace/4/Mode/Write", "SET", ":TRAC4:MODE", "WRITe", ""),

        # Trace Mode MaxHold
        ("N940B", "Trace/1/Mode/MaxHold", "SET", ":TRAC1:MODE", "MAXHold", ""),
        ("N9340B", "Trace/2/Mode/MaxHold", "SET", ":TRAC2:MODE", "MAXHold", ""),
        ("N9340B", "Trace/3/Mode/MaxHold", "SET", ":TRAC3:MODE", "MAXHold", ""),
        ("N9340B", "Trace/4/Mode/MaxHold", "SET", ":TRAC4:MODE", "MAXHold", ""),

        # Trace Mode Average
        ("N9340B", "Trace/1/Mode/Average", "SET", ":TRAC1:MODE", "AVERage", ""),
        ("N9340B", "Trace/2/Mode/Average", "SET", ":TRAC2:MODE", "AVERage", ""),
        ("N9340B", "Trace/3/Mode/Average", "SET", ":TRAC3:MODE", "AVERage", ""),
        ("N9340B", "Trace/4/Mode/Average", "SET", ":TRAC4:MODE", "AVERage", ""),

        # Trace Mode MinHold
        ("N9340B", "Trace/1/Mode/MinHold", "SET", ":TRAC1:MODE", "MINHold", ""),
        ("N9340B", "Trace/2/Mode/MinHold", "SET", ":TRAC2:MODE", "MINHold", ""),
        ("N9340B", "Trace/3/Mode/MinHold", "SET", ":TRAC3:MODE", "MINHold", ""),
        ("N9340B", "Trace/4/Mode/MinHold", "SET", ":TRAC4:MODE", "MINHold", ""),

        ("N9340B", "Trace/Display/Type", "GET", ":DISPlay:WINDow:TRACe:TYPE", "?", ""),
        ("N9340B", "Trace/Display/Y Scale/Spacing", "SET", ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing", "LOGarithmic", ""),
        ("N9342CN", "Trace/Format/Data/ASCII (N9340B)", "SET", ":TRACe:FORMat:DATA", "ASCii", ""), # For N9340B
        ("N9340B", "Trace/Format/Data/ASCII (General)", "SET", ":FORMat:DATA", "ASCii", ""), # General

        # Marker - Expanded for 6 markers
        # Marker Calculate Max
        ("N9340B", "Marker/1/Calculate/Max", "DO", ":CALCulate:MARKer1:MAX", "", ""),
        ("N9340B", "Marker/2/Calculate/Max", "DO", ":CALCulate:MARKer2:MAX", "", ""),
        ("N9340B", "Marker/3/Calculate/Max", "DO", ":CALCulate:MARKer3:MAX", "", ""),
        ("N9340B", "Marker/4/Calculate/Max", "DO", ":CALCulate:MARKer4:MAX", "", ""),
        ("N9340B", "Marker/5/Calculate/Max", "DO", ":CALCulate:MARKer5:MAX", "", ""),
        ("N9340B", "Marker/6/Calculate/Max", "DO", ":CALCulate:MARKer6:MAX", "", ""),

        # Marker Calculate State
        ("N9340B", "Marker/1/Calculate/State", "SET", ":CALCulate:MARKer1:STATe", "ON", ""),
        ("N9340B", "Marker/2/Calculate/State", "SET", ":CALCulate:MARKer2:STATe", "ON", ""),
        ("N940B", "Marker/3/Calculate/State", "SET", ":CALCulate:MARKer3:STATe", "ON", ""),
        ("N9340B", "Marker/4/Calculate/State", "SET", ":CALCulate:MARKer4:STATe", "ON", ""),
        ("N9340B", "Marker/5/Calculate/State", "SET", ":CALCulate:MARKer5:STATe", "ON", ""),
        ("N9340B", "Marker/6/Calculate/State", "SET", ":CALCulate:MARKer6:STATe", "ON", ""),

        # Marker Calculate X (Frequency)
        ("N9340B", "Marker/1/Calculate/X", "GET", ":CALCulate:MARKer1:X", "?", ""),
        ("N9340B", "Marker/2/Calculate/X", "GET", ":CALCulate:MARKer2:X", "?", ""),
        ("N9340B", "Marker/3/Calculate/X", "GET", ":CALCulate:MARKer3:X", "?", ""),
        ("N9340B", "Marker/4/Calculate/X", "GET", ":CALCulate:MARKer4:X", "?", ""),
        ("N9340B", "Marker/5/Calculate/X", "GET", ":CALCulate:MARKer5:X", "?", ""),
        ("N9340B", "Marker/6/Calculate/X", "GET", ":CALCulate:MARKer6:X", "?", ""),

        # Marker Calculate Y (Amplitude)
        ("N9340B", "Marker/1/Calculate/Y", "GET", ":CALCulate:MARKer1:Y", "?", ""),
        ("N9340B", "Marker/2/Calculate/Y", "GET", ":CALCulate:MARKer2:Y", "?", ""),
        ("N9340B", "Marker/3/Calculate/Y", "GET", ":CALCulate:MARKer3:Y", "?", ""),
        ("N9340B", "Marker/4/Calculate/Y", "GET", ":CALCulate:MARKer4:Y", "?", ""),
        ("N9340B", "Marker/5/Calculate/Y", "GET", ":CALCulate:MARKer5:Y", "?", ""),
        ("N9340B", "Marker/6/Calculate/Y", "GET", ":CALCulate:MARKer6:Y", "?", ""),

        # Memory/Preset
        ("N9340B", "Memory/Preset/Catalog", "GET", ":MMEMory:CATalog:STATe", "?", ""),
        ("N9340B", "Memory/Preset/Load", "SET", ":MMEMory:LOAD:STATe", "0", ""),
        ("N9340B", "Memory/Preset/Store", "SET", ":MMEMory:STORe:STATe", "0", ""),
    ]
    return default_raw_commands
