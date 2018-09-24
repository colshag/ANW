# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# galaxy.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a working Galaxy of ANW.  A Galaxy is essentially one 
# running game of ANW.
# ---------------------------------------------------------------------------
from anw.func import root, storedata, funcs, globals, names
from anw.gae.access import GAE
from anw.util.Injection import Services
from anw.war import regiment, shipbattle, captain, ship, shipdesign
import marketstat
import order
import os
import random
import string
import traderoute
import galacticmarket

class Galaxy(root.Root):
    """A Galaxy object represents one working game of ANW."""
    def __init__(self, args):
        # Attributes
        self.name = str() # name of Galaxy
        self.version = str() # game version Galaxy is playing within
        self.systemSize = int() # graphical size of one system in Galaxy, used for sizing map objects
        self.xMax = int() # total x size of Galactic Map
        self.yMax = int() # total y size of Galactic Map
        self.delayBonus = int() # delay bonus for finishing turn early
        self.currentRound = int() # Current Round of Play
        self.maxHoursLeft = int(25) # Game Max Hours Set that all Players agree to try and finish turn within
        self.currentHoursLeft = int(25) # Current Hours Left before Round Forced
        self.cities = 0 # total cities in galaxy currently
        self.defaultAttributes = ('name', 'version', 'systemSize', 'xMax','yMax', 'delayBonus',
                                  'currentRound', 'maxHoursLeft', 'currentHoursLeft', 'cities')
        self.setAttributes(args)
        
        self.empires = {} # Dict key = empire id, value = empire object
        self.systems = {} # Dict key = system id, value = system object
        self.AIPlayers = {} # Dict key = AIPlayer id, value = AIPlayer object
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
        self.galacticMarket = None
        self.designMode = 0 # galaxy is in a design game mode for turn ending
        self.systemSellMessages = {}#key=empireid, value = message sell body for turn
        self.systemBuyMessages = {}#key=empireid, value = message buy body for turn

        self.prices = {}
        
    def __getstate__(self):
        """Cannot pickle __builtins__ that include ellipse type, 
        probably bug in python 2.5, unsure if this is a good idea"""
        odict = self.__dict__.copy() # copy the dict since we change it
        if '__builtins__' in self.__dict__.keys():
            del odict['__builtins__']  # remove stuff not to be pickled
        return odict
    
    def setGalacticMarket(self):
        self.galacticMarket = galacticmarket.GalacticMarket(self)
    
    def mailRegimentsLostInTransport(self, empireID, body):
        """Inform empire of any regiments lost in transport during battle phase"""
        myEmpire = self.empires[empireID]
        dMail = {'fromEmpire':empireID, 'round':self.currentRound+1, 'messageType':'fleet',
                 'subject':'REGIMENT LOSSES from Transport Destruction','body':str(body)}
        myEmpire.genMail(dMail)
    
    def getRegimentsAtRisk(self, systemID):
        """Scan galaxy to see what regiments are at risk before a battle"""
        d = {}
        for regimentID in funcs.sortStringList(self.regiments.keys()):
            myRegiment = self.regiments[regimentID]
            if (myRegiment.fromSystem != myRegiment.toSystem 
                and myRegiment.toSystem == systemID):
                self.addRegimentFromSystemToDict(regimentID, myRegiment.empireID, myRegiment.fromSystem, d)
        return d
    
    def addRegimentFromSystemToDict(self, regimentID, empireID, fromSystem, d):
        if empireID not in d.keys():
            d[empireID] = {}
        if fromSystem not in d[empireID].keys():
            d[empireID][fromSystem] = [regimentID]
        else:
            d[empireID][fromSystem].append(regimentID)
    
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
                if (xDist + yDist) != 0 and (xDist <= self.systemSize) and (yDist <= self.systemSize):
                    mySystem.connectedSystems.append(id2)
    
    def getMyInfoAsDict(self):
        """Return only galaxy information that server wants to give to client"""
        list = ['name', 'version', 'systemSize', 'xMax', 
                'yMax', 'currentRound', 'currentHoursLeft']
        d = self.getSelectedAttr(list)
        return d
    
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
            if mySystem.myEmpireID == empireID or globals.diplomacy[self.empires[mySystem.myEmpireID].diplomacy[empireID].diplomacyID]['trade'] == 1:
                # selected system is owned by empire given or its not but they have trade agreement
                d = mySystem.getMySystemInfo()
            else:
                # selected system is not owned, give less info dict
                d = mySystem.getOtherSystemInfo()
            
            # only return one intel report
            d['intelReport'] = d['intelReport'][empireID]
            systemDict[id] = d
        return systemDict
    
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
                fromSystem = self.systems[myTradeRoute.fromSystem]
                toSystem = self.systems[myTradeRoute.toSystem]
                fromSystem.usedWGC += myTradeRoute.warpReq
                toSystem.usedWGC += myTradeRoute.warpReq
                if myTradeRoute.type <> 'GEN':
                    fromSystem.AL -= myTradeRoute.AL
                    fromSystem.EC -= myTradeRoute.EC
                    fromSystem.IA -= myTradeRoute.IA
                
                # send a message to all Empires involved
                result = self.mailTradeInfo('created', myTradeRoute, self.currentRound)
            return result
        except:
            return 'galaxy->genTradeRoute error'
        
    def validateTradeRoute(self, tradeRouteDict):
        """Validate generating trade route, return 1=pass, string=fail"""
        try:
            systemFrom = self.systems[tradeRouteDict['fromSystem']]
            systemTo = self.systems[tradeRouteDict['toSystem']]
            # has a trade route already been setup between these planets?
            if tradeRouteDict['id'] in self.tradeRoutes.keys():
                self.cancelTradeRoute(tradeRouteDict['id'], self.currentRound, 0)
            
            (sysFrom, sysTo, tradeType) = string.split(tradeRouteDict['id'], '-')
            # are these systems adjacent, or share a warp gate with a trade pact
            if systemTo.id in systemFrom.connectedSystems:
                pass
            elif systemTo.id in systemFrom.warpGateSystems:
                tempRoute = traderoute.TradeRoute(tradeRouteDict)
                warpReq = tempRoute.getWarpRequired(self)
                if warpReq > (systemFrom.usedWGC + systemFrom.availWGC):
                    return 'System:%s Requires %d Warp Capactiy to setup this Trade Route' % (systemFrom.name, warpReq)
                if warpReq > (systemTo.usedWGC + systemTo.availWGC):
                    return 'System:%s Requires %d Warp Capactiy to setup this Trade Route' % (systemTo.name, warpReq)
            else:
                return 'Systems are not adjacent and have no warp gates between them'
            # do these systems share the same empire owner, or are the two empires in a trade pact?
            if systemFrom.myEmpireID != systemTo.myEmpireID and globals.diplomacy[self.empires[systemFrom.myEmpireID].diplomacy[systemTo.myEmpireID].diplomacyID]['trade'] == 0:
                return 'System Owners are not the same, or no Trade Pact in Effect'
            # is a negative trade route being sent?
            if (tradeRouteDict['AL'] < 0 or tradeRouteDict['EC'] < 0 or tradeRouteDict['IA'] < 0):
                return 'you cannot send negative values in trade'
            # is something being sent?
            if (tradeRouteDict['AL'] == 0 and tradeRouteDict['EC'] == 0 and tradeRouteDict['IA'] == 0) and tradeRouteDict['type'] != 'GEN':
                return 'no resources are being sent, trade route invalid'
            # does the system have the resources to setup this trade?
            if (systemFrom.AL < tradeRouteDict['AL'] or systemFrom.EC < tradeRouteDict['EC'] or
                systemFrom.IA < tradeRouteDict['IA']):
                return '%s does not have enough resources to setup this trade route' % systemFrom.name
            for id, myTradeRoute in self.tradeRoutes.iteritems():
                if sysFrom == myTradeRoute.fromSystem and tradeType == myTradeRoute.type == 'GEN':
                    return 'you cannot setup two GEN trade routes from the same system'
            return 1
        except:
            return 'galaxy->validateTradeRoute error'

    def mailTradeInfo(self, type, tradeRoute, round):
        """Inform both empires involved in a Trade Route of its status:
            type=created -> trade route created
            type=removed -> trade route removed"""
        try:
            systemFrom = self.systems[tradeRoute.fromSystem]
            systemTo = self.systems[tradeRoute.toSystem]
            empireFrom = systemFrom.myEmpire
            empireTo = systemTo.myEmpire
            # only give trade information from other empires
            if empireFrom != empireTo or tradeRoute.warpReq > 0:
                tradeDetails = ['TRADE DETAILS:',
                                '=============',
                                'From System: %s' % systemFrom.name,
                                'To System: %s' % systemTo.name,
                                '',
                                'Alloys(AL) Sent:%d' % tradeRoute.AL,
                                'Energy(EC) Sent:%d' % tradeRoute.EC,
                                'Arrays(IA) Sent:%d' % tradeRoute.IA,
                                'Warp Used up   :%d' % tradeRoute.warpReq]
                
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

    def getMyTradeRouteInfo(self, empireID):
        """Return only trade routes specfic to empire given"""
        d = {}
        tradeRoutesDict = self.getMyDictInfo('tradeRoutes')
        for trID, myTradeRouteDict in tradeRoutesDict.iteritems():
            if (self.systems[myTradeRouteDict['fromSystem']].myEmpire.id == empireID or 
                self.systems[myTradeRouteDict['toSystem']].myEmpire.id == empireID):
                d[trID] = myTradeRouteDict
        return d
    
    def getOneTradeRouteInfo(self, tradeRouteID):
        """Get just one Trade Route info as Dict given ID"""
        d = {}
        tradeRoutesDict = self.getMyDictInfo('tradeRoutes')
        d[tradeRouteID] = tradeRoutesDict[tradeRouteID]
        return d
    
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
                warpReq = myTradeRoute.getWarpRequired()
                # choose trade route type
                if tradeRouteType == 'GEN':
                    # update what system sends based on what it makes
                    myTradeRoute.AL = systemFrom.prodAL
                    myTradeRoute.EC = systemFrom.prodEC
                    myTradeRoute.IA = systemFrom.prodIA
                    if (systemFrom.AL - systemFrom.prodAL < 0 or
                        systemFrom.EC - systemFrom.prodEC < 0 or
                        systemFrom.IA - systemFrom.prodIA < 0):
                        resultslist.append('cancel gen trade route=%s' % myTradeRoute.id)
                        self.cancelTradeRoute(myTradeRoute.id, nextRound)
                        continue
                    else:
                        systemFrom.AL -= systemFrom.prodAL
                        systemFrom.EC -= systemFrom.prodEC
                        systemFrom.IA -= systemFrom.prodIA 
                    
                # process trade route
                systemTo.AL += myTradeRoute.AL
                systemTo.EC += myTradeRoute.EC
                systemTo.IA += myTradeRoute.IA
                # deduct properly if empires are different
                empireFrom = self.empires[systemFrom.myEmpireID]
                empireTo = self.empires[systemTo.myEmpireID]
                if empireFrom != empireTo:
                    empireFrom.AL -= myTradeRoute.AL
                    empireFrom.EC -= myTradeRoute.EC
                    empireFrom.IA -= myTradeRoute.IA
                    empireTo.AL += myTradeRoute.AL
                    empireTo.EC += myTradeRoute.EC
                    empireTo.IA += myTradeRoute.IA
                    
                    # mail trade route completion
                    resultslist.append('Trade from System:%s to System:%s complete' % (systemFrom.id, systemTo.id))
                    self.mailTradeInfo('completed', myTradeRoute, nextRound)
                
                # check if route should be cancelled
                cancel = 0
                # check if trade route is adjacent or requires warp gate capacity
                if systemTo.id not in systemFrom.connectedSystems:
                    if systemTo.id in systemFrom.warpGateSystems:
                        if warpReq > (systemFrom.availWGC-systemFrom.usedWGC) or warpReq > (systemTo.availWGC-systemTo.usedWGC):
                            cancel = 1                    
                if (systemFrom.AL < myTradeRoute.AL or
                    systemFrom.EC < myTradeRoute.EC or
                    systemFrom.IA < myTradeRoute.IA):
                    cancel = 1
                if myTradeRoute.oneTime == 1:
                    cancel = 1
                if tradeRouteType == 'GEN':
                    cancel = 0                
                    
                if cancel == 1:
                    myTradeRoute.AL = 0
                    myTradeRoute.EC = 0
                    myTradeRoute.IA = 0
                    myTradeRoute.warpReq = 0
                    if myTradeRoute.oneTime == 1:
                        resultslist.append('one time trade route=%s' % myTradeRoute.id)
                    else:
                        resultslist.append('cancel trade route=%s' % myTradeRoute.id)
                    self.cancelTradeRoute(myTradeRoute.id, nextRound)
                
                if cancel == 0:
                    if tradeRouteType == 'GEN':
                        systemFrom.usedWGC += warpReq
                        systemTo.usedWGC += warpReq
                    else:
                        systemFrom.AL -= myTradeRoute.AL
                        systemFrom.EC -= myTradeRoute.EC
                        systemFrom.IA -= myTradeRoute.IA
                        systemFrom.usedWGC += warpReq
                        systemTo.usedWGC += warpReq
                    
            return str(resultslist)
        except:
            return 'galaxy->processTradeRoutes error'
    
    def cancelTradeRoute(self, tradeRouteID, round, mail=1):
        """Cancel trade route based on ID Provided"""
        try:
            # send a message to all Empires involved
            myTradeRoute = self.tradeRoutes[tradeRouteID]
            mySystem = self.systems[myTradeRoute.fromSystem]
            toSystem = self.systems[myTradeRoute.toSystem]
            if mail == 1:
                result = self.mailTradeInfo('removed', myTradeRoute, round)
            else:
                result = 1
            if result == 1:
                if myTradeRoute.type <> 'GEN':
                    mySystem.AL += myTradeRoute.AL
                    mySystem.EC += myTradeRoute.EC
                    mySystem.IA += myTradeRoute.IA
                mySystem.usedWGC -= myTradeRoute.warpReq
                toSystem.usedWGC -= myTradeRoute.warpReq
                del self.tradeRoutes[tradeRouteID]
            return result
        except:
            return 'galaxy->cancelTradeRoute error'
    
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
                else:
                    return result
            else:
                return result
            return d
        except:
            return 'galaxy->genMarketOrder error'
        
    def genGalacticMarketOrder(self, orderDict):
        """Generate a galactic market order"""
        try:
            id = self.getNextID(self.marketOrders)
            d = {'id':id}
            for key, value in orderDict.iteritems():
                d[key] = value
            d['round'] = self.currentRound
            myMarketOrder = order.MarketOrder(d)
            self.marketOrders[id] = myMarketOrder
            return d
        except:
            return 'galaxy->genGalacticMarketOrder error'
    
    def validateMarketOrder(self, orderDict):
        """Validate Market Order, return 1=pass, string=fail"""
        try:
            if (orderDict['amount'] == 0 or (orderDict['min'] == 0 and orderDict['max'] == 0)):
                return 'You must place an order with a min/max and amount > 0'
            return 1
        except:
            return 'galaxy->validateMarketOrder error'    
    
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
      
    def refundMarketOrder(self, marketOrder):
        """Refund the cost of the market order"""
        try:
            if marketOrder.system == 'marketSystem':
                return 1
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
    
    def getMyMarketOrders(self, empireID):
        """Return only market orders specfic to empire given"""
        d = {}
        marketOrdersDict = self.getMyDictInfo('marketOrders')
        for marketID, myMarketOrderDict in marketOrdersDict.iteritems():
            if self.systems[myMarketOrderDict['system']].myEmpire.id == empireID:
                d[marketID] = myMarketOrderDict
        return d
    
    def processMarketOrders(self, doGalacticMarket=1):
        """Go through all current System Market Orders and resolve them"""
        try:
            nextRound = self.currentRound+1
            if doGalacticMarket == 1 and self.currentRound > 0:
                self.galacticMarket.doMyTurn()
            resultsList = []
            master = {}
            self.genMarketStat()
            myMarketStat = self.marketStats[str(self.currentRound)]
                
            # sorted lists of market orders
            master['buyAL'] = funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'AL', 'min':0})
            master['buyEC'] = funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'EC', 'min':0})
            master['buyIA'] = funcs.sortDictByChildObjValue(self.marketOrders, 'max', True, {'value':'IA', 'min':0})
            master['sellAL'] = funcs.sortDictByChildObjValue(self.marketOrders, 'min', True, {'value':'AL', 'max':0})
            master['sellEC'] = funcs.sortDictByChildObjValue(self.marketOrders, 'min', True, {'value':'EC', 'max':0})
            master['sellIA'] = funcs.sortDictByChildObjValue(self.marketOrders, 'min', True, {'value':'IA', 'max':0})
            count = 0
            
            for res in ['AL', 'EC', 'IA']:
                for sellOrder in master['sell%s' % res]:
                    if sellOrder.system != 'marketSystem':
                        self.processBuyOrders(count, master['buy%s' % res], sellOrder, resultsList)
                
                for sellOrder in master['sell%s' % res]:
                    if sellOrder.system == 'marketSystem':
                        self.processBuyOrders(count, master['buy%s' % res], sellOrder, resultsList)
                
                # set the average market prices for this round
                if getattr(myMarketStat, 'volSold%s' % res) > 0:
                    price = round(getattr(myMarketStat, 'sumSold%s' % res) / getattr(myMarketStat, 'volSold%s' % res))
                    if price <= 1:
                        price = 1
                    setattr(myMarketStat, 'avgSold%s' % res, price)
            
            # clean up market orders for next round
            if doGalacticMarket == 1 and self.currentRound > 0:
                self.galacticMarket.reset()
            for orderID in self.marketOrders.keys():
                myMarketOrder = self.marketOrders[orderID]
                myMarketOrder.cleanUp()
                if myMarketOrder.amount == 0:
                    resultsList.append('cancel market Order=%s' % orderID)
                    self.cancelMarketOrder(orderID)
            
            return str(resultsList)
        except:
            return 'galaxy->processMarketOrders error'
    
    def processBuyOrders(self, count, masterBuyOrder, sellOrder, resultsList):
        """Find buy orders required to meet the sell order"""
        for buyOrder in masterBuyOrder:
            if buyOrder.max >= sellOrder.min and buyOrder.amount > buyOrder.amountUsed:
                price = sellOrder.min
                result = self.processMarketTransaction(count, buyOrder, sellOrder, price)
                count += 1
                if buyOrder.system != sellOrder.system:
                    resultsList.append(result)
                if sellOrder.amountUsed == sellOrder.amount:
                    return
        
    def processMarketTransaction(self, count, buyOrder, sellOrder, resolvedPrice):
        """Process a transaction between buyer and seller"""
        try:
            buyOrderAmountLeft = buyOrder.amount - buyOrder.amountUsed
            sellOrderAmountLeft = sellOrder.amount - sellOrder.amountUsed
            myMarketStat = self.marketStats[str(self.currentRound)]
            buySystem = None
            buySystemName = 'Galactic Market'
            sellSystem = None
            sellSystemName = 'Galactic Market'
            round = str(self.currentRound)
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
                    if buyOrder.system != 'marketSystem':
                        buySystem = self.systems[buyOrder.system]
                    if sellOrder.system != 'marketSystem':
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
                    transID = '<R%s-T%d> ' % (self.currentRound, count)
                    # give credits to seller
                    if sellSystem != None:
                        sellSystemName = sellSystem.name
                        self.systemSellMessages[sellSystem.myEmpire.id].append('Transaction: %s =========================================>' % (transID))
                        self.systemSellMessages[sellSystem.myEmpire.id].append('(%s) - Resource:%s - SOLD: (%d units at %d)' % (sellSystem.name, sellOrder.value, actualAmount, resolvedPrice))
                        self.systemSellMessages[sellSystem.myEmpire.id].append('Remaining Unsold %s from this Order:%d' % (sellOrder.value, sellOrder.amount-sellOrder.amountUsed))
                        creditsMade = actualAmount*resolvedPrice
                        sellSystem.myEmpire.depositCR(creditsMade)
                        if round not in sellSystem.myEmpire.empireStats.keys():
                            sellSystem.myEmpire.genEmpireStat()
                        myEmpireStat = sellSystem.myEmpire.empireStats[round]
                        myEmpireStat.CRfromMarketSales += creditsMade
                    # give resource and refund to buyer
                    if buySystem != None:
                        buySystemName = buySystem.name
                        buySystem.payResources(-refund,0,0,0)
                        myEmpireStat = buySystem.myEmpire.empireStats[round]
                        myEmpireStat.CRfromMarketSales += abs(refund)
                        buySystem.modifyResource(buyOrder.value, actualAmount)
                        self.systemBuyMessages[buySystem.myEmpire.id].append('Transaction: %s =========================================>' % (transID))
                        self.systemBuyMessages[buySystem.myEmpire.id].append('(%s) - Resource:%s - BOUGHT: (%d units at %d) Refund=%d' % (buySystem.name, buyOrder.value, actualAmount, resolvedPrice, refund))
                        self.systemBuyMessages[buySystem.myEmpire.id].append('Remaining Unbought %s from this Order:%d' % (buyOrder.value, buyOrder.amount-buyOrder.amountUsed))
    
                    return 'transaction completed: %s SOLD %d %s to %s for %d price' % (sellSystemName, actualAmount, sellOrder.value, buySystemName, resolvedPrice)
                else:
                    return '(%s)resolved price=%d, not in range, seller=%s, buyer=%s' % (buyOrder.value, resolvedPrice, sellOrder.id, buyOrder.id)
            else:
                return 'unknown order type'

        except:
            return 'galaxy->processMarketTransaction error'
    
    def getMyCaptialSystem(self, myEmpireID):
        """Determine the captial system by its city size"""
        myCaptialSystem = None
        for systemID, mySystem in self.systems.iteritems():
            if mySystem.myEmpireID == myEmpireID:
                if myCaptialSystem == None:
                    myCaptialSystem = mySystem
                elif myCaptialSystem.cities < mySystem.cities:
                    myCaptialSystem = mySystem
        return myCaptialSystem
    
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
    
    def switchShiptoNewEmpire(self, shipID, empireID):
        """Ship has been taken over in combat, send to other empire"""
        myShip = self.ships[shipID]
        oldEmpire = self.empires[myShip.empireID]
        myEmpire = self.empires[empireID]
        myCaptain = self.captains[myShip.captainID]
        myCaptain.setMyEmpire(myEmpire)
        (name, hullID, compDict, weaponDict) = myShip.myDesign.getMyDesign()
        (shipDesignID, shipDesignName) = myEmpire.copyShipDesign(name, hullID, compDict, weaponDict)
        myNewDesign = myEmpire.shipDesigns[shipDesignID]
        self.copyDroneDesigns(weaponDict, oldEmpire, myEmpire)
        myShip.myDesign = myNewDesign
        myShip.designID = shipDesignID
        myShip.empireID = empireID
        myShip.takenOverByEmpire = ''
    
    def copyDroneDesigns(self, weaponDict, oldEmpire, newEmpire):
        """Make sure that if this ship design is a carrier that all its drone designs are copied"""
        for key, value in weaponDict.iteritems():
            if key == 'dronedesign':
                myDroneDesign = oldEmpire.droneDesigns[value]
                (name, hullID, compDict, weaponDict) = myDroneDesign.getMyDesign()
                newEmpire.copyDroneDesign(name, hullID, compDict, weaponDict)
    
    def setCaptainNames(self):
        """Build the captain names list, uses self.id for consitant name generation"""
        inputFile = '%s/../Data/captain_names.txt' % os.getcwd()
        self.captainNames = names.getNames(inputFile,self.maxCaptainNames+100, self.rand.randint(1,100))
        self.currentCaptainName = 0
    
    def setCaptainName(self, empireID, id, name):
        """Set the name of captain to another"""
        try:
            myCaptain = self.captains[id]
            if myCaptain.empireID != empireID:
                return 'cannot set captain name not owned by player requesting change'
            # make sure no other captain shares same name
            for captainID, otherCaptain in self.captains.iteritems():
                if otherCaptain.name == name and otherCaptain.id != id:
                    return 'Another captain already has the name:%s' % name
            myCaptain.setMyName(name)
            return 1
        except:
            return 'error-> could not set captain name'
    
    def getCaptainName(self):
        """Retreive the latest captain name"""
        if self.shouldSetCaptainNames():
            self.setCaptainNames()
        # grab the latest name
        name = '%s %s' % (self.captainNames[self.currentCaptainName], self.captainNames[self.currentCaptainName+1])
        self.currentCaptainName += 2
        return name
    
    def shouldSetCaptainNames(self):
        """Should the self.captainNames list be set"""
        if self.captainNames == []:
            return 1
        if self.currentCaptainName >= self.maxCaptainNames-50:
            return 1
        return 0
    
    def getMyShips(self, empireID):
        """Return all of my ship/armada information from galaxy"""
        myShipsDict = {}
        myArmadasDict = {}
        otherArmadasDict = {}
        warpedArmadasDict = {}
        for shipID, myShip in self.ships.iteritems():
            if myShip.empireID == empireID:
                myShipsDict[shipID] = myShip.getMyShipInfo()
                if myShip.fromSystem == myShip.toSystem:
                    if not (myArmadasDict.has_key(myShip.toSystem)):
                        # add new armada to this system
                        myArmadasDict[myShip.toSystem] = [myShip.id]
                    else:
                        # existing armada, add to ship id list
                        myArmadasDict[myShip.toSystem].append(myShip.id)
                else:
                    if not (warpedArmadasDict.has_key(myShip.toSystem)):
                        # add new armada to this system
                        warpedArmadasDict[myShip.toSystem] = [myShip.id]
                    else:
                        # existing armada, add to ship id list
                        warpedArmadasDict[myShip.toSystem].append(myShip.id)
            else:
                # other ship, add to other armada dict
                if not (otherArmadasDict.has_key(myShip.fromSystem)):
                    # add new armada to this system
                    otherArmadasDict[myShip.fromSystem] = [myShip.empireID]
                else:
                    # existing armada, append ship empire owner
                    if myShip.empireID not in otherArmadasDict[myShip.fromSystem]:
                        otherArmadasDict[myShip.fromSystem].append(myShip.empireID)
                
        return (myShipsDict, myArmadasDict, otherArmadasDict, warpedArmadasDict)
  
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
        warpedArmiesDict = {}
        for regimentID, myRegiment in self.regiments.iteritems():
            if myRegiment.empireID == empireID:
                myRegimentsDict[regimentID] = myRegiment.getMyRegimentInfo()
                if myRegiment.fromSystem == myRegiment.toSystem:
                    if not (myArmiesDict.has_key(myRegiment.toSystem)):
                        # add new army to this system
                        myArmiesDict[myRegiment.toSystem] = [myRegiment.id]
                    else:
                        # existing army, add to regiment id list
                        myArmiesDict[myRegiment.toSystem].append(myRegiment.id)
                else:
                    if not (warpedArmiesDict.has_key(myRegiment.toSystem)):
                        # add new army to this system
                        warpedArmiesDict[myRegiment.toSystem] = [myRegiment.id]
                    else:
                        # existing army, add to regiment id list
                        warpedArmiesDict[myRegiment.toSystem].append(myRegiment.id)
            else:
                # other army, add to other army dict
                if not (otherArmiesDict.has_key(myRegiment.fromSystem)):
                    # add new army to this system
                    otherArmiesDict[myRegiment.fromSystem] = [myRegiment.empireID]
                else:
                    # existing army, append regiment empire owner
                    if myRegiment.empireID not in otherArmiesDict[myRegiment.fromSystem]:
                        otherArmiesDict[myRegiment.fromSystem].append(myRegiment.empireID)
                
        return (myRegimentsDict, myArmiesDict, otherArmiesDict, warpedArmiesDict)

    def getShipBattle(self, empireID, shipBattleKey):
        """Return a Ship Battle serialized object"""
        try:
            # grab ship battle from server using key provided.
            # check that key is in ship battle list
            myEmpire = self.empires[empireID]
            if shipBattleKey not in myEmpire.myShipBattles:
                return -1
            try:
                shipBattle = storedata.loadFromFile('../Database/%s/%s.ship' % (self.name, shipBattleKey))
            except:
                return -1
            shipBattle = storedata.saveToString(shipBattle)
            return shipBattle
        except:
            return -1

    def cancelMoveShips(self, shipList, empireID):
        """Attempt to cancel move ships"""
        try:
            for shipID in shipList:
                myShip = self.ships[shipID]
                if myShip.empireID != empireID:
                    return 'Cannot move ship if it is not yours'
            
            for shipID in shipList:
                myShip = self.ships[shipID]
                toSystem = self.systems[myShip.toSystem]
                fromSystem = self.systems[myShip.fromSystem]
                if toSystem.id not in fromSystem.connectedSystems:
                    toSystem.usedWGC -= 1
                    fromSystem.usedWGC -= 1
                myShip.moveToSystem(5, myShip.fromSystem)
            return 1
            
        except:
            return 'galaxy->cancelMoveShips error'
    
    def cancelMoveReg(self, regList, empireID):
        """Attempt to cancel move regiments"""
        try:
            systemsUsingWarp = {}
            for regID in regList:
                myReg = self.regiments[regID]
                if myReg.empireID != empireID:
                    return 'Cannot move regiment if it is not yours'
            
            for regID in regList:
                myReg = self.regiments[regID]
                toSystem = self.systems[myReg.toSystem]
                fromSystem = self.systems[myReg.fromSystem]
                if toSystem.id not in fromSystem.connectedSystems:
                    key = (fromSystem.id, toSystem.id)
                    if key not in systemsUsingWarp:
                        systemsUsingWarp[key] = 1
                    else:
                        systemsUsingWarp[key] += 1
                myReg.moveToSystem(myReg.fromSystem)
                
            for (fromSystemID, toSystemID), num in systemsUsingWarp.iteritems():
                warpcostBefore = self.getRegWarpMoveCost(empireID, 0, fromSystemID, toSystemID)
                warpcostAfter = self.getRegWarpMoveCost(empireID, num, fromSystemID, toSystemID)
                warpcost = warpcostAfter-warpcostBefore
                fromSystem = self.systems[fromSystemID]
                fromSystem.usedWGC -= warpcost
                toSystem = self.systems[toSystemID]
                toSystem.usedWGC -= warpcost
            return 1
            
        except:
            return 'galaxy->cancelMoveReg error'
        
    def moveShips(self, shipList, empireID, systemID):
        """Attempt to move ships from list given to system specified"""
        try:
            # init attributes that all ships should share
            shipOne = self.ships[shipList[0]]
            shipOwner = shipOne.empireID
            if shipOwner != empireID:
                return 'Cannot move ship if it is not yours'
            fromSystem = self.systems[shipOne.fromSystem]
            toSystem = self.systems[systemID]
            newSystemGrid = funcs.getMapQuadrant(toSystem, shipOne, fromSystem.x, fromSystem.y,
                                                           toSystem.x, toSystem.y)
            # check if group of ships share these attributes
            for shipID in shipList:
                myShip = self.ships[shipID]
                if myShip.fromSystem != fromSystem.id:
                    return 'Ship %s comes from system: %s' % (myShip.name, fromSystem.name)
                if myShip.empireID != shipOwner:
                    return 'Ship %s has different empire Owner: %s' % (myShip.name, myShip.empireID)
                
            valid = 0
            # ships have been validated to be going the same place, now validate movement
            checkwarp = 0
            for shipID in shipList:
                myShip = self.ships[shipID]
                # can ship be moved?
                if myShip.fromSystem != myShip.toSystem and systemID != myShip.fromSystem:
                    return 'Ship %s has already moved' % myShip.name
                
                # check if ship is platform going out of own empire
                if (myShip.myShipHull.abr[1:] == 'WP' and 
                    (toSystem.myEmpireID != empireID and globals.diplomacy[self.empires[empireID].diplomacy[toSystem.myEmpireID].diplomacyID]['alliance'] == 0)):
                    return 'Platforms can only move between your systems, they cannot attack.'
                
                # check that ship is allowed to move to system
                if toSystem.myEmpireID != empireID and globals.diplomacy[self.empires[empireID].diplomacy[toSystem.myEmpireID].diplomacyID]['move'] == 0:
                    return 'Diplomacy will not allow your ships to move to this system'
                else:
                    # is system adjacent?
                    if systemID in fromSystem.connectedSystems:
                        valid = 1
                    else:
                        checkwarp = 1
            
            if checkwarp == 1:
                if len(shipList) <= (fromSystem.availWGC-fromSystem.usedWGC) and len(shipList) <= (toSystem.availWGC-toSystem.usedWGC):
                    fromSystem.usedWGC += len(shipList)
                    toSystem.usedWGC += len(shipList)
                    valid = 1
                else:
                    return 'Not enough Warp Capacity Points to move Ships'
            
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
    
    def moveReg(self, regList, empireID, systemID):
        """Attempt to move regiments from list given to system specified"""
        try:
            regOne = self.regiments[regList[0]]
            regOwner = regOne.empireID
            if regOwner != empireID:
                return 'Cannot move regiment if it is not yours'
            fromSystem = self.systems[regOne.fromSystem]
            toSystem = self.systems[systemID]
            
            # check if group of reg share these attributes
            for regID in regList:
                myReg = self.regiments[regID]
                if myReg.fromSystem != fromSystem.id:
                    return 'Regiment %s comes from system: %s' % (myReg.name, fromSystem.name)
                if myReg.empireID != regOwner:
                    return 'Regiment %s has different empire Owner: %s' % (myReg.name, myReg.empireID)
                
            valid = 0
            # reg have been validated to be going the same place, now validate movement
            checkwarp = 0
            for regID in regList:
                myReg = self.regiments[regID]
                # can reg be moved?
                if myReg.fromSystem != myReg.toSystem and systemID != myReg.fromSystem:
                    return 'Regiment %s has already moved' % myReg.name
                
                # check that reg is allowed to move to system
                if toSystem.myEmpireID != empireID and globals.diplomacy[self.empires[empireID].diplomacy[toSystem.myEmpireID].diplomacyID]['move'] == 0:
                    return 'Diplomacy will not allow your regiments to move to this system'
                else:
                    # is system adjacent?
                    if systemID in fromSystem.connectedSystems:
                        valid = 1
                    else:
                        checkwarp = 1  
                        
            if checkwarp == 1:
                warpcostBefore = self.getRegWarpMoveCost(empireID, 0, fromSystem.id, toSystem.id)
                warpcostAfter = self.getRegWarpMoveCost(empireID, len(regList), fromSystem.id, toSystem.id)
                warpcost = warpcostAfter-warpcostBefore
                if warpcost <= (fromSystem.availWGC-fromSystem.usedWGC) and warpcost <= (toSystem.availWGC-toSystem.usedWGC):
                    fromSystem.usedWGC += warpcost
                    toSystem.usedWGC += warpcost
                    valid = 1
                else:
                    return 'Not enough Warp Capacity Points to move Regiments'
            
            if valid == 1:
                for regID in regList:
                    myReg = self.regiments[regID]
                    myReg.moveToSystem(systemID)
                return 1
            else:
                return 'Not a valid Regiment Movement Order'
        except:
            return 'galaxy->moveReg error'
    
    def getRegWarpMoveCost(self, empireID, numToWarp, systemOneID , systemTwoID):
        """Return the Warp Costs of any Regiments to move from systemOne to systemTwo"""
        numReg = numToWarp
        for regID, myReg in self.regiments.iteritems():
            if myReg.empireID == empireID and myReg.fromSystem == systemOneID and myReg.toSystem == systemTwoID:
                numReg += 1
        return funcs.getTransportsRequired(numReg)
        
    def swapCaptains(self, empireID, shipOneID, shipTwoID):
        """Attempt to swap captains between two ships"""
        try:
            myEmpire = self.empires[empireID]
            shipOne = self.ships[shipOneID]
            shipTwo = self.ships[shipTwoID]
            
            # make sure empire is correct
            if shipOne.empireID != empireID or shipTwo.empireID != empireID:
                return 'You cannot switch the captains with another Empires Ship'
            
            # swap ship captains
            captain2 = shipTwo.myCaptain
            shipTwo.setMyCaptain(shipOne.myCaptain)
            shipOne.setMyCaptain(captain2)
            return 1
        except:
            return 'galaxy->swapCaptains error'
    
    def sortAllCaptains(self, empireID, systemID, shipList):
        """Sort Captains putting the best in the best ships at system"""
        try:
            d = {}
            captainsWorstFirst = []
            shipsSmallestFirst = []
            captainDict = {}
            shipDict = {}
            for shipID in shipList:
                myShip = self.ships[shipID]
                myCaptain = self.captains[myShip.captainID]
                captainDict[myCaptain] = myCaptain.experience
                shipDict[myShip] = myShip.myDesign.getMyBattleValue()
            captainsWorstFirst = funcs.sortDictByValue(captainDict)
            shipsSmallestFirst = funcs.sortDictByValue(shipDict)
            num = 0
            for ship in shipsSmallestFirst:
                captain = captainsWorstFirst[num]
                ship.setMyCaptain(captain)
                d[ship.id] = captain.id
                num += 1
            return d
        except:
            return 'galaxy->sortAllCaptains error'
        
    def removeCaptain(self, captainID):
        """Remove captain from galaxy"""
        del self.captains[captainID]
        
    def removeRegiment(self, regimentID):
        """Remove Regiment from galaxy"""
        del self.regiments[regimentID]

    def removeShip(self, shipID):
        """Remove ship from galaxy"""
        if shipID in self.ships.keys():
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
            myEmpire.resetDesigns()
        
        # reset system data
        for systemID, mySystem in self.systems.iteritems():
            mySystem.setWarpConnections()
        
        # reset ship data
        for shipID in self.ships.keys():
            myShip = self.ships[shipID]
            if myShip.isTransport == 1:
                self.removeShip(shipID)
                myShip = None
            else:
                myShip.resetData()
        
        # reset regiment data
        for regimentID, myRegiment in self.regiments.iteritems():
            myRegiment.resetData()
            
        # reset ship orders
        for shipID, myShip in self.ships.iteritems():
            myShip.setAvailSystems()
        
        # reset regiment orders
        for regimentID, myRegiment in self.regiments.iteritems():
            myRegiment.setAvailSystems()
        
        # set intel reports
        for systemID, mySystem in self.systems.iteritems():
            mySystem.setIntelReports()
        
        # set empire stats
        self.setEmpireStats()

        self.setTotalCities()
        self.setMarketForNextRound()
        for empireID, myEmpire in self.empires.iteritems():
            myEmpire.calculateMyCredits()
            myEmpire.mailEconomicReport()

    def setTotalCities(self):
        """Set the Total Cities of Galaxy"""
        self.cities = 0
        for empireID, myEmpire in self.empires.iteritems():
            self.cities += myEmpire.cities

    def setMarketForNextRound(self):
        """Reset the Market Information for next round"""
        self.prices['AL'] = self.marketStats[str(self.currentRound-1)].avgSoldAL
        self.prices['EC'] = self.marketStats[str(self.currentRound-1)].avgSoldEC
        self.prices['IA'] = self.marketStats[str(self.currentRound-1)].avgSoldIA
    
    def setEmpireStats(self):
        """Each Round all Empires are compared to each other for stats which are mailed out"""
        totalEmpires = len(self.empires.keys())
        stats = {'Research':[], 'Fleet Size':[], 'Army Size':[], 'AL Production':[],
                 'EC Production':[],'IA Production':[]}
        
        # Calculate Research Stats
        d = {}
        for empireID, myEmpire in self.empires.iteritems():
            if empireID != '0':
                num = 0
                for techID, myTech in myEmpire.techTree.iteritems():
                    if myTech.complete == 1:
                        num += 1
                d[empireID] = num
        stats['Research'] = funcs.sortDictByValue(d, True)
        
        # Calculate Fleet Stats
        d = {}
        for shipID, myShip in self.ships.iteritems():
            if myShip.empireID != '0':
                (BV,CR,AL,EC,IA) = myShip.getMyValue()
                if myShip.empireID in d.keys():
                    d[myShip.empireID] += BV
                else:
                    d[myShip.empireID] = BV
        stats['Fleet Size'] = funcs.sortDictByValue(d, True)
        
        # Calculate Army Stats
        d = {}
        for regimentID, myRegiment in self.regiments.iteritems():
            if myRegiment.empireID != '0':
                (BV,CR,AL,EC,IA) = myRegiment.getMyValue()
                if myRegiment.empireID in d.keys():
                    d[myRegiment.empireID] += BV
                else:
                    d[myRegiment.empireID] = BV
        stats['Army Size'] = funcs.sortDictByValue(d, True)

        # Calculate Production Stats
        for res in ['AL','EC','IA']:
            d = {}
            for systemID, mySystem in self.systems.iteritems():
                if mySystem.myEmpireID != '0':
                    myValue = getattr(mySystem, 'prod%s' % res)
                    if mySystem.myEmpireID in d.keys():
                        d[mySystem.myEmpireID] += myValue
                    else:
                        d[mySystem.myEmpireID] = myValue
                    myEmpire = self.empires[mySystem.myEmpireID]
                    myEmpireValue = getattr(myEmpire, 'totalProd%s' % res)
                    setattr(myEmpire, 'totalProd%s' % res, myEmpireValue+myValue)
            
            stats['%s Production' % res] = funcs.sortDictByValue(d, True)
        
        # calculate top captains
        d = {}
        for captainID, myCaptain in self.captains.iteritems():
            if myCaptain.myEmpire.id != '0':
                myCaptain.resetData()
                d[myCaptain.id] = myCaptain.experience
        topCaptains = funcs.sortDictByValue(d, True)
        topCaptains = topCaptains[:2*len(self.empires.keys())]
        
        # Send out Stats to each Empire
        for empireID, myEmpire in self.empires.iteritems():
            if empireID != '0':
                title = 'Round:%d Statistics' % self.currentRound
                body = ['%s ROUND %d STATS:' % (myEmpire.name, self.currentRound)]
                body.append('====================================================')
                for item in ['Research','Fleet Size', 'Army Size',
                             'AL Production', 'EC Production', 'IA Production']:
                    if empireID in stats[item]:
                        body.append('You are %s in %s' % (funcs.getNiceNumber(stats[item].index(empireID)+1), item))
                        
                # total production
                body.append('')
                body.append('TOTAL EMPIRE PRODUCTION OVER %d ROUNDS:' % self.currentRound)
                body.append('====================================================')
                for res in ['AL','EC','IA']:
                    body.append('Total %s Production:  %d' % (res, getattr(myEmpire, 'totalProd%s' % res)))

                # legendary captains
                body.append('')
                body.append('TOP %d STARSHIP CAPTAINS in ROUND %d:' % ((2*len(self.empires.keys()), self.currentRound)))
                body.append('====================================================')
                for captainID in topCaptains:
                    myCaptain = self.captains[captainID]
                    body.append('%s ---> RANK:%s -- EXP:%d -- %s' % (string.upper(myCaptain.name), myCaptain.rank, myCaptain.experience, string.upper(myCaptain.myEmpire.name)))
                
                myEmpire.genMail({'fromEmpire':empireID, 'round':self.currentRound,
                                  'messageType':'general', 'subject':title, 'body':body})

    def setNewRegiment(self, empireID, systemID, typeID, name='Marine'):
        """Create a new regiment for empire on system"""
        id = self.getNextID(self.regiments)
        myEmpire = self.empires[empireID]
        myRegiment = regiment.Regiment({'id':id, 'empireID':empireID, 
                                        'fromSystem':systemID, 'toSystem':systemID, 
                                        'typeID':typeID})
        myRegiment.setMyGalaxy(self)
        myRegiment.setMyStatus(name)
        return myRegiment
    
    def endEmpireTurn(self, currentEmpire, singleplayer=0):
        """End the turn for Empire, check if all empires have ended their turns"""
        try:
            # end the Empire's turn
            currentEmpire.endTurn()

            # check if all Empires turns are done
            done = 1
            for empireID, myEmpire in self.empires.iteritems():
                if myEmpire.id != '0' and myEmpire.roundComplete == 0 and myEmpire.alive == 1:
                    return 0
            return 1
        except:
            return 'galaxy->endEmpireTurn error'
  
    def endRound(self, doAITurn=1):
        """End the Round of Play for this galaxy"""
        # first copy
        resultsList = []
        try:       
            # calculate research rolls
            researchRolls = funcs.getRandomD100Rolls(100)
                
            for empireID, myEmpire in self.empires.iteritems():
                if empireID != '0' and self.currentRound > 0:
                    myEmpire.sendMyCredits()
                    # Don't turn a player into ai player if they are late to end their turn
                    #if myEmpire.roundComplete == 0:
                        #myEmpire.setAIinControl()
            
            # Process for Each Empire
            for empireID, myEmpire in self.empires.iteritems():
                myEmpire.addDelay()
                myEmpire.genEmpireStat()
                self.systemSellMessages[empireID] = ['Galactic Market Sell Results for Round:%d' % self.currentRound,
                                                     '===========================================']
                self.systemBuyMessages[empireID] = ['Galactic Market Buy Results for Round:%d' % self.currentRound,
                                                    '==========================================']
                # build industry
                resultsList.append('%s(%s) - buildIndustry:%s' % (myEmpire.name, empireID, myEmpire.buildIndustry()))
                
                # generate income and research points
                resultsList.append('%s(%s) - processSystems:%s' % (myEmpire.name, empireID, myEmpire.processSystems()))
                
                # calculate research orders
                resultsList.append('%s(%s) - calcResearch:%s' % (myEmpire.name, empireID, myEmpire.calcResearch(researchRolls)))
                
                # calculate diplomacy
                resultsList.append('%s(%s) - resolveDiplomacy:%s' % (myEmpire.name, empireID, myEmpire.resolveDiplomacy()))
            
            # Process trade routes
            resultsList.append('Process Trade Routes:%s' % self.processTradeRoutes())
            
            # Process Market Orders
            resultsList.append('Process Market Orders:%s' % self.processMarketOrders())
            
            # Process all Ship Battles
            resultsList.append('Process Ship Battles:%s' % self.processShipBattles())
            
            # Process all Ground Battles
            resultsList.append('Process Ground Battles:%s' % self.processGroundBattles())
            
            for empireID, myEmpire in self.empires.iteritems():
                if empireID != '0' and myEmpire.alive == 1 and self.currentRound > 0:
                    ##resultsList.append('%s(%s) - calculateExperience:%s' % (myEmpire.name, empireID, myEmpire.calculateExperience()))
                    self.mailMarketReport(empireID)
            
            # reset galaxy data
            resultsList.append('Reset galaxy data, increment round')
            self.printResults(resultsList)
            self.resetData()
            if doAITurn == 1:
                self.doAITurns()
            return 1
        except:
            return 'galaxy->endRound error'
    
    def mailMarketReport(self, empireID):
        """Mail the Galactic Market Report for selling and buying orders for each empire"""
        myEmpire = self.empires[empireID]
        myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':self.currentRound+1, 
                        'messageType':'market', 'subject':'Galactic Market Report - Sell Orders',
                        'body':self.systemSellMessages[empireID]})
        myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':self.currentRound+1, 
                        'messageType':'market', 'subject':'Galactic Market Report - Buy Orders',
                        'body':self.systemBuyMessages[empireID]})
        
    def doAITurns(self):
        """Any AI Players should conduct their turns now that the round has reset to the next round"""
        for empireID, myEmpire in self.empires.iteritems():
                if empireID != '0' and myEmpire.alive == 1 and myEmpire.ai == 1:
                    self.endEmpireTurn(myEmpire)
                    myEmpire.myAIPlayer.doMyTurn()
        
    def printResults(self, resultsList):
        """Print the resultsList to the server"""
        for line in resultsList:
            print str(line)
    
    def genShipBattle(self, systemID):
        """Generate a ShipBattle object for processing by the Ship Simulator and for
        Ship Battle History storage"""
        mySystem = self.systems[systemID]
        empiresDict = {}
        shipsDict = {}
        captainsDict = {}
        regimentsExposed = self.createTransportsForBattle(systemID)
                    
        for shipID, myShip in self.ships.iteritems():
            if myShip.toSystem == systemID:
                shipsDict[shipID] = myShip.getMyShipInfo()
        
        shipNum = len(shipsDict.keys())
        battleNum = self.getBattleNum(shipNum)
        shipNumPerBattle = shipNum/battleNum
        for i in range(battleNum):
            i += 1
            if i == battleNum:
                myShipsDict = shipsDict
            else:
                myShipsDict = self.pickShipsForBattle(shipsDict, shipNumPerBattle)
            targets = self.setupShipsForBattle(systemID, myShipsDict, empiresDict, captainsDict)
            
            if len(empiresDict.keys()) > 1 and targets > 0:
                myShipBattle = self.getMyShipBattle(mySystem)
                myShipBattle.setEmpiresDict(empiresDict)
                myShipBattle.setShipsDict(myShipsDict)
                myShipBattle.setCaptainsDict(captainsDict)
                myShipBattle.setRegimentsExposed(regimentsExposed)

                filename = '../Database/%s/%s.ship' % (self.name, myShipBattle.id)
                storedata.saveToFile(myShipBattle, filename)
                myShipBattle.setMyGalaxy(self)
            
                for empireID in empiresDict.keys():
                    if empireID != '0':
                        myEmpire = self.empires[empireID]
                        myEmpire.setMyShipBattle(myShipBattle.id)
    
    def setupShipsForBattle(self, systemID, myShipsDict, empiresDict, captainsDict):
        """Setup the ships and their captains for battle"""
        targets = 0
        size = int(globals.battlemapQuadSize)/2
        for shipID, myShipDict in myShipsDict.iteritems():
            myShip = self.ships[shipID] 
            myShip.setX = -30 + random.randint(0,size)
            myShip.setY = -30 + random.randint(0,size)
            myShip.setSystemGrid()
            myShip.setPosition()
            myShip.clearTargetShips()
            
            for othershipID in myShipsDict.keys():
                otherShip = self.ships[othershipID]
                if (otherShip.toSystem == systemID and 
                    otherShip.empireID != myShip.empireID and
                    globals.diplomacy[self.empires[otherShip.empireID].diplomacy[myShip.empireID].diplomacyID]['engage'] == 1):
                    myShip.addTargetShip(othershipID)
            
            targets += len(myShip.targets)
    
            if not empiresDict.has_key(myShip.empireID):
                myEmpire = self.empires[myShip.empireID]
                e = {}
                e['id'] = myEmpire.id
                e['name'] = myEmpire.name
                e['color1'] = myEmpire.color1
                e['color2'] = myEmpire.color2
                e['imageFile'] = myEmpire.imageFile
                e['shipDesigns'] = {}
                e['droneDesigns'] = {}
                for droneDesignID, droneDesign in myEmpire.droneDesigns.iteritems():
                    e['droneDesigns'][droneDesignID] = droneDesign.getMyShipDesignInfo()
                
                empiresDict[myShip.empireID] = e

            myShipsDict[shipID] = myShip.getMyShipInfo()
            captainsDict[myShip.captainID] = self.captains[myShip.captainID].getMyInfoAsDict()
    
            if myShip.designID not in empiresDict[myShip.empireID]['shipDesigns'].keys():
                empiresDict[myShip.empireID]['shipDesigns'][myShip.designID] = myShip.myDesign.getMyShipDesignInfo()
        return targets
                        
    def createTransportsForBattle(self, systemID):
        """Check for regiments flying into this system if so create transport ships"""
        regimentsExposed = {}
        for regID, myReg in self.regiments.iteritems():
            if myReg.toSystem == systemID and myReg.fromSystem != myReg.toSystem:
                key = '%s-%s' % (myReg.empireID, myReg.fromSystem)
                if key not in regimentsExposed.keys():
                    regimentsExposed[key] = 1
                else:
                    regimentsExposed[key] += 1
        if regimentsExposed != {}:
            for key, regNum in regimentsExposed.iteritems():
                (empireID, fromSystem) = string.split(key, '-')
                transportNum = funcs.getTransportsRequired(regNum)
                for i in range(transportNum):
                    self.createTransport(empireID, fromSystem, systemID)
        return regimentsExposed
                        
    def getBattleNum(self, shipNum):
        """How many battles should we generate based on total ship numbers and the maxshipsperbattle"""
        num = shipNum/globals.maxShipsPerBattle
        extra = 0
        if num == 0:
            return 1
        else:
            if shipNum%globals.maxShipsPerBattle > 0:
                extra = 1
        num += extra
        return num
     
    def getMyShipBattle(self, mySystem):
        d = {}
        d['id'] = self.getNextID(self.shipBattles)
        d['systemID'] = mySystem.id
        d['systemName'] = mySystem.name
        d['round'] = self.currentRound
        d['empireID'] = mySystem.myEmpireID
        d['cities'] = mySystem.cities
        d['x'] = mySystem.x
        d['y'] = mySystem.y
        myShipBattle = shipbattle.ShipBattle(d)
        myShipBattle.setSeed()
        return myShipBattle
    
    def pickShipsForBattle(self, shipsDict, shipNumPerBattle):
        """Pick random ships for battle"""
        shipKeys = shipsDict.keys()
        newShipDict = {}
        if len(shipKeys) <= globals.maxShipsPerBattle:
            return shipsDict
        
        for i in range(shipNumPerBattle):
            shipID = random.choice(shipKeys)
            shipKeys.remove(shipID)
            newShipDict[shipID] = shipsDict[shipID]
            del shipsDict[shipID]
        return newShipDict
        
    def createDesignShips(self, myEmpire, myShipDesign):
        """Build some Ships for the Design War"""
        mySystem = None
        for systemID, system in self.systems.iteritems():
            if system.myEmpireID == myEmpire.id:
                mySystem = system

        i = 0
        amount = funcs.getShipNum(myShipDesign)
        while i < amount:
            myShip = mySystem.addShip(1, myEmpire.id, myShipDesign.id)
            size = int(globals.battlemapQuadSize)/2
            myShip.setX = -30 + random.randint(0,size)
            myShip.setY = -30 + random.randint(0,size)
            myShip.toSystem = '5'
            myShip.myCaptain.addExperience(800)
            i += 1
    
    def createTransport(self, empireID, fromSystem, toSystem):
        """create a temporary transport ship"""
        shipID = self.getNextID(self.ships)
        myEmpire = self.empires[empireID]
        myDesign = myEmpire.shipDesigns['12']
        
        captainID = self.getNextID(self.captains)
        name = self.getCaptainName()
        myCaptain = captain.Captain({'id':captainID, 'name':name})
        myCaptain.setMyEmpire(myEmpire)
        
        myTransport = ship.Ship({'id':shipID, 'fromSystem':fromSystem, 'empireID':empireID})
        myTransport.toSystem = toSystem
        myTransport.setMyCaptain(myCaptain)
        myTransport.setMyGalaxy(self)
        myTransport.setMyDesign(myDesign)
        myTransport.setMyStatus()
        myTransport.isTransport = 1
        
    def runShipBattle(self, myShipBattle):
        """Run through a Ship Battle"""
        try:
            if myShipBattle.shipsDict == {}:
                return 'No ShipBattle Possible, no ships'
            from anw.client.app import Application
            from anw.war import shipsimulator
            myApp = Application('','','','',myShipBattle,glow=0)
            myApp.loadGame()
            myApp.setIntervalValue(globals.intervalValue)
            running = 1
            game = myApp.game
            myShipBattle.setData(self.componentdata, self.shiphulldata, self.dronehulldata, self.weapondata)
            mode = shipsimulator.ShipSimulator(game, myShipBattle, False, self)
            print 'simulating battle:%s' % myShipBattle.id
            while running:
                if mode.update(globals.intervalValue) == 0:
                    running = 0
            mode = None
            return 'ShipBattle success'
        except:
            return 'galaxy->runShipBattle error: %s' % myShipBattle.systemName
    
    def processGroundBattles(self):
        """Go through all Ground Battles and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultslist = []
            
            # go through each system and check for a battle
            for systemID, mySystem in self.systems.iteritems():
                for regimentID, myRegiment in self.regiments.iteritems():
                    if myRegiment.toSystem == mySystem.id:
                        # regiment is on system, check if its an enemy
                        if (myRegiment.empireID != mySystem.myEmpireID and
                            globals.diplomacy[self.empires[myRegiment.empireID].diplomacy[mySystem.myEmpireID].diplomacyID]['invade'] == 1):
                            self.setDecreasedDiplomacy(self.empires[myRegiment.empireID], mySystem.myEmpireID)
                            resultslist.append(mySystem.processGroundInvasion())
                            break
                    
            return str(resultslist)
        except:
            return 'galaxy->processGroundBattles error'
        
    def setDecreasedDiplomacy(self, empire1, empire2ID):
        """Check that empire1 and empire2 are at war, if not make them"""
        if empire1.id == '0' or empire2ID == '0':
            return
        if (empire1.diplomacy[empire2ID].diplomacyID > 1 and
            empire1.diplomacy[empire2ID].myIntent != 'decrease'):
            empire1.decreaseDiplomacy(empire2ID)
            
    def processShipBattles(self):
        """Go through all Ship Battles and resolve them"""
        try:
            nextRound = self.currentRound+1
            resultslist = []
            
            systemsUnderAttack = self.getSystemsUnderAttack()
            for systemID, mySystem in self.systems.iteritems():
                if systemID in systemsUnderAttack:
                    self.genShipBattle(systemID)
            
            # go through all new shipBattle objects and resolve the battle at server level
            if self.currentRound > 0:
                for battleID, battleDesc in self.shipBattles.iteritems():
                    (round, name) = string.split(battleDesc, '-')
                    round = int(round)
                    if round == self.currentRound:
                        # load ship battle object for processing
                        myShipBattle = storedata.loadFromFile('../Database/%s/%s.ship' % (self.name, battleID))
                        resultslist.append('New Ship Battle at:%s' % myShipBattle.systemName)
                        # run the battle at server level and update stats
                        resultslist.append(self.runShipBattle(myShipBattle))
                    
            return str(resultslist)
        except:
            return 'galaxy->processShipBattles error'

    def getSystemsUnderAttack(self):
        """to Save processing time and creating a bunch of transports that are not needed"""
        threatList = []
        for shipID, myShip in self.ships.iteritems():
            mySystem = self.systems[myShip.toSystem]
            if (myShip.empireID != mySystem.myEmpireID and
                globals.diplomacy[self.empires[myShip.empireID].diplomacy[mySystem.myEmpireID].diplomacyID]['engage'] == 1):
                if mySystem.id not in threatList:
                    threatList.append(mySystem.id)
        
        for regID, myReg in self.regiments.iteritems():
            mySystem = self.systems[myReg.toSystem]
            if (myReg.empireID != mySystem.myEmpireID and
                globals.diplomacy[self.empires[myReg.empireID].diplomacy[mySystem.myEmpireID].diplomacyID]['engage'] == 1):
                if mySystem.id not in threatList:
                    threatList.append(mySystem.id)
        return threatList

        
            
