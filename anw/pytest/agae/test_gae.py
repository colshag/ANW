# Armada Net Wars (ANW)
# test_gae.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The function of GAE (Google App Engine) Server is to store the user ladder and 
# game information, to validate all users as they login to play games on any
# Server globally.
# ---------------------------------------------------------------------------
import xmlrpclib
import time

admin = "admin"
adminpass = "adminpass"
serverurl = "http://localhost:8000/"

gameFinderGame = ""

class TestGAE(object):
    # Yes, I know I broke all these!
    # I need to think about how this will work
    # we will need to guard all methods with either user/password and/or some sort of auth token
    def setup_class(self):
        self.server = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
        
    def testGetGameDictionary(self):
        result = self.server.app.getGameDictionary('testguy', 'pass1')
        assert result == None
    
    def testGetAllPlayers(self):
        result = self.server.app.getAllPlayers()
        assert result == []
    
    def testAddAdminFirst(self):
        result = self.server.app.addAdminFirst(admin, adminpass, 'fakeemail@blah')
        assert result == 0
        
    def testAddNewPlayer(self):
        # testguy1 can start a server
        # testguy2 can not
        result = self.server.app.addNewUser(admin, adminpass, 'testguy1', 'pass1', 'test@armadanetwars.com', False, True)
        assert result == 0
        result = self.server.app.addNewUser(admin, adminpass, 'testguy2', 'pass1', 'test1@armadanetwars.com', False, False)
        assert result == 0
        result = self.server.app.addNewUser(admin, adminpass, 'testguy3', 'pass1', 'test2@armadanetwars.com', False, False)
        assert result == 0
        result = self.server.app.addNewUser(admin, adminpass, 'testguy4', 'pass1', 'test3@armadanetwars.com', False, False)
        assert result == 0
        result = self.server.app.isPlayerValid('testguy1', 'pass1')
        assert result == 1
        result = self.server.app.isPlayerValid('testguy2', 'pass1')
        assert result == 1
        result = self.server.app.getAllPlayers()
        assert 'testguy1' in result
        assert 'testguy2' in result   
        assert 'testguy3' in result   
        assert 'testguy4' in result   
    
    def testAddNewPlayerWithName(self):
        result = self.server.app.addNewUser(admin, adminpass, 'testguy5', 'pass1', 'test4@armadanetwars.com', False, False, 'first', 'last')
        assert result == 0
        result = self.server.app.getAllPlayers()
        assert 'testguy5' in result
             
    def testIsServerUserValid(self):
        result = self.server.app.isServerUserValid('testguy1', 'pass1')
        assert result == 1
        
        result = self.server.app.isServerUserValid('testguy2', 'pass1')
        assert result == 0
        
    def testAddNewServer(self):
        result = self.server.app.addNewServer(admin, adminpass, serverurl)
        assert result == 0
        
    def testAddNewGame(self):
        result = self.server.app.addNewGame(admin, adminpass, serverurl, 4, "somever")
        assert result == "ANW1"
        result = self.server.app.addNewGame(admin, adminpass, serverurl, 4, "somever")
        assert result == "ANW2"
    
    def testAddUsertoGame(self):
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW1', 'testguy1') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW1', 'testguy2') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW1', 'testguy3') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW1', 'testguy4') == 0

        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW2', 'testguy1') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW2', 'testguy2') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW2', 'testguy3') == 0
        assert self.server.app.addUserToGame(admin, adminpass, serverurl, 'ANW2', 'testguy4') == 0
    
    def testEmpireIdFetch(self):
        gameinfo = self.server.app.getGameDictionary('testguy1', 'pass1')
        print gameinfo
        assert gameinfo.has_key('ANW1')
        empid = self.server.app.getEmpireIdForTokenInGame(admin, adminpass, gameinfo['ANW1']['token'], 'ANW1')
        assert empid == 1

        gameinfo = self.server.app.getGameDictionary('testguy2', 'pass1')
        print gameinfo
        assert gameinfo.has_key('ANW1')
        empid = self.server.app.getEmpireIdForTokenInGame(admin, adminpass, gameinfo['ANW1']['token'], 'ANW1')
        assert empid == 2
        

    def testIncorrectToken(self):
        empid = self.server.app.getEmpireIdForTokenInGame(admin, adminpass, "obviously incorrect token", 'ANW1')
        assert empid == None
        
    def testIncorrectLogin(self):
        empid = self.server.app.addNewServer(admin, "not the pass", serverurl)
        
    def testStartGame(self):
        assert self.server.app.startGame(admin, adminpass, 'ANW1') == True
        
    def testCurrentRoundIsOne(self):
        assert self.server.app.getCurrentRound(admin, adminpass, 'ANW1') == 1
        
    def testEndRound(self):
        assert self.server.app.endRound(admin, adminpass, 'ANW1', 1) == True
        assert self.server.app.getCurrentRound(admin, adminpass, 'ANW1') == 1
        assert self.server.app.endRound(admin, adminpass, 'ANW1', 5) == True
        assert self.server.app.getCurrentRound(admin, adminpass, 'ANW1') == 5
        
        
    def testTurnNotComplete(self):
        # testguy should be empire 1
        dic = self.server.app.getGameDictionary("testguy1", "pass1")
        print dic
        assert dic['ANW1']['turncomplete'] == False
        
    def testEndTurn(self):
        assert self.server.app.setEmpireTurnStatus(admin, adminpass, "ANW1", 1, True) == True
        
    def testTurnNowComplete(self):
        # testguy should be empire 1
        assert self.server.app.getGameDictionary("testguy1", "pass1")['ANW1']['turncomplete'] == True

    def testQueryUserOrEmail(self):
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "testguy1") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "testguy2") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "test@armadanetwars.com") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "test@armadanetwarss.com") == False


    def testRegisterUser(self):
        #registerNewUser(self, meta, handle, emailaddress, password, hint):
        assert self.server.app.registerNewUser("mynewuser", "my_new_user@emailaddress.com", "awesomepassword", "awesomehint") == 0
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "mynewuser") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "my_new_user@emailaddress.com") == True
        
    def testRegisterUserWithName(self):
        assert self.server.app.registerNewUser("mynewuser2", "my_new_user2@emailaddress.com", "awesomepassword", "awesomehint", "firstname", "lastname") == 0
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "mynewuser2") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "my_new_user2@emailaddress.com") == True

    def testCantAddUserWithUpperCase(self):
        assert self.server.app.registerNewUser("InvalidUser", "doesntmatter@emailaddress.com", "awesomepassword", "awesomehint") == 0
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "invaliduser") == True
        assert self.server.app.isValidEmailOrUserId(admin, adminpass, "InvalidUser") == True

    def testCanAddUserWhenValid(self):
        assert self.server.app.registerNewUser("validuser", "doesntmatter1@emailaddress.com", "awesomepassword", "awesomehint") == 0

    def testMinUsernameLength(self):
        # minimum should be 4 chars
        assert self.server.app.registerNewUser("vali", "doesntmatter2@emailaddress.com", "awesomepassword", "awesomehint") == 0
        assert self.server.app.registerNewUser("nop", "doesntmatter2@emailaddress.com", "awesomepassword", "awesomehint") == 1

    def testMaxUsernameLength(self):
        # maximum should be 4 chars
        thirtytwo = "x"*32
        thirtythree = "x"*33
        assert self.server.app.registerNewUser(thirtytwo, "doesntmatter3@emailaddress.com", "awesomepassword", "awesomehint") == 0
        assert self.server.app.registerNewUser(thirtythree, "doesntmatter4@emailaddress.com", "awesomepassword", "awesomehint") == 1
    
    def testLatestVersion(self):
        print self.server.app.addSupportedVersion(admin, adminpass, "0.8", True, True)
        print self.server.app.addSupportedVersion(admin, adminpass, "0.9", False, False)
        print self.server.app.addSupportedVersion(admin, adminpass, "0.7", False, False)
        assert self.server.app.getLatestVersion() == "0.8"

        
    def testSurrender(self):
        games = self.server.app.getGameDictionary('testguy1', 'pass1')
        assert games != None
        assert games.has_key("ANW2") == True
        self.server.app.setEmpireSurrender(admin, adminpass, 'ANW2', 1)
        newGames = self.server.app.getGameDictionary('testguy1', 'pass1')
        assert newGames != None
        assert newGames.has_key("ANW2") == False
        
    def testEndGame(self):
        games = self.server.app.getGameDictionary('testguy2', 'pass1')
        assert games != None
        assert games.has_key("ANW2") == True
        self.server.app.setGameOver(admin, adminpass, 'ANW2')
        newGames = self.server.app.getGameDictionary('testguy2', 'pass1')
        assert newGames != None
        assert newGames.has_key("ANW2") == False
    
    def testPasswordChange(self):
        
        result = self.server.app.addNewUser(admin, adminpass, 'passwordchange', 'pass1', 'test_password_change@armadanetwars.com', False, True)
        assert result == 0
        assert self.server.app.isPlayerValid('passwordchange', 'pass1') == True
        assert self.server.app.isPlayerValid('passwordchange', 'pass2') == False
        # can't change password
        assert self.server.app.changePlayerPassword('password_change', 'pass2', 'pass2') == 1
        assert self.server.app.isPlayerValid('passwordchange', 'pass2') == False

        # can change password
        assert self.server.app.changePlayerPassword('passwordchange', 'pass1', 'new pass') == 0
        assert self.server.app.isPlayerValid('passwordchange', 'new pass') == True
        assert self.server.app.isPlayerValid('passwordchange', 'pass1') == False

    def testGetEmailAddressesDictionary(self):
        result = self.server.app.getGameUserEmailDictionary(admin, adminpass, 'ANW1')
        assert len(result) == 4
        assert result['testguy1'] == 'test@armadanetwars.com'
        assert result['testguy2'] == 'test1@armadanetwars.com'
        assert result['testguy3'] == 'test2@armadanetwars.com'
        assert result['testguy4'] == 'test3@armadanetwars.com'
        
        
    def testRegisterInGameFinder(self):
        result = self.server.app.registerForGameFinder("testguy2", "pass1")
        assert result == True
        time.sleep(1)
        result = self.server.app.registerForGameFinder("testguy2", "pass1")
        assert result == False
        result = self.server.app.registerForGameFinder("testguy1", "incorrect pass")
        assert result == False
        result = self.server.app.registerForGameFinder("testguy1", "pass1")
        assert result == True
        time.sleep(1)
        result = self.server.app.registerForGameFinder("testguy3", "pass1")
        assert result == True
        time.sleep(1)
        result = self.server.app.registerForGameFinder("testguy4", "pass1")
        assert result == True
    # commenting out as this test is slow

    def testGameDictionaryWithPending(self):
        games = self.server.app.getGameDictionary('testguy2', 'pass1')
        print games
        assert games.has_key("Game Finder") == True
        info = games['Game Finder']
        assert info['pending'] == False
        
    
    def testAddUsersToGameWithGameFinder(self):
        global gameFinderGame
        gameFinderGame = self.server.app.addNewGame(admin, adminpass, serverurl, 4, "somever") 
        
        # users should be in order they were put in game finder
        result = self.server.app.addUserToGameFromGameFinder(admin, adminpass, serverurl, gameFinderGame)
        assert result == 'testguy2'
        result = self.server.app.addUserToGameFromGameFinder(admin, adminpass, serverurl, gameFinderGame)
        assert result == 'testguy1'
        result = self.server.app.addUserToGameFromGameFinder(admin, adminpass, serverurl, gameFinderGame)
        assert result == 'testguy3'
        result = self.server.app.addUserToGameFromGameFinder(admin, adminpass, serverurl, gameFinderGame)
        assert result == 'testguy4'
        
    def testUserPendingInGameFinder(self):
        games = self.server.app.getGameDictionary('testguy2', 'pass1')
        print games
        assert games.has_key("Game Finder") == True
        info = games['Game Finder']
        assert info['pending'] == True
        
    def testUserNotInGameFinderAfterRoundSwitch(self):
        self.server.app.endRound(admin, adminpass, gameFinderGame, 15)
        games = self.server.app.getGameDictionary('testguy2', 'pass1')
        print games
        assert games.has_key("Game Finder") == False
                    
    def testAddUpdateURL(self):
        add = "http://localhost/awesome"
        self.server.app.addUpdateURL(admin, adminpass, add)
        firsturl = self.server.app.getUpdateURL()
        assert add == firsturl
        
    def testQueryAllURLWhenOnlyOne(self):
        assert self.server.app.getAllUpdateURL() == ["http://localhost/awesome"]
    
    def testQueryAllURLWhenTwo(self):
        self.server.app.addUpdateURL(admin, adminpass, "http://blah")
        allurl = self.server.app.getAllUpdateURL()
        assert "http://localhost/awesome" in allurl
        assert "http://blah" in allurl
        
    def testGetAllGamesHosting(self):
        gamehosting = self.server.app.getGameHostingDictionary(admin, adminpass)
        assert 'ANW1' in gamehosting
        assert 'ANW3' in gamehosting
        assert 'ANW2' not in gamehosting
        assert gamehosting['ANW1']['url'] == 'http://localhost:8000/'
        assert gamehosting['ANW1']['round'] == 5
        assert gamehosting['ANW1']['maxplayers'] == 4
    #def testAddOneThousandUsers(self):
    #    for x in range(1000):
    #        result = self.server.app.addNewUser(admin, adminpass, 'stresstest' + str(x), 'pass1', 'test@example.com', False, False)
    #    assert result == 0
        
    def testGetLatestVersion(self):
        print self.server.app.addSupportedVersion(admin, adminpass, "0.10", False, True)
        print self.server.app.addSupportedVersion(admin, adminpass, "0.11", False, True)
        versions = self.server.app.getSupportedVersions()
        assert '0.8'  in versions
        assert '0.10' in versions
        assert '0.11' in versions
        assert len(versions) == 3
        
