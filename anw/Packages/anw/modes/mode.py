# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mode.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the base mode class in ANW
# ---------------------------------------------------------------------------
import random
import types
import logging

from anw.func import globals
if globals.serverMode == 0:
    from pandac.PandaModules import Point2, Point3, Vec3, Vec4, BitMask32
    from pandac.PandaModules import PandaNode,NodePath, TextNode
    from direct.task import Task
    from pandac.PandaModules import CollisionTraverser,CollisionNode
    from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
    from pandac.PandaModules import Shader, ColorBlendAttrib
    import direct.directbase.DirectStart #camera
    from anw.gui import textonscreen, fadingtext, mainmenubuttons, line
    from direct.directtools.DirectGeometry import LineNodePath

class Mode(object):
    """This is the base Mode class"""
    def __init__(self, game):
        self.name = "MODE"
        self.guiMediaPath = '../Packages/anw/gui/media/'
        self.alive = 1
        self.enableMouseCamControl = 1
        self.enableScrollWheelZoom = 1
        self.canSelectFlags = {}
        self.messagePositions = []
        self.selectTypes = []
        self.gui = []
        self.sims = []
        self.game = game
        self.depth = 20.0
        self.zoomCameraDepth = 10.0
        self.zoomCameraOutDepth = -10.0
        self.zoomSpeed = 5
        self.panSpeed = 1.0
        self.runningTasks = []
        if globals.serverMode == 0:
            self.setMyBackground()
            camera.setHpr(0,0,0)
        self.mainmenu = None
        self.scrollSpeed = 0.1

        if globals.serverMode == 0:
            self.setMousePicker()
            self.setCameraPosition()
        
        self.selector = None
        self.selector2 = None
        
        self.log = logging.getLogger('mode')
        
        self.entryFocusList = ('anw.gui.mainmenubuttons','anw.gui.industryvalue',
                                'anw.gui.cityindustry','anw.gui.weapondirection',
                                'anw.gui.scrollvalue','anw.gui.shipdesignvalue',
                                'anw.gui.systemmenu','anw.gui.tradevalue',
                                'anw.gui.designmenu','anw.gui.shipyardmenu', 'anw.gui.mimenu',
                                'anw.gui.textentry', 'anw.gui.marketsystemsellvalue', 
                                'anw.gui.sendcreditsvalue')
    
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        log=logging.getLogger('mode')
        self.__dict__.update(dict)
        self.log=log
    
    def setMousePicker(self):
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)
        self.selectable = render.attachNewNode("selectable")

    def setCameraPosition(self):
        self.cameraPos = (camera.getX(), camera.getY(), camera.getZ())
        self.cameraMoving = 0
    
    def setCanSelectFlag(self, key):
        """Set the Flag"""
        self.clearAllCanSelectFlags()
        self.canSelectFlags[key] = 1
        
    def clearAllCanSelectFlags(self):
        """Clear any selection flags"""
        for key in self.canSelectFlags.keys():
            self.canSelectFlags[key] = 0
     
    def isAnyFlagSelected(self):
        """Return 1 if any flags are selected"""
        for key in self.canSelectFlags.keys():
            if self.canSelectFlags[key] == 1:
                return 1
        return 0
            
    def validateSelection(self):
        """Can something be selected right now"""
        if self.cameraMoving == 0:
            return 1
        else:
            return 0
        
    def removeMyGui(self, myGuiName):
        """Remove gui"""
        myGui = getattr(self, myGuiName)
        if myGui in self.gui:
            self.gui.remove(myGui)
        if myGui != None:
            myGui.destroy()
            setattr(self, myGuiName, None)
    
    def createMainMenu(self, key):
        self.mainmenu = mainmenubuttons.MainMenuButtons(self.guiMediaPath)
        self.mainmenu.setMyGame(self.game)
        self.mainmenu.setMyMode(self)
        self.mainmenu.enableLastButton(key)
        self.mainmenu.checkDisableButton(key)
        self.mainmenu.writeGameInfo()
        self.mainmenu.acceptSpaceBarKey()
        self.gui.append(self.mainmenu)
    
    def removeMainMenu(self):
        if self.mainmenu != None:
            self.mainmenu.destroyMe()
            self.mainmenu = None
    
    def centerCameraOnSim(self, sim):
        """Center the camera on the sim position"""
        self.game.app.disableMouseCamControl()
        camera.setPos(sim.getX(), camera.getY(), sim.getZ())
        camera.setHpr(0,0,0)
        if self.enableMouseCamControl == 1:
            self.game.app.enableMouseCamControl()
    
    def drawBox(self, x, y, width, height, color='guiblue1', lineWidth=0.15, glow=1):
        """Draw a box"""
        #LEFT
        myLine = line.Line(self.guiMediaPath,(x,y),(x,y+height), 'square_grey', lineWidth, glow)
        myLine.sim.setColor(globals.colors[color])
        self.gui.append(myLine)
        #TOP
        myLine = line.Line(self.guiMediaPath,(x,y+height),(x+width,y+height), 'square_grey', lineWidth, glow)
        myLine.sim.setColor(globals.colors[color])
        self.gui.append(myLine)
        #RIGHT
        myLine = line.Line(self.guiMediaPath,(x+width,y+height),(x+width,y), 'square_grey', lineWidth, glow)
        myLine.sim.setColor(globals.colors[color])
        self.gui.append(myLine)
        #BOTTOM
        myLine = line.Line(self.guiMediaPath,(x+width,y),(x,y), 'square_grey', lineWidth, glow)
        myLine.sim.setColor(globals.colors[color])
        self.gui.append(myLine)
    
    def stopCameraTasks(self):
        taskMgr.remove('zoomInCameraTask')
        taskMgr.remove('zoomOutCameraTask')
        self.cameraMoving = 0
        self.game.app.enableMouseCamControl()
        self.enableMouseCamControl=1
        
    def resetCamera(self):
        self.game.app.disableMouseCamControl()
        camera.setPos(self.cameraPos[0], self.zoomCameraOutDepth, self.cameraPos[2])
        # I don't really understand why this doesn't reset the view when having a planet selected and hitting spacebar?    
        camera.setHpr(0,0,0)

        if self.enableMouseCamControl == 1:
            self.game.app.enableMouseCamControl()
    
    def zoomInCamera(self):
        
        if camera.getY() <= self.zoomCameraDepth:
            self.game.app.disableMouseCamControl()
            taskMgr.add(self.zoomInCameraTask, 'zoomInCameraTask', extraArgs=[self.zoomCameraDepth])
            self.runningTasks.append('zoomInCameraTask')
    
    def zoomInCameraAmount(self, amount):
        """Zoom in Camera a certain amount specified"""
        depth = camera.getY()+amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.zoomInCameraTask, 'zoomInCameraTask', extraArgs=[depth])
        self.runningTasks.append('zoomInCameraTask')
    
    def zoomInCameraTask(self, depth):
        """Zoom in the camera until its at depth"""
        y = camera.getY()
        if y + 0.1 >= depth: # or y >= 8.0:  # TODO: tacking this on will mess with the design screen but prevents you from zooming in too close everywhere else.  
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            camera.setY(y)    
            return Task.done
        else:
            camera.setY(y+self.getZoomSpeed(y, depth))
            self.cameraMoving = 1
            return Task.cont
        
    def getZoomSpeed(self, y, depth):
        """Make Camera zoom in faster if camera is further away"""
        diff = depth-y
        return diff/5.0
    
    def zoomOutCamera(self):
        if camera.getY() >= self.zoomCameraOutDepth:
            self.game.app.disableMouseCamControl()
            taskMgr.add(self.zoomOutCameraTask, 'zoomOutCameraTask', extraArgs=[self.zoomCameraOutDepth])
            self.runningTasks.append('zoomOutCameraTask')
            
    def zoomOutCameraAmount(self, amount):
        """Zoom out Camera a certain amount sepecified"""
        depth = camera.getY()-amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.zoomOutCameraTask, 'zoomOutCameraTask', extraArgs=[depth])
        self.runningTasks.append('zoomOutCameraTask')
    
    def zoomOutCameraTask(self, depth):
        """Zoom out the camera until its at 0 Depth"""
        y = camera.getY()
        if y - 0.1 <= depth:
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            camera.setY(y)
            return Task.done
        else:
            camera.setY(y+self.getZoomSpeed(y, depth))
            self.cameraMoving = 1
            return Task.cont
    
    def panCameraLeft(self, amount):
        """Pan Camera"""
        pos = camera.getX()-amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.panCameraLeftTask, 'panCameraLeftTask', extraArgs=[pos])
        self.runningTasks.append('panCameraLeftTask')
    
    def panCameraLeftTask(self, pos):
        """pan the camera to new position"""
        x = camera.getX()
        if x <= pos:
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            return Task.done
        else:
            camera.setX(x-self.panSpeed)
            self.cameraMoving = 1
            return Task.cont

    def panCameraRight(self, amount):
        """Pan Camera"""
        pos = camera.getX()+amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.panCameraRightTask, 'panCameraRightTask', extraArgs=[pos])
        self.runningTasks.append('panCameraRightTask')
    
    def panCameraRightTask(self, pos):
        """pan the camera to new position"""
        x = camera.getX()
        if x >= pos:
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            return Task.done
        else:
            camera.setX(x+self.panSpeed)
            self.cameraMoving = 1
            return Task.cont
        
    def panCameraUp(self, amount):
        """Pan Camera"""
        pos = camera.getZ()+amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.panCameraUpTask, 'panCameraUpTask', extraArgs=[pos])
        self.runningTasks.append('panCameraUpTask')
    
    def panCameraUpTask(self, pos):
        """pan the camera to new position"""
        z = camera.getZ()
        if z >= pos:
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            return Task.done
        else:
            camera.setZ(z+self.panSpeed)
            self.cameraMoving = 1
            return Task.cont

    def panCameraDown(self, amount):
        """Pan Camera"""
        pos = camera.getZ()-amount
        self.game.app.disableMouseCamControl()
        taskMgr.add(self.panCameraDownTask, 'panCameraDownTask', extraArgs=[pos])
        self.runningTasks.append('panCameraDownTask')
    
    def panCameraDownTask(self, pos):
        """pan the camera to new position"""
        z = camera.getZ()
        if z <= pos:
            self.cameraMoving = 0
            if self.enableMouseCamControl == 1:
                self.game.app.enableMouseCamControl()
            return Task.done
        else:
            camera.setZ(z-self.panSpeed)
            self.cameraMoving = 1
            return Task.cont
        
    def createSelector(self,type='select',speed=2.0):
        """Create selector for indication of selected objects"""
        self.selector = self.loadObject(type, scale=2, parent=render, transparency=True, pos=Point2(0,0), glow=1)
        self.selector.hide()
        ival = self.selector.hprInterval((speed), Vec3(0, 0, 360))
        ival.loop()
    
    def createSelector2(self,type='select',speed=2.0):
        """Create selector2 for indication of secondary selected objects"""
        self.selector2 = self.loadObject(type, scale=2, parent=render, transparency=True, pos=Point2(0,0), glow=1)
        self.selector2.hide()
        ival = self.selector2.hprInterval((speed), Vec3(0, 0, 360))
        ival.loop()
    
    def playSound(self, soundName):
        """Play a Sound based on soundName given, call app"""
        if globals.serverMode == 0:
            self.game.app.playSound(soundName)
    
    def askForHelp(self):
        """Ask the Server to analyse Player and provide help"""
        try:
            serverResult = self.game.server.askForHelp(self.game.authKey)
            if type(serverResult) == types.ListType:
                (message, self.game.myEmpire['help']) = serverResult
                self.modeMsgBox(message)
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('askForHelp->Connection to Server Lost')
        
    def assignSelector(self, myObj, scale):
        """create the Selector and assign to myObj at scale"""
        if self.selector == None:
            self.createSelector()
            self.selector.show()
            
        self.selector.setPos(myObj.getX(), myObj.getY(), myObj.getZ())
        self.selector.setScale(scale)
    
    def assignSelector2(self, myObj, scale):
        """create the Selector2 and assign to myObj at scale"""
        if self.selector2 == None:
            self.createSelector2()
            self.selector2.show()
            
        self.selector2.setPos(myObj.getX(), myObj.getY(), myObj.getZ())
        self.selector2.setScale(scale)
       
    ##def checkEndTurn(self):
        ##"""Do a Server Assesment of turn before ending the turn"""
        ##try:
            ##if 'EndTurn' in self.game.myEmpire['help']:
                ### turn not ended yet
                ##(serverResult, self.game.myEmpire['help']) = self.game.server.askForHelp(self.game.authKey)
                ##if serverResult == 'Server Assessment: WARNINGS:0, CRITICAL:0 (Check Mail for Assesment)':
                    ### server assessment is good, end the turn without asking
                    ##self.endMyTurn()
                ##else:
                    ### server assessment has not come back without warnings ask for confirmation
                    ##self.modeYesNoBox('%s - Do you still want to end your turn?' % serverResult, 'endturnYes', 'yesNoBoxNo')
            ##else:
                ### turn already ended, unend turn
                ##self.modeYesNoBox('Do you want to cancel your end turn?' , 'endturnYes', 'yesNoBoxNo')
        ##except:
            ##self.modeMsgBox('checkEndTurn->Connection to Server Lost, Login Again')
    
    def exitGame(self, doLogout=True):
        """Exit the game"""
        self.setEmpireDefaults(self.game.authKey)
        if doLogout:
            self.setLogout(self.game.authKey)
        self.alive = 0
        self.game.app.quit()
    
    def getCreditInfoFromServer(self):
        self.getEmpireUpdate(['CR'])
    
    def refreshCredit(self):
        """Ask the Server for an updated Credit Info"""
        self.mainmenu.updateCR()
    
    def getEmpireUpdate(self, listAttr):
        """Ask the Server for updated Empire info"""
        try:
            serverResult = self.game.server.getEmpireUpdate(self.game.authKey, listAttr)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    self.game.myEmpire[key] = value
        except:
            self.modeMsgBox('getEmpireUpdate->Connection to Server Lost')
    
    def getMailUpdate(self):
        """Ask the Server for any updated mail"""
        try:
            myMailDict = self.game.myEmpire['mailBox']
            serverResult = self.game.server.getMailUpdate(self.game.authKey, myMailDict.keys())
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    myMailDict[key] = value
        except:
            self.modeMsgBox('getMailUpdate->Connection to Server Lost')
    
    def getGalaxyUpdate(self, listAttr):
        """Ask the Server for updated Galaxy info"""
        try:
            serverResult = self.game.server.getGalaxyUpdate(listAttr, self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    self.game.myGalaxy[key] = value
        except:
            self.modeMsgBox('getGalaxyUpdate->Connection to Server Lost')
    
    def getSystemUpdate(self, listAttr, systemID):
        """Ask the Server for updated System info"""
        try:
            serverResult = self.game.server.getSystemUpdate(listAttr, systemID, self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                mySystemDict = self.game.allSystems[systemID]
                for key, value in serverResult.iteritems():
                    mySystemDict[key] = value
        except:
            self.modeMsgBox('getSystemUpdate->Connection to Server Lost')
        
    def enterMode(self):
        """Enter the mode."""
        self.alive = 1
        self.setShortcuts()
    
    def setShortcuts(self):
        """Set the default mode shortcuts"""
        self.game.app.accept('mouse1', self.onMouse1Down)
        self.game.app.accept('mouse3', self.onMouse2Down)
        self.game.app.accept('space', self.onSpaceBarClear)
        if self.enableMouseCamControl == 1:
            self.game.app.accept('wheel_up', self.onMouseWheelUp)
            self.game.app.accept('wheel_down', self.onMouseWheelDown)
        
    def exitMode(self):
        """Exit the mode"""
        self.removeMySims()
        self.removeAllGui()
        self.game.app.ignoreAll()
        self.removeAllTasks()
        self.alive = 0
    
    def removeAllTasks(self):
        """Remove and Stop any tasks running"""
        for taskName in self.runningTasks:
            taskMgr.remove(taskName)

    def removeMySims(self):
        """Remove all sims in mode"""
        for sim in self.sims:
            try:
                sim.destroy()
            except:
                sim.removeNode()
    
    def removeAllGui(self):
        """Remove all DirectGUI"""
        for gui in self.gui:
            gui.destroy()
    
    def setPlanePickable(self, obj, dictName):
        """Set the plane model itself to be collideable with the mouse ray"""
        obj.sim.reparentTo(self.selectable)
        obj.sim.find('**/pPlane1').node().setIntoCollideMask(BitMask32.bit(1))
        obj.sim.find('**/pPlane1').node().setTag(dictName, obj.id)
    
    def setSpherePickable(self, obj, dictName):
        """Set the sphere model itself to be collideable with the mouse ray"""
        obj.sim.reparentTo(self.selectable)
        obj.sim.find('**/pSphere1').node().setIntoCollideMask(BitMask32.bit(1))
        obj.sim.find('**/pSphere1').node().setTag(dictName, obj.id)
    
    def setMySelector(self, x, y, z, scale):
        """Show selector if it is not in current position else return false"""
        selectorPos = (self.selector.getX(), self.selector.getY(), self.selector.getZ())
        if selectorPos != (x,y,z):
            self.selector.setPos(x,y,z)
            self.selector.show()
            self.selector.setScale(scale)
            return 1
        else:
            self.selector.setPos(-1,-1,-1)
            return 0
        #self.enableScrollWheelZoom = 0
    
    def getListButton(self, id, myScrolledList):
        """Return Button selected from buttonList gui based on id"""
        for button in myScrolledList.buttonsList:
            if button['extraArgs'][1] == id:
                return button
        
    def setMySelector2(self, x, y, z, scale):
        """Show selector2 if it is not in current position else return false"""
        selectorPos = (self.selector2.getX(), self.selector2.getY(), self.selector2.getZ())
        if selectorPos != (x,y,z):
            self.selector2.setPos(x,y,z)
            self.selector2.show()
            self.selector2.setScale(scale)
            return 1
        else:
            self.selector2.setPos(-1,-1,-1)
            return 0
        #self.enableScrollWheelZoom = 0
    
    def hideMySelector(self):
        """Hide the selector, move its position"""
        self.selector.setPos(-1,-1,-1)
        self.selector.hide()
        if self.selector2 != None:
            self.selector2.hide()
    
    def onMouse1Down(self):
        """Allow dynamic picking of an object within mode"""
        #Check to see if we can access the mouse. We need it to do anything else
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position
            mpos = base.mouseWatcherNode.getMouse()
         
            #Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            
            #Do the actual collision pass (Do it only on the selectable for
            #efficiency purposes)
            self.picker.traverse(self.selectable)
            if self.pq.getNumEntries() > 0:
                #if we have hit something, sort the hits so that the closest
                #is first, and highlight that node
                self.pq.sortEntries()
                for selectable in self.selectTypes:
                    name = self.pq.getEntry(0).getIntoNode().getTag(selectable)
                    if name != '':
                        self.clearAnyGui()
                        mySelectedDict = getattr(self, selectable)
                        mySelected = mySelectedDict[name]
                        myMethod = getattr(self, '%sSelected' % selectable)
                        if self.validateSelection():
                            myMethod(mySelected)
                        break
                    
    def onMouseWheelUp(self):
        """ zoom out """
        if self.enableScrollWheelZoom:
            self.stopCameraTasks()
            self.zoomInCameraAmount(20.0)
        
    def onMouseWheelDown(self):
        """ zoom in """
        if self.enableScrollWheelZoom:
            self.stopCameraTasks()
            self.zoomOutCameraAmount(20.0)
        
    def onMouse2Down(self):
        """clear"""
        self.onSpaceBarClear()
    
    def onSpaceBarClear(self):
        """Space bar should reset the view in the mode"""
        if self.validateSelection():
            self.resetCamera()
            self.clearMouseSelection()
            self.zoomOutCamera()
            self.setShortcuts()
            self.enableScrollWheelZoom = 1
    
    def clearMouseSelection(self):
        """Clear mouse selection before selecting something new"""
        pass

    def clearAnyGui(self):
        pass
    
    def update(self, interval):
        """update the mode, return the status, 0 means stop game"""
        return self.alive
        
    def setMyBackground(self):
        """Set the Background of mode"""
        base.setBackgroundColor(globals.colors['guiblue3'])
        
    def setEmpireDefaults(self, clientKey):
        """Read the defaults currently set and change them in the database"""
        try:
            # setup attributes to send to server
            defaults = ['viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes']
            d = {}
            for item in defaults:
                d[item] = self.game.myEmpire[item]
            serverResult = self.game.server.setEmpire(clientKey, d)
            if serverResult == 1:
                print 'Setup Empire Defaults Success'
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('SetEmpireDefaults->Connection to Server Lost, Login Again')

    def setEmpireValues(self, dValues):
        """Update Empire with d = key: empire attribute name,
        value = new value"""
        try:
            serverResult = self.game.server.setEmpire(self.game.authKey, dValues)
            if serverResult == 1:
                for key, value in dValues.iteritems():
                    self.game.myEmpire[key] = value
                print 'Empire Update Success'
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('setEmpireValues->Connection to Server Lost, Login Again')

    def setLogout(self, clientKey):
        """Send a Logout Request to the Server"""
        try:
            serverResult = self.game.server.logout(clientKey)
            if serverResult == 1:
                print 'Logout Successful, Exit Program'
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('setLogout->Connection to Server Lost, Login Again')
    
    def submitDesign(self, name):
        """Take Ship Design and submit it to Server for verification and storage"""
        (oldName, hullID, compDict, weaponDict) = self.myShipDesign.getMyDesign()
        dOrder = {'name':name, 'hullID':hullID, 'compDict':compDict, 'weaponDict':weaponDict}
        try:
            serverResult = self.game.server.addShipDesign(self.game.authKey, dOrder)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                # design has been accepted by server, retrieve design ID and add to client
                (ID,name) = serverResult
                self.game.shipDesigns[ID] = (name, hullID, compDict, weaponDict)
                self.getEmpireUpdate(['designsLeft'])
        except:
            self.modeMsgBox('submitDesign->Connection to Server Lost, Login Again')
      
    def destroyTempFrames(self):
        """Destroy any Temp Frames"""
        for frame in self.tempFrames:
            frame.destroy()
        self.tempFrames = []
    
    def modeMsgBox(self, messageText):
        """Create a message for the user"""
        self.createMessage(messageText)
    
    def createMessage(self, text):
        """Create a new message for user"""
        myMessage = fadingtext.FadingText(self.guiMediaPath, text, self.messagePositions)
        self.messagePositions.append(myMessage.getMyPosition())
        self.playSound('beep03')
    
    def writeToScreen(self, myText, x, z, scale=0.2, 
                      color='default', font=3, wordwrap=10):
        if color == 'default':
            color = Vec4(.1,.1,.8,.8)
        text = textonscreen.TextOnScreen(self.guiMediaPath, myText, scale,font=3)
        text.writeTextToScreen(x, self.depth, z, wordwrap=wordwrap)
        text.setColor(color)
        self.gui.append(text)
    
    def loadObject(self, tex=None, pos='default', depth=55, scale=1,
               transparency=True, parent='cam', model='plane', glow=0):
        if pos == 'default':
            pos = Point2(0,0)
        if parent == 'cam':
            parent = camera
        scaleX = 187.5
        scaleZ = 117.1875
        obj = loader.loadModelCopy('%s%s' % (self.guiMediaPath, model)) #default object uses the plane model
        if parent:
            obj.reparentTo(parent)              #Everything is parented to the camera so
                                            #that it faces the screen
        obj.setPos(Point3(pos.getX(), depth, pos.getY())) #Set initial position
        obj.setSx(scaleX)
        obj.setSz(scaleZ)
        obj.setBin("unsorted", 0)           #This tells Panda not to worry about the
                                            #order this is drawn in. (it prevents an
                                            #effect known as z-fighting)
        if transparency: obj.setTransparency(1) #All of our objects are trasnparent
        if tex:
            tex = loader.loadTexture('%s%s.png' % (self.guiMediaPath, tex)) #Load the texture
            obj.setTexture(tex, 1)                           #Set the texture
      
        self.sims.append(obj)
        obj.setShaderInput('glow',Vec4(glow,0,0,0),glow)
        return obj

    def onEntryFocus(self):
        """When a text Entry is in focus disable all shortcut keys"""
        for gui in self.gui:
            if gui.__module__ in self.entryFocusList:
                gui.ignoreShortcuts()
    
    def onEntryOutFocus(self):
        """When an text Entry is out of focus enable all shortcut keys"""
        for gui in self.gui:
            if gui.__module__ in self.entryFocusList:
                gui.setShortcuts()
