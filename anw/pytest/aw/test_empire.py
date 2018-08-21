# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_empire.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an Empire in ANW
# ---------------------------------------------------------------------------
import os
from anw.admin import generate
from anw.aw import galaxy
from anw.func import globals

class TestEmpire(object):
    
    def setup_class(self):
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.myGalaxy = None
        self.myEmpire = None
        self.generate = None
        self.mySystem = None
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
        self.myGalaxy = self.generate.getGalaxy()
        self.myEmpire = self.myGalaxy.empires['0']
    
    def testGenGalaxy(self):
        """Can entire Galaxy Object be generated"""
        assert self.myGalaxy.xMax == 14 * globals.systemSize
        assert self.myGalaxy.yMax == 8 * globals.systemSize
    
    def testGetMyInfoAsDict(self):
        """Get Empire Information as Dictionary"""
        d = self.myEmpire.getMyInfoAsDict()
        for attr, value in d.iteritems():
            assert getattr(self.myEmpire, attr) == value
    
    def testMailEconomicReport(self):
        """Mail the Empire an income Report"""
        myEmpire = self.myGalaxy.empires['1']
        myEmpire.mailEconomicReport()
        myMailReport = myEmpire.mailBox['6'].body
        assert 'CREDIT INCOME REPORT FOR ROUND: 1' in myMailReport
    
    def testAskForHelp(self):
        """Returns Help in a list of strings, also returns list of areas of interest to player
        input->mail=1"""
        self.myEmpire.mailBox = {}
        result = self.myEmpire.askForHelp()
        assert result == ('Server Assessment: WARNINGS:0, CRITICAL:0 (Check Mail for Assesment)', ['EndTurn'])
        ##myNewMail = self.myEmpire.mailBox['1']
        ##mailBody = eval(myNewMail.body)
        ##assert mailBody == ['CONFIG',
                            ##'===================================================',
                            ##'CRITICAL: You have not set an email address',
                            ##'',
                            ##'RESEARCH',
                            ##'===================================================',
                            ##'',
                            ##'ECONOMY',
                            ##'===================================================',
                            ##'',
                            ##'MILITARY',
                            ##'===================================================',
                            ##'',
                            ##'DIPLOMACY',
                            ##'===================================================']
    
    def testGetMyResearchedRegiments(self):
        """Return list of regiment id's usable by empire"""
        result = self.myEmpire.getMyResearchedRegiments()
        assert result == ['1']
    
    def testGetMyResearchedIndustry(self):
        """Return list of industry id's usable by empire"""
        result = self.myEmpire.getMyResearchedIndustry()
        assert result == ['1', '4', '7', '10', '13', '22', '28', '31', '34', '37', '40']
    
    def testGenTechOrder(self):
        """Generate tech order for empire
        input->dict={round, techID, amount}"""
        assert self.myEmpire.rpAvail == 0
        assert self.myEmpire.rpUsed == 0
        assert self.myEmpire.techOrders == {}
        self.myEmpire.techTree['10'].complete = 0
        self.myEmpire.techTree['10'].currentPoints = 0
        d = {'type': '10', 'round': 1, 'value': 45}
        result = self.myEmpire.genTechOrder(d)
        assert result == 'You do not have enough research points left: Req=45, Avail=0'
        self.myEmpire.rpAvail = 50
        result = self.myEmpire.genTechOrder(d)
        assert result == 1
        assert self.myEmpire.rpAvail == 5
        assert self.myEmpire.rpUsed == 45    
    
    def testReduceTechOrder(self):
        """Reduce and Cancel a Tech order, get back research points
        input->techOrderID"""
        assert self.myEmpire.rpAvail == 5
        assert self.myEmpire.rpUsed == 45
        d = {'type': '10', 'round': 1, 'value': -15}
        result = self.myEmpire.genTechOrder(d)
        assert result == 1
        d = self.myEmpire.getMyOrdersByRound('techOrders')
        assert d == {'10-1': {'id': '10-1', 'round': 1, 'type': '10', 'value': '30'}}
        assert self.myEmpire.rpAvail == 20
        assert self.myEmpire.rpUsed == 30
        
        d = {'type': '10', 'round': 1, 'value': -30}
        result = self.myEmpire.genTechOrder(d)
        assert result == 1
        assert self.myEmpire.techOrders == {}
        assert self.myEmpire.rpAvail == 50
        assert self.myEmpire.rpUsed == 0
    
    def testCalcResearch(self):
        """Calculate research orders for Empire in current round
        input->researchRolls"""
        d = {'type': '10', 'round': 1, 'value': 45}
        result = self.myEmpire.genTechOrder(d)
        researchRolls = [88,75]
        assert self.myEmpire.techTree['10'].complete == 0
        self.myEmpire.mailBox == {}
        result = self.myEmpire.calcResearch(researchRolls)
        assert result == "['TECH:Marine Academy - Roll Needed:55, Roll Actual:88->SUCCESS!']"
        assert self.myEmpire.techTree['10'].complete == 1
    
    def testSetInitialDiplomacy(self):
        """Confirm Setting the Empire Starting Diplomacy"""
        self.myEmpire.diplomacy = {}
        self.myEmpire.setInitialDiplomacy()
        d = {}
        for id, myDiplomacy in self.myEmpire.diplomacy.iteritems():
            d[id] = myDiplomacy.getMyInfoAsDict()
        assert d == {'0': {'diplomacyID': 2,
                           'empireID': '0',
                           'empireIntent': 'none',
                           'myIntent': 'none'},
                     '1': {'diplomacyID': 2,
                           'empireID': '1',
                           'empireIntent': 'none',
                           'myIntent': 'none'},
                     '2': {'diplomacyID': 2,
                           'empireID': '2',
                           'empireIntent': 'none',
                           'myIntent': 'none'},
                     '3': {'diplomacyID': 2,
                           'empireID': '3',
                           'empireIntent': 'none',
                           'myIntent': 'none'},
                     '4': {'diplomacyID': 2,
                           'empireID': '4',
                           'empireIntent': 'none',
                           'myIntent': 'none'}}
    
    def testIncreaseDiplomacy(self):
        """Increase Diplomacy between empires
        input->empireID"""
        result = self.myEmpire.increaseDiplomacy('2')
        assert result == 1
        assert self.myEmpire.diplomacy['2'].myIntent == 'increase'
    
    def testDecreaseDiplomacy(self):
        """Decrease Diplomacy between empires
        input->empireID"""
        result = self.myEmpire.decreaseDiplomacy('3')
        assert result == 1
        assert self.myEmpire.diplomacy['3'].myIntent == 'decrease'
    
    def testResolveDiplomacy(self):
        """Resolve Diplomacy for Empire with other Empires for round"""
        result = eval(self.myEmpire.resolveDiplomacy())
        assert result == ['You have no change in Relations with Yellow Empire from No Relations',
                          'You have decreased Relations with Green Empire to At War',
                          'You have no change in Relations with Brown Empire from No Relations',
                          'You have no change in Relations with Blue Empire from No Relations']
        self.myGalaxy.empires['2'].increaseDiplomacy('0')
        result = eval(self.myEmpire.resolveDiplomacy())
        assert result == ['You have no change in Relations with Yellow Empire from No Relations',
                          'You have no change in Relations with Green Empire from At War',
                          'You have increased Relations with Brown Empire to Non Agression Pact',
                          'You have no change in Relations with Blue Empire from No Relations']
    
    def testGetMyShipDesigns(self):
        """Return Ship Designs"""
        d = self.myEmpire.getMyShipDesigns()
        assert d['1'] == ('HCO1-Neutral-HCO',
                          '4',
                          {'aft': ['25', '4', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1'],
                            'fore': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7'],
                            'port': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7'],
                            'star': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7']},
                           {'aft-1': {'facing': 0.0, 'id': '1', 'type': '24'}})
    
    def testGetMyDroneDesigns(self):
        """Return Drone Designs"""
        d = self.myEmpire.getMyDroneDesigns()
        assert d['1'] == ('LND1-Neutral-LND',
                          '101',
                          {'fore': ['25', '25', '7', '7', 'W1', 'W1', 'W1', 'W1']},
                          {'fore-1': {'facing': 0.0, 'id': '1', 'type': '1'}})
    
    def testGenShipDesign(self):
        """Generate a Ship Design
        input->name, hullID, compDict, weaponDict, bypass=0)"""
        compDict = {'fore':['31','31','31','31'],
                    'port':['31','1','7','34'],
                    'star':['31','1','4','34'],
                    'aft':['W1','W1','W1','W1']}
        weapDict = {'aft-1':{'id':'1', 'type':'13', 'facing':0}}
        result = self.myEmpire.genShipDesign('Photon', '1', compDict, weapDict)
        assert result == 'You do not have enough Design Centers to build another Ship Design this Round'
        self.myEmpire.designsLeft = 1
        result = self.myEmpire.genShipDesign('Photon', '1', compDict, weapDict)
        assert result == ('16', 'SCT16-Photon')
        d = self.myEmpire.getMyShipDesigns()
        assert d['16'] == ('SCT16-Photon',
                          '1',
                          {'aft': ['W1', 'W1', 'W1', 'W1'],
                           'fore': ['31', '31', '31', '31'],
                           'port': ['1', '31', '34', '7'],
                           'star': ['1', '31', '34', '4']},
                          {'aft-1':{'facing':0.0, 'id': '1', 'type': '13'}})
    
    def testRemoveShipDesign(self):
        """Remove ship design by setting it obsolete
        input->shipDesignID"""
        result = self.myEmpire.removeShipDesign('9')
        assert result == 1
        assert self.myEmpire.shipDesigns['9'].obsolete == 1
    
    def testGenDroneDesign(self):
        """Generate a Drone Design
        input->name, hullID, compDict, weaponDict, bypass=0)"""
        compDict = {'fore':['9','9','9','9','W1','W1','W1','W1']}
        weapDict = {'fore-1':{'id':'1', 'type':'1', 'facing':0}}
        result = self.myEmpire.genDroneDesign('Photon', '101', compDict, weapDict)
        assert result == 'You do not have enough Design Centers to build another Drone Design this Round'
        self.myEmpire.designsLeft = 1
        result = self.myEmpire.genDroneDesign('Photon', '101', compDict, weapDict)
        assert result == ('4', 'LND4-Photon')
        d = self.myEmpire.getMyDroneDesigns()
        assert d['4'] == ('LND4-Photon',
                          '101',
                          {'fore': ['9', '9', '9', '9', 'W1', 'W1', 'W1', 'W1']},
                          {'fore-1': {'facing': 0.0, 'id': '1', 'type': '1'}})
    
    def testRemoveDroneDesign(self):
        result = self.myEmpire.removeDroneDesign('4')
        assert result == 1
        assert self.myEmpire.droneDesigns['4'].obsolete == 1
        
    def testGetMailUpdate(self):
        """Return a dict of mail based on mail not in ids given
        input->mailIDList"""
        mailIDs = self.myEmpire.mailBox.keys()
        assert mailIDs == ['1', '3', '2', '5', '4']
        result = self.myEmpire.getMailUpdate(['1','2','3'])
        assert result['5']['subject'] == 'Diplomatic Results, Round:1'
        assert result['5']['messageType'] == 'general'
                                
    def testGetMyEmpireInfo(self):
        """Return empire information from server to client as dict"""
        d = self.myEmpire.getMyEmpireInfo()
        for attr in ['id', 'name', 'player', 'emailAddress', 'color1', 'color2', 
                     'viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes',
                     'CR', 'AL', 'EC', 'IA', 'cities', 'simulationsLeft',
                     'designsLeft', 'rpAvail', 'rpUsed', 'ip', 'key', 'imageFile']:
            assert getattr(self.myEmpire, attr) == d[attr]

    def testSendCredits(self):
        """Send Credits from empire to another empire
        input->empireID, amount"""
        assert self.myEmpire.id == '0'
        self.myEmpire.mailBox = {}
        self.myEmpire.CR = 0
        self.myGalaxy.empires['1'].CR = 0
        result = self.myEmpire.sendCreditsInLieu('1', 2000)
        assert result == 'not enough credits'
        self.myEmpire.CR = 4000.0
        assert self.myGalaxy.empires['1'].CR == 0.0
        assert self.myEmpire.creditsInLieu == {}
        assert self.myEmpire.sendCreditsInLieu('1', 2000) == 1
        assert self.myEmpire.CR == 2000.0
        assert self.myEmpire.creditsInLieu == {'1':2000}
            
    def testSetTotalCities(self):
        """Set the total cities under Empire Control"""
        # 40 + 15 + 15 + 20 + 10 + 10 = 110 cities to start
        myEmpire = self.myGalaxy.empires['1']
        assert myEmpire.cities == 110
        myEmpire.cities = 0
        myEmpire.setTotalCities()
        assert myEmpire.cities == 110
    
    def testGetAllSystemResources(self):
        """Return total Resources currently on all systems owned by Empire"""
        myEmpire = self.myGalaxy.empires['1']
        result = myEmpire.getAllSystemResources()
        assert result == [6800.0, 1200.0, 600.0]
    
    def testGetAllShipResources(self):
        """Return total Resources by summing all ships value in resources
        account for ship being damaged"""
        myEmpire = self.myGalaxy.empires['1']
        result = myEmpire.getAllShipResources()
        assert result == [0, 0, 0]
        
    def testProcessSystems(self):
        """Go through each system that is owned by this Empire and process them: """
        result = self.myEmpire.processSystems()
        assert self.myEmpire.id == '0'
        assert result == None
        
        result = self.myGalaxy.empires['1'].processSystems()
        assert result == "['System:Racor Has Produced->300 Research Points', '===================================================', 'Total Research Points Generated: 300']\n\n['System:Idanebandr Has Produced->(AL=400, EC=0, IA=0) Resources', 'System:Librass Has Produced->(AL=200, EC=0, IA=0) Resources', 'System:Acor Has Produced->(AL=200, EC=0, IA=0) Resources', 'System:Sioth Has Produced->(AL=300, EC=0, IA=0) Resources', 'System:Eraze Has Produced->(AL=300, EC=0, IA=0) Resources', 'System:Racor Has Produced->(AL=800, EC=0, IA=0) Resources', '===================================================', 'Total Resources Generated:', '(AL) = 2200 Alloys', '(EC) = 0 Energy Crystals', '(IA) = 0 Intel Arrays']"
    
    def testGenIndustryOrder(self):
        """Generate an industry order"""
        d = self.myEmpire.getMyOrdersByRound('industryOrders')
        assert d == {}
        dOrder = {'system':'19', 'type':'Repair Starship',
                  'value':'1', 'round': 1}
        result = self.myEmpire.genIndustryOrder(dOrder)
        assert result == 'ship already at 100% strength'
        myShip = self.myGalaxy.ships['1']
        myShip.strength = 75
        mySystem = self.myGalaxy.systems['19']
        mySystem.availSYC = 200
        myShip.myDesign.hasAllTech = 1
        assert myShip.myDesign.hasAllTech == 1
        result = self.myEmpire.genIndustryOrder(dOrder)
        assert result == 1
        
    def testGetMyOrdersByRound(self):
        """Return empire orders for current round as dict
        input->orderName"""
        d = self.myEmpire.getMyOrdersByRound('industryOrders')
        assert d == {'1': {'id': '1',
                           'round': 1,
                           'system': '19',
                           'type': 'Repair Starship',
                           'value': '1'}}

    def testCancelIndustryOrder(self):
        """Cancel an Industry Order for Empire
        input->orderID"""
        self.myEmpire.cancelIndustryOrder('1')
        assert self.myEmpire.industryOrders == {}
        