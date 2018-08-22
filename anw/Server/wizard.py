import xmlrpclib
import time
#from anw.gae.access import GAE, LocalGAE
from anw.util.Injection import Services
from anw.admin import generate
from anw.func import storedata, globals
#from anw.menusystem import XMLMenuGenie
#from anw.menusystem import MenuSystem
import sys
import os
import glob
import re
import string
from random import shuffle
#import menusystem

class wzGame:
    """blah"""
    def __init__(self, name):
        #self._sighandler = signal.signal(signal.SIGINT, self.killnicely)

        self.name = name
        self.players = []
        self.mapfile = ""
        self.dataPath = ""
        self.s = xmlrpclib.Server('http://localhost:8090/xmlrpc')
        self.serverAddress = "http://localhost:8000"
        self.serveruser = ""
        self.serverpass = ""
        self.numHumans = 1
        self.serverversion = globals.currentVersionShort

    def printAll(self):
        print "*************Game Information**************"
        print "*** Game name:", self.name
        print "*** Map file:", self.dataPath, self.mapfile, " (with", self.numHumans, "human slots)"
        print "*** Server:", self.serverAddress, " Version:", self.serverversion
        print "*** Server user:", self.serveruser, "and pass: *****"
        print "*******************************************"

    def uploadGame(self):
        print self.serveruser, self.serverpass, self.serverAddress
        self.s.app.addNewServer(self.serveruser, self.serverpass, self.serverAddress)


def setupDepenencyInjection(localgae=0, serveruser="required", serverpass="required"):
    """ Register all object implementations up front """
    if localgae:
        Services.register(GAE, LocalGAE)
    else:
        Services.register(GAE)
    Services.inject(GAE).username = serveruser
    Services.inject(GAE).password = serverpass 

def testUserForGAEAccess():
    return Services.inject(GAE).isServerUserValid()

def printListNumbers(values):
    """Takes a list and prints it to stdout with numbers
    for picking an item"""
    column = 0
    colSize = 5
    list = iter(values)
    for number in range(1,len(values)+1):
        column += 1
        print '{0}) {1:10}'.format(number, list.next()),
        if (column == colSize):
            column = 0
            print 

def pickFromList(values, max, multiple=False):
    newList = []
    loop = True
    printListNumbers(values)
    total = 0
    while (loop):
        total += 1
        try:
            choice = raw_input("Please pick a number:")
            someVar = int(choice)
            print "Adding %s to the list" % (values[someVar-1])
            newList.append(values[someVar-1])
            if not multiple:
                loop = False
        except (TypeError, ValueError):
            loop = False
    return newList

def pick_map(gameObj):
    os.chdir(gameObj.dataPath)
    dirList = glob.glob('*.map')
    printListNumbers(dirList)

    filechoice = raw_input("\nWhich map file do you want?: ")
    templateFileName = '%s' % dirList[int(filechoice)-1]
    fullMapFilePath = '%s%s' % (gameObj.dataPath, templateFileName)
    print " You have selected %s \n" % (fullMapFilePath)

    #Import map file dictionary
    templateFilePath = os.path.normpath(gameObj.dataPath + "/" + templateFileName)
    myDict = {"__builtins__":None,
              "range" : range
              }
    execfile(templateFilePath, myDict)

    numEmpires = myDict['numEmpires'] - 1
    numHumans = int(numEmpires)

    gameObj.numHumans = numHumans
    gameObj.mapfile = templateFileName
    gameObj.printAll()

