# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# guibase.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the base gui class for all ANW gui frames
# ---------------------------------------------------------------------------
import pyui
import anwp.func.funcs
import anwp.func.globals

class BaseFrame(pyui.widgets.Frame):
    """The GuiBase is a Frame that contains basic Gui Functions and Characteristics
       common to all ANW Frames"""
    def __init__(self, mode, x, y, w, h, title):
        pyui.widgets.Frame.__init__(self, x, y, w, h, title)
        self.mode = mode
        try:
            self.mode.panels.append(self)
        except:
            pass
    
    def close(self):
        """Destroy the Frame"""
        self.destroy()
        
    def setPanel(self, panel):
        """Set the panel for this frame"""
        self.panel = panel
        self.replacePanel(self.panel)
    
    def frameResize(self, w, h):
        """dont allow resizing"""
        return

    def frameMove(self, x, y):
        """dont allow moving"""
        return

    def frameClose(self):
        """dont allow closing"""
        return

class BaseInfoFrame(BaseFrame):
    """The BaseInfoFrame is a frame that gives information about a game entity
    The Frame resides on the Right side of the display and changes as entities are
    Moused Over.  This class captures common sizing requirements of these frames"""
    def __init__(self, mode, app, title, left=1):
        self.width = 400 # 4 across
        self.app = app
        self.currentID = 0
        try:
            self.simImagePath = app.simImagePath
        except:
            self.simImagePath = ''
        try:
            self.height = app.height - mode.mainMenu.height - mode.mainFooter.height - 20 #variable down
        except:
            self.height = app.height - 100
        x = (app.width - self.width*left - 10*(left-1))
        try:
            y = (mode.mainMenu.height) + 10
        except:
            y = 30
        BaseFrame.__init__(self, mode, x, y, self.width, self.height, title)
        # play default sound
        try:
            self.app.playSound('select1')
        except:
            pass

