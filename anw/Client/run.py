# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# run.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is runs the main client in ANW
# ---------------------------------------------------------------------------
import os
import sys
sys.path.append(os.path.join("..", "Packages"))
import time
from anw.admin import generate
import argparse
import fnmatch
import logging
from multiprocessing import Process, Queue
import ConfigParser
from anw.func import funcs

from pandac.PandaModules import *


from servermain import serverMain
from anw.func import storedata, globals

class ANWRunner(object):
    def __init__(self, singlePlayer=True, startSinglePlayerServer=True, remoteServer=None, serverPort=8000, galaxy='ANW1', empire=1, password=None, sound=True, fullscreen=False, resolution="1280x1024", mapfile="testai2man.map"):
        self.singlePlayer = singlePlayer
        self.startSinglePlayerServer = startSinglePlayerServer
        self.remoteServer = remoteServer
        self.serverPort = serverPort
        self.galaxy = galaxy
        self.empire = empire
        self.password = password
        self.sound = sound
        self.fullscreen = fullscreen
        self.resolution = resolution
        self.mapfile = mapfile

    def performSinglePlayerSetup(self):
        process = None
        serverCommQueue = None
        if self.singlePlayer and self.startSinglePlayerServer:
            logging.info("Running in single player mode. Generate map if required.")
            self.generateSinglePlayer()

            serverCommQueue = Queue()
            logging.info("Starting server process")
            process = Process(target=serverMain, args=(serverCommQueue, self.singlePlayer, self.galaxy))
            process.start()
            logging.info("Waiting for server startup...")
            result = serverCommQueue.get(timeout=60)
            if result == "server ready":
                logging.info("Server startup complete.")
            else:
                logging.error("Failed to start server... {}".format(result))
                sys.exit(1)
        return process, serverCommQueue

    def cleanupSinglePlayer(self, process, serverCommQueue):
        if self.singlePlayer and self.startSinglePlayerServer:
            serverCommQueue.put("shutdown")
            process.join()
            logging.info("Server shutdown. exiting")

    def start(self):
        if self.serverPort is None:
            # singlePlayer
            process, serverCommQueue = self.performSinglePlayerSetup()
            try:
                    self.__runANW()
            finally:
                logging.info("Sending shutdown signal to server")
                self.cleanupSinglePlayer(process, serverCommQueue)
        else:
            # multiplayer
            galaxy = 0
            galaxy = self.generateMultiplayer()
            serverMain(None, self.singlePlayer, database=self.galaxy, port=self.serverPort, firsttime=galaxy )

    def generateSinglePlayer(self):
        absDataPath = os.path.abspath(os.path.join(os.path.join("..", "Data")))
        if os.path.isdir(os.path.join("..", "Database", self.galaxy)):
            logging.info("Database directory already exists")
            return
        os.makedirs(os.path.join("..", "Database", self.galaxy))
        generateGalaxy = generate.GenerateGalaxy()
        generateGalaxy.genGalaxy(dataPath = absDataPath + "/", starMapFile=self.mapfile, playerList = ['singleplayer'], doAI = 1, galaxyName = self.galaxy)
        workingGalaxy = generateGalaxy.getGalaxy()

        storedata.saveToFile(workingGalaxy, os.path.join("..", "Database", self.galaxy, self.galaxy + ".anw"))

        return self.galaxy

    def generateMultiplayer(self):
        logging.info("Running in multiplayer mode. Generate map if required.")
        absDataPath = os.path.abspath(os.path.join(os.path.join("..", "Data")))
        if os.path.isdir(os.path.join("..", "Database", self.galaxy)):
            logging.info("Database directory already exists")
            return
        if self.mapfile == "":
            logging.info("No mapfile provided in arguments")
            return
        setupFile = "%s-setup.txt" % self.galaxy
        if os.path.isdir(setupFile):
            logging.info("Please create a player list to create game: %s" % setupFile)
            return        
        myPlayerList = [line.rstrip('\n') for line in open(setupFile)]
        logging.info("Generate new Galaxy instance since none detected.")
        os.makedirs(os.path.join("..", "Database", self.galaxy))
        generateGalaxy = generate.GenerateGalaxy()
        generateGalaxy.genGalaxy(dataPath = absDataPath + "/", starMapFile=self.mapfile, playerList = myPlayerList, doAI = 1, galaxyName = self.galaxy, serverPort=self.serverPort)
        workingGalaxy = generateGalaxy.getGalaxy()

        storedata.saveToFile(workingGalaxy, os.path.join("..", "Database", self.galaxy, self.galaxy + ".anw"))

        return self.galaxy

    def loadConfigFromProfile(self, profile, configSection = "CosmicaServer"):
        """
        profile name.  This will be in $HOME/.anw/<profile>.config
        will work for both profile and /path/to/profile arguments
        """

        if os.path.isfile(profile):
            print "found file", profile, "using it as config.  If you entended to use a profile make sure the name doesn't match a relative path"
            profilepath = profile
        else:
            if not profile.endswith(".config"):
                profile += ".config"
            # expand to full path, cross platform
            # from http://ubuntuforums.org/showthread.php?t=820043&page=2
            profilepath = os.path.expanduser(os.path.join("~",".anw",profile))

        # redundant if they passed the actual path to a config file, but check anyway since we expand the path if it was a profile name
        if not os.path.isfile(profilepath):
            print "Could not find profile", profile, "at path", profilepath
            sys.exit()

        parser = ConfigParser.RawConfigParser()
        parser.read(profilepath)
        config = {}
        config['server'] = parser.get(configSection, "server")
        config['galaxy'] = parser.get(configSection, "galaxy")
        config['empire'] = parser.get(configSection, "empire")
        # TODO must be a better way to pass the password into the application??
        config['password'] = parser.get(configSection, "password")
        config['sound'] = parser.get(configSection, "sound") in ("True", "true", "1", "yes")
        config['fullscreen'] = parser.get(configSection, "fullscreen") in ("True", "true", "1", "yes")
        config['resolution'] = parser.get(configSection, "resolution")

        return config

    def __runANW(self):
        from anw.client.directapp import DirectApplication
        wp = WindowProperties()
        x, y = self.resolution.split("x")
        wp.setSize(int(x), int(y)) # there will be more resolutions
        wp.setFullscreen(bool(self.fullscreen))
        base.win.requestProperties(wp)
        self.app = DirectApplication(self.sound, self.remoteServer, self.galaxy, self.empire, self.password)
        self.app.loadGame()
        self.mainloop()

    def mainloop(self):
        while not self.app.shutdownFlag.is_set():
            taskMgr.step()

