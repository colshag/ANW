# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# designinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays Design Informaiton
# ---------------------------------------------------------------------------
import string

from anw.gui import rootbutton, textonscreen
from anw.func import globals

class DesignInfo(rootbutton.RootButton):
    """Describe Ship Design"""
    def __init__(self, path, empireID, myDesign, x, y):
        self.empireID = empireID
        self.myDesign = myDesign
        self.color1 = globals.empires[int(self.empireID)]['color1']
        self.color2 = globals.empires[int(self.empireID)]['color2']
        rootbutton.RootButton.__init__(self, path, x, y, '')
        self.sim = None
        self.textMass = None
        self.textPower = None
        self.textBattery = None
        self.textThrust = None
        self.textRotation = None
        self.textRadar = None
        self.textJamming = None
        self.textRepair = None
        self.textAssault = None
        self.textTotalAMSPower = None
        self.textTotalWeapPower = None
        self.textAMSFireRate = None
        self.textWeapFireRate = None
        self.textCR = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        self.textBV = None
        self.textHasAllTech = None
        self.textTargetPref = None
        self.yOffset = 0.0
        self.createTitleCard('designdescription', '(%s) Summary:' % myDesign.name,
                         30,self.posInitX,self.posInitY)
        self.createSim()
    
    def createSim(self, x=0.1, y=-0.1):
        """Create myData Sim Picture"""
        name = '%s_%s' % (string.lower(self.myDesign.myShipHull.abr), self.empireID)
        if self.sim == None:
            self.sim = loader.loadModelCopy('%s/plane' % self.path)
            self.sim.setScale(0.15)
            self.sim.reparentTo(aspect2d)
            self.sim.setTransparency(1)
            tex = loader.loadTexture('%s/%s.png' % (self.path, name))
            self.sim.setTexture(tex, 0)
            self.sim.setPos(self.posInitX+x, 0, self.posInitY+y)
            self.myWidgets.append(self.sim)
        else:
            tex = loader.loadTexture('%s/%s.png' % (self.path, name))
            self.sim.setTexture(tex, 0)
    
    def writeAttributes(self):
        """For Each Attribute given display"""
        self.yOffset -= 0.02
        self.writeAttribute(self.textCR, 1, globals.resourceColors['CR'],'%d' % self.myDesign.costCR, x=0.22)
        self.writeAttribute(self.textAL, 1, globals.resourceColors['AL'],'%d' % self.myDesign.costAL, x=0.22)
        self.writeAttribute(self.textEC, 1, globals.resourceColors['EC'],'%d' % self.myDesign.costEC, x=0.22)
        self.writeAttribute(self.textIA, 1, globals.resourceColors['IA'],'%d' % self.myDesign.costIA, x=0.22)
        
        self.writeAttribute(self.textThrust, self.myDesign.accel, 'guiwhite','Thrust = %s,  Rotate = %s' % (self.displayMax(self.myDesign.accel, 5.0), self.displayMax(self.myDesign.rotation, 60.0) ))
        self.writeAttribute(self.textPower, self.myDesign.maxPower, 'guigreen','Power = %d,  Battery = %d' % (self.myDesign.maxPower,self.myDesign.maxBattery))
        self.writeAttribute(self.textTotalWeapPower, self.myDesign.totalWeapPower, 'guigreen','Weap Power = %d' % self.myDesign.totalWeapPower)
        self.writeAttribute(self.textAMSFireRate, self.myDesign.amsFireRate, 'guigreen','AMS Fire Rate = %.2f' % self.myDesign.amsFireRate)
        self.writeAttribute(self.textWeapFireRate, self.myDesign.weapFireRate, 'guigreen','Weap Fire Rate = %.2f' % self.myDesign.weapFireRate)
        
        self.writeAttribute(self.textRadar, self.myDesign.radar, 'guiyellow','Radar = %d,  Jamming = %d' % (self.myDesign.radar,self.myDesign.jamming))
        self.writeAttribute(self.textRepair, self.myDesign.repair, 'guiyellow','Repair = %d' % self.myDesign.repair)
        self.writeAttribute(self.textAssault, self.myDesign.maxAssault, 'guiyellow','Marine Assault Strength = %d' % self.myDesign.maxAssault)
        if self.myDesign.myShipHull.abr not in globals.targetPreference.keys():
            text = 'Ship Targets nearest enemy ship'
        else:
            text = 'Ship seeks out: %s' % globals.targetPrefDisplay[self.myDesign.myShipHull.abr]
        self.writeAttribute(self.textTargetPref, 1, 'guiblue1',text)
        
        if self.myDesign.hasAllTech == 0:
            self.writeAttribute(self.textHasAllTech, 1, 'guired','Ship Past Tech Level')
        else:
            self.writeAttribute(self.textHasAllTech, 1, 'guigreen','Ship Within Tech Level')
                    
    def displayMax(self, value, max):
        if value >= max:
            return 'MAX (%s)' % value
        else:
            return value
    
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
               