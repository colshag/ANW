# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# categories.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Stores all sim categories
# ---------------------------------------------------------------------------

class ClickableCategory(object):
    """Represents any category that can be clicked by the mouse"""
    def __init__(self, image, type):
        self.name = type
        self.mobile = 0
        self.collide = 1
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/%s.py' % type

class ClickableMobileCategory(object):
    """Represents any category that can be clicked by the mouse and can move"""
    def __init__(self, image, type):
        self.name = type
        self.mobile = 1
        self.collide = 1
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/%s.py' % type
        
class TradeRouteCategory(object):
    """A TradeRoute represents a trade route on the map"""
    def __init__(self, image):
        self.name = 'traderoute'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/traderoute.py'
    
class StaticCategory(object):
    """A Static Category represents a sim that does not move/rotate or become clicked by user"""
    def __init__(self, image, name):
        self.name = name
        self.mobile = 0
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/%s.py' % name

class SelectorCategory(object):
    """A Selector represents a Selection Object, 
    it pops up upon selecting something, size = 'small', 'big'"""
    def __init__(self, image, size):
        self.name = 'selector'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/selector_%s.py' % size

class ExplosionCategory(object):
    """An Explosion represents an Explosion in the simulator
    size = 'small', 'big'"""
    def __init__(self, image, size):
        self.name = 'explosion'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 2
        self.image = image
        self.source = '../Packages/anwp/sims/explosion_%s.py' % size
        
class DirectFireCategory(object):
    """A Direct Fire weapon shot"""
    def __init__(self, image, size):
        self.name = 'direct'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        if size == 'l':
            self.life = 0.5
        elif size == 'm':
            self.life = 1
        else:
            self.life = 1.5
        self.image = image
        self.source = '../Packages/anwp/sims/direct_%s.py' % size
     
class WeaponArcCategory(object):
    """A Weapon Arc"""
    def __init__(self, image, type):
        self.name = 'weaponarc'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/weaparc_%s.py' % type
        
class ShipCategory(object):
    """A Ship represents a Star Ship in the simulator
    shiphull = 'eca', 'sct', etc..."""
    def __init__(self, image, shiphull):
        self.name = 'ship'
        self.mobile = 1
        self.collide = 1
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/%s.py' % shiphull

class MissileCategory(object):
    """A Missile represents a Missile in the simulator
    size = 'l', 'm', 'h'
    type = 1(missile) 2(photon)"""
    def __init__(self, image, size, type):
        self.name = 'missile'
        self.mobile = 1
        self.collide = 1
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/missile%d_%s.py' % (type,size)

class JunkCategory(object):
    """A Junk represents a shrapnel in the simulator
    type = num"""
    def __init__(self, image, num):
        self.name = 'junk'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/junk%d.py' % (num)

class CaptainCategory(object):
    """A Drone represents a Captain image in the simulator"""
    def __init__(self, image):
        self.name = 'captain'
        self.mobile = 1
        self.collide = 0
        self.threshold = 0
        self.life = 0
        self.image = image
        self.source = '../Packages/anwp/sims/captain.py'
