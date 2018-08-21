# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# galaxy.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a working Galaxy of ANW.  A Galaxy is essentially one 
# running game of ANW.
# ---------------------------------------------------------------------------
import random
import string

import anwp.func.root
import anwp.func.storedata
import anwp.func.funcs
import anwp.func.globals
import traderoute
import order
import marketstat
import anwp.war.shipbattle
import anwp.war.shipsimulator
import anwp.war.regiment
import anwp.client.app

class Galaxy(anwp.func.root.Root):
    """A Galaxy object represents one working game of ANW."""
    def __init__(self, args):
        # Attributes
        self.name = str() # name of Galaxy
        self.version = str() # game version Galaxy is playing within
        self.systemSize = int() # graphical size of one system in Galaxy, used for sizing map objects
        self.xMax = int() # total x size of Galactic Map
        self.yMax = int() # total y size of Galactic Map
        self.delayBonus = int() # delay bonus for finishing turn early
        self.password = str() # password to have access to Galaxy
        self.currentRound = int() # Current Round of Play
        self.maxHoursLeft = int(30) # Game Max Hours Set that all Players agree to try and finish turn within
        self.currentHoursLeft = int(30) # Current Hours Left before Round Forced
        self.defaultAttributes = ('name', 'version', 'systemSize', 'xMax','yMax', 'delayBonus', 
                             'password', 'currentRound', 'maxHoursLeft', 'currentHoursLeft')
        self.setAttributes(args)
        
        self.empires = {} # Dict key = empire id, value = empire object
        self.systems = {} # Dict key = system id, value = system object
        self.industrydata = {} # Dict key = industrydata id, value = industrydata object
        self.tradeRoutes = {} # Dict key = tradeRoute id, value = tradeRoute object
        self.marketOrders = {} # Dict key = marketOrder id, value = marketOrder object
        self.marketStats = {} # Dict key = marketStat id, value = marketStat object
        self.componentdata = {} # Dict key = componentdata id, value = obj
        self.shiphulldata = {} # Dict key = shiphulldata id, value = obj
        self.dronehulldata = {} # Dict key = dronehulldata id, value = obj
        self.weapondata = {} # Dict key = weapondata id, value = obj
        self.regimentdata = {} # Dict key = regimentdata id, value = obj
        self.shipBattles = {} # Dict key = ship battle id, value = round of battle
        self.ships = {} # Dict key = ship id, value = obj
        self.regiments = {} # all regiments created key=id, value=obj
        self.captains = {} # all captains created key=id, value=obj
        self.captainNames = [] # list of available captain names to draw from
        self.currentCaptainName = 0 # keep track of each name taken
        self.maxCaptainNames = 500 # max captain names to use
        self.rand = random.Random(19)
        
        # create app and game objects for battle simulation
        self.app = anwp.client.app.Application(0,0,'',0)
        self.app.setIntervalValue(anwp.func.globals.intervalValue)
        
    def cancelMarketOrder(self, orderID):
        """Cancel trade route based on ID Provided"""
        try:
            myOrder = self.marketOrders[orderID]
            result = self.refundMarketOrder(myOrder)
            if result == 1:
                del self.marketOrders[orderID]
            return result
        except:
            return 'galaxy->cancelMarketOrder error'    
    
    def cancelTradeRoute(self, tradeRouteID, round):
        """Cancel trade route based on ID Provided"""
        try:
            # send a message to all Empires involved
            result = self.mailTradeInfo('removed', self.tradeRoutes[tradeRouteID], round)
            if result == 1:
                del self.tradeRoutes[tradeRouteID]
            return result
        except:
            return 'galaxy->cancelTradeRoute error'
        
    def connectSystems(self):
        """Take systems dict and connect them according to the galaxy dimensions
        and systemSize"""
        for id in self.systems.keys():
            mySystem = self.systems[id]
            mySystem.connectedSystems = []
            for id2 in self.systems.keys():
                mySystem2 = self.systems[id2]
                xDist = abs(mySystem.x - mySystem2.x)
                yDist = abs(mySystem.y - mySystem2.y)
                if (xDist + yDist) <> 0 and (xDist <= self.systemSize) and (yDist <= self.systemSize):
                    mySystem.connectedSystems.append(id2)
  
    def endEmpireTurn(self, myEmpire):
        """End the turn for Empire, check if all empires have ended their turns"""
        try:
            # end the Empire's turn
            myEmpire.endTurn()
            
            # check if all Empires turns are done
            done = 1
            for empireID, myEmpire in self.empires.iteritems():
                if myEmpire.roundComplete == 0 and myEmpire.ai == 0:
                    done = 0
                    break
            return done
        except:
            return 'galaxy->endEmpireTurn error'
  
    def endRound(self):
        """End the Round of Play for this galaxy"""
        # first copy
        resultsList = []
        try:
            # calculate research rolls
            researchRolls = anwp.func.funcs.getRandomD100Rolls(100)
                
            # Process for Each Empire
            for empireID, myEmpire in self.empires.iteritems():
                # build industry
                resultsList.append('%s(%s) - buildIndustry:%s' % (myEmpire.name, empireID, myEmpire.buildIndustry()))
                
                # generate income and research points
                resultsList.append('%s(%s) - processSystems:%s' % (myEmpire.name, empireID, myEmpire.processSystems()))
                
                # calculate research orders
                resultsList.append('%s(%s) - calcResearch:%s' % (myEmpire.name, empireID, myEmpire.calcResearch(researchRolls)))
                
                # calculate diplomacy
                resultsList.append('%s(%s) - checkDiplomacy:%s' % (myEmpire.name, empireID, myEmpire.checkDiplomacy()))
            
            # Process trade routes
            resultsList.append('Process Trade Routes:%s' % self.processTradeRoutes())
            
            # Process Market Orders
            resultsList.append('Process Market Orders:%s' % self.processMarketOrders())
            
            # Process all Ship Battles
            resultsList.append('Process Ship Battles:%s' % self.processShipBattles())
            
            # Process all Ground Battles
            resultsList.append('Process Ground Battles:%s' % self.processGroundBattles())
            
            # reset galaxy data
            resultsList.append('Reset galaxy data, increment round')
            self.printResults(resultsList)
            self.resetData()
            return 1
        except:
            return 'galaxy->endRound error'
        
    def genTradeRoute(self, tradeRouteDict):
        """Generate a trade route
        type = GEN or REG"""
        try:
            # add order id
            id = '%s-%s-%s' % (tradeRouteDict['fromSystem'], tradeRouteDict['toSystem'], tradeRouteDict['type'])
            d = {'id':id}
            for key, value in tradeRouteDict.iteritems():
                d[key] = value
            # validate trade route
            result = self.validateTradeRoute(d)
            if result == 1:
                # valid route, process
                myTradeRoute = traderoute.TradeRoute(d)
                myTradeRoute.setMyGalaxy(self)
                myTradeRoute.getWarpRequired()
                
                # send a message to all Empires involved
                result = self.mailTradeInfo('created', myTradeRoute, self.currentRound)
            return result
        except:
            return 'galaxy->genTradeRoute error'
    
    def genMarketStat(self):
        """Generate a market Stat"""
        myMarketStat = marketstat.MarketStat({'id':str(self.currentRound)})
        self.marketStats[str(self.currentRound)] = myMarketStat
        # set avg price to last rounds market avg price
        if self.currentRound > 1:
            lastMarketStat = self.marketStats[str(self.currentRound-1)]
            myMarketStat.avgSoldAL = lastMarketStat.avgSoldAL
            myMarketStat.avgSoldEC = lastMarketStat.avgSoldEC
            myMarketStat.avgSoldIA = lastMarketStat.avgSoldIA
    
    def genMarketOrder(self, orderDict):
        """Generate a market order"""
        try:
            # validate market order
            result = self.validateMarketOrder(orderDict)
            if result == 1:
                # pay for order
                result = self.payForMarketOrder(orderDict)
                if result == 1:
                    # valid, process
                    id = self.getNextID(self.marketOrders)
                    d = {'id':id}
                    for key, value in orderDict.iteritems():
                        d[key] = value
                    d['round'] = self.currentRound
                    myMarketOrder = order.MarketOrder(d)
                    self.marketOrders[id] = myMarketOrder
            return result
        except:
            return 'galaxy->genMarketOrder error'

    def genShipBattle(self, systemID):
        """Generate a ShipBattle object for processing by the Ship Simulator and for
        Ship Battle History storage"""
        mySystem = self.systems[systemID]
        d = {}
        d['id'] = self.getNextID(self.shipBattles)
        d['systemID'] = systemID
        d['systemName'] = mySystem.name
        d['round'] = self.currentRound
        myShipBattle = anwp.war.shipbattle.ShipBattle(d)
        myShipBattle.setSeed()
        empiresDict = {} # dict breakdown of empires involved
        shipsDict = {} # dict breakdown of ships involved
        captainsDict = {} # dict breakdown of captains involved
        targets = 0
        
        # loop through all ships to find the ones that are currently in orbit in this system
        for shipID, myShip in self.ships.iteritems():
            if myShip.toSystem == systemID:
                # set ship position for battle
                myShip.setSystemGrid()
                myShip.setPosition()
                
                # determine target ships
                myShip.clearTargetShips()
                for othershipID, otherShip in self.ships.iteritems():
                    if (otherShip.toSystem == systemID and 
                        otherShip.empireID <> myShip.empireID and
                        anwp.func.globals.diplomacy[self.empires[otherShip.empireID].diplomacy[myShip.empireID].diplomacyID]['engage'] == 1):
                        myShip.addTargetShip(othershipID)
                
                # add to targets
                targets += len(myShip.targets)

                # empire involved in battle
                if not empiresDict.has_key(myShip.empireID):
                    myEmpire = self.empires[myShip.empireID]
                    e = {}
                    e['id'] = myEmpire.id
                    e['name'] = myEmpire.name
                    e['color1'] = myEmpire.color1
                    e['color2'] = myEmpire.color2
                    e['imageFile'] = myEmpire.imageFile
                    e['shipDesigns'] = {}
                    
                    # add drone design info
                    e['droneDesigns'] = {}
                    for droneDesignID, droneDesign in myEmpire.droneDesigns.iteritems():
                        e['droneDesigns'][droneDesignID] = droneDesign.getMyShipDesignInfo()
                    
                    empiresDict[myShip.empireID] = e
                
                # retrieve ship info
                shipsDict[shipID] = myShip.getMyShipInfo()
                captainsDict[myShip.captainID] = self.captains[myShip.captainID].getMyInfoAsDict()
                
                # add ship design info if required
                if myShip.designID not in empiresDict[myShip.empireID]['shipDesigns'].keys():
                    empiresDict[myShip.empireID]['shipDesigns'][myShip.designID] = myShip.myDesign.getMyShipDesignInfo()
                    
        # if a battle has taken place in this system, create ship battle
        if len(empiresDict.keys()) > 1 and targets > 0:
            myShipBattle.setEmpiresDict(empiresDict)
            myShipBattle.setShipsDict(shipsDict)
            myShipBattle.setCaptainsDict(captainsDict)
            
            # save battle
            if self.currentRound == 1:
                filename = '../Database/ANW.ship'
            else:
                filename = '../Database/%s/%s.ship' % (self.name, myShipBattle.id)
            anwp.func.storedata.saveToFile(myShipBattle, filename)
            myShipBattle.setMyGalaxy(self)
            
            # share this battle with empires involved in battle
            for empireID in empiresDict.keys():
                if empireID <> '1':
                    myEmpire = self.empires[empireID]
                    myEmpire.setMyShipBattle(myShipBattle.id)

    def getAllEmpireInfo(self, empireID):
        """Return dict dict of all empires in galaxy
           give extra info for empire specified by empireID given"""
        empireDict = {}
        for id in self.empires.keys():
            myEmpire = self.empires[id]
            if id == empireID:
                # selected empire is empire given
                d = myEmpire.getMyEmpireInfo()
            else:
                # selected system is not owned, give less info dict
                d = myEmpire.getOtherEmpireInfo()
            empireDict[id] = d
        return empireDict

    def getAllSystemInfo(self, empireID):
        """Return dict dict of all systems in galaxy
           give extra info for systems that are owned by empireID given"""
        systemDict = {}
        for id in self.systems.keys():
            mySystem = self.systems[id]
            if mySystem.myEmpireID == empireID or anwp.func.globals.diplomacy[self.empires[mySystem.myEmpireID].diplomacy[empireID].diplomacyID]['trade'] == 1:
                # selected system is owned by empire given or its not but they have trade agreement
                d = mySystem.getMySystemInfo()
            else:
                # selected system is not owned, give less info dict
                d = mySystem.getOtherSystemInfo()
            
            # only return one intel report
            d['intelReport'] = d['intelReport'][empireID]
            systemDict[id] = d
        return systemDict
  
    def getCaptainName(self):
        """Retreive the latest captain name"""
        if self.currentCaptainName == self.maxCaptainNames-50:
            # used up all captain names, build a new list of names
            self.setCaptainNames()
        # grab the latest name
        name = '%s %s' % (self.captainNames[self.currentCaptainName], self.captainNames[self.currentCaptainName+1])
        self.currentCaptainName += 2
        return name
  
    def getShipUpdate(self, empireID, shipList):
        """Return dict specifically to ship movement changes only"""
        d = {}
        for shipID in shipList:
            myShip = self.ships[shipID]
            myShip.setAvailSystems()
            dShip = {}
            if myShip.empireID == empireID:
                dShip['availSystems'] = myShip.availSystems
                dShip['toSystem'] = myShip.toSystem
                dShip['systemGrid'] = myShip.systemGrid
                dShip['currentTransport'] = myShip.currentTransport
                d[shipID] = dShip
        return d
    
    def getMyShips(self, empireID):
        """Return all of my ship/armada information from galaxy"""
        myShipsDict = {}
        myArmadasDict = {}
        otherArmadasDict = {}
        for shipID, myShip in self.ships.iteritems():
            if myShip.empireID == empireID:
                myShipsDict[shipID] = myShip.getMyShipInfo()
                if not (myArmadasDict.has_key(myShip.toSystem)):
                    # add new armada to this system
                    myArmadasDict[myShip.toSystem] = [myShip.id]
                else:
                    # existing armada, add to ship id list
                    myArmadasDict[myShip.toSystem].append(myShip.id)
            else:
                # other ship, add to other armada dict
                if not (otherArmadasDict.has_key(myShip.fromSystem)):
                    # add new armada to this system
                    otherArmadasDict[myShip.fromSystem] = [myShip.empireID]
                else:
                    # existing armada, append ship empire owner
                    if myShip.empireID not in otherArmadasDict[myShip.fromSystem]:
                        otherArmadasDict[myShip.fromSystem].append(myShip.empireID)
                
        return (myShipsDict, myArmadasDict, otherArmadasDict)
  
    def getMyCaptains(self, empireID):
        """Return all Captain info as dict for captains in this empire employ"""
        d = {}
        for captainID, myCaptain in self.captains.iteritems():
            if myCaptain.empireID == empireID:
                d[captainID] = myCaptain.getMyInfoAsDict()
        return d
  
    def getMyRegiments(self, empireID):
        """Return all of my regiment/army information from galaxy"""
        myRegimentsDict = {}
        myArmiesDict = {}
        otherArmiesDict = {}
        for regimentID, myRegiment in self.regiments.iteritems():
            if myRegiment.empireID == empireID:
                myRegimentsDict[regimentID] = myRegiment.getMyRegimentInfo()
                # find systemID regiment is currently "at", this decides if army icon required
                systemID = myRegiment.getMyCurrentSystemID()
                if not (myArmiesDict.has_key(systemID)):
                    # add new army to this system
                    myArmiesDict[systemID] = [myRegiment.id]
                else:
                    # existing army, add to regiment id list
                    myArmiesDict[systemID].append(myRegiment.id)
            else:
                # other regiment, add to other army dict
                if not (otherArmiesDict.has_key(myRegiment.fromSystem)):
                    # add new army to this system
                    otherArmiesDict[myRegiment.fromSystem] = [myRegiment.empireID]
                else:
                    # existing army, append regiment empire owner
                    if myRegiment.empireID not in otherArmiesDict[myRegiment.fromSystem]:
                        otherArmiesDict[myRegiment.fromSystem].append(myRegiment.empireID)
                
        return (myRegimentsDict, myArmiesDict, otherArmiesDict)
  
    def getMyInfoAsDict(self):
        """Return only galaxy information that server wants to give to client"""
        list = ['name', 'version', 'systemSize', 'xMax', 
                'yMax', 'currentRound', 'currentHoursLeft']
        d = self.getSelectedAttr(list)
        return d

    def getMyTradeRouteInfo(self, empireID):
        """Return only trade routes specfic to empire given"""
        d = {}
        tradeRoutesDict = self.getMyDictInfo('tradeRoutes')
        for trID, myTradeRouteDict in tradeRoutesDict.iteritems():
            if (self.systems[myTradeRouteDict['fromSystem']].myEmpire.id == empireID or 
                self.systems[myTradeRouteDict['toSystem']].myEmpire.id == empireID):
                d[trID] = myTradeRouteDict
        return d
    
    def getMyMarketOrders(self, empireID):
        """Return only market orders specfic to empire given"""
        d = {}
        marketOrdersDict = self.getMyDictInfo('marketOrders')
        for marketID, myMarketOrderDict in marketOrdersDict.iteritems():
            if self.systems[myMarketOrderDict['system']].myEmpire.id == empireID:
                d[marketID] = myMarketOrderDict
        return d

    def getShipBattle(self, empireID, shipBattleKey):
        """Return a Ship Battle serialized object"""
        try:
            # grab ship battle from server using key provided.
            # check that key is in ship battle list
            myEmpire = self.empires[empireID]
            if shipBattleKey not in myEmpire.myShipBattles:
                return -1
            try:
                shipBattle = anwp.func.storedata.loadFromFile('../Database/%s/%s.ship' % (self.name, shipBattleKey))
            except:
                return -1
            shipBattle = anwp.func.storedata.saveToString(shipBattle)
            return shipBattle
        except:
            return -1
    
    def getRegimentUpdate(self, empireID, regimentList):
        """Return dict key=regimentID, value=regiment info for selected Regiments"""
        d = {}
        for regimentID in regimentList:
            myRegiment = self.regiments[regimentID]
            myRegiment.setMyPotentialOrders()
            if myRegiment.empireID == empireID:
                d[regimentID] = myRegiment.getMyRegimentInfo()
        return d

    def mailTradeInfo(self, type, tradeRoute, round):
        try:
            """Inform both empires involved in a Trade Route of its status:
            type=created -> trade route created
            type=removed -> trade route removed"""
            systemFrom = self.systems[tradeRoute.fromSystem]
            systemTo = self.systems[tradeRoute.toSystem]
            empireFrom = systemFrom.myEmpire
            empireTo = systemTo.myEmpire
            # only give trade information from other empires
            if empireFrom <> empireTo:
                tradeDetails = ['TRADE DETAILS:',
                                '=============',
                                'From System: %s' % systemFrom.name,
                                'To System: %s' % systemTo.name,
                                '',
                                'Alloys(AL) Sent:%d' % tradeRoute.AL,
                                'Energy(EC) Sent:%d' % tradeRoute.EC,
                                'Arrays(IA) Sent:%d' % tradeRoute.IA]
                
                dMail = {'fromEmpire':empireFrom.id, 'round':round, 'messageType':'trade',
                         'body':str(tradeDetails)}
                if type == 'created':
                    dMail['subject'] = 'Trade Route FROM:%s  TO:%s  <has been CREATED>' % (systemFrom.name, systemTo.name)
                elif type == 'removed':
                    dMail['subject'] = 'Trade Route FROM:%s  TO:%s  <has been REMOVED>' % (systemFrom.name, systemTo.name)
                elif type == 'completed':
                    dMail['subject'] = 'Trade Route FROM:%s  TO:%s  <has COMPLETED>' % (systemFrom.name, systemTo.name)
                else:
                    return 'mailTradeInfo->unrecognized type'
                
                # mail Empires involved in trade route
                if empireFrom == empireTo:
                    empireFrom.genMail(dMail)
                else:
                    empireFrom.genMail(dMail)
                    dMail['fromEmpire'] = empireTo.id
                    empireTo.genMail(dMail)
            return 1
        except:
            return 'galaxy->mailTradeInfo error'
    
    def moveShips(self, shipList, empireID, systemID):
        """Attempt to move ships from list given to system specified"""
        try:
            # init attributes that all ships should share
            shipOne = self.ships[shipList[0]]
            shipOwner = shipOne.empireID
            if shipOwner <> empireID:
                return 'Cannot move ship if it is not yours'
            fromSystem = self.systems[shipOne.fromSystem]
            toSystem = self.systems[systemID]
            newSystemGrid = anwp.func.funcs.getMapQuadrant(fromSystem.x, fromSystem.y,
                                                           toSystem.x, toSystem.y)
            # check if group of ships share these attributes
            for shipID in shipList:
                myShip = self.ships[shipID]
                if myShip.fromSystem.id <> fromSystem.id:
                    return 'Ship %s comes from system: %s' % (myShip.name, fromSystem.name)
                if myShip.empireID <> shipOwner:
                    return 'Ship %s has different empire Owner: %s' % (myShip.name, myShip.empireID)
                
                    
            valid = 0
            # ships have been validated to be going the same place, now validate movement
            for shipID in shipList:
                myShip = self.ships[shipID]
                # can ship be moved?
                if myShip.fromSystem <> myShip.toSystem and systemID <> myShip.fromSystem:
                    return 'Ship %s has already moved' % myShip.name
                # check if ship is platform going out of own empire
                if (myShip.myShipHull.abr[1:] == 'WP' and 
                    (toSystem.myEmpireID <> empireID and anwp.func.globals.diplomacy[self.empires[empireID].diplomacy[toSystem.myEmpireID].diplomacyID]['alliance'] == 0)):
                    return 'Platforms can only move between your systems, they cannot attack.'
                # check that ship is allowed to move to system
                if toSystem.myEmpireID <> empireID and anwp.func.globals.diplomacy[self.empires[empireID].diplomacy[toSystem.myEmpireID].diplomacyID]['move'] == 0:
                    return 'Diplomacy will not allow your ships to move to this system'
                    
                # is ship returning from move this round?
                if systemID == myShip.fromSystem:		
                    # is system adjacent?
                    if myShip.toSystem in fromSystem.connectedSystems:
                        valid = 1
                    else:
                        # refund warp point
                        fromSystem = self.systems[myShip.toSystem]
                        fromSystem.usedWGC -= 1
                        toSystem.usedWGC -= 1
                        valid = 1
                else:
                    # is system adjacent?
                    if systemID in fromSystem.connectedSystems:
                        valid = 1
                    else:
                        # is warp available?
                        if 1 <= (fromSystem.availWGC-fromSystem.usedWGC) and 1 <= (toSystem.availWGC-toSystem.usedWGC):
                            # spend warp points
                            fromSystem.usedWGC += 1
                            toSystem.usedWGC += 1
                            valid = 1
                        else:
                            return 'Not enough Warp Capacity Points to move %s' % myShip.name
            
            if valid == 1:
                # move ships
                for shipID in shipList:
                    myShip = self.ships[shipID]
                    myShip.moveToSystem(newSystemGrid, systemID)
                return 1
            else:
                return 'Not a valid Ship Movement Order'
        except:
            return 'galaxy->moveShips error'
    
    def swapCaptains(self, empireID, shipOneID, shipTwoID):
        """Attempt to swap captains between two ships"""
        try:
            myEmpire = self.empires[empireID]
            shipOne = self.ships[shipOneID]
            shipTwo = self.ships[shipTwoID]
            
            # make sure empire is correct
            if shipOne.empireID <> empireID or shipTwo.empireID <> empireID:
                return 'You cannot switch the captains with another Empires Ship'
            
            # swap ship captains
            captain2 = shipTwo.myCaptain
            shipTwo.setMyCaptain(shipOne.myCaptain)
            shipOne.setMyCaptain(captain2)
            return 1
        except:
            return 'galaxy->swapCaptains error'
    
    def payForMarketOrder(self, dOrder):
        """Actually pay to place market order"""
        try:
            mySystem = self.systems[dOrder['system']]
            amount = dOrder['amount']
            if dOrder['type'] == 'sell':
                # remove resources that system wants to sell
                resource = getattr(mySystem, dOrder['value'])
                if resource - amount < 0:
                    return 'You do not have enough %s to place this SELL order on the market' % dOrder['value']
                else:
                    mySystem.modifyResource(dOrder['value'], -amount)
            else:
                # this is a buy order, remove credits to reserve order with market
                myEmpire = mySystem.myEmpire
                totalCR = amount * dOrder['max']
                if myEmpire.CR < totalCR:
                    return 'You do not have %d CR to place this BUY order on the market' % totalCR
                else:
                    mySystem.payResources(totalCR,0,0,0)
                    
            return 1                
        except:
            return 'galaxy->payForMarketOrder error'
    
    def printResults(self, resultsList):
        """Print the resultsList to the server"""
        for line in resultsList:
            print str(line)
    
    def processMarketOrders(self):
        """Go through all current System Market Orders and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultsList = []
            master = {}
            self.genMarketStat()
            myMarketStat = self.marketStats[str(self.currentRound)]
                
            # sorted lists of market orders
            master['buyAL'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'AL', 'min':0})
            master['buyEC'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'EC', 'min':0})
            master['buyIA'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'IA', 'min':0})
            master['sellAL'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'min', False, {'value':'AL', 'max':0})
            master['sellEC'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'min', False, {'value':'EC', 'max':0})
            master['sellIA'] = anwp.func.funcs.sortDictByChildObjValue(self.marketOrders, 'min', False, {'value':'IA', 'max':0})
            
            for res in ['AL', 'EC', 'IA']:
                for sellOrder in master['sell%s' % res]:
                    # min sell order gets first chance to sell its product
                    if sellOrder.amountUsed == sellOrder.amount:
                        pass # seller has sold all he wants with this order
                    else:
                        i = 0
                        for buyOrder in master['buy%s' % res]:
                            # determine price, allow for bidding on price
                            try:
                                nextBuyOrder = master['buy%s' % res][i+1]
                                if nextBuyOrder.max < buyOrder.max and (nextBuyOrder.max+1) >= sellOrder.min:
                                    price = nextBuyOrder.max + 1
                                else:
                                    price = buyOrder.max
                            except IndexError:
                                price = buyOrder.max
                            # max buy order gets first chance to buy sellers product
                            resultsList.append(self.processMarketTransaction(buyOrder, sellOrder, price))
                            i += 1
                
                # set the average market prices for this round
                if getattr(myMarketStat, 'volSold%s' % res) > 0:
                    setattr(myMarketStat, 'avgSold%s' % res, (getattr(myMarketStat, 'sumSold%s' % res) / 
                                                              getattr(myMarketStat, 'volSold%s' % res)))
            
            # clean up market orders for next round
            for orderID in self.marketOrders.keys():
                myMarketOrder = self.marketOrders[orderID]
                myMarketOrder.cleanUp()
                if myMarketOrder.amount == 0:
                    resultsList.append('cancel market Order=%s' % orderID)
                    self.cancelMarketOrder(orderID)
            
            return str(resultsList)
        except:
            return 'galaxy->processMarketOrders error'

    def processMarketTransaction(self, buyOrder, sellOrder, resolvedPrice):
        """Process a transaction between buyer and seller"""
        try:
            buyOrderAmountLeft = buyOrder.amount - buyOrder.amountUsed
            sellOrderAmountLeft = sellOrder.amount - sellOrder.amountUsed
            myMarketStat = self.marketStats[str(self.currentRound)]
            # go through transaction rules
            if sellOrderAmountLeft == 0:
                return '(%s)seller:%s out of Resources' % (buyOrder.value, sellOrder.id)
            if buyOrder.amountUsed == buyOrder.amount:
                return '(%s)buyer:%s Already has completed transaction' % (buyOrder.value, buyOrder.id)
            elif buyOrderAmountLeft > sellOrderAmountLeft and buyOrder.type == 'buy-all':
                return '(%s)buyer:%s wants to buy all-or-none, buy=%d, sell=%d' % (buyOrder.value, buyOrder.id, buyOrder.amount, sellOrder.amount)
            elif buyOrder.type == 'buy-any' or buyOrderAmountLeft <= sellOrderAmountLeft:
                if resolvedPrice >= sellOrder.min and resolvedPrice <= buyOrder.max:
                    # process Transaction
                    buySystem = self.systems[buyOrder.system]
                    sellSystem = self.systems[sellOrder.system]
                    # determine amount to transact
                    if sellOrderAmountLeft >= buyOrderAmountLeft:
                        actualAmount = buyOrderAmountLeft
                    else:
                        actualAmount = sellOrderAmountLeft
                    # store data for galactic market records
                    setattr(myMarketStat, 'sumSold%s' % buyOrder.value, getattr(myMarketStat, 'sumSold%s' % buyOrder.value) + (actualAmount*resolvedPrice))
                    setattr(myMarketStat, 'volSold%s' % buyOrder.value, getattr(myMarketStat, 'volSold%s' % buyOrder.value) + actualAmount)
                    # remove amount from orders
                    buyOrder.amountUsed += actualAmount
                    sellOrder.amountUsed += actualAmount
                    # calculate credits and refund
                    credits = actualAmount * resolvedPrice
                    refund = (buyOrder.max-resolvedPrice)*actualAmount
                    # give credits to seller
                    sellSystem.payResources(-credits,0,0,0)
                    # give resource and refund to buyer
                    buySystem.payResources(-refund,0,0,0)
                    buySystem.modifyResource(buyOrder.value, actualAmount)
                    # mail Empires result
                    sellSystem.myEmpire.genMail({'fromEmpire':sellSystem.myEmpire.id, 'round':self.currentRound+1, 
                                        'messageType':'market', 'subject':'(%s) - Resource:%s - SOLD: (%d units at %d)' % (sellSystem.name, sellOrder.value, actualAmount, resolvedPrice),
                                        'body':['Remaining Unsold %s from this Order:%d' % (sellOrder.value, sellOrder.amount-sellOrder.amountUsed)]})
                    buySystem.myEmpire.genMail({'fromEmpire':buySystem.myEmpire.id, 'round':self.currentRound+1, 
                                        'messageType':'market', 'subject':'(%s) - Resource:%s - BOUGHT: (%d units at %d)' % (buySystem.name, buyOrder.value, actualAmount, resolvedPrice),
                                        'body':['Remaining Unbought %s from this Order:%d' % (buyOrder.value, buyOrder.amount-buyOrder.amountUsed)]})

                    return 'transaction completed: %s SOLD %d %s to %s for %d price' % (sellSystem.name, actualAmount, sellOrder.value, buySystem.name, resolvedPrice)
                else:
                    return '(%s)resolved price=%d, not in range, seller=%s, buyer=%s' % (buyOrder.value, resolvedPrice, sellOrder.id, buyOrder.id)
            else:
                return 'unknown order type'

        except:
            return 'galaxy->processMarketTransaction error'

    def processGroundBattles(self):
        """Go through all Ground Battles and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultslist = []
            
            # go through each system and check for a battle
            for systemID, mySystem in self.systems.iteritems():
                for regimentID, myRegiment in self.regiments.iteritems():
                    if ((myRegiment.state == 1 and myRegiment.fromSystem == mySystem.id) or
                         (myRegiment.state == 4 and myRegiment.toSystem == mySystem.id)):
                        # regiment is on system, check if its an enemy
                        if (myRegiment.empireID <> mySystem.myEmpireID and
                            anwp.func.globals.diplomacy[self.empires[myRegiment.empireID].diplomacy[mySystem.myEmpireID].diplomacyID]['invade'] == 1):
                            resultslist.append(mySystem.processGroundInvasion())
                            break
                    
            return str(resultslist)
        except:
            return 'galaxy->processGroundBattles error'
        
    def processShipBattles(self):
        """Go through all Ship Battles and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultslist = []
            
            # go through each system and create shipBattle objects
            for systemID, mySystem in self.systems.iteritems():
                self.genShipBattle(systemID)
            
            # go through all new shipBattle objects and resolve the battle at server level
            if self.currentRound > 0:
                for battleID, battleDesc in self.shipBattles.iteritems():
                    (round, name) = string.split(battleDesc, '-')
                    round = int(round)
                    if round == self.currentRound:
                        # load ship battle object for processing
                        myShipBattle = anwp.func.storedata.loadFromFile('../Database/%s/%s.ship' % (self.name, battleID))
                        resultslist.append('New Ship Battle at:%s' % myShipBattle.systemName)
                        # run the battle at server level and update stats
                        resultslist.append(self.runShipBattle(myShipBattle))
                    
            return str(resultslist)
        except:
            return 'galaxy->processShipBattles error'

    def processTradeRoutes(self):
        """Go through all Trade Routes and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultslist = []
            for trID in self.tradeRoutes.keys():
                myTradeRoute = self.tradeRoutes[trID]
                (systemFromID, systemToID, tradeRouteType) = string.split(trID, '-')
                systemFrom = self.systems[systemFromID]
                systemTo = self.systems[systemToID]
                cancel = 0
                warpReq = 0
                # choose trade route type
                if tradeRouteType == 'GEN':
                    # update what system sends based on what it makes
                    myTradeRoute.AL = systemFrom.prodAL
                    myTradeRoute.EC = systemFrom.prodEC
                    myTradeRoute.IA = systemFrom.prodIA
                    
                # check if trade route is adjacent or requires warp gate capacity
                if systemTo.id in systemFrom.warpGateSystems:
                    warpReq = myTradeRoute.getWarpRequired()
                    if warpReq > (systemFrom.availWGC-systemFrom.usedWGC) or warpReq > (systemTo.availWGC-systemTo.usedWGC):
                        cancel = 1
                elif systemTo.id not in systemFrom.connectedSystems:
                    cancel = 1
                    
                if (systemFrom.AL >= myTradeRoute.AL and
                    systemFrom.EC >= myTradeRoute.EC and
                    systemFrom.IA >= myTradeRoute.IA and 
                    cancel == 0):
                    # process trade route
                    systemFrom.AL -= myTradeRoute.AL
                    systemFrom.EC -= myTradeRoute.EC
                    systemFrom.IA -= myTradeRoute.IA
                    systemTo.AL += myTradeRoute.AL
                    systemTo.EC += myTradeRoute.EC
                    systemTo.IA += myTradeRoute.IA
                    # deduct properly if empires are different
                    empireFrom = self.empires[systemFrom.myEmpireID]
                    empireTo = self.empires[systemTo.myEmpireID]
                    if empireFrom <> empireTo:
                        empireFrom.AL -= myTradeRoute.AL
                        empireFrom.EC -= myTradeRoute.EC
                        empireFrom.IA -= myTradeRoute.IA
                        empireTo.AL += myTradeRoute.AL
                        empireTo.EC += myTradeRoute.EC
                        empireTo.IA += myTradeRoute.IA
                    
                    if warpReq > 0:
                        systemFrom.usedWGC += warpReq
                        systemTo.usedWGC += warpReq
                    
                    # mail trade route completion
                    resultslist.append('Trade from System:%s to System:%s complete' % (systemFrom.id, systemTo.id))
                    self.mailTradeInfo('completed', myTradeRoute, nextRound)
                else:
                    cancel = 1
                
                # check if route should be cancelled
                if cancel == 1:
                    resultslist.append('cancel trade route=%s' % myTradeRoute.id)
                    self.cancelTradeRoute(myTradeRoute.id, nextRound)
                elif myTradeRoute.oneTime == 1:
                    resultslist.append('one time trade route=%s' % myTradeRoute.id)
                    self.cancelTradeRoute(myTradeRoute.id, nextRound)
                    
            return str(resultslist)
        except:
            return 'galaxy->processTradeRoutes error'
    
    def refundMarketOrder(self, marketOrder):
        """Refund the cost of the market order"""
        try:
            mySystem = self.systems[marketOrder.system]
            if marketOrder.type == 'sell':
                # refund system resource
                mySystem.modifyResource(marketOrder.value, marketOrder.amount)
            else:
                # refund empire credits
                mySystem.payResources(-(marketOrder.amount * marketOrder.max),0,0,0)
                
            return 1
        except:
            return 'galaxy->refundMarketOrder error'
    
    def removeCaptain(self, captainID):
        """Remove captain from galaxy"""
        del self.captains[captainID]
        
    def removeRegiment(self, regimentID):
        """Remove Regiment from galaxy"""
        myRegiment = self.regiments[regimentID]
        
        # check that no ship was holding this regiment
        if myRegiment.fromShip in self.ships.keys() and myRegiment.state in (2,3):
            myTransport = self.ships[myRegiment.fromShip]
            myTransport.unloadRegiment(regimentID)
        
        myRegiment = None
        del self.regiments[regimentID]

    def removeShip(self, shipID):
        """Remove ship from galaxy"""
        myShip = self.ships[shipID]
        # remove captain first
        myCaptain = myShip.myCaptain
        self.removeCaptain(myCaptain.id)
        # remove ship
        del self.ships[shipID]
    
    def resetData(self):
        """Reset any data that requires reset each round"""
        self.currentHoursLeft = self.maxHoursLeft
        self.currentRound = self.currentRound + 1
        # reset empire data
        for empireID, myEmpire in self.empires.iteritems():
            myEmpire.resetData()
            myEmpire.resetRoundData()
        
        # reset system data
        for systemID, mySystem in self.systems.iteritems():
            mySystem.setWarpConnections()
        
        # reset ship data
        for shipID, myShip in self.ships.iteritems():
            myShip.resetData()
        
        # reset regiment data
        for regimentID, myRegiment in self.regiments.iteritems():
            myRegiment.resetData()
            
        # reset ship orders
        for shipID, myShip in self.ships.iteritems():
            myShip.setAvailSystems()
        
        # reset regiment orders
        for regimentID, myRegiment in self.regiments.iteritems():
            myRegiment.setMyPotentialOrders()
        
        # set intel reports
        for systemID, mySystem in self.systems.iteritems():
            mySystem.setIntelReports()
        
        # set empire stats
        self.setEmpireStats()
    
    def runShipBattle(self, myShipBattle):
        """Run through a Ship Battle"""
        try:
            running = 1
            interval = anwp.func.globals.intervalValue
            game = self.app.game
            myShipBattle.setData(self.componentdata, self.shiphulldata, self.dronehulldata, self.weapondata)
            mode = anwp.war.shipsimulator.ShipSimulator(game, myShipBattle, False, self)
            
            while running:
                if mode.update(interval) == 0:
                    running = 0
            mode = None
            return 'ShipBattle success'
        except:
            return 'galaxy->runShipBattle error: %s' % myShipBattle.systemName
        
    def setCaptainNames(self):
        """Build the captain names list, uses self.id for consitant name generation"""
        self.captainNames = anwp.func.names.getNames('system_names.txt',self.maxCaptainNames+100, self.rand.randint(1,100))
        self.currentCaptainName = 0
    
    def setCaptainName(self, empireID, id, name):
        """Set the name of captain to another"""
        try:
            myCaptain = self.captains[id]
            if myCaptain.empireID <> empireID:
                return 'cannot set captain name not owned by player requesting change'
            # make sure no other captain shares same name
            for captainID, otherCaptain in self.captains.iteritems():
                if otherCaptain.name == name and otherCaptain.id <> id:
                    return 'Another captain already has the name:%s' % name
            myCaptain.setMyName(name)
            return 1
        except:
            return 'error-> could not set captain name'
        
    def setEmpireStats(self):
        """Each Round all Empires are compared to each other for stats which are mailed out"""
        totalEmpires = len(self.empires.keys())
        stats = {'Research':[], 'Fleet Size':[], 'Army Size':[], 'CR Production':[],
                 'AL Production':[],'EC Production':[],'IA Production':[]}
        
        # Calculate Research Stats
        d = {}
        for empireID, myEmpire in self.empires.iteritems():
            if empireID <> '1':
                num = 0
                for techID, myTech in myEmpire.techTree.iteritems():
                    if myTech.complete == 1:
                        num += 1
                d[empireID] = num
        stats['Research'] = anwp.func.funcs.sortDictByValue(d, True)
        
        # Calculate Fleet Stats
        d = {}
        for shipID, myShip in self.ships.iteritems():
            if myShip.empireID <> '1':
                (BV,CR,AL,EC,IA) = myShip.getMyValue()
                if myShip.empireID in d.keys():
                    d[myShip.empireID] += BV
                else:
                    d[myShip.empireID] = BV
        stats['Fleet Size'] = anwp.func.funcs.sortDictByValue(d, True)
        
        # Calculate Army Stats
        d = {}
        for regimentID, myRegiment in self.regiments.iteritems():
            if myRegiment.empireID <> '1':
                (BV,CR,AL,EC,IA) = myRegiment.getMyValue()
                if myRegiment.empireID in d.keys():
                    d[myRegiment.empireID] += BV
                else:
                    d[myRegiment.empireID] = BV
        stats['Army Size'] = anwp.func.funcs.sortDictByValue(d, True)

        # Calculate Production Stats
        for res in ['CR','AL','EC','IA']:
            d = {}
            for systemID, mySystem in self.systems.iteritems():
                if mySystem.myEmpireID <> '1':
                    myValue = getattr(mySystem, 'prod%s' % res)
                    if mySystem.myEmpireID in d.keys():
                        d[mySystem.myEmpireID] += myValue
                    else:
                        d[mySystem.myEmpireID] = myValue
                    myEmpire = self.empires[mySystem.myEmpireID]
                    myEmpireValue = getattr(myEmpire, 'totalProd%s' % res)
                    setattr(myEmpire, 'totalProd%s' % res, myEmpireValue+myValue)
            
            stats['%s Production' % res] = anwp.func.funcs.sortDictByValue(d, True)
        
        # calculate top captains
        d = {}
        for captainID, myCaptain in self.captains.iteritems():
            if myCaptain.myEmpire.id <> '1':
                myCaptain.resetData()
                d[myCaptain.id] = myCaptain.experience
        topCaptains = anwp.func.funcs.sortDictByValue(d, True)
        topCaptains = topCaptains[:2*len(self.empires.keys())]
        
        # Send out Stats to each Empire
        for empireID, myEmpire in self.empires.iteritems():
            if empireID <> '1':
                title = 'Round:%d Statistics' % self.currentRound
                body = ['%s ROUND %d STATS:' % (myEmpire.name, self.currentRound)]
                body.append('====================================================')
                for item in ['Research','Fleet Size', 'Army Size', 'CR Production',
                             'AL Production', 'EC Production', 'IA Production']:
                    if empireID in stats[item]:
                        body.append('You are %s in %s' % (anwp.func.funcs.getNiceNumber(stats[item].index(empireID)+1), item))
                        
                # total production
                body.append('')
                body.append('TOTAL EMPIRE PRODUCTION OVER %d ROUNDS:' % self.currentRound)
                body.append('====================================================')
                for res in ['CR','AL','EC','IA']:
                    body.append('Total %s Production:  %d' % (res, getattr(myEmpire, 'totalProd%s' % res)))

                # legendary captains
                body.append('')
                body.append('TOP %d STARSHIP CAPTAINS in ROUND %d:' % ((2*len(self.empires.keys()), self.currentRound)))
                body.append('====================================================')
                for captainID in topCaptains:
                    myCaptain = self.captains[captainID]
                    myCaptain.promoteMe()
                    body.append('%s ---> RANK:%s -- EXP:%d -- %s' % (string.upper(myCaptain.name), myCaptain.rank, myCaptain.experience, string.upper(myCaptain.myEmpire.name)))
                
                myEmpire.genMail({'fromEmpire':empireID, 'round':self.currentRound,
                                  'messageType':'general', 'subject':title, 'body':body})

    def setNewRegiment(self, empireID, systemID, typeID, name='Marine'):
        """Create a new regiment for empire on system"""
        id = self.getNextID(self.regiments)
        myEmpire = self.empires[empireID]
        myRegiment = anwp.war.regiment.Regiment({'id':id, 'empireID':myEmpire.id, 
                                        'fromSystem':systemID, 'state':1, 'typeID':typeID})
        myRegiment.setMyGalaxy(self)
        myRegiment.setMyStatus(name)
        myRegiment.setMyPotentialOrders()
        return myRegiment
    
    def validateTradeRoute(self, tradeRouteDict):
        """Validate generating trade route, return 1=pass, string=fail"""
        try:
            systemFrom = self.systems[tradeRouteDict['fromSystem']]
            systemTo = self.systems[tradeRouteDict['toSystem']]
            # has a trade route already been setup between these planets?
            (sysFrom, sysTo, type) = string.split(tradeRouteDict['id'], '-')
            # are these systems adjacent, or share a warp gate with a trade pact
            if systemTo.id in systemFrom.connectedSystems:
                pass
            elif systemTo.id in systemFrom.warpGateSystems:
                tempRoute = anwp.aw.traderoute.TradeRoute(tradeRouteDict)
                warpReq = tempRoute.getWarpRequired()
                if warpReq > (systemFrom.usedWGC + systemFrom.availWGC):
                    return 'System:%s Requires %d Warp Capactiy to setup this Trade Route' % (systemFrom.name, warpReq)
                if warpReq > (systemTo.usedWGC + systemTo.availWGC):
                    return 'System:%s Requires %d Warp Capactiy to setup this Trade Route' % (systemTo.name, warpReq)
            else:
                return 'Systems are not adjacent and have no warp gates between them'
            # do these systems share the same empire owner, or are the two empires in a trade pact?
            if systemFrom.myEmpireID <> systemTo.myEmpireID and anwp.func.globals.diplomacy[self.empires[systemFrom.myEmpireID].diplomacy[systemTo.myEmpireID].diplomacyID]['trade'] == 0:
                return 'System Owners are not the same, or no Trade Pact in Effect'
            # is a negative trade route being sent?
            if (tradeRouteDict['AL'] < 0 or tradeRouteDict['EC'] < 0 or tradeRouteDict['IA'] < 0):
                return 'you cannot send negative values in trade'
            # is something being sent?
            if (tradeRouteDict['AL'] == 0 and tradeRouteDict['EC'] == 0 and tradeRouteDict['IA'] == 0) and tradeRouteDict['type'] <> 'GEN':
                return 'no resources are being sent, trade route invalid'
            # does the system have the resources to setup this trade?
            if (systemFrom.AL < tradeRouteDict['AL'] or systemFrom.EC < tradeRouteDict['EC'] or
                systemFrom.IA < tradeRouteDict['IA']):
                return '%s does not have enough resources to setup this trade route' % systemFrom.name
            return 1
        except:
            return 'galaxy->validateTradeRoute error'
    
    def validateMarketOrder(self, orderDict):
        """Validate Market Order, return 1=pass, string=fail"""
        try:
            if (orderDict['amount'] == 0 or (orderDict['min'] == 0 and orderDict['max'] == 0)):
                return 'You must place an order with a min/max and amount > 0'
            return 1
        except:
            return 'galaxy->validateMarketOrder error'
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_galaxy.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