class BasePanel(pyui.widgets.Panel):
    """The Gui BasePanel is a panel that contains basic Gui Panel Functions common to
       all ANW Panels"""
    def __init__(self, frame):
        pyui.widgets.Panel.__init__(self)
        self.frame = frame
        self.descLength = 25 # maximum length of description dicts
        self.testDict = {'1': '1', '2':'2', '10': '10', '3': '3', '4':'4', '5':'5', '6':'6', '7':'7', '8':'8', '9':'9', '11':'11', '12':'12', '13':'13', '14':'14', '15':'15', '16':'16', '17':'17', '18':'18', '19':'19', '20':'20'}
        self.testImagePath = '../../../Client/images/'
        self.testAmount = 888
        self.setImagePath()
        
        # resource images
        self.symbolEC = '%ssymbol_ec.png' % self.imagePath
        self.symbolIA = '%ssymbol_ia.png' % self.imagePath
        self.symbolAL = '%ssymbol_al.png' % self.imagePath
        self.symbolCR = '%ssymbol_cr.png' % self.imagePath
    
    def buildAvail(self, availDict):
        """Calculate what is available for selection"""
        d = {}
        availList = availDict.keys()
        availList = anwp.func.funcs.sortStringList(availList)
        for ID in availList:
            myObj = availDict[ID]
            try:
                if self.frame.mode.game.myTech[myObj.techReq]['complete'] == 1:
                    d[ID] = '%s-%s' % (myObj.abr, myObj.name)
            except:
                pass
        return d
    
    def buildOrders(self, n, x, title, height=4, width=1):
        """Build the default orders listbox and label with a cancel orders button"""
        self.lbl = pyui.widgets.Label(text=title, type=1)
        self.addChild(self.lbl, (0, n, 4*width, 1))
        self.lstOrders = pyui.widgets.ListBox(self.onOrderSelected, None, 100, 100, 1)
        self.addChild(self.lstOrders, (0, n+1, 4*width, height+x))
        self.btnCancelOrder = pyui.widgets.Button('Cancel Order', self.onCancelOrder)
        self.addChild(self.btnCancelOrder, (0, n+height+1+x, 2*width, 1))
        self.btnSelectAllOrders = pyui.widgets.Button('Select All', self.onAllOrders)
        self.addChild(self.btnSelectAllOrders, (2*width, n+height+1+x, 2*width, 1))
    
    def buildResources(self, n, title='', width=1, prefix='', includeList=['CR', 'AL', 'EC', 'IA']):
        """Many gui panels require a Resource breakdown, this will generate the standar Resources"""
        if title <> '':
            self.lblTitle = pyui.widgets.Label(text=title, type=1)
            self.addChild(self.lblTitle, (0, n, 4*width, 1))
            n = n+1
        i = 0
        for resource in includeList:
            # build pictures
            symbol = getattr(self, 'symbol%s' % resource)
            name = 'pct%s' % resource
            setattr(self, name, pyui.widgets.Picture(symbol))
            myPicture = getattr(self, name)
            self.addChild(myPicture, (i*width, n, width, 1))
            # build labels
            name = 'lblTotal%s%s' % (resource,prefix)
            setattr(self, name, pyui.widgets.Label('0', type=1))
            myLabel = getattr(self, name)
            self.addChild(myLabel, (i*width, n+1, width, 1))
            # color the labels
            if resource == 'CR':
                myLabel.setColor(anwp.func.globals.colors['green'])
            elif resource == 'AL':
                myLabel.setColor(anwp.func.globals.colors['blue'])
            elif resource == 'EC':
                myLabel.setColor(anwp.func.globals.colors['yellow'])
            elif resource == 'IA':
                myLabel.setColor(anwp.func.globals.colors['red'])
            i += 1
        
    def onAllOrders(self, item):
        """Select All Orders"""
        for key in self.lstOrders.dSelected.keys():
            self.lstOrders.dSelected[key] = 1
        self.lstOrders.setDirty()
        self.enableButtons(self.lstOrders, [self.btnCancelOrder])
        
    def onExit(self, item):
        """Exit the Program"""
        self.frame.mode.exitGame()
    
    def setStats(self, n, attrList):
        """Set Stats for panel based on list"""
        i = 0
        for item in attrList:
            self.lbl = pyui.widgets.Label(item)
            self.addChild(self.lbl, (0,n+i,2,1))
            setattr(self, 'lbl%d' % i, pyui.widgets.Label('0', type=2))
            myLabel = getattr(self, 'lbl%d' % i)
            self.addChild(myLabel, (2,n+i,2,1))
            i += 1
        self.statNum = i-1
    
    def onCancel(self, item):
        """Close Frame, do not exit Program"""
        self.frame.destroy()
    
    def setImagePath(self):
        """Set the image Path for Panel"""
        try:
            self.imagePath = self.frame.app.genImagePath
        except:
            self.imagePath = self.testImagePath
    
    def panelMsgBox(self, messageText):
        """Create a message for the user"""
        import msgbox
        self.frame.mode.msgBox = msgbox.MessageBox(self.frame.mode, self.frame.mode.game.app, self.frame.mode.name, messageText)
        self.frame.mode.panels.append(self.frame.mode.msgBox)
    
    def populateListbox(self, lstBox, dataDict):
        """Take data Dictionary and populate a listbox"""
        lstBox.clearAllItems()
        list = dataDict.keys()
        if anwp.func.funcs.sortStringList(list) == -1:
            list = dataDict.keys()
            list.sort()
        for key in list:
            lstBox.addItem(dataDict[key], key)
    
    def enableButtons(self, myListBox, buttonList):
        """Enable Buttons if List has selected items, buttonList = names of buttons"""
        enableButtons = 0
        if len(myListBox.getMultiSelectedItems()) > 0:
            enableButtons = 1
            
        for myButton in buttonList:
            if enableButtons == 1:
                myButton.enable()
            else:
                myButton.disable()

class BaseWindow(pyui.base.Window):
    """The Gui BaseWindow contains the basic Gui functions for ANW Windows"""
    def __init__(self, mode, x, y, w, h):
        pyui.base.Window.__init__(self, x, y, w, h)
        self.mode = mode
        try:
            self.mode.panels.append(self)
        except:
            pass
    
    def setPanel(self, panel):
        """Set the panel for this window"""
        self.panel = panel
        self.replacePanel(self.panel)
        
    def draw(self, renderer):
        """Override draw window so that we use theme for window"""
        """Draws to the actual frame if the renderer requires it.
        """
        if not self.show:
            return
        self.hitList = pyui.desktop.getTheme().drawWindow( (0,0,self.width, self.height))
        self._panel.draw(renderer)

    