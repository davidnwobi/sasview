# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import warnings
import platform
import sys

block_cipher = None
PYTHON_LOC = sys.exec_prefix

datas = [
    ('../src/sas/sasview/images', 'images'),
    ('../src/sas/sasview/media', 'media'),
    ('../src/sas/sasview/test', 'test'),
    ('../src/sas/sasview/custom_config.py', '.'),
    ('../src/sas/sasview/local_config.py', '.'),
    ('../src/sas/sasview/wxcruft.py', '.'),
    ('../src/sas/qtgui/Perspectives/Fitting/plugin_models', 'plugin_models'),
    ('../src/sas/logger_config.py', '.'),
    ('../src/sas/logging.ini', '.'),
    ('../../sasmodels/sasmodels','sasmodels'),
]
#TODO: Hopefully we can get away from here
if platform.system() == 'Darwin':
    datas.append((os.path.join(PYTHON_LOC,'lib','python3.8', 'site-packages','jedi'),'jedi'))
    datas.append((os.path.join(PYTHON_LOC,'lib','python3.8', 'site-packages','zmq'),'.'))
    datas.append((os.path.join(PYTHON_LOC,'lib','python3.8', 'site-packages','debugpy'),'debugpy'))
else:
    (os.path.join(PYTHON_LOC,'Lib','site-packages','debugpy'),'debugpy'),

def add_data(data):
    for component in data:
        target = component[0]
        for filename in component[1]:
           datas.append((filename, target))

import sasmodels
add_data(sasmodels.data_files())

try:
    import tinycc
    add_data(tinycc.data_files())
except ImportError:
    warnings.warn("TinyCC package is not available and will not be included")

import periodictable
add_data(periodictable.data_files())

hiddenimports = [
    'sas.sascalc.dataloader.readers.abs_reader',
    'sas.sascalc.dataloader.readers.anton_paar_saxs_reader',
    'sas.sascalc.dataloader.readers.ascii_reader',
    'sas.sascalc.dataloader.readers.cansas_reader_HDF5',
    'sas.sascalc.dataloader.readers.cansas_reader',
    'sas.sascalc.dataloader.readers.danse_reader',
    'sas.sascalc.dataloader.readers.red2d_reader',
    'sas.sascalc.dataloader.readers.sesans_reader',
    'sas.sascalc.dataloader.readers.tiff_reader',
    'sas.sascalc.dataloader.readers.xml_reader',
    #'PyQt5',
    #'periodictable.core',
    #'sasmodels.core',
    'pyopencl',
    #'tinycc',
    #'SocketServer',
    #'logging',
    #'logging.config',
    'reportlab',
    'reportlab.graphics',
    'reportlab.graphics.barcode.common',
    'reportlab.graphics.barcode.code128',
    'reportlab.graphics.barcode.code93',
    'reportlab.graphics.barcode.code39',
    'reportlab.graphics.barcode.lto',
    'reportlab.graphics.barcode.qr',
    'reportlab.graphics.barcode.usps',
    'reportlab.graphics.barcode.usps4s',
    'reportlab.graphics.barcode.eanbc',
    'reportlab.graphics.barcode.ecc200datamatrix',
    'reportlab.graphics.barcode.fourstate',
    #'ipykernel',
    #'ipykernel.datapub',
    #'pygments',
    #'pygments.lexers',
    #'pygments.lexers.python',
    #'pygments.styles',
    #'pygments.styles.default',
    #'atexit', 'cython', 'sip', 'xhtml2pdf',
    #'zmq', 'zmq.utils', 'zmq.utils.strtypes',
    #'zmq.utils.jsonapi','zmq.utils.garbage',
    #'zmq.backend.cython','zmq.backend.cffi',
    #'site','lxml._elementpath','lxml.etree',
    #'scipy._lib.messagestream',
    #'numba',
    'xmlrpc',
    'xmlrpc.server',
    'debugpy',
    'debugpy._vendored',
    'uncertainties',
]

a = Analysis(
    ['sasview.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

if platform.system() == 'Darwin':
    exe = EXE(
          pyz,
          a.scripts,
          exclude_binaries=True,
          name='sasview',
          debug=False,
          upx=False,
          icon=os.path.join("../src/sas/sasview/images","ball.icns"),
          version="version.txt",
          console=False )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='sasview',
        debug=False,
        bootloader_ignore_signals=False,
        icon=os.path.join("../src/sas/sasview/images","ball.ico"),
        strip=False,
        upx=True,
        console=True)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='sasview'
)

if platform.system() == 'Darwin':
    app = BUNDLE(coll,
        name='SasView5.app',
        icon='../src/sas/sasview/images/ball.icns',
        bundle_identifier='org.sasview.SasView5',
        info_plist={'NSHighResolutionCapable': 'True'})
