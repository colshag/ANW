# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# buttonlist.py
# Written by ynjo from panada3d forums, Chris Lewis wrapper class
# ---------------------------------------------------------------------------
# Displays a Scrolled Button List
# ---------------------------------------------------------------------------
import types
import logging
import sys

__all__=['ScrolledButtonsList']

from pandac.PandaModules import Vec4, TextNode
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame
from direct.gui.DirectGui import DGG, DirectLabel
from direct.interval.IntervalGlobal import Sequence
from direct.task import Task
from direct.showbase.PythonUtil import clampScalar
from types import IntType
from anw.func import globals
from anw.gui import textonscreen

class ButtonList(DirectObject):
    """Wrap the Scrolled Button List"""
    def __init__(self, path, title, width, height, titlewidth=30):
        self.titlewidth = titlewidth
        self.title = title
        self.path = path
        self.font = loader.loadFont('%s/star5' % self.path)
        self.myWidgets = []
        self.myTitle = None
        self.height = height
        self.width = width
        self.x = 0
        self.y = 0
        self.myNodePath = aspect2d.attachNewNode(title)
        self.myScrolledList = None
        self.createScrolledList()
        self.mode=None
        self.onClickMethod = ''
        self.createTitleCard()
    
    def addMultiLines(self, listOfData):
        """Add multiple lines of text to listbox if nessessary"""
        for item in listOfData:
            if type(item) == types.StringType:
                self.addMultiLineOfText(item)
            elif type(item) == types.ListType:
                for subitem in item:
                    self.addMultiLineOfText(subitem)
    
    def addMultiLineOfText(self, myText):
        """If text given is too long break it down and add each line"""
        num = 100
        if len(myText) > num:
            s1 = myText[:num]
            s2 = myText[num:]
            self.myScrolledList.addItem(text=s1)
            self.addMultiLineOfText(s2)
        else:
            self.myScrolledList.addItem(text=myText)
        
    def createTitleCard(self):
        """Default Title label"""
        if self.title != '':
            self.myTitle = textonscreen.TextOnScreen(self.path, self.title, 0.025, 5, aspect2d)
            self.myTitle.writeTextToScreen(self.x, 0, self.y+0.04, self.titlewidth)
            self.myTitle.setTitleStyle()
            self.myWidgets.append(self.myTitle)
    
    def setMyPosition(self, x, y):
        self.myNodePath.setPos(x, 0, y)
        self.myTitle.setMyPosition(x-self.width/1.85, 0, y+self.height/1.9)
    
    def createScrolledList(self):
        """Create the Scrolled List"""
        self.myScrolledList = ScrolledButtonsList(parent=self.myNodePath,
                                                  frameSize=(self.width, self.height),
                                                  command=self.onItemSelected)
        self.myWidgets.append(self.myScrolledList)
    
    def setMyMode(self, mode):
        self.mode = mode
        print self.myScrolledList
        self.myScrolledList.setMyMode(mode)
        self.disableZoom()

    def disableZoom(self):
        if self.mode:
            self.mode.enableScrollWheelZoom = 0        
        
    def setOnClickMethod(self, methodName):
        self.onClickMethod = methodName
    
    def onItemSelected(self, item, index, button):
        """Pass on Method and index declared from parent mode"""
        if self.onClickMethod != '':
            myMethod = getattr(self.mode, self.onClickMethod)
            myMethod(item, index, button)
    
    def getSelectedButtonID(self):
        """Return the id of the selected button"""
        myButton = self.myScrolledList.focusButton
        if myButton == None:
            return None
        else:
            return self.myScrolledList.buttonsList.index(myButton)
    
    def focusOnNextButton(self, id):
        """Press the next available button"""
        if id == None:
            return
        id += 1
        if len(self.myScrolledList.buttonsList) > id:
            self.myScrolledList.focusViewOnItem(id)
    
    def destroy(self):
        """Destroy gui"""
        self.removeMyWidgets()
    
    def removeMyWidgets(self):
        """Remove all sub widgets"""
        for myWidget in self.myWidgets:
            try:
                myWidget.removeNode()
            except:
                myWidget.destroy()
        self.ignoreAll()
        
