import layouts
import pyui

from pyui.desktop import getDesktop, getTheme, getRenderer
from pyui.base import Base, Panel, Window


class Dockable(Base):
    """an object that can be docked within a frame. This could be a toolbar or menu..
    """
    def __init__(self, minWidth, minHeight):
        Base.__init__(self)
        self.frame = None
        self.minWidth = minWidth
        self.minHeight = minHeight
        self.resize(minWidth, minHeight)
        
    def dock(self, frame, slot):
        """dock me in a frame. This should only ever be called by a dockSlot
        """
        self.frame = frame
        self.dockSlot = slot

    def draw(self, renderer):
        renderer.drawRect( pyui.colors.white, self.rect)
        print self.rect


class DockSlot(Base):
    """a container of dockables at one edge of a frame.
    """
    def __init__(self):
        Base.__init__(self)
        self.frame = None
        self.slot = 0
        self.width = 0
        self.height = 0
        self.dockables = []
        
    def dock(self, frame, slot, interiorRect):
        self.parent = frame
        self.slot = slot
        self.calcDockPos(interiorRect)
        
    def calcDockPos(self, interiorRect):
        if self.slot == pyui.locals.DOCK_TOP:
            self.posX = interiorRect[0]
            self.posY = interiorRect[1]
            self.width = interiorRect[2]
            self.height = self.calcHeight()
            
        elif self.slot == pyui.locals.DOCK_BOTTOM:
            self.posX = interiorRect[0]
            self.posY = interiorRect[1] + interiorRect[3] - self.calcHeight()
            self.width = interiorRect[2]
            self.height = self.calcHeight()
            
        elif self.slot == pyui.locals.DOCK_LEFT:
            self.posX = interiorRect[0]
            self.posY = interiorRect[1]
            self.width = self.calcWidth()
            self.height = interiorRect[3]
            
        elif self.slot == pyui.locals.DOCK_RIGHT:
            self.posX = interiorRect[0] + interiorRect[2] - self.calcWidth()
            self.posY = interiorRect[1]
            self.width = self.calcWidth()
            self.height = interiorRect[3]

    def calcWidth(self):
        w = 0
        for dockable in self.dockables:
            w += dockable.rect[2]
        return w

    def calcHeight(self):
        h = 0
        for dockable in self.dockables:
            h += dockable.rect[3]
        return h
    
    def getSpan(self):
        """returns the relevant width or height depending on the slot.
        """
        if self.slot == pyui.locals.DOCK_LEFT or self.slot == pyui.locals.DOCK_RIGHT:
            return self.width
        else:
            return self.height

    def addDockable(self, dockable, interiorRect):
        self.dockables.append(dockable)
        self.calcDockPos(interiorRect)
        dockable.parent = self
        dockable.calcSize()

    def removeDockable(self, dockable):
        self.dockables.remove(dockable)

    def resize(self, x, y, w, h):
        """resize myself to fit in these dimensions. this resizes all of the
        dockables as well, but only along one axis
        """
        self.posX = x
        self.posY = y
        self.width = w
        self.height = h
        
        for dockable in self.dockables:
            if self.slot == pyui.locals.DOCK_LEFT:
                dockable.moveto(x, y)
                dockable.resize(dockable.rect[2], h)
                x += dockable.rect[2]
                
            if self.slot == pyui.locals.DOCK_RIGHT:
                dockable.moveto(x-dockable.rect[2], y)
                dockable.resize(dockable.rect[2], h)
                x -= dockable.rect[2]
                
            if self.slot == pyui.locals.DOCK_TOP:
                dockable.moveto(x, y)
                dockable.resize(w, dockable.rect[3])
                y += dockable.rect[3]
                
            if self.slot == pyui.locals.DOCK_BOTTOM:
                dockable.moveto(x, y-dockable.rect[3])
                dockable.resize(w, dockable.rect[3])
                y -= dockable.rect[3]

    def trim(self, x, y, w, h):
        """this is passed the rect of the interior of the frame. trim
        this rect to allow placement of my dockables.
        """
        if self.slot == pyui.locals.DOCK_LEFT:
            self.resize(x,y,self.width, h)
            x += self.width
            self.height = h
            
        elif self.slot == pyui.locals.DOCK_RIGHT:
            self.resize(x+w, y, self.width, h)
            w -= self.width
            self.height = h
            
        elif self.slot == pyui.locals.DOCK_TOP:
            self.resize(x,y,w,self.height)
            y += self.height
            h -= self.height
            self.width = w
                
        elif self.slot == pyui.locals.DOCK_BOTTOM:
            self.resize(x, y+h , w, self.height)
            h -= self.height
            self.width = w

        # the size of the dockable is NOT the size of the inner rect of the frame..
            
        return (x, y, w, h)
            
    def draw(self, renderer):
        for d in self.dockables:
            d.draw(renderer)

    def handleEvent(self, event):
        for d in self.dockables:
            if d.handleEvent(event):
                return 1
            

