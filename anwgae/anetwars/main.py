from GameManagement import GameManagement
from MailUtil import *
from QueryUtil import *
from StringIO import StringIO
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from models import User, Game, Server, UserGameInfo, SimpleCounterShard, \
    SupportedVersions, Updater
from xmlrpcserver import XmlRpcServer
import cgi
import hashlib
import logging
import os
import random
import re
import time
import traceback
import xmlrpclib
from google.appengine.ext.db import DateTimeProperty

# any lowercase letter or number combination 4 to 32 characters wide
validUserRegex = re.compile("^[a-z0-9]{4,32}$")

playerRanks = {1:{'name':'Rookie'},
               2:{'name':'Cadet'},
               4:{'name':'Ensign'},
               8:{'name':'Chief'},
               16:{'name':'Master Chief'},
               25:{'name':'Lieutenant 2nd Class'},
               35:{'name':'Lieutenant 1st Class'},
               50:{'name':'Lieutenant Commander'},
               65:{'name':'Commander 2nd Class'},
               75:{'name':'Commander 1st Class'},
               90:{'name':'Captain'},
               110:{'name':'Commodore 2nd Class'},
               130:{'name':'Commodore 1st Class'},
               180:{'name':'Rear Admiral'},
               220:{'name':'Vice Admiral'},
               300:{'name':'Admiral'},
               400:{'name':'Emperor'}
               }

def clugesleep():
    time.sleep(0.5)

def getNewRank(level):
    maxRank = 1
    for key in playerRanks.keys():
        if level > key and key > maxRank:
            maxRank = key
    return maxRank


