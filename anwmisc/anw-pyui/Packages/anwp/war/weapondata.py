# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weapondata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for ship weapons, weapon objects will reference this object
# ---------------------------------------------------------------------------
import anwp.func.datatype

class WeaponData(anwp.func.datatype.DataType):
    """A Weapon Data object represents one type of Weapon in detail"""
    def __init__(self, args):
        # Attributes
        anwp.func.datatype.DataType.__init__(self, args)
        self.range = int() # weapon range
        self.arc = int() # weapon arc in degrees (in each direction of weapon facing)
        self.damage = float() # weapon damage
        self.speed = int() # weapon speed (0 for direct weapons)
        self.tracking = float() # weapon tracking (number of seconds of tracking)
        self.maxLock = float() # time required to obtain lock (seconds)
        self.ammo = int() # does weapon require ammo (1=yes)
        self.maxPower = float() # power required to fire weapon
        self.ammoHP = int() # weapon ammo HP for missiles and drones
        self.maxCompHP = int() # total Hit Points of one component
        self.numComps = int() # number of components per weapon
        self.AMS = int() # Anti Missle System? (1=yes)
        self.missile = str() # '', 'impact', 'energy'
        self.direct = str() # '', 'impact', 'energy'
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'range', 'arc', 'damage', 'speed', 'tracking', 'maxLock',
                                  'ammo', 'maxPower', 'ammoHP', 'maxCompHP', 'numComps', 'AMS',
                                  'missile', 'direct')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_weapondata.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        
