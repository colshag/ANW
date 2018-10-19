# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# valuebar.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Displays a Value in a loading bar fashion
# ---------------------------------------------------------------------------
import direct.directbase.DirectStart #aspect2d
from direct.gui.DirectGui import DirectWaitBar
from anw.func import globals
from anw.gui import rootsim, textonscreen
        
class ValueBar(rootsim.RootSim):
    """Display Value in a loading bar fashion"""
    def __init__(self, path, scale=0.5, extraText='', decimal=0, showOverValues=1):
        rootsim.RootSim.__init__(self, path, scale=scale)
        self.extraText = extraText
        self.currentValue = 0.0
        self.maxValue = 0.0
        self.barValue = 0.0
        self.scale = scale
        self.decimal = decimal
        self.showOverValues = showOverValues
        self.myText = ''
        self.textOverValue = None
        self.myBar = DirectWaitBar(text = '0 / 0', scale = scale, 
                                   frameColor = globals.colors['guiblue2'],
                                   borderWidth = (0.01, 0.01))
        self.barColor = globals.colors['guiblue1']
    
    def setMyPosition(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.myBar.setPos(x, y, z)
        if self.textOverValue != None:
            barWidth = self.myBar.getWidth()*self.scale/2.0
            barHeight = self.myBar.getHeight()*self.scale/3.0
            self.textOverValue.setMyPosition(x+barWidth, y, z-barHeight)
    
    def updateMyBar(self):
        """Update the bar on the screen"""
        self.myBar['text'] = self.myText
        self.myBar['value'] = self.barValue
        self.myBar['barColor'] = self.barColor
    
    def setMyValues(self, currentValue, maxValue):
        self.currentValue = float(currentValue)
        self.maxValue = float(maxValue)
        self.setMyText()
        self.setBarValue()
        self.updateMyBar()
        self.writeOverValue()
    
    def setMyText(self):
        if self.currentValue == self.maxValue:
            if self.decimal == 1:
                self.myText = '%s' % self.currentValue
            else:
                self.myText = '%d' % self.currentValue
        else:
            if self.decimal == 1:
                self.myText = '%s / %s' % (self.currentValue, self.maxValue)
            else:
                self.myText = '%d / %d' % (self.currentValue, self.maxValue)
        self.myText = self.myText + ' %s' % self.extraText
    
    def setBarValue(self):
        """Bar Value can only be from 0 to 100"""
        if self.currentValue > self.maxValue:
            self.barValue = 100
        elif self.maxValue == 0:
            self.barValue = 0
        else:
            self.barValue = (self.currentValue / self.maxValue) * 100.0
    
    def setColor(self, color):
        """set the text color = Vec4(red, green, blue, alpha)"""
        self.barColor = color
        self.updateMyBar()
    
    def writeOverValue(self):
        """Set the textOverValue text if currentValue > maxValue"""
        if self.showOverValues == 1:
            value = self.currentValue - self.maxValue
            self.clearText(self.textOverValue)
            if int(value) > 0:
                self.textOverValue = textonscreen.TextOnScreen(self.path, '+ %d' % value,
                                                               self.scale/8.0, parent=aspect2d)
                self.textOverValue.writeTextToScreen(self.x, self.y, self.z)
                self.textOverValue.setColor(globals.colors['guiyellow'])
    
    def clearText(self, textSim):
        """If sim exists remove from panda"""
        if textSim != None:
            textSim.destroy()
            textSim = None
    
    def destroy(self):
        """remove Bar, text"""
        self.myBar.destroy()
        self.clearText(self.textOverValue)

class IndustryBars(object):
    """Display industry values AL, EC, IA in valuebar format"""
    def __init__(self, path, currentList, maxList, x=0, y=0, 
                 scale=0.29, extraText='', title=''):
        self.path = path
        self.currentList = currentList
        self.maxList = maxList
        self.scale = scale
        self.x = x
        self.y = y
        self.extraText = extraText
        self.myTitle = None
        id = 0
        self.resourceNames = globals.resourceNames
        for resource in globals.resourceNames:
            if resource in ['AL','EC','IA']:
                color = globals.resourceColors[resource]
                self.createValueBar(id, color)
            id += 1
        if title != '':
            self.createTitle(title)
    
    def createTitle(self, title):
        """Create the Title Text Label"""
        self.myTitle = textonscreen.TextOnScreen(self.path, title, 0.025, 5, aspect2d)
        self.myTitle.writeTextToScreen(self.x-0.28, 0, self.y+0.04, 30)
        self.myTitle.setTitleStyle()
    
    def createValueBar(self, id, color):
        text = '  (%s %s)' % (self.resourceNames[id], self.extraText)
        setattr(self, 'industryBar%s' % id, ValueBar(self.path, scale=self.scale, extraText=text))
        myBar = getattr(self, 'industryBar%s' % id)
        barHeight = myBar.myBar.getHeight()*self.scale
        myBar.setMyValues(self.currentList[id], self.maxList[id])
        myBar.setMyPosition(self.x,0,self.y-barHeight*id)
        myBar.setColor(globals.colors[color])
    
    def updateValueBars(self, currentList):
        id = 0
        for value in currentList:
            try:
                myBar = getattr(self, 'industryBar%s' % id)
                myBar.setMyValues(value, self.maxList[id])
            except:
                pass
            id += 1
    
    def destroy(self):
        for id in range(4):
            try:
                myBar = getattr(self, 'industryBar%s' % id)
                myBar.destroy()
            except:
                pass
        if self.myTitle != None:
            self.myTitle.destroy()

class ColoredBars(IndustryBars):
    def __init__(self, path, currentList, maxList, x=0, y=0, 
                 scale=0.29, extraText='', title='', identBars=[]):
        self.identBars = identBars # eg. ['Mechanized', 'Artillery', 'Infantry']
        IndustryBars.__init__(self, path=path, currentList=currentList, maxList=maxList, x=x, y=y, 
                 scale=scale, extraText=extraText, title=title)
        
    def createValueBar(self, id, color):
        text = '  (%s %s)' % (self.identBars[id], self.extraText)
        setattr(self, 'industryBar%s' % id, ValueBar(self.path, scale=self.scale, extraText=text))
        myBar = getattr(self, 'industryBar%s' % id)
        barHeight = myBar.myBar.getHeight()*self.scale
        myBar.setMyValues(self.currentList[id], self.maxList[id])
        myBar.setMyPosition(self.x,0,self.y-barHeight*id)
        myBar.setColor(globals.colors[color])
    
            
class CostBars(IndustryBars):
    """Display Cost values CR, AL, EC, IA in valuebar format"""
    def __init__(self, path, currentList, maxList, x=0, y=0, 
                 scale=0.29, extraText='', title=''):
        self.path = path
        self.currentList = currentList
        self.maxList = maxList
        self.scale = scale
        self.x = x
        self.y = y
        self.extraText = extraText
        self.myTitle = None
        id = 0
        self.resourceNames = ['CR','AL','EC','IA']
        for resource in self.resourceNames:
            color = globals.resourceColors[resource]
            self.createValueBar(id, color)
            id += 1
        if title != '':
            self.createTitle(title)

if __name__ == "__main__":
    mediaPath = 'media'
    import direct.directbase.DirectStart
    myBar = ValueBar(mediaPath, scale=1)
    myBar.setMyValues(125.0, 200.0)
    myBar.setMyPosition(0,0,0)
    myBar.myBar.setSx(0.5)
    
    myBar2 = ValueBar(mediaPath, scale=0.5)
    myBar2.setMyValues(225.0, 200.0)
    myBar2.setMyPosition(-0.5,0,-0.8)
    
    myBar3 = ValueBar(mediaPath, scale=1)
    myBar3.setMyValues(225.0, 200.0)
    myBar3.setMyPosition(0,0,-0.3)
    
    
    myIndustryBar = IndustryBars(mediaPath,[10, 4, 20],[10,5,15], 0.5, 0.5, extraText='XX',title='Industry Bars:')
    myCostBars = CostBars(mediaPath, [1000,50,10,5],[1000,100,5,2], -0.5, 0.5, extraText='YY',title='Cost Bars:')
    run()
    