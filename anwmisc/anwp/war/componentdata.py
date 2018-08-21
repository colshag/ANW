# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# componentdata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for ship components, component objects will reference this object
# ---------------------------------------------------------------------------
import anwp.func.datatype

class ComponentData(anwp.func.datatype.DataType):
    """A Component Data object represents one type of Component in detail"""
    def __init__(self, args):
        # Attributes
        anwp.func.datatype.DataType.__init__(self, args)
        self.maxAmmo = int() # max amount of weapon ammo
        self.explosive = int() # 1=yes, component will explode (> 1 = damage, 1=ammo amount*weapon damage)
        self.storage = int() # marines that can be stored
        self.engine = float() # engine thrust
        self.rotate = float() # rotation thrust
        self.power = int() # Power generation
        self.battery = int() # battery storage
        self.repair = int() # repair amount
        self.target = int() # targetting factor
        self.radar = int() # radar factor
        self.genSP = int() # shield regen factor
        self.maxSP = int() # max shield points
        self.typeAP = str() # armor type: '', 'impact', 'energy'
        self.maxAP = int() # max armor points
        self.maxHP = int() # max hit points of component
        self.mass = float() # component mass
        self.jamming = int() # jamming factor
        self.defaultAttributes = ('id', 'name', 'abr', 'costCR', 'costAL',
                                  'costEC', 'costIA', 'techReq', 'description',
                                  'maxAmmo', 'explosive', 'storage', 'engine', 'rotate', 'power', 'battery',
                                  'repair', 'target', 'radar', 'genSP', 'maxSP',
                                  'typeAP', 'maxAP', 'maxHP', 'mass','jamming')
        self.setAttributes(args)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_componentdata.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        