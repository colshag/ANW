# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# regimentinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays Design Informaiton
# ---------------------------------------------------------------------------
import string

from anw.gui import rootbutton, textonscreen
from anw.func import globals

class RegimentInfo(rootbutton.RootButton):
    """Describe Regiment"""
    def __init__(self, path, empireID, myRegiment, myRegimentData, x, y):
        self.empireID = empireID
        self.myRegimentData = myRegimentData
        self.myRegiment = myRegiment
        self.color1 = globals.empires[int(self.empireID)]['color1']
        self.color2 = globals.empires[int(self.empireID)]['color2']
        rootbutton.RootButton.__init__(self, path, x, y, '')
        self.sim = None
        self.textPower = None
        self.textVsMilitia = None
        self.textVsInfantry = None
        self.textVsMechanized = None
        self.textVsArtillery = None
        self.textCR = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        self.textGlory = None
        self.textRank = None
        self.yOffset = 0.0
        self.createTitleCard('regimentname', '(%s) Summary:' % self.myRegimentData.name,
                         30,self.posInitX,self.posInitY)
        self.createSim()
    
    def createSim(self, x=0.1, y=-0.1):
        """Create myData Sim Picture"""
        if self.sim == None:
            self.sim = loader.loadModelCopy('%s/plane' % self.path)
            self.sim.setScale(0.15)
            self.sim.reparentTo(aspect2d)
            self.sim.setTransparency(1)
            tex = loader.loadTexture('%s/logo.png' % self.path)
            self.sim.setTexture(tex, 0)
            self.sim.setPos(self.posInitX+x, 0, self.posInitY+y)
            self.myWidgets.append(self.sim)
    
    def writeAttributes(self):
        """For Each Attribute given display"""
        self.yOffset -= 0.02
        self.writeAttribute(self.textCR, 1, globals.resourceColors['CR'],'%d' % self.myRegimentData.costCR, x=0.22)
        self.writeAttribute(self.textAL, 1, globals.resourceColors['AL'],'%d' % self.myRegimentData.costAL, x=0.22)
        self.writeAttribute(self.textEC, 1, globals.resourceColors['EC'],'%d' % self.myRegimentData.costEC, x=0.22)
        self.writeAttribute(self.textIA, 1, globals.resourceColors['IA'],'%d' % self.myRegimentData.costIA, x=0.22)
        
        if self.myRegiment != None:
            self.writeAttribute(self.textRank, self.myRegiment['rank'], 'guiyellow','Rank = %s' % self.myRegiment['rank'])
            self.writeAttribute(self.textGlory, self.myRegiment['glory'], 'guiwhite','Regiment Glory = %d' % self.myRegiment['glory'])
        self.writeAttribute(self.textPower, self.myRegimentData.power, 'guigreen','Power Rating = %.2f' % self.myRegimentData.power)
        self.writeAttribute(self.textVsMilitia, self.myRegimentData.L, 'guigreen','Vs Militia = %.2f' % self.myRegimentData.L)
        self.writeAttribute(self.textVsInfantry, self.myRegimentData.I, 'guigreen','Vs Infantry = %.2f' % self.myRegimentData.I)
        self.writeAttribute(self.textVsMechanized, self.myRegimentData.M, 'guigreen','Vs Mechanized = %.2f' % self.myRegimentData.M)
        self.writeAttribute(self.textVsArtillery, self.myRegimentData.A, 'guigreen','Vs Artillery = %.2f' % self.myRegimentData.A)
        
    
    def writeAttribute(self, myAttribute, value, color, text, x=0):
        if value > 0:
            self.yOffset -= 0.04
            myAttribute = textonscreen.TextOnScreen(self.path, text,
                                                    scale=0.03, font=5, 
                                                    parent=aspect2d)
            myAttribute.writeTextToScreen(self.posInitX+x, 0, self.posInitY+self.yOffset, 40)
            myAttribute.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            myAttribute.setColor(globals.colors[color])
            self.myWidgets.append(myAttribute)
               