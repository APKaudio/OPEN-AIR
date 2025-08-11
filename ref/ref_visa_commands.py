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
        ("Keysight Technologies", "*", "Frequency/Start", "SET", ":FREQuency:STARt", "1000", ""),
        ("Keysight Technologies", "*", "Frequency/Stop", "GET", ":FREQuency:STOP", "?", ""),
        ("Keysight Technologies", "*", "Frequency/Stop", "SET", ":FREQuency:STOP", "2000", ""),
        ("Keysight Technologies", "*", "Frequency/Sweep/Points", "GET", ":SENSe:SWEep:POINts", "?", ""),
        
        
        ("Keysight Technologies", "N9342CN", "Frequency/Sweep/Time", "GET", "::SENSe:SWEep:TIME", "?", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Sweep/Time/On", "DO", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Sweep/Time", "GET", "::SENSe:SWEep:TIME", "?", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Sweep/Time/Off", "DO", ":SENSe:SWEep:TIME:AUTO", "OFF", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Sweep/Time", "GET", "::SENSe:SWEep:TIME", "?", ""),



        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time", "SET", ":SENSe:SWEep:TIME", "3", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time", "GET", "::SENSe:SWEep:TIME", "?", ""),

        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto/On", "DO", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto/Off", "DO", ":SENSe:SWEep:TIME:AUTO", "OFF", ""),

        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Mode", "DO", ":SENSe:SWEep:TIME:AUTO:MODE", "NORMAL", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Time/Auto", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),        
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Mode", "DO", ":SENSe:SWEep:TIME:AUTO:MODE", "FAST", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/Mode", "GET", ":SENSe:SWEep:TIME:AUTO:MODE", "?", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/TDMode/On", "DO", ":SENSe:SWEep:TDMode", "ON", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/TDMode/Off", "DO", ":SENSe:SWEep:TDMode", "OFF", ""),
        ("Agilent Technologies", "N9340B", "Frequency/Sweep/TDMode", "GET", ":SENSe:SWEep:TDMode", "?", ""),

        ("Keysight Technologies", "*", "Frequency/Sweep/Spacing/Linear", "DO", ":SENSe:X:SPACing LINear", "LINear", ""),
        
        
        ("Keysight Technologies", "N9342CN", "Frequency/Offset", "GET", ":FREQuency:OFFSet", "?", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Shift", "GET", ":INPut:RFSense:FREQuency:SHIFt", "?", ""),
        ("Keysight Technologies", "N9342CN", "Frequency/Shift/0", "DO", ":INPut:RFSense:FREQuency:SHIFt", "0", ""),

        # Bandwidth (RBW/VBW)
        ("Keysight Technologies", "*", "Bandwidth/Resolution", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),
        ("Keysight Technologies", "*", "Bandwidth/Resolution", "SET", ":SENSe:BANDwidth:RESolution", "1000000", ""),
        ("Keysight Technologies", "*", "Bandwidth/Resolution", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),

        ("Keysight Technologies", "*", "INITiate/CONTinuous", "GET", ":INITiate:CONTinuous", "?", ""),
        ("Keysight Technologies", "*", "INITiate/CONTinuous/On", "DO", ":INITiate:CONTinuous", "ON", ""),
        ("Keysight Technologies", "*", "INITiate/CONTinuous", "GET", ":INITiate:CONTinuous", "?", ""),
        ("Keysight Technologies", "*", "INITiate/CONTinuous/Off", "DO", ":INITiate:CONTinuous", "Off", ""),
        ("Keysight Technologies", "*", "INITiate/IMMediate", "SET", ":INITiate:IMMediate", "", ""),


        ("Keysight Technologies", "*", "Bandwidth/Video", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video", "SET", ":SENSe:BANDwidth:VIDeo", "1000000", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),

        ("Keysight Technologies", "*", "Bandwidth/Video/Auto/On", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video/Auto", "GET", ":SENSe:BANDwidth:VIDeo:AUTO", "?", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video/Auto/Off", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "OFF", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video/Auto", "GET", ":SENSe:BANDwidth:VIDeo:AUTO", "?", ""),

        ("Keysight Technologies", "*", "Bandwidth/Resolution/Auto/On", "DO", ":SENSe:BANDwidth:RESolution:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Bandwidth/Video/Auto/On", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),

        # Amplitude/Reference Level/Attenuation/Gain
        
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/0", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "0", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        
        ("Keysight Technologies", "*", "Amplitude/Reference Level/10", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "10", ""),   
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Reference Level/20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "20", ""),   
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Reference Level/30", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "30", ""),   
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Reference Level/20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "40", ""),   
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Reference Level/-10", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-10", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        
               
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-20", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-30", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-30", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-40", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-40", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-50", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-50", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Reference Level/-50", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-50", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-60", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-60", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-70", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-70", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-80", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-80", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-90", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-90", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level/-100", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-100", ""),
        ("Keysight Technologies", "*", "Amplitude/Reference Level", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto/On", "DO", ":INPut:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto", "GET", ":INPut:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto/Off", "DO", ":INPut:ATTenuation:AUTO", "OFF", ""),
        ("Keysight Technologies", "*", "Amplitude/Attenuation/Auto", "GET", ":INPut:ATTenuation", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Gain/State/On", "DO", ":INPut:GAIN:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Gain/State", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Gain/State/Off", "DO", ":INPut:GAIN:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "Amplitude/Gain/State", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/Auto/On", "DO", ":POWer:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/Auto/Off", "DO", ":POWer:ATTenuation:AUTO", "OFF", ""),

        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/0dB", "DO", ":POWer:ATTenuation", "0", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/10dB", "DO", ":POWer:ATTenuation", "10", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/20dB", "DO", ":POWer:ATTenuation", "20", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/30dB", "DO", ":POWer:ATTenuation", "30", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/40dB", "DO", ":POWer:ATTenuation", "40", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/50dB", "DO", ":POWer:ATTenuation", "50", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/50dB", "DO", ":POWer:ATTenuation", "60", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/50dB", "DO", ":POWer:ATTenuation", "70", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Attenuation/", "GET", ":POWer:ATTenuation", "?", ""),

        ("Keysight Technologies", "*", "Amplitude/Power/Gain/On", "DO", ":POWer:GAIN", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/On", "GET", ":POWer:GAIN", "?", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/Off", "DO", ":POWer:GAIN", "OFF", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/Gain/On", "GET", ":POWer:GAIN", "?", ""),
        #("Keysight Technologies", "*", "Amplitude/Power/Gain/1", "DO", ":POWer:GAIN", "1", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/High Sensitive/On", "DO", ":POWer:HSENsitive", "ON", ""),
        ("Keysight Technologies", "*", "Amplitude/Power/High Sensitive/Off", "DO", ":POWer:HSENsitive", "OFF", ""),


        # Trace Mode Write
        ("Keysight Technologies", "*", "Trace/1/Mode/Write", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/Write", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/Write", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/Write", "DO", ":TRAC4:MODE", "WRITe", ""),

        # Trace/Display - Expanded for 4 traces
        # Trace Data Query
        ("Keysight Technologies", "N9342CN", "Trace/1/Data", "GET", ":TRACe:DATA? TRACE1", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/2/Data", "GET", ":TRACe:DATA? TRACE2", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/3/Data", "GET", ":TRACe:DATA? TRACE3", "", ""),
        ("Keysight Technologies", "N9342CN", "Trace/4/Data", "GET", ":TRACe:DATA? TRACE4", "", ""),

        ("Keysight Technologies", "N9340B", "Trace/1/Data", "GET", ":TRACe1:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/2/Data", "GET", ":TRACe2:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/3/Data", "GET", ":TRACe3:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "Trace/4/Data", "GET", ":TRACe4:DATA", "?", ""),


             # Trace Mode BLANK

#turn averaging on
        ("Keysight Technologies", "*", "Trace/1/Average/On", "DO", ":SENS:AVER:TRAC1:STAT", "ON", ""),
        ("Keysight Technologies", "*", "Trace/2/Average/On", "DO", ":SENS:AVER:TRAC2:STAT", "ON", ""),
        ("Keysight Technologies", "*", "Trace/3/Average/On", "DO", ":SENS:AVER:TRAC3:STAT", "ON", ""),
        ("Keysight Technologies", "*", "Trace/4/Average/On", "DO", ":SENS:AVER:TRAC4:STAT", "ON", ""),


# Trace Mode write
        ("Keysight Technologies", "*", "Trace/1/Mode/WRITe", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/WRITe", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/WRITe", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/WRITe", "DO", ":TRAC4:MODE", "WRITe", ""),
        
        
        ("Keysight Technologies", "*", "Trace/1/Mode", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode", "GET", ":TRAC4:MODE", "?", ""),




        ("Keysight Technologies", "*", "Trace/1/Mode/WRITe", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/1/Mode/WRITe", "DO", ":TRAC1:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/WRITe", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/WRITe", "DO", ":TRAC2:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/WRITe", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/WRITe", "DO", ":TRAC3:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/WRITe", "DO", ":TRAC4:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/WRITe", "DO", ":TRAC4:MODE", "BLANk", ""),
        

        ("Keysight Technologies", "*", "Trace/1/Mode", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode", "GET", ":TRAC4:MODE", "?", ""),

        # Trace Mode MaxHold
        ("Keysight Technologies", "*", "Trace/1/Mode/MaxHold", "DO", ":TRAC1:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/MaxHold", "DO", ":TRAC2:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/MaxHold", "DO", ":TRAC3:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/MaxHold", "DO", ":TRAC4:MODE", "MAXHold", ""),

        ("Keysight Technologies", "*", "Trace/1/Mode", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode", "GET", ":TRAC4:MODE", "?", ""),

        # Trace Mode MinHold
        ("Keysight Technologies", "*", "Trace/1/Mode/MinHold", "DO", ":TRAC1:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/MinHold", "DO", ":TRAC2:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/MinHold", "DO", ":TRAC3:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/MinHold", "DO", ":TRAC4:MODE", "MINHold", ""),

        ("Keysight Technologies", "*", "Trace/1/Mode", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode", "GET", ":TRAC4:MODE", "?", ""),


   

        # Trace Mode VIEW
        ("Keysight Technologies", "*", "Trace/1/Mode/WRITe", "DO", ":TRAC1:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode/WRITe", "DO", ":TRAC2:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode/WRITe", "DO", ":TRAC3:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode/WRITe", "DO", ":TRAC4:MODE", "VIEW", ""),

        ("Keysight Technologies", "*", "Trace/1/Mode", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Mode", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Mode", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Mode", "GET", ":TRAC4:MODE", "?", ""),



#Averaging:

        ("Keysight Technologies", "", "Trace/1/Average/Count", "SET", ":SENS:AVER:TRAC1:COUNT", "10", ""),
        ("Keysight Technologies", "", "Trace/2/Average/Count", "SET", ":SENS:AVER:TRAC2:COUNT", "10", ""),
        ("Keysight Technologies", "", "Trace/3/Average/Count", "SET", ":SENS:AVER:TRAC3:COUNT", "10", ""),
        ("Keysight Technologies", "", "Trace/4/Average/Count", "SET", ":SENS:AVER:TRAC4:COUNT", "10", ""),

        ("Keysight Technologies", "", "Trace/1/Average/Count", "GET", ":SENS:AVER:TRAC1:COUNT", "?", ""),
        ("Keysight Technologies", "", "Trace/2/Average/Count", "GET", ":SENS:AVER:TRAC2:COUNT", "?", ""),
        ("Keysight Technologies", "", "Trace/3/Average/Count", "GET", ":SENS:AVER:TRAC3:COUNT", "?", ""),
        ("Keysight Technologies", "", "Trace/4/Average/Count", "GET", ":SENS:AVER:TRAC4:COUNT", "?", ""),





        ("Keysight Technologies", "*", "Trace/1/Average", "GET", ":SENS:AVER:TRAC1:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Average", "GET", ":SENS:AVER:TRAC2:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Average", "GET", ":SENS:AVER:TRAC3:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Average", "GET", ":SENS:AVER:TRAC4:STAT", "?", ""),


        ("Keysight Technologies", "*", "Trace/1/Average/Off", "SET", ":SENS:AVER:TRAC1:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "Trace/2/Average/Off", "SET", ":SENS:AVER:TRAC2:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "Trace/3/Average/Off", "SET", ":SENS:AVER:TRAC3:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "Trace/4/Average/Off", "SET", ":SENS:AVER:TRAC4:STAT", "OFF", ""),

        ("Keysight Technologies", "*", "Trace/1/Average", "GET", ":SENS:AVER:TRAC1:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/2/Average", "GET", ":SENS:AVER:TRAC2:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/3/Average", "GET", ":SENS:AVER:TRAC3:STAT", "?", ""),
        ("Keysight Technologies", "*", "Trace/4/Average", "GET", ":SENS:AVER:TRAC4:STAT", "?", ""),





        ("Keysight Technologies", "*", "Trace/Display/Type", "GET", ":DISPlay:WINDow:TRACe:TYPE", "?", ""),
        ("Keysight Technologies", "*", "Trace/Display/Y Scale/Spacing", "SET", ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing", "LOGarithmic", ""),
        ("Keysight Technologies", "N9342CN", "Trace/Format/Data/ASCII (*)", "DO", ":TRACe:FORMat:DATA", "ASCii", ""), # For *
        ("Keysight Technologies", "N9342CN", "Trace/Format/Data/ASCII (General)", "DO", ":FORMat:DATA", "ASCii", ""), # General

        # Marker - Expanded for 6 markers
        # Marker Calculate Max
        ("Keysight Technologies", "*", "Marker/1/Calculate/Max", "DO", ":CALCulate:MARKer1:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/Max", "DO", ":CALCulate:MARKer2:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/Max", "DO", ":CALCulate:MARKer3:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/Max", "DO", ":CALCulate:MARKer4:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/Max", "DO", ":CALCulate:MARKer5:MAX", "", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/Max", "DO", ":CALCulate:MARKer6:MAX", "", ""),

        # Marker Calculate State
        ("Keysight Technologies", "*", "Marker/1/Calculate/State", "DO", ":CALCulate:MARKer1:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/2/Calculate/State", "DO", ":CALCulate:MARKer2:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/3/Calculate/State", "DO", ":CALCulate:MARKer3:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/4/Calculate/State", "DO", ":CALCulate:MARKer4:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/5/Calculate/State", "DO", ":CALCulate:MARKer5:STATe", "ON", ""),
        ("Keysight Technologies", "*", "Marker/6/Calculate/State", "DO", ":CALCulate:MARKer6:STATe", "ON", ""),

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
        
        
        ("Keysight Technologies", "*", "Power/Reset", "DO", "SYSTem:POWer:RESet", "", ""),
    ]
    return default_raw_commands