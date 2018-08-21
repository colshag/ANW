import sys
import os
sys.path.append(os.path.join("..", "Packages"))

import glob
import argparse
import fnmatch
import getpass
from anw.util.Injection import Services
from anw.admin import generate
from anw.func import storedata, globals
from anw.gae.access import GAE, LocalGAE

absDataPath = os.path.abspath(os.path.join(os.path.join("..", "Data")))

def getMapList():
    files = os.listdir(absDataPath)
    match = fnmatch.filter(files, "*.map")
    return match

def startGame(args):
    for user in args.users:
        if not Services.inject(GAE).isValidEmailOrUserId(user):
            raise Exception("User {} is invalid".format(user))

    gameName = Services.inject(GAE).createNewGame(args.address, args.users)
    os.makedirs(os.path.join("..", "Database", gameName))

    generateGalaxy = generate.GenerateGalaxy()
    generateGalaxy.genGalaxy(dataPath = absDataPath + "/", starMapFile=args.map, playerList = args.users, doAI = 1, galaxyName = gameName)
    workingGalaxy = generateGalaxy.getGalaxy()

    storedata.saveToFile(workingGalaxy, os.path.join("..", "Database", gameName, gameName + ".anw"))

    return gameName


def getArguments():
    parser = argparse.ArgumentParser(description="ANW Server Wizard")
    parser.add_argument('--user', '-u', dest="users", metavar="USER", type=str, nargs='+', required=True, help="Provide a list of users that should be in the game")
    parser.add_argument('--randomizeusers', '-r', action="store_true", default=False, help="Randomize the list of provided users")
    parser.add_argument('--map', '-m', metavar="MAPFILE", type=str, required=True, choices=getMapList(), help="MAPFILE can be one of {}".format(getMapList()))
    parser.add_argument('--localMode', '-l', dest="localmode", action="store_true", default=False, help="Local App Engine for testing")
    parser.add_argument("--serveruser", dest="serveruser", metavar="USERNAME", required=True, help="The username of the person running the server. This doesn't need to be a player")
    parser.add_argument("--serverpass", dest="serverpass", metavar="PASSWORD", help="This parameter will be prompted for if not specifiedxs")
    parser.add_argument("--address", dest="address", default="http://localhost:8000", help="The publicly available address the server will be accessible at. Defaults to http://localhost:8000. Careful! This is the address your players will connect to. Make sure it is valid. You can't change it later!")
    return parser.parse_args()
    
def setupDepenencyInjection(localgae=0, serveruser="required", serverpass="required"):
    """ Register all object implementations up front """
    if localgae:
        print("Using local GAE")
        Services.register(GAE, LocalGAE)
    else:
        Services.register(GAE)
    Services.inject(GAE).username = serveruser
    Services.inject(GAE).password = serverpass     
    
args = getArguments()

if args.serverpass is None:
    args.serverpass = getpass.getpass("Enter server admin password: ")

setupDepenencyInjection(localgae=args.localmode, serveruser=args.serveruser, serverpass=args.serverpass)

gameName = startGame(args)

print("Game {} generated.  Now run the server.".format(gameName))
