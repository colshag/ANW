# Armada Net Wars (ANW)
# test_server.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The function of server is to answer clients and manage galaxy data
# ---------------------------------------------------------------------------
from anw.admin import generate
from anw.aw import galaxy
from anw.func import funcs, globals
from anw.gae.access import GAE, LocalGAE
from anw.server import anwserver
from anw.util.Injection import Services
import copy
import os
import xmlrpclib


class TestServer(object):
    
    def setup_class(self):

        Services.register(GAE, LocalGAE)
        Services.inject(GAE).username = "admin"
        Services.inject(GAE).password = "adminpass"
        
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.generate = None
        self.myServer = None
        self.myServerConnection = None
        self.myGalaxy = None
        self.myEmpire = None
        self.key={'galaxyName':'ANW1', 'empireID':'2', 'empirePass':'pass2', 'key':'12345', 'version':globals.currentVersion, 'ip':'127.0.0.1', 'round':1}
        
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
        self.myGalaxy = self.generate.getGalaxy()
        self.myServer = anwserver.ANWServer()
        self.myServer.runServer(7999)
        self.myServer.galaxies['ANW1'] = self.myGalaxy
        self.myEmpire = self.myGalaxy.empires['2']
    
    def testStartServer(self):
        """Can Server start up"""
        assert self.myServer.__module__ == 'anw.server.anwserver'
        assert 'ANW1' in self.myServer.galaxies.keys()
    
    def testCopyGalaxy(self):
        """Can Server copy the galaxy properly to file"""
        result = anwserver.copyGalaxy(self.myServer, 'ANW1')
        assert result == 1
    
    def testSaveGalaxy(self):
        """Can Server save the galaxy"""
        result = anwserver.saveGalaxy(self.myServer, 'ANW1')
        assert result == 1
    
    def testValidateLogin(self):
        """Does initial player login validate"""
        # I don't like this.
        gae = xmlrpclib.Server('http://localhost:8090/xmlrpc/')
        oldkey = copy.deepcopy(self.key)
        #result = self.myServer._ValidateLogin(self.key)
        for id, myEmpire in self.myGalaxy.empires.iteritems():
            # all other tests are based around id #2
            if id != "2":
                continue
            d = gae.app.getGameDictionary('testguy' + str(id), 'pass1')
            myEmpire.player = 'testguy' + str(id)
            myEmpire.password = d['ANW1']['token']
            print myEmpire.player, myEmpire.password
            self.key['empirePass'] = d['ANW1']['token']
            self.key['empireID'] = id
             
        result = self.myServer._ValidateLogin(self.key)
        assert result == 1

        self.key = oldkey
    
    def testLogin(self):
        """Login asks the Server to store all relevant information as a dict of dicts
        the dict is then turned into a string and compressed, to be converted by client"""
        result = self.myServer.xmlrpc_login(self.key)
        result = funcs.decompressString(result)
        result = eval(result)
        for key in ['myGalaxy', 'allEmpires', 'allSystems', 'myTech', 'tradeRoutes',
                    'marketOrders', 'marketStats', 'shipDesignsDict', 'myCaptains', 
                    'myShips', 'myArmadas', 'otherArmadas', 'warpedArmadas', 'shipBattleDict', 'myRegiments', 
                    'myArmies', 'otherArmies', 'warpedArmies']:
            assert key in result.keys()
    
    def testValidateKey(self):
        """Does generated Key Validate"""
        self.myGalaxy.empires['2'].key = '12345'
        self.myGalaxy.empires['2'].ip = '127.0.0.1'
        self.key={'galaxyName':'ANW1', 'empireID':'2', 'key':'12345', 'ip':'127.0.0.1', 'round':1}
        result = self.myServer._ValidateKey(self.key)
        assert result == 1
    
    def testGetGalaxies(self):
        """Attempt to retreive galaxy name as dict [name] = name"""
        result = self.myServer.xmlrpc_getGalaxies()
        assert 'ANW1' in result
    
    def testAddTechOrder(self):
        """Attempt to add a tech order and modify and remove tech order"""
        techOrderDict = {'type': '11', 'round': 1, 'value': 45}
        result = self.myServer.xmlrpc_addTechOrder(self.key, techOrderDict)
        assert result == 'You have already researched this technology'
        techOrderDict = {'type': '13', 'round': 1, 'value': 45}
        result = self.myServer.xmlrpc_addTechOrder(self.key, techOrderDict)
        assert result == 'Research:Radar First '
        techOrderDict = {'type': '4', 'round': 1, 'value': 45}
        self.myEmpire.rpAvail = 0
        self.myEmpire.rpUsed = 0
        result = self.myServer.xmlrpc_addTechOrder(self.key, techOrderDict)
        assert result == 'You do not have enough research points left: Req=45, Avail=0'
        self.myEmpire.rpAvail = 50
        result = self.myServer.xmlrpc_addTechOrder(self.key, techOrderDict)
        assert result == 1
        d = self.myEmpire.getMyOrdersByRound('techOrders')
        assert d == {'4-1': {'id': '4-1', 'round': 1, 'type': '4', 'value': '45'}}
        techOrderDict = {'type': '4', 'round': 1, 'value': -15}
        result = self.myServer.xmlrpc_addTechOrder(self.key, techOrderDict)
        assert result == 1
        d = self.myEmpire.getMyOrdersByRound('techOrders')
        assert d == {'4-1': {'id': '4-1', 'round': 1, 'type': '4', 'value': '30'}}
        assert self.myEmpire.rpAvail == 20
        assert self.myEmpire.rpUsed == 30
    
    def testGetTechOrders(self):
        """Attempt to retreive tech orders"""
        result = self.myServer.xmlrpc_getEmpireOrders(self.key, 'techOrders')
        assert result == {'4-1':{'id':'4-1', 'round':1, 'type':'4', 'value':'30'}}
    
    def testGetEmpireUpdate(self):
        """Attempt an empire update of information"""
        result = self.myServer.xmlrpc_getEmpireUpdate(self.key, ['rpAvail','rpUsed'])
        assert result == {'rpAvail':20, 'rpUsed':30}
    
    def testChangeCityIndustry(self):
        """Add update city list for system"""
        assert self.myGalaxy.systems['10'].cityIndustry == [10,0,0]
        result = self.myServer.xmlrpc_changeCityIndustry(self.key, '1', [40,40,40])
        assert result == 'You are trying to update City Industry on System not owned by you'
        result = self.myServer.xmlrpc_changeCityIndustry(self.key, '10', [40,40,40])
        assert result == 'You are trying to update City Industry where total cities(120) not equal to 10'
        result = self.myServer.xmlrpc_changeCityIndustry(self.key, '10', [2,3,5])
        assert result == 1
        assert self.myGalaxy.systems['10'].cityIndustry == [2,3,5]
    
    def testAddIndustry(self):
        """Add new industry to system"""
        self.myEmpire.CR = 217760.0
        assert self.myEmpire.CR == 217760.0
        mySystem = self.myGalaxy.systems['10']
        mySystem.AL = 0
        assert mySystem.myIndustry['1'] == 0
        result = self.myServer.xmlrpc_addIndustry(self.key, '1', 0, '3')
        assert result == 'You are trying to add industry on System not owned by you'
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', 0, '3')
        assert result == 'You cannot add 0 Industry'
        assert mySystem.cities == 10
        assert mySystem.citiesUsed == 0
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', 11, '3')
        assert result == 'Not enough Cities to build Intelligent Alloy Factory on %s' % mySystem.name
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', 2, '3')
        assert result == 'Intelligent Alloy Factories must be researched before industry can be added'
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', -2, '3')
        assert result == 'Cannot add negative amounts'
        
        # CR only paid when new industry
        for dataList in ((0,0,1,1), (5,5,3,3), (8,5,2,2), (3,5,4,2), (14,5,1,1), (1,5,1,0)):
            (myIndustry, myOldIndustry, amountToAdd, amountCR) = dataList
            mySystem.myOldIndustry['1'] = myOldIndustry
            mySystem.myIndustry['1'] = myIndustry
            result = self.myServer.xmlrpc_addIndustry(self.key, '10', amountToAdd, '1')
            assumedResult = 'You Require: (CR:%d),(AL:%d),(EC:0),(IA:0) Resources' % (amountCR*1000,amountToAdd*100)
            assert result == assumedResult

        mySystem.myIndustry['1'] = 0
        mySystem.myOldIndustry['1'] = 0
        mySystem.AL = 200
        assert self.myEmpire.CR == 217760.0
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', 2, '1')
        assert result == 1
        assert mySystem.AL == 0
        assert self.myEmpire.CR == 215760.0
        assert mySystem.citiesUsed == 2
        assert mySystem.myIndustry['1'] == 2
    
    def testRemoveIndustry(self):
        """Remove industry from system"""
        mySystem = self.myGalaxy.systems['10']
        assert mySystem.myIndustry['1'] == 2
        result = self.myServer.xmlrpc_removeIndustry(self.key, '1', 0, '3')
        assert result == 'You are trying to remove industry on System not owned by you'
        result = self.myServer.xmlrpc_removeIndustry(self.key, '10', 0, '3')
        assert result == 'You cannot remove 0 Industry'
        assert mySystem.cities == 10
        assert mySystem.citiesUsed == 2
        result = self.myServer.xmlrpc_removeIndustry(self.key, '10', 2, '3')
        assert result == 'Not enough Intelligent Alloy Factory on %s' % mySystem.name
        result = self.myServer.xmlrpc_removeIndustry(self.key, '10', -1, '3')
        assert result == 'Cannot remove negative amounts'
        mySystem.AL = 0
        
        # CR only refunded on new industry
        for dataList in ((1,0,1,1), (5,5,3,0), (8,5,2,2), (3,5,3,0), (10,5,1,1), (1,5,1,0)):
            (myIndustry, myOldIndustry, amountToRemove, amountCR) = dataList
            mySystem.myOldIndustry['1'] = myOldIndustry
            mySystem.myIndustry['1'] = myIndustry
            mySystem.citiesUsed = myIndustry
            self.myEmpire.CR = 100000.0
            result = self.myServer.xmlrpc_removeIndustry(self.key, '10', amountToRemove, '1')
            assert result == 1
            assumedResult = (100000 + 1000*amountCR)
            assert self.myEmpire.CR == assumedResult

        mySystem.myOldIndustry['1'] = 0
        mySystem.myIndustry['1'] = 0
        self.myEmpire.CR = 168909.0
        assert self.myEmpire.CR == 168909.0
        mySystem.AL = 100
        result = self.myServer.xmlrpc_addIndustry(self.key, '10', 1, '1')
        assert result == 1
        assert mySystem.AL == 0
        assert self.myEmpire.CR == 167909.0
        result = self.myServer.xmlrpc_removeIndustry(self.key, '10', 1, '1')
        assert result == 1
        assert mySystem.AL == 100
        assert self.myEmpire.CR == 168909.0
        
        mySystem.myIndustry['1'] = 2
        mySystem.myOldIndustry['1'] = 2
        mySystem.AL = 0
        self.myEmpire.CR = 168909.0
        assert self.myEmpire.CR == 168909.0
        mySystem.citiesUsed = 2
        result = self.myServer.xmlrpc_removeIndustry(self.key, '10', 2, '1')
        assert result == 1
        assert mySystem.AL == 200
        assert self.myEmpire.CR == 168909.0
        assert mySystem.citiesUsed == 0
        assert mySystem.myIndustry['1'] == 0
        mySystem.AL = 0

    def testAddTradeRoute(self):
        """Can a trade route be added"""
        d = {'fromSystem':'1', 'toSystem':'2', 'type':'REG', 
             'AL':100,'EC':0,'IA':0,'oneTime':1}
        result = self.myServer.xmlrpc_addTradeRoute(self.key, d)
        assert result == 'System Owners are not the same, or no Trade Pact in Effect'
        
        d = {'fromSystem':'10', 'toSystem':'11', 'type':'REG', 
             'AL':100,'EC':0,'IA':0,'oneTime':1}
        result = self.myServer.xmlrpc_addTradeRoute(self.key, d)
        self.myGalaxy.systems['10'].AL = 0
        assert self.myGalaxy.systems['10'].AL == 0
        assert result == '%s does not have enough resources to setup this trade route' % self.myGalaxy.systems['10'].name
        self.myGalaxy.systems['10'].AL = 200
        result = self.myServer.xmlrpc_addTradeRoute(self.key, d)
        assert result == 1
        
        d['AL'] = 200
        result = self.myServer.xmlrpc_addTradeRoute(self.key, d)
        assert result == 1
        
        d = {'fromSystem':'11', 'toSystem':'10', 'type':'GEN', 
             'AL':0,'EC':0,'IA':0,'oneTime':0}
        result = self.myServer.xmlrpc_addTradeRoute(self.key, d)
        assert result == 1
    
    def testGetTradeRoutes(self):
        """Can we retrieve trade route info as dict"""
        result = self.myServer.xmlrpc_getTradeRoutes(self.key)
        assert result == {'10-11-REG': {'AL': 200.0,
                                        'EC': 0.0,
                                        'IA': 0.0,
                                        'fromSystem': '10',
                                        'id': '10-11-REG',
                                        'imageFile': 'traderoute_blue_once',
                                        'oneTime': 1,
                                        'toSystem': '11',
                                        'type':'REG',
                                        'warpReq': 0},
                          '11-10-GEN': {'AL': 0.0,
                                        'EC': 0.0,
                                        'IA': 0.0,
                                        'fromSystem': '11',
                                        'id': '11-10-GEN',
                                        'imageFile': 'traderoute_orange',
                                        'oneTime': 0,
                                        'toSystem': '10',
                                        'type':'GEN',
                                        'warpReq': 0}}

        result = self.myServer.xmlrpc_getTradeRoutes(self.key, '10-11-REG')
        assert result == {'10-11-REG': {'AL': 200.0,
                                        'EC': 0.0,
                                        'IA': 0.0,
                                        'fromSystem': '10',
                                        'id': '10-11-REG',
                                        'imageFile': 'traderoute_blue_once',
                                        'oneTime': 1,
                                        'toSystem': '11',
                                        'type':'REG',
                                        'warpReq': 0}}
    
    def testCancelTradeRoute(self):
        """Can we cancel a trade route"""
        assert '10-11-REG' in self.myGalaxy.tradeRoutes.keys()
        result = self.myServer.xmlrpc_cancelTradeRoute(self.key, '10-11-REG')
        assert '10-11-REG' not in self.myGalaxy.tradeRoutes.keys()
    
    def testAddShipDesign(self):
        """Can we add a ship design"""
        self.myEmpire.shipDesigns = {}
        compDict = {'fore':['9','3','6','9','3','3','53','27','9','6'],
                                'port':['9','3','6','9','3','3','53','27','9','6'],
                                'star':['9','3','6','9','3','3','53','27','9','6'],
                                'aft' :['W1','W1','W1','W1','W1','W1','W1','W1','27','6']}
        weapDict = {'aft-1':{'id':'1', 'type':'32', 'facing':0}}
        dOrder = {'name':'TestShip', 'hullID':'4', 'compDict':compDict, 'weaponDict':weapDict}
        result = self.myServer.xmlrpc_addShipDesign(self.key, dOrder)
        assert result == ('1', 'HCO1-TestShip')
        assert self.myEmpire.shipDesigns.keys() == ['1']
    
    def testAddDroneDesign(self):
        """Can we add a drone design"""
        self.myEmpire.droneDesigns = {}
        compDict = {'fore':['9','9','27','27','W1','W1','W1','W1']}
        weapDict = {'fore-1':{'id':'1', 'type':'1', 'facing':0}}
        dOrder = {'name':'TestDrone', 'hullID':'101', 'compDict':compDict, 'weaponDict':weapDict}
        result = self.myServer.xmlrpc_addDroneDesign(self.key, dOrder)
        assert result == 'You do not have enough Design Centers to build another Drone Design this Round'
        self.myEmpire.designsLeft = 1
        result = self.myServer.xmlrpc_addDroneDesign(self.key, dOrder)
        assert result == ('1', 'LND1-TestDrone')
        assert self.myEmpire.shipDesigns.keys() == ['1']
    
    def testAddShipOrder(self):
        """Can we add a ship build order"""
        assert self.myEmpire.shipDesigns.keys() == ['1']
        assert self.myEmpire.id == '2'
        assert self.key['empireID'] == '2'
        dOrder = {'type':'Add Ship', 'value':'2-1', 'round':1, 'system':'3'}
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 'Invalid Order, coming from system not owned by Empire'
        dOrder['system'] = '10'
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 'Not have enough Shipyard Capacity to build 2 HCO1-TestShip on Rnatz'
        dOrder['system'] = '22'
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert 'You Require: (CR:' in result
        assert self.myEmpire.CR == 168909.0
        self.myGalaxy.systems['22'].AL = 4000
        self.myGalaxy.systems['22'].EC = 2000
        self.myGalaxy.systems['22'].IA = 400
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 1
        assert self.myEmpire.industryOrders['1'].round == 1
        assert self.myEmpire.industryOrders['1'].system == '22'
        assert self.myEmpire.industryOrders['1'].type == 'Add Ship'
        assert self.myEmpire.industryOrders['1'].value == '2-1'
        assert self.myEmpire.CR == 138069.0
    
    def testModifyShipOrder(self):
        """Can we modify a ship order"""
        self.myEmpire.CR = 168909.0
        assert self.myEmpire.CR == 168909.0
        self.myGalaxy.systems['22'].AL = 0
        self.myGalaxy.systems['22'].EC = 0
        self.myGalaxy.systems['22'].IA = 0
        assert self.myEmpire.industryOrders['1'].round == 1
        assert self.myEmpire.industryOrders['1'].system == '22'
        assert self.myEmpire.industryOrders['1'].type == 'Add Ship'
        assert self.myEmpire.industryOrders['1'].value == '2-1'
        
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '1', -3)
        assert result == 'Cannot Remove more ships then in Ship Build Order'
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '1', 0)
        assert result == 'Invalid Order to modify'
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '999', 0)
        assert result == 'Invalid Order to modify'
        
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '1', -1)
        assert result == 1
        assert self.myEmpire.industryOrders['1'].value == '1-1'
        assert self.myEmpire.CR == 184329.0
        
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '1', 1)
        assert result == 2
        assert self.myEmpire.industryOrders['1'].value == '2-1'
        assert self.myEmpire.CR == 168909.0
        assert self.myGalaxy.systems['22'].AL == 0
        assert self.myGalaxy.systems['22'].EC == 0
        assert self.myGalaxy.systems['22'].IA == 0
        
        result = self.myServer.xmlrpc_modifyShipOrder(self.key, '1', -2)
        assert result == 0
        assert self.myEmpire.industryOrders == {}
        assert self.myEmpire.CR == 199749.0

    
    def testAddRegimentOrder(self):
        """Can we add a regiment build order"""
        assert self.myEmpire.id == '2'
        assert self.key['empireID'] == '2'
        dOrder = {'type':'Add Regiment', 'value':'3-2', 'round':1, 'system':'4'}
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 'Invalid Order, coming from system not owned by Empire'
        dOrder['system'] = '10'
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 'Not have enough Military Installation Capacity to build 3 Light Nuclear Infantry on Rnatz'
        dOrder['system'] = '22'
        self.myEmpire.CR = 0.0
        assert self.myEmpire.CR == 0.0
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 'You Require: (CR:5400),(AL:0),(EC:0),(IA:144) Resources'
        self.myEmpire.CR = 10000.0
        assert self.myEmpire.CR == 10000.0
        result = self.myServer.xmlrpc_addIndustryOrder(self.key, dOrder)
        assert result == 1
        assert self.myEmpire.industryOrders['1'].round == 1
        assert self.myEmpire.industryOrders['1'].system == '22'
        assert self.myEmpire.industryOrders['1'].type == 'Add Regiment'
        assert self.myEmpire.industryOrders['1'].value == '3-2'
        assert self.myEmpire.CR == 4600.0
        
    def testModifyRegimentOrder(self):
        """Can we modify a regiment order"""
        self.myEmpire.CR = 10000.0
        assert self.myEmpire.CR == 10000.0
        self.myGalaxy.systems['22'].AL = 0
        self.myGalaxy.systems['22'].EC = 0
        self.myGalaxy.systems['22'].IA = 0
        assert self.myEmpire.industryOrders.keys() == ['1']
        assert self.myEmpire.industryOrders['1'].round == 1
        assert self.myEmpire.industryOrders['1'].system == '22'
        assert self.myEmpire.industryOrders['1'].type == 'Add Regiment'
        assert self.myEmpire.industryOrders['1'].value == '3-2'
        
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '1', -5)
        assert result == 'Cannot Remove more regiments then in Regiment Build Order'
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '1', 0)
        assert result == 'Invalid Order to modify'
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '999', 0)
        assert result == 'Invalid Order to modify'
        
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '1', -1)
        assert result == 2
        assert self.myEmpire.industryOrders['1'].value == '2-2'
        assert self.myEmpire.CR == 11800.0
        assert self.myGalaxy.systems['22'].AL == 0
        assert self.myGalaxy.systems['22'].EC == 0
        assert self.myGalaxy.systems['22'].IA == 48
        
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '1', 1)
        assert result == 3
        assert self.myEmpire.industryOrders['1'].value == '3-2'
        assert self.myEmpire.CR == 10000.0
        assert self.myGalaxy.systems['22'].AL == 0
        assert self.myGalaxy.systems['22'].EC == 0
        assert self.myGalaxy.systems['22'].IA == 0
        
        result = self.myServer.xmlrpc_modifyRegimentOrder(self.key, '1', -3)
        assert result == 0
        assert self.myEmpire.industryOrders == {}
        assert self.myEmpire.CR == 15400.0
        assert self.myGalaxy.systems['22'].AL == 0
        assert self.myGalaxy.systems['22'].EC == 0
        assert self.myGalaxy.systems['22'].IA == 144
    
    def testSendMail(self):
        """Send Message to Empire"""
        assert self.key['empireID'] == '2'
        empireMe = self.myGalaxy.empires['2']
        empireYou = self.myGalaxy.empires['3']
        result = self.myServer.xmlrpc_sendMail(self.key, '3', 'This is a test message')
        assert result == 1
        d = empireYou.getMailUpdate(['1','2','3','4','5'])
        assert d['6']['body'] != ''
        
        d = empireMe.getMailUpdate(['1','2','3','4','5'])
        assert d['6']['body'] != ''
    
    def testIncreaseDiplomacy(self):
        """Increase Diplomacy with another empire"""
        assert self.key['empireID'] == '2'
        empireMe = self.myGalaxy.empires['2']
        empireYou = self.myGalaxy.empires['3']
        assert empireMe.diplomacy['3'].myIntent == 'none'
        assert empireYou.diplomacy['2'].myIntent == 'none'
        assert empireMe.diplomacy['3'].empireIntent == 'none'
        assert empireYou.diplomacy['2'].empireIntent == 'none'
        result = self.myServer.xmlrpc_increaseDiplomacy(self.key, '3')
        assert result == 1
        assert empireMe.diplomacy['3'].myIntent == 'increase'
        assert empireYou.diplomacy['2'].myIntent == 'none'
        assert empireMe.diplomacy['3'].empireIntent == 'none'
        assert empireYou.diplomacy['2'].empireIntent == 'increase'
        
    def testDecreaseDiplomacy(self):
        """Decrease Diplomacy with another empire"""
        assert self.key['empireID'] == '2'
        empireMe = self.myGalaxy.empires['2']
        empireYou = self.myGalaxy.empires['3']
        assert empireMe.diplomacy['3'].myIntent == 'increase'
        assert empireYou.diplomacy['2'].myIntent == 'none'
        assert empireMe.diplomacy['3'].empireIntent == 'none'
        assert empireYou.diplomacy['2'].empireIntent == 'increase'
        result = self.myServer.xmlrpc_decreaseDiplomacy(self.key, '3')
        assert result == 1
        assert empireMe.diplomacy['3'].myIntent == 'decrease'
        assert empireYou.diplomacy['2'].myIntent == 'none'
        assert empireMe.diplomacy['3'].empireIntent == 'none'
        assert empireYou.diplomacy['2'].empireIntent == 'decrease'
        d = empireYou.getMyDiplomacyInfo()
        assert d['2']['empireIntent'] == 'none'