# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_generate.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The function of generate is to build up a galaxy object for admin purposes
# ---------------------------------------------------------------------------
import os

from anw.admin import generate
from anw.aw import galaxy, system, tech
from anw.func import globals, datatype
from anw.war import shipdesign, ship

class TestGenerateGalaxy(object):
    
    def setup_class(self):
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.generate = None
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
    
    def testFindCorrectDataPath(self):
        """The point of this test is to make sure we are pointing at Data Path"""
        files = self.generate.getDataFilesAsList()
        for file in files:
            if file == 'industrydata.csv':                
                assert file == 'industrydata.csv'
                return
        raise ValueError("Cannot find Correct Data Path")
    
    def testGenInitialGalaxy(self):
        """Can we create a galaxy object"""
        self.generate.genInitialGalaxy()
        assert isinstance(self.generate.myGalaxy, galaxy.Galaxy)
        assert self.generate.myGalaxy.version == globals.currentVersion
    
    def testSetTemplateData(self):
        """Can we add the galaxy template file information to galaxy"""
        myTempGalaxy = galaxy.Galaxy({})
        self.generate.setTemplateData('starMap4A.map')
        assert self.generate.myGalaxy.numEmpires == 5
        for attr in myTempGalaxy.defaultAttributes:
            assert hasattr(self.generate.myGalaxy, attr)
    
    def testGenDataTypes(self):
        """Can we create the various data types"""
        myTempDataType = datatype.DataType({})
        self.generate.genDataTypes()
        for dataname in ('regimentdata', 'industrydata', 'componentdata', 
                     'shiphulldata', 'dronehulldata', 'weapondata'):
            myDataTypeDict = getattr(self.generate.myGalaxy, dataname)
            assert len(myDataTypeDict.keys()) > 4
            key = myDataTypeDict.keys()[0]
            myDataType = myDataTypeDict[key]
            for attr in myTempDataType.defaultAttributes:
                assert hasattr(myDataType, attr)
    
    def testGenEmpires(self):
        """Were the Empires created properly"""
        self.generate.genEmpires()
        assert len(self.generate.myGalaxy.empires.keys()) == self.generate.myGalaxy.numEmpires
        myTestEmpire = self.generate.myGalaxy.empires['1']
        assert '6' not in self.generate.myGalaxy.empires.keys()
        assert myTestEmpire.name == globals.empires[1]['name']
        assert myTestEmpire.color1 == globals.empires[1]['color1']
        assert myTestEmpire.color2 == globals.empires[1]['color2']
        assert len(myTestEmpire.diplomacy.keys()) == self.generate.myGalaxy.numEmpires
        for empireID, myDiplomacy in myTestEmpire.diplomacy.iteritems():
            assert myDiplomacy.diplomacyID == 2
    
    def testGenSystems(self):
        """Can we create the systems properly"""
        myTempSystem = system.System({})
        self.generate.genSystems()
        assert len(self.generate.myGalaxy.systems.keys()) > 16
        myTestSystem = self.generate.myGalaxy.systems['1']
        for attr in myTempSystem.defaultAttributes:
            assert hasattr(myTestSystem, attr)
        assert len(myTestSystem.connectedSystems) > 0
        assert len(myTestSystem.myIndustry.keys()) > 0
    
    def testSetTechData(self):
        """Was the tech data retrieved?"""
        assert len(self.generate.generateTech.techData) > 100
    
    def testGenTech(self):
        """Can we create Tech"""
        myTempTech = tech.Tech({})
        myTestEmpire = self.generate.myGalaxy.empires['1']
        assert myTestEmpire.name == globals.empires[1]['name']
        assert len(myTestEmpire.techTree.keys()) > 100
        myTestTech = self.generate.myGalaxy.empires['1'].techTree['1']
        for attr in myTempTech.defaultAttributes:
            assert hasattr(myTestTech, attr)
    
    def testSetTechPosition(self):
        """Does technology properly move based on Tech Age"""
        myTech1 = self.generate.myGalaxy.empires['2'].techTree['0']
        myTech2 = self.generate.myGalaxy.empires['2'].techTree['100']
        assert myTech1.x + 24.0 == myTech2.x
        assert myTech1.y == myTech2.y       
    
    def testGenDefaultIndustry(self):
        """Can we create the default industry for neutral player
        which is some militia fortresses (industrydataid = 25),
        and for regular players which is only on captial system and 
        is based on map file"""
        for systemID, mySystem in self.generate.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == '0':
                assert mySystem.myIndustry['22'] == 0
            elif mySystem.id == '16':
                assert mySystem.myIndustry['34'] == 0
        self.generate.genDefaults()
        for systemID, mySystem in self.generate.myGalaxy.systems.iteritems():
            if mySystem.myEmpireID == '0':
                if mySystem.cities >= 30:
                    assert mySystem.myIndustry['22'] == 0
                    assert mySystem.myIndustry['23'] == 0
                    assert mySystem.myIndustry['24'] > 0
                elif mySystem.cities >= 20:
                    assert mySystem.myIndustry['22'] == 0
                    assert mySystem.myIndustry['23'] > 0
                    assert mySystem.myIndustry['24'] == 0
                else:
                    assert mySystem.myIndustry['22'] > 0
                    assert mySystem.myIndustry['23'] == 0
                    assert mySystem.myIndustry['24'] == 0
            elif mySystem.id == '16':
                assert mySystem.myIndustry['34'] == 3
    
    def testEndRound(self):
        """Can the Galaxy can end its round"""
        assert self.generate.myGalaxy.currentRound == 0
        self.generate.myGalaxy.endRound(doAITurn=0)
        assert self.generate.myGalaxy.currentRound == 1
    
    def testGenDesigns(self):
        """Can drone and ship designs be created"""
        myTempShipDesign = shipdesign.ShipDesign({})
        self.generate.genDesigns()
        for empireID, myEmpire in self.generate.myGalaxy.empires.iteritems():
            for droneDesignID, myDroneDesign in myEmpire.droneDesigns.iteritems():
                for attr in myTempShipDesign.defaultAttributes:
                    assert hasattr(myDroneDesign, attr)
            for shipDessignID, myShipDesign in myEmpire.shipDesigns.iteritems():
                for attr in myTempShipDesign.defaultAttributes:
                    assert hasattr(myShipDesign, attr)
    
    def testGenNeutralShips(self):
        """Can Neutral Ships be created"""
        myTempShip = ship.Ship({})
        self.generate.genNeutralShips()
        for shipID, myShip in self.generate.myGalaxy.ships.iteritems():
            for attr in myTempShip.defaultAttributes:
                assert hasattr(myShip, attr)
        assert len(self.generate.myGalaxy.ships.keys()) == len(self.generate.myGalaxy.captains.keys())
            
            
            
        
        