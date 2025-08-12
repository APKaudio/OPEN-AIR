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
# Version 20250811.204600.0

current_version = "20250811.204600.0"
current_version_hash = 20250811 * 204600 * 0

def get_default_commands():
    """
    Returns a list of default VISA commands.
    Each entry is a tuple: (Manufacturer, Model, Command Type, Action, VISA Command, Default Value for Variable, Validated).
    """
    default_raw_commands = [
        # System/Identification
        ("Keysight Technologies", "*", "SYSTEM/ID", "GET", "*IDN", "?", ""),
        ("Keysight Technologies", "*", "SYSTEM/RESET", "DO", "*RST", "", ""),
        ("Keysight Technologies", "*", "SYSTEM/ERRORS", "GET", ":SYSTem:ERRor", "?", ""),
        ("Keysight Technologies", "*", "SYSTEM/DISPLAY/UPDATE", "DO", ":SYSTem:DISPlay:UPDate", "", ""),
        ("Rohde & Schwarz", "*", "SYSTEM/ID", "GET", "*IDN", "?", ""),
        ("Rohde & Schwarz", "*", "SYSTEM/RESET", "DO", "*RST", "", ""),
        ("Rohde & Schwarz", "*", "SYSTEM/ERRORS", "GET", ":SYSTem:ERRor", "?", ""),
        ("Rohde & Schwarz", "*", "SYSTEM/DISPLAY/UPDATE", "DO", ":SYSTem:DISPlay:UPDate", "", ""),
        # Frequency/Span/Sweep
        ("Keysight Technologies", "*", "FREQUENCY/CENTER", "SET", ":SENSe:FREQuency:CENTer", "1000", ""),
        ("Keysight Technologies", "*", "FREQUENCY/CENTER", "GET", ":SENSe:FREQuency:CENTer", "?", ""),
        ("Keysight Technologies", "*", "FREQUENCY/SPAN", "SET", ":SENSe:FREQuency:SPAN", "1000", ""),
        ("Keysight Technologies", "*", "FREQUENCY/SPAN", "GET", ":SENSe:FREQuency:SPAN", "?", ""),
        ("Keysight Technologies", "*", "FREQUENCY/START", "GET", ":FREQuency:STARt", "?", ""),
        ("Keysight Technologies", "*", "FREQUENCY/START", "SET", ":FREQuency:STARt", "1000", ""),
        ("Keysight Technologies", "*", "FREQUENCY/STOP", "GET", ":FREQuency:STOP", "?", ""),
        ("Keysight Technologies", "*", "FREQUENCY/STOP", "SET", ":FREQuency:STOP", "2000", ""),
        ("Keysight Technologies", "*", "FREQUENCY/SWEEP/POINTS", "GET", ":SENSe:SWEep:POINts", "?", ""),
        
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SWEEP/TIME", "GET", "::SENSe:SWEep:TIME", "?", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SWEEP/TIME/ON", "DO", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SWEEP/TIME", "GET", "::SENSe:SWEep:TIME", "?", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SWEEP/TIME/OFF", "DO", ":SENSe:SWEep:TIME:AUTO", "OFF", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SWEEP/TIME", "GET", "::SENSe:SWEep:TIME", "?", ""),

        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME", "SET", ":SENSe:SWEep:TIME", "3", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME", "GET", "::SENSe:SWEep:TIME", "?", ""),

        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO/ON", "DO", ":SENSe:SWEep:TIME:AUTO", "ON", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO/OFF", "DO", ":SENSe:SWEep:TIME:AUTO", "OFF", ""),

        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/MODE", "DO", ":SENSe:SWEep:TIME:AUTO:MODE", "NORMAL", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TIME/AUTO", "GET", ":SENSe:SWEep:TIME:AUTO", "?", ""),        
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/MODE", "DO", ":SENSe:SWEep:TIME:AUTO:MODE", "FAST", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/MODE", "GET", ":SENSe:SWEep:TIME:AUTO:MODE", "?", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TDMODE/ON", "DO", ":SENSe:SWEep:TDMode", "ON", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TDMODE/OFF", "DO", ":SENSe:SWEep:TDMode", "OFF", ""),
        ("Agilent Technologies", "N9340B", "FREQUENCY/SWEEP/TDMODE", "GET", ":SENSe:SWEep:TDMode", "?", ""),

        ("Keysight Technologies", "*", "FREQUENCY/SWEEP/SPACING/LINEAR", "DO", ":SENSe:X:SPACing LINear", "LINear", ""),
        
        ("Keysight Technologies", "N9342CN", "FREQUENCY/OFFSET", "GET", ":FREQuency:OFFSet", "?", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SHIFT", "GET", ":INPut:RFSense:FREQuency:SHIFt", "?", ""),
        ("Keysight Technologies", "N9342CN", "FREQUENCY/SHIFT/0", "DO", ":INPut:RFSense:FREQuency:SHIFt", "0", ""),

        # Bandwidth (RBW/VBW)
        ("Keysight Technologies", "*", "BANDWIDTH/RESOLUTION", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/RESOLUTION", "SET", ":SENSe:BANDwidth:RESolution", "1000000", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/RESOLUTION", "GET", ":SENSe:BANDwidth:RESolution", "?", ""),

        ("Keysight Technologies", "*", "INITIATE/CONTINUOUS", "GET", ":INITiate:CONTinuous", "?", ""),
        ("Keysight Technologies", "*", "INITIATE/CONTINUOUS/ON", "DO", ":INITiate:CONTinuous", "ON", ""),
        ("Keysight Technologies", "*", "INITIATE/CONTINUOUS", "GET", ":INITiate:CONTinuous", "?", ""),
        ("Keysight Technologies", "*", "INITIATE/CONTINUOUS/OFF", "DO", ":INITiate:CONTinuous", "Off", ""),
        ("Keysight Technologies", "*", "INITIATE/IMMEDIATE", "SET", ":INITiate:IMMediate", "", ""),

        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO", "SET", ":SENSe:BANDwidth:VIDeo", "1000000", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO", "GET", ":SENSe:BANDwidth:VIDeo", "?", ""),

        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO/AUTO/ON", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO/AUTO", "GET", ":SENSe:BANDwidth:VIDeo:AUTO", "?", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO/AUTO/OFF", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "OFF", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO/AUTO", "GET", ":SENSe:BANDwidth:VIDeo:AUTO", "?", ""),

        ("Keysight Technologies", "*", "BANDWIDTH/RESOLUTION/AUTO/ON", "DO", ":SENSe:BANDwidth:RESolution:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "BANDWIDTH/VIDEO/AUTO/ON", "DO", ":SENSe:BANDwidth:VIDeo:AUTO", "ON", ""),

        # Amplitude/Reference Level/Attenuation/Gain
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/0", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "0", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/10", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "10", ""),   
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "20", ""),   
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/30", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "30", ""),   
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "40", ""),   
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-10", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-10", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),              
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-20", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-20", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-30", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-30", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-40", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-40", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-50", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-50", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-50", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-50", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-60", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-60", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-70", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-70", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-80", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-80", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-90", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-90", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL/-100", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel", "-100", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/REFERENCE LEVEL", "GET", ":DISPlay:WINDow:TRACe:Y:RLEVel", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/ATTENUATION/AUTO/ON", "DO", ":INPut:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/ATTENUATION/AUTO", "GET", ":INPut:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/ATTENUATION/AUTO/OFF", "DO", ":INPut:ATTenuation:AUTO", "OFF", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/ATTENUATION/AUTO", "GET", ":INPut:ATTenuation", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/GAIN/STATE/ON", "DO", ":INPut:GAIN:STATe", "ON", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/GAIN/STATE", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/GAIN/STATE/OFF", "DO", ":INPut:GAIN:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/GAIN/STATE", "GET", ":INPut:GAIN:STATe", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/AUTO/ON", "DO", ":POWer:ATTenuation:AUTO", "ON", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/AUTO/OFF", "DO", ":POWer:ATTenuation:AUTO", "OFF", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/0DB", "DO", ":POWer:ATTenuation", "0", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/10DB", "DO", ":POWer:ATTenuation", "10", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/20DB", "DO", ":POWer:ATTenuation", "20", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/30DB", "DO", ":POWer:ATTenuation", "30", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/40DB", "DO", ":POWer:ATTenuation", "40", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/50DB", "DO", ":POWer:ATTenuation", "50", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/60DB", "DO", ":POWer:ATTenuation", "60", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION/70DB", "DO", ":POWer:ATTenuation", "70", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/ATTENUATION", "GET", ":POWer:ATTenuation", "?", ""),

        ("Keysight Technologies", "*", "AMPLITUDE/POWER/GAIN/ON", "DO", ":POWer:GAIN", "ON", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/GAIN", "GET", ":POWer:GAIN", "?", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/GAIN/OFF", "DO", ":POWer:GAIN", "OFF", ""),
        ("Keysight Technologies", "*", "AMPLITUDE/POWER/GAIN", "GET", ":POWer:GAIN", "?", ""),
        
        ("Keysight Technologies", "N9342CN", "AMPLITUDE/POWER/HIGH SENSITIVE/ON", "DO", ":POWer:HSENsitive", "ON", ""),
        ("Keysight Technologies", "N9342CN", "AMPLITUDE/POWER/HIGH SENSITIVE/OFF", "DO", ":POWer:HSENsitive", "OFF", ""),

        ("Keysight Technologies", "N9340B", "AMPLITUDE/POWER/HIGH SENSITIVE/ON", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel -50; :POWer:ATTenuation 0; :POWer:GAIN ON", "", ""),
        ("Keysight Technologies", "N9340B", "AMPLITUDE/POWER/HIGH SENSITIVE/OFF", "DO", ":DISPlay:WINDow:TRACe:Y:RLEVel 0; :POWer:ATTenuation 20; :POWer:GAIN OFF", "", ""),



        # Trace Mode Write
        ("Keysight Technologies", "*", "TRACE/1/MODE/WRITE", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/WRITE", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/WRITE", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/WRITE", "DO", ":TRAC4:MODE", "WRITe", ""),

        # Trace/Display - Expanded for 4 traces
        # Trace Data Query
        ("Keysight Technologies", "N9342CN", "TRACE/1/DATA", "GET", ":TRACe:DATA? TRACE1", "", ""),
        ("Keysight Technologies", "N9342CN", "TRACE/2/DATA", "GET", ":TRACe:DATA? TRACE2", "", ""),
        ("Keysight Technologies", "N9342CN", "TRACE/3/DATA", "GET", ":TRACe:DATA? TRACE3", "", ""),
        ("Keysight Technologies", "N9342CN", "TRACE/4/DATA", "GET", ":TRACe:DATA? TRACE4", "", ""),

        ("Keysight Technologies", "N9340B", "TRACE/1/DATA", "GET", ":TRACe1:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "TRACE/2/DATA", "GET", ":TRACe2:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "TRACE/3/DATA", "GET", ":TRACe3:DATA", "?", ""),
        ("Keysight Technologies", "N9340B", "TRACE/4/DATA", "GET", ":TRACe4:DATA", "?", ""),

        # Averaging
        ("Keysight Technologies", "*", "TRACE/1/AVERAGE/ON", "DO", ":SENS:AVER:TRAC1:STAT", "ON", ""),
        ("Keysight Technologies", "*", "TRACE/2/AVERAGE/ON", "DO", ":SENS:AVER:TRAC2:STAT", "ON", ""),
        ("Keysight Technologies", "*", "TRACE/3/AVERAGE/ON", "DO", ":SENS:AVER:TRAC3:STAT", "ON", ""),
        ("Keysight Technologies", "*", "TRACE/4/AVERAGE/ON", "DO", ":SENS:AVER:TRAC4:STAT", "ON", ""),

        # Trace Mode write
        ("Keysight Technologies", "*", "TRACE/1/MODE/WRITE", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/WRITE", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/WRITE", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/WRITE", "DO", ":TRAC4:MODE", "WRITe", ""),
        
        ("Keysight Technologies", "*", "TRACE/1/MODE", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE", "GET", ":TRAC4:MODE", "?", ""),

        ("Keysight Technologies", "*", "TRACE/1/MODE/WRITE", "DO", ":TRAC1:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/1/MODE/BLANK", "DO", ":TRAC1:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/WRITE", "DO", ":TRAC2:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/BLANK", "DO", ":TRAC2:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/WRITE", "DO", ":TRAC3:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/BLANK", "DO", ":TRAC3:MODE", "BLANk", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/WRITE", "DO", ":TRAC4:MODE", "WRITe", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/BLANK", "DO", ":TRAC4:MODE", "BLANk", ""),
        
        ("Keysight Technologies", "*", "TRACE/1/MODE", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE", "GET", ":TRAC4:MODE", "?", ""),

        # Trace Mode MaxHold
        ("Keysight Technologies", "*", "TRACE/1/MODE/MAXHOLD", "DO", ":TRAC1:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/MAXHOLD", "DO", ":TRAC2:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/MAXHOLD", "DO", ":TRAC3:MODE", "MAXHold", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/MAXHOLD", "DO", ":TRAC4:MODE", "MAXHold", ""),

        ("Keysight Technologies", "*", "TRACE/1/MODE", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE", "GET", ":TRAC4:MODE", "?", ""),

        # Trace Mode MinHold
        ("Keysight Technologies", "*", "TRACE/1/MODE/MINHOLD", "DO", ":TRAC1:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/MINHOLD", "DO", ":TRAC2:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/MINHOLD", "DO", ":TRAC3:MODE", "MINHold", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/MINHOLD", "DO", ":TRAC4:MODE", "MINHold", ""),

        ("Keysight Technologies", "*", "TRACE/1/MODE", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE", "GET", ":TRAC4:MODE", "?", ""),

        # Trace Mode VIEW
        ("Keysight Technologies", "*", "TRACE/1/MODE/VIEW", "DO", ":TRAC1:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE/VIEW", "DO", ":TRAC2:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE/VIEW", "DO", ":TRAC3:MODE", "VIEW", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE/VIEW", "DO", ":TRAC4:MODE", "VIEW", ""),

        ("Keysight Technologies", "*", "TRACE/1/MODE", "GET", ":TRAC1:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/MODE", "GET", ":TRAC2:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/MODE", "GET", ":TRAC3:MODE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/MODE", "GET", ":TRAC4:MODE", "?", ""),

        # Averaging:
        ("Keysight Technologies", "", "TRACE/1/AVERAGE/COUNT", "SET", ":SENS:AVER:TRAC1:COUNT", "10", ""),
        ("Keysight Technologies", "", "TRACE/2/AVERAGE/COUNT", "SET", ":SENS:AVER:TRAC2:COUNT", "10", ""),
        ("Keysight Technologies", "", "TRACE/3/AVERAGE/COUNT", "SET", ":SENS:AVER:TRAC3:COUNT", "10", ""),
        ("Keysight Technologies", "", "TRACE/4/AVERAGE/COUNT", "SET", ":SENS:AVER:TRAC4:COUNT", "10", ""),

        ("Keysight Technologies", "", "TRACE/1/AVERAGE/COUNT", "GET", ":SENS:AVER:TRAC1:COUNT", "?", ""),
        ("Keysight Technologies", "", "TRACE/2/AVERAGE/COUNT", "GET", ":SENS:AVER:TRAC2:COUNT", "?", ""),
        ("Keysight Technologies", "", "TRACE/3/AVERAGE/COUNT", "GET", ":SENS:AVER:TRAC3:COUNT", "?", ""),
        ("Keysight Technologies", "", "TRACE/4/AVERAGE/COUNT", "GET", ":SENS:AVER:TRAC4:COUNT", "?", ""),

        ("Keysight Technologies", "*", "TRACE/1/AVERAGE", "GET", ":SENS:AVER:TRAC1:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/AVERAGE", "GET", ":SENS:AVER:TRAC2:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/AVERAGE", "GET", ":SENS:AVER:TRAC3:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/AVERAGE", "GET", ":SENS:AVER:TRAC4:STAT", "?", ""),

        ("Keysight Technologies", "*", "TRACE/1/AVERAGE/OFF", "SET", ":SENS:AVER:TRAC1:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "TRACE/2/AVERAGE/OFF", "SET", ":SENS:AVER:TRAC2:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "TRACE/3/AVERAGE/OFF", "SET", ":SENS:AVER:TRAC3:STAT", "OFF", ""),
        ("Keysight Technologies", "*", "TRACE/4/AVERAGE/OFF", "SET", ":SENS:AVER:TRAC4:STAT", "OFF", ""),

        ("Keysight Technologies", "*", "TRACE/1/AVERAGE", "GET", ":SENS:AVER:TRAC1:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/2/AVERAGE", "GET", ":SENS:AVER:TRAC2:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/3/AVERAGE", "GET", ":SENS:AVER:TRAC3:STAT", "?", ""),
        ("Keysight Technologies", "*", "TRACE/4/AVERAGE", "GET", ":SENS:AVER:TRAC4:STAT", "?", ""),

        ("Keysight Technologies", "*", "TRACE/DISPLAY/TYPE", "GET", ":DISPlay:WINDow:TRACe:TYPE", "?", ""),
        ("Keysight Technologies", "*", "TRACE/DISPLAY/Y SCALE/SPACING", "SET", ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing", "LOGarithmic", ""),
        ("Keysight Technologies", "N9342CN", "TRACE/FORMAT/DATA/ASCII", "DO", ":TRACe:FORMat:DATA", "ASCii", ""), # For *
        ("Keysight Technologies", "N9340B", "TRACE/FORMAT/DATA/ASCII", "DO", ":FORMat:DATA", "ASCii", ""), # General

        # Marker - Expanded for 6 markers
        # Marker Calculate Max
        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/MAX", "DO", ":CALCulate:MARKer1:MAX", "", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/MAX", "DO", ":CALCulate:MARKer2:MAX", "", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/MAX", "DO", ":CALCulate:MARKer3:MAX", "", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/MAX", "DO", ":CALCulate:MARKer4:MAX", "", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/MAX", "DO", ":CALCulate:MARKer5:MAX", "", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/MAX", "DO", ":CALCulate:MARKer6:MAX", "", ""),


        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/NEXT", "DO", ":CALCulate:MARKer1:NEXT", "", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/NEXT", "DO", ":CALCulate:MARKer2:NEXT", "", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/NEXT", "DO", ":CALCulate:MARKer3:NEXT", "", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/NEXT", "DO", ":CALCulate:MARKer4:NEXT", "", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/NEXT", "DO", ":CALCulate:MARKer5:NEXT", "", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/NEXT", "DO", ":CALCulate:MARKer6:NEXT", "", ""),

        ("Keysight Technologies", "*", "MARKER/PEAK/SEARCH", "DO", "CALCulate:MARKer1:MAXimum; :CALCulate:MARKer2:MAXimum:LEFT; :CALCulate:MARKer3:MAXimum:RIGHt; :CALCulate:MARKer4:MAXimum:LEFT; :CALCulate:MARKer5:MAXimum:RIGHt; :CALCulate:MARKer6:MAXimum:LEFT", "", ""),




        # Marker Calculate State
        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer1:STATe", "ON", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer2:STATe", "ON", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer3:STATe", "ON", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer4:STATe", "ON", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer5:STATe", "ON", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/STATE/ON", "DO", ":CALCulate:MARKer6:STATe", "ON", ""),

        # Marker Calculate State
        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer1:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer2:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer3:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer4:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer5:STATe", "OFF", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/STATE/OFF", "DO", ":CALCulate:MARKer6:STATe", "OFF", ""),



        # Marker Calculate X (Frequency)
        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/X", "GET", ":CALCulate:MARKer1:X", "?", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/X", "GET", ":CALCulate:MARKer2:X", "?", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/X", "GET", ":CALCulate:MARKer3:X", "?", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/X", "GET", ":CALCulate:MARKer4:X", "?", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/X", "GET", ":CALCulate:MARKer5:X", "?", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/X", "GET", ":CALCulate:MARKer6:X", "?", ""),

        # Marker Calculate Y (Amplitude)
        ("Keysight Technologies", "*", "MARKER/1/CALCULATE/Y", "GET", ":CALCulate:MARKer1:Y", "?", ""),
        ("Keysight Technologies", "*", "MARKER/2/CALCULATE/Y", "GET", ":CALCulate:MARKer2:Y", "?", ""),
        ("Keysight Technologies", "*", "MARKER/3/CALCULATE/Y", "GET", ":CALCulate:MARKer3:Y", "?", ""),
        ("Keysight Technologies", "*", "MARKER/4/CALCULATE/Y", "GET", ":CALCulate:MARKer4:Y", "?", ""),
        ("Keysight Technologies", "*", "MARKER/5/CALCULATE/Y", "GET", ":CALCulate:MARKer5:Y", "?", ""),
        ("Keysight Technologies", "*", "MARKER/6/CALCULATE/Y", "GET", ":CALCulate:MARKer6:Y", "?", ""),

        # Memory/Preset
        ("Keysight Technologies", "*", "MEMORY/PRESET/CATALOG", "GET", ":MMEMory:CATalog:STATe", "?", ""),
        ("Keysight Technologies", "*", "MEMORY/PRESET/LOAD", "SET", ":MMEMory:LOAD:STATe", "0", ""),
        ("Keysight Technologies", "*", "MEMORY/PRESET/STORE", "SET", ":MMEMory:STORe:STATe", "0", ""),
        
        ("Keysight Technologies", "*", "POWER/RESET", "DO", "SYSTem:POWer:RESet", "", ""),
    ]
    return default_raw_commands