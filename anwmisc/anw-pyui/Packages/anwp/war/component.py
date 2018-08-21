# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# component.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a basic ship component
# ---------------------------------------------------------------------------
import anwp.func.root

class Component(anwp.func.root.Root):
    """A Ship Component contains the basic attributes of any ship component"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.type = str() # Given Component Type (id)
        self.weaponID = str() # if component part of weapon ID of weapon
        self.currentAmount = float() # current ammount of whatever for component
        self.currentHP = int() # current HP of component
        self.defaultAttributes = ('id', 'type', 'weaponID', 'currentAmount', 'currentHP')
        self.setAttributes(args)
        
        self.myQuad = None # Actual Quadrant object containing component
        self.myComponentData = None # Referenced
           
    def setMyQuad(self, quadObject):
        """Set the Quad Owner of this shipComponent"""
        self.myQuad = quadObject
        quadObject.components[self.id] = self
        self.myComponentData = self.myQuad.componentdata[self.type]
        if self.weaponID == '':
            self.currentHP = self.myComponentData.maxHP
        else:
            myWeapon = self.myQuad.weapons[self.weaponID]
            self.currentHP = myWeapon.myWeaponData.maxCompHP
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_component.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        