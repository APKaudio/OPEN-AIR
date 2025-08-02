# frequency_bands.py
#
# This module defines constants and data structures related to frequency bands
# relevant to RF spectrum analysis. It separates the bands used for instrument
# scanning from those used purely for plotting markers (e.g., TV channels,
# government/commercial bands), enhancing modularity and clarity.
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
# Conversion factor from MHz to Hz
MHZ_TO_HZ = 1_000_000

# Ratio for Video Bandwidth (VBW) to Resolution Bandwidth (RBW)
VBW_RBW_RATIO = 1/3

# Define the frequency bands to *SCAN* (User's specified bands for instrument operation)
# This list will be used by the scan_bands function.
# Each dictionary contains:
# - "Band Name": A human-readable name for the band.
# - "Start MHz": The starting frequency of the band in Megahertz.
# - "Stop MHz": The stopping frequency of the band in Megahertz.
SCAN_BAND_RANGES = [
    {"Band Name": "Low VHF+FM", "Start MHz": 50.000, "Stop MHz": 110.000},
    {"Band Name": "High VHF+216", "Start MHz": 170.000, "Stop MHz": 220.000},
    {"Band Name": "UHF 400-500", "Start MHz": 400.000, "Stop MHz": 500.000},
    {"Band Name": "UHF 500-600", "Start MHz": 500.000, "Stop MHz": 600.000},
    {"Band Name": "UHF 600-700", "Start MHz": 600.000, "Stop MHz": 700.000},
    {"Band Name": "UHF 700-800", "Start MHz": 700.000, "Stop MHz": 800.000},
    {"Band Name": "UHF 800-900", "Start MHz": 800.000, "Stop MHz": 900.000},
    {"Band Name": "ISM-STL 900-970", "Start MHz": 900.000, "Stop MHz": 970.000},
    {"Band Name": "AFTRCC 1430-1540", "Start MHz": 1430.000, "Stop MHz": 1540.000},
    {"Band Name": "DECT-ALL 1880-2000", "Start MHz": 1880.000, "Stop MHz": 2000.000},
    {"Band Name": "Cams Lower 2G-2.2G", "Start MHz": 2000.000, "Stop MHz": 2200.000},
    {"Band Name": "Cams Upper 2.4G-2.4G", "Start MHz": 2200.000, "Stop MHz": 2400.000},
]

