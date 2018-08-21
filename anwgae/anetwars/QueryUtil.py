from google.appengine.ext import db
from models import User, Game, Server, UserGameInfo, SimpleCounterShard, GameFinder, Updater
import datetime
import hashlib
import random
import time

NUM_SHARDS = 20
def clugesleep():
    time.sleep(0.5)

# taken from app engine docs for a simple counter
def get_count():
    """Retrieve the value for a given sharded counter."""
    total = 0
    for counter in SimpleCounterShard.all():
        total += counter.count
    return total

def increment():
    """Increment the value for a given sharded counter."""
    def txn():
        index = random.randint(0, NUM_SHARDS - 1)
        shard_name = "shard" + str(index)
        counter = SimpleCounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = SimpleCounterShard(key_name=shard_name)
        counter.count += 1
        counter.put()
    db.run_in_transaction(txn)
    
def queryGameFinderFromUserName(username):
    user = getUser(username)
    if user:
        query = db.Query(GameFinder)
        query.filter("user =", user)
        return query.get()
    return None

def queryUserGameInfo(user, game):
    """This function expects to be passed Model objects"""
    query = db.Query(UserGameInfo)
    query.filter("user =", user)
    query.filter("game =", game)
    
    return query.get()

def queryUsersInGame(game):
    """This function expects to be passed Model objects"""
    query = db.Query(UserGameInfo)
    query.filter("game =", game)
    users = []
    for u in query:
        users.append(u.user)
    
    return users

def queryUserGameInfosInGame(game):
    """This function expects to be passed Model objects"""
    query = db.Query(UserGameInfo)
    query.filter("game =", game)
    
    ugis = []
    for ugi in query:
        ugis.append(ugi)
        
    return ugis

def queryTokenGameInfo(token, game):
    """This function expects to be passed Model objects"""
    query = db.Query(UserGameInfo)
    query.filter("empireToken =", token)
    query.filter("game =", game)
    
    return query.get()

def getEmpireIdForUserInGame(token, game):
    # TODO - this is copy/paste from the code for creating the games
    # should we care what server the request is coming from?
    
    myGame = queryGameWithNameOnly(game)

    if myGame == None:
        # must create game first
        return None

    gameinfo = queryTokenGameInfo(token, myGame)
    if gameinfo == None:
        return None
    
    # we found them in the game for the right server! we are making the 
    # sha1 token is unique inside this game
    return gameinfo.empireId
    
    
def getUserGameInfoInGameForEmpireId(gameName, empireId):
    myGame = queryGameWithNameOnly(gameName)
    if myGame == None:
        return None
    
    query = db.Query(UserGameInfo)
    query.filter("game = ", myGame)
    query.filter("empireId = ", empireId)
    return query.get()
    
def getAllUserGameInfoInGame(gameName):
    myGame = queryGameWithNameOnly(gameName)
    
    if myGame == None:
        # no game exists
        return None
    
    query = db.Query(UserGameInfo)
    query.filter("game =", myGame)
    gameInfos = []
    for ugi in query:
        gameInfos.append(ugi)
        
    return gameInfos
    
    

def queryAllGamesForUser(user):
    """This function expects to be passed a user key name. It will only return games that haven't been surrendered or aren't over"""
    u = getUser(user)
    query = db.Query(UserGameInfo)
    query.filter('user = ', u)
    query.filter('surrender = ', False)
    
    games = []
    for g in query:
        if g.game.gameOver == False:
            games.append(g)
    return games

def getNextEmpireId(game):
    query = db.Query(UserGameInfo)
    query.filter("game = ", game)
    max = 0
    for result in query:
        if result.empireId > max:
            max = result.empireId
    if max + 1 > game.maxPlayers:
        return -1
    return max + 1
    
def getNextGameNum():
    increment()
    clugesleep()
    return get_count()

def queryGame(server, name):
    """ this function expects a server model and a game name"""
    query = db.Query(Game)
    query.filter("server =", server)
    query.filter("name =", name)
    
    return query.get()

def queryGameWithNameOnly(name):
    query = db.Query(Game)
    query.filter("name =", name)
    # game names should be globally unique!
    return query.get()


def getUser(user):
    user = user.lower()
    foundUser = User.get_by_key_name(user)
    if foundUser:
        return foundUser

