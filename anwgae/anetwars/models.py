from google.appengine.ext import db

# Taken from app engine documentation
class SimpleCounterShard(db.Model):
    """Shards for the counter"""
    count = db.IntegerProperty(required=True, default=0)

class SupportedVersions(db.Model):
    latestVersion = db.BooleanProperty()
    version = db.StringProperty() # eg. 0.8
    supported = db.BooleanProperty() # set to False to prevent people from installing

class User(db.Model):
    password = db.StringProperty()
    salt = db.StringProperty()
    email = db.EmailProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    passwordhint = db.StringProperty()
    valid = db.BooleanProperty()
    expiry = db.DateTimeProperty()
    trustedServerOwner = db.BooleanProperty()
    # an untrusted user may also have the ability to start a server
    canStartServer = db.BooleanProperty()
    # only an admin can modify user data
    admin = db.BooleanProperty()

class League(db.Model):
    leagueTitle = db.StringProperty()
    leagueAdmin = db.ReferenceProperty(User, required=True)

class Server(db.Model):
    """Having a separate server allows us to have trusted and untrusted servers. 
    A server can host more than a single game
    """
    # there is no unique key for Servers at this time.  We will find all the servers based on owner
    # this will allow users to start 'localhost' servers.
    serverUrl = db.LinkProperty(required=True)
    userOwner = db.ReferenceProperty(User, required=True, collection_name='owners')
    
class Game(db.Model):
    name = db.StringProperty()
    # should server be its own entity?
    server = db.ReferenceProperty(Server, required=True, collection_name = 'servers')
    dateCreated = db.DateTimeProperty(auto_now_add=True)
    maxPlayers = db.IntegerProperty()
    # need to link to more information?
    roundNum = db.IntegerProperty()
    hoursLeft = db.IntegerProperty()
    version = db.StringProperty()

    gameOver = db.BooleanProperty(default=False)
    
    # what league this game is part of
    # TODO - can link a game to a league after it is created.
    # only a league admin can do this
    
    league = db.ReferenceProperty(League, required=False)

class UserGameInfo(db.Model):
    """ This is ties a user into a game """
    user = db.ReferenceProperty(User, required=True,
                                collection_name = 'users')
    game = db.ReferenceProperty(Game, required=True,
                                collection_name = 'games')
    empireId = db.IntegerProperty()
    # will be a sha1 that the client will send to the server for authentication
    empireToken = db.StringProperty()
    
    surrender = db.BooleanProperty(default=False)
    
class GameRound(db.Model):
    """ each game round belongs to a game """
    game = db.ReferenceProperty(Game, required=True, collection_name = 'game_rounds')
    roundNum = db.IntegerProperty()
    
    
class EmpireGameRound(db.Model):
    """ Each empire statistics for a round belongs to a game round 
    When a round starts this information gets created.  when the round ends the information is updated from the server
    """ 
    gameRound = db.ReferenceProperty(GameRound, required=True, collection_name = 'empire_game_round')
    # based on the user game info we can now find all the round information for that user.
    userGameInfo = db.ReferenceProperty(UserGameInfo, required=True, collection_name = 'empire_game_round')

    roundNum = db.IntegerProperty()

    # when a user clicks end-turn, this property will end.
    # once the server rolls the turn it will send a message to GAE indicating a new round was started.  At that point
    # gae will create all the necessary entries for the new round
    turnComplete = db.BooleanProperty()

  
class LeagueUser(db.Model):
    league = db.ReferenceProperty(League, required=True)
    user = db.ReferenceProperty(User, required=True)
    admin = db.BooleanProperty()
    
class GameFinder(db.Model):
    user = db.ReferenceProperty(User, required=True)
    pendingGameStart = db.BooleanProperty(default=False)
    # will get set when added to database
    dateCreated = db.DateTimeProperty(auto_now_add=True)
    # we may want to check in the future if a user has been pending too long, we can add him back into the queue.
    # not fair to the user to take them out if the server operator doesn't get his game going
    dateAddedToGame = db.DateTimeProperty()

class Updater(db.Model):
    updateUrl = db.LinkProperty(required=True) 
        


    