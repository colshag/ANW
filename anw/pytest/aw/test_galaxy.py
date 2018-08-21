# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_galaxy.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a working Galaxy of ANW.  A Galaxy is essentially one 
# running game of ANW.
# ---------------------------------------------------------------------------
import os
import types

from anw.admin import generate
from anw.aw import galaxy, system
from anw.func import globals, storedata, funcs

class TestGalaxy(object):
    
    def setup_class(self):
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.myGalaxy = None
        self.generate = None
        self.myShipBattle = None
        self.tempIDList = []
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
        self.myGalaxy = self.generate.getGalaxy()
    
    def testGenGalaxy(self):
        """Can entire Galaxy Object be generated"""
        assert self.myGalaxy.xMax == 14 * globals.systemSize
        assert self.myGalaxy.yMax == 8 * globals.systemSize
        for id, mySystem in self.myGalaxy.systems.iteritems():
            mySystem.name = '%s%s' % ('System-', id)
    
    def testSetTotalCities(self):
        """Set the Total Cities of Galaxy"""
        assert self.myGalaxy.cities == 1150
        self.myGalaxy.cities = 0
        self.myGalaxy.setTotalCities()
        assert self.myGalaxy.cities == 1150
    
    def testGetMyInfoAsDict(self):
        """Get Galaxy Information as Dictionary"""
        d = self.myGalaxy.getMyInfoAsDict()
        for attr, value in d.iteritems():
            assert getattr(self.myGalaxy, attr) == value
    
    def testGetAllEmpireInfo(self):
        """Get Empire Info as dict of dicts, fleshed out dict specified by empireID given"""
        d = self.myGalaxy.getAllEmpireInfo('1')
        neutralEmpireDict = d['0']
        myEmpireDict = d['1']
        assert neutralEmpireDict ==  {'ai':1, 'color1': 'white','color2': 'black',
                                      'id': '0','imageFile': '','name': 'Neutral', 
                                      'loggedIn': 0, 'roundComplete': 0, 'alive':1}
        print neutralEmpireDict
        result = {'0': {'diplomacyID': 2,
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
        print result
        assert myEmpireDict['diplomacy'] == result
    
    def testGetAllSystemInfo(self):
        """Get System Info, player systems more fleshed out"""
        myTempSystem = system.System({})
        d = self.myGalaxy.getAllSystemInfo('1')
        neutralSystemDict = d['18']
        mySystemDict = d['17']
        assert neutralSystemDict == {'cities': 10,
                                     'connectedSystems':['27', '28', '5', '4', '6', '17'],
                                     'id': '18',
                                     'imageFile': 'sys_4_white_black',
                                     'intelReport': {'industryReport': {},
                                                     'marineReport': {},
                                                     'round': 0,
                                                     'shipReport': {}},
                                     'myEmpireID': '0',
                                     'name': 'System-18',
                                     'x': 5 * globals.systemSize,
                                     'y': 2 * globals.systemSize}
        for attr in myTempSystem.defaultAttributes:
            assert attr in mySystemDict.keys()
    
    def testGetMyCaptialSystem(self):
        """Can we retrieve captial system for player based on number of cities"""
        myCaptialSystem = self.myGalaxy.getMyCaptialSystem('1')
        assert myCaptialSystem.name == 'System-16'
        assert myCaptialSystem.cities == 40
        
    def testGenTradeRoute(self):
        """Can Trade Route be generated"""
        myFromSystem = self.myGalaxy.systems['18']
        myFromSystem.AL = 0
        d = {'AL':0.0, 'EC':0.0, 'IA':0.0, 'fromSystem':'18', 'toSystem':'17',
                  'type':'GEN'}
        result = self.myGalaxy.genTradeRoute(d)
        assert result == 'System Owners are not the same, or no Trade Pact in Effect'
        d['toSystem'] = '5'
        result = self.myGalaxy.genTradeRoute(d)
        assert result == 1
        d['type'] = 'REG'
        result = self.myGalaxy.genTradeRoute(d)
        assert result == 'no resources are being sent, trade route invalid'
        d['AL'] = 100.0
        result = self.myGalaxy.genTradeRoute(d)
        assert result == 'System-18 does not have enough resources to setup this trade route'
        myFromSystem.AL = 100.0
        result = self.myGalaxy.genTradeRoute(d)
        assert result == 1
     
    def testGetMyTradeRouteInfo(self):
        """Return Trade Route info as Dict"""
        result = self.myGalaxy.getMyTradeRouteInfo('0')
        dict = {'18-5-GEN': {'AL': 0.0,
              'EC': 0.0,
              'IA': 0.0,
              'fromSystem': '18',
              'id': '18-5-GEN',
              'imageFile': 'traderoute_orange',
              'oneTime': 0,
              'toSystem': '5',
              'type':'GEN',
              'warpReq': 0},
              '18-5-REG': {'AL': 100.0,
              'EC': 0.0,
              'IA': 0.0,
              'fromSystem': '18',
              'id': '18-5-REG',
              'imageFile': 'traderoute_blue',
              'oneTime': 0,
              'toSystem': '5',
              'type':'REG',
              'warpReq': 0}}
        assert result == dict
    
    def testCancelTradeRoute(self):
        """Can Trade Route be removed"""
        result = self.myGalaxy.cancelTradeRoute('18-5-GEN',1)
        assert result == 1
        dict = {'18-5-REG': {'AL': 100.0,
              'EC': 0.0,
              'IA': 0.0,
              'fromSystem': '18',
              'id': '18-5-REG',
              'imageFile': 'traderoute_blue',
              'oneTime': 0,
              'toSystem': '5',
              'type':'REG',
              'warpReq': 0}}
        assert self.myGalaxy.getMyTradeRouteInfo('0') == dict
    
    def testGenMarketOrder(self):
        """Can we create a Market Order"""
        myEmpire = self.myGalaxy.empires['1']
        mySystem = self.myGalaxy.systems['2']
        mySystem.AL = 0
        assert mySystem.myEmpireID == myEmpire.id
        d = {'type':'sell', 'value':'AL', 'min':100.0, 'max':0.0, 'amount':50.0, 'system':'2'}
        result = self.myGalaxy.genMarketOrder(d)
        assert result == 'You do not have enough AL to place this SELL order on the market'
        d['min'] = 0.0
        result = self.myGalaxy.genMarketOrder(d)
        assert result == 'You must place an order with a min/max and amount > 0'
        d = {'type':'sell', 'value':'AL', 'min':100.0, 'max':0.0, 'amount':50.0, 'system':'2'}
        mySystem.AL = 50.0
        result = self.myGalaxy.genMarketOrder(d)
        assert result == {'amount': 50.0, 'id': '1', 'max': 0.0, 'min': 100.0, 'system':'2', 'value':'AL', 'round':1, 'type':'sell' }
        assert mySystem.AL == 0.0
        dict = {'1': {'min': 100.0, 'max': 0.0, 'system': '2', 'value': 'AL', 'round': 1, 'amount': 50.0, 'amountUsed': 0.0, 'type': 'sell', 'id': '1'}}
        assert self.myGalaxy.getMyMarketOrders(myEmpire.id) == dict
    
    def testCancelMarketOrder(self):
        """Can we cancel a market order created"""
        mySystem = self.myGalaxy.systems['2']
        self.myGalaxy.cancelMarketOrder('1')
        assert self.myGalaxy.getMyMarketOrders('2') == {}
    
    def testProcessMarketOrders(self):
        """Can we process Market Orders and properly assign resources"""
        i = 10
        systemNames = ['System-5','System-6','System-7','System-8']
        for systemID in ['5','6','7','8']:
            mySystem = self.myGalaxy.systems[systemID]
            mySystem.IA = 100
            d = {'type':'sell', 'value':'IA', 'min':i, 'max':0, 'amount':i, 'system':systemID}
            result = self.myGalaxy.genMarketOrder(d)
            assert type(result) == types.DictionaryType
            assert systemNames.pop(0) == mySystem.name
            i += 10
            
        i = 60
        systemNames = ['System-25','System-26','System-27','System-28']
        for systemID in ['25','26','27','28']:
            mySystem = self.myGalaxy.systems[systemID]
            self.myGalaxy.empires[mySystem.myEmpireID].CR = 10000
            d = {'type':'buy-any', 'value':'IA', 'max':i, 'min':0, 'amount':20, 'system':systemID}
            result = self.myGalaxy.genMarketOrder(d)
            assert type(result) == types.DictionaryType
            assert systemNames.pop(0) == mySystem.name
            i -= 10
            
        result = eval(self.myGalaxy.processMarketOrders(doGalacticMarket=0))
        assert result[0] == 'transaction completed: System-8 SOLD 20 IA to System-25 for 40 price'
        assert result[1] == 'transaction completed: System-8 SOLD 20 IA to System-26 for 40 price'
        assert result[2] == 'transaction completed: System-7 SOLD 20 IA to System-27 for 30 price'
        assert result[3] == 'transaction completed: System-7 SOLD 10 IA to System-28 for 30 price'
        assert len(result) == 11
                
    def testMarketStats(self):
        """Are the Market Stats Correct after processing Orders"""
        result = self.myGalaxy.marketStats[str(self.myGalaxy.currentRound)].getMyInfoAsDict()
        assert result['avgSoldAL'] == 10.0
        assert result['avgSoldEC'] == 20.0
        assert result['avgSoldIA'] == 34.00
        assert result['id'] == '1'
        assert result['sumSoldAL'] == 0.0
        assert result['sumSoldEC'] == 0.0
        assert result['sumSoldIA'] == 2700.0
        assert result['volSoldAL'] == 0.0
        assert result['volSoldEC'] == 0.0
        assert result['volSoldIA'] == 80.0
    
    def testSetCaptainNames(self):
        """Can we reset self.captainNames list of names"""
        assert len(self.myGalaxy.captainNames) == 573
        assert self.myGalaxy.captainNames[0] == 'Berker'
        assert self.myGalaxy.captainNames[572] == 'Rewsong'
        assert self.myGalaxy.currentCaptainName == 402
        assert self.myGalaxy.maxCaptainNames == 500
        self.myGalaxy.setCaptainNames()
        assert len(self.myGalaxy.captainNames) == 561
        assert self.myGalaxy.captainNames[0] == 'Frawforra'
        assert self.myGalaxy.captainNames[560] == 'Iguez'
        assert self.myGalaxy.currentCaptainName == 0
    
    def testSetCaptainName(self):
        """Change Captain Name to new name
        input->empireID, captainID, new name"""
        myCaptain = self.myGalaxy.captains['19']
        assert myCaptain.name == 'Rcia Ewson'
        self.myGalaxy.setCaptainName('0', '19', 'Darth Vader')
        assert myCaptain.name == 'Darth Vader'
    
    def testGetMyShips(self):
        """Return myShipsDict, myArmadasDict, otherArmadasDict for client
        input->empireID"""
        self.myGalaxy.empires['1'].shipDesigns['1'] = self.myGalaxy.empires['0'].shipDesigns['1']
        self.buildTempShip('1')
        (myShipsDict, myArmadasDict, otherArmadasDict, warpedArmadasDict) = self.myGalaxy.getMyShips('0')
        for id, myShip in self.myGalaxy.ships.iteritems():
            if myShip.empireID == '0':
                myShipDict = myShipsDict[id]
                for attr in myShip.defaultAttributes:
                    assert getattr(myShip, attr) == myShipDict[attr]
        
        for systemID, ShipIDList in myArmadasDict.iteritems():
            for shipID in ShipIDList:
                myShip = self.myGalaxy.ships[shipID]
                assert myShip.toSystem == systemID   
                
        assert otherArmadasDict == {'2': ['1']}
    
    def buildTempShip(self, empireID):
        """build another ship for empireID"""
        mySystem = self.myGalaxy.systems['2']
        myNewShip = mySystem.addShip(1,empireID,'1')
        myNewShip.toSystem = mySystem.id
        self.tempIDList.append(myNewShip.id)
    
    def testRemoveShip(self):
        """Remove Ship
        input->shipID"""
        assert self.tempIDList[0] in self.myGalaxy.ships.keys()
        myShip = self.myGalaxy.ships[self.tempIDList[0]]
        captainID = myShip.captainID
        assert captainID in self.myGalaxy.captains.keys()
        self.myGalaxy.removeShip(self.tempIDList[0])
        assert captainID not in self.myGalaxy.captains.keys()
        assert self.tempIDList.pop() not in self.myGalaxy.ships.keys()
    
    def testGetMyCaptains(self):
        """Return all Captain info as dict for captains in this empire employ
        input->empireID"""
        d = self.myGalaxy.getMyCaptains('1')
        for id, myCaptain in self.myGalaxy.captains.iteritems():
            if myCaptain.empireID == '1':
                myCaptainDict = d[id]
                for name, value in myCaptainDict.iteritems():
                    assert getattr(myCaptain, name) == value
    
    def testSwapCaptains(self):
        """Swap two captains between ships
        input->empireID, shipOneID, shipTwoID"""
        shipOne = self.myGalaxy.ships['1']
        shipTwo = self.myGalaxy.ships['2']
        captainOne = self.myGalaxy.captains['1']
        captainTwo = self.myGalaxy.captains['2']
        assert shipOne.captainID == '1'
        assert shipTwo.captainID == '2'
        assert captainOne.myShipID == '1'
        assert captainTwo.myShipID == '2'
        self.myGalaxy.swapCaptains('0', '1', '2')
        assert shipOne.captainID == '2'
        assert shipTwo.captainID == '1'
        assert captainOne.myShipID == '2'
        assert captainTwo.myShipID == '1'
        
    def testSetNewRegiment(self):
        """Create a new regiment for empire on system
        input->empireID, systemID, typeID, name='Marine'"""
        assert len(self.myGalaxy.regiments) == 0
        self.myGalaxy.setNewRegiment('0', '56', '1')
        self.myGalaxy.setNewRegiment('2', '2', '2')
        assert len(self.myGalaxy.regiments) == 2
    
    def testGetMyRegiments(self):
        """Return myRegimentsDict, myArmiesDict, otherArmiesDict, warpedArmiesDict for client
        input->empireID"""
        (myRegimentsDict, myArmiesDict, otherArmiesDict, warpedArmiesDict) = self.myGalaxy.getMyRegiments('0')
        for id, myRegiment in self.myGalaxy.regiments.iteritems():
            if myRegiment.empireID == '0':
                myRegimentDict = myRegimentsDict[id]
                for attr in myRegiment.defaultAttributes:
                    assert getattr(myRegiment, attr) == myRegimentDict[attr]
        
        for systemID, RegimentIDList in myArmiesDict.iteritems():
            for RegimentID in RegimentIDList:
                myRegiment = self.myGalaxy.regiments[RegimentID]
                assert myRegiment.fromSystem == systemID
                
        assert otherArmiesDict == {'2': ['2']}
    
    def testMoveShips(self):
        """Move Ships"""
        (myShipsDict, myArmadasDict, otherArmadasDict, warpedArmadasDict) = self.myGalaxy.getMyShips('0')
        assert myArmadasDict['56'] == ['6', '1', '2', '3', '4', '5']
        assert warpedArmadasDict == {}
        myShip = self.myGalaxy.ships['4']
        myShip.setAvailSystems()
        assert myShip.empireID == '0'
        assert myShip.fromSystem == '56'
        assert myShip.availSystems == ['68', '69', '46', '47', '70', '57']
        assert myShip.oldAvailSystems == ['68', '69', '46', '47', '70', '57']
        assert myShip.maxAssault == 0
        
        result = self.myGalaxy.moveShips(['4'], '0', '70')
        assert result == 1
        myEmpire = self.myGalaxy.empires[self.myGalaxy.ships['4'].empireID]
        assert myShip.toSystem == '70'
        assert myShip.availSystems == ['56']
        assert myShip.oldAvailSystems == ['68', '69', '46', '47', '70', '57']
        (myShipsDict, myArmadasDict, otherArmadasDict, warpedArmadasDict) = self.myGalaxy.getMyShips('0')
        assert myArmadasDict['56'] == ['6', '1', '2', '3', '5']
        assert warpedArmadasDict['70'] == ['4']
        
    def testCancelMoveShips(self):
        """Cancel move ships"""
        myShip = self.myGalaxy.ships['4']
        result = self.myGalaxy.cancelMoveShips(['4'], '0')
        assert myShip.empireID == '0'
        assert myShip.fromSystem == '56'
        assert myShip.availSystems == ['68', '69', '46', '47', '70', '57']
        assert myShip.oldAvailSystems == ['68', '69', '46', '47', '70', '57']
        (myShipsDict, myArmadasDict, otherArmadasDict, warpedArmadasDict) = self.myGalaxy.getMyShips('0')
        assert myArmadasDict['56'] == ['6', '1', '2', '3', '4', '5']
        assert warpedArmadasDict == {}
    
    def testRemoveRegiment(self):
        """Remove Regiment
        input->shipID"""
        for id in ['1','2']:
            assert id in self.myGalaxy.regiments.keys()
            myRegiment = self.myGalaxy.regiments[id]
            self.myGalaxy.removeRegiment(id)
        assert len(self.myGalaxy.regiments.keys()) == 0
        
    def testSetEmpireStats(self):
        """Each Round all Empires are compared to each other for stats which are mailed out"""
        myEmpire = self.myGalaxy.empires['2']
        self.myGalaxy.setEmpireStats()
        for id, myMail in myEmpire.mailBox.iteritems():
            if myMail.subject == 'Round:1 Statistics':
                body = myMail.body
                assert 'Brown Empire ROUND 1 STATS:' in body
    
    def testGenShipBattle(self):
        """Generate a ShipBattle object for processing by the Ship Simulator and for
        Ship Battle History storage"""
        mySystem = self.myGalaxy.systems['1']
        count = 0
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.toSystem == mySystem.id:
                count += 1
                if count < 5:
                    myShip.empireID = '1'
                else:
                    myShip.empireID = '2'
        
        assert self.myGalaxy.shipBattles == {}
        self.myGalaxy.genShipBattle('1')
        assert self.myGalaxy.empires['1'].myShipBattles == ['1']
        assert self.myGalaxy.empires['2'].myShipBattles == ['1']
        assert self.myGalaxy.shipBattles == {'1':'1-System-1'}
    
    def testGetShipBattle(self):
        """Return a Ship Battle serialized object"""
        self.myShipBattle = storedata.loadFromString(self.myGalaxy.getShipBattle('1','1'))
        assert self.myShipBattle.empiresDict != {}
        assert self.myShipBattle.shipsDict != {}
        assert self.myShipBattle.captainsDict != {}
    