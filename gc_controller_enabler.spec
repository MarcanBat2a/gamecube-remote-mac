# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

icon_file = 'controller.icns'
console = False

block_cipher = None

# Collect all customtkinter submodules + data files (themes, fonts, icons).
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")

# Collect pystray and its dependencies
pystray_datas, pystray_binaries, pystray_hiddenimports = collect_all("pystray")

# Data files to include
datas = ctk_datas + pystray_datas
binaries = ctk_binaries + pystray_binaries
if os.path.exists(os.path.join('images', 'controller.png')):
    datas.append((os.path.join('images', 'controller.png'), '.'))
if os.path.exists(os.path.join('images', 'stick_left.png')):
    datas.append((os.path.join('images', 'stick_left.png'), '.'))
if os.path.exists(os.path.join('images', 'stick_right.png')):
    datas.append((os.path.join('images', 'stick_right.png'), '.'))

# Window/taskbar icon (bundled into _MEIPASS root for runtime use)
if os.path.exists('controller.png'):
    datas.append(('controller.png', '.'))

# Bundled font
_font_path = os.path.join('src', 'gc_controller', 'fonts', 'VarelaRound-Regular.ttf')
if os.path.exists(_font_path):
    datas.append((_font_path, os.path.join('gc_controller', 'fonts')))

# Bundled controller PNG assets
_assets_dir = os.path.join('src', 'gc_controller', 'assets', 'controller')
if os.path.isdir(_assets_dir):
    for f in os.listdir(_assets_dir):
        if f.endswith('.png'):
            datas.append((os.path.join(_assets_dir, f),
                          os.path.join('gc_controller', 'assets', 'controller')))

# Hidden imports for libraries that might not be detected
hiddenimports = [
    'hid',
    'usb.core',
    'usb.util',
    'gc_controller.virtual_gamepad',
    'gc_controller.controller_constants',
    'gc_controller.settings_manager',
    'gc_controller.calibration',
    'gc_controller.connection_manager',
    'gc_controller.emulation_manager',
    'gc_controller.controller_ui',
    'gc_controller.input_processor',
    'tkinter',
    'tkinter.ttk',
    '_tkinter',
    'PIL._tkinter_finder',
    # pystray — dynamic backend selection requires explicit imports
    'pystray',
    'pystray._base',
    'pystray._util',
    'six',
    # BLE (Bleak + CoreBluetooth)
    'bleak',
    'gc_controller.ble',
    'gc_controller.ble.bleak_backend',
    'gc_controller.ble.bleak_subprocess',
    'gc_controller.ble.sw2_protocol',
    # pystray macOS backend (requires pyobjc-framework-Cocoa)
    'pystray._darwin',
    'AppKit',
    'Foundation',
    'objc',
    'PyObjCTools',
    'PyObjCTools.MachSignals',
] + ctk_hiddenimports + pystray_hiddenimports

a = Analysis(
    ['src/gc_controller/__main__.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='NSO-GameCube-Controller-Pairing-App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if icon_file and os.path.exists(icon_file) else None,
)

# Create macOS app bundle
app = BUNDLE(
    exe,
    name='NSO-GameCube-Controller-Pairing-App.app',
    icon=icon_file if icon_file and os.path.exists(icon_file) else None,
    bundle_identifier='com.nso.gamecube-controller-pairing-app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
        'NSRequiresAquaSystemAppearance': False,
    },
)
