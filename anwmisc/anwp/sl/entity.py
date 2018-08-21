# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# entity.py
# Contains the entity object
# ---------------------------------------------------------------------------
from sim import SimObject
import eventManager
import entityManager
from observer import Observable

class Entity(SimObject, Observable):
    """Game Entity.
    """
    def __init__(self, category, drawCallback = None):
        SimObject.__init__(self, category, drawCallback)
        Observable.__init__(self)
        self.gid = entityManager.nextGID(self)

    def assignGID(self, newGID):
        entityManager.assignGID(newGID, self, self.gid)
        
    def isSame(self, other):
        if isinstance(other, Entity):
            return self.gid == other.gid
        else:
            return 0
        
    def postEvent(self, action, delay, *args):
        return eventManager.postEvent(self.gid, action, delay ,args)

    def clearEvents(self):
        eventManager.clearEventsFor(self.gid)
        
    def update(self, interval, world):
        if self.dirty:
            self.notify()
        return SimObject.update(self, interval, world)
    