def getMapList():
    files = os.listdir(absDataPath)
    match = fnmatch.filter(files, "*.map")
    return match

if __name__ == '__main__':

    absDataPath = os.path.abspath(os.path.join(os.path.join("..", "Data")))
    parser = argparse.ArgumentParser()

    parser.add_argument("--galaxy", "-g", default='ANW1', help="galaxy name to use to. eg. ANW1. Default: ANW1")
    parser.add_argument("--empireid", "-e", default=1, help="empire id to play in galaxy", type=int)
    parser.add_argument("--empirepass", "-p", default="singleplayer", help="password for connecting to remote server")
    parser.add_argument("--remoteserver", "-s", default="http://localhost:8000", help="server URL to play game")
    parser.add_argument("--disableSound", "-d", action="store_true", default=False, help="Disable audio")
    parser.add_argument("--resolution", "-r", default="1280x1024", help="Resolution game window runs at", type=str)
    parser.add_argument("--fullscreen", "-f", action="store_true", default=False, help="Set game window to fullscreen")
    parser.add_argument("--server", metavar="port", default=None, help="Turns into standalone server. Listens on defined port", type=int)
    parser.add_argument("--clientonly", action="store_true", default=False)
    parser.add_argument('--map', '-m', metavar="MAPFILE", type=str, default="testai2man.map", choices=getMapList(), help="MAPFILE can be one of {}".format(getMapList()))
    args = parser.parse_args()

    runner = ANWRunner(singlePlayer=not args.server, startSinglePlayerServer=not args.clientonly, remoteServer=args.remoteserver, galaxy=args.galaxy, empire=args.empireid, password=args.empirepass, sound=not args.disableSound,fullscreen=args.fullscreen, resolution=args.resolution, serverPort=args.server, mapfile=args.map)
    runner.start()


