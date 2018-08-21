#!/usr/bin/env python

import xmlrpclib
import time

s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
#s = xmlrpclib.Server('http://anetwars.appspot.com/xmlrpc/')
#result = s.app.getAllPlayers()
#print '%s' % result
#result = s.app.isPlayerValid('testguy','pass1')
#print '%s' % result
#result = s.app.addNewPlayer('testguy', 'pass1', 'test@example.com')
#print '%s' % result
#result = s.app.addNewPlayer('testgirl', 'pass2', 'test2@example.com')
#print '%s' % result
#result = s.app.createGalaxy('ANW99', 2, "['testguy', 'testgirl']", 24)
#print '%s' % result

admin = "admin"
password = "pass"

print "add admin first", s.app.addAdminFirst(admin, password, "fake@fake")
print "add admin second", s.app.addAdminFirst(admin, password, "fake@fake")


count = 0
for name in ['yamato1','montgomery1','patton1','testgirl','testguy']:
    count += 1
    t = time.time()
    result = s.app.addNewUser(admin, password, name, 'pass1', 'email' + str(count) + '@fake', False, False)
    print '%s %f' % (result, time.time() - t)

print s.app.addNewUser(admin, password, 'user1', 'pass1', 'kris.kundert+user1@gmail.com', False, True)
print s.app.addNewUser(admin, password, 'user2', 'pass1', 'kris.kundert+user2@gmail.com', False, False)
print s.app.addNewUser(admin, password, 'user3', 'pass1', 'user3@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user4', 'pass1', 'user4@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user5', 'pass1', 'user5@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user6', 'pass1', 'user6@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user7', 'pass1', 'user7@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user8', 'pass1', 'user8@blah.org', False, False)
print s.app.addNewUser(admin, password, 'user9', 'pass1', 'user9@blah.org', False, False)
print s.app.addNewUser(admin, password, 'testguy', 'pass1', 'kris.kundert+testguy@gmail.com', False, False)
print s.app.addNewUser(admin, password, 'testgirl', 'pass1', 'kris.kundert+testgirl@gmail.com', False, False)

print "valid user should be true", s.app.isValidEmailOrUserId("user1", "pass1", "user1@blah.org")
print "valid user should be true", s.app.isValidEmailOrUserId("user1", "pass1", "user6")
print "valid user should be false", s.app.isValidEmailOrUserId("user1", "pass1", "shiznit@blahsky")


print 'add new server', s.app.addNewServer('user1', 'pass1', 'http://localhost:8000/')  # create server and it is run by 'user1'
print 'add new server', s.app.addNewServer('user1', 'pass1', 'http://www.armadanetwars.com:8000/')  # create server and it is run by 'user1'
game1 = s.app.addNewGame('user1', 'pass1', 'http://localhost:8000/', 4, "0.7") # create a game on the server.  ANW1
game2 = s.app.addNewGame('user1', 'pass1', 'http://localhost:8000/', 4, "0.8") # create a game on the server.  ANW2
game3 = s.app.addNewGame('user1', 'pass1', 'http://www.armadanetwars.com:8000/', 4, "0.7") # create a game on the server.  ANW2
print "new game: ", game1 
print "new game: ", game2
print "new game: ", game3
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'testguy')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'testgirl')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'user1')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'user2')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'user5') # fails game full
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'user6') # fails game full
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game1, 'user7') # fails game full
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game2, 'user1')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game3, 'user1')
print s.app.addUserToGame('user1', 'pass1', 'http://localhost:8000/', game3, 'user2')
gameinfo = s.app.getGameDictionary('user1', 'pass1') # should be in 1 game
print "2 games:",s.app.getGameDictionary('user1', 'pass1') # should be in 2 games
print "empire id for user1 (should be 3)", s.app.getEmpireIdForTokenInGame(admin, password, gameinfo['ANW1']['token'], 'ANW1')
gameinfo = s.app.getGameDictionary('user2', 'pass1') # should be in 1 game
print "1 games:", gameinfo
print "no games", s.app.getGameDictionary('user7', 'pass1') # should be in no games
print "empire id for user2 (should be 4)", s.app.getEmpireIdForTokenInGame(admin, password, gameinfo['ANW1']['token'], 'ANW1')


print "Start game ANW1", s.app.startGame('user1', 'pass1', game1)
print "Start game ANW1", s.app.startGame('user1', 'pass1', game2)
print "Start game ANW1", s.app.startGame('user1', 'pass1', game3)
s.app.endRound('user1', 'pass1', game1, 1)
s.app.endRound('user1', 'pass1', game1, 2)
s.app.endRound('user1', 'pass1', game1, 3)
s.app.endRound('user1', 'pass1', game3, 4)
s.app.setEmpireTurnStatus('user1', 'pass1', 'ANW1', 1, True)

print s.app.addSupportedVersion(admin, password, "0.9", False, True)
print s.app.addSupportedVersion(admin, password, "0.10", False, True)
print s.app.addSupportedVersion(admin, password, "0.11", False, True)
print s.app.addSupportedVersion(admin, password, "0.8", True, True)
print s.app.getLatestVersion()

s.app.sendEmpireToEmpireEmail('user1', 'pass1', game1, 1, 2, "Send from empire 1 to empire 2", "my message")

# surrender for testguy in ANW1
print "Should be in ANW1", s.app.getGameDictionary('testguy', 'pass1')
print s.app.setEmpireSurrender('user1', 'pass1', game1, 1)
print "Should no longer be in ANW1", s.app.getGameDictionary('testguy', 'pass1')

print "Should be in ANW1, ANW2", s.app.getGameDictionary('user1', 'pass1')
print s.app.setGameOver('user1', 'pass1', game2)
print "Shouldn't be in ANW2, only ANW1", s.app.getGameDictionary('user1', 'pass1')

print s.app.updateGameModels(admin, password)
print s.app.updateUserGameInfoModels(admin, password)

print s.app.registerForGameFinder('user1', 'pass1')
print s.app.registerForGameFinder('user9', 'pass1')

print s.app.addUpdateURL(admin, password, 'http://localhost/anw/update')

print s.app.getGameHostingDictionary('user1', 'pass1')

print s.app.getSupportedVersions()