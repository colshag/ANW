# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# techinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is an info panel that relates to any Tech object on the Tech Tree
# ---------------------------------------------------------------------------
import pyui
import guibase
import anwp.func.funcs

class TechInfoFrame(guibase.BaseInfoFrame):
    """Displays Tech Information"""  
    def __init__(self, mode, app, title='Technology Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(TechInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.techEntity = subject
        if self.techEntity.techID <> self.currentID:
            # different tech populate panel
            self.currentID = self.techEntity.techID
            self.setPanel(TechInfoPanel(self))
            self.panel.populate(self.techEntity.myTechDict)

class TechInfoPanel(guibase.BasePanel):
    """Panel for information about Techs on players tech tree:
    This would include detailed information about tech"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # tech Info
        self.pctTech = pyui.widgets.Picture('')
        self.addChild(self.pctTech, (0, 0, 1, 3))
        self.lstTechDesc = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstTechDesc, (1, 0, 3, 3))
        
        n = 4
        self.btnAdd = pyui.widgets.Button('Add', self.onAddResearch)
        self.addChild(self.btnAdd, (0, n, 1, 1))
        self.txtTechAmount = pyui.widgets.NumberEdit('', 4, None, 0)
        self.addChild(self.txtTechAmount, (1, n, 1, 1))
        self.lblResearch = pyui.widgets.Label(text=' Research Points', type=2)
        self.addChild(self.lblResearch, (2, n, 2, 1))
        
        # add research
        n = n+2
        self.lbl = pyui.widgets.Label(text='OR Add a Default Research of:', type=2)
        self.addChild(self.lbl, (0, n, 4, 1))
        num = 0
        for i in [1,5,10,25,50,75,100,200]:
            setattr(self, 'btnAddTech%d' % i, pyui.widgets.Button(str(i), self.onAddTech))
            myButton = getattr(self, 'btnAddTech%d' % i)
            self.addChild(myButton, (num-4*(num/4), n+(num/4)+1, 1, 1))
            num += 1
        
        # pretechs required
        n = n+4
        self.lblPreTech = pyui.widgets.Label(text='PRETECHS REQUIRED:', type=1)
        self.addChild(self.lblPreTech, (0, n, 3, 1))
        self.lstPreTech = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstPreTech, (0, n + 1, 4, 4))
        
        # tech enables
        n = n+6
        self.lblTechEnables = pyui.widgets.Label(text='THIS TECH ENABLES:', type=1)
        self.addChild(self.lblTechEnables, (0, n, 3, 1))
        self.lstTechEnables = pyui.widgets.ListBox(self.onEnableSelected, None)
        self.addChild(self.lstTechEnables, (0, n + 1, 4, 4))
        
        # tech Orders
        n = n+6+x
        self.buildOrders(n,x,'CURRENT RESEARCH ORDERS:')
        
        # pack widgets
        self.pack

    def populate(self, myTechDict):
        """Populate frame with new data"""
        self.myTechDict = myTechDict
        # disable buttons
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            myTechPict = '%s%s.png' % (self.frame.app.simImagePath, myTechDict['imageFile'])
            myOrders = self.buildTechOrderData(self.frame.mode.game.myEmpire['techOrders'])
            myPointsLeft = (myTechDict['requiredPoints'] - myTechDict['currentPoints']) / 2
            if myPointsLeft > self.frame.mode.game.myEmpire['rpAvail']:
                myPointsLeft = self.frame.mode.game.myEmpire['rpAvail']
        except:
            # this allows for testing panel outside game
            myTechPict = self.testImagePath + 'tech.png'
            myOrders = self.testDict
            myPointsLeft = 10
            
        myTechName = '%s: %d/%d' % (myTechDict['name'], myTechDict['currentPoints'], myTechDict['requiredPoints']) 
        myTechDesc = anwp.func.funcs.returnDictFromString(myTechDict['description'], self.descLength)
        myPreTech = {}
        for techID in myTechDict['preTechs']:
            tech = self.frame.app.game.myTech[techID]
            myPreTech[techID] = tech['name']
        myTechEnables = {}
        self.myTechEnableDesc = {}
        
        # tech Info
        self.pctTech.setFilename(myTechPict)
        self.frame.title = myTechName
        self.txtTechAmount.setText(str(myPointsLeft))
            
        self.populateListbox(self.lstTechDesc, myTechDesc)
        
        # pretechs required
        self.populateListbox(self.lstPreTech, myPreTech)
        
        # tech enables
        self.populateListbox(self.lstTechEnables, myTechEnables)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)
    
    def buildTechOrderData(self, dTechOrderData):
        """Take Tech Order Data from Server and Transform into Form Friendly Data"""
        d = {}
        for id, dTechOrder in dTechOrderData.iteritems():
            myTechDict = self.frame.mode.game.myTech[dTechOrder['type']]
            name = 'ADD %s:%s' % (dTechOrder['value'], myTechDict['name'])
            d[id] = name
        return d
    
    def onEnableSelected(self, item):
        pass
    
    def onAddTech(self, item):
        """Add a preset Tech amount"""
        self.frame.mode.addTechOrder(int(item.text), self.myTechDict['id'])
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.btnCancelOrder.enable()
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelTechOrder(self.lstOrders.getMultiSelectedItems(), self.frame.currentID)
    
    def onAddResearch(self, item):
        """Add Research to Tech"""
        self.frame.mode.addTechOrder(int(self.txtTechAmount.getValue()), self.myTechDict['id'])

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    myTech = {'name': 'Intelligent Shipyards', 'currentPoints': 0, 'imageFile': 'tech_red', 'y': 1800, 'id': '216', 'preTechs': ['216'], 'complete': 0, 'requiredPoints': 400, 'x': 300, 'preTechNum': 1, 'techAge': 3, 'description': 'Intelligent Shipyards'}
    pyui.init(width, height, 'p3d', 0, 'Testing Tech Info Panel')
    app = run.TestApplication(width, height)
    frame = TechInfoFrame(None, app)
    frame.panel.populate(myTech)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
