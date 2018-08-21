# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_system.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an System in ANW
# ---------------------------------------------------------------------------
import os
import types

from anw.admin import generate
from anw.aw import galaxy
from anw.func import globals

class TestSystem(object):
    
    def setup_class(self):
        osPath = os.getcwd()
        self.dataPath = osPath[:-7] + '/Data/'
        self.myGalaxy = None
        self.mySystem = None
        self.generate = None
        self.generate = generate.GenerateGalaxy()
        self.generate.genGalaxy(self.dataPath, 'starMap4A.map')
        self.myGalaxy = self.generate.getGalaxy()
        self.mySystem = self.myGalaxy.systems['1']
    
    def testGenGalaxy(self):
        """Can entire Galaxy Object be generated"""
        assert self.myGalaxy.xMax == 14 * globals.systemSize
        assert self.myGalaxy.yMax == 8 * globals.systemSize
    
    def testGetMyInfoAsDict(self):
        """Get Empire Information as Dictionary"""
        d = self.mySystem.getMyInfoAsDict()
        for attr, value in d.iteritems():
            assert getattr(self.mySystem, attr) == value
    
    def testGetMySystemInfo(self):
        """Return detailed System info as dict to goto player"""
        d = self.mySystem.getMySystemInfo()
        for attr in self.mySystem.defaultAttributes:
            assert attr in d.keys()
    
    def testSetMyEmpire(self):
        """Set the Empire Owner of System
        input->empireObject"""
        assert self.mySystem.myEmpireID == '0'
        self.mySystem.setMyEmpire(self.myGalaxy.empires['2'])
        assert self.mySystem.myEmpireID == '2'
        assert self.mySystem.myEmpire == self.myGalaxy.empires['2']
    
    def testSetMyGalaxy(self):
        """Set the System Galaxy Owner
        input-->Galaxy Object"""
        self.mySystem.setMyGalaxy(self.myGalaxy)
        assert self.mySystem.myGalaxy == self.myGalaxy
        for empireID, intelReport in self.mySystem.intelReport.iteritems():
            assert intelReport == self.mySystem.blankIntelReport
    
    def testAddFleetCadets(self):
        """Add Fleet Cadets
        input->amount"""
        assert self.mySystem.fleetCadets == 0
        self.mySystem.addFleetCadets(1)
        assert self.mySystem.fleetCadets == 1
    
    def testAddArmyCadets(self):
        """Add Army Cadets
        input->amount"""
        assert self.mySystem.armyCadets == 0
        self.mySystem.addArmyCadets(1)
        assert self.mySystem.armyCadets == 1
    
    def testSetMIC(self):
        """Set the Military Installation Capactiy for the system
        input->amount"""
        assert self.mySystem.availMIC == 0
        self.mySystem.setMIC(1000)
        assert self.mySystem.availMIC == 1000
        assert self.mySystem.usedMIC == 0
    
    def testSetWGC(self):
        """Set the Warp Gate Capacity for the system
        input->amount"""
        assert self.mySystem.availWGC == 0
        self.mySystem.setWGC(10)
        assert self.mySystem.availWGC == 10
        assert self.mySystem.usedWGC == 0
    
    def testSetJammingStrength(self):
        """Set the Jamming Strength of System
        input->amount"""
        assert self.mySystem.jammingStrength == 0
        self.mySystem.setJammingStrength(10)
        assert self.mySystem.jammingStrength == 10
    
    def testSetRadarStrength(self):
        """Set the Radar Strength of System
        input->amount"""
        assert self.mySystem.radarStrength == 0
        self.mySystem.setRadarStrength(20)
        assert self.mySystem.radarStrength == 20
    
    def testSetIntelReports(self):
        """Setup Intel Reports for System based on Jamming/Radar"""
        d = self.mySystem.intelReport
        assert d == {'0': {'industryReport': {}, 'marineReport': {}, 'round': 0, 'shipReport': {}},
                     '1': {'industryReport': {}, 'marineReport': {}, 'round': 0, 'shipReport': {}},
                     '2': {'industryReport': {}, 'marineReport': {}, 'round': 0, 'shipReport': {}},
                     '3': {'industryReport': {}, 'marineReport': {}, 'round': 0, 'shipReport': {}},
                     '4': {'industryReport': {}, 'marineReport': {}, 'round': 0, 'shipReport': {}}}
        self.mySystem.setIntelReports()
        d2 = self.mySystem.intelReport['2']
        assert d2['industryReport'] == {'1': '2 - Basic Militia Fortress'}
    
    def testAddIndustry(self):
        """Add Industry to System,
        input->amount, industrytype"""
        assert self.mySystem.myIndustry['3'] == 0
        self.mySystem.addIndustry(4, '3')
        assert self.mySystem.myIndustry['3'] == 4
    
    def testRemoveIndustry(self):
        """Remove Industry from System
        input->amount, industrytype"""
        assert self.mySystem.myIndustry['3'] == 4
        self.mySystem.removeIndustry(3, '3')
        assert self.mySystem.myIndustry['3'] == 1
    
    def testGetAllConnections(self):
        """Get all System Connections as list of system IDs for movement only"""
        result = self.mySystem.getAllConnections()
        assert result == ['2', '15', '14']
    
    def testSetWarpConnections(self):
        """Set .warpGateSystems list of system IDs available for trade via warp gates"""
        assert self.mySystem.warpGateSystems == []
        self.myGalaxy.systems['15'].addIndustry(1, '40')
        self.mySystem.setWarpConnections()
        assert self.mySystem.warpGateSystems == []
        for i in range(1,20):
            self.myGalaxy.systems[str(i)].availWGC = 10
        self.mySystem.setWarpConnections()
        assert self.mySystem.warpGateSystems == ['11', '10', '12']
    
    def testModifyResource(self):
        """Set the specified Resource (AL, EC, IA) by the amount specified
        input->resourceName, amount"""
        self.mySystem.AL = 0
        myEmpire = self.myGalaxy.empires[self.mySystem.myEmpireID]
        myEmpire.AL = 0
        self.mySystem.modifyResource('AL', 100)
        assert self.mySystem.AL == 100
        assert myEmpire.AL == 100
    
    def testAddRegiment(self):
        """Add Regiments to system from Military Installations, DONE ON ROUND END
        input->amount, empireID, regimentTypeID"""
        assert self.myGalaxy.regiments == {}
        result = self.mySystem.addRegiment(3, '2', '2')
        assert result == 'ADDED 3 BRO-LNI-Marine-3 ON:%s' % self.mySystem.name
        assert len(self.myGalaxy.regiments.keys()) == 3
    
    def testRestoreRegiment(self):
        """Restore Regiment strength to 100%
        input->regimentID"""
        myRegiment = self.myGalaxy.regiments['3']
        myRegiment.strength = 50
        self.mySystem.restoreRegiment('3')
        assert myRegiment.strength == 100
    
    def testUpgradeRegiment(self):
        """Upgrade the Regiment to the new type"""
        myRegiment = self.myGalaxy.regiments['3']
        name = myRegiment.myRegimentData.name
        assert name == 'Light Nuclear Infantry'
        result = self.mySystem.upgradeRegiment('3')
        assert result == 'UPGRADED %s TO:Light Fusion Infantry ON:%s' % (name, self.mySystem.name)
        myRegiment = self.myGalaxy.regiments['3']
        assert myRegiment.myRegimentData.name == 'Light Fusion Infantry'
    
    def testRepairStarship(self):
        """Repair Starship to 100%
        input->shipID"""
        myShip = self.myGalaxy.ships['1']
        myShip.quads['fore'].components = {}
        myShip.setMyStatus()
        assert myShip.strength == 75.0
        
        assert myShip.empireID == '0'
        assert myShip.fromSystem == '56'
        mySystem = self.myGalaxy.systems['56']
        result = mySystem.repairStarship('1')
        assert result == 'REPAIRED %s to 100%s strength' % (myShip.name, '%')
        myShip2 = self.myGalaxy.ships['1']
        assert myShip2.strength == 100.0
    
    def testUpgradeStarship(self):
        """Upgrade the Starship to the new Design"""
        myShip = self.myGalaxy.ships['1']
        mySystem = self.myGalaxy.systems['56']
        assert myShip.designID in ('1','2')
        result = mySystem.upgradeStarship(myShip.id, '4')
        assert result == 'UPGRADED %s to TYPE = HCO4-Neutral-HCO' % myShip.myDesign.name
        myShip = self.myGalaxy.ships['1']
        assert myShip.designID == '4'
        assert myShip.name == 'HCO4-Neutral-HCO-1'
        
    def testValidateCityIndustry(self):
        """Can City Industry be changed"""
        result = self.mySystem.validateUpdateCityIndustry('9', [1,2,2,2])
        assert result == 'You are trying to update City Industry on System not owned by you'
        result = self.mySystem.validateUpdateCityIndustry(self.mySystem.myEmpireID, [1,2,2,2])
        assert result == 'You are trying to update City Industry where total cities(7) not equal to 10'
        result = result = self.mySystem.validateUpdateCityIndustry(self.mySystem.myEmpireID, [0,2,3,5])
        assert result == 1
    
    def testUpdateCityIndustry(self):
        """process city industry change of focus"""
        assert self.mySystem.cityIndustry == [10,0,0]
        result = self.mySystem.updateCityIndustry([2,3,5])
        assert result == 1
        assert self.mySystem.cityIndustry == [2,3,5]
    
    def testGetCurrentIndustryResourceValue(self):
        """Return total Resources by summing all industry from system"""
        result = self.mySystem.getCurrentIndustryResourceValue()
        assert self.mySystem.myIndustry == {'42': 0, '24': 0, '25': 0, '26': 0, 
                                            '27': 0, '20': 0, '21': 0, '22': 2, 
                                            '23': 0, '28': 0, '29': 0, '40': 0, 
                                            '41': 0, '1': 0, '3': 1, '2': 0, 
                                            '5': 0, '4': 0, '7': 0, '6': 0, 
                                            '9': 0, '8': 0, '13': 0, '12': 0, 
                                            '11': 0, '10': 0, '39': 0, '38': 0, 
                                            '15': 0, '14': 0, '17': 0, '16': 0, 
                                            '19': 0, '18': 0, '31': 0, '30': 0, 
                                            '37': 0, '36': 0, '35': 0, '34': 0, 
                                            '33': 0, '32': 0}
        assert result == [700.0, 0.0, 0.0]
        
    
    def testGenWealth(self):
        """Generate Wealth for System, done once each round, wealth consists of
        (AL)(EC)(IA) - these resources are added to the systems totals
        (prodAL, prodEC, prodIA) are all updated, these declare how much was
        generated for each resource by this system this round"""
        result = self.mySystem.genWealth()
        # this is assuming one intelligent alloy factory and IA=5,AL=2,EC=3 for city focus
        assert result == 'System:Vuseus Has Produced->(AL=52, EC=30, IA=25) Resources'
    
    def testResetCitiesUsed(self):
        """Reset the Cities Used attribute each turn"""
        self.mySystem.citiesUsed = 0
        self.mySystem.resetCitiesUsed()
        # assuming 2 fortresses and 1 intelligent alloy factory
        assert self.mySystem.citiesUsed == 5
        
        