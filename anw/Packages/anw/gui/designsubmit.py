# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# designsubmit.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This displays ship designs left, simulations left, and allows user
# to submit designs
# ---------------------------------------------------------------------------
from pandac.PandaModules import TextNode
from anw.gui import rootbutton
from anw.func import globals, funcs

class DesignSubmit(rootbutton.RootButton):
    """Allows User to submit Designs"""
    def __init__(self, path, mode, myDesign, x, z):
        self.myDesign = myDesign
        self.designsLeft = mode.game.myEmpire['designsLeft']
        self.simulationsLeft = mode.game.myEmpire['simulationsLeft']
        rootbutton.RootButton.__init__(self, path, x=x, y=z, name='design')
        self.mode = mode
        self.scale = 0.25
        self.disableButtonTime = -1
        self.disableButtonIgnore = []
        self.myTitle2 = None
        self.myText2 = None
        x = self.posInitX-0.03
        z = self.posInitY+0.30
        self.createTitleCard('scrollTitle1','Remaining Ship Designs this Round:',
                         12,x,z)
        self.createTextCard(x+0.33,z-0.04)
        self.createTitleCard2('scrollTitle2','Remaining Ship Simulation Points:',
                         12,x,z-0.12)
        self.createTextCard2(x+0.33,z-0.16)
        self.actualDesignID = ''
        self.isDroneDesign = 0
        self.enableSubmit()

    def createTitleCard2(self, name, text, wordwrap, x, z, scale=0.025):
        """Default Title label for gui controls"""
        self.myTitle2 = TextNode(name)
        self.myTitle2.setFont(self.font)
        self.myTitle2.setText(text)
        self.myTitle2.setWordwrap(wordwrap)
        self.myTitle2.setTextColor(globals.colors['guiwhite'])
        self.myTitle2.setCardColor(globals.colors['guiblue3'])
        self.myTitle2.setFrameColor(globals.colors['guiblue2'])
        self.myTitle2.setFrameAsMargin(.3, .5, .5, .5)
        self.myTitle2.setFrameLineWidth(3)
        self.myTitle2.setCardAsMargin(.3, .5, .5, .5)
        textNodePath = aspect2d.attachNewNode(self.myTitle2)
        textNodePath.setScale(scale)
        textNodePath.setPos(x, 0, z)
        self.myWidgets.append(textNodePath)

    def createTextCard(self, x, z):
        """Text Card stored current Scroll Value"""
        self.myText = TextNode('scrollValue')
        funcs.setZeroToText(self.myText, self.designsLeft)
        self.enableSubmit()
        self.myText.setFont(self.font)
        self.myText.setCardColor(globals.colors['guiblue3'])
        self.myText.setFrameColor(globals.colors['guiblue2'])
        self.myText.setFrameAsMargin(0, 0, 0, 0)
        self.myText.setFrameLineWidth(3)
        self.myText.setCardAsMargin(.1, .1, .1, .1)
        textNodePath = aspect2d.attachNewNode(self.myText)
        textNodePath.setScale(0.09)
        textNodePath.setPos(x, 0, z)
        self.myWidgets.append(textNodePath)

    def createTextCard2(self, x, z):
        """Text Card For Simulations Left"""
        self.myText2 = TextNode('scrollValue2')
        funcs.setZeroToText(self.myText2, self.simulationsLeft)
        self.enableSubmit()
        self.myText2.setFont(self.font)
        self.myText2.setCardColor(globals.colors['guiblue3'])
        self.myText2.setFrameColor(globals.colors['guiblue2'])
        self.myText2.setFrameAsMargin(0, 0, 0, 0)
        self.myText2.setFrameLineWidth(3)
        self.myText2.setCardAsMargin(.1, .1, .1, .1)
        textNodePath = aspect2d.attachNewNode(self.myText2)
        textNodePath.setScale(0.09)
        textNodePath.setPos(x, 0, z)
        self.myWidgets.append(textNodePath)
    
    def enableSubmit(self):
        """setup enabled buttons"""
        self.disableButton('submitdesign')
        self.enableSimulateSubmit()
        self.enableRemoveDesign()

    def enableDesignSubmit(self):
        """Enable the submit design button"""
        if self.designsLeft > 0 and self.mode.designName != '':
            self.enableButton('submitdesign')
        else:
            self.disableButton('submitdesign')
        self.enableSimulateSubmit()
    
    def enableRemoveDesign(self):
        """Enable the Remove Design"""
        if self.mode.selectedShipHull.aftQuadInfo == None:
            self.isDroneDesign = 1
            self.enableRemoveDroneDesign()
        else:
            self.isDroneDesign = 0
            self.enableRemoveShipDesign()
    
    def enableRemoveDroneDesign(self):
        for designID, realDesign in self.mode.game.droneDesignObjects.iteritems():
            if self.myDesign.name == realDesign.name:
                self.enableButton('removedesign')
                self.actualDesignID = designID
                return
        self.disableButton('removedesign')
            
    def enableRemoveShipDesign(self):
        for designID, realDesign in self.mode.game.shipDesignObjects.iteritems():
            if self.myDesign.name == realDesign.name:
                self.enableButton('removedesign')
                self.actualDesignID = designID
                return
        self.disableButton('removedesign')
    
    def enableSimulateSubmit(self):
        if (self.simulationsLeft > 0 and 'aft' in self.myDesign.quads.keys() and 
            self.isValidForSimulation() == 1):
            self.enableButton('simulatedesign')
        else:
            self.disableButton('simulatedesign')
    
    def isValidForSimulation(self):
        """Is the design valid for a simulation"""
        for position, myQuad in self.myDesign.quads.iteritems():
            if myQuad.components != {}:
                return 1
        return 0
            
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['submitdesign','simulatedesign','removedesign','cancel']:
            buttonPosition = (self.posInitX+0.21,0,(self.posInitY+0.08+y*.09))
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.045)
            y -= 0.5

    def presssubmitdesign(self):
        """Submit Design to Server"""
        self.mode.submitDesign(self.myDesign)

    def presssimulatedesign(self):
        """Simulate Ship Design"""
        self.mode.selectedShipHull.clearSimulateDesign()
        self.mode.selectedShipHull.createAllDesignsList()
    
    def pressremovedesign(self):
        """Remove Ship Design"""
        if self.isDroneDesign == 1:
            self.mode.submitRemoveDroneDesign(self.actualDesignID)
        else:
            self.mode.submitRemoveShipDesign(self.actualDesignID)
    
    def presscancel(self):
        """Cancel the Ship Design"""
        self.mode.resetMode()
            
    def pressX(self):
        pass
    
    def pressS(self):
        pass
    
    