class ScrolledButtonsList(DirectObject):
    """
       A class to display a list of selectable buttons.
       It is displayed using scrollable window (DirectScrolledFrame).
    """
    def __init__(self, parent=None, frameSize=(.8,1.2), buttonTextColor=(1,1,1,1),
                 font=None, itemScale=.045, itemTextScale=0.85, itemTextZ=0,
                 command=None, contextMenu=None, autoFocus=0,
                 colorChange=1, colorChangeDuration=1, newItemColor=globals.colors['guiblue1'],
                 rolloverColor=globals.colors['guiyellow'],
                 suppressMouseWheel=1, modifier='control'):
        self.mode = None
        self.focusButton=None
        self.command=command
        self.contextMenu=contextMenu
        self.autoFocus=autoFocus
        self.colorChange=colorChange
        self.colorChangeDuration=colorChangeDuration*.5
        self.newItemColor=newItemColor
        self.rolloverColor=rolloverColor
        self.rightClickTextColors=(Vec4(0,1,0,1),Vec4(0,35,100,1))
        self.font=font
        if font:
           self.fontHeight=font.getLineHeight()
        else:
           self.fontHeight=TextNode.getDefaultFont().getLineHeight()
        self.fontHeight*=1.2 # let's enlarge font height a little
        self.xtraSideSpace=.2*self.fontHeight
        self.itemTextScale=itemTextScale
        self.itemTextZ=itemTextZ
        self.buttonTextColor=buttonTextColor
        self.suppressMouseWheel=suppressMouseWheel
        self.modifier=modifier
        self.buttonsList=[]
        self.numItems=0
        self.__eventReceivers={}
        # DirectScrolledFrame to hold items
        self.itemScale=itemScale
        self.itemVertSpacing=self.fontHeight*self.itemScale
        self.frameWidth,self.frameHeight=frameSize
        # I set canvas' Z size smaller than the frame to avoid the auto-generated vertical slider bar
        self.childrenFrame = DirectScrolledFrame(
                     parent=parent,pos=(-self.frameWidth*.5,0,.5*self.frameHeight), relief=DGG.GROOVE,
                     state=DGG.NORMAL, # to create a mouse watcher region
                     frameSize=(0, self.frameWidth, -self.frameHeight, 0), frameColor=(0,0,0,.7),
                     canvasSize=(0, 0, -self.frameHeight*.5, 0), borderWidth=(0.01,0.01),
                     manageScrollBars=0, enableEdit=0, suppressMouse=0, sortOrder=1000 )
        # the real canvas is "self.childrenFrame.getCanvas()",
        # but if the frame is hidden since the beginning,
        # no matter how I set the canvas Z pos, the transform would be resistant,
        # so just create a new node under the canvas to be my canvas
        self.canvas=self.childrenFrame.getCanvas().attachNewNode('myCanvas')
        # slider background
        SliderBG=DirectFrame( parent=self.childrenFrame,frameSize=(-.025,.025,-self.frameHeight,0),
                     frameColor=(0,0,0,.7), pos=(-.03,0,0),enableEdit=0, suppressMouse=0)
        # slider thumb track
        sliderTrack = DirectFrame( parent=SliderBG, relief=DGG.FLAT, #state=DGG.NORMAL,
                     frameColor=(1,1,1,.2), frameSize=(-.015,.015,-self.frameHeight+.01,-.01),
                     enableEdit=0, suppressMouse=0)
        # page up
        self.pageUpRegion=DirectFrame( parent=SliderBG, relief=DGG.FLAT, state=DGG.NORMAL,
                     frameColor=(1,.8,.2,.1), frameSize=(-.015,.015,0,0),
                     enableEdit=0, suppressMouse=0)
        self.pageUpRegion.setAlphaScale(0)
        self.pageUpRegion.bind(DGG.B1PRESS,self.__startScrollPage,[-1])
        self.pageUpRegion.bind(DGG.WITHIN,self.__continueScrollUp)
        self.pageUpRegion.bind(DGG.WITHOUT,self.__suspendScrollUp)
        # page down
        self.pageDnRegion=DirectFrame( parent=SliderBG, relief=DGG.FLAT, state=DGG.NORMAL,
                     frameColor=(1,.8,.2,.1), frameSize=(-.015,.015,0,0),
                     enableEdit=0, suppressMouse=0)
        self.pageDnRegion.setAlphaScale(0)
        self.pageDnRegion.bind(DGG.B1PRESS,self.__startScrollPage,[1])
        self.pageDnRegion.bind(DGG.WITHIN,self.__continueScrollDn)
        self.pageDnRegion.bind(DGG.WITHOUT,self.__suspendScrollDn)
        self.pageUpDnSuspended=[0,0]
        # slider thumb
        self.vertSliderThumb=DirectButton(parent=SliderBG, relief=DGG.FLAT,
                     frameColor=(1,1,1,.6), frameSize=(-.015,.015,0,0),
                     enableEdit=0, suppressMouse=0, rolloverSound=None, clickSound=None)
        self.vertSliderThumb.bind(DGG.B1PRESS,self.__startdragSliderThumb)
        self.vertSliderThumb.bind(DGG.WITHIN,self.__enteringThumb)
        self.vertSliderThumb.bind(DGG.WITHOUT,self.__exitingThumb)
        self.oldPrefix=base.buttonThrowers[0].node().getPrefix()
        self.sliderThumbDragPrefix='draggingSliderThumb-'
        # GOD & I DAMN IT !!!
        # These things below don't work well if the canvas has a lot of buttons.
        # So I end up checking the mouse region every frame by myself using a continuous task.
  #       self.accept(DGG.WITHIN+self.childrenFrame.guiId,self.__enteringFrame)
  #       self.accept(DGG.WITHOUT+self.childrenFrame.guiId,self.__exitingFrame)
        self.isMouseInRegion=False
        self.mouseOutInRegionCommand=(self.__exitingFrame,self.__enteringFrame)
        taskMgr.doMethodLater(.2,self.__getFrameRegion,'getFrameRegion')
  
    def __getFrameRegion(self,t):
        for g in range(base.mouseWatcherNode.getNumGroups()):
            region=base.mouseWatcherNode.getGroup(g).findRegion(self.childrenFrame.guiId)
            if region!=None:
               self.frameRegion=region
               taskMgr.add(self.__mouseInRegionCheck,'mouseInRegionCheck')
               break
  
    def __mouseInRegionCheck(self,t):
        """
           check if the mouse is within or without the scrollable frame, and
           upon within or without, run the provided command
        """
        if not base.mouseWatcherNode.hasMouse(): return Task.cont
        m=base.mouseWatcherNode.getMouse()
        bounds=self.frameRegion.getFrame()
        inRegion=bounds[0]<m[0]<bounds[1] and bounds[2]<m[1]<bounds[3]
        if self.isMouseInRegion==inRegion: return Task.cont
        self.isMouseInRegion=inRegion
        self.mouseOutInRegionCommand[inRegion]()
        return Task.cont
  
    def __startdragSliderThumb(self,m=None):
        if self.mode != None:
            if hasattr(self.mode, 'enableMouseCamControl') == 1:
                if self.mode.enableMouseCamControl == 1:
                    self.mode.game.app.disableMouseCamControl()
        mpos=base.mouseWatcherNode.getMouse()
        parentZ=self.vertSliderThumb.getParent().getZ(render2d)
        sliderDragTask=taskMgr.add(self.__dragSliderThumb,'dragSliderThumb')
        sliderDragTask.ZposNoffset=mpos[1]-self.vertSliderThumb.getZ(render2d)+parentZ
  #       sliderDragTask.mouseX=base.winList[0].getPointer(0).getX()
        self.oldPrefix=base.buttonThrowers[0].node().getPrefix()
        base.buttonThrowers[0].node().setPrefix(self.sliderThumbDragPrefix)
        self.acceptOnce(self.sliderThumbDragPrefix+'mouse1-up',self.__stopdragSliderThumb)
  
    def __dragSliderThumb(self,t):
        if not base.mouseWatcherNode.hasMouse():
           return
        mpos=base.mouseWatcherNode.getMouse()
  #       newY=base.winList[0].getPointer(0).getY()
        self.__updateCanvasZpos((t.ZposNoffset-mpos[1])/self.canvasRatio)
  #       base.winList[0].movePointer(0, t.mouseX, newY)
        return Task.cont
  
    def __stopdragSliderThumb(self,m=None):
        if self.mode != None:
            if hasattr(self.mode, 'enableMouseCamControl') == 1:
                if self.mode.enableMouseCamControl == 1:
                    self.mode.game.app.enableMouseCamControl()
        taskMgr.remove('dragSliderThumb')
        self.__stopScrollPage()
        base.buttonThrowers[0].node().setPrefix(self.oldPrefix)
        if self.isMouseInRegion:
           self.mouseOutInRegionCommand[self.isMouseInRegion]()
  
    def __startScrollPage(self,dir,m):
        self.oldPrefix=base.buttonThrowers[0].node().getPrefix()
        base.buttonThrowers[0].node().setPrefix(self.sliderThumbDragPrefix)
        self.acceptOnce(self.sliderThumbDragPrefix+'mouse1-up',self.__stopdragSliderThumb)
        t=taskMgr.add(self.__scrollPage,'scrollPage',extraArgs=[int((dir+1)*.5),dir*.01/self.canvasRatio])
        self.pageUpDnSuspended=[0,0]
  
    def __scrollPage(self,dir,scroll):
        if not self.pageUpDnSuspended[dir]:
           self.__scrollCanvas(scroll)
        return Task.cont
  
    def __stopScrollPage(self,m=None):
        taskMgr.remove('scrollPage')
  
    def __suspendScrollUp(self,m=None):
        self.pageUpRegion.setAlphaScale(0)
        self.pageUpDnSuspended[0]=1
    def __continueScrollUp(self,m=None):
        if taskMgr.hasTaskNamed('dragSliderThumb'):
           return
        self.pageUpRegion.setAlphaScale(1)
        self.pageUpDnSuspended[0]=0
   
    def __suspendScrollDn(self,m=None):
        self.pageDnRegion.setAlphaScale(0)
        self.pageUpDnSuspended[1]=1
    def __continueScrollDn(self,m=None):
        if taskMgr.hasTaskNamed('dragSliderThumb'):
           return
        self.pageDnRegion.setAlphaScale(1)
        self.pageUpDnSuspended[1]=0
  
    def __suspendScrollPage(self,m=None):
        self.__suspendScrollUp()
        self.__suspendScrollDn()
   
    def __enteringThumb(self,m=None):
        self.vertSliderThumb['frameColor']=(1,1,1,1)
        self.__suspendScrollPage()
  
    def __exitingThumb(self,m=None):
        self.vertSliderThumb['frameColor']=(1,1,1,.6)
  
    def __scrollCanvas(self,scroll):
        if self.vertSliderThumb.isHidden() or self.buttonsList == []:
           return
        self.__updateCanvasZpos(self.canvas.getZ()+scroll)
  
    def __updateCanvasZpos(self,Zpos):
        newZ=clampScalar(Zpos, .0, self.canvasLen-self.frameHeight+.015)
        self.canvas.setZ(newZ)
        thumbZ=-newZ*self.canvasRatio
        self.vertSliderThumb.setZ(thumbZ)
        self.pageUpRegion['frameSize']=(-.015,.015,thumbZ-.01,-.01)
        self.pageDnRegion['frameSize']=(-.015,.015,-self.frameHeight+.01,thumbZ+self.vertSliderThumb['frameSize'][2])
  
    def __adjustCanvasLength(self,numItem):
        self.canvasLen=float(numItem)*self.itemVertSpacing
        self.canvasRatio=(self.frameHeight-.015)/(self.canvasLen+.01)
        if self.canvasLen<=self.frameHeight-.015:
           canvasZ=.0
           self.vertSliderThumb.hide()
           self.pageUpRegion.hide()
           self.pageDnRegion.hide()
           self.canvasLen=self.frameHeight-.015
        else:
           canvasZ=self.canvas.getZ()
           self.vertSliderThumb.show()
           self.pageUpRegion.show()
           self.pageDnRegion.show()
        self.__updateCanvasZpos(canvasZ)
        self.vertSliderThumb['frameSize']=(-.015,.015,-self.frameHeight*self.canvasRatio,-.01)
        thumbZ=self.vertSliderThumb.getZ()
        self.pageUpRegion['frameSize']=(-.015,.015,thumbZ-.01,-.01)
        self.pageDnRegion['frameSize']=(-.015,.015,-self.frameHeight+.01,thumbZ+self.vertSliderThumb['frameSize'][2])
  
    def __acceptAndIgnoreWorldEvent(self,event,command,extraArgs=[]):
        receivers=messenger.whoAccepts(event)
        if receivers is None:
           self.__eventReceivers[event]={}
        else:
           self.__eventReceivers[event]=receivers.copy()
        for r in self.__eventReceivers[event].keys():
            if type(r) != types.TupleType:
                r.ignore(event)
        self.accept(event,command,extraArgs)
  
    def __ignoreAndReAcceptWorldEvent(self,events):
        for event in events:
            self.ignore(event)
            if self.__eventReceivers.has_key(event):
               for r, method_xtraArgs_persist in self.__eventReceivers[event].items():
                   if type(r) != types.TupleType:
                       messenger.accept(event,r,*method_xtraArgs_persist)
            self.__eventReceivers[event]={}
  
    def __enteringFrame(self,m=None):
        # sometimes the WITHOUT event for page down region doesn't fired,
        # so directly suspend the page scrolling here
        self.__suspendScrollPage()
        BTprefix=base.buttonThrowers[0].node().getPrefix()
        if BTprefix==self.sliderThumbDragPrefix:
           return
        self.inOutBTprefix=BTprefix
        if self.suppressMouseWheel:
           self.__acceptAndIgnoreWorldEvent(self.inOutBTprefix+'wheel_up',
                command=self.__scrollCanvas, extraArgs=[-.07])
           self.__acceptAndIgnoreWorldEvent(self.inOutBTprefix+'wheel_down',
                command=self.__scrollCanvas, extraArgs=[.07])
        else:
           self.accept(self.inOutBTprefix+self.modifier+'-wheel_up',self.__scrollCanvas, [-.07])
           self.accept(self.inOutBTprefix+self.modifier+'-wheel_down',self.__scrollCanvas, [.07])
  
    def __exitingFrame(self,m=None):
        if not hasattr(self,'inOutBTprefix'):
           return
        if self.suppressMouseWheel:
           self.__ignoreAndReAcceptWorldEvent( (
                                               self.inOutBTprefix+'wheel_up',
                                               self.inOutBTprefix+'wheel_down',
                                               ) )
        else:
           self.ignore(self.inOutBTprefix+self.modifier+'-wheel_up')
           self.ignore(self.inOutBTprefix+self.modifier+'-wheel_down')
  
    def __setFocusButton(self,button,item):
        if self.focusButton:
           self.restoreNodeButton2Normal()
        self.focusButton=button
        self.highlightNodeButton()
        if callable(self.command) and button in self.buttonsList:
           # run user command and pass the selected item, it's index, and the button
           self.command(item,self.buttonsList.index(button),button)
  
    def __rightPressed(self,button,m):
        self.__isRightIn=True
  #       text0 : normal
  #       text1 : pressed
  #       text2 : rollover
  #       text3 : disabled
        button._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rightClickTextColors[self.focusButton==button])
        button.bind(DGG.B3RELEASE,self.__rightReleased,[button])
        button.bind(DGG.WITHIN,self.__rightIn,[button])
        button.bind(DGG.WITHOUT,self.__rightOut,[button])
  
    def __rightIn(self,button,m):
        self.__isRightIn=True
        button._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rightClickTextColors[self.focusButton==button])
    def __rightOut(self,button,m):
        self.__isRightIn=False
        button._DirectGuiBase__componentInfo['text2'][0].setColorScale(Vec4(1,1,1,1))
  
    def __rightReleased(self,button,m):
        button.unbind(DGG.B3RELEASE)
        button.unbind(DGG.WITHIN)
        button.unbind(DGG.WITHOUT)
        button._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rolloverColor)
        if not self.__isRightIn:
           return
        if callable(self.contextMenu):
           # run user command and pass the selected item, it's index, and the button
           self.contextMenu(button['extraArgs'][1],self.buttonsList.index(button),button)

    def scrollToBottom(self):
        ##for i in range(0,self.numItems):
        self.__scrollCanvas(1)

    def selectButton(self, button, item):
        self.__setFocusButton(button, item)
  
    def restoreNodeButton2Normal(self):
        """
           stop highlighting item
        """
        if self.focusButton != None:
            #self.focusButton['text_fg']=(1,1,1,1)
            self.focusButton['frameColor']=(0,0,0,0)
  
    def highlightNodeButton(self,idx=None):
        """
           highlight the item
        """
        if idx is not None:
            self.focusButton=self.buttonsList[idx]
        #self.focusButton['text_fg']=(.01,.01,.01,1)
        # nice dark blue.  don't mess with the text fg color though! we want it custom
        self.focusButton['frameColor']=(0,.3,.8,1)
  
    def clear(self):
        """
           clear the list
        """
        for c in self.buttonsList:
            c.remove()
        self.buttonsList=[]
        self.focusButton=None
        self.numItems=0
  
    def addItem(self,text,extraArgs=None,atIndex=None,textColorName=None):
        """
           add item to the list
           text : text for the button
           extraArgs : the object which will be passed to user command(s)
                       (both command and contextMenu) when the button get clicked
           atIndex : where to add the item
                     <None> : put item at the end of list
                     <integer> : put item at index <integer>
                     <button> : put item at <button>'s index
            textColorName : the color name eg. 'yellow'
        """
        textColor = self.buttonTextColor
        if textColorName != None:
            textColor = globals.colors[textColorName]
            
        button = DirectButton(parent=self.canvas,
            scale=self.itemScale,
            relief=DGG.FLAT,
            frameColor=(0,0,0,0),text_scale=self.itemTextScale,
            text=text, text_pos=(0,self.itemTextZ),text_fg=textColor,
            text_font=self.font, text_align=TextNode.ALeft,
            command=self.__setFocusButton,
            enableEdit=0, suppressMouse=0, rolloverSound=None,clickSound=None)
        #button.setMyMode(self.mode)
        l,r,b,t=button.getBounds()
        # top & bottom are blindly set without knowing where exactly the baseline is,
        # but this ratio fits most fonts
        baseline=-self.fontHeight*.25
        #button['saved_color'] = textColor
        button['frameSize']=(l-self.xtraSideSpace,r+self.xtraSideSpace,baseline,baseline+self.fontHeight)
  
  #          Zc=NodePath(button).getBounds().getCenter()[1]-self.fontHeight*.5+.25
  # #          Zc=button.getCenter()[1]-self.fontHeight*.5+.25
  #          button['frameSize']=(l-self.xtraSideSpace,r+self.xtraSideSpace,Zc,Zc+self.fontHeight)
       
        button['extraArgs']=[button,extraArgs]
        button._DirectGuiBase__componentInfo['text2'][0].setColorScale(self.rolloverColor)
        button.bind(DGG.B3PRESS,self.__rightPressed,[button])
        if isinstance(atIndex,DirectButton):
           if atIndex.isEmpty():
              atIndex=None
           else:
              index=self.buttonsList.index(atIndex)
              self.buttonsList.insert(index,button)
        if atIndex==None:
           self.buttonsList.append(button)
           index=self.numItems
        elif type(atIndex)==IntType:
           index=atIndex
           self.buttonsList.insert(index,button)
        Zpos=(-.7-index)*self.itemVertSpacing
        button.setPos(.02,0,Zpos)
        if index!=self.numItems:
           for i in range(index+1,self.numItems+1):
               self.buttonsList[i].setZ(self.buttonsList[i],-self.fontHeight)
        self.numItems+=1
        self.__adjustCanvasLength(self.numItems)
        if self.autoFocus:
           self.focusViewOnItem(index)
        if self.colorChange:
           Sequence(
              button.colorScaleInterval(self.colorChangeDuration,self.newItemColor,globals.colors['guiblue3']),
              button.colorScaleInterval(self.colorChangeDuration,Vec4(1,1,1,1),self.newItemColor)
              ).start()
  
    def focusViewOnItem(self,idx):
        """
           Scroll the window so the newly added item will be displayed
           in the middle of the window, if possible.
        """
        Zpos=(idx+.7)*self.itemVertSpacing-self.frameHeight*.5
        self.__updateCanvasZpos(Zpos)
       
    def setAutoFocus(self,b):
        """
           set auto-view-focus state of newly added item
        """
        self.autoFocus=b
  
    def index(self,button):
        """
           get the index of button
        """
        if not button in self.buttonsList:
           return None
        return self.buttonsList.index(button)
       
    def getNumItems(self):
        """
           get the current number of items on the list
        """
        return self.numItems
  
    def disableItem(self,i):
        if not 0<=i<self.numItems:
           print 'DISABLING : invalid index (%s)' %i
           return
        self.buttonsList[i]['state']=DGG.DISABLED
        self.buttonsList[i].setColorScale(.3,.3,.3,1)
   
    def enableItem(self,i):
        if not 0<=i<self.numItems:
           print 'ENABLING : invalid index (%s)' %i
           return
        self.buttonsList[i]['state']=DGG.NORMAL
        self.buttonsList[i].setColorScale(1,1,1,1)
  
    def removeItem(self,index):
        if not 0<=index<self.numItems:
           print 'REMOVAL : invalid index (%s)' %index
           return
        if self.numItems==0: return
        if self.focusButton==self.buttonsList[index]:
           self.focusButton=None
        self.buttonsList[index].removeNode()
        del self.buttonsList[index]
        self.numItems-=1
        for i in range(index,self.numItems):
            self.buttonsList[i].setZ(self.buttonsList[i],self.fontHeight)
        self.__adjustCanvasLength(self.numItems)
  
    def destroy(self):
        self.clear()
        self.__exitingFrame()
        self.ignoreAll()
        self.childrenFrame.removeNode()
        taskMgr.remove('mouseInRegionCheck')
  
    def hide(self):
        self.childrenFrame.hide()
        self.isMouseInRegion=False
        self.__exitingFrame()
        taskMgr.remove('mouseInRegionCheck')
  
    def show(self):
        self.childrenFrame.show()
        if not hasattr(self,'frameRegion'):
           taskMgr.doMethodLater(.2,self.__getFrameRegion,'getFrameRegion')
        elif not taskMgr.hasTaskNamed('mouseInRegionCheck'):
           taskMgr.add(self.__mouseInRegionCheck,'mouseInRegionCheck')
  
    def toggleVisibility(self):
        if self.childrenFrame.isHidden():
           self.show()
        else:
           self.hide()
  
    def setMyMode(self, myMode):
        self.mode = myMode
  
