# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# runTest.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is runs the main client in ANW
# ---------------------------------------------------------------------------
import os

import pyui
import anwp.client.app
import anwp.func.globals

def run(width, height, window, psyco, sound, server='http://localhost:8000',
        galaxy='', empire='', password=''):
    # Import Psyco if available
    if psyco:
        try:
            import psyco
            psyco.full()
        except ImportError:
            pass
    pyui.init(width, height, 'p3d', window, 'Armada Net Wars - version: %s' % anwp.func.globals.currentVersion)
    # read ini file for connection to server
    try:
        fileName = '%s/connect.ini' % os.getcwd()
        input = open(fileName, 'r')
        inputLines = [L.rstrip() for L in input]
        input.close()
    except:
        inputLines = ['http://localhost:8888']
    app = anwp.client.app.Application(width, height, inputLines, sound, server, galaxy, empire, password)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    run(1024, 768, 0, 0, 0)
