# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# py2exeSetup.py
# Written by Ruedi Eder and Chris Lewis
# ---------------------------------------------------------------------------
# This packs the client into a single win32 executable.
#      options = {"py2exe": {"compressed": 1,
#                          "optimize": 2,
#                          "bundle_files": 1}},
# ---------------------------------------------------------------------------
from distutils.core import setup
import py2exe

import anwp.func.funcs
import anwp.func.globals

# create list of all files in directories:
soundFiles = list(anwp.func.funcs.all_files('../Client/sounds/', '*.wav;*.ogg'))
imageFiles = list(anwp.func.funcs.all_files('../Client/images', '*.png'))
simsFiles = list(anwp.func.funcs.all_files('../Packages/anwp/sims', '*.py'))
fontFiles = list(anwp.func.funcs.all_files('../Client/fonts', '*.ttf'))
cursorFiles = list(anwp.func.funcs.all_files('../Packages/pyui/images', '*.png'))
shipBattleFiles = list(anwp.func.funcs.all_files('../Database', '*.ship'))

setup( 
      options = {'py2exe': {'includes': 'anwp.client.*, anwp.func.*, anwp.gui.*, anwp.modes.*, anwp.sims.*, anwp.sl.*, anwp.war.*'}}, 
      version = anwp.func.globals.currentVersion, 
      description = 'Armada Net Wars Client', 
      name = 'ANW Client', 
      #zipfile = None,
      console=['../Client/run.py'], 
      data_files=[( '../Database', shipBattleFiles),
                  ( 'images', imageFiles),
                  ( 'sounds', soundFiles),
                  ( '../Packages/anwp/sims', simsFiles),
                  ( 'fonts', fontFiles),
                  ( '', ['../Client/connect.ini']),
                  ( '', cursorFiles),
                  ( '', ['../Client/client.data']),
                  ( 'sims/images', [])
                  ]
    )
#help(py2exe)



