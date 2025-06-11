# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Student Database Management System
This file configures the build process for creating an executable
"""

import os
from PyInstaller.utils.hooks import collect_data_files

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))

# Define paths
src_path = os.path.join(project_root, 'src')
run_script = os.path.join(project_root, 'run.py')
icon_path = os.path.join(project_root, 'Student Database.ico')
data_dir = os.path.join(project_root, 'data')
assets_dir = os.path.join(project_root, 'src', 'assets')

# Collect data files
datas = []

# Add database file if it exists
db_file = os.path.join(data_dir, 'student_management_system.db')
if os.path.exists(db_file):
    datas.append((db_file, 'data'))

# Add assets directory (profile pictures and images)
if os.path.exists(assets_dir):
    datas.append((assets_dir, 'src/assets'))

# Add matplotlib data files
datas += collect_data_files('matplotlib')

# Add ttkbootstrap themes
try:
    datas += collect_data_files('ttkbootstrap')
except:
    pass

a = Analysis(
    [run_script],
    pathex=[project_root, src_path],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'sqlite3',
        'matplotlib.backends.backend_tkagg',
        'ttkbootstrap',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.platypus',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Student Database Management System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
)
