# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# war library
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# event.py
# Game events on entity objects
# ---------------------------------------------------------------------------
import anwp.sl.event

class GameInterEvent(anwp.sl.event.GameEvent):
    """A game event that is invoked on an object.
    This event uses the iteration of each frame for timing purposes instead of
    a time based function.  This allows for exact event firings for replay purposes.
    """
    def __init__(self, gid, action, callTic, args):
        self.gid = gid        
        self.action = action
        self.callTic = callTic
        self.args = args

    def __cmp__(self, other):
        return cmp(self.callTic, other.callTic)