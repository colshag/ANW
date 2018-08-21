# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# event.py
# Game events on entity objects
# ---------------------------------------------------------------------------
import entityManager

class GameEvent:
    """A game event that is invoked on an object.
    """
    def __init__(self, gid, action, callTime, args):
        self.gid = gid        
        self.action = action
        self.callTime = callTime
        self.args = args

    def __cmp__(self, other):
        return cmp(self.callTime, other.callTime)
    
    def __call__(self):
        """Execute the event's action on the target."""
        target = entityManager.lookupGID(self.gid)
        if target:
            meth = getattr(target, "event_%s" % self.action)
            if meth:
                return apply(meth, self.args)
        else:
            print "ERROR: unable to find object <%d>" % self.gid
