# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None
current_dir = os.path.abspath(os.path.dirname(SPEC)) if 'SPEC' in globals() else os.path.abspath(os.getcwd())

datas = [
    (os.path.join(current_dir, 'gui'), 'gui'),
    (os.path.join(current_dir, 'app_icon.ico'), '.')
]

version_file = os.path.join(current_dir, 'version_info.txt') if (sys.platform == 'win32' and os.path.exists(os.path.join(current_dir, 'version_info.txt'))) else None
icon_file = os.path.join(current_dir, 'app_icon.ico')

a = Analysis(
    ['app.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=['webview', 'pystray', 'PIL', 'aiohttp', 'websockets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='QueueJoiner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_file,
    icon=icon_file if os.path.exists(icon_file) else None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='QueueJoiner.app',
        icon=icon_file if os.path.exists(icon_file) else None,
        bundle_identifier='com.queuejoiner.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
        }
    )
