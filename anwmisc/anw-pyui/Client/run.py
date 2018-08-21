# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# run.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is runs the main client in ANW
# ---------------------------------------------------------------------------
# the following PIL plugins are imported to accomdate py2exe ##
import Image
import ImageOps
import ImagePalette
import BmpImagePlugin
import GifImagePlugin
import ImageFile
import JpegImagePlugin
import PngImagePlugin
import PpmImagePlugin
import TiffImagePlugin
################################################################
import os
import sys

import pyui
import anwp.client.app
import anwp.func.globals

def run(width, height, window, psyco, sound, server, galaxy, empire, password=''):
    # Import Psyco if available
    if psyco:
        try:
            import psyco
            psyco.full()
            print "psyco loaded"
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
    from optparse import OptionParser
    from optparse import Option
    parser = OptionParser(option_list=[Option("-x", dest="width", default=1024),
                                       Option("-y", dest="height", default=768),
                                       Option("-f", dest="fullscreen", default=0),
                                       Option("-p", dest="psyco", default=1),
                                       Option("-r", dest="resolution", default=""),
                                       Option("-o", dest="sound", default=1),
                                       Option("-s", dest="server", default=""),
                                       Option("-g", dest="galaxy", default=""),
                                       Option("-e", dest="empire", default=""),
                                       Option("-w", dest="password", default="")])
    (options, args) = parser.parse_args()
    print "opts:",options.width, options.height, options.fullscreen, options.psyco, options.resolution, options.sound

    # I wanted a way to set the screen size based on a 1280x1024 type string.
    # this allows the linux start shell script to not have to do as much work.
    if options.resolution != "":
        res = options.resolution.split("x")
        try:
            options.width = int(res[0])
            options.height = int(res[1])
        except:
            print "Invalid resolution specified [" + options.resolution +"]. Should be in the format  '1280x1024'"
            sys.exit()

    """
    import profile
    profile.run('run(int(options.width), int(options.height), int(options.fullscreen), int(options.psyco),int(options.sound), options.server, options.galaxy, options.empire, options.password)')
    """

    run(int(options.width), int(options.height), int(options.fullscreen), int(options.psyco),
        int(options.sound), options.server, options.galaxy, options.empire, options.password)
