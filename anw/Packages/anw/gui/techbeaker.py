# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# techbeaker.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The techbeaker represents one research object in tech mode
# ---------------------------------------------------------------------------
import direct.directbase.DirectStart
from anw.gui import textonscreen, rootsim
from anw.func import globals
        
class TechBeaker(rootsim.RootSim):
    """A Tech Beaker displays technology information to player in tech mode"""
    def __init__(self, path, myTech, myGame):
        rootsim.RootSim.__init__(self, path, 'tech')
        self.myTech = myTech
        self.myGame = myGame
        self.currentTechOrder = 0
        self.id = myTech.id
        self.textName = None
        self.textCurrent = None
        self.textRequired = None
        self.textOrder = None
        self.textPreTech = None
        self.clickable = 0
        self.x = myTech.x
        self.z = myTech.y
        self.preTechs = myTech.preTechs
        self.preTechNum = myTech.preTechNum
        self.y = 20
        self.scale = 1
        self.glow = 0
        self.createMySim()
    
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.setPos()
        self.writeName()
        self.writeTechValues()
        self.setMySimStatus()
        self.writePreTech()
    
    def destroy(self):
        """Remove the beaker from game"""
        self.sim.removeNode()
        self.clearText(self.textName)
        self.clearText(self.textCurrent)
        self.clearText(self.textRequired)
        self.clearText(self.textOrder)
        self.clearText(self.textPreTech)
    
    def writeName(self):
        """Write the tech name"""
        self.textName = textonscreen.TextOnScreen(self.path, self.myTech.name, 0.25, font=1)
        self.textName.writeTextToScreen(self.x-0.5, self.y-0.1, self.z-0.7,wordwrap=10)
    
    def writeTechValues(self):
        """Write the tech current and required values onto beaker"""
        self.textCurrent = textonscreen.TextOnScreen(self.path, str(self.myTech.currentPoints), 0.2)
        self.textCurrent.writeTextToScreen(self.x-0.25, self.y-0.1, self.z-0.1)
        self.textRequired = textonscreen.TextOnScreen(self.path, str(self.myTech.requiredPoints), 0.2)
        self.textRequired.writeTextToScreen(self.x-0.25, self.y-0.1, self.z-0.3)
    
    def writeCurrentOrder(self):
        """Write the current tech orders for this technology"""
        if self.currentTechOrder != 0:
            self.clearText(self.textOrder)
            self.textOrder = textonscreen.TextOnScreen(self.path, str(self.currentTechOrder), 0.4)
            self.textOrder.writeTextToScreen(self.x -0.65, self.y-0.1, self.z+0.2)
            self.textOrder.setColor(globals.colors['guiyellow'])
    
    def writePreTech(self):
        """Only Write the minimum pre techs required if its not all of them"""
        if len(self.preTechs) > self.preTechNum:
            self.textPreTech = textonscreen.TextOnScreen(self.path, 'P:%s' % self.preTechNum, 0.2)
            self.textPreTech.writeTextToScreen(self.x+0.2, self.y-0.1, self.z+0.23)
            self.textPreTech.setColor(globals.colors['guiwhite'])
    
    def setMySimStatus(self):
        """Set Sim color based on Tech researched"""
        if self.myTech.complete == 1:
            self.setSimGreen()
        elif self.myTech.currentPoints > 0:
            self.setSimYellow()
        elif self.isMyPreTechsResearched() == 1:
            self.setSimCyan()
        else:
            self.setSimRed()
    
    def isMyPreTechsResearched(self):
        """Check if my pre-tech techs are researched"""
        num = 0
        for id in self.myTech.preTechs:
            preTech = self.myGame.myTech[id]
            if preTech.complete == 1:
                num += 1
        if num < self.myTech.preTechNum:
            return 0
        return 1
    
    def setSimCyan(self):
        """Sim is can be Researched, but hasn't yet, should be cyan"""
        self.sim.setColor(globals.colors['cyan'])
        self.textName.setColor(globals.colors['cyan'])
        self.textCurrent.setColor(globals.colors['guiyellow'])
        self.textRequired.setColor(globals.colors['black'])
        self.clickable = 1
    
    def setSimGreen(self):
        """Sim is Researched, should be green"""
        self.sim.setColor(globals.colors['guigreen'])
        self.textName.setColor(globals.colors['guigreen'])
        self.textCurrent.setColor(globals.colors['guiblue2'])
        self.textRequired.setColor(globals.colors['guiblue2'])
        self.clickable = 0
    
    def setSimRed(self):
        """Sim has no research, and cannot be researched yet, should be red"""
        self.sim.setColor(globals.colors['guired'])
        self.textName.setColor(globals.colors['guired'])
        self.textCurrent.setColor(globals.colors['guiyellow'])
        self.textRequired.setColor(globals.colors['guiwhite'])
        self.clickable = 0
    
    def setSimYellow(self):
        """Sim has some research, should be yellow"""
        self.sim.setColor(globals.colors['guiyellow'])
        self.textName.setColor(globals.colors['guiyellow'])
        self.textCurrent.setColor(globals.colors['dkgreen'])
        self.textRequired.setColor(globals.colors['guiblue2'])
        self.clickable = 1
    
    def getMaxValue(self, techAvailable):
        """Return the max value of tech that can be added"""
        maxValue = self.myTech.requiredPoints - self.myTech.currentPoints - self.currentTechOrder
        if maxValue > techAvailable:
            maxValue = techAvailable
        return maxValue
    
    def getMinValue(self):
        """Return th emin value of tech that can be added"""
        minValue = self.currentTechOrder * -1
        return minValue
    
    def setCurrentTechOrder(self):
        """Parse through all tech orders and retreive any already set for this technology"""
        myTechOrdersDict = self.game.myEmpire['techOrders']
        myOrderID = '%s-%d' % (self.id, self.game.currentRound)
        if myOrderID in myTechOrdersDict.keys():
            myOrder = myTechOrdersDict[myOrderID]
            self.currentTechOrder = int(myOrder['value'])
            self.writeCurrentOrder()
        else:
            self.clearCurrentOrder()
    
    def clearCurrentOrder(self):
        """Clear the current order from beaker"""
        self.currentTechOrder = 0
        self.clearText(self.textOrder)
        
if __name__ == "__main__":
    from anw.war import tech
    mediaPath = 'media'
    myTech1 = tech.Tech({'name':'Test Technology Test', 'x':0, 'y':0, 'complete':1,
              'currentPoints':200, 'requiredPoints':200, 'id':'1', 'preTechNum':1, 'preTechs':['1','2']})
    testBeaker1 = TechBeaker(mediaPath, myTech1)
    myTech2 = tech.Tech({'name':'Test Technology Test', 'x':0, 'y':2, 'complete':0,
              'currentPoints':100, 'requiredPoints':200, 'id':'2', 'preTechNum':1, 'preTechs':['1','2']})
    testBeaker2 = TechBeaker(mediaPath, myTech2)
    myTech3 = tech.Tech({'name':'Test Technology Test', 'x':0, 'y':4, 'complete':0,
              'currentPoints':0, 'requiredPoints':200, 'id':'3', 'preTechNum':1, 'preTechs':['1','2']})
    testBeaker3 = TechBeaker(mediaPath, myTech3)
    run()