# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# game.py
# a generic game class
# ---------------------------------------------------------------------------
import pyui

import datamanager
import world

class Game:
    """A game.
    """
    def __init__(self, displayWidth, displayHeight, dataModule = None):
        self.mode = None        
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        pyui.desktop.getRenderer().setBackMethod(self.draw)
        self.events = []
        self.paused = 0
        
        # initialize data
        self.dm = datamanager.DataManager()
        if dataModule:
            dataModule.initialize(self.dm)

        # create the world
        self.world = world.World(displayWidth, displayHeight)
        
    def update(self, interval):
        if self.paused == 1:
            return 1
        result = self.world.update(interval)
        if self.mode:
            self.mode.update(interval, self.world)
        self.processEvents()
        return result

    def draw(self):
        if self.mode:
            self.mode.draw()
        
    def enterMode(self, newMode):
        if self.mode:
            print "Exiting mode:", self.mode.name
            self.mode.exitMode()
        self.mode = newMode
        print "Entering mode:", newMode.name        
        self.mode.enterMode()

    def setWorld(self, newWorld):
        if self.world:
            self.world.removeAll()
        self.world = newWorld

    def postEvent(self, action, target, *args):
        """Post an event to the event queue to be
        processed at the end of the frame.
        """
        event = GameEvent(action, target, args)
        self.events.append( event )

    def processEvents(self):
        """process all of the pending events.
        """
        for event in self.events:
            event.invoke()
        self.events = []

    def togglePause(self):
        if self.paused:
            self.paused = 0
        else:
            self.paused = 1
        
class GameEvent:
    """A game events that is invoked on an object.
    """
    def __init__(self, action, target, args):
        self.action = action
        self.target = target
        self.args = args
        self.meth = getattr(self.target, "event_%s" % self.action)

    def invoke(self):
        """Execute the event's action on the target."""
        if self.meth:
            return apply(self.meth, self.args)
        


        
