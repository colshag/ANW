# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# diplomacy.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a diplomatic state between two empires
# ---------------------------------------------------------------------------
from anw.func import root

class Diplomacy(root.Root):
    """A Diplomacy Represents a Diplomatic State between two Empires"""
    def __init__(self, args):
        # Attributes
        self.empireID = str() # represents the other empire id
        self.diplomacyID = int() # Given Diplomacy id
        self.myIntent = str() # 'none', 'increase', 'decrease'
        self.empireIntent = str() # 'none', 'increase', 'decrease'
        self.defaultAttributes = ('empireID', 'diplomacyID', 'myIntent', 'empireIntent')
        self.setAttributes(args)
        