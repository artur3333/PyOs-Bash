import os
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.datastruct import Tree

hidden_imports = ['shell', 'filesystem', 'auth','package_manager',
    'requests', 'ping3', 'cpuinfo', 'psutil'
]

datas = []
datas += collect_data_files('certifi')

a = Analysis(
    ['bootloader.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PyOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='pyos.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    Tree('assets', prefix='assets'),
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PyOS',
)
