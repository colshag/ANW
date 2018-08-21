# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# componentdata.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a data container for ship components, component objects will reference this object
# ---------------------------------------------------------------------------
from anw.func import datatype

class ComponentData(datatype.DataType):
    """A Component Data object represents one type of Component in detail"""
    def __init__(self, args):
        # Attributes
        datatype.DataType.__init__(self, args)
        self.maxAmmo = int() # max amount of weapon ammo
        self.explosive = int() # 1=yes, component will explode (> 1 = damage, 1=ammo amount*weapon damage)
        self.assault = int() # marine assault capacity
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
                                  'maxAmmo', 'explosive', 'assault', 'engine', 'rotate', 'power', 'battery',
                                  'repair', 'target', 'radar', 'genSP', 'maxSP',
                                  'typeAP', 'maxAP', 'maxHP', 'mass','jamming')
        self.setAttributes(args)
        self.setDescription()
    
    def setDescription(self):
        """Create the Description based on attributes given"""
        s = 'Mass=%d' % self.mass
        for (desc,attr) in [('Thrust','engine'),
                            ('Rotation','rotate'),
                            ('Power Generation','power'),
                            ('Battery Power','battery'),
                            ('Targetting','target'),
                            ('Radar','radar'),
                            ('Jamming','jamming'),
                            ('Shield Generation','genSP'),
                            ('Shield Points','maxSP'),
                            ('Armor Points','maxAP'),
                            ('Armor Type','typeAP'),
                            ('Marine Assault','assault'),
                            ('Ship Construction','repair'),
                            ('Max Ammo','maxAmmo')]:
            value = getattr(self,attr)
            if value > 0 and value != '':
                s = s + '\n%s=%s' % (desc, value)
        self.description = s