class Application:
    """This is the main GAE Application, methods that have an _ cannot be called
    this is my own notation and is really based on having meta in the function"""

    def getAllPlayers(self, meta):
        """ this is for compatibility with legacy code. we shouldn't need this """
        query = User.all()
        #result = query.fetch()
        usernames = []
        for r in query:
            usernames.append(r.key().name())
        return usernames

    def addAdminFirst(self, meta, user, password, email):
        """ On a fresh database instance without any users, this function will add a super user. only really useful for testing purposes""" 
        query = User.all()
        result = query.fetch(1)
        if len(result):
            return 1
            
        u = User(key_name=user)
        u.admin = True
        u.salt = getRandomSalt()
        u.password = getPasswordHash(password, u.salt)
        u.firstName = ""
        u.lastName = ""
        u.email = email
        u.passwordHint = ""
        u.valid = True
        u.trustedServerOwner = False
        u.canStartServer = True
        u.put()
        return 0
    
    
    def addSupportedVersion(self, meta, user, password, version, latest, supported):
        if not isAuthForAdmin(user, password):
            return -1

        query = db.Query(SupportedVersions)
        query.filter("version = ", version)
        sv = query.get()
        if sv == None:
            sv = SupportedVersions()

        sv.latestVersion = latest
        sv.version = version
        sv.supported = supported
        
        sv.put()
        clugesleep()
        return 0
        
    def getLatestVersion(self, meta):
        query = db.Query(SupportedVersions)
        query.filter("supported = ", True)
        query.filter("latestVersion = ", True)
        
        latestVersion = query.get()
        versionString = None
        if latestVersion != None:
            versionString = latestVersion.version
        return versionString
        
    def getSupportedVersions(self, meta):
        query = db.Query(SupportedVersions)
        query.filter("supported =", True)
        results = {}
        for res in query:
            results[res.version] = {'version':res.version, 'latest':res.latestVersion}
        
        return results
    
    def __changeUserPassword(self, handle, newpassword):
        u = getUser(handle)
        if u == None:
            return -1
        
        u.salt = getRandomSalt()
        u.password = getPasswordHash(newpassword, u.salt)

        u.put()
        
        return 0
        
    def __addNewUser(self, handle, emailaddress, password, hint, trustedServerOwner, canStartServer, firstName="", lastName=""):
        
        # ensure handle is lowercase
        handle = handle.lower()
        if validUserRegex.match(handle) == None:
            return 1

        if getUser(handle) != None or getUserByEmail(emailaddress) != None:
            # if the email or user is a valid id then we can't continue
            return 2
        
        u = User(key_name=handle)
        u.admin = False
        # python implementation doesn't need a large value for salt as it is sloooow
        u.salt = getRandomSalt()
        u.password = getPasswordHash(password, u.salt)
        u.passwordhint = hint
        u.email = emailaddress
        u.firstName = firstName
        u.lastName = lastName
        u.valid = True
        u.trustedServerOwner = trustedServerOwner
        u.canStartServer = canStartServer
        u.put()
        clugesleep()
        return 0
        
    
    def addNewUser(self, meta, user, password, handle, newuserpassword, email, trustedServerOwner, canStartServer, firstName="", lastName=""):
        """This method is very likely not thread safe"""
        if not isAuthForAdmin(user, password):
            return 1

        return self.__addNewUser(handle, email, newuserpassword, "no hint", trustedServerOwner, canStartServer, firstName, lastName) 
    
    def registerNewUser(self, meta, handle, emailaddress, password, hint, firstName="", lastName=""):
        return self.__addNewUser(handle, emailaddress, password, hint, False, False, firstName, lastName)
    
    def addNewGame(self, meta, user, password, server, maxplayers, version):

        if not isAuthForAddGame(user, password):
            return -1
        
        # server is url to server, which is also the key in our table
        
        s = queryServer(user, server)
        if s == None:
            raise ValueError("Server [%s] doesn't exist. it must be created first"%(server))
            #return 
        
        g = Game(server = s.key())
        g.name = "ANW" + str(getNextGameNum())
        g.maxPlayers = maxplayers
        g.version = version
        g.put()
        clugesleep()
        return g.name
        
        
    def addNewServer(self, meta, user, password, server):
        "the server url and owner username" 
        
        if not isAuthForAddGame(user, password):
            return 1
        
        s = queryServer(user, server)
        u = getUser(user)
        if not u:
            raise ValueError("Owner does not exist in database. add the owner as a user first")
        if not s:
            s = Server(serverUrl=db.Link(server), userOwner=u.key())

        s.userOwner = u.key()
        s.put()
        clugesleep()
        return 0

    def addUpdateURL(self, meta, user, password, url):
        if not isAuthForAdmin(user, password):
            return 1
        
        s = Updater(updateUrl=db.Link(url))
        s.put()
        clugesleep()
        return 0
    
    def getUpdateURL(self, meta):
        url = queryFirstUpdateURL()
        return str(url)
    
    def getAllUpdateURL(self, meta):
        return queryAllUpdateURL()

    def addUserToGame(self, meta, user, password, server, gamename, userName):
        """ TODO - improve error handling!! 
        Also do not allow a duplicate empire id
        """
        if not isAuthForAddGame(user, password):
            return 1
        
        # guard against adding a user to a server I don't own
        myServer = queryServer(user, server)
        myUser = getUser(userName)
        if not myUser and not myServer:
            return 2
                
        # I can't get here if I don't own the server
        myGame = queryGame(myServer, gamename)

        if myGame == None:
            # must create game first
            return 3

        gameinfo = queryUserGameInfo(myUser, myGame)
        if gameinfo == None:
            gameinfo = UserGameInfo(user = myUser, game = myGame)
        else:
            # can't be added twice
            return 4
        # TODO - we need to generate the empire id    
        # not thread safe
        gameinfo.empireId = getNextEmpireId(myGame)
        gameinfo.empireToken = hashlib.sha1(userName + str(time.time()) + str(random.random())).hexdigest()
        if gameinfo.empireId == -1:
            return 5
        
        gameinfo.put()
        clugesleep()
        return 0

    def addUserToGameFromGameFinder(self, meta, user, password, server, gamename):
        """ Function to retreive a user from GameFinder list. 
        how do we prevent a user from being pulled out of the list into an aborted game? 
        returns name of user we added
        """
        
        myUser = None
        success = False
        try:        
            
            myUser = getNextGameFinder()
            if not myUser:
                return None
            
            successVal = self.addUserToGame(meta, user, password, server, gamename, myUser.user.key().name()) 
            if successVal == 0:
                success = True
                # everything is good.  caller of function needs to know what the user name is so it can be added to the database
                return myUser.user.key().name()
        finally:
            if success == False:
                rollbackUserFromGameFinder(myUser)

    def isPlayerValid(self, meta, user, password):
        return isPasswordCorrect(user, password)

    def isServerUserValid(self, meta, user, password):
        return isAuthForAddGame(user, password)

    def changePlayerPassword(self, meta, user, oldpassword, newpassword):
        if isPasswordCorrect(user, oldpassword):
            return self.__changeUserPassword(user, newpassword)
        else:
            return 1

    def isPlayerTokenValidForGameAndEmpire(self, meta, token, empireid, game):
        """ This is an anonymous server function for the time being."""
        return str(empireid) == str(getEmpireIdForUserInGame(token, game))
    
    def getEmpireIdForTokenInGame(self, meta, user, password, token, game):
        """ username, sha1token, server url(eg. http://blah.org:8000/), game name(eg. ANW7) 
        returns
        """
        if not isAuthForAddGame(user, password):
            return None
        
        # this will return the empire id for the game. otherwise, None
        return getEmpireIdForUserInGame(token, game)


    def getGameHostingDictionary(self, meta, user, password):
        if not isPasswordCorrect(user, password):
            return None
        
        gamesDict = {}
        allGames = getAllGamesAmAdminFor(getUser(user))
        for game in allGames:
            gamesDict[game.name] = {'name' : game.name, 
                                    'url' : str(game.server.serverUrl),
                                    'datecreated' : game.dateCreated,
                                    'maxplayers' : game.maxPlayers,
                                    'round' : game.roundNum,
                                    'version' : game.version,
                                    }
        return gamesDict

    def getGameDictionary(self, meta, user, password):
        if not isPasswordCorrect(user, password):
            return None
        
        gamesDict = {}
        allGames = queryAllGamesForUser(user)
        for gameInfo in allGames:
            if gameInfo.game.gameOver == True:
                continue

            gm = GameManagement(gameInfo.game.name)
            # pass in empire_game_round query into search
            maxRoundNum, turnComplete = gm.getCurrentRoundAndTurnComplete(gameInfo.empireId)
            
            gameDict = {}
            gameDict['empireid'] = gameInfo.empireId
            gameDict['url'] = str(gameInfo.game.server.serverUrl)
            gameDict['version'] = gameInfo.game.version
            gameDict['token'] = gameInfo.empireToken
            gameDict['round'] = maxRoundNum
            gameDict['turncomplete'] = turnComplete
            
            # this name should be globally unique
            gamesDict[gameInfo.game.name] = gameDict

        gameFinder = queryGameFinderFromUserName(user)

        if gameFinder:
            gameDict = {}
            gameDict['pending'] = gameFinder.pendingGameStart
            if gameFinder.dateCreated:
                gameDict['dateCreated'] = gameFinder.dateCreated.ctime()
            else:
                gameDict['dateCreated'] = None
            if gameFinder.dateAddedToGame:
                gameDict['dateAddedToGame'] = gameFinder.dateAddedToGame.ctime()
            else:
                gameDict['dateAddedtoGame'] = None
                
            gamesDict['Game Finder'] = gameDict 

        return gamesDict
    
    def registerForGameFinder(self, meta, user, password):
        if not isPasswordCorrect(user, password):
            return False
        return registerInGameFinder(user)
        
        
    def getGameUserEmailDictionary(self, meta, user, password, gameName):
        if not isAuthForGameAdmin(user, password, gameName):
            return None
        
        game = queryGameWithNameOnly(gameName)
        ugis = queryUserGameInfosInGame(game)
        retVal = {}
        for ugi in ugis:
            retVal[ugi.user.key().name()] = str(ugi.user.email)
        return retVal
        
    def startGame(self, meta, user, password, gameName):
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        gm = GameManagement(gameName)
        return gm.startGame() 

    def getCurrentRound(self, meta, user, password, gameName):
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        gm = GameManagement(gameName)
        return gm.getCurrentRoundNumber()
        

    def endRound(self, meta, user, password, gameName, newRound):
        if not isAuthForGameAdmin(user, password, gameName):
            return False
                    
        gm = GameManagement(gameName)
        return gm.initializeRound(newRound)
    
    def setEmpireTurnStatus(self, meta, user, password, gameName, empireId, turnEnded):
        """ end an individual empires turn status. to end turn, set turnEnded to true """
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        gm = GameManagement(gameName)
        return gm.setEmpireTurnStatus(empireId, turnEnded)
    
    def setEmpireSurrender(self, meta, user, password, gameName, empireId):
        """ this will surrender the empire. There is no turning back, they won't be able to get game information from GAE any longer """
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        gm = GameManagement(gameName)
        return gm.setEmpireSurrenderStatus(empireId, True)

    def setGameOver(self, meta, user, password, gameName):
        """ Ends the game.  The server might still be running, but as far as GAE is concerned, the game will be unreachable by all users"""
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        gm = GameManagement(gameName)
        return gm.setGameOver()

    def isValidEmailOrUserId(self, meta, user, password, userOrEmail):
        """ pass in a user id or email address and this function returns True if it is a valid user, False otherwise 
        this function requires game adding ability
        """
        if not isAuthForAddGame(user, password):
            return False

        user = getUser(userOrEmail)
        if user != None:
            return True
        
        user = getUserByEmail(userOrEmail)
        if user != None:
            return True

        return False
    
    def sendEmpireToEmpireEmail(self, meta, user, password, gameName, fromEmpire, toEmpire, subject, message):
        if not isAuthForGameAdmin(user, password, gameName):
            return False
        
        fromUser = getUserGameInfoInGameForEmpireId(gameName, int(fromEmpire))
        if fromUser == None:
            return False
        toUser = getUserGameInfoInGameForEmpireId(gameName, int(toEmpire))
        if toUser == None:
            return False
        
    
        sendMessage(destinationAddress=toUser.user.email, subjectText=subject, bodyText=message)
    
        return True
    
    def updateGameModels(self, meta, adminuser, adminpass):
        if isAuthForAdmin(adminuser, adminpass):
            query = db.Query(Game)
            for game in query:
                game.put()
            return True
        return False

    def updateUserGameInfoModels(self, meta, adminuser, adminpass):
        if isAuthForAdmin(adminuser, adminpass):
            query = db.Query(UserGameInfo)
            for ugi in query:
                ugi.put()
            return True
        return False
    
    def updateUserModels(self, meta, adminuser, adminpass):
        if isAuthForAdmin(adminuser, adminpass):
            query = db.Query(User)
            for u in query:
                u.put()
            return True
        return False

class XMLRpcHandler(webapp2.RequestHandler):                                    
    rpcserver = None

    def __init__(self, value, value2):
        super(XMLRpcHandler, self).__init__(value, value2)         
        self.rpcserver = XmlRpcServer()                                        
        app = Application()                                                    
        self.rpcserver.register_class('app',app)                               

    def post(self):
        request = StringIO(self.request.body)
        request.seek(0)                                                        
        response = StringIO()                                                  
        try:
            self.rpcserver.execute(request, response, None)                    
        except Exception, e:                                                   
            logging.error('Error executing: '+str(e))                          
            for line in traceback.format_exc().split('\n'):                    
                logging.error(line)
        finally:
            response.seek(0)  

        rstr = response.read()                                                 
        self.response.headers['Content-type'] = 'text/xml'                     
        self.response.headers['Content-length'] = "%d"%len(rstr)               
        self.response.out.write(rstr)
        
app = webapp2.WSGIApplication(
                                     [('/xmlrpc/', XMLRpcHandler)],
                                     debug=True)

