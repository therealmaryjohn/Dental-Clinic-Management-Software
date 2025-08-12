# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\ajohn34\\PycharmProjects\\Pilot_Project'],
    binaries=[],
    datas=[
        ('assets\\*', 'assets'),
        ('database\\*', 'database'),
        ('Invoice\\*', 'Invoice'),
        ('modules\\*', 'modules'),
        ('Reports\\*', 'Reports'),
        ('settings\\*', 'settings'),
        ('Support\\*', 'Support'),
        ('templates\\*', 'templates'),
        ('ui\\*', 'ui'),
        ('utils\\*', 'utils'),
        ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a terminal window
    icon=r'C:\Users\ajohn34\PycharmProjects\Pilot_Project\Support\DNS.ico',  # Replace with your actual icon file name
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