# North American TV Channel Bands (for plotting)
# This list is used by the plotting functions to overlay visual markers
# on the spectrum plots, helping to identify common TV broadcast frequencies.
# Each dictionary contains:
# - "Band Name": The name of the TV channel.
# - "Start MHz": The starting frequency of the channel in Megahertz.
# - "Stop MHz": The stopping frequency of the channel in Megahertz.
TV_PLOT_BAND_MARKERS = [
    {"Band Name": "TV Channel 2", "Start MHz": 54, "Stop MHz": 60},
    {"Band Name": "TV Channel 3", "Start MHz": 60, "Stop MHz": 66},
    {"Band Name": "TV Channel 4", "Start MHz": 66, "Stop MHz": 72},
    {"Band Name": "TV Channel 5", "Start MHz": 76, "Stop MHz": 82},
    {"Band Name": "TV Channel 6", "Start MHz": 82, "Stop MHz": 88},
    {"Band Name": "TV Channel 7", "Start MHz": 174, "Stop MHz": 180},
    {"Band Name": "TV Channel 8", "Start MHz": 180, "Stop MHz": 186},
    {"Band Name": "TV Channel 9", "Start MHz": 186, "Stop MHz": 192},
    {"Band Name": "TV Channel 10", "Start MHz": 192, "Stop MHz": 198},
    {"Band Name": "TV Channel 11", "Start MHz": 198, "Stop MHz": 204},
    {"Band Name": "TV Channel 12", "Start MHz": 204, "Stop MHz": 210},
    {"Band Name": "TV Channel 13", "Start MHz": 210, "Stop MHz": 216},
    {"Band Name": "TV Channel 14", "Start MHz": 470, "Stop MHz": 476},
    {"Band Name": "TV Channel 15", "Start MHz": 476, "Stop MHz": 482},
    {"Band Name": "TV Channel 16", "Start MHz": 482, "Stop MHz": 488},
    {"Band Name": "TV Channel 17", "Start MHz": 488, "Stop MHz": 494},
    {"Band Name": "TV Channel 18", "Start MHz": 494, "Stop MHz": 500},
    {"Band Name": "TV Channel 19", "Start MHz": 500, "Stop MHz": 506},
    {"Band Name": "TV Channel 20", "Start MHz": 506, "Stop MHz": 512},
    {"Band Name": "TV Channel 21", "Start MHz": 512, "Stop MHz": 518},
    {"Band Name": "TV Channel 22", "Start MHz": 518, "Stop MHz": 524},
    {"Band Name": "TV Channel 23", "Start MHz": 524, "Stop MHz": 530},
    {"Band Name": "TV Channel 24", "Start MHz": 530, "Stop MHz": 536},
    {"Band Name": "TV Channel 25", "Start MHz": 536, "Stop MHz": 542},
    {"Band Name": "TV Channel 26", "Start MHz": 542, "Stop MHz": 548},
    {"Band Name": "TV Channel 27", "Start MHz": 548, "Stop MHz": 554},
    {"Band Name": "TV Channel 28", "Start MHz": 554, "Stop MHz": 560},
    {"Band Name": "TV Channel 29", "Start MHz": 560, "Stop MHz": 566},
    {"Band Name": "TV Channel 30", "Start MHz": 566, "Stop MHz": 572},
    {"Band Name": "TV Channel 31", "Start MHz": 572, "Stop MHz": 578},
    {"Band Name": "TV Channel 32", "Start MHz": 578, "Stop MHz": 584},
    {"Band Name": "TV Channel 33", "Start MHz": 584, "Stop MHz": 590},
    {"Band Name": "TV Channel 34", "Start MHz": 590, "Stop MHz": 596},
    {"Band Name": "TV Channel 35", "Start MHz": 596, "Stop MHz": 602},
    {"Band Name": "TV Channel 36", "Start MHz": 602, "Stop MHz": 608},
    {"Band Name": "TV Channel 37 (Radio Astronomy)", "Start MHz": 608, "Stop MHz": 614}, # Note for special use
    {"Band Name": "TV Channel 38", "Start MHz": 614, "Stop MHz": 620},
    {"Band Name": "TV Channel 39", "Start MHz": 620, "Stop MHz": 626},
    {"Band Name": "TV Channel 40", "Start MHz": 626, "Stop MHz": 632},
    {"Band Name": "TV Channel 41", "Start MHz": 632, "Stop MHz": 638},
    {"Band Name": "TV Channel 42", "Start MHz": 638, "Stop MHz": 644},
    {"Band Name": "TV Channel 43", "Start MHz": 644, "Stop MHz": 650},
    {"Band Name": "TV Channel 44", "Start MHz": 650, "Stop MHz": 656},
    {"Band Name": "TV Channel 45", "Start MHz": 656, "Stop MHz": 662},
    {"Band Name": "TV Channel 46", "Start MHz": 662, "Stop MHz": 668},
    {"Band Name": "TV Channel 47", "Start MHz": 668, "Stop MHz": 674},
    {"Band Name": "TV Channel 48", "Start MHz": 674, "Stop MHz": 680},
    {"Band Name": "TV Channel 49", "Start MHz": 680, "Stop MHz": 686},
    {"Band Name": "TV Channel 50", "Start MHz": 686, "Stop MHz": 692},
    {"Band Name": "TV Channel 51", "Start MHz": 692, "Stop MHz": 698},
]