class Frame(Window):
    """A frame is a window that has a titlebar and borders. it is resizable and movable
    by dragging the titlebar. Frames can have Dockables docked within them at any border.
    """
    def __init__(self, x, y, w, h, title, topmost = 0):
        self.theme = getTheme()
        self.innerWidth = w
        self.innerHeight = h
        self.title = title

        self.dockables = {}  # map of dockable positions to list of docked items
        self.interiorRect = (0,0,w,h)
        
        Window.__init__(self, x, y, w, h, topmost)
        self.setTitle(self.title)

        #setup interior
        self.placeInteriorObjects()

        self.registerEvent(pyui.locals.LMOUSEBUTTONDOWN, self._pyuiMouseDown)
        self.registerEvent(pyui.locals.LMOUSEBUTTONUP, self._pyuiMouseUp)
        self.registerEvent(pyui.locals.MOUSEMOVE, self._pyuiMouseMotion)
        self.moving = 0
        self.resizing = 0
        self.startX = 0
        self.startY = 0
        self.resizingCursor=0
        self.movingCursor=0
        self.backImage=None

    def calculateInterior(self):
        """I use the borders of the frame and any dockables to calculate the
        size of the useable interior space of the frame.
        """
        # start with real outer size of the frame
        iwidth = self.rect[2]
        iheight = self.rect[3]
        ileft = 0
        itop = 0

        # apply frame borders
        iwidth -= self.theme.getFrameBorderLeft()
        iwidth -= self.theme.getFrameBorderRight()
        iheight -= self.theme.getFrameBorderBottom()
        iheight -= self.theme.getFrameBorderTop()
        ileft += self.theme.getFrameBorderLeft()
        itop += self.theme.getFrameBorderTop()

        interior = (ileft, itop, iwidth, iheight)
        for dockSlot in self.dockables.values():
            interior = apply(dockSlot.trim,interior)
        return interior

    def placeInteriorObjects(self):
        """called to fix the placement of the interior panel and
        any dockable objects (menus and toolbars.
        """
        self.interiorRect = self.calculateInterior()        
        self._panel.moveto(self.interiorRect[0], self.interiorRect[1])
        self._panel.resize(self.interiorRect[2], self.interiorRect[3])

    def addDockable(self, dockable, slot):
        """Add a dockable element
        """
        if not slot in pyui.locals.dockSlots:
            raise "invalid docking slot %d" % slot

        dockList = self.dockables.get(slot)
        if not dockList:
            dockList = DockSlot()
            dockList.dock(self, slot, self.interiorRect)
            self.dockables[slot] = dockList
            
        dockList.addDockable(dockable, self.interiorRect)

        dockable.dock(self, slot)
        self.placeInteriorObjects()
        
    def setTitle(self, title):
        self.title = title

    def setBackImage(self, filename):
        self.backImage = filename
        
    def draw(self, renderer):
        """Draws to the actual frame if the renderer requires it.
        """
        if not self.show:
            return

        # draw frame border
        self.hitList = getTheme().drawFrame( (0,0,self.width, self.height), self.title, None)
        if self.backImage:
            renderer.drawImage(self.interiorRect, self.backImage)

        # draw interior widgets
        Window.draw(self, renderer)

        # draw dockables. this allows dockables to overdraw the interior area
        for dockSlot in self.dockables.values():
            if dockSlot:
                dockSlot.draw(renderer)
        
    def replacePanel(self, panel):
        Window.replacePanel(self, panel)
        self.placeInteriorObjects()

    def hitFrameRegion(self, pos):
        # put hit position in window relative coords
        x = pos[0] - self.rect[0]
        y = pos[1] - self.rect[1]

        # scan through hit regions        
        for (regionId, rect) in self.hitList:
            if x >= rect[0] and y >= rect[1] and x < rect[0]+rect[2] and y < rect[1]+rect[3]:
                return regionId
        else:
            return None

    def _pyuiMouseMotion(self, event):
        if self.moving:
            mouseX = event.pos[0] - self.posX
            mouseY = event.pos[1] - self.posY
            self.move( mouseX - self.startX, mouseY - self.startY)
            getRenderer().moveWindow(self.handle, self.posX, self.posY)
            return 1
        if self.resizing:
            mouseX = event.pos[0] - self.posX
            mouseY = event.pos[1] - self.posY
            if mouseX < 64:
                mouseX = 64
            if mouseY < 64:
                mouseY = 64
            self.resize( self.width + mouseX - self.startX, self.height + mouseY - self.startY)
            (self.startX, self.startY) = (mouseX, mouseY)
            return 1

        # set the proper cursor
        if event.pos[0] > self.posX + self.innerWidth and event.pos[1] > self.posY + self.innerHeight:
            self.resizingCursor=1
            self.theme.setResizeCursor()
        elif self.resizingCursor:
            self.resizingCursor=0
            self.theme.setArrowCursor()
            
        if event.pos[0] < self.posX +self.width- 32 and event.pos[1] < self.posY + self.theme.getFrameBorderTop()-8:
            self.movingCursor = 1
            self.theme.setMovingCursor()
        elif self.movingCursor:
            self.movingCursor = 0
            self.theme.setArrowCursor()
            
        if not self.hit(event.pos):
            if self.resizingCursor and not self.resizing:
                self.resizingCursor=0
                self.theme.setArrowCursor()
            if self.movingCursor and not self.moving:
                self.movingCursor=0
                self.theme.setArrowCursor()
            return 0
        else:
            return 1
        
    def _pyuiMouseDown(self, event):
        if not self.hit(event.pos):
            return 0

        self.getFocus()
        regionId = self.hitFrameRegion(event.pos)
        
        # check for closing            
        if regionId == pyui.locals.HIT_FRAME_CLOSE:
            if hasattr(self, "onCloseButton"):
                return self.onCloseButton()
            return self._pyuiCloseButton()
        
        # check for moving
        if regionId == pyui.locals.HIT_FRAME_MOVE:
            self.moving  = 1
            self.startX = event.pos[0] - self.posX
            self.startY = event.pos[1] - self.posY
            return 1
        
        # check for resizing
        if regionId == pyui.locals.HIT_FRAME_RESIZE_BOTTOM_RIGHT:
            self.resizing = 1
            self.startX = event.pos[0] - self.posX
            self.startY = event.pos[1] - self.posY
            return 1

        return 1

    def _pyuiMouseUp(self, event):
        if self.moving:
            self.moving = 0
            return 1
        if self.resizing:
            self.resizing = 0
            return 1
        if self.resizingCursor:
            self.resizingCursor=0
            self.theme.setArrowCursor()                                        
        if not self.hit(event.pos):
            return 0
        return 1

    def resize(self, w, h):
        if w < 64:
            w = 64
        if h < 64:
            h = 64
        Base.resize(self, w, h)
        if self._panel:
            self.placeInteriorObjects()

    def _pyuiCloseButton(self):
        print "Destroying window", self
        self.theme.setArrowCursor()        
        self.destroy()
        return 1            

    def handleEvent(self, event):
        """ event processing for frame objects
        """
        if not self.show:
            return

        for slot in self.dockables.values():
            if slot.handleEvent(event):
                return 1
            
        i = len(self.children) - 1
        while i > -1:
            child = self.children[i]
            if child.handleEvent(event):
                return 1
            i = i  - 1
        if self.eventMap.has_key(event.type):
            if self.eventMap[event.type](event):
                return 1

        # popup handling here so it's not overridden with subclass event behavior
        if self.popup and event.type == pyui.locals.RMOUSEBUTTONDOWN and self.hit(event.pos):
            self.popup.activate(event.pos[0], event.pos[1])
            return 1
        return 0

