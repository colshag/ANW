# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# traderoute.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# A Trade Route displays the trade information between two systems
# ---------------------------------------------------------------------------
from anw.gui import rootsim, textonscreen
from anw.func import funcs, globals
        
class TradeRoute(rootsim.RootSim):
    """A Trade Route displays the trade information between two systems"""
    def __init__(self, path, tradeRouteDict, fromSystemDict, toSystemDict, extraTradeRoute):
        self.tradeRouteDict = tradeRouteDict
        self.fromSystemDict = fromSystemDict
        self.toSystemDict = toSystemDict
        self.extraTradeRoute = extraTradeRoute
        self.id = tradeRouteDict['id']
        rootsim.RootSim.__init__(self, path, texture=tradeRouteDict['imageFile'], 
                           type='plane', transparent=1, scale=1)
        self.glow = 1
        self.textWarpReq = None
        self.x1 = fromSystemDict['x']
        self.z1 = fromSystemDict['y']
        self.x2 = toSystemDict['x']
        self.z2 = toSystemDict['y']
        self.x = 0.0
        self.z = 0.0
        self.y = 20.2
        self.width = 0.5
        self.height = 2
        self.angle = funcs.getRelativeAngle(self.x1, self.z1, self.x2, self.z2)
        self.setMyXZ()
        self.createMySim()
    
    def setMyXZ(self):
        """Set the x and z attributes based on if it uses warp gates or not"""
        if self.tradeRouteDict['warpReq'] == 0:
            self.x = (self.x1+self.x2)/2
            self.z = (self.z1+self.z2)/2
        else:
            (self.x, self.z) = funcs.findOffset(self.x1, self.z1, self.angle, 2)
    
    def writeWarpReq(self, x, z):
        """Display the warp required for this trade route"""
        if self.tradeRouteDict['warpReq'] > 0:
            text = 'WARP = %d' % self.tradeRouteDict['warpReq']
            self.textWarpReq = textonscreen.TextOnScreen(self.path, text, 0.15, font=5)
            self.textWarpReq.writeTextToScreen(x, self.y, z, wordwrap=20)
            self.textWarpReq.setColor(globals.colors['guiwhite'])
            self.myWidgets.append(self.textWarpReq)
            
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.reSize()
        self.setPos()
        self.rotate()
    
    def destroy(self):
        """Remove the traderoute from game"""
        self.sim.removeNode()
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
        self.clearText(self.textWarpReq)
        
    def setOffsetPosition(self):
        """Offset the route based on its angle"""
        for i in range(self.extraTradeRoute):
            (self.x,self.z) = funcs.findOffset(self.x, self.z, self.angle+90, 0.25)
        self.setPos()
        self.writeResources()
    
    def writeResources(self):
        """Display any available resources"""
        (x,z) = funcs.findOffset(self.x, self.z, self.angle+90, 0.5)
        self.resourceCount = 0
        if self.tradeRouteDict['type'] == 'GEN':
            (self.tradeRouteDict['AL'],
             self.tradeRouteDict['EC'],
             self.tradeRouteDict['IA']) = self.mode.systems[self.tradeRouteDict['fromSystem']].getGenResources()
        for resource in ['AL','EC','IA']:
            value = self.tradeRouteDict[resource]

            if value > 0:
                myMethod = getattr(self, 'write%s' % resource)
                myMethod(x-0.45, self.y, z-0.1*self.resourceCount, value)
                self.resourceCount += 1
        self.writeWarpReq(x-0.45, z-0.1*self.resourceCount)
        self.mode.enableScrollWheelZoom = 1
    
    def refreshResources(self):
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
        self.clearText(self.textWarpReq)
        self.writeResources()