EU_TV_BAND_MARKERS = [
    {"Band Name": "TV Channel E5", "Start MHz": 174, "Stop MHz": 181},
    {"Band Name": "TV Channel E6", "Start MHz": 181, "Stop MHz": 188},
    {"Band Name": "TV Channel E7", "Start MHz": 188, "Stop MHz": 195},
    {"Band Name": "TV Channel E8", "Start MHz": 195, "Stop MHz": 202},
    {"Band Name": "TV Channel E9", "Start MHz": 202, "Stop MHz": 209},
    {"Band Name": "TV Channel E10", "Start MHz": 209, "Stop MHz": 216},
    {"Band Name": "TV Channel E21", "Start MHz": 470, "Stop MHz": 478},
    {"Band Name": "TV Channel E22", "Start MHz": 478, "Stop MHz": 486},
    {"Band Name": "TV Channel E23", "Start MHz": 486, "Stop MHz": 494},
    {"Band Name": "TV Channel E24", "Start MHz": 494, "Stop MHz": 502},
    {"Band Name": "TV Channel E25", "Start MHz": 502, "Stop MHz": 510},
    {"Band Name": "TV Channel E26", "Start MHz": 510, "Stop MHz": 518},
    {"Band Name": "TV Channel E27", "Start MHz": 518, "Stop MHz": 526},
    {"Band Name": "TV Channel E28", "Start MHz": 526, "Stop MHz": 534},
    {"Band Name": "TV Channel E29", "Start MHz": 534, "Stop MHz": 542},
    {"Band Name": "TV Channel E30", "Start MHz": 542, "Stop MHz": 550},
    {"Band Name": "TV Channel E31", "Start MHz": 550, "Stop MHz": 558},
    {"Band Name": "TV Channel E32", "Start MHz": 558, "Stop MHz": 566},
    {"Band Name": "TV Channel E33", "Start MHz": 566, "Stop MHz": 574},
    {"Band Name": "TV Channel E34", "Start MHz": 574, "Stop MHz": 582},
    {"Band Name": "TV Channel E35", "Start MHz": 582, "Stop MHz": 590},
    {"Band Name": "TV Channel E36", "Start MHz": 590, "Stop MHz": 598},
    {"Band Name": "TV Channel E37", "Start MHz": 598, "Stop MHz": 606},
    {"Band Name": "TV Channel E38", "Start MHz": 606, "Stop MHz": 614},
    {"Band Name": "TV Channel E39", "Start MHz": 614, "Stop MHz": 622},
    {"Band Name": "TV Channel E40", "Start MHz": 622, "Stop MHz": 630},
    {"Band Name": "TV Channel E41", "Start MHz": 630, "Stop MHz": 638},
    {"Band Name": "TV Channel E42", "Start MHz": 638, "Stop MHz": 646},
    {"Band Name": "TV Channel E43", "Start MHz": 646, "Stop MHz": 654},
    {"Band Name": "TV Channel E44", "Start MHz": 654, "Stop MHz": 662},
    {"Band Name": "TV Channel E45", "Start MHz": 662, "Stop MHz": 670},
    {"Band Name": "TV Channel E46", "Start MHz": 670, "Stop MHz": 678},
    {"Band Name": "TV Channel E47", "Start MHz": 678, "Stop MHz": 686},
    {"Band Name": "TV Channel E48", "Start MHz": 686, "Stop MHz": 694},
]

# Common Resolution Bandwidth (RBW) options in Hz
RBW_OPTIONS = [10, 100, 1000, 3000, 10000, 30000, 100000, 300000, 1000000, 3000000]

# Common Video Bandwidth (VBW) to Resolution Bandwidth (RBW) ratio options
VBW_RBW_RATIO_OPTIONS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10]

# Default Reference Level options in dBm
DEFAULT_REF_LEVEL_OPTIONS = [-100, -90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30]

# Default Frequency Shift options in Hz
DEFAULT_FREQ_SHIFT_OPTIONS = [0, 1000000, 2000000, 5000000, 10000000] # Example shifts

