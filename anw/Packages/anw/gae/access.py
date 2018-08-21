'''
Created on 2011-08-03

@author: kundertk
'''

import xmlrpclib
import logging
import sys
from anw.func import globals


class GAE(object):
    
    username = "setme"
    password = "setme"
    usernameEmailLookup = {}
    
    """ This is the default implementation that connects to the official GAE """
    def getConnection(self):
        return None

    def endEmpireTurn(self, galaxyName, empireId, turnStatus):
        # this is basically just a boolean flag that will will get set in GAE
        return True

    def endRound(self, galaxyName, newRoundId):
        return 0

    def isPlayerTokenValidForGameAndEmpire(self, empirePass, empireID, galaxyName):
        logging.info("Checking player token for empire %s in galaxy %s"%(empireID, galaxyName))
        return True

    def isServerUserValid(self):
        """Check if this server is configured with the right username/password"""
        return True

    def sendMail(self, galaxy, sourceEmpire, toEmpire, subject, message):
        #try:
        logging.warn("Warning, this function should no longer be used. It doesn't do anything anymore")

        
    def getEmailAddressesForUsersInGalaxy(self, galaxy):
        """ Pass in galaxy name and this function will return a dictionary of username -> email address"""
        return []

    def setEmpireSurrender(self, galaxy, empireId):
        pass
    
    def isValidEmailOrUserId(self, playerName):
        return True
     
    
    def createNewGame(self, serverAddress, players):
        return "ANW1"

class LocalGAE(GAE):
    def getConnection(self):
        s = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
        return s

    