if __name__ == "__main__":

    from optparse import OptionParser
    from optparse import Option

    parser = OptionParser(option_list=[Option("-l", dest="localgae", default=0)])
    (options, args) = parser.parse_args()

    print"opts: Local = ", options.localgae

    localGAE = int(options.localgae)


    print "*********************************************"
    print "* Welcome to the ANW game creation wizard.  *"
    print "*********************************************\n\n"

    newgame = wzGame("unknown")

    path = os.path.abspath(sys.path[0])[:-6]
    dataPath = '%sData/' % path
    adminPath = '%sAdmin/' % path
    serverPath = '%sServer/' % path
    newgame.dataPath = dataPath

    if localGAE:
        s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
    else:
        s = xmlrpclib.Server('https://armadanetwars.appspot.com/xmlrpc/')

    #Ask for username and password of game creator
    newgame.serveruser = raw_input("Please enter your ANW Username: ")
    newgame.serverpass = raw_input("Please enter your ANW Password: ")

    setupDepenencyInjection(localgae=localGAE, serveruser=newgame.serveruser, serverpass=newgame.serverpass)

    gaeResult = testUserForGAEAccess()
#    #gaeResult = True
    if gaeResult == False:
        print "The configured server username does not have the permissions to administer a server"
        sys.exit(0)
    elif gaeResult == None:
        print "Could not contact Google App Engine"
        sys.exit(0)
    else:
        print "GAE credentials OK to start server"

    #Select a map  
    pick_map(newgame)
    print "The map file you have chosen allows for %i human players max" % newgame.numHumans


    #Select friends from file.
    if localGAE:
        friendFile = serverPath + "localfriends.txt"
    else:
        friendFile = serverPath + "friends.txt"

    playerList = []
    friendFileFound = False
    finalPlayerList = []
    try:
        ffile = open(friendFile, 'r')
        friendLine = ffile.readline()

        print "Friend file found with the following users: %s" %  friendLine
        yn = raw_input("Do you want to pick from these friends? Y/N")
        if yn.lower() == 'y':
            friendFileFound = True
            playerList = eval(friendLine)
            #printListNumbers(playerList)
            finalPlayerList = pickFromList(playerList,newgame.numHumans, multiple=True)
    except (IOError):
        print '   could not read friends.txt'

    yn = raw_input("Do you want to add players manually? Y/N [N]")
    if (yn.lower() == 'y'):
        playerName = ""
        loop = True
        while(loop):
            try:
                playerName = raw_input("Please enter a username to add:")
                if playerName == '' :
                    loop = False
                elif s.app.isValidEmailOrUserId(newgame.serveruser, newgame.serverpass, playerName):
                    print "Adding %s to the list" % (playerName)
                    finalPlayerList.append(playerName)
                else:
                    print "%s is not a valid player" % playerName
            except (TypeError, ValueError):
                loop = False


    print "Human players are: %s" % finalPlayerList

    #serverAddress = 'http://localhost:8000/'

    newServer = raw_input("Please enter the servers address: [default. http://localhost:8000]:")
    if not newServer == '':
        newgame.serverAddress = newServer

    result = s.app.addNewServer(newgame.serveruser, newgame.serverpass, newgame.serverAddress)
    #result = Services.inject(GAE).addNewServer(serveruser, serverpass, serverAddress)
    #you have Y spots left, how many should be AI
    newgame.name = s.app.addNewGame(newgame.serveruser, newgame.serverpass, newgame.serverAddress, newgame.numHumans, newgame.serverversion)
    print "Game: %s. Created at %s." % (newgame.name, newgame.serverAddress)

    #add players to game
    yn = 'y'
    yn = raw_input("Do you want to shuffle the players? Y/N [Y]")
    if (yn.lower() == 'y'):
        shuffle(finalPlayerList)
    for player in finalPlayerList:
        result = s.app.addUserToGame(newgame.serveruser, newgame.serverpass, newgame.serverAddress, newgame.name, player)

    #generate the galaxy file and save
    generateGalaxy = generate.GenerateGalaxy()
    generateGalaxy.genGalaxy(dataPath = newgame.dataPath, starMapFile = newgame.mapfile, playerList = finalPlayerList, doAI = 1, galaxyName = newgame.name)
    workingGalaxy = generateGalaxy.getGalaxy()

    try:
        os.mkdir("../Database/" + newgame.name )
    except OSError:
        pass

    storedata.saveToFile(workingGalaxy, "../Database/" + newgame.name + "/" + newgame.name + ".anw")

    print "Start game: ", s.app.startGame(newgame.serveruser, newgame.serverpass, newgame.name)

