# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mapmove.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to zoom in and out, select items and scroll around map
# ---------------------------------------------------------------------------
from anw.gui import rootbutton
from anw.func import funcs

class MapMove(rootbutton.RootButton):
    """Allows user to zoom in and out, select items and scroll around map"""
    def __init__(self, path, x, y, targets):
        rootbutton.RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.targets = targets
        self.allKeys = ['A','S','D','F','G','Z','X','C','V','B']
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = []
        self.createTitleCard('mapmovetitle','Map Scroll and Select:',
                             30,self.posInitX-0.03,self.posInitY+0.17)
        
    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode

    def appendTarget(self, target):
        self.targets.append(target)

    def createButtons(self):
        """Create all Buttons"""
        x = self.posInitX+0.01
        y = self.posInitY+0.01
        for key in ['Z','X','C','V','B']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1

        self.x = 0
        self.y = 1
        for key in ['A','S','D','F','G']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1

    def pressA(self):
        """Zoom Out"""
        self.mode.zoomOutCameraAmount(20)

    def pressS(self):
        """Scroll Up"""
        self.mode.panCameraUp(10)

    def pressD(self):
        """Zoom In"""
        self.mode.zoomInCameraAmount(20)

    def pressF(self):
        """Select Nearest"""
        nearestRange = 999999
        nearestTarget = None

        for myTarget in self.targets:
            if myTarget.alive == 1:
                range = funcs.getTargetRange(camera.getX(), camera.getZ(),
                                             myTarget.posX, myTarget.posY)
                if range < nearestRange:
                    nearestRange = range
                    nearestTarget = myTarget
        if nearestTarget != None:
            self.mode.shipsSelected(nearestTarget)

    def pressG(self):
        """Clear Selection"""
        self.mode.clearMouseSelection()

    def pressZ(self):
        """Scroll Left"""
        self.mode.panCameraLeft(10)

    def pressX(self):
        """Scroll Down"""
        self.mode.panCameraDown(10)

    def pressC(self):
        """Scroll Right"""
        self.mode.panCameraRight(10)

    def pressV(self):
        """Select Leftmost"""
        nearestRange = 999999
        nearestTarget = None

        for myTarget in self.targets:
            x1 = round(camera.getX(),2)
            x2 = round(myTarget.posX,2)
            if myTarget.alive == 1 and x2 < x1 and myTarget != self.mode.shipSelected:
                range = funcs.getTargetRange(camera.getX(), 0, myTarget.posX, 0)
                if range < nearestRange:
                    nearestRange = range
                    nearestTarget = myTarget
        if nearestTarget != None:
            self.mode.shipsSelected(nearestTarget)

    def pressB(self):
        """Select Rightmost"""
        nearestRange = 999999
        nearestTarget = None

        for myTarget in self.targets:
            x1 = round(camera.getX(),2)
            x2 = round(myTarget.posX,2)
            if myTarget.alive == 1 and x2 > x1 and myTarget != self.mode.shipSelected:
                range = funcs.getTargetRange(x1, 0, x2, 0)
                if range < nearestRange:
                    nearestRange = range
                    nearestTarget = myTarget
        if nearestTarget != None:
            self.mode.shipsSelected(nearestTarget)

if __name__ == "__main__":
    myGui = MapMove('media', 0, 0)
    run()