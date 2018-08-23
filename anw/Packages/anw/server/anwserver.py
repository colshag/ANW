# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# server.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main ANW Server: The Servers Job is to verify user
# requests, read the object database and ask those objects to 
# return values.  The Server then converts these values into
# XML for the client.
# ---------------------------------------------------------------------------
import os
import string, shutil
import random, types, logging, xmlrpclib
from anw.func import storedata, globals, funcs

from twisted.internet import reactor
from twisted.web import xmlrpc
#from anw.gae.access import GAE
import sys
from anw.util.Injection import Services
from anw.mail.sending import Email

class ANWServer(xmlrpc.XMLRPC):
    """The ANWServer maintains the state of various ANW galaxies at once
    it handles the various user requests, validates them, and saves changes
    to the various ANW databases"""
    def __init__(self):
        #self._sighandler = signal.signal(signal.SIGINT, self.killnicely)
        
        # setup game data
        xmlrpc.XMLRPC.__init__(self)
        logging.basicConfig(level=logging.INFO, 
            format='%(asctime)s %(levelname)s %(message)s',
            filename='server.log',filemode='a') 
        self.log=logging.getLogger('anw.server')
        self.galaxies = {}
        self.path = '../Database/'
        self.savingGalaxyFlag = [] # keep track of galaxies saving to disk
        self.endRoundGalaxyFlag = [] # keep track of galaxies going through endRound  
        self.lp = None

    def runServer(self, port, galaxyName=None, singleplayer=0):
        """run the Server"""
        self.singleplayer = singleplayer
        self._Log('Starting Server on Port:' + str(port))
        self._Log('Loading Galaxies')
        self._LoadGalaxies(galaxyName)
        self._Log('Server Running')


    def writeGameStatus(self):
        """Write All running Galaxy Status to file"""
        s = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
            <html>
            <head>
            <title>Untitled Document</title>
            <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
            </head>
            <body>
            """
        for galaxyName, myGalaxy in self.galaxies.iteritems():
            s = s + """
            <table width="75%s" border="0">
            <tr> 
              <td bgcolor="#000099"> <div align="center"><font color="#FFFFFF" size="4"><strong>%s : ROUND %d : %d HRS LEFT</strong></font></div></td>
            </tr>
            <tr> 
              <td><table width="100%s" border="0">
              <tr bgcolor="#0066FF"> 
                    <td width="44%s"><font color="#FFFFFF"><strong>Name</strong></font></td>
                    <td width="27%s"> <div align="center"><font color="#FFFFFF"><strong>Experience</strong></font></div></td>
                    <td width="17%s"> <div align="center"><font color="#FFFFFF"><strong>Status</strong></font></div></td>
                    <td width="12%s"> <div align="center"><font color="#FFFFFF"><strong>Delay</strong></font></div></td>
                  </tr>
              """ % ('%',myGalaxy.name, myGalaxy.currentRound, myGalaxy.currentHoursLeft,'%','%','%','%','%')
            empireKeys = myGalaxy.empires.keys()
            while empireKeys:
                empireID = random.choice(empireKeys)
                myEmpire = myGalaxy.empires[empireID]
                name = myEmpire.name
                if myEmpire.id != '0':
                    delay = myEmpire.delay
                    exp = myEmpire.experience
                    if myEmpire.alive == 0:
                        status = 'defeated'
                        color = '#FF0000'
                    elif myEmpire.roundComplete == 1:
                        status = 'done'
                        color = '#00FF66'
                    else:
                        status = 'not done'
                        color = '#FFFF00'
                    s = s + """
                    <tr bgcolor="%s"> 
                        <td><strong>%s</strong></td>
                        <td><div align="center"><strong><font color="#000000">%.2f</font></strong></div></td>
                        <td><div align="center"><strong><font color="#000000">%s</font></strong></div></td>
                        <td><div align="center"><strong><font color="#000000">%d</font></strong></div></td>
                      </tr>
                      """ % (color, name, exp, status, delay)
                empireKeys.remove(empireID)
                
            s = s + """
              </table></td>
              </tr>
              </table>
              <p>&nbsp;</p>
              """
            
        # write current end turn status to file
        try:
            # TODO - we should get rid of this!!
            html_file = open('../../../../web/currentstats.html', 'w')
            html_file.write(s)
            html_file.close()
            return
        except:
            pass

    def xmlrpc_vacationMode(self, adminKey, empireID, awayMode):
        """Set or Clear auto-end round mode for empireID"""
        # check adminPassword
        adminPassword = adminKey['adminPassword']
        galaxyName = adminKey['galaxyName']
        if adminPassword == globals.adminaccess:
            #self.sendGlobalInternalMail(galaxyName, subject, message)
            #do stuff here because we've authenticated
            self.setVacationMode(galaxyName,empireID, awayMode)
            return True
        return False

    def setVacationMode(self, galaxyName, empireID, mode):
        """Set empireID into AI (vacation) mode"""
        myGalaxy = self.galaxies[galaxyName]
        myEmpire = myGalaxy.empires[empireID]
        myEmpire.ai = int(mode)
        logging.info('Vacation set to [%d] Success %s %s'%(mode, galaxyName, empireID))

    def xmlrpc_getUserInformation(self, adminKey):
        """ Return a dictionary of empire information """
        adminPassword = adminKey['adminPassword']
        galaxyName = adminKey['galaxyName']

        if adminPassword == globals.adminaccess:
            returnDict = {}
            myGalaxy = self.galaxies[galaxyName]
            for empireID, myEmpire in myGalaxy.empires.iteritems():
                if myEmpire.id == "0":
                    continue
                empireInfo = {}
                empireInfo['id'] = myEmpire.id
                empireInfo['username'] = myEmpire.player
                empireInfo['empireName'] = myEmpire.name
                empireInfo['ai'] = myEmpire.ai
                empireInfo['CR'] = myEmpire.CR
                empireInfo['AL'] = myEmpire.AL
                empireInfo['EC'] = myEmpire.EC
                empireInfo['IA'] = myEmpire.IA
                empireInfo['alive'] = myEmpire.alive
                empireInfo['roundComplete'] = myEmpire.roundComplete
                empireInfo['loggedIn'] = myEmpire.loggedIn
                returnDict[myEmpire.id] = empireInfo
            return returnDict
        else:
            return False
    
    def xmlrpc_sendGlobalInternalMail(self, adminKey, galaxyName, subject, message):
        """Send a global message to all players"""
        # check adminPassword
        adminPassword = adminKey['adminPassword']
        galaxyName = adminKey['galaxyName']
        if adminPassword == globals.adminaccess:
            self.sendGlobalInternalMail(galaxyName, subject, message)
        return True
                
    def sendGlobalInternalMail(self, galaxyName, subject, message):
        """Send a global message to all players annonymously
        subject = string, message = list of strings"""
        myGalaxy = self.galaxies[galaxyName]
        for empireID, myEmpire in myGalaxy.empires.iteritems():
            if empireID != '0' and myEmpire.ai == 0:
                dMail = {'fromEmpire':myEmpire.id, 'round':myGalaxy.currentRound, 'messageType':'general',
                         'subject':subject, 'body':str(message)}
                myEmpire.genMail(dMail)
                self.sendSMTPMail(galaxyName, myEmpire.player, subject, message)

    def xmlrpc_askForHelp(self, clientKey):
        """Ask Server for a detailed Report"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                return myEmpire.askForHelp(1)
            else:
                s = 'invalid key: cannot askForHelp'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->askForHelp error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_forceEndRound(self, adminKey):
        """Force the end of the round, this is an admin function only"""
        try:
            # check adminPassword
            adminPassword = adminKey['adminPassword']
            galaxyName = adminKey['galaxyName']
            if adminPassword == globals.adminaccess:
                return endRound(self, galaxyName)
            else:
                s = 'server->ForceEndRound Permission Denied'
                self._Log(s)
                return s
        except:
            s = 'server->forceEndRound Error'
            self._Log(s)
            return s
        
    def xmlrpc_forceSave(self, adminKey):
        """Force the saving of all galaxies"""
        try:
            # check adminPassword
            adminPassword = adminKey['adminPassword']
            galaxyName = adminKey['galaxyName']
            if adminPassword == globals.adminaccess:
                return saveAllGalaxies(self)
            else:
                s = 'server->forceSave Permission Denied'
                self._Log(s)
                return s
        except:
            s = 'server->forceSave Error'
            self._Log(s)
            return s
    
    def xmlrpc_getEmpireUpdate(self, clientKey, listAttr):
        """Return Empire update for specified attributes only"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                d = myEmpire.getSelectedAttr(listAttr)
                self._Log('getEmpireUpdate Success', clientKey)
                return d
            else:
                s = 'invalid key: cannot get Empire Update'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getEmpireUpdate error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_getGalaxyUpdate(self, listAttr, clientKey):
        """return Galaxy update for specified attributes only"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                d = myGalaxy.getSelectedAttr(listAttr)
                self._Log('getGalaxyUpdate Success', clientKey)
                return d
            else:
                s = 'invalid key: cannot get Galaxy Update'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getGalaxyUpdate error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_getShipBattle(self, clientKey, shipBattleKey):
        """Retreive serialized ship battle object from galaxy"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.getShipBattle(clientKey['empireID'], shipBattleKey)
                if type(result) == types.StringType:
                    self._Log('getShipBattle Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot getShipBattle'
                self._Log(s, clientKey)
                return -1
        except:
            s = 'server->getShipBattle error'
            self._Log(s, clientKey)
            return -1

    def xmlrpc_getShipBattleDict(self, clientKey):
        """Return a dictionary key=shipBattleKey, value = shipbattle description"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                d = myEmpire.getShipBattleDict()
                if type(result) == types.DictType:
                    self._Log('getShipBattleDict Success')
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot getShipBattleDict'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getShipBattleDict error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_getSystemUpdate(self, listAttr, systemID, clientKey):
        """return System update for specified attributes only"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                mySystem = myGalaxy.systems[systemID]
                d = mySystem.getSelectedAttr(listAttr)
                self._Log('getSystemUpdate Success', clientKey)
                return d
            else:
                s = 'invalid key: cannot get System Update'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getSystemUpdate error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_getEmpireOrders(self, clientKey, orderTypeName):
        """Retreive latest Empire orders by order type name"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.getMyOrdersByRound(orderTypeName)
                if type(result) == types.DictType:
                    self._Log('getEmpireOrders:%s Success' % orderTypeName, clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot get Orders:%s' % orderTypeName
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getEmpireOrders:%s error' % orderTypeName
            self._Log(s, clientKey)
            return s      
    
    def xmlrpc_getTradeRoutes(self, clientKey, tradeRouteID=''):
        """Retreive latest trade routes from galaxy"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                if tradeRouteID in myGalaxy.tradeRoutes.keys():
                    result = myGalaxy.getOneTradeRouteInfo(tradeRouteID)
                else:
                    result = myGalaxy.getMyTradeRouteInfo(clientKey['empireID'])
                if type(result) == types.DictType:
                    self._Log('getTradeRoutes Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot get trade routes'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getTradeRoutes error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_getMailUpdate(self, clientKey, listMailID):
        """Retreive latest mail messages from server"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.getMailUpdate(listMailID)
                if type(result) == types.DictType:
                    self._Log('getMailUpdate Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot getMailUpdate'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getMailUpdate error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_surrender(self, clientKey):
        """Player is surrendering from the game"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                myEmpire.setAIinControl()
                subject = '%s Has Surrendered' % myEmpire.name
                message = '%s has surrendered and will no longer be playing in this game, any remaining units will be AI controlled' % myEmpire.name
                self.sendGlobalInternalMail(myGalaxy.name, subject, [message])
                myGalaxy.endEmpireTurn(myEmpire)
                return 1
        except:
            s = 'server->getMailUpdate error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_getMarketOrders(self, clientKey):
        """Retreive latest market orders from galaxy"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.getMyMarketOrders(clientKey['empireID'])
                if type(result) == types.DictType:
                    self._Log('getMarketOrders Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot get market orders'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->getMarketOrders error'
            self._Log(s, clientKey)
            return s 
    
    def xmlrpc_changeCityIndustry(self, clientKey, systemID, newIndustryList):
        """Change city industry for system specified
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                mySystem = myGalaxy.systems[systemID]
                result = mySystem.validateUpdateCityIndustry(myEmpire.id, newIndustryList)
                if result == 1:
                    result = mySystem.updateCityIndustry(newIndustryList)
                    self._Log('changeCityIndustry Success', clientKey)
                    return result
                else:
                    self._Log(result, clientKey)
                    return result
            else:
                s = 'invalid key: cannot add Industry Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->changeCityIndustry error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_addIndustry(self, clientKey, systemID, industryNum, industryType):
        """Add industry for system specified}
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                mySystem = myGalaxy.systems[systemID]
                result = mySystem.validateAddIndustry(myEmpire.id, industryNum, industryType)
                if result == 1:
                    result = mySystem.payForAddIndustry(industryNum, industryType)
                    if result == 1:
                        result = mySystem.addIndustry(industryNum, industryType)
                        self._Log('addIndustry Success', clientKey)
                        return result
                    else:
                        self._Log(result, clientKey)
                        return result
                else:
                    self._Log(result, clientKey)
                    return result
            else:
                s = 'invalid key: cannot add Industry'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addIndustry error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_removeIndustry(self, clientKey, systemID, industryNum, industryType):
        """Remove industry for system specified
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                mySystem = myGalaxy.systems[systemID]
                result = mySystem.validateRemoveIndustry(myEmpire.id, industryNum, industryType)
                if result == 1:
                    result = mySystem.removeIndustry(industryNum, industryType)
                    if result == 1:
                        result = mySystem.refundForRemoveIndustry(industryNum, industryType)
                        self._Log('removeIndustry Success', clientKey)
                        return result
                    else:
                        self._Log(result, clientKey)
                        return result
                else:
                    self._Log(result, clientKey)
                    return result
            else:
                s = 'invalid key: cannot remove Industry'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->removeIndustry error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_addIndustryOrder(self, clientKey, indOrderDict):
        """Add an Industry Order, 
        input: clientKey (dict)
               indOrderDict
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.genIndustryOrder(indOrderDict)
                if result == 1:
                    self._Log('addIndustryOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Industry Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addIndustryOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_modifyShipOrder(self, clientKey, orderID, change):
        """Modify a Ship Build order, 
        input: clientKey (dict)
        order ID and change (negative allowed)
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                if orderID not in myEmpire.industryOrders.keys() or change == 0:
                    return 'Invalid Order to modify'
                myOrder = myEmpire.industryOrders[orderID]
                (amount, shipType) = string.split(myOrder.value, '-')
                amount = int(amount)
                mySystem = myGalaxy.systems[myOrder.system]
                diff = amount+change
                if diff < 0:
                    return 'Cannot Remove more ships then in Ship Build Order'
                if diff == 0:
                    myEmpire.cancelIndustryOrder(orderID)
                    return 0
                if diff > 0:
                    if change < 0:
                        myOrder.value = '%d-%s' % (diff, shipType)
                        result = mySystem.refundAddShip(abs(change), shipType)
                        if result == 1:
                            return diff
                        else:
                            return 'Error in Refunding Ship Order Modification'
                    else:
                        result = mySystem.validateAddShip(change, shipType)
                        if result == 1:
                            result = mySystem.payForAddShip(change, shipType)
                            if result == 1:
                                myOrder.value = '%d-%s' % (diff, shipType)
                                return diff
                        else:
                            return result
            else:
                s = 'invalid key: cannot Modify Ship Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->modifyShipOrder error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_modifyRegimentOrder(self, clientKey, orderID, change):
        """Modify a Regiment Build order, 
        input: clientKey (dict)
        order ID and change (negative allowed)
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                if orderID not in myEmpire.industryOrders.keys() or change == 0:
                    return 'Invalid Order to modify'
                myOrder = myEmpire.industryOrders[orderID]
                (amount, regType) = string.split(myOrder.value, '-')
                amount = int(amount)
                mySystem = myGalaxy.systems[myOrder.system]
                diff = amount+change
                if diff < 0:
                    return 'Cannot Remove more regiments then in Regiment Build Order'
                if diff == 0:
                    myEmpire.cancelIndustryOrder(orderID)
                    return 0
                if diff > 0:
                    if change < 0:
                        myOrder.value = '%d-%s' % (diff, regType)
                        result = mySystem.refundAddRegiment(abs(change), regType)
                        if result == 1:
                            return diff
                        else:
                            return 'Error in Refunding Regiment Order Modification'
                    else:
                        result = mySystem.validateAddRegiment(change, regType)
                        if result == 1:
                            result = mySystem.payForAddRegiment(change, regType)
                            if result == 1:
                                myOrder.value = '%d-%s' % (diff, regType)
                                return diff
                        else:
                            return result
            else:
                s = 'invalid key: cannot Modify Regiment Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->modifyRegimentOrder error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_addTechOrder(self, clientKey, techOrderDict):
        """Add a Tech Order, 
        input: clientKey (dict)
               techOrderDict
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.genTechOrder(techOrderDict)
                if result == 1:
                    self._Log('addTechOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Tech Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addTechOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_addTradeRoute(self, clientKey, tradeRouteDict):
        """Add a Trade Route, 
        input: clientKey (dict)
               tradeRouteDict
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.genTradeRoute(tradeRouteDict)
                if result == 1:
                    self._Log('addTradeRoute Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Trade Route'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addTradeRoute error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_addMarketOrder(self, clientKey, dOrder):
        """Add a Market Order, 
        input: clientKey (dict)
               dOrder
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.genMarketOrder(dOrder)
                if type(result) == types.DictionaryType:
                    self._Log('addMarketOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Market Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addMarketOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_addShipDesign(self, clientKey, designDict):
        """Submit a ship design, 
        input: clientKey (dict)
               designDict
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.genShipDesign(designDict['name'], designDict['hullID'],
                                                designDict['compDict'], designDict['weaponDict'])
                if type(result) != types.StringType:
                    self._Log('addShipDesign Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Ship Design'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addShipDesign error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_addDroneDesign(self, clientKey, designDict):
        """Submit a drone design, 
        input: clientKey (dict)
               designDict
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.genDroneDesign(designDict['name'], designDict['hullID'],
                                                 designDict['compDict'], designDict['weaponDict'])
                if type(result) != types.StringType:
                    self._Log('addDroneDesign Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot add Drone Design'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->addDroneDesign error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_cancelIndustryOrder(self, clientKey, orderID):
        """Cancel an Industry Order, 
        input: clientKey (dict)
               orderID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.cancelIndustryOrder(orderID)
                if result == 1:
                    self._Log('cancelIndustryOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Industry Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->cancelIndustryOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelShipyardOrder(self, clientKey, orderID):
        """Cancel a Shipyard Order, 
        input: clientKey (dict)
               orderID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.cancelShipyardOrder(orderID)
                if result == 1:
                    self._Log('cancelShipyardOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Shipyard Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->cancelShipyardOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelTradeRoute(self, clientKey, tradeID):
        """Cancel a Trade Route, 
        input: clientKey (dict)
               tradeID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.cancelTradeRoute(tradeID, myGalaxy.currentRound)
                if result == 1:
                    self._Log('cancelTradeRoute Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Trade Route'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->cancelTradeRoute error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelMarketOrder(self, clientKey, orderID):
        """Cancel a Market Order, 
        input: clientKey (dict)
               orderID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.cancelMarketOrder(orderID)
                if result == 1:
                    self._Log('cancelMarketOrder Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Market Order'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->cancelMarketOrder error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_removeShipDesign(self, clientKey, designID):
        """Remove a Ship Design, 
        input: clientKey (dict)
               designID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.removeShipDesign(designID)
                if result == 1:
                    self._Log('removeShipDesign Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot remove Ship Design'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->removeShipDesign error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_removeDroneDesign(self, clientKey, designID):
        """Remove a Drone Design, 
        input: clientKey (dict)
               designID
        """
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.removeDroneDesign(designID)
                if result == 1:
                    self._Log('removeDroneDesign Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot remove Drone Design'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->removeDroneDesign error'
            self._Log(s, clientKey)
            return s

    def xmlrpc_endEmpireTurn(self, clientKey):
        """End the Empires round of play"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                myEmpire.ai = 0
                result = myGalaxy.endEmpireTurn(myEmpire, self.singleplayer)
                if result == 1:
                    # all empires are done their turn, end round
                    self._Log('endEmpireTurn Success', clientKey)
                    return 2
                elif result == 0:
                    # write status to website
                    if self.singleplayer == 0:
                        self.writeGameStatus()
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot endEmpireTurn'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->endEmpireTurn error: %s'%str(sys.exc_info())
            self._Log(s, clientKey)
            return s

    def xmlrpc_endRound(self, clientKey):
        """End the Empires round of play"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                return endRound(self, myGalaxy.name)
            else:
                s = 'invalid key: cannot endEmpireTurn'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->endRound error: %s'%str(sys.exc_info())
            self._Log(s, clientKey)
            return s    
        
    def xmlrpc_getGalaxies(self):
        """Return list of Galaxy Names"""
        try:
            dict = {}
            list = self.galaxies.keys()
            self._Log('getGalaxies Success')
            return list
        except:
            s = 'server->getGalaxies error'
            self._Log(s)
            return s
    
    def xmlrpc_login(self, loginKey):
        """Return game information if login works"""
        try:
            result = self._ValidateLogin(loginKey)
            if result == 1:
                myGalaxy = self.galaxies[loginKey['galaxyName']]
                myEmpire = myGalaxy.empires[loginKey['empireID']]
                # update help
                myEmpire.askForHelp(0)

                # update empire login info
                myEmpire.ip = loginKey['ip']
                myEmpire.key = self._generateKey()
                empireDict = myGalaxy.getAllEmpireInfo(loginKey['empireID'])
                galaxyDict = myGalaxy.getMyInfoAsDict()
                systemDict = myGalaxy.getAllSystemInfo(myEmpire.id)
                tradeRoutesDict = myGalaxy.getMyTradeRouteInfo(loginKey['empireID'])
                marketOrders = myGalaxy.getMyMarketOrders(loginKey['empireID'])
                marketStats = myGalaxy.getMyDictInfo('marketStats')
                empireStats = myEmpire.getMyDictInfo('empireStats')
                techDict = myEmpire.getMyDictInfo('techTree')
                shipDesignsDict = myEmpire.getMyShipDesigns()
                droneDesignsDict = myEmpire.getMyDroneDesigns()
                myCaptains = myGalaxy.getMyCaptains(loginKey['empireID'])
                (myShips,myArmadas,otherArmadas,warpedArmadas) = myGalaxy.getMyShips(loginKey['empireID'])
                (myRegiments,myArmies,otherArmies,warpedArmies) = myGalaxy.getMyRegiments(loginKey['empireID'])
                shipBattleDict = myEmpire.getShipBattleDict()
                dict = {'myGalaxy':galaxyDict, 'allEmpires':empireDict, 
                        'allSystems':systemDict, 'myTech':techDict, 'tradeRoutes':tradeRoutesDict,
                        'marketOrders':marketOrders, 'marketStats':marketStats, 'prices':myGalaxy.prices,
                        'shipDesignsDict':shipDesignsDict, 'droneDesignsDict':droneDesignsDict, 
                        'myCaptains':myCaptains, 'myShips':myShips, 'myArmadas':myArmadas, 
                        'otherArmadas':otherArmadas, 'warpedArmadas':warpedArmadas, 'shipBattleDict':shipBattleDict, 
                        'myRegiments':myRegiments, 'myArmies':myArmies, 'otherArmies':otherArmies, 'empireStats':empireStats, 
                        'warpedArmies':warpedArmies}
                self._Log('login Success', loginKey)
                s = str(dict)
                s = funcs.compressString(s)
                return s
            else:
                self._Log(result, loginKey)
                return {'error': result}
        except:
            s = 'server->login error'
            self._Log(s, loginKey)
            return {'error': s}
    
    def xmlrpc_logout(self, clientKey):
        """Log Player out of game properly, clear values in empire"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                myEmpire.resetData()
                self._Log('logout Success', clientKey)
                return 1
            else:
                s = 'invalid key: cannot Logout Properly, Please Re-Logout'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->logout error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_decreaseDiplomacy(self, clientKey, empireID):
        """Decrease Diplomacy with empire specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.decreaseDiplomacy(empireID)
                if result == 1:
                    self._Log('decreaseDiplomacy Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot decreaseDiplomacy'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->decreaseDiplomacy error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_increaseDiplomacy(self, clientKey, empireID):
        """Increase Diplomacy with empire specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.increaseDiplomacy(empireID)
                if result == 1:
                    self._Log('increaseDiplomacy Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot increaseDiplomacy'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->increaseDiplomacy error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_moveShips(self, clientKey, shipList, systemID):
        """Move a ships specified to system specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myGalaxy.moveShips(shipList, myEmpire.id, systemID)
                if result == 1:
                    self._Log('moveShips Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot Move Ships'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server-> moveShips error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_moveReg(self, clientKey, regList, systemID):
        """Move a regiment group specified to system specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myGalaxy.moveReg(regList, myEmpire.id, systemID)
                if result == 1:
                    self._Log('moveReg Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot Move Regiments'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server-> moveReg error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelMoveShips(self, clientKey, shipList):
        """Cancel Moving ships specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myGalaxy.cancelMoveShips(shipList, myEmpire.id)
                if result == 1:
                    self._Log('cancelMoveShips Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Move Ships'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server-> cancelMoveShips error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelMoveReg(self, clientKey, regList):
        """Cancel Moving regiments specified"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myGalaxy.cancelMoveReg(regList, myEmpire.id)
                if result == 1:
                    self._Log('cancelMoveReg Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot cancel Move Regiments'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server-> cancelMoveReg error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_sendMail(self, clientKey, empireID, message):
        """Send Message to Empire"""
        if self.singleplayer == 0:
            try:
                if self._ValidateKey(clientKey) == 1:
                    myGalaxy = self.galaxies[clientKey['galaxyName']]
                    myEmpire = myGalaxy.empires[clientKey['empireID']]
                    toEmpire = myGalaxy.empires[empireID]
                    message = str([message])
                    toEmpire.genMail({'fromEmpire':myEmpire.id, 'round':myGalaxy.currentRound,
                                      'messageType':'general', 'subject':'PERSONAL MESSAGE FROM:%s' % myEmpire.name,
                                      'body':message})
                    myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':myGalaxy.currentRound,
                                      'messageType':'general', 'subject':'SEND THIS MESSAGE TO:%s' % toEmpire.name,
                                      'body':message})
                    subject = '%s - INTERNAL MESSAGE' % myGalaxy.name
                    message = 'You have Recieved an internal message from Empire: %s\n\n%s' % (myEmpire.name, message)
                    self.sendSMTPMail(myGalaxy.name, toEmpire.player, subject, message)
                    return 1
                else:
                    s = 'invalid key: cannot sendMail'
                    self._Log(s, clientKey)
                    return s
            except:
                s = 'server->sendMail error'
                self._Log(s, clientKey)
                return s
    
    #def sendGAEMail(self, galaxy, sourceEmpire, toEmpire, subject, message):
        #if self.singleplayer == 0:
            #try:
                #Services.inject(GAE).sendMail(galaxy, sourceEmpire, toEmpire, subject, message)
            #except:
                #logging.error("Could not send mail: " + str(sys.exc_info()[0]) )

    def sendSMTPMail(self, galaxy, toEmpireName, subject, message):
        if self.singleplayer == 0:
            try:
                #TODO enable email
                #addresses = Services.inject(GAE).getEmailAddressesForUsersInGalaxy(galaxy)
                if addresses:
                    email = Services.inject(Email)
                    email.send(addresses[toEmpireName], subject, message)
                else:
                    logging.warn("Could not get the email address lookup dictionary")
            except:
                logging.error("Could not send mail to: %s, reason: %s"%(toEmpireName, str(sys.exc_info()[0])) )
    
    def xmlrpc_sendCredits(self, clientKey, id, amount):
        """Send Credits to Empire"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.sendCreditsInLieu(id, amount)
                if result == 1:
                    self._Log('sendCredits Success: id=%s, amount=%d' % (id, amount), clientKey)
                return result
            else:
                s = 'invalid key: cannot Send Credits'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->sendCredits error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_cancelSendCredits(self, clientKey, id):
        """Cancel Send Credits to Empire"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.cancelCreditsInLieu(id)
                if result == 1:
                    self._Log('cancelSendCredits Success: id=%s' % id, clientKey)
                return result
            else:
                s = 'invalid key: cannot Cancel Send Credits'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->cancelSendCredits error'
            self._Log(s, clientKey)
            return s
        
    def xmlrpc_setCaptainName(self, clientKey, id, name):
        """Set Captain name given id"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                result = myGalaxy.setCaptainName(clientKey['empireID'], id, name)
                if result == 1:
                    self._Log('setCaptainName Success: id=%s, name=%s' % (id, name), clientKey)
                return result
            else:
                s = 'invalid key: cannot set Captain Name'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->setCaptainName error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_setEmpire(self, clientKey, dAttributes):
        """Set some attributes for an Empire"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                myEmpire.setAttributes(dAttributes)
                self._Log('setEmpire Success: attr=%s' % str(dAttributes), clientKey)
                return 1
            else:
                s = 'invalid key: cannot set Empire Attributes'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->setEmpire error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_setRegimentOrder(self, clientKey, regimentID, order):
        """Set Regiment Order"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                myRegiment = myGalaxy.regiments[regimentID]
                result = myRegiment.setMyOrder(order)
                if type(result) == types.ListType:
                    self._Log('setRegimentOrder Success: %s' % order, clientKey)
                    myRegiment.setMyPotentialOrders()
                    return (myRegiment.getMyRegimentInfo(), result)
                elif type(result) == types.StringType:
                    self._Log(result, clientKey)
                    return result
            else:
                s = 'invalid key: cannot setRegimentOrder'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->setRegimentOrder error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_shareShipBattle(self, clientKey, empireID, shipBattleKey):
        """Share Battle with another empire"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myEmpire.shareShipBattle(shipBattleKey, empireID)
                if result == 1:
                    self._Log('shareBattle Success', clientKey)
                    return 1
                elif type(result) == types.StringType:
                    self._Log(result, clientKey)
                    return result
            else:
                s = 'invalid key: cannot share Ship Battle'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->shareShipBattle error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_sortAllCaptains(self, clientKey, systemID, shipList):
        """Sort All Captains so that the best captains are in the best Ships"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                mySystem = myGalaxy.systems[systemID]
                result = myGalaxy.sortAllCaptains(myEmpire.id, mySystem.id, shipList)
                if type(result) == types.DictType:
                    self._Log('sortRegiments Success', clientKey)
                elif type(result) == types.StringType:
                    self._Log(result, clientKey)
                else:
                    self._Log('unknown result', clientKey)
                return result
            else:
                s = 'invalid key: cannot sort Captains'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server->sortAllCaptains error'
            self._Log(s, clientKey)
            return s
    
    def xmlrpc_swapCaptains(self, clientKey, shipOneID, shipTwoID):
        """Swap two ship captains"""
        try:
            if self._ValidateKey(clientKey) == 1:
                myGalaxy = self.galaxies[clientKey['galaxyName']]
                myEmpire = myGalaxy.empires[clientKey['empireID']]
                result = myGalaxy.swapCaptains(myEmpire.id, shipOneID, shipTwoID)
                if result == 1:
                    self._Log('swapCaptains Success', clientKey)
                else:
                    self._Log(result, clientKey)
                return result
            else:
                s = 'invalid key: cannot Swap Captains'
                self._Log(s, clientKey)
                return s
        except:
            s = 'server-> swapCaptains error'
            self._Log(s, clientKey)
            return s
    
    def _backupGalaxy(self, galaxyName):
        """Backup the galaxy file"""
        try:
            dbPath = '%s%s/%s.anw' % (self.path, galaxyName, galaxyName)
            try:
                shutil.copyfile(dbPath+'.backup1', dbPath+'.backup2')
            except IOError:
                pass
            try:
                shutil.copyfile(dbPath, dbPath+'.backup1')
            except IOError:
                pass
            self._Log('Backup Galaxy:%s Success' % galaxyName)
            return 1
        except:
            self._Log('backupGalaxy:%s Error' % galaxyName)
            return 'server->backupGalaxy error'   
    
    def _generateKey(self):
        """Generate a unique key"""
        rand = random.Random()
        key = ''
        for i in range(20):
          key += str(rand.randrange(0, 9))
        return key
    
    def _Log(self, message, myKey = None):
        """Write a Message to the Server Log"""
        if type(myKey) == types.DictType:
            galaxyName = myKey['galaxyName']
            myGalaxy = self.galaxies[galaxyName]
            myEmpire = myGalaxy.empires[myKey['empireID']]
            message = '[galaxy=%s, empireID=%s, userIP=%s, round=%d] %s\n' % (myKey['galaxyName'], myKey['empireID'], myKey['ip'], myKey['round'], message)
        self.log.info(message)
    
    def _LoadGalaxies(self, galaxyName):
        """Load all Galaxy Data Files into object memory"""
        if galaxyName == None:
            # load all galaxy files in database sub folders
            for path, subdirs, files in os.walk(self.path):
                for name in subdirs:
                    if 'ANW' in name:
                        self._LoadGalaxy(name)
        else:
            self._LoadGalaxy(galaxyName)

    def _LoadGalaxy(self, name):
        """attempt to load galaxy to memory given name of galaxy (eg: ANW1)"""
        galaxyFilename = '%s%s/%s.anw' % (self.path,name,name)
        galaxy = storedata.loadFromFile(galaxyFilename)
        self.galaxies[galaxy.name] = galaxy
        self._Log('Loading Galaxy:' + galaxy.name)

    def _ValidateKey(self, clientKey):
        """All Server Requests have to have the client key verified"""
        try:
            galaxyName = clientKey['galaxyName']
            empireID = clientKey['empireID']
            myKey = clientKey['key']
            ip = clientKey['ip']
            round = clientKey['round']
            
            # verify galaxy
            if self.galaxies[galaxyName]:
                galaxy = self.galaxies[galaxyName]
            else:
                self._Log('Invalid key: galaxy not in database', myKey)
                return 0
            
            # verfigy galaxy is not ending currently
            if galaxyName in self.endRoundGalaxyFlag:
                self._Log('Cannot Validate: galaxy currently in end round mode', myKey)
                return 0
            
            # verify empire
            if galaxy.empires[empireID]:
                empire = galaxy.empires[empireID]
            else:
                self._Log('Invalid key: empire not in galaxy', myKey)
                return 0

            return 1
        except:
            self._Log('Invalid key: general error', myKey)
            return 0

    def _ValidateLogin(self, myKey):
        """All Login Requests to the server must be validated before being allowed"""
        galaxyName = myKey['galaxyName']
        empireID = myKey['empireID']
        empirePass = myKey['empirePass']
        version = myKey['version']
        ip = myKey['ip']
        self._Log("Validate login: empire: %s, %s"%(empireID, empirePass), myKey)
        # verify galaxy
        s = 'Invalid Login: unknown error'
        try:
            # verify galaxy name
            if self.galaxies[galaxyName]:
                galaxy = self.galaxies[galaxyName]
            else:
                return 'Invalid Login: galaxy not in database'
                
            # verify version
            if 'x' in galaxy.version:
                return 'In Game Bug is currently Being Fixed, Please await email from Administrator'
            elif version != globals.currentVersion:
                return 'This current game requires client version: %s' % globals.currentVersion
                    
            # verify empire
            if galaxy.empires[empireID]:
                empire = galaxy.empires[empireID]
            else:
                return 'Invalid Login: empire not in galaxy'
            
            # verify empire password
            if self.singleplayer == 0:
                if empirePass != galaxy.empires[empireID].password:
                    return 'Invalid Login: empire password is incorrect'
            
            # verify galaxy not in end round state
            if galaxyName in self.endRoundGalaxyFlag:
                return 'Cannot Login, Galaxy currently ending Round, please wait for email'
            
            empire.loggedIn = 1
            empire.IP = ip
            return 1
           
        except:
            return 'Invalid Login: general error',  sys.exc_info()

def endRound(server, galaxyName):
    """End the round of galaxy given"""
    myGalaxy = server.galaxies[galaxyName]
    # first save the galaxy
    result = saveGalaxy(server, galaxyName)
    if result == 1:
        # now make a backup copy of the galaxy
        result = server._backupGalaxy(galaxyName) 
        if result == 1:
            # now actually end the round
            if galaxyName in server.endRoundGalaxyFlag:
                # round already being ended
                return 'Round already being ended for Galaxy:%s' % galaxyName
            else:
                server.endRoundGalaxyFlag.append(galaxyName)
            result = myGalaxy.endRound()
            if result == 1:
                server._Log('EndRound of Galaxy:%s success' % galaxyName)
                #if server.singleplayer == 0:
                    #if Services.inject(GAE).endRound(galaxyName, myGalaxy.currentRound):
                        #logging.info("Successfully ended round in GAE system")
                
                # notify all players of new round
                for empireID, myEmpire in myGalaxy.empires.iteritems():
                    if myEmpire.alive == 1:
                        # build empire message
                        body = 'NEW ROUND OF PLAY, BELOW IS YOUR END ROUND MESSAGES:\n'

                        for key, mail in myEmpire.mailBox.iteritems():
                            if mail.round == myGalaxy.currentRound:
                                # split out mail body (setup as string(list)
                                mailBody = ''
                                list = eval(mail.body)
                                for item in list:
                                    if type(item) == types.StringType:
                                        mailBody = mailBody + item + '\n'
                                    elif type(item) == types.ListType:
                                        for item2 in item:
                                            mailBody = mailBody + item2 + '\n'
                                body = body + '=========================================================\n%s\n' % mailBody
                                
                        server.sendSMTPMail(galaxyName, myEmpire.player,
                                      '%s: New Round:%d' % (galaxyName, myGalaxy.currentRound),
                                      body)
                        
                server.endRoundGalaxyFlag.remove(galaxyName)
                result = saveGalaxy(server, galaxyName)                
                server.writeGameStatus()
                return 1
    server.endRoundGalaxyFlag.remove(galaxyName)
    return 'endRound did not work, reason:%s' % result

def copyGalaxy(server, galaxyName):
    """Copy the current round galaxy"""
    try:
        dbPath = '%s%s/%s.anw' % (server.path, galaxyName, galaxyName)
        myGalaxy = server.galaxies[galaxyName]
        try:
            shutil.copyfile(dbPath, dbPath+'.%d' % myGalaxy.currentRound)
        except IOError:
            server._Log('copyGalaxy:%s IOError' % galaxyName)

        server._Log('copyGalaxy:%s Success' % galaxyName)
        return 1
    except:
        server._Log('copyGalaxy:%s Error' % galaxyName)
        return 'copyGalaxy error'  

def saveGalaxy(server, galaxyName):
    """Save the Galaxy information to disk"""
    try:
        if galaxyName in server.savingGalaxyFlag or galaxyName in server.endRoundGalaxyFlag:
            return 1
        else:
            backup_dir = '%s%s/' % (server.path, galaxyName)
            dbPath = '%s%s.anw' % (backup_dir, galaxyName)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            myGalaxy = server.galaxies[galaxyName]
            server.savingGalaxyFlag.append(galaxyName)
            result = copyGalaxy(server, galaxyName)
            if result == 1:
                result = storedata.saveToFile(myGalaxy, dbPath)
            server.savingGalaxyFlag.remove(galaxyName)
        if result == 1:
            server._Log('SaveGalaxy:%s Success' % galaxyName)
            return 1
        else:
            return result
    except:
        server._Log('SaveGalaxy:%s Error' % galaxyName)
        if galaxyName in server.savingGalaxyFlag:
            server.savingGalaxyFlag.remove(galaxyName)
        return 'server->SaveGalaxy error'

def saveAllGalaxies(server):
    for galaxyName, myGalaxy in server.galaxies.iteritems():
        result = saveGalaxy(server, galaxyName)
        
def endRoundCounter(server):
    """Run as a seperate thread every hour, if a galaxy is out of hours, end the round for galaxy"""
    # go through each galaxy in server
    for galaxyName, myGalaxy in server.galaxies.iteritems():
        if myGalaxy.currentHoursLeft <= 0:
            endRound(server, galaxyName)
        elif myGalaxy.currentHoursLeft == 1:
            # email all players that round will end in one hour
            title = '%s will Force-End Round in 1 hour' % galaxyName
            desc = 'Please end your turn'
            for empireID, myEmpire in myGalaxy.empires.iteritems():
                if myEmpire.roundComplete == 0 and myEmpire.alive == 1:
                    server.sendSMTPMail(galaxyName, myEmpire.player, title, desc)
            myGalaxy.currentHoursLeft -= 1
        else:
            # reduce counter
            myGalaxy.currentHoursLeft -= 1
            # save galaxy
            result = saveGalaxy(server, galaxyName)
    
    # update page
    server.writeGameStatus()
    