# Government/Commercial Plot Band Markers (for plotting)
# This list is used by the plotting functions to overlay visual markers
# on the spectrum plots for various government and commercial frequency allocations.
# Each dictionary contains:
# - "Band Name": A human-readable name for the band (e.g., "Public Safety 700 MHz").
# - "Start MHz": The starting frequency of the band in Megahertz.
# - "Stop MHz": The stopping frequency of the band in Megahertz.
GOV_PLOT_BAND_MARKERS = [
    {"Band Name": "Amateur Radio 6m", "Start MHz": 50, "Stop MHz": 54},
    {"Band Name": "FM Broadcast", "Start MHz": 88, "Stop MHz": 108},
    {"Band Name": "Air Traffic Control", "Start MHz": 108, "Stop MHz": 137},
    {"Band Name": "VHF Marine Radio", "Start MHz": 156, "Stop MHz": 162.025},
    {"Band Name": "Amateur Radio 2m", "Start MHz": 144, "Stop MHz": 148},
    {"Band Name": "Paging/Land Mobile", "Start MHz": 150, "Stop MHz": 174},
    {"Band Name": "Public Safety/Land Mobile", "Start MHz": 450, "Stop MHz": 470},
    {"Band Name": "Amateur Radio 70cm", "Start MHz": 420, "Stop MHz": 450},
    {"Band Name": "FRS/GMRS", "Start MHz": 462.5, "Stop MHz": 467.7625},
    {"Band Name": "LTE Band 13 (Uplink)", "Start MHz": 777, "Stop MHz": 787},
    {"Band Name": "LTE Band 13 (Downlink)", "Start MHz": 746, "Stop MHz": 756},
    {"Band Name": "Public Safety 700 MHz", "Start MHz": 764, "Stop MHz": 776},
    {"Band Name": "Public Safety 800 MHz", "Start MHz": 851, "Stop MHz": 869},
    {"Band Name": "LTE Band 5 (Uplink)", "Start MHz": 824, "Stop MHz": 849},
    {"Band Name": "LTE Band 5 (Downlink)", "Start MHz": 869, "Stop MHz": 894},
    {"Band Name": "GSM 850 (Uplink)", "Start MHz": 824, "Stop MHz": 849},
    {"Band Name": "GSM 850 (Downlink)", "Start MHz": 869, "Stop MHz": 894},
    {"Band Name": "Amateur Radio 33cm", "Start MHz": 902, "Stop MHz": 928},
    {"Band Name": "ISM 900 MHz", "Start MHz": 902, "Stop MHz": 928},
    {"Band Name": "LTE Band 2/25 (Uplink)", "Start MHz": 1850, "Stop MHz": 1915},
    {"Band Name": "LTE Band 2/25 (Downlink)", "Start MHz": 1930, "Stop MHz": 1995},
    {"Band Name": "PCS (Uplink)", "Start MHz": 1850, "Stop MHz": 1910},
    {"Band Name": "PCS (Downlink)", "Start MHz": 1930, "Stop MHz": 1990},
    {"Band Name": "LTE Band 4 (Uplink)", "Start MHz": 1710, "Stop MHz": 1755},
    {"Band Name": "LTE Band 4 (Downlink)", "Start MHz": 2110, "Stop MHz": 2155},
    {"Band Name": "AWS-1 (Uplink)", "Start MHz": 1710, "Stop MHz": 1755},
    {"Band Name": "AWS-1 (Downlink)", "Start MHz": 2110, "Stop MHz": 2155},
    {"Band Name": "Amateur Radio 23cm", "Start MHz": 1240, "Stop MHz": 1300},
    {"Band Name": "GPS L1", "Start MHz": 1575.42, "Stop MHz": 1575.42}, # Specific frequency
    {"Band Name": "GPS L2", "Start MHz": 1227.60, "Stop MHz": 1227.60}, # Specific frequency
    {"Band Name": "Bluetooth", "Start MHz": 2400, "Stop MHz": 2483.5},
    {"Band Name": "Wi-Fi 2.4 GHz", "Start MHz": 2400, "Stop MHz": 2483.5},
    {"Band Name": "ISM 2.4 GHz", "Start MHz": 2400, "Stop MHz": 2500},
    {"Band Name": "LTE Band 7 (Uplink)", "Start MHz": 2500, "Stop MHz": 2570},
    {"Band Name": "LTE Band 7 (Downlink)", "Start MHz": 2620, "Stop MHz": 2690},
    {"Band Name": "Amateur Radio 13cm", "Start MHz": 2300, "Stop MHz": 2450},
    {"Band Name": "Amateur Radio 13cm (cont)", "Start MHz": 2400, "Stop MHz": 2450}, # Overlap with ISM
]
