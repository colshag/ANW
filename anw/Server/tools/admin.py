from xmlrpclib import ServerProxy
import os
import re
import sys

# forward declare. defined at bottom
COMMANDS = {}
PROMPT = "ANW>"

class ServerConnection(object):

    def __init__(self, galaxy):
        """ This will not support ssl mode obviously """
        key, port, pid = self.getConnectionInfo(galaxy)
        self.connection = ServerProxy('http://localhost:%s'%port)
        self.adminPassword = key
        self.galaxyName = galaxy
        self.key = {'adminPassword':self.adminPassword, 'galaxyName':self.galaxyName}

    def getConnectionInfo(self, database):
        infoFilePath = os.path.join(os.path.expanduser("~"), ".anw", database + ".info")
        info = open(infoFilePath, "rb").read()
    
        keyRegex = re.compile("key\s*=\s*(.*)")
        portRegex = re.compile("port\s*=\s*(.*)")    
        pidRegex = re.compile("pid\s*=\s*(.*)")
        key = keyRegex.findall(info)[0]    
        port = portRegex.findall(info)[0]    
        pid = pidRegex.findall(info)[0]    

        return key, port, pid

    def forceEndRound(self):
        return self.connection.forceEndRound(self.key)

    def sendGlobalEmail(self, message):
        return self.connection.sendGlobalInternalMail(self.key, self.galaxyName, self.galaxyName + " ADMIN MESSAGE", message)
        
    def vacationMode(self, empireID, awayMode):
        return self.connection.vacationMode(self.key, empireID, awayMode)

    def getPlayerList(self):
        return self.connection.getUserInformation(self.key)

def commandPop(tokens):
    return tokens.pop(0).upper()

def processHelp(tokens):
    if not len(tokens):
        print "Available commands"
        print "-----------------------"
        for c in COMMANDS:
            print "%s"%c
        print "-----------------------"
        print "Type help in front of any command for information"
        return
    
    help = commandPop(tokens)
    if help in COMMANDS:
        print COMMANDS[help][1]

def printHelp(section, message):
    print "Invalid Input -", message
    print
    print COMMANDS[section.upper()][1]

def processEndGame(tokens):
    if len(tokens) != 2:
        printHelp("endgame", "You must provide a galaxy name and an end game status")
        return
    
    raise NotImplemented

def processEndRound(tokens):
    if len(tokens) != 1:
        printHelp("endround", "you must provide a galaxy name")
        return
    
    galaxy = commandPop(tokens)
    connection = ServerConnection(galaxy)

    result = connection.forceEndRound()
    if result == 1:
        print "Successfully sent end round command for galaxy", galaxy
    else:
        print "End round failed. Reason [%s]"%str(result)

def processVacation(tokens):
    if len(tokens) != 3:
        printHelp("vacation", "you must provide a galaxy name, empireID and True/False")
        return

    galaxy = commandPop(tokens)
    empireID = commandPop(tokens)
    awayMode = commandPop(tokens)
    if awayMode.lower() in ['true', '1']:
        awayMode = True
    else:
        awayMode = False
    print "I should ", awayMode, "Empire ", empireID, " in galaxy ", galaxy
    
    connection = ServerConnection(galaxy)

    result = connection.vacationMode(empireID, awayMode)
    if result:
        print "Successfully set/cleared [%s] vacation mode"%str(empireID)
    else:
        print "Setting Vacation Failed"

def processMail(tokens):
    if len(tokens) != 1:
        printHelp("mail", "you must specify a galaxy name")
        return

    galaxy = commandPop(tokens)
    connection = ServerConnection(galaxy)
    print "Enter your message that will go to everyone and press enter to send. (Ctrl-C to abort) >",
    message = raw_input()
    connection.sendGlobalEmail(message)
    print "Successfully send global message to everyone for galaxy", galaxy
    
def processPlayerList(tokens):
    if len(tokens) < 1:
        printHelp("playerlist", "you must specify a galaxy name")
        return
    galaxy = commandPop(tokens)
    detailed = False
    if len(tokens) and commandPop(tokens) == "DETAILED":
        detailed = True
    
    connection = ServerConnection(galaxy)
    playerDict = connection.getPlayerList()
    if playerDict == 1:
        print "Error retrieving players"
        return
    
    if detailed:
        print "| %8s | %12s | %13s | %10s | %5s | %10s | %10s | %10s | %10s |"%("Empire", "User", "Turn Complete", "Logged In", "AFK", "CR", "AL", "IA", "EC")
    else:
        print "| %8s | %12s | %13s | %10s | %5s |"%("Empire", "User", "Turn Complete", "Logged In", "AFK")
        
    for id in range(len(playerDict)):
        # player list starts at 1
        player = playerDict[str(id+1)]
        empireName = player['empireName'].replace(" Empire", "")
        if detailed:
            print "| %8s | %12s | %13d | %10d | %5s | %10d | %10d | %10d | %10d |"%(empireName, player['username'], player['roundComplete'], player['loggedIn'], player['ai'], player['CR'], player['AL'], player['IA'], player['EC'])
        else:
            print "| %8s | %12s | %13s | %10d | %5s |"%(empireName, player['username'], player['roundComplete'], player['loggedIn'], player['ai'])
        
def processExit(tokens):
    sys.exit(0)
        
def processInput(tokens):
    command = commandPop(tokens)
    if command == "":
        return
    if command not in COMMANDS:
        print "Unknown command: '%s'"%command
        print
        processHelp([])
        return
    
    COMMANDS[command][0](tokens)



COMMANDS = {
"PLAYERLIST"
:
(processPlayerList,
"""PLAYERLIST GALAXY [detailed]
- This will list players, and who is currently online
- if option 'detailed' is specified, more empire information will be displayed.  NO CHEATING! ;)
"""
)
,
"MAIL" 
: 
(processMail,
"""MAIL GALAXY
- This will prompt for a message to send to all players in the GALAXY
- eg. MAIL ANW77
"""
)
,
"ENDROUND"
:
(processEndRound,
"""ENDROUND GALAXY
- This will force an end round for the GALAXY specified 
- eg. ENDROUND ANW77
"""
)
,
"ENDGAME"
:
(processEndGame,
"""ENDGAME GALAXY <True|False>
- This will tell the server to flag the game as ended in the central registry. Specify True to end the game.  Specify False to re-enable the game
- eg. ENDGAME ANW77 True
"""
)
,
"VACATION"
:
(processVacation,
"""VACATION GALAXY <empire|empireid> <True|False>
- Flag an empire as being on vacation in the database. This will make their turn auto ended.  When the user logs into the game and un-ends his turn he will leave vacation mode.
- eg. vacation ANW77 1 True
- eg. vacation ANW77 brown True
- empire can be one of Yellow, Brown, Green, Blue, Pink, Red, Cyan or Fire 
"""
)
,
"HELP"
:
(processHelp,
"""
HELP HELP
- displays commands for help"
- eg. help help :p
"""
)
,
"EXIT"
:
(processExit,
"""
exits admin tool
"""
)
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        processInput(sys.argv[1:])
    else:
        try:
            while True:
                print PROMPT,
                line = raw_input()
                processInput(line.strip().split(" "))
        except EOFError:
            pass

        