class FrameMenuItem:
    """Used by menu widget to track items. Can have an icon 16x16 in size.
    """
    def __init__(self, handler, text, subMenu):
        self.handler = handler
        self.text = text
        (width, height) = getRenderer().getTextSize(text, getTheme().defaultFont)
        self.width = width
        self.subMenu = subMenu
        self.icon = None
        self.rect = (0,0,0,0)
        self.canActivate = handler or subMenu

    def setIcon(self, icon):
        self.icon = icon


class FrameMenuBar(Dockable):
    """Menu bar that fits at the top of a frame
    """
    border = 1
    def __init__(self):
        Dockable.__init__(self, getDesktop().width, 20)
        self.setShow(1)
        self.menus = []
        self.hitList = []
        self.active = None
        self.highlight = None
        self.registerEvent(pyui.locals.LMOUSEBUTTONDOWN, self._pyuiMouseDown)
        self.registerEvent(pyui.locals.LMOUSEBUTTONUP, self._pyuiMouseUp)
        self.registerEvent(pyui.locals.MOUSEMOVE, self._pyuiMouseMotion)
        self.registerEvent(pyui.locals.MENU_EXIT, self._pyuiMenuExit)

    def draw(self, renderer):
        #print "manu bar:", self.rect
        if self.show:
            getTheme().drawMenuBar(self.rect)
            h = self.height - 2 * self.border
            x = self.border
            self.hitList = []
            for menu in self.menus:
                rect = getTheme().drawMenuBarItem( (x, self.parent.rect[1]+self.border+self.rect[1], 1, h),
                                     menu.menuTitle, menu == self.highlight)
                menu.moveto(self.posX + rect[0] - self.border, self.posY + self.height)
                print "drawing hit list at ", rect, self.rect
                self.hitList.append((menu, rect))
                x += rect[2]
        
    def addMenu(self, menu):
        self.menus.append(menu)
        menu.parent = self
        menu.calcSize()

    def setActiveMenu(self, menu):
        if self.active:
            self.active.setShow(0)
        self.active = menu
        self.highlight = menu
        if ( menu ):
            menu.setShow(1)
        self.setDirty()

    def _pyuiMenuExit(self, event):
        if self.active:
            self.setActiveMenu(None)
            return 1
        return 0

    def _pyuiMouseMotion(self, event):
        print "mouse:", event.pos
        # give active child first chance
        if self.active and self.active._pyuiMouseMotion(event):
            return 1
        menu = self.findMenu(event.pos)
        if self.active:
            if menu and menu != self.active:
                self.setActiveMenu(menu)
        else:
            if menu != self.highlight:
                self.highlight = menu
                self.setDirty()
        return 0
                
    def _pyuiMouseDown(self, event):
        # give active child first chance
        if self.active and self.active._pyuiMouseDown(event):
            return 1
        menu = self.findMenu(event.pos)
        if menu != self.active:
            self.setActiveMenu(menu)
            return 1
        return 0

    def _pyuiMouseUp(self, event):
        # give active child first chance
        if self.active and self.active._pyuiMouseUp(event):
            return 1
        menu = self.findMenu(event.pos)
        if self.active and not menu:
            self.setActiveMenu(None)
            return 1
        return 0

    def setParent(self, parent):
        Base.setParent(self, parent)

    def findMenu(self, pos):
        if not self.hit(pos):                             
            return None


        # put hit position in window relative coords
        x = pos[0] - self.rect[0]
        y = pos[1] - self.rect[1]
        #print "findMenu:", x, y, self.hitList
        for (menu, rect) in self.hitList:
            if x >= rect[0] and y >= rect[1] and x < rect[0]+rect[2] and y < rect[1]+rect[3]:
                #print "findMenu hit:", menu
                return menu
        else:
            return None

    def destroy(self):
        for menu in self.menus:
            menu.destroy()
            del menu
        self.menus = None
        self.hitList = None
        Dockable.destroy(self)

