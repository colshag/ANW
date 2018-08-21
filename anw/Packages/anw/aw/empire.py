# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# empire.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an Empire in ANW
# ---------------------------------------------------------------------------
import string
import types
import order
import mail
import locale
from anw.func import root, funcs, globals
from anw.war import shipdesign, dronedesign
from anw.aw import diplomacy
import empirestat

class Empire(root.Root):
    """A Empire object represents a Player or AI Controlled Empire."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Name of Empire
        self.player = str() # Players unique name in GAE
        self.emailAddress = str() # Email Address of Empire Player
        self.viewIndustry = int() # default map view choices
        self.viewMilitary = int() # default map view choices
        self.viewResources = int() # default map view choices
        self.viewTradeRoutes = int() # default map view choices
        self.color1 = str() # First Color Representing Empire
        self.color2 = str() # Second Color Representing Empire
        self.ai = int() # AI Type if Empire is AI controlled
        self.CR = float() # Total Galactic Credits available
        self.AL = float() # Total Empire Alloys
        self.EC = float() # Total Empire Crystals
        self.IA = float() # Total Empire Arrays
        self.totalProdCR = float() # Total Produced Credits
        self.totalProdAL = float() # Total Produced Alloys
        self.totalProdEC = float()
        self.totalProdIA = float()
        self.alive = int() # Check on Empire still in the game
        self.roundComplete = int() # Empire Turn Complete
        self.loggedIn = int() # Player Logged in or not
        self.level = int() # Players level
        self.experience = float() # Players accumulated experience during game
        self.delay = int() # Players average delay during game
        self.cities = int() # Total Cities under the control of Empire
        self.simulationsLeft = int() # Total Simulation points left
        self.designsLeft = int() # Total Designs Left this Turn
        self.rpAvail = int() # Total Research Points available this Turn
        self.rpUsed = int() # Total Research Points used this Turn
        self.ip = str() # current ip address of player
        self.key = str() # authentication key of player
        self.imageFile = str() # image file of empire
        self.help = list() # list of help areas eg: ['Map','Tech','Diplomacy','Design','EndTurn']
        self.defaultAttributes = ('id', 'level', 'experience', 'delay', 'name', 'player', 'emailAddress',
                                  'viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes',
                                  'color1', 'color2', 'ai', 'CR', 'AL', 'EC', 'IA',
                                  'totalProdCR','totalProdAL','totalProdEC','totalProdIA',
                                  'alive', 'roundComplete', 'loggedIn', 'cities', 'simulationsLeft', 
                                  'designsLeft', 'rpAvail', 'rpUsed', 'ip', 'key', 'imageFile', 'help')
        self.setAttributes(args)
        
        self.setDefaults()
        self.myGalaxy = None # Actual Galaxy Object that contains this Empire
        self.myAIPlayer = None # Link to AI object if empire being controlled by AI Player
        self.techTree = {} # technology Tree of Empire, key=tech id, value=tech obj
        self.techOrders = {} # technology orders for Empire
        self.industryOrders = {} # industry orders for Empire
        self.mailBox = {} # contains all mail ever sent to Empire
        self.diplomacy = {} # key=other empire gid, value=diplomacy object
        self.shipDesigns = {} # all starship designs created key=id, value=obj
        self.droneDesigns = {} # all drone designs created key=id, value=obj
        self.myShipBattles = [] # list of ship battles keys of viewable ship battles
        self.totalResources = [0,0,0] # total resources available to Empire [AL,EC,IA]
        self.creditsInLieu = {} # key=empireID credits going to, value=amount of credits
        self.empireStats = {} # Dict key = empireStat id, value = empireStat object
    
    def setAIinControl(self):
        """Turn the AI player in control of this empire"""
        if self.ai == 0:
            self.ai = 1
            self.setupAIShipDesigns()
            self.setupAIDroneDesigns()
            
    def setupAIShipDesigns(self):
        """AI requires a preset number of ship designs to build its ships"""
        existingNames = []
        for designID, myShipDesign in self.shipDesigns.iteritems():
            if myShipDesign.obsolete == 0:
                existingNames.append(myShipDesign.name)
        for (name, hullID, compDict, weapDict) in self.myAIPlayer.myShipDesigns:
            if name not in existingNames:
                self.genShipDesign(name, hullID, compDict, weapDict, 1)
                
    def setupAIDroneDesigns(self):
        """AI requires a preset number of drone designs to build its ships"""
        existingNames = []
        for designID, myDroneDesign in self.droneDesigns.iteritems():
            if myDroneDesign.obsolete == 0:
                existingNames.append(myDroneDesign.name)
        for (name, hullID, compDict, weapDict) in self.myAIPlayer.myDroneDesigns:
            if name not in existingNames:
                self.genDroneDesign(name, hullID, compDict, weapDict, 1)
        
    def genEmpireStat(self):
        """Generate an Empire Stat"""
        myEmpireStat = empirestat.EmpireStat({'id':str(self.myGalaxy.currentRound)})
        self.empireStats[str(self.myGalaxy.currentRound)] = myEmpireStat
        
    def calculateMyCredits(self):
        """Calculate the credits this empire has made this round"""
        creditTotal = 0.0
        CRcostOfDole = self.getCRCityCosts()
        CRcostOfShips = self.getCRCostOfShips()
        CRcostOfMarines = self.getCRCostOfMarines()
        myEmpireStat = self.empireStats[str(self.myGalaxy.currentRound-1)]
        ALtax = myEmpireStat.ALProduced*self.myGalaxy.prices['AL']
        ECtax = myEmpireStat.ECProduced*self.myGalaxy.prices['EC']
        IAtax = myEmpireStat.IAProduced*self.myGalaxy.prices['IA']
        myEmpireStat.previousCR = self.CR - myEmpireStat.CRfromMarketSales
        myEmpireStat.CRcostOfDole = CRcostOfDole
        myEmpireStat.CRcostOfShips = CRcostOfShips
        myEmpireStat.CRcostOfMarines = CRcostOfMarines
        creditTotal = self.CR + ALtax + ECtax + IAtax - CRcostOfDole - CRcostOfShips - CRcostOfMarines
        if creditTotal < 0.0:
            self.CR = 0.0
        else:
            self.CR = creditTotal
    
    def getCRCityCosts(self):
        """Return the city taxes minus the city dole costs for cities not working"""
        cities = 0
        citiesUsed = 0
        for systemID, mySystem in self.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == self.id:
                cities += mySystem.cities
                citiesUsed += mySystem.citiesUsed
        doleCost = (cities-citiesUsed) * globals.dolePerCity
        return doleCost
    
    def getCRCostOfShips(self):
        """Get the maintenance cost of ships in fleet per round"""
        cost = 0.0
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.empireID == self.id:
                cost += (myShip.myShipHull.mass/globals.shipUpkeep)
                
        variance =self.cities/globals.cityupkeepMultiplier
        return (cost*variance)

    def getCRCostOfMarines(self):
        """Return the upkeep cost of marines"""
        regNum = 0
        for regID, myReg in self.myGalaxy.regiments.iteritems():
            if myReg.empireID == self.id:
                regNum += 1
        
        variance = self.cities/globals.cityupkeepMultiplier
        return (regNum*globals.armyUpkeep*variance)
            
    def setDefaults(self):
        self.alive = 1
        self.viewIndustry = 1
        self.viewMilitary = 1
        self.viewResources = 1
        self.viewTradeRoutes = 1
    
    def askForHelp(self, mail=1):
        """Return an assessment of players current status"""
        try:
            # reset help list
            self.help = []
            resultList = []
            warnings = 0
            critical = 0
            # check end turn
            if self.roundComplete == 0:
                self.addHelp('EndTurn')
            
            #resultList.append('CONFIG')
            #resultList.append('===================================================')
            # check email
            #if self.emailAddress == '':
            #    resultList.append('CRITICAL: You have not set an email address')
            #    critical += 1
            #    self.addHelp('Config')

            # check tech
            resultList.append('')
            resultList.append('RESEARCH')
            resultList.append('===================================================')
            # check if all research used up
            if self.rpAvail > 0:
                critical += 1
                resultList.append('CRITICAL: You have %d Research Points still to allocate this round' % (self.rpAvail))
                self.addHelp('Tech')
            # check if any ongoing research was forgotten
            ongoingTechList = []
            for techID, myTech in self.techTree.iteritems():
                if myTech.complete == 0 and myTech.currentPoints > 0:
                    ongoingTechList.append(techID)
            for orderID, myOrder in self.techOrders.iteritems():
                (id, round) = string.split(orderID, '-')
                if int(round) == self.myGalaxy.currentRound and id in ongoingTechList:
                    ongoingTechList.remove(id)
            for id in ongoingTechList:
                myTech = self.techTree[id]
                critical += 1
                resultList.append('CRITICAL: Place some research into:%s' % myTech.name)
                self.addHelp('Tech')
            
            resultList.append('')
            resultList.append('ECONOMY')
            resultList.append('===================================================')
            # check if any systems are conducting trade routes that will fail due to lack of resources
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if mySystem.myEmpireID == self.id:
                    # check for systems that have built factories that cannot add value
                    factoryCR = 0
                    factoryAL = 0
                    factoryEC = 0
                    factoryIA = 0
                    for key, myIndustryNum in mySystem.myIndustry.iteritems():
                        if myIndustryNum > 0:
                            if self.myGalaxy.industrydata[key].abr[1:] == 'CC':
                                factoryCR = 1
                            elif self.myGalaxy.industrydata[key].abr[1:] == 'AF':
                                factoryAL = 1
                            elif self.myGalaxy.industrydata[key].abr[1:] == 'CM':
                                factoryEC = 1
                            elif self.myGalaxy.industrydata[key].abr[1:] == 'SS':
                                factoryIA = 1
                            
                    if mySystem.prodCR == 0 and factoryCR == 1:
                        resultList.append('CRITICAL: System:%s has Credit Centers, but does not produce Credits(CR)' % mySystem.name)
                        critical += 1
                        self.addHelp('Map')
                    elif mySystem.prodAL == 0 and factoryAL == 1:
                        resultList.append('CRITICAL: System:%s has Alloy Factories, but does not produce Alloys(AL)' % mySystem.name)
                        critical += 1
                        self.addHelp('Map')
                    elif mySystem.prodEC == 0 and factoryEC == 1:
                        resultList.append('CRITICAL: System:%s has Crystal Mines, but does not produce Energy Crystals(EC)' % mySystem.name)
                        critical += 1
                        self.addHelp('Map')
                    elif mySystem.prodIA == 0 and factoryIA == 1:
                        resultList.append('CRITICAL: System:%s has Synthetic Sytems, but does not Intel Arrays(IA)' % mySystem.name)
                        critical += 1
                        self.addHelp('Map')
            
            resultList.append('')
            resultList.append('MILITARY')
            resultList.append('===================================================')
            # get list of regiment ID's currently given restoration orders:
            regimentsToRestore = []
            for orderID, myOrder in self.industryOrders.iteritems():
                if myOrder.round == self.myGalaxy.currentRound and myOrder.type == 'Restore Regiment':
                    regimentsToRestore.append(myOrder.value)
            # check if any regiments need restoring
            for regimentID, myRegiment in self.myGalaxy.regiments.iteritems():
                if (myRegiment.empireID == self.id and 
                    self.myGalaxy.systems[myRegiment.fromSystem].availMIC > 0
                    and myRegiment.strength < 100 and myRegiment.id not in regimentsToRestore):
                        resultList.append('WARNING: Regiment:%s ON:%s is damaged and should be restored' % (myRegiment.name, self.myGalaxy.systems[myRegiment.fromSystem].name))
                        warnings += 1
                        
            resultList.append('')
            resultList.append('DIPLOMACY')
            resultList.append('===================================================')
            # check if empire has any petitions for increased relations from other empires
            for empireID, myDiplomacy in self.diplomacy.iteritems():
                if myDiplomacy.myIntent == 'none' and myDiplomacy.empireIntent == 'increase':
                    resultList.append('WARNING: %s would like to increase relations with you' % self.myGalaxy.empires[empireID].name)
                    warnings += 1
                    self.addHelp('View Diplomacy')
            
            # mail out results to Empire
            results = str(resultList)
            if len(resultList) > 0 and (critical > 0 or warnings > 0) and mail == 1:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound,
                              'messageType':'general', 'subject':'Server Assessment of Empire Status: WARNINGS:%d, CRITICAL:%d' % (warnings, critical),
                              'body':results})
            return ('Server Assessment: WARNINGS:%d, CRITICAL:%d (Check Mail for Assesment)' % (warnings, critical), self.help)
        except:
            return 'empire->askForHelp error'
    
    def addHelp(self, help):
        """Add to help list"""
        if help not in self.help:
            self.help.append(help)
    
    def buildIndustry(self):
        """Take the current industry orders for current round and build industry on systems"""
        try:
            resultList = []
            for indOrderID, myOrder in self.industryOrders.iteritems():
                if myOrder.round == self.myGalaxy.currentRound:
                    result = 'empire->buildIndustry: Order Type not recognized'
                    mySystem = self.myGalaxy.systems[myOrder.system]
                    if myOrder.type == 'Add City':
                        result = mySystem.addCity(myOrder.value)
                    elif myOrder.type == 'Add Industry':
                        (amount, indType) = string.split(myOrder.value, '-')
                        amount = int(amount)
                        result = mySystem.addIndustry(amount, indType)
                    elif myOrder.type == 'Remove Industry':
                        result = mySystem.removeIndustry(myOrder.value)
                    elif myOrder.type == 'Upgrade Industry':
                        result = mySystem.upgradeIndustry(myOrder.value)
                    elif myOrder.type == 'Add Ship':
                        (amount, shipType) = string.split(myOrder.value, '-')
                        amount = int(amount)
                        myShip = mySystem.addShip(amount, self.id, shipType)
                        result = 'ADDED %d %s ON:%s' % (amount, myShip.myDesign.name, mySystem.name)
                    elif myOrder.type == 'Add Regiment':
                        (amount, regimentType) = string.split(myOrder.value, '-')
                        amount = int(amount)
                        result = mySystem.addRegiment(amount, self.id, regimentType)
                    elif myOrder.type == 'Restore Regiment':
                        result = mySystem.restoreRegiment(myOrder.value)
                    elif myOrder.type == 'Upgrade Regiment':
                        result = mySystem.upgradeRegiment(myOrder.value)
                    elif myOrder.type == 'Repair Starship':
                        result = mySystem.repairStarship(myOrder.value)
                    elif myOrder.type == 'Upgrade Starship':
                        (shipID, newDesignID) = string.split(myOrder.value, '-')
                        result = mySystem.upgradeStarship(shipID, newDesignID)
                        
                    # append result
                    resultList.append(result)
            
            # mail out results to Empire
            results = str(resultList)
            if len(resultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                              'messageType':'industry', 'subject':'Empire Wide Industry Results, Round:%d' % self.myGalaxy.currentRound,
                              'body':results})
            return results

        except:
            return 'empire->buildIndustry error'
        
    def calcResearch(self, researchRolls):
        """Calculate each research order for Empire in current round only
        researchRolls is a list of random D100 Rolls that is shared by each Empire (for fairness)"""
        try:
            resultList = []
            # get tech orders for current round
            techOrderDict = self.getMyOrdersByRound('techOrders')
            i = 0
            for id, dtechOrder in techOrderDict.iteritems():
                techID = dtechOrder['type']
                techAmount = int(dtechOrder['value'])
                myTech = self.techTree[techID]
                myTech.currentPoints += techAmount
                ratio = int((float(myTech.currentPoints) / float(myTech.requiredPoints)) * 100)
                ratio = 100 - ratio
                # check if tech has been researched
                desc = 'TECH:%s - Roll Needed:%d, Roll Actual:%d' % (myTech.name, ratio, researchRolls[i])
                if researchRolls[i] >= (ratio):
                    # tech has been researched
                    myTech.currentPoints = myTech.requiredPoints
                    myTech.complete = 1
                    desc = desc + '->SUCCESS!'
                else:
                    # tech has not been researched
                    desc = desc + '->FAILED...'
                
                # update tech
                resultList.append(desc)
                
                # iterate to next D100 Roll
                i += 1
                
            # mail out results to Empire
            results = str(resultList)
            if len(resultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                              'messageType':'research', 'subject':'Research Results, Round:%d' % self.myGalaxy.currentRound,
                              'body':results})
            return results
        except:
            return 'empire->calcResearch error'
        
    def cancelIndustryOrder(self, indOrderID):
        """Cancel Industry Order based on ID provided"""
        try:       
            # refund order
            myOrder = self.industryOrders[indOrderID]
            mySystem = self.myGalaxy.systems[myOrder.system]
            result = 1
            if myOrder.type == 'Add City':
                # return resources
                result = mySystem.refundAddCity()
            elif myOrder.type == 'Add Ship':
                # return resources
                (amount, shipType) = string.split(myOrder.value, '-')
                amount = int(amount)
                result = mySystem.refundAddShip(amount, shipType)
            elif myOrder.type == 'Add Regiment':
                # return resources
                (amount, regimentType) = string.split(myOrder.value, '-')
                amount = int(amount)
                result = mySystem.refundAddRegiment(amount, regimentType)
            elif myOrder.type == 'Restore Regiment':
                result = mySystem.refundRestoreRegiment(myOrder.value)
            elif myOrder.type == 'Upgrade Regiment':
                result = mySystem.refundUpgradeRegiment(myOrder.value)
            elif myOrder.type == 'Repair Starship':
                result = mySystem.refundRepairStarship(myOrder.value)
            elif myOrder.type == 'Upgrade Starship':
                (shipID, newDesignID) = string.split(myOrder.value, '-')
                result = mySystem.refundUpgradeStarship(shipID, newDesignID)
            # remove order
            del self.industryOrders[indOrderID]
            
            return result
        except:
            return 'empire->cancelIndustryOrder error'
            
    def cancelTechOrder(self, techOrderID):
        """Cancel Tech Order based on ID Provided"""
        try:             
            # cancel order
            del self.techOrders[techOrderID]
            
            return result
        except:
            return 'empire->cancelTechOrder error'

    def resolveDiplomacy(self):
        """Resolve the diplomacy in relation to other empires"""
        try:
            resultList = []
            for empireID, myDiplomacy in self.diplomacy.iteritems():
                myAllianceNum = self.getEmpireAlliances(self.id)
                if empireID != '0' and empireID != self.id:
                    otherName = self.myGalaxy.empires[empireID].name
                    otherEmpire = self.myGalaxy.empires[empireID]
                    otherAllianceNum = self.getEmpireAlliances(empireID)
                            
                    if (myDiplomacy.myIntent == 'increase' and myDiplomacy.empireIntent == 'increase' 
                        and ((myAllianceNum < self.myGalaxy.maxPlayersToAlly or otherAllianceNum < self.myGalaxy.maxPlayersToAlly) or (myDiplomacy.diplomacyID < 5))
                        ):
                        # increase diplomacy
                        newLevel = self.getIncreasedDiplomacy(myDiplomacy.diplomacyID)
                        self.setDiplomacy(empireID, newLevel)
                        resultList.append('You have increased Relations with %s to %s' % (otherName, globals.diplomacy[newLevel]['name']))
                        message = 'GOOD NEWS: INCREASED RELATIONS WITH %s !!' % otherName
                        message2 = 'YOUR DIPLOMATIC RELATIONS WITH %s HAVE GONE UP TO %s' % (otherName, globals.diplomacy[newLevel]['name'])
                        self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                                      'messageType':'general', 'subject':message,
                                                      'body':str([message2])})
                    elif myDiplomacy.myIntent == 'decrease' or myDiplomacy.empireIntent == 'decrease':
                        newLevel = self.getDecreasedDiplomacy(myDiplomacy.diplomacyID)
                        # check if war has been declared
                        if newLevel != myDiplomacy.diplomacyID and newLevel == 1:
                            message = '%s and %s have gone to WAR!' % (self.name,otherName)
                            for id, myEmpire in self.myGalaxy.empires.iteritems():
                                if id != '0':
                                    myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':self.myGalaxy.currentRound+1,
                                                      'messageType':'general', 'subject':message,
                                                      'body':str([message])})
                        # decrease diplomacy
                        self.setDiplomacy(empireID, newLevel)
                        resultList.append('You have decreased Relations with %s to %s' % (otherName, globals.diplomacy[newLevel]['name']))
                        message = 'WARNING: DECREASED RELATIONS WITH %s !!!!' % otherName
                        message2 = 'WARNING: YOUR DIPLOMATIC RELATIONS WITH %s HAVE GONE DOWN TO %s' % (otherName, globals.diplomacy[newLevel]['name'])
                        self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                                      'messageType':'general', 'subject':message,
                                                      'body':str([message2])})
                    else:
                        newLevel = myDiplomacy.diplomacyID
                        resultList.append('You have no change in Relations with %s from %s' % (otherName, globals.diplomacy[newLevel]['name']))
                        if (myDiplomacy.myIntent != 'increase' and myDiplomacy.empireIntent == 'increase'):
                            message = 'NOTICE: %s WANTS TO INCREASE DIPLOMACY WITH YOU...' % otherName
                            message2 = '%s Would like to increase diplomacy with you' % otherName
                            self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                                      'messageType':'general', 'subject':message,
                                                      'body':str([message2])})
            
            # mail out results to Empire
            results = str(resultList)
            if len(resultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                              'messageType':'general', 'subject':'Diplomatic Results, Round:%d' % self.myGalaxy.currentRound,
                              'body':results})
            return results
        except:
            return 'empire->resolveDiplomacy error'
    
    def getEmpireAlliances(self, empireID):
        """Count the number of alliances for empire"""
        myEmpire = self.myGalaxy.empires[empireID]
        count = 0
        for id, someDiplomacy in myEmpire.diplomacy.iteritems():
            if globals.diplomacy[someDiplomacy.diplomacyID]['alliance'] == 1:
                count += 1
        return count
    
    def decreaseDiplomacy(self, empireID):
        """Decrease Diplomacy with empire"""
        try:
            otherEmpire = self.myGalaxy.empires[empireID]
            self.diplomacy[empireID].myIntent = 'decrease'
            otherEmpire.diplomacy[self.id].empireIntent = 'decrease'
            return 1
        except:
            return 'empire->decreaseDiplomacy error'

    def increaseDiplomacy(self, empireID):
        """Increase Diplomacy with empire"""
        try:
            otherEmpire = self.myGalaxy.empires[empireID]
            self.diplomacy[empireID].myIntent = 'increase'
            otherEmpire.diplomacy[self.id].empireIntent = 'increase'
            return 1
        except:
            return 'empire->increaseDiplomacy error'

    def getDecreasedDiplomacy(self, diplomacyID):
        """Return a diplomacy ID based on diplomacyID given"""
        if diplomacyID == 1:
            return diplomacyID
        else:
            diplomacyID -= 1
            return diplomacyID
        
    def getIncreasedDiplomacy(self, diplomacyID):
        """Return a diplomacy ID based on diplomacyID given"""
        if globals.diplomacy[diplomacyID]['alliance'] == 1:
            return diplomacyID
        else:
            diplomacyID += 1
            return diplomacyID

    def endTurn(self):
        """Toggle End my Turn"""
        if self.roundComplete == 0:
            self.roundComplete = 1
        else:
            self.roundComplete = 0
        
    def genIndustryOrder(self, indOrderDict):
        """Generate a Build Industry order OR Add City Order for this empire, 
        input: dict = {system -> id of system
                       round -> round number
                       type -> 'Add', 'Upgrade', 'Remove', 'City', etc..
                       value -> industryDataID OR city Resource eg 'CR'
        """
        try:
            result = 'genIndustryOrder Error'
            # allow industry orders through if in round 0
            if self.myGalaxy.currentRound == 0:
                result = 1
            else:
                # validate order can be processed
                result = self.validateGenIndustryOrder(indOrderDict)
                if result == 1:
                    # pay for order
                    result = self.payForIndustryOrder(indOrderDict)
                    
            if result == 1:
                id = self.getNextID(self.industryOrders)
                d = {'id':id}
                for key, value in indOrderDict.iteritems():
                    d[key] = value                        
                myIndOrder = order.IndustryOrder(d)
                self.industryOrders[id] = myIndOrder
                
            return result
        except:
            return 'empire->genIndustryOrder error'
            
    def genMail(self, mailDict):
        """Generate a new mail message to this Empire:"""
        try:
            if type(mailDict['body']) == types.StringType:
                body = eval(mailDict['body'])
            else:
                body = mailDict['body']
            body.insert(0,'=================================================')
            body.insert(0,mailDict['subject'])
            mailDict['body'] = str(body)
            id = self.getNextID(self.mailBox)
            d = {'id':id}
            for key, value in mailDict.iteritems():
                d[key] = value
            
            myMail = mail.Mail(d)
            self.mailBox[id] = myMail
            return 1
        except:
            return 'empire->genMail error'

    def copyShipDesign(self, name, hullID, compDict, weaponDict):
        """Attempt to copy a StarShip Design based on ship being taken over
        don't copy a design if the exact same design is already in design list"""
        for designID, myShipDesign in self.shipDesigns.iteritems():
            if myShipDesign.obsolete == 0:
                (oldname, oldhullID, oldcompDict, oldweaponDict) = myShipDesign.getMyDesign()
                if hullID == oldhullID and compDict == oldcompDict and weaponDict == oldweaponDict:
                    return (designID, myShipDesign.name)
        result = self.genShipDesign(name, hullID, compDict, weaponDict, bypass=1)
        return result
                
    def genShipDesign(self, name, hullID, compDict, weaponDict, bypass=0):
        """Attempt to build a StarShip Design, return name and ID"""
        try:
            id = self.getNextID(self.shipDesigns)
            result = self.validateShipDesign(hullID, compDict, weaponDict, bypass)
            if result == 1:
                designName = '%s%s-%s' % (self.myGalaxy.shiphulldata[hullID].abr, id, name)
                myShipDesign = shipdesign.ShipDesign({'id':id, 'name':designName, 'shipHullID':hullID})
                myShipDesign.setMyEmpire(self)
                myShipDesign.setMyDesign(hullID, compDict, weaponDict)
                if bypass == 0:
                    self.designsLeft -= 1
                result = (myShipDesign.id, myShipDesign.name)
            return result
        except:
            return 'empire->genShipDesign error'
    
    def copyDroneDesign(self, name, hullID, compDict, weaponDict):
        """Attempt to copy a Drone Design based on Carrier ship being taken over
        don't copy a design if the exact same design is already in design list"""
        for designID, myDroneDesign in self.droneDesigns.iteritems():
            if myDroneDesign.obsolete == 0:
                (oldname, oldhullID, oldcompDict, oldweaponDict) = myDroneDesign.getMyDesign()
                if hullID == oldhullID and compDict == oldcompDict and weaponDict == oldweaponDict:
                    return (designID, myDroneDesign.name)
        result = self.genDroneDesign(name, hullID, compDict, weaponDict, bypass=1)
        return result
    
    def genDroneDesign(self, name, hullID, compDict, weaponDict, bypass=0):
        """Attempt to build a Drone Design, return name and ID"""
        try:
            id = self.getNextID(self.droneDesigns)
            result = self.validateDroneDesign(hullID, compDict, weaponDict, bypass)
            if result == 1:
                designName = '%s%s-%s' % (self.myGalaxy.dronehulldata[hullID].abr, id, name)
                myDesign = dronedesign.DroneDesign({'id':id, 'name':designName, 'shipHullID':hullID})
                myDesign.setMyEmpire(self)
                myDesign.setMyDesign(hullID, compDict, weaponDict)
                if bypass == 0:
                    self.designsLeft -= 1
                result = (myDesign.id, myDesign.name)
            return result
        except:
            return 'empire->genDroneDesign error'
        
    def genTechOrder(self, techOrderDict):
        """Generate a research tech order for this empire, 
        input: dict = {round -> round number
                       type -> id of tech (id from empire.techTree)
                       value -> amount to research
        """
        try:
            # add order id to tech order
            id = '%s-%d' % (techOrderDict['type'], techOrderDict['round'])
            d = {'id':id}
            for key, value in techOrderDict.iteritems():
                d[key] = value
            # validate order can be processed
            result = self.validateTechOrder(d)
            if result == 1:
                # pay for order
                result = self.payForTechOrder(d)
                if result == 1:
                    self.processTechOrder(d)
            return result
        except:
            return 'empire->genTechOrder error'
    
    def processTechOrder(self, techOrderDict):
        """Process the order, allow adding or removing from existing order"""
        if techOrderDict['id'] in self.techOrders.keys():
            myOrder = self.techOrders[techOrderDict['id']]
            myOrder.value = str(eval(myOrder.value) + techOrderDict['value'])
            if myOrder.value == '0':
                self.cancelTechOrder(myOrder.id)
        else:
            myTechOrder = order.Order(techOrderDict)
            self.techOrders[techOrderDict['id']] = myTechOrder
    
    def getNetWorthInResources(self):
        """Return (AL, EC, IA) totals by summing all resources and resource
        value of industry and ships"""
        return self.getAllSystemResources()
    
    def getAllSystemResources(self):
        """Return total Resources currently on all systems owned by Empire"""
        myResources = [0,0,0]
        for systemID, mySystem in self.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == self.id:
                (valueAL, valueEC, valueIA) = mySystem.getCurrentIndustryResourceValue()
                myResources[0] += (valueAL+mySystem.AL)
                myResources[1] += (valueEC+mySystem.EC)
                myResources[2] += (valueIA+mySystem.IA)
        return myResources
    
    def getAllShipResources(self):
        """Return total Resources by summing all ships value in resources
        account for ship being damaged"""
        myResources = [0,0,0]
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.empireID == self.id:
                (valueAL, valueEC, valueIA) = myShip.getCurrentResourceValue()
                myResources[0] += valueAL
                myResources[1] += valueEC
                myResources[2] += valueIA
        return myResources
                
    def getMailUpdate(self, listMailID):
        """Return a dict of mail based on mail not in ids given"""
        try:
            d = {}
            myMailBoxDict = self.getMyDictInfo('mailBox')
            for mailID in self.mailBox.keys():
                if mailID not in listMailID:
                    d[mailID] = myMailBoxDict[mailID]
            return d
        except:
            return 'empire->getMailUpdate error'
    
    def getMyEmpireInfo(self):
        """Return only empire information that server wants to give to client"""
        list = ['id', 'name', 'player', 'emailAddress', 'color1', 'color2', 
                'viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes',
                'CR', 'AL', 'EC', 'IA', 'cities', 'simulationsLeft',
                'designsLeft', 'rpAvail', 'rpUsed', 'ip', 'key', 'imageFile',
                'roundComplete', 'loggedIn']
        d = self.getSelectedAttr(list)
        d['techOrders'] = self.getMyOrdersByRound('techOrders')
        d['industryOrders'] = self.getMyOrdersByRound('industryOrders')
        d['researchedIndustry'] = self.getMyResearchedIndustry()
        d['researchedRegiments'] = self.getMyResearchedRegiments()
        d['mailBox'] = self.getMyDictInfo('mailBox')
        d['help'] = self.help
        d['diplomacy'] = self.getMyDiplomacyInfo()
        d['totalResources'] = self.totalResources
        d['creditsInLieu'] = self.creditsInLieu
        return d
    
    def getMyDiplomacyInfo(self):
        """Return the diplomacy information but keep out other players intents if they are negative"""
        d = self.getMyDictInfo('diplomacy')
        for empireID, diplomacyDict in d.iteritems():
            for key, value in diplomacyDict.iteritems():
                if value == 'decrease' and key == 'empireIntent':
                    d[empireID][key] = 'none'
        return d
    
    def getMyOrdersByRound(self, dictOrderName):
        """Return only appropriate Industry Orders for this empire,
        base on round number"""
        d = {}
        myDict = getattr(self, dictOrderName)
        for id, myOrder in myDict.iteritems():
            if myOrder.round == self.myGalaxy.currentRound:
                # return Order
                d[id] = myOrder.getMyInfoAsDict()
        return d
    
    def getMyResearchedRegiments(self):
        """Return list of regiment id's usable by empire"""
        list = []
        for id, myRegimentData in self.myGalaxy.regimentdata.iteritems():
            # check if regiment type is researched
            myTech = self.techTree[myRegimentData.techReq]
            if myTech.complete == 1:
                list.append(id)
        list = funcs.sortStringList(list)
        return list
    
    def getMyResearchedIndustry(self):
        """Return list of industry id's usable by empire"""
        list = []
        for id, myIndustryData in self.myGalaxy.industrydata.iteritems():
            # check if industry is researched
            myTech = self.techTree[myIndustryData.techReq]
            if myTech.complete == 1:
                list.append(id)
        list = funcs.sortStringList(list)
        return list

    def getMyShipDesigns(self):
        """Return Ship Designs"""
        d = {}
        for id, myDesign in self.shipDesigns.iteritems():
            if myDesign.obsolete == 0:
                d[id] = myDesign.getMyDesign()
        return d

    def getMyDroneDesigns(self):
        """Return Drone Designs"""
        d = {}
        for id, myDesign in self.droneDesigns.iteritems():
            if myDesign.obsolete == 0:
                d[id] = myDesign.getMyDesign()
        return d
    
    def getOtherEmpireInfo(self):
        """Return only limited Empire information"""
        list = ['id', 'name', 'color1', 'color2', 'imageFile', 'roundComplete',
                'loggedIn', 'alive', 'ai']
        d = self.getSelectedAttr(list)
        return d
    
    def getShipBattleDict(self):
        """Return a dictionary of ship battles viewable to Empire"""
        try:
            d = {}
            for shipBattleKey in self.myShipBattles:
                desc = self.myGalaxy.shipBattles[shipBattleKey]
                (round, systemName) = string.split(desc, '-')
                d[shipBattleKey] = 'ShipBattle %s - Round %s - On: %s' % (shipBattleKey, round, systemName)
            return d
        except:
            return 'empire->getShipBattleDict error'
    
    def payForIndustryOrder(self, indOrderDict):
        """If Industry Order requires payment, pay for order"""
        try:
            mySystem = self.myGalaxy.systems[indOrderDict['system']]
            type = indOrderDict['type']
            value = indOrderDict['value']
            # go through each order type
            if type == 'Add Ship':
                (amount, shipType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.payForAddShip(amount, shipType)
            elif type == 'Add Regiment':
                (amount, regimentType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.payForAddRegiment(amount, regimentType)
            elif type == 'Restore Regiment':
                return mySystem.payForRestoreRegiment(value)
            elif type == 'Upgrade Regiment':
                return mySystem.payForUpgradeRegiment(value)
            elif type == 'Repair Starship':
                return mySystem.payForRepairStarship(value)
            elif type == 'Upgrade Starship':
                (shipID, newDesignID) = string.split(value, '-')
                return mySystem.payForUpgradeStarship(shipID, newDesignID)
            else:
                return 'empire->payForIndustryOrder: Unknown type'
        except:
            return 'empire->payForIndustryOrder error'
    
    def payForTechOrder(self, techOrderDict):
        """Pay in Research Points for Tech Order"""
        try:
            amount = int(techOrderDict['value'])
            self.rpAvail -= amount
            self.rpUsed += amount
            return 1
        except:
            return 'empire->payForTechOrder error'
        
    def processSystems(self):
        """Go through each system that is owned by this Empire and process them: """
        try:
            if self.id == '0':
                return
            # clear data
            self.rpAvail = 0
            self.rpUsed = 0
            self.simulationsLeft = 0
            self.designsLeft = 0
                
            # generate result lists
            ResourceResultList = []
            totalAL = 0.0
            totalEC = 0.0
            totalIA = 0.0
            totalSims = 0
            totalDesigns = 0
            ResearchResultList = []
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if mySystem.myEmpire.id == self.id:
                    # reset system data
                    mySystem.resetData()
                    
                    # calculate income generated
                    ResourceResultList.append(mySystem.genWealth())
                    totalAL += mySystem.prodAL
                    totalEC += mySystem.prodEC
                    totalIA += mySystem.prodIA
                    
                    # calculate research points generated
                    (amount, message) = mySystem.returnIndustryOutput('RC','Research Points')
                    if amount != 0:
                        self.rpAvail += amount
                        ResearchResultList.append(message)
                    
                    # calculate simulations allowed
                    (amount, message) = mySystem.returnIndustryOutput('SC','Simulations')
                    if amount != 0:
                        self.simulationsLeft += amount
                    
                    # calculate designs allowed
                    (amount, message) = mySystem.returnIndustryOutput('DC','Designs')
                    if amount != 0:
                        self.designsLeft += amount
                    
                    # calculate shipyard capacity
                    (amount, message) = mySystem.returnIndustryOutput('SY','Shipyard Capacity Points')
                    mySystem.setSYC(amount)
                    
                    # calculate military installation capacity
                    (amount, message) = mySystem.returnIndustryOutput('MI','Military Installation Points')
                    mySystem.setMIC(amount)
                        
                    # calculate warp gate capacity
                    (amount, message) = mySystem.returnIndustryOutput('WG','Warp Gate Capacity Points')
                    mySystem.setWGC(amount)
                    
                    # calculate radar strength
                    (amount, message) = mySystem.returnIndustryOutput('RS','Radar Strength')
                    mySystem.setRadarStrength(amount)
                    
                    # calculate jamming strength
                    (amount, message) = mySystem.returnIndustryOutput('JS','Jamming Strength')
                    mySystem.setJammingStrength(amount)
                    
                    # calculate fleet cadets
                    (amount, message) = mySystem.returnIndustryOutput('FA','Fleet Cadets')
                    mySystem.addFleetCadets(amount)
                    
                    # calculate army cadet classes
                    (amount, message) = mySystem.returnIndustryOutput('MA','Marine Cadet Classes')
                    mySystem.addArmyCadets(amount)
            
            try:
                myEmpireStat = self.empireStats[str(self.myGalaxy.currentRound)]
                myEmpireStat.ALProduced = totalAL
                myEmpireStat.ECProduced = totalEC
                myEmpireStat.IAProduced = totalIA
            except:
                pass
            
            # add totals
            ResourceResultList.append('===================================================')
            ResourceResultList.append('Total Resources Generated:')
            ResourceResultList.append('(AL) = %d Alloys' % totalAL)
            ResourceResultList.append('(EC) = %d Energy Crystals' % totalEC)
            ResourceResultList.append('(IA) = %d Intel Arrays' % totalIA)
            
            ResearchResultList.append('===================================================')
            ResearchResultList.append('Total Research Points Generated: %d' % self.rpAvail)
            
            # mail results to Empire
            researchResults = str(ResearchResultList)
            resourceResults = str(ResourceResultList)
            results = '%s\n\n%s' % (researchResults, resourceResults)
            if len(ResearchResultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                  'messageType':'research', 'subject':'Research Points Generated, Round:%d' % self.myGalaxy.currentRound,
                                  'body':researchResults})
            if len(ResourceResultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                  'messageType':'economics', 'subject':'Economic Report, Round:%d' % self.myGalaxy.currentRound,
                                  'body':resourceResults})
            return results
        except:
            return 'empire->processSystems error'

    def refundTechOrder(self, techOrderID):
        """Refund for the tech order"""
        try:
            myTechOrder = self.techOrders[techOrderID]
            amount = int(myTechOrder.value)
            self.rpAvail += amount
            self.rpUsed -= amount
            return 1
        except:
            return 'empire->refundTechOrder error'
            
    def removeShipDesign(self, shipDesignID):
        """Remove Ship Design based on ID Provided"""
        try:
            # make sure no ships currently have this design first
            for shipID, myShip in self.myGalaxy.ships.iteritems():
                if myShip.designID == shipDesignID and myShip.empireID == self.id:
                    return 'You cannot remove this design because you still have ships using it'
            
            # make sure no ships being built with this design
            for orderID, myIndustryOrder in self.industryOrders.iteritems():
                if myIndustryOrder.type == 'Add Ship' and myIndustryOrder.round == self.myGalaxy.currentRound:
                    (amount, designID) = string.split(myIndustryOrder.value, '-')
                    if designID == shipDesignID:
                        return 'You have a ship currently being built with this design, remove ship build order'

            # set design obsolete
            self.shipDesigns[shipDesignID].obsolete = 1
            return 1
        except:
            return 'empire->removeShipDesign error'

    def removeDroneDesign(self, droneDesignID):
        """Remove Drone Design based on ID Provided"""
        try:
            
            for shipdesignID, myShipDesign in self.shipDesigns.iteritems():
                if myShipDesign.obsolete == 0:
                    if self.isDroneIDinShipDesignID(droneDesignID, shipdesignID):
                        return 'Remove carrier designs using this drone design first'
            
            for shipID, myShip in self.myGalaxy.ships.iteritems():
                if myShip.empireID == self.id:
                    if self.isDroneIDinShipDesignID(droneDesignID, myShip.designID):
                        return 'You cannot remove this drone design because you still have ships using it'
            
            for orderID, myIndustryOrder in self.industryOrders.iteritems():
                if myIndustryOrder.type == 'Add Ship' and myIndustryOrder.round == self.myGalaxy.currentRound:
                    (amount, designID) = string.split(myIndustryOrder.value, '-')
                    if self.isDroneIDinShipDesignID(droneDesignID, designID):
                        return 'You have a ship currently being built with this drone design, remove ship build order'

            # set design obsolete
            self.droneDesigns[droneDesignID].obsolete = 1
            return 1
        except:
            return 'empire->removeDroneDesign error'
    
    def isDroneIDinShipDesignID(self, droneDesignID, shipDesignID):
        myShipDesign = self.shipDesigns[shipDesignID]
        for id, myQuad in myShipDesign.quads.iteritems():
            for id, myWeapon in myQuad.weapons.iteritems():
                if myWeapon.droneID == droneDesignID:
                    return 1
        return 0
        
    def resetData(self):
        """Reset Data for Empire"""
        self.ip = ''
        self.loggedIn = 0
        self.key = ''
    
    def resetDesigns(self):
        """Make sure each ship design is checked if its still not researchable"""
        for designID, myDesign in self.shipDesigns.iteritems():
            if myDesign.obsolete == 0:
                myDesign.setMyStatus()
        for designID, myDesign in self.droneDesigns.iteritems():
            if myDesign.obsolete == 0:
                myDesign.setMyStatus()
        
    def addDelay(self):
        """Check if empire needs to add delay"""
        if (self.roundComplete == 0 
            and self.myGalaxy.currentRound > 1 
            and self.isMoreThanTwoPlayersAlive()
            and self.alive == 1
            and self.id != '0'):
            self.delay += 1
        
    def isMoreThanTwoPlayersAlive(self):
        count = 0
        for empireID, myEmpire in self.myGalaxy.empires.iteritems():
            if myEmpire.alive == 1 and myEmpire.id != '0':
                count += 1
        if count > 2:
            return 1
        return 0
            
    def resetRoundData(self):
        """Reset Round Data"""
        self.roundComplete = 0
        if self.myGalaxy.currentRound > 5:
            self.techOrders = {}
            self.industryOrders = {}
        self.totalResources = self.getNetWorthInResources()
        self.setTotalCities()
        self.amIDead()
    
    def setTotalCities(self):
        """Set the total cities under Empire Control"""
        self.cities = 0
        for systemID, mySystem in self.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == self.id:
                self.cities += mySystem.cities
    
    def amIDead(self):
        """Check if Empire has no more cities, if so, send out email and set alive=0"""
        if self.cities == 0 and self.alive == 1:
            message = '%s has been defeated' % (self.name)
            for id, myEmpire in self.myGalaxy.empires.iteritems():
                if id != '0':
                    myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':self.myGalaxy.currentRound+1,
                                          'messageType':'general', 'subject':message,
                                          'body':str([message])})
            self.alive = 0
        elif self.cities > 0 and self.alive == 0:
            if self.myGalaxy.currentRound > 4 and self.ai == 0:
                self.alive = 1
    
    def sendMyCredits(self):
        """Send all my Credits that were setup for this round"""
        try:
            for empireID, amount in self.creditsInLieu.iteritems():
                toEmpire = self.myGalaxy.empires[empireID]
                result = toEmpire.depositCR(amount)
                if result == 1:
                    dMail = {'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                             'messageType':'economics', 'subject':'Credit Transfer, Round:%d' % self.myGalaxy.currentRound,
                             'body':str(['%d Credits Transfered from %s to %s' % (amount, self.name, toEmpire.name)])}
                    self.genMail(dMail)
                    toEmpire.genMail(dMail)
            self.creditsInLieu = {}
            return 1
        except:
            return 'empire->sendCredits error'
    
    def sendCreditsInLieu(self, empireID, amount):
        """Place Credits into a bank to be sent later"""
        try:
            toEmpire = self.myGalaxy.empires[empireID]
            result = self.withdrawCR(amount)
            if result == 1:
                if empireID in self.creditsInLieu.keys():
                    self.creditsInLieu[empireID] += amount
                else:
                    self.creditsInLieu[empireID] = amount
                return 1
            else:
                return result
        except:
            return 'empire->sendCreditsInLieu error'
    
    def withdrawCR(self, amount):
        """Withdraw credits from account"""
        if amount < 0:
            return 'cannot withdraw negative credits'
        if self.CR < amount:
            return 'not enough credits'
        self.CR -= amount
        return 1
    
    def depositCR(self, amount):
        """Deposit credits into account"""
        if amount < 0:
            return 'cannot deposit negative credits'
        self.CR += amount
        return 1
        
    def cancelCreditsInLieu(self, empireID):
        """Cancel a send credits command"""
        try:
            if empireID not in self.creditsInLieu.keys():
                return 'invalid cancel credits order'
            amount = self.creditsInLieu[empireID]
            del self.creditsInLieu[empireID]
            result = self.depositCR(amount)
            return result
        except:
            return 'empire->cancelCreditsInLieu'
    
    def mailEconomicReport(self):
        """Mail the Empire an income Report"""
        myEmpireStat = self.empireStats[str(self.myGalaxy.currentRound-1)]
        body = []
        locale.setlocale( locale.LC_ALL, '' )
        ALFactor = self.myGalaxy.prices['AL'] / globals.AL
        ECFactor = self.myGalaxy.prices['EC'] / globals.EC
        IAFactor = self.myGalaxy.prices['IA'] / globals.IA
        ecoFactor = (ALFactor+ECFactor+IAFactor)/3.0
        
        ALtax = myEmpireStat.ALProduced*self.myGalaxy.prices['AL']
        ECtax = myEmpireStat.ECProduced*self.myGalaxy.prices['EC']
        IAtax = myEmpireStat.IAProduced*self.myGalaxy.prices['IA']
        totalCredits = myEmpireStat.CRfromMarketSales+ALtax+ECtax+IAtax
        totalDebits = myEmpireStat.CRcostOfDole+myEmpireStat.CRcostOfShips+myEmpireStat.CRcostOfMarines
        totalDebits = totalDebits*ecoFactor
        body.append('======  CREDIT INCOME REPORT FOR ROUND: %s  =======' % self.myGalaxy.currentRound)
        body.append('========================================================')
        body.append('')
        body.append('======  CREDITS THIS ROUND:  ======================')
        body.append('AL PRODUCTION TAX (AL produced x AL Price)(%d x %d) = %s' % (myEmpireStat.ALProduced, self.myGalaxy.prices['AL'],locale.format('%d', ALtax, True)))
        body.append('EC PRODUCTION TAX (EC Produced x EC price)(%d x %d) = %s' % (myEmpireStat.ECProduced, self.myGalaxy.prices['EC'],locale.format('%d', ECtax, True)))
        body.append('IA PRODUCTION TAX (IA Produced x IA price)(%d x %d) = %s' % (myEmpireStat.IAProduced, self.myGalaxy.prices['IA'],locale.format('%d', IAtax, True)))
        body.append('MARKET SALES and REBATES = %s' % locale.format('%d', myEmpireStat.CRfromMarketSales, True))
        body.append('--------------------------------------------------------')
        body.append('TOTAL CREDITS TO ACCOUNT: %s' % locale.format('%d', totalCredits, True))
        body.append('========================================================')
        body.append('')
        body.append('======  DEBITS THIS ROUND:  ======================')
        body.append('DOLE FOR NON WORKING CITIES (%d x Cities not Working) = %s' % (globals.dolePerCity, locale.format('%d', myEmpireStat.CRcostOfDole, True)))
        body.append('SHIP UPKEEP = %s' % locale.format('%d', myEmpireStat.CRcostOfShips, True))
        body.append('MARINE UPKEEP = %s' % locale.format('%d', myEmpireStat.CRcostOfMarines, True))
        body.append('ECO FACTOR = %s' % locale.format('%.4f', ecoFactor, True))
        body.append('--------------------------------------------------------')
        body.append('TOTAL DEBITS TO ACCOUNT: %s' % locale.format('%d', totalDebits, True))
        body.append('========================================================')
        body.append('')
        body.append('======  ACCOUNT BALANCE:  ======================')
        body.append('LAST ROUND BALANCE: %s' % locale.format('%d', myEmpireStat.previousCR, True))
        body.append('TOTAL CREDITS TO ACCOUNT: %s' % locale.format('%d', totalCredits, True))
        body.append('TOTAL DEBITS TO ACCOUNT: %s' % locale.format('%d', totalDebits, True))
        body.append('--------------------------------------------------------')
        body.append('ACCOUNT BALANCE = %s' % locale.format('%d', self.CR, True))
        body.append('========================================================')
        dMail = {'fromEmpire':self.id, 'round':self.myGalaxy.currentRound,
                 'messageType':'economics', 'subject':'Credit Report, Round:%d' % self.myGalaxy.currentRound,
                 'body':str(body)}
        
        self.genMail(dMail)
    
    def setInitialDiplomacy(self):
        """Set the initial Diplomacy of Empire to no relations"""
        for i in range(self.myGalaxy.numEmpires):
            self.setDiplomacy(str(i), 2)
        for diplomacyGroup in self.myGalaxy.startingAllies:
            if self.id in diplomacyGroup:
                for otherID in diplomacyGroup:
                    self.setDiplomacy(otherID, 6)
        
    def setDiplomacy(self, empireID, diplomacyID):
        """Set the diplomacy for empire given in relation to this empire"""
        d = {'empireID':empireID, 'diplomacyID':diplomacyID, 'myIntent':'none', 'empireIntent':'none'}
        myDiplomacy = diplomacy.Diplomacy(d)
        self.diplomacy[empireID] = myDiplomacy
        
    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this Empire"""
        self.myGalaxy = galaxyObject
        galaxyObject.empires[self.id] = self

    def setMyShipBattle(self, shipBattleKey):
        """Add to my list of viewable ship battles"""
        self.myShipBattles.append(shipBattleKey)

    def shareShipBattle(self, shipBattleKey, empireToShareID):
        """Share a ship battle with another empire"""
        try:
            # validate first
            if shipBattleKey not in self.myShipBattles:
                return 'Cannot Share a battle that is not available in Ship Battle List'
            
            # share ship battle
            otherEmpire = self.myGalaxy.empires[empireToShareID]
            
            # check if empire already has that battle
            if shipBattleKey in otherEmpire.myShipBattles:
                return 'Other Empire already has that Battle in Ship Battle List'
            else:
                otherEmpire.setMyShipBattle(shipBattleKey)
                shipBattle = self.myGalaxy.shipBattles[shipBattleKey]
                (round,name) = string.split(shipBattle, '-')
                # notify other empire that you have shared a battle
                dMail = {'fromEmpire':self.id, 'round':self.myGalaxy.currentRound, 'messageType':'general',
                         'subject':'Empire:%s Has Shared a Ship Battle with you' % self.name, 
                         'body':str(['Click on Battles->View Past Battles to watch this battle.',
                                     'Battle Information:',
                                     'System: %s' % name,
                                     'Round:  %s' % round])}
                otherEmpire.genMail(dMail)
            return 1
        except:
            return 'empire->shareShipBattle error'

    def validateGenIndustryOrder(self, indOrderDict):
        """Validate generating industry order, return 1=pass, string=fail"""
        try:
            mySystem = self.myGalaxy.systems[indOrderDict['system']]
            if mySystem.myEmpire.id != self.id:
                return 'Invalid Order, coming from system not owned by Empire'
            type = indOrderDict['type']
            value = indOrderDict['value']
            # go through each order type
            if type == 'Add Ship':
                (amount, shipType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.validateAddShip(amount, shipType)
            elif type == 'Add Regiment':
                (amount, regimentType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.validateAddRegiment(amount, regimentType)
            elif type == 'Restore Regiment':
                return mySystem.validateRestoreRegiment(value)
            elif type == 'Upgrade Regiment':
                return mySystem.validateUpgradeRegiment(value)
            elif type == 'Repair Starship':
                return mySystem.validateRepairStarship(value)
            elif type == 'Upgrade Starship':
                (shipID, newDesignID) = string.split(value, '-')
                return mySystem.validateUpgradeStarship(shipID, newDesignID)
            else:
                return 'empire->validateGenIndustryOrder: Unknown type'
        except:
            return 'empire->validateGenIndustryOrder error'

    def validateShipDesign(self, hullID, compDict, weaponDict, bypass=0):
        """Validate that Ship Design supplied is valid"""
        try:
            myShipHull = self.myGalaxy.shiphulldata[hullID]
            # check that Empire has enough designs left this round
            if self.designsLeft == 0 and bypass == 0:
                return 'You do not have enough Design Centers to build another Ship Design this Round'
            # check weapons
            for key, valueDict in weaponDict.iteritems():
                myWeaponData = self.myGalaxy.weapondata[valueDict['type']]
                if myWeaponData.abr in globals.weaponLimitations[myShipHull.function]:
                    return '%s cannot be added to %s' % (myWeaponData.name, myShipHull.name)
            # check components
            genCount = 0
            engineCount = 0
            rotCount = 0
            for key, valueList in compDict.iteritems():
                # check that only valid number of components submitted
                if len(valueList) > myShipHull.componentNum:
                    return 'You are attempting to add more components then the max allowed'
                for componentID in valueList:
                    if componentID[0] != 'W':
                        # check technology
                        myComponentData = self.myGalaxy.componentdata[componentID]
                        if (myComponentData.abr in globals.componentLimitations[myShipHull.function] or
                            (myComponentData.abr in ['CSE','CRT'] and hullID not in ['8','9','10','11','12'] )):
                            return '%s cannot be added to %s' % (myComponentData.name, myShipHull.name)

                        # add to counts
                        abr = self.myGalaxy.componentdata[componentID].abr
                        if abr == 'SSE' or abr == 'PSE' or abr == 'USE' or abr == 'CSE':
                            engineCount += 1
                        elif abr == 'SRT' or abr == 'PRT' or abr == 'URT' or abr == 'CRT':
                            rotCount += 1
                        elif abr == 'SPP' or abr == 'PPP' or abr == 'UPP':
                            genCount += 1
                            
            # make sure design has at least one of each (engine, rotation, power)
            if engineCount == 0:
                return 'Your Ship Design does not have any Engine components'
            if genCount == 0:
                return 'Your Ship Design does not have any Power Plant components'
            if rotCount == 0:
                return 'Your Ship Design does not have any Rotational Thruster components'
            
            # design is valid
            return 1
        except:
            return 'empire->validateShipDesign error'

    def validateDroneDesign(self, hullID, compDict, weaponDict, bypass=0):
        """Validate that Drone Design supplied is valid"""
        try:
            myDroneHull = self.myGalaxy.dronehulldata[hullID]
            # check that Empire has enough designs left this round
            if self.designsLeft == 0 and bypass == 0:
                return 'You do not have enough Design Centers to build another Drone Design this Round'
            # check weapons
            for key, valueDict in weaponDict.iteritems():
                myWeaponData = self.myGalaxy.weapondata[valueDict['type']]
                if myWeaponData.abr in globals.weaponLimitations[myDroneHull.function]:
                    return '%s cannot be added to %s' % (myWeaponData.name, myDroneHull.name)
            # check components
            genCount = 0

            for key, valueList in compDict.iteritems():
                # check that only valid number of components submitted
                if len(valueList) > myDroneHull.componentNum:
                    return 'You are attempting to add more components then the max allowed'
                for componentID in valueList:
                    if componentID[0] != 'W':
                        # check technology
                        myComponentData = self.myGalaxy.componentdata[componentID]
                        if myComponentData.abr in globals.componentLimitations[myDroneHull.function]:
                            return '%s cannot be added to %s' % (myComponentData.name, myDroneHull.name)
    
                        # add to counts
                        abr = self.myGalaxy.componentdata[componentID].abr
                        if abr == 'SPP' or abr == 'PPP' or abr == 'UPP':
                            genCount += 1
                        
            if genCount == 0:
                return 'Your Drone Design does not have any Power Plant components'
            
            # design is valid
            return 1
        except:
            return 'empire->validateDroneDesign error'

    def validateTechOrder(self, techOrderDict):
        """Validate generating tech order, return 1=pass, string=fail"""
        try:
            type = techOrderDict['type']
            value = int(techOrderDict['value'])
            techGid = techOrderDict['id']
            myTech = self.techTree[type]
            
            # have the prereqs been researched?
            num = 0
            for id in myTech.preTechs:
                preTech = self.techTree[id]
                if preTech.complete == 1:
                    num += 1
            if num < myTech.preTechNum:
                if myTech.preTechNum == 1:
                    return 'Research:%s First ' % preTech.name
                else:
                    return 'Research:%d more preTechs First' % (myTech.preTechNum-num)
            # has this already been researched?
            if myTech.complete == 1:
                return 'You have already researched this technology'
            # is there enough research points available?
            if value > self.rpAvail:
                return 'You do not have enough research points left: Req=%d, Avail=%d' % (value, self.rpAvail)
            # have they allocated too many points to this tech?
            if value > (myTech.requiredPoints - myTech.currentPoints):
                return 'You are placing too much research on this technology'
            return 1
        except:
            return 'empire->validateTechOrder error'    

    def calculateExperience(self):
        """Calculate Player Experience currently, if lower then past calcs keep past calc"""
        try:
            resultList = []
            oldExp = self.experience
            s = 'Your Highest Calculated Experience from Past Rounds = %d' % oldExp
            resultList.append(s)
            resultList.append('===================================================')
            newExp = 0.0
            (newExp, text) = self.getExpForPlanetsTaken(newExp)
            for s in text:
                resultList.append(s)
            
            (newExp, text) = self.getExpForTech(newExp)
            for s in text:
                resultList.append(s)
            
            (newExp, text) = self.getExpForCapitols(newExp)
            for s in text:
                resultList.append(s)
                
            (newExp, text) = self.getExpForNoDelay(newExp)
            for s in text:
                resultList.append(s)
                
            if newExp > oldExp:
                s = 'Congrats experience earned this round is %.2f and is the most you have earned so far!!' % newExp
                self.experience = newExp
            else:
                s = 'Your experience this round is %.2f and is less then past rounds so we will discount it' % newExp
            resultList.append(s)
                
            results = str(resultList)
            if len(resultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                              'messageType':'general', 'subject':'Experience Calculated, Round:%d' % self.myGalaxy.currentRound,
                              'body':results})
            return results

        except:
            return 'empire->calculateExperience error'

    def getExpForPlanetsTaken(self, exp):
        text = []
        totalLevels = self.myGalaxy.delayBonus
        myLevel = self.level
        totalLevels = totalLevels - myLevel
        totalExp = totalLevels*400.0
        text.append('Your Galaxy Total Experience up for grabs = %.2f' % totalExp)
        galaxyCities = float(self.myGalaxy.cities)
        myCities = float(self.cities)
        totalRounds = float(self.myGalaxy.currentRound)
        myDelay = self.delay
        try:
            galaxyTakenOver = myCities/galaxyCities
        except:
            galaxyTakenOver = 0.0
        text.append('Total Galaxy Taken over by your Empire = %d' % (galaxyTakenOver*100) + '%')
        myExp = totalExp*galaxyTakenOver
        text.append('(Experience for grabs) x (Galaxy taken over) = %.2f' % myExp)
        try:
            delayPenalty = (totalRounds-myDelay)/totalRounds
        except:
            delayPenalty = 0.0
        text.append('Delay penalty (rounds-your delay)/total rounds played so far = %.2f' % delayPenalty)
        myExp = myExp*delayPenalty
        text.append('Experience Earned x Delay Penalty = %.2f' % myExp)
        text.append('===================================================')
        return (myExp+exp, text)
    
    def getExpForTech(self, exp):
        text = []
        totalTech = 0
        doneTech = 0
        for id, myTech in self.techTree.iteritems():
            if myTech.techAge > 1:
                totalTech += 1
                if myTech.complete == 1:
                    doneTech += 1
        techRatio = float(doneTech)/float(totalTech)
        text.append('Your Technology Researched/Total to Research = (%d/%d) = %.2f' % (doneTech, totalTech, techRatio) + '%')
        myExp = techRatio*500.0
        text.append('Experience bonus = 500 x ratio = %.2f' % myExp)
        text.append('===================================================')
        return (myExp+exp, text)
    
    def getExpForCapitols(self, exp):
        text = []
        count = 0
        for id, mySystem in self.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == self.id and mySystem.cities == 40:
                count += 1
        text.append('Total Capitol Planets under your control = %d' % count)
        myExp = count*400.0
        text.append('Experience bonus = 400 x total = %.2f' % myExp)
        text.append('===================================================')
        return (myExp+exp, text)
    
    def getExpForNoDelay(self, exp):
        text = []
        if len(self.myGalaxy.empires.keys()) == 3:
            text.append('Delay is not accounted for in a 2 player game')
            myExp = 0
        elif self.myGalaxy.currentRound < 6:
            text.append('Delay bonus not used until after Round 5')
            myExp = 0
        else:
            myDelay = self.delay
            if myDelay == 0:
                myExp = 1000.0
            elif myDelay == 1:
                myExp = 500.0
            elif myDelay == 2:
                myExp = 200.0
            elif myDelay == 3:
                myExp = 100.0
            elif myDelay == 4:
                myExp = 50.0
            else:
                myExp = 0
            text.append('You have %d delay in the game, you get %.2f Experience bonus!' % (myDelay, myExp))
            
        text.append('===================================================')    
        return (myExp+exp, text)
    