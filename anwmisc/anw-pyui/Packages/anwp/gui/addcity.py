# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# addcity.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows a user to add a city to a system, or modify a city resource focus
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.globals

class AddCityFrame(guibase.BaseFrame):
    """Basic Add City Frame, requires position, passes data to Panel"""  
    def __init__(self, mode, app, title, cityList, systemID, systemName):
        self.app = app
        self.width = 320
        self.height = 420 # 14 * 30 down
        self.cityList = cityList
        self.systemID = systemID
        self.systemName = systemName
        x = (app.width - 2*self.width)
        try:
            y = (mode.mainMenu.height) + 20
        except:
            y = 40
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        if cityList == None:
            self.setPanel(AddCityPanel(self))            
        else:
            self.setPanel(ModifyCityPanel(self))

class AddCityPanel(guibase.BasePanel):
    """Add City Panel"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 13))
        
        resourceDict = {'CR':'CR - Credits', 'AL':'AL - Alloys', 'EC':'EC - Energy', 'IA':'IA - Arrays'}
        symbolCity = '%ssymbol_city.png' % self.imagePath
        
        cityName = 'New City'
        buttonName = 'Add City'

        # title section
        self.pctCity = pyui.widgets.Picture(symbolCity)
        self.addChild(self.pctCity, (0, 0, 3, 3))
        self.lblSystemName = pyui.widgets.Label(text='System: %s' % self.frame.systemName, type=1)
        self.addChild(self.lblSystemName, (3, 0, 5, 1))
        self.lblCityName = pyui.widgets.Label(text=cityName, type = 2)
        self.addChild(self.lblCityName, (3, 1, 5, 1))
        
        # create Listbox
        self.lblTitle = pyui.widgets.Label(text='CHOOSE RESOURCE FOCUS:', type=1)
        self.addChild(self.lblTitle, (0, 4, 8, 1))
        self.lstResources = pyui.widgets.ListBox(self.onSelected, None)
        self.addChild(self.lstResources, (0, 5, 8, 3))
        self.populateListbox(self.lstResources, resourceDict)
        
        # resource cost
        reqCR = anwp.func.globals.addCityResource['CR']
        reqAL = anwp.func.globals.addCityResource['AL']
        reqEC = anwp.func.globals.addCityResource['EC']
        reqIA = anwp.func.globals.addCityResource['IA']

        n = 9
        self.buildResources(n,'ADD ONE CITY COST:', 2)
        self.lblTotalCR.setText('%d' % (reqCR))
        self.lblTotalAL.setText('%d' % (reqAL))
        self.lblTotalEC.setText('%d' % (reqEC))
        self.lblTotalIA.setText('%d' % (reqIA))
        
        # create Buttons
        n = n + 3
        self.btnAddChangeCity = pyui.widgets.Button(buttonName, self.onButton)
        self.addChild(self.btnAddChangeCity, (0, n, 4, 1))
        self.btnAddChangeCity.disable()
        self.btnCancel = pyui.widgets.Button('Cancel', self.onCancel)
        self.addChild(self.btnCancel, (4, n , 4, 1))
        
        self.pack
    
    def onButton(self, item):
        """Send Add City Command to Empire Industry Orders"""
        self.frame.mode.addCity(self.selectedItemData, self.frame.systemID)    
    
    def onSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.selectedItemData = item.data
            print 'name=%s, data=%s' % (item.name, self.selectedItemData)
            self.btnAddChangeCity.enable()

class ModifyCityPanel(AddCityPanel):
    """Modify City Resource Panel"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.setLayout(pyui.layouts.TableLayoutManager(8, 13))
        
        resourceDict = {'CR':'CR - Credits', 'AL':'AL - Alloys', 'EC':'EC - Energy', 'IA':'IA - Arrays'}
        symbolCity = '%ssymbol_city.png' % self.imagePath
        
        if len(self.frame.cityList) > 5:
            cityName = 'Mulitple Cities'
        else:
            cityName = 'City %s' % str(self.frame.cityList)
        buttonName = 'Change City'
        
        # title section
        self.pctCity = pyui.widgets.Picture(symbolCity)
        self.addChild(self.pctCity, (0, 0, 3, 3))
        self.lblSystemName = pyui.widgets.Label(text='System: %s' % self.frame.systemName, type=1)
        self.addChild(self.lblSystemName, (3, 0, 5, 1))
        self.lblCityName = pyui.widgets.Label(text=cityName, type = 2)
        self.addChild(self.lblCityName, (3, 1, 5, 1))
        
        # create Listbox
        self.lblTitle = pyui.widgets.Label(text='CHOOSE RESOURCE FOCUS:', type=1)
        self.addChild(self.lblTitle, (0, 4, 8, 1))
        self.lstResources = pyui.widgets.ListBox(self.onSelected, None)
        self.addChild(self.lstResources, (0, 5, 8, 3))
        self.populateListbox(self.lstResources, resourceDict)
        
        # resource cost
        try:
            if self.frame.mode.game.currentRound > 1:
                reqCR = anwp.func.globals.updateCityResource['CR']
                reqAL = anwp.func.globals.updateCityResource['AL']
                reqEC = anwp.func.globals.updateCityResource['EC']
                reqIA = anwp.func.globals.updateCityResource['IA']
            else:
                reqCR = 0
                reqAL = 0
                reqEC = 0
                reqIA = 0
        except:
            reqCR = 0
            reqAL = 0
            reqEC = 0
            reqIA = 0

        n = 9
        self.buildResources(n,'MODIFY CITY COST (PER CITY):', 2)
        self.lblTotalCR.setText('%d' % (reqCR))
        self.lblTotalAL.setText('%d' % (reqAL))
        self.lblTotalEC.setText('%d' % (reqEC))
        self.lblTotalIA.setText('%d' % (reqIA))
        
        # create Buttons
        n = n + 3
        self.btnAddChangeCity = pyui.widgets.Button(buttonName, self.onButton)
        self.addChild(self.btnAddChangeCity, (0, n, 4, 1))
        self.btnAddChangeCity.disable()
        self.btnCancel = pyui.widgets.Button('Cancel', self.onCancel)
        self.addChild(self.btnCancel, (4, n , 4, 1))
        
        self.pack
        
    def onButton(self, item):
        """Send Modify City Command to Empire Industry Orders"""
        self.frame.mode.changeCity(self.selectedItemData, self.frame.cityList, self.frame.systemID)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing City Panel')
    app = run.TestApplication(width, height)
    ##frame = AddCityFrame(None, app, 'Add City', '0', '1', 'Colin')
    frame = AddCityFrame(None, app, 'Change City Resource', [11,20,14, 25,18], '1', 'Colin')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
