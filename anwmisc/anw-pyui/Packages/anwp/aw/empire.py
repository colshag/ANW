# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# empire.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an Empire in ANW
# ---------------------------------------------------------------------------
import string

import anwp.func.root
import order
import mail
import anwp.func.funcs
import anwp.func.globals
import anwp.func.storedata
import anwp.func.names
import anwp.war.component
import anwp.war.quad
import anwp.war.shipdesign
import anwp.war.dronedesign
import anwp.war.weapon

class Empire(anwp.func.root.Root):
    """A Empire object represents a Player or AI Controlled Empire."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Name of Empire
        self.password = str() # Password to login to game as Empire
        self.emailAddress = str() # Email Address of Empire Player
        self.viewIndustry = int() # default map view choices
        self.viewMilitary = int() # default map view choices
        self.viewResources = int() # default map view choices
        self.viewTradeRoutes = int() # default map view choices
        self.color1 = str() # First Color Representing Empire
        self.color2 = str() # Second Color Representing Empire
        self.ai = int() # AI Type if Empire is AI controlled
        self.CR = float() # Total Empire Credits
        self.AL = float() # Total Empire Alloys
        self.EC = float() # Total Empire Crystals
        self.IA = float() # Total Empire Arrays
        self.totalProdCR = float() # Total Produced Credits
        self.totalProdAL = float() # Total Produced Alloys
        self.totalProdEC = float()
        self.totalProdIA = float()
        self.alive = int(1) # Check on Empire still in the game
        self.roundComplete = int() # Empire Turn Complete
        self.loggedIn = int() # Player Logged in or not
        self.dateEnded = str() # Date and Time that Player ended Turn
        self.cities = int() # Total Cities under the control of Empire
        self.simulationsLeft = int() # Total Simulations Left this Turn
        self.designsLeft = int() # Total Designs Left this Turn
        self.rpAvail = int() # Total Research Points available this Turn
        self.rpUsed = int() # Total Research Points used this Turn
        self.ip = str() # current ip address of player
        self.key = str() # authentication key of player
        self.imageFile = str() # image file of empire
        self.help = list() # list of help areas eg: ['Map','Tech','Diplomacy','Design','EndTurn']
        self.defaultAttributes = ('id', 'name', 'password', 'emailAddress',
                                  'viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes',
                                  'color1', 'color2', 'ai', 'CR', 'AL', 'EC', 'IA',
                                  'totalProdCR','totalProdAL','totalProdEC','totalProdIA',
                                  'alive', 'roundComplete', 'loggedIn', 'dateEnded', 'cities', 'simulationsLeft', 
                                  'designsLeft', 'rpAvail', 'rpUsed', 'ip', 'key', 'imageFile', 'help')
        self.setAttributes(args)
        
        self.myGalaxy = None # Actual Galaxy Object that contains this Empire
        self.techTree = {} # technology Tree of Empire, key=tech id, value=tech obj
        self.techOrders = {} # technology orders for Empire
        self.industryOrders = {} # industry orders for Empire
        self.mailBox = {} # contains all mail ever sent to Empire
        self.diplomacy = {} # key=other empire gid, value=diplomacy object
        self.shipDesigns = {} # all starship designs created key=id, value=obj
        self.droneDesigns = {} # all drone designs created key=id, value=obj
        self.myShipBattles = [] # list of ship battles keys of viewable ship battles
    
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
            
            resultList.append('CONFIG')
            resultList.append('======================================')
            # check password
            if self.password == '':
                resultList.append('CRITICAL: You have not set a password')
                critical += 1
                self.addHelp('Config')
            # check email
            if self.emailAddress == '':
                resultList.append('CRITICAL: You have not set an email address')
                critical += 1
                self.addHelp('Config')
            
            # check tech
            resultList.append('')
            resultList.append('RESEARCH')
            resultList.append('======================================')
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
            resultList.append('======================================')
            # check if any systems are conducting trade routes that will fail due to lack of resources
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if mySystem.myEmpireID == self.id:
                    # check for systems that have built factories that cannot add value
                    factoryCR = 0
                    factoryAL = 0
                    factoryEC = 0
                    factoryIA = 0
                    for industryKey, myIndustry in mySystem.myIndustry.iteritems():
                        if self.myGalaxy.industrydata[myIndustry.industrytype].abr[1:] == 'CC':
                            factoryCR = 1
                        elif self.myGalaxy.industrydata[myIndustry.industrytype].abr[1:] == 'AF':
                            factoryAL = 1
                        elif self.myGalaxy.industrydata[myIndustry.industrytype].abr[1:] == 'CM':
                            factoryEC = 1
                        elif self.myGalaxy.industrydata[myIndustry.industrytype].abr[1:] == 'SS':
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
            resultList.append('======================================')
            # get list of regiment ID's currently given restoration orders:
            regimentsToRestore = []
            for orderID, myOrder in self.industryOrders.iteritems():
                if myOrder.round == self.myGalaxy.currentRound and myOrder.type == 'Restore Regiment':
                    regimentsToRestore.append(myOrder.value)
            # check if any regiments currently still in a transport
            for regimentID, myRegiment in self.myGalaxy.regiments.iteritems():
                if myRegiment.empireID == self.id:
                    if (myRegiment.state in [2,3] and 
                        self.myGalaxy.systems[myRegiment.toSystem].myEmpireID <> self.id
                        and myRegiment.strength == 100):
                        resultList.append('WARNING: Regiment:%s might want to invade:%s' % (myRegiment.name, self.myGalaxy.systems[myRegiment.fromSystem].name))
                        warnings += 1
                        self.addHelp('Map')
                    elif (myRegiment.state == 1 and 
                          self.myGalaxy.systems[myRegiment.fromSystem].availMIC > 0
                          and myRegiment.strength < 100 and myRegiment.id not in regimentsToRestore):
                        resultList.append('WARNING: Regiment:%s ON:%s is damaged and should be restored' % (myRegiment.name, self.myGalaxy.systems[myRegiment.fromSystem].name))
                        warnings += 1
                        
            resultList.append('')
            resultList.append('DIPLOMACY')
            resultList.append('======================================')
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
                    elif myOrder.type == 'Change City':
                        (cityID, resource) = string.split(myOrder.value, '-')
                        result = mySystem.updateCityResource(cityID, resource)
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
                # check if tech has been researched
                desc = 'TECH:%s - Roll Needed:%d, Roll Actual:%d' % (myTech.name, ratio, researchRolls[i])
                if researchRolls[i] <= (ratio):
                    # tech has been researched
                    myTech.currentPoints = myTech.requiredPoints
                    myTech.complete = 1
                    desc = desc + '->SUCCESS!'
                else:
                    # tech has not been researched
                    desc = desc + '->FAILED...'
                
                # update tech
                myTech.getImageFileName()
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
            elif myOrder.type == 'Change City':
                # return resources
                result = mySystem.refundUpdateCity()
            elif myOrder.type == 'Add Industry':
                # return resources and available cities
                (amount, indType) = string.split(myOrder.value, '-')
                amount = int(amount)
                result = mySystem.refundAddIndustry(amount, indType)
            elif myOrder.type == 'Upgrade Industry':
                # return resources
                result = mySystem.refundUpgradeIndustry(myOrder.value)
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
            # refund order
            result = self.refundTechOrder(techOrderID)
            
            # cancel order
            del self.techOrders[techOrderID]
            
            return result
        except:
            return 'empire->cancelTechOrder error'

    def checkDiplomacy(self):
        """Check the diplomacy for this empire in relation to other empires"""
        try:
            resultList = []
            # check if empire already in alliance
            alliance = 0
            for id, someDiplomacy in self.diplomacy.iteritems():
                if anwp.func.globals.diplomacy[someDiplomacy.diplomacyID]['alliance'] == 1:
                    alliance = 1
                    break
            for empireID, myDiplomacy in self.diplomacy.iteritems():
                if empireID <> '1':
                    otherAlliance = 0
                    # check if other empire in alliance
                    otherEmpire = self.myGalaxy.empires[empireID]
                    for id, otherDiplomacy in otherEmpire.diplomacy.iteritems():
                        if anwp.func.globals.diplomacy[otherDiplomacy.diplomacyID]['alliance'] == 1 and id <> self.id:
                            otherAlliance = 1
                            break
                            
                    if (myDiplomacy.myIntent == 'increase' and myDiplomacy.empireIntent == 'increase' 
                        and ((alliance == 0 and otherAlliance == 0) or (myDiplomacy.diplomacyID < 5))
                        ):
                        # increase diplomacy
                        newLevel = self.getIncreasedDiplomacy(myDiplomacy.diplomacyID)
                        self.setDiplomacy(empireID, newLevel)
                        resultList.append('You have increased Relations with %s to %s' % (self.myGalaxy.empires[empireID].name, anwp.func.globals.diplomacy[newLevel]['name']))
                    elif myDiplomacy.myIntent == 'decrease':
                        newLevel = self.getDecreasedDiplomacy(myDiplomacy.diplomacyID)
                        # check if war has been declared
                        if newLevel <> myDiplomacy.diplomacyID and newLevel == 1:
                            message = '%s has declared WAR on %s' % (self.name,self.myGalaxy.empires[empireID].name)
                            for id, myEmpire in self.myGalaxy.empires.iteritems():
                                if myEmpire.ai == 0:
                                    myEmpire.genMail({'fromEmpire':myEmpire.id, 'round':self.myGalaxy.currentRound+1,
                                                      'messageType':'general', 'subject':message,
                                                      'body':str([message])})
                        # decrease diplomacy
                        self.setDiplomacy(empireID, newLevel)
                        resultList.append('You have decreased Relations with %s to %s' % (self.myGalaxy.empires[empireID].name, anwp.func.globals.diplomacy[newLevel]['name']))
                        # if other empire does not have decrease in their plans, decrease for them
                        if otherEmpire.diplomacy[self.id].myIntent <> 'decrease':
                            otherEmpire.setDiplomacy(self.id, newLevel)
                    else:
                        newLevel = myDiplomacy.diplomacyID
                        resultList.append('You have no change in Relations with %s from %s' % (self.myGalaxy.empires[empireID].name, anwp.func.globals.diplomacy[newLevel]['name']))
            
            # mail out results to Empire
            results = str(resultList)
            if len(resultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                              'messageType':'general', 'subject':'Diplomatic Results, Round:%d' % self.myGalaxy.currentRound,
                              'body':results})
            return results
        except:
            return 'empire->checkDiplomacy error'

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
        if anwp.func.globals.diplomacy[diplomacyID]['alliance'] == 1:
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
            id = self.getNextID(self.mailBox)
            d = {'id':id}
            for key, value in mailDict.iteritems():
                d[key] = value
            
            myMail = mail.Mail(d)
            self.mailBox[id] = myMail
            return 1
        except:
            return 'empire->genMail error'

    def genShipDesign(self, name, hullID, compDict, weaponDict, bypass=0):
        """Attempt to build a StarShip Design, return name and ID"""
        try:
            id = self.getNextID(self.shipDesigns)
            # check if design is valid
            result = self.validateShipDesign(hullID, compDict, weaponDict, bypass)
            if result == 1:
                # create ship design
                designName = '%s%s-%s' % (self.myGalaxy.shiphulldata[hullID].abr, id, name)
                myShipDesign = anwp.war.shipdesign.ShipDesign({'id':id, 'name':designName, 'shipHullID':hullID})
                myShipDesign.setMyEmpire(self)
                myShipDesign.setMyDesign(hullID, compDict, weaponDict)
                if bypass == 0:
                    self.designsLeft -= 1
                result = (myShipDesign.id, myShipDesign.name)
            return result
        except:
            return 'empire->genShipDesign error'
    
    def genDroneDesign(self, name, hullID, compDict, weaponDict, bypass=0):
        """Attempt to build a Drone Design, return name and ID"""
        try:
            id = self.getNextID(self.droneDesigns)
            # check if design is valid
            result = self.validateDroneDesign(hullID, compDict, weaponDict, bypass)
            if result == 1:
                # create drone design
                designName = '%s%s-%s' % (self.myGalaxy.dronehulldata[hullID].abr, id, name)
                myDesign = anwp.war.dronedesign.DroneDesign({'id':id, 'name':designName, 'shipHullID':hullID})
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
                    # valid order, process
                    myTechOrder = order.Order(d)
                    self.techOrders[id] = myTechOrder
            return result
        except:
            return 'empire->genTechOrder error'
    
    def getImageFileName(self, symbolNum):
        """Generate the image filename depends on:
        - Empire Color1, Color2, symbolNum"""
        
        # create image file
        self.imageFile = 'emp_%s_%s_%s' % (symbolNum, self.color1, self.color2)
    
    def getMailUpdate(self, listMailID):
        """Return a dictionary Update Mail based on what id's are new"""
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
        list = ['id', 'name', 'emailAddress', 'color1', 'color2', 
                'viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes',
                'CR', 'AL', 'EC', 'IA', 'cities', 'simulationsLeft',
                'designsLeft', 'rpAvail', 'rpUsed', 'ip', 'key', 'imageFile']
        d = self.getSelectedAttr(list)
        d['techOrders'] = self.getMyOrdersByRound('techOrders')
        d['industryOrders'] = self.getMyOrdersByRound('industryOrders')
        d['researchedIndustry'] = self.getMyResearchedIndustry()
        d['researchedRegiments'] = self.getMyResearchedRegiments()
        d['mailBox'] = self.getMyDictInfo('mailBox')
        d['help'] = self.help
        d['diplomacy'] = self.getMyDictInfo('diplomacy')
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
        list = anwp.func.funcs.sortStringList(list)
        return list
    
    def getMyResearchedIndustry(self):
        """Return list of industry id's usable by empire"""
        list = []
        for id, myIndustryData in self.myGalaxy.industrydata.iteritems():
            # check if industry is researched
            myTech = self.techTree[myIndustryData.techReq]
            if myTech.complete == 1:
                list.append(id)
        list = anwp.func.funcs.sortStringList(list)
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
        list = ['id', 'name', 'color1', 'color2', 'imageFile']
        d = self.getSelectedAttr(list)
        return d
    
    def getShipBattleDict(self):
        """Return a dictionary of ship battles viewable to Empire"""
        try:
            d = {}
            for shipBattleKey in self.myShipBattles:
                desc = self.myGalaxy.shipBattles[shipBattleKey]
                (round, systemName) = string.split(desc, '-')
                d[shipBattleKey] = 'Round %s: %s' % (round, systemName)
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
            if type == 'Add City':
                return mySystem.payForAddCity()
            elif type == 'Change City':
                return mySystem.payForUpdateCity()
            elif type == 'Add Industry':
                (amount, indType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.payForAddIndustry(amount, indType)
            elif type == 'Remove Industry':
                return 1 # no cost
            elif type == 'Upgrade Industry':
                return mySystem.payForUpgradeIndustry(value)
            elif type == 'Add Ship':
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
            # clear data
            self.rpAvail = 0
            self.rpUsed = 0
            self.simulationsLeft = 0
            self.designsLeft = 0
                
            # generate result lists
            IncomeResultList = []
            totalCR = 0.0
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
                    IncomeResultList.append(mySystem.genWealth())
                    totalCR += mySystem.prodCR
                    totalAL += mySystem.prodAL
                    totalEC += mySystem.prodEC
                    totalIA += mySystem.prodIA
                    
                    # calculate research points generated
                    (amount, message) = mySystem.returnIndustryOutput('RC','Research Points')
                    if amount <> 0:
                        self.rpAvail += amount
                        ResearchResultList.append(message)
                    
                    # calculate simulations allowed
                    (amount, message) = mySystem.returnIndustryOutput('SC','Simulations')
                    if amount <> 0:
                        self.simulationsLeft += amount
                    
                    # calculate designs allowed
                    (amount, message) = mySystem.returnIndustryOutput('DC','Designs')
                    if amount <> 0:
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
                    mySystem.setFleetCadets(amount)
                    
                    # calculate army cadet classes
                    (amount, message) = mySystem.returnIndustryOutput('MA','Marine Cadet Classes')
                    mySystem.setArmyCadets(amount)
            
            # add totals
            IncomeResultList.append('========================================')
            IncomeResultList.append('Total Resources Generated:')
            IncomeResultList.append('(CR) = %d Credits' % totalCR)
            IncomeResultList.append('(AL) = %d Alloys' % totalAL)
            IncomeResultList.append('(EC) = %d Energy Crystals' % totalEC)
            IncomeResultList.append('(IA) = %d Intel Arrays' % totalIA)
            
            ResearchResultList.append('========================================')
            ResearchResultList.append('Total Research Points Generated: %d' % self.rpAvail)
            
            # mail results to Empire
            researchResults = str(ResearchResultList)
            incomeResults = str(IncomeResultList)
            results = '%s\n\n%s' % (researchResults, incomeResults)
            if len(ResearchResultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                  'messageType':'research', 'subject':'Research Points Generated, Round:%d' % self.myGalaxy.currentRound,
                                  'body':researchResults})
            if len(IncomeResultList) > 0:
                self.genMail({'fromEmpire':self.id, 'round':self.myGalaxy.currentRound+1,
                                  'messageType':'economics', 'subject':'Economic Report, Round:%d' % self.myGalaxy.currentRound,
                                  'body':incomeResults})
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
        
    def resetData(self):
        """Reset Data for Empire"""
        self.ip = ''
        self.loggedIn = 0
        self.key = ''
        
    def resetRoundData(self):
        """Reset Round Data"""
        self.roundComplete = 0
        self.dateEnded = ''
        if self.myGalaxy.currentRound > 5:
            self.techOrders = {}
            self.industryOrders = {}
    
    def sendCredits(self, empireID, amount):
        """Send Amount of Credits to Empire"""
        try:
            toEmpire = self.myGalaxy.empires[empireID]
            if self.CR < amount:
                return 'not enough credits to send to empire'
            self.CR -= amount
            toEmpire.CR += amount
            dMail = {'fromEmpire':self.id, 'round':self.myGalaxy.currentRound,
                                  'messageType':'economics', 'subject':'Credit Transfer, Round:%d' % self.myGalaxy.currentRound,
                                  'body':str(['%d Credits Transfered from %s to %s' % (amount, self.name, toEmpire.name)])}
            self.genMail(dMail)
            toEmpire.genMail(dMail)
            return 1
        except:
            return 'empire->sendCredits error'
    
    def setDiplomacy(self, empireID, diplomacyID):
        """Set the diplomacy for empire given in relation to this empire"""
        d = {'empireID':empireID, 'diplomacyID':diplomacyID, 'myIntent':'none', 'empireIntent':'none'}
        myDiplomacy = anwp.aw.diplomacy.Diplomacy(d)
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
            type = indOrderDict['type']
            value = indOrderDict['value']
            # go through each order type
            if type == 'Add City':
                return mySystem.validateAddCity()
            elif type == 'Change City':
                return mySystem.validateUpdateCity(value)
            elif type == 'Add Industry':
                (amount, indType) = string.split(value, '-')
                amount = int(amount)
                return mySystem.validateAddIndustry(amount, indType)
            elif type == 'Remove Industry':
                return 1
            elif type == 'Upgrade Industry':
                return mySystem.validateUpgradeIndustry(value)
            elif type == 'Add Ship':
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
            # check hull type
            if self.techTree[myShipHull.techReq].complete == 0 and bypass == 0:
                return 'You do not have the technology to use this Hull:%s' % self.myGalaxy.shiphulldata[hullID].name
            # check weapons
            for key, valueDict in weaponDict.iteritems():
                myWeaponData = self.myGalaxy.weapondata[valueDict['type']]
                if self.techTree[myWeaponData.techReq].complete == 0 and bypass == 0:
                    return 'You do not have the technology to use this weapon:%s' % self.myGalaxy.weapondata[valueDict['type']].name
                elif myWeaponData.abr in anwp.func.globals.weaponLimitations[myShipHull.function]:
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
                    if componentID[0] <> 'W':
                        # check technology
                        myComponentData = self.myGalaxy.componentdata[componentID]
                        if self.techTree[myComponentData.techReq].complete == 0 and bypass == 0:
                            return 'You do not have the technology to use this component:%s' % self.myGalaxy.componentdata[componentID].name
                        elif myComponentData.abr in anwp.func.globals.componentLimitations[myShipHull.function]:
                            return '%s cannot be added to %s' % (myComponentData.name, myShipHull.name)

                        # add to counts
                        abr = self.myGalaxy.componentdata[componentID].abr
                        if abr == 'SSE' or abr == 'PSE' or abr == 'USE':
                            engineCount += 1
                        elif abr == 'SRT' or abr == 'PRT' or abr == 'URT':
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
            # check hull type
            if self.techTree[myDroneHull.techReq].complete == 0 and bypass == 0:
                return 'You do not have the technology to use this Hull:%s' % self.myGalaxy.dronehulldata[hullID].name
            # check weapons
            for key, valueDict in weaponDict.iteritems():
                myWeaponData = self.myGalaxy.weapondata[valueDict['type']]
                if self.techTree[myWeaponData.techReq].complete == 0 and bypass == 0:
                    return 'You do not have the technology to use this weapon:%s' % self.myGalaxy.weapondata[valueDict['type']].name
                elif myWeaponData.abr in anwp.func.globals.weaponLimitations[myDroneHull.function]:
                    return '%s cannot be added to %s' % (myWeaponData.name, myDroneHull.name)
            # check components
            genCount = 0
            engineCount = 0
            rotCount = 0
            for key, valueList in compDict.iteritems():
                # check that only valid number of components submitted
                if len(valueList) > myDroneHull.componentNum:
                    return 'You are attempting to add more components then the max allowed'
                for componentID in valueList:
                    if componentID[0] <> 'W':
                        # check technology
                        myComponentData = self.myGalaxy.componentdata[componentID]
                        if self.techTree[myComponentData.techReq].complete == 0 and bypass == 0:
                            return 'You do not have the technology to use this component:%s' % self.myGalaxy.componentdata[componentID].name
                        elif myComponentData.abr in anwp.func.globals.componentLimitations[myDroneHull.function]:
                            return '%s cannot be added to %s' % (myComponentData.name, myDroneHull.name)

                        # add to counts
                        abr = self.myGalaxy.componentdata[componentID].abr
                        if abr == 'SSE' or abr == 'PSE' or abr == 'USE':
                            engineCount += 1
                        elif abr == 'SRT' or abr == 'PRT' or abr == 'URT':
                            rotCount += 1
                        elif abr == 'SPP' or abr == 'PPP' or abr == 'UPP':
                            genCount += 1
                        
            # make sure design has at least one of each (engine, rotation, power)
            if engineCount == 0:
                return 'Your Drone Design does not have any Engine components'
            if genCount == 0:
                return 'Your Drone Design does not have any Power Plant components'
            if rotCount == 0:
                return 'Your Drone Design does not have any Rotational Thruster components'
            
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
            # is there an existing order in place for this tech?
            if self.techOrders.has_key(techGid):
                return 'You have already made a research order for this Technology'
            # is there enough research points available?
            if value > self.rpAvail:
                return 'You do not have enough research points left: Req=%d, Avail=%d' % (value, self.rpAvail)
            # have they allocated too many points to this tech?
            if value > (myTech.requiredPoints - myTech.currentPoints):
                return 'You are placing too much research on this technology'
            return 1
        except:
            return 'empire->validateTechOrder error'    

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_empire.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()