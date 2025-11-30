# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

hidden_imports = [
    'numpy',
    'pandas',
    'matplotlib',
    'PIL',
    'paho.mqtt.client',
    'pdfplumber',
    'bs4',
    'pyvisa',
    'usb.core',
    'usbtmc',
    'vxi11',
    'serial',
    'psutil',
    'zeroconf',
    'tkinter',
    'tkinter.ttk',
    'seaborn',
    'display.gui_display'
]
hidden_imports += collect_submodules('workers')
hidden_imports += collect_submodules('display')
hidden_imports += collect_submodules('datasets')
hidden_imports += collect_submodules('managers')


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('workers', 'workers'),
        ('display', 'display'),
        ('datasets', 'datasets'),
        ('managers', 'managers'),
        ('DATA', 'DATA'),
        ('/usr/share/tcltk/tcl8.6', 'tcl'),
        ('/usr/share/tcltk/tk8.6', 'tk')
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OPEN-AIR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)