class MenuItem:
    """Used by menu widget to track items. Can have an icon 16x16 in size.
    """
    def __init__(self, handler, text, subMenu):
        self.handler = handler
        self.text = text
        (width, height) = getRenderer().getTextSize(text, getTheme().defaultFont)
        self.width = width
        self.subMenu = subMenu
        self.icon = None
        self.rect = (0,0,0,0)
        self.canActivate = handler or subMenu

    def setIcon(self, icon):
        self.icon = icon

class FrameMenu(Base):
    """Menu that can be floating or attached to a menuBar.
    """
    iconWidth = 20  # fixme[pmf]: actually defined in theme
    minWidth = 20
    border = 4
    def __init__(self, title):
        Base.__init__(self)
        self.resize(100,100)
        self.menuTitle = title
        self.width = self.minWidth
        self.items = []
        self.active = None
        self.subActive = None
        self.setShow(0)
        # no register events; we'll receive events from the menu bar (or other parent menu)

    def draw(self, renderer):
        if self.show:
            getTheme().drawMenu((self.rect[0],rect[1],self.width, self.height))
            y = self.border
            for item in self.items:
                rect = getTheme().drawMenuItem( (self.border, y, self.width - self.border*2, 0),
                                     item.text, item == self.active, item.icon )
                item.rect = (rect[0], rect[1], rect[2], rect[3])
                y += rect[3]

    def setShow(self, show):
        if show:
            self.getFocus()
        if self.subActive:
            self.subActive.setShow(0)
        self.subActive = None
        self.active = None
        Base.setShow(self,show)

    def setActive(self, item):
        if item == self.active:
            return
        if self.subActive:
            self.subActive.setShow(0)
            
        # can't use menu items without an event attached
        if item and not item.canActivate:
            self.active = None
            return
        
        self.active = item
        if item:
            self.subActive = item.subMenu
            if self.subActive:
                self.activateSubmenu(item)
        self.setDirty()

    def _pyuiMouseMotion(self, event):
        # give active submenu first chance
        if self.subActive and self.subActive._pyuiMouseMotion(event):
            return 1
        item = self.findItem(event.pos)
        if item and item != self.active:
            self.setActive(item)
        return item != None

    def _pyuiMouseDown(self, event):
        # give active submenu first chance
        if self.subActive and self.subActive._pyuiMouseDown(event):
            return 1
        item = self.findItem(event.pos)
        if item != self.active:
            self.setActive(item)
        return item != None

    def _pyuiMouseUp(self, event):
        # give active submenu first chance
        if self.subActive and self.subActive._pyuiMouseUp(event):
            return 1
        item = self.findItem(event.pos)
        if item != self.active:
            self.setActive(item)
        if not item:
            return 0
        if item.subMenu:
            return 1
        if not item.canActivate:
            return 1
        print "picked menu item:", item.text
        if item.handler:
            item.handler(item)
        #e = self.postEvent(item.eventType)
        #e.item = item
        self.postEvent(pyui.locals.MENU_EXIT)
        return 1

    def activateSubmenu(self, item):
        self.subActive = item.subMenu
        (x,y) = (self.posX + item.rect[2], self.posY + item.rect[1] - self.border)
        if x + item.subMenu.width > getDesktop().width:
            # try moving to left of menu
            x -= self.width + item.subMenu.width
            if x < 0:
                # the menu won't fit, nor to the left of the parent menu, nor to the right. What to do?
                # Align the submenu to the right margin.
                x = getDesktop().width - item.subMenu.width
                item.subMenu.moveto(getDesktop().width - item.subMenu.width, self.posY + item.subMenu.height * getTheme().defaultTextHeight)
        if y + item.subMenu.height > getDesktop().height:
            y = getDesktop().height - item.subMenu.height
            if y < 0:
                raise "No room for submenu!"
        item.subMenu.moveto(x, y)
        item.subMenu.setShow(1)
        
    def addItem(self, title, handler = None, subMenu = None):
        """Add an item to the menu.
        """
        if subMenu:
            title = title + "..."
        newItem = MenuItem(handler, title, subMenu)
        self.items.append(newItem)

        h = getTheme().defaultTextHeight * len(self.items) + self.border * 2
        w = self.minWidth
        for item in self.items:
            if item.width > w:
                w = item.width
        self.resize(w + self.iconWidth * 2 + self.border * 2, h)
        self.setDirty()
        return newItem

    def changeItemTitle(self, oldTitle, newTitle, newHandler):
        for item in self.items:
            if item.text == oldTitle:
                item.text = newTitle
                item.handler = newHandler
                self.setDirty(1)
                break
        
            
    def findItem(self, pos):
        if not self.hit(pos):
            return None

        # put hit position in window relative coords
        x = pos[0] - self.posX
        y = pos[1] - self.posY
        for item in self.items:
            if x >= item.rect[0] and y >= item.rect[1] and x < item.rect[0]+item.rect[2] and y < item.rect[1]+item.rect[3]:
                return item
        return None
            
