# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# tech.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a technology
# ---------------------------------------------------------------------------
from anw.func import root

class Tech(root.Root):
    """A Technology represents one technolgy type in the game.  Each Empire
    contains a dictionary of Technologies of varying types."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given Tech Name
        self.description = str() # Tech Description
        self.x = float() # x Coordinate of Tech on Tech Tree
        self.y = float() # y Coordinate of Tech on Tech Tree
        self.complete = int() # 0 for incomplete, 1 for complete
        self.preTechs = list() # List of ids of techs required to research this tech, item = system id
        self.preTechNum = int() # Number of preTechs Required
        self.requiredPoints = int() # Number of Required Tech Points (eg 100)
        self.currentPoints = int() # Currently Researched Tech Points
        self.techAge = int() # Age of Technology tech belongs to
        self.defaultAttributes = ('id', 'name', 'description', 'x', 'y', 'complete', 'preTechs',
                                  'preTechNum', 'requiredPoints', 'currentPoints', 'techAge')
        self.setAttributes(args)
        