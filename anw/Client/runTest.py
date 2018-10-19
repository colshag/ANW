# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# runTest.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is runs the main client in ANW
# ---------------------------------------------------------------------------
import os

from anw.client.directapp import DirectApplication

def runMe(sound=0, psyco=0, server='http://localhost:8000',
          galaxy='ANW1', empire='1', password='pass1'):
    
    if psyco:
        try:
            import psyco
            psyco.full()
        except ImportError:
            pass
    
    app = DirectApplication(sound, server, galaxy, empire, password)
    app.loadGame()
    run()
    
if __name__ == '__main__':
    runMe()