if __name__=='__main__':
   import direct.directbase.DirectStart
   import string,sys
   from random import uniform
   
   counter=0
   selectedButton=None

   def itemSelected(item,index,button): # don't forget to receive item, it's index, and the button
       global selectedButton
       selectedButton=button
       print item,'(idx : %s) SELECTED' %index

   def itemRightClicked(item,index,button): # don't forget to receive item, it's index, and the button
       print item,'(idx : %s) RIGHT-CLICKED' %index

   def addNewItem():
       global counter
       i='new item '+str(counter)
       btnList.addItem(text=i, extraArgs='NEW_%s'%counter)
       counter+=1

   def insertNewItemAtSelected():
       global counter
       i='new item '+str(counter)
       btnList.addItem(text=i, extraArgs='NEW_%s'%counter, atIndex=selectedButton)
       counter+=1

   def insertNewItemBelowSelected():
       index=btnList.index(selectedButton)
       if index==None: return
       global counter
       i='new item '+str(counter)
       btnList.addItem(text=i, extraArgs='NEW_%s'%counter, atIndex=index+1)
       counter+=1

   def disableRandomItem():
       btnList.disableItem(int(uniform(0,btnList.getNumItems())))
       
   def enableRandomItem():
       btnList.enableItem(int(uniform(0,btnList.getNumItems())))

   def removeRandomItem():
       btnList.removeItem(int(uniform(0,btnList.getNumItems())))
       
   # 3d node
   teapot=loader.loadModel('teapot')
   teapot.reparentTo(render)

   OnscreenText(text='''[ H ] : hide browser        [ S ] : show browser        [ SPACE ] : toggle visibility       [ DEL ] : destroy browser
[ MOUSE WHEEL ]  inside scrollable window : scroll window
[ MOUSE WHEEL ]  outside scrollable window : change teapot scale
hold  [ ENTER ] : add new item at the end of list
hold  [ INSERT ] : insert new item at selected item
hold  [ CTRL-INSERT ] : insert new item below selected item
''', scale=.045, fg=(1,1,1,1), shadow=(0,0,0,1)).setZ(.96)
   OnscreenText(text='''hold  [ CAPS LOCK] : disable random item
hold  [ TAB ] : enable random item
hold  [ X ] : remove random item
''', scale=.045, fg=(1,1,1,1), shadow=(0,0,0,1)).setZ(-.75)

   # load other font
