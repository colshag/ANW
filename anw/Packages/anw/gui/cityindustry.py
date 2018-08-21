# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# cityindustry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to modify the
# city industry focus for a system
# ---------------------------------------------------------------------------
import copy

from rootbutton import RootButton
from anw.gui import valuebar

class CityIndustry(RootButton):
    """The City Industry Gui"""
    def __init__(self, path, x=-1.25, y=0.19, name='', systemID='', cityIndustryList=[]):
        self.systemID = systemID
        self.cityIndustryList = copy.copy(cityIndustryList)
        self.initCityIndustryList = copy.copy(cityIndustryList)
        RootButton.__init__(self, path, x=x, y=y, name=name)
        self.allKeys = ['A','S','D','Z','X','C']
        self.scale = 0.29
        self.cityIndustryBars = None
        self.disableButtonTime = 0.5
        self.disableButtonIgnore = ['S', 'Z', 'X', 'C']
        self.resource = 0 # 0=AL,1=EC,2=IA
        self.pressButton('Z')
        self.disableButton('S')
        self.spareCities = 0
        self.totalCities = 0
        self.totalCityList = []
        self.setTotalCities()
        self.createCityIndustryBars()
    
    def setTotalCities(self):
        """Total Cities to work with"""
        for cities in self.cityIndustryList:
            self.totalCities += cities
        self.totalCityList = [self.totalCities,self.totalCities,self.totalCities]
    
    def setResource(self, resource):
        self.resource = resource
    
    def createCityIndustryBars(self):
        """These bars will show the proposed City Industry breakdown"""
        x = self.posInitX
        y = self.posInitY + 0.28
        self.createTitleCard('cityTitle1','Modify City Industry Focus:',
                         30,x-0.03, y+0.04)
        self.cityIndustryBars = valuebar.IndustryBars(self.path, self.cityIndustryList,
                                                      self.totalCityList,x=x+0.25,
                                                      y=y,scale=self.scale)
        self.myWidgets.append(self.cityIndustryBars)
    
    def setResourceValue(self, value):
        """Update cityIndustryList based on resource currently being changed"""
        if self.validateValue(value):
            if value < 0:
                self.spareCities += 1
            else:
                self.spareCities -=1
            self.cityIndustryList[self.resource] += value
            self.cityIndustryBars.updateValueBars(self.cityIndustryList)
            self.enableSubmit()
    
    def enableSubmit(self):
        """Make sure submit button only enabled when it should be"""
        if self.spareCities == 0 and self.cityIndustryList != self.initCityIndustryList:
            self.enableButton('S')
        else:
            self.disableButton('S')
    
    def validateValue(self, value):
        """Validate City can be added or removed from resource"""
        if value == 1:#trying to add a city to resource
            if self.spareCities < 1:
                return 0
            elif self.cityIndustryList[self.resource] == self.totalCities:
                return 0
            else:
                return 1
        else:#trying to remove a city from resource
            if self.cityIndustryList[self.resource] == 0:
                return 0
            else:
                return 1
    
    def acceptExtraKeys(self):
        """Allow mousewheel to increment/decrement value"""
        self.accept('wheel_up', self.pressButton, ['D'])
        self.accept('wheel_down', self.pressButton, ['A'])
    
    def createButtons(self):
        """Create all Buttons"""
        x = self.posInitX+0.01
        y = self.posInitY+0.01
        for key in ['Z','X','C']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
        self.x = 0
        self.y = 1
        for key in ['A','S','D']:
            buttonPosition = ((x+self.x*.10),0,(y+self.y*.10))
            self.createButton(key, buttonPosition)
            self.x += 1
                
    def pressS(self):
        """Submit value to server"""
        self.mode.changeCityIndustry(self.systemID, self.cityIndustryList)
        self.disableButton('S')
    
    def pressD(self):
        """Increment Value"""
        self.setResourceValue(1)
    
    def pressA(self):
        """Decrement Value"""
        self.setResourceValue(-1)
   
    def pressZ(self):
        """Set resource to AL"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.setResource(0)
    
    def pressX(self):
        """Set resource to EC"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.setResource(1)
    
    def pressC(self):
        """Set resource to IA"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.setResource(2)
    
if __name__ == "__main__":
    myCityIndustry = CityIndustry('media', -0.3, -0.17, 'city',systemID='1',
                              cityIndustryList=[10,0,0])
    run()