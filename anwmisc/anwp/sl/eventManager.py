# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# eventManager.py
# Manages Game events on entity objects
# ---------------------------------------------------------------------------
from bisect import insort_right
from event import GameEvent

gEvents = []     # list of events sorted by time
gEventTimer = 0  # current event time (not the real time!)

def postEvent(gid, action, delay, args):
    """Post an event to be processed. insert in sorted order
    """
    event = GameEvent(gid, action, gEventTimer+delay, args)
    insort_right(gEvents, event)
    #print gid, action
    return event

def processEvents(interval):
    """process all of the pending events up to the current time.
    """
    global gEvents, gEventTimer
    gEventTimer += interval
    
    while len(gEvents) > 0:
        # grab the next event
        event = gEvents.pop(0)
        if event.callTime < gEventTimer:
            # time to call it
            event()
        else:
            # not time to call it, put it back in the list.
            gEvents.insert(0, event)
            break
    
def clearEventsFor(gid, action=''):
    """clear all pending events for a game object ID.
    """
    global gEvents
    if action == '':
        gEvents = filter(lambda event: event.gid != gid, gEvents)
    else:
        # clear all events for a certain gid of a certain action
        gEvents = filter(lambda event: not(event.gid == gid and event.action == action), gEvents)
