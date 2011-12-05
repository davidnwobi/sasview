"""
This is a setup.py script partly generated by py2applet

Usage:
    python setup.py py2app
    
    
NOTES:
   12/01/2011: When seeing an error related to pytz.zoneinfo not being found, change the following line in py2app/recipes/matplotlib.py
               mf.import_hook('pytz.tzinfo', m, ['UTC'])
   12/05/2011: Generally needs a recent version of macholib, modulegraph, and altgraph (through easy_install) on OSX >= 10.6
"""
from setuptools import setup
import periodictable.xsf
import sans.dataloader.readers 
from distutils.sysconfig import get_python_lib
import os
import string
import local_config
import pytz
import sys
import platform

ICON = local_config.SetupIconFile_mac
EXTENSIONS_LIST = []
DATA_FILES = []
RESOURCES_FILES = []

#Periodictable data file
DATA_FILES = periodictable.data_files()
#invariant and calculator help doc
import sans.perspectives.fitting as fitting
DATA_FILES += fitting.data_files()
import sans.perspectives.calculator as calculator
DATA_FILES += calculator.data_files()
import sans.perspectives.invariant as invariant
DATA_FILES += invariant.data_files()
import sans.models as models
DATA_FILES += models.data_files()
import sans.guiframe as guiframe
DATA_FILES += guiframe.data_files()

#CANSAxml reader data files
RESOURCES_FILES.append(os.path.join(sans.dataloader.readers.get_data_path(),'defaults.xml'))

# Locate libxml2 library
lib_locs = ['/usr/local/lib', '/usr/lib']
libxml_path = None
for item in lib_locs:
    libxml_path_test = '%s/libxml2.2.dylib' % item
    if os.path.isfile(libxml_path_test): 
        libxml_path = libxml_path_test
if libxml_path == None:
    raise RuntimeError, "Could not find libxml2 on the system"

APP = ['sansview.py']
DATA_FILES += ['images','test','plugins','media', 'custom_config.py', 'local_config.py']
# locate file extensions
def find_extension():
    """
    Describe the extensions that can be read by the current application
    """
    try:
        list = []
        EXCEPTION_LIST = ['*', '.', '']
        from sans.dataloader.loader import Loader
        wild_cards = Loader().get_wildcards()
        for item in wild_cards:
            #['All (*.*)|*.*']
            file_type, ext = string.split(item, "|*.", 1)
            if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
                list.append(ext)
    except:
        print sys.exc_value
        
    try:
        file_type, ext = string.split(local_config.APPLICATION_WLIST, "|*.", 1)
        if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
            list.append(ext)
    except:
        print sys.exc_value
        
    try:
        for item in local_config.PLUGINS_WLIST:
            file_type, ext = string.split(item, "|*.", 1)
            if ext.strip() not in EXCEPTION_LIST and ext.strip() not in list:
                list.append(ext) 
    except:
        print sys.exc_value
    
    return list

EXTENSIONS_LIST = find_extension()

 
plist = dict(CFBundleDocumentTypes=[dict(CFBundleTypeExtensions=EXTENSIONS_LIST,
                                         CFBundleTypeIconFile=ICON,
                                   CFBundleTypeName="sansview file",
                                   CFBundleTypeRole="Shell" )],)

APP = ['sansview.py']
DATA_FILES += ['images','test','plugins','media']

EXCLUDES = ['PyQt4', 'sip', 'QtGui']

OPTIONS = {'packages': ['lxml','numpy', 'scipy', 'pytz', 'encodings'],
           'iconfile': ICON,
           'frameworks':[libxml_path],
           'resources': RESOURCES_FILES,
           'plist':plist,
           'excludes' : EXCLUDES,
           }

# Cross-platform applications generally expect sys.argv to
# be used for opening files. This requires argv_emulation = True
# ---> argv_emulation is not supported for 64-bit apps
print platform.architecture()[0]
if not platform.architecture()[0] == '64bit':
    OPTIONS['argv-emulation'] = True
else:
    OPTIONS['argv-emulation'] = False
    
setup(
    app=APP,
    data_files=DATA_FILES,
    include_package_data= True,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