#    transMtl=loader.loadFont('/g/fontku/- use/Crystal clear.ttf')
#    transMtl=loader.loadFont('Transmetals.ttf')
#    transMtl.setLineHeight(.9)

   # create ScrolledButtonsList
   btnList=ScrolledButtonsList(
               parent=None, # attach to this parent node
               frameSize=(.8,1.2), buttonTextColor=(1,1,1,1),
               font=None, itemScale=.045, itemTextScale=1, itemTextZ=0,
#                font=transMtl, itemScale=.05, itemTextScale=1, itemTextZ=0,
               command=itemSelected, # user defined method, executed when a node get selected,
                                     # receiving extraArgs (which passed to addItem)
               contextMenu=itemRightClicked, # user defined method, executed when a node right-clicked,
                                             # receiving extraArgs (which passed to addItem)
               autoFocus=0, # initial auto view-focus on newly added item
               colorChange=1,
               colorChangeDuration=.7,
               newItemColor=(0,1,0,1),
               rolloverColor=(1,.8,.2,1),
               suppressMouseWheel=1,  # 1 : blocks mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by putting mouse cursor
                                      #     inside the scrollable window.
                                      # 0 : does not block mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by holding down the modifier key
                                      #     (defined below) while scrolling your wheel.
               modifier='control'  # shift/control/alt
               )
   # populate the list with alphabets and numbers
   for a in string.ascii_letters+string.digits:
       # extraArgs would be passed to command and contextMenu
       btnList.addItem(text='item  '+(a+' ')*10, extraArgs=a, atIndex=None)
   btnList.setAutoFocus(1)  # after adding those items,
                            # enable auto view-focus on newly added item

   DO=DirectObject()
   # events for btnList
   DO.accept('h',btnList.hide)
   DO.accept('s',btnList.show)
   DO.accept('space',btnList.toggleVisibility)
   DO.accept('delete',btnList.destroy)
   DO.accept('enter',addNewItem)
   DO.accept('enter-repeat',addNewItem)
   DO.accept('insert',insertNewItemAtSelected)
   DO.accept('insert-repeat',insertNewItemAtSelected)
   DO.accept('control-insert',insertNewItemBelowSelected)
   DO.accept('control-insert-repeat',insertNewItemBelowSelected)
   DO.accept('caps_lock-repeat',disableRandomItem)
   DO.accept('tab-repeat',enableRandomItem)
   DO.accept('x-repeat',removeRandomItem)
   # events for the world
   DO.accept('wheel_up',teapot.setScale,[teapot,1.2])
   DO.accept('wheel_down',teapot.setScale,[teapot,.8])
   DO.accept('escape',sys.exit)

   camera.setPos(11.06, -16.65, 8.73)
   camera.setHpr(42.23, -25.43, -0.05)
   base.setBackgroundColor(.2,.2,.2,1)
   base.disableMouse()
#    messenger.toggleVerbose()
   # to visualize the mouse regions, uncomment the next line
   #base.mouseWatcherNode.showRegions(render2d,'gui-popup',0)
   run()