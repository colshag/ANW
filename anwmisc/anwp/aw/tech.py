# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# tech.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a technology
# ---------------------------------------------------------------------------
import anwp.func.root

class Tech(anwp.func.root.Root):
    """A Technology represents one technolgy type in the game.  Each Empire
    contains a dictionary of Technologies of varying types."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given Tech Name
        self.description = str() # Tech Description
        self.x = int() # x Coordinate of Tech on Tech Tree
        self.y = int() # y Coordinate of Tech on Tech Tree
        self.complete = int() # 0 for incomplete, 1 for complete
        self.preTechs = list() # List of ids of techs required to research this tech, item = system id
        self.preTechNum = int() # Number of preTechs Required
        self.requiredPoints = int() # Number of Required Tech Points (eg 100)
        self.currentPoints = int() # Currently Researched Tech Points
        self.techAge = int() # Age of Technology tech belongs to
        self.imageFile = str() # image file of Tech
        self.defaultAttributes = ('id', 'name', 'description', 'x', 'y', 'complete', 'preTechs',
                                  'preTechNum', 'requiredPoints', 'currentPoints', 'techAge', 'imageFile')
        self.setAttributes(args)
        
    def getImageFileName(self):
        """Generate the image filename depends on:
        - amount researched"""
        # decide color, red: no research, yellow: some, green: all
        color = 'red'
        if self.complete == 1:
            color = 'green'
        else:
            if self.currentPoints > 0:
                color = 'yellow'
                    
        # create image file
        self.imageFile = 'tech_%s' % color
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_tech.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        