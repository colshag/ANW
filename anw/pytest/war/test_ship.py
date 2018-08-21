# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# test_ship.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a starship
# ---------------------------------------------------------------------------
import os
from anw.admin import generate
from anw.aw import galaxy
from anw.func import globals
from anw.func.misc import near

class TestShip(object):
    
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
    
    def testGetCurrentResourceValue(self):
        """Return current value including repairs required in (AL, EC, IA)"""
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.name == 'HCO1-Neutral-HCO-2':
                result = myShip.getCurrentResourceValue()
                assert result == (890.0, 464.0, 160.0)
    
    def testGetMyValue(self):
        """Return the (valueBV, valueCR, valueAL, valueEC, valueIA) in a tuple
        valueBV = credit conversion of ship"""
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.name == 'HCO1-Neutral-HCO-2':
                result = myShip.getMyValue()
                i = 0
                for item in (33.88, 9300.0, 890.0, 464.0, 160.0):
                    assert near(item, result[i])
                    i += 1
    
    ##def testGetNearestTarget(self):
        ##"""Look for nearest target of target type"""
        ##myShip = self.myGalaxy.ships['1']
        ##myShip.myGalaxy = shipsimulator.ShipSimulator(None,None)
        ##result = myShip.getNearestTarget()
        ##assert result == None
        ##myTarget = self.myGalaxy.ships['2']
        ##myShip.targets.append('2')
        ##result = myShip.getNearestTarget()
        ##assert result == myTarget
    
    def testWeaponGetMyXY(self):
        """Return the current (x,y) of this weapon in simulation"""
        myShip = self.myGalaxy.ships['1']
        myWeapon = myShip.activeWeapons[0]
        myWeapon.distance = 4
        testGroup = {(0,4):0.0,
                     (4,0.0):90.0,
                     (0.0,-4):180.0,
                     (-4,0.0):270.0
                     }
        for (x,y),angle in testGroup.iteritems():
            myWeapon.direction = angle
            (resultX,resultY) = myWeapon.getMyXY()
            assert near(x, resultX, 0.00001)
            assert near(y, resultY, 0.00001)
    
    def testShipDesignGetMyBattleValue(self):
        """Return Battle Value of Ship Design"""
        myDesign = self.myEmpire.shipDesigns['1']
        myCarrierShipDesign = self.myEmpire.shipDesigns['8']
        result = myDesign.getMyBattleValue()
        assert near(33.88, result)
        result = myCarrierShipDesign.getMyBattleValue()
        assert near(130.98, result)
            
    def testShipDesignGetMyDesign(self):
        """Return the ship design attributes in the form of (hullID, compDict, weaponDict)"""
        myDesign = self.myEmpire.shipDesigns['1']
        myCarrierShipDesign = self.myEmpire.shipDesigns['8']
        result = myDesign.getMyDesign()
        assert result == ('HCO1-Neutral-HCO',
                        '4',
                        {'aft': ['25', '4', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1', 'W1'],
                         'fore': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7'],
                         'port': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7'],
                         'star': ['1', '1', '1', '25', '4', '4', '45', '7', '7', '7']},
                        {'aft-1': {'facing': 0.0, 'id': '1', 'type': '24'}})
        result = myCarrierShipDesign.getMyDesign()
        assert result == ('HCA8-Neutral-HCA',
                            '14',
                             {'aft': ['3',
          '3',
          '3',
          '6',
          '9',
          '9',
          '9',
          '9',
          '9',
          '9',
          '9',
          '9',
          'W1',
          'W1',
          'W1',
          'W1'],
  'fore': ['W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W2',
           'W2',
           'W2',
           'W2',
           'W2',
           'W2',
           'W2',
           'W2'],
  'port': ['3',
           '3',
           '3',
           '3',
           '3',
           '3',
           '6',
           '6',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1'],
  'star': ['3',
           '6',
           '9',
           '9',
           '9',
           '9',
           '9',
           '9',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1',
           'W1']},
 {'aft-1': {'facing': 90.0, 'id': '1', 'type': '12'},
  'fore-1': {'dronedesign': '1', 'facing': 90.0, 'id': '1', 'type': '43'},
  'fore-2': {'dronedesign': '1', 'facing': 90.0, 'id': '2', 'type': '43'},
  'port-1': {'dronedesign': '1', 'facing': 90.0, 'id': '1', 'type': '43'},
  'star-1': {'dronedesign': '1', 'facing': 90.0, 'id': '1', 'type': '43'}})

        
        
        