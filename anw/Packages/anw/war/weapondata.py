# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weapondata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for ship weapons, weapon objects will reference this object
# ---------------------------------------------------------------------------
from anw.func import datatype

class WeaponData(datatype.DataType):
    """A Weapon Data object represents one type of Weapon in detail"""
    def __init__(self, args):
        # Attributes
        datatype.DataType.__init__(self, args)
        self.range = float() # weapon range
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
        self.setDescription()

    def setDescription(self):
        """Create the Description based on attributes given"""
        s = 'Range=%s' % self.range
        for (desc,attr) in [('Arc (Degrees)','arc'),
                            ('Damage','damage'),
                            ('Power Req','maxPower'),
                            ('Lock Time','maxLock'),
                            ('Components Req','numComps'),
                            ('Missile Type','missile'),
                            ('Speed','speed'),
                            ('Tracking (sec)','tracking'),
                            ('Direct Type','direct'),
                            ('Anti-Missle','AMS'),
                            ('Requires Ammo','ammo')]:
            value = getattr(self,attr)
            if value > 0 and value != '':
                if value == 1:
                    value = 'yes'
                s = s + '\n%s=%s' % (desc, value)
        self.description = s