def registerInGameFinder(userName):
    """ This method involves a cheezy way of getting into the game finder. it has a race condition if we have malicious users.  can get added twice"""
    userVal = getUser(userName)
    
    query = db.Query(GameFinder)
    query.filter("user =", userVal)
    val = query.get()
    if val != None:
        # already in game finder!
        return False
    
    gameFinder = GameFinder(user=userVal)
    gameFinder.put()
    clugesleep()
    return True
    
def getNextGameFinder():
    """ TODO, because we can use transactions, we should probably be re-running the query to find a different user if something fails"""
    query = db.Query(GameFinder)
    query.filter("pendingGameStart =", False)
    query.order("dateCreated")
    
    gameFinder = query.get()
    return db.run_in_transaction(getNextGameFinderTransaction, gameFinder)

def getNextGameFinderTransaction(gameFinder):
    if gameFinder:
        gameFinder.pendingGameStart = True
        gameFinder.dateAddedtoGame = datetime.datetime.now()
        gameFinder.put()
        clugesleep()
        return gameFinder
    return None

def removeUserFromGameFinder(user):
    if user:
        query = db.Query(GameFinder)
        query.filter("user = ", user)
        query.filter("pendingGameStart = ", True)
        gameFinders = query.fetch(limit=5)
        db.delete(gameFinders)
        return 0
    return 1

def rollbackUserFromGameFinder(gameFinder):
    db.run_in_transaction(rollbackUserFromGameFinder, gameFinder)
    
def rollbackUserFromGameFinderTransaction(gameFinder):
    if gameFinder:
        gameFinder.pendingGameStart = False
        gameFinder.dateAddedToGame = None
        clugesleep()
        gameFinder.put()

def getUserByEmail(email):
    query = db.Query(User)
    query.filter("email =", email)
    
    return query.get()

def queryServer(user, server):
    query = db.Query(Server)
    query.filter("serverUrl =", server)
    query.filter("userOwner =", getUser(user))
    return query.get()

def queryFirstUpdateURL():
    query = db.Query(Updater)
    updater = query.get()
    if updater != None:
        return updater.updateUrl
    else:
        return None

def queryAllUpdateURL():
    l = []
    query = db.Query(Updater)
    results = query.fetch(limit=15)
    for element in results:
        l.append(str(element.updateUrl))
    return l


def isPasswordCorrect(user, password):
    u = getUser(user)
    if u == None:
        return False
    
    if u.password != getPasswordHash(password, u.salt):
        return False
    
    # TODO - check account expiry
    # if u.expiry blah blah:
    
    if not u.valid:
        return False
    
    return True
    
def isAuthForAddGame(user, password):
    # FIXME - this will let us add games to servers we don't own
    if not isPasswordCorrect(user, password):
        return False

    u = getUser(user)

    return u.canStartServer

def isGameAdmin(user, game):
    """ This method expects user,and game to be models """
    
    return game.server.userOwner == user

def getAllGamesAmAdminFor(user):
    """ This method expects user to be a model """
    query = db.Query(Server)
    query.filter("userOwner =", user)
    
    servers = [q for q in query]
    
    games = []
    
    for server in servers:
        query = db.Query(Game)
        query.filter("server =", server)
        query.filter("gameOver =", False)
        for g in query:
            games.append(g)
            
    return games
            
    

def isAuthForGameAdmin(user, password, gameName):
    # we need a simple way to verify the gameName is linked to the user provided
    if not isAuthForAddGame(user, password):
        return -1
    
    game = queryGameWithNameOnly(gameName)
    if not game:
        return -2

    #server = game.server        

    if not isGameAdmin(user, game):
        return -3
               
    
    

def isAuthForAdmin(user, password):
    if not isPasswordCorrect(user, password):
        return False
    u = getUser(user)
    return u.admin
     
def isAuthForPlay(user, password):
    return isPasswordCorrect(user, password)

# should be using bcrypt.  but we need to use a low salt value for app engine.  if hackers download our database they will be able to run the algorithms
# much faster with a C bcrypt implementation...
def getPasswordHash(password, salt):
    #return bcrypt.hashpw(password, salt)
    # make it slightly harder. hopefully nobody steals our code
    return hashlib.sha1(str(password) + "_"*len(password) + str(salt)).hexdigest()

def getRandomSalt():
    #return bcrypt.gensalt(random.randint(1,2))
    return hashlib.sha1("%d"%(random.randint(0, 10000000))).hexdigest()

    