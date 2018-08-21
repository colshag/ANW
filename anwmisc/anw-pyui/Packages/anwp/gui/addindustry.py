# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# addindustry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel allows a user to add a industry to a system
# ---------------------------------------------------------------------------
import string

import pyui
import guibase
import anwp.func.funcs

class AddIndustryFrame(guibase.BaseFrame):
    """Basic Add City Frame, requires position, passes data to Panel"""  
    def __init__(self, mode, app, title, systemID):
        self.app = app
        self.width = 320
        self.height = 660 # 22 * 30 down
        self.systemID = systemID
        x = (app.width - 2*self.width)
        try:
            y = (mode.mainMenu.height) + 20
        except:
            y = 40
        guibase.BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        self.setPanel(AddIndustryPanel(self))

class AddIndustryPanel(guibase.BasePanel):
    """Panel that contains:
    Label
    Listbox
    Picture/Description Listbox
    Add Button
    Cancel Button
    """
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)        
        self.setLayout(pyui.layouts.TableLayoutManager(4, 22))
        self.amount = 1
        
        # set the available industry
        self.industryDict = self.buildIndustryAvailable()
        
        # choose industry section
        self.lblChooseInd = pyui.widgets.Label(text='INDUSTRY TYPE-CITIES REQ:', type=1)
        self.addChild(self.lblChooseInd, (0, 0, 4, 1))
        self.lstAvailInd = pyui.widgets.ListBox(self.onSelected, None)
        self.addChild(self.lstAvailInd, (0, 1, 4, 9))
        self.populateListbox(self.lstAvailInd, self.industryDict)
        
        # industry details
        n = 11
        self.lblDetails = pyui.widgets.Label(text='SELECTED INDUSTRY DETAILS:', type=1)
        self.addChild(self.lblDetails, (0, n, 4, 1))
        self.pctIndustry = pyui.widgets.Picture('')
        self.addChild(self.pctIndustry, (0, n+1, 1, 3))
        self.lstIndDesc = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstIndDesc, (1, n+1, 3, 3))
        
        # industry resource cost
        n = n + 5      
        self.buildResources(n,'SELECTED INDUSTRY COST:')
        
        # choose industry amount
        n = n + 3
        self.lblAmount = pyui.widgets.Label(text='CHOOSE INDUSTRY AMOUNT:', type=1)
        self.addChild(self.lblAmount, (0, n, 4, 1))
        self.slbAmount = pyui.widgets.SliderBar(None, 20)
        self.addChild(self.slbAmount, (0, n+1, 4, 1))
        
        # create Buttons
        n = n + 2
        self.btnAddIndustry = pyui.widgets.Button('Add Industry', self.onAddIndustry)
        self.addChild(self.btnAddIndustry, (0, n, 2, 1))
        self.btnAddIndustry.disable()
        self.btnCancel = pyui.widgets.Button('Cancel', self.onCancel)
        self.addChild(self.btnCancel, (2, n , 2, 1))
        
        self.pack
    
    def buildIndustryAvailable(self):
        """Take list of available industry and build a dict of industry available"""
        d = {}
        try:
            for indDataID in self.frame.mode.game.myEmpire['researchedIndustry']:
                name = '%s-%d' % (self.frame.mode.game.industrydata[indDataID]['name'],self.frame.mode.game.industrydata[indDataID]['cities'])
                d[indDataID] = name
            return d
        except:
            return self.testDict
    
    def onAddIndustry(self, item):
        """Send Add Industry Command to Empire Industry Orders"""
        self.frame.mode.addIndustry(self.slbAmount.position, self.selectedItemData, self.frame.systemID)
    
    def onSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.selectedItemName = item.name
            self.selectedItemData = item.data
            print 'name=%s, data=%s' % (self.selectedItemName, self.selectedItemData)
            self.populateIndustry(self.selectedItemData)
            self.btnAddIndustry.enable()
        
    def populateIndustry(self, industryDataID):
        """Populate Industry Data using industryDataID provided"""
        try:
            indData = self.frame.mode.game.industrydata[industryDataID]
            myIndustryPict = '%sind_%s.png' % (self.imagePath, string.lower(indData['abr']))
            myIndustryDesc = anwp.func.funcs.returnDictFromString(indData['description'], self.descLength)
            self.populateListbox(self.lstIndDesc, myIndustryDesc)
            self.pctIndustry.setFilename(myIndustryPict)
            self.lblTotalCR.setText('%d' % indData['costCR'])
            self.lblTotalAL.setText('%d' % indData['costAL'])
            self.lblTotalEC.setText('%d' % indData['costEC'])
            self.lblTotalIA.setText('%d' % indData['costIA'])
        except:
            self.frame.mode.modeMsgBox('addindustry->populateIndustry error')
            
def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Industry Panel')
    app = run.TestApplication(width, height)
    frame = AddIndustryFrame(None, app, 'Add Industry to System', '1')
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
