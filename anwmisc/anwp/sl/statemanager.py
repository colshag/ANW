# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# statemanager.py
# Game State Management
# ---------------------------------------------------------------------------
import pyui

from entity import Entity

class StateException(Exception):
    pass

class StateManager:
    """ I keep the set of global states and layers. Instances
    of me are responsible for tracking states of actors.
    """
    layers = {}
    
    def __init__(self, actor):
        self.actor = actor
        self.currentStates = {}
        self.updateTimes = {}

    def setInitialState(self, stateName, layerName):
        """Set the initial state of a layer.
        """
        layer = StateManager.layers.get(layerName, None)
        if layer:
            state = layer.get(stateName)
            if state:
                interval = state.enter(self.actor)
                self.currentStates[layerName] = state
                self.updateTimes[layerName] = pyui.readTimer() + interval
                return 1
        raise StateException("No state %s or layer %s" % (stateName, layerName) )
            
    def setInput(self, input, layerName = None):
        """Send an input event to a layer.
        """
        if layerName == None:
            # try each of the current states
            for key in self.currentStates.keys():
                state = self.currentStates[key]
                newStateName = state.inputs.get(input)
                if newStateName:
                    return self.gotoState(newStateName, key)
            return

        # use the specified layer / currentState
        currentState = self.currentStates.get(layerName)
        if not currentState:
            raise StateException("No layer %s" % layerName)
        newStateName = currentState.inputs.get(input)
        if newStateName:
            return self.gotoState(newStateName, layerName)

    def gotoState(self, newStateName, layerName):
        """Set a layer to a state.
        """
        layer = StateManager.layers.get(layerName)
        if not layer:
            raise StateException("No layer %s" % layerName) 
        currentState = self.currentStates.get(layerName)
        if not currentState:
            raise StateException("No curreState for layer  %s" % layerName)
        newState = layer.get(newStateName, None)
        if not newState:
            raise StateException("New state %s doesnt exist" % newStateName)                        
        currentState.leave(self.actor)
        self.currentStates[layerName] = newState
        interval = newState.enter(self.actor)
        self.updateTimes[layerName] = pyui.readTimer() + interval
        return 1

    def getState(self, layerName):
        """Get the state name for a layer.
        """
        state = self.currentStates.get(layerName)
        return state.name

    def updateStates(self):
        now = pyui.readTimer()
        for layerName, updateTime in self.updateTimes.items():
            if now >= updateTime:
                interval = self.currentStates[layerName].update(self.actor)
                self.updateTimes[layerName] = now + interval
            
class SimActor(Entity):
    """an entity that is able to move in a controlled way
    in the physical simulation.
    """
    def __init__(self, stateManager, category, drawCallback = None):
        Entity.__init__(self, category, drawCallback)
        self.stateManager = stateManager

    def setInitialState(self, stateName, layerName):
        self.stateManager.setInitialState(stateName, layerName)
        
    def setInput(self, input, layerName = None):
        return self.stateManager.setInput(input, layerName)

    def gotoState(self, stateName, layerName):
        return self.stateManager.gotoState(stateName, layerName)

    def getState(self, layerName):
        return self.stateManager.getState(layerName)
    
    def update(self, interval, world):
        self.stateManager.updateStates()
        return Entity.update(self, interval, world)
