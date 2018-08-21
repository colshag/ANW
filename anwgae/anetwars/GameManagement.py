from QueryUtil import *
from MailUtil import *
from models import *

def clugesleep():
    time.sleep(0.5)

class GameManagement(object):
    def __init__(self, gameName):
        self.gameName = gameName
        
    def startGame(self):
        return self.initializeRound(1)
        
    def roundExists(self, roundNum):
        return self.getGameRound(roundNum) != None
            
    def getEmpireGameRoundFromGameRound(self, userGameInfo, gameRound):
        query = db.Query(EmpireGameRound)
        query.filter("gameRound =", gameRound)
        query.filter("userGameInfo =", userGameInfo)
        query.order("-roundNum")
        return query.get()
        
    def getGameRound(self, roundNum):
        game = queryGameWithNameOnly(self.gameName)
        query = db.Query(GameRound)
        query.filter("roundNum =", roundNum)
        query.filter("game =", game)
        
        return query.get()
    
    
    def getCurrentRoundNumber(self):
        # ensure something gets returned
        round = self.getCurrentRound()
        if round != None:
            return round.roundNum
        else:
            return -1 
        
    def getCurrentRound(self):
        game = queryGameWithNameOnly(self.gameName)
        query = db.Query(GameRound)
        query.filter("game =", game)
        query.order("-roundNum")
        
        round = query.get()
        return round
        
    
    def initializeRound(self, roundNum):
        if self.roundExists(roundNum):
            # already done
            return True
        
        # we need to initialize the game round information.  start at 0
        myGame = queryGameWithNameOnly(self.gameName)
        myUsers = getAllUserGameInfoInGame(self.gameName)
        gr = GameRound(game=myGame)
        gr.roundNum = roundNum
        myGame.roundNum = roundNum
        myGame.put()
        gr.put()
        clugesleep()
        
        for ugi in myUsers:
            egr = EmpireGameRound(gameRound = gr, userGameInfo = ugi)
            egr.roundNum = roundNum
            egr.turnComplete = False
            egr.put()
            removeUserFromGameFinder(ugi.user)
            sendNewRoundEmailTo(ugi, self.gameName, roundNum)

        clugesleep()
        return True
        
        
    def setEmpireTurnStatus(self, empireId, turnStatus):
        """ this will find the latest EmpireGameRound for the empireId in the game and set the round status 
        This way if the user doesn't end the turn we can scan back in this list and see which rounds they 
        didn't get a chance to end their turn
        """
        #myGame = queryGameWithNameOnly(self.gameName)
        ugi = getUserGameInfoInGameForEmpireId(self.gameName, empireId)
        currentRound = self.getCurrentRound()

        currentEmpireGameRound = self.getEmpireGameRoundFromGameRound(ugi, currentRound)
    
        currentEmpireGameRound.turnComplete = turnStatus
        currentEmpireGameRound.put()
        
        clugesleep()        
        return True
    
    def getMaxEmpireGameRoundNum(self, empireGameRounds):
        maxRound = self.getMaxEmpireGameRound(empireGameRounds)
        if maxRound:
            return maxRound.gameRound.roundNum
        else:
            return -1
        
    def getCurrentRoundAndTurnComplete(self, empireId):
        ugi = getUserGameInfoInGameForEmpireId(self.gameName, empireId)
        currentRound = self.getCurrentRound()

        egr = self.getEmpireGameRoundFromGameRound(ugi, currentRound)

        if egr:    
            return egr.roundNum, egr.turnComplete
        else:
            return 0, False

        
 
        
    def setEmpireSurrenderStatus(self, empireId, surrenderStatus):
        ugi = getUserGameInfoInGameForEmpireId(self.gameName, empireId)
        
        if ugi:
            ugi.surrender = surrenderStatus
            ugi.put()
            clugesleep()
            return True
        
        return False
    
    def setGameOver(self, gameOverStatus = True):
        game = queryGameWithNameOnly(self.gameName)
        if game:
            game.gameOver = gameOverStatus
            game.put()
            clugesleep()