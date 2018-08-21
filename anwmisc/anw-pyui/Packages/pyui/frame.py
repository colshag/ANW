import layouts
import pyui

from pyui.desktop import getDesktop, getTheme, getRenderer

from pyui.base import Base, Panel, Window

class Frame(Window):
    """A frame is a window that has a titlebar and borders. it is resizable and movable by dragging the titlebar.
    """
    def __init__(self, x, y, w, h, title, topmost = 0):
        self.theme = getTheme()
        self.title = title
        self._menuBar = None
        self.innerRect = (0,0,w,h)
        
        Window.__init__(self, x, y, w, h, topmost)
        self.setTitle(self.title)

        self.resize(w, h)
        
        self.registerEvent(pyui.locals.LMOUSEBUTTONDOWN, self._pyuiMouseDown)
        self.registerEvent(pyui.locals.LMOUSEBUTTONUP, self._pyuiMouseUp)
        self.registerEvent(pyui.locals.MOUSEMOVE, self._pyuiMouseMotion)
        self.moving = 0
        self.resizing = 0
        self.startX = 0
        self.startY = 0
        self.hitList = []
        self.resizingCursor=0
        self.movingCursor=0
        self.backImage=None
        self.calcInnerRect()
        self.placeInnerObjects()

    def placeInnerObjects(self):
        self._panel.moveto(self.innerRect[0], self.innerRect[1])
        self._panel.resize(self.innerRect[2], self.innerRect[3])
        if self._menuBar:
            self._menuBar.resize(self.innerRect[2], self._menuBar.rect[3])
        
    def calcInnerRect(self):
        """calculate the size of the inner rectangle of the frame. this excludes
        the frame borders and the menubar.
        """
        left = 0
        top = 0
        width = self.width
        height = self.height

        if self._menuBar:
            top += self._menuBar.height
            height -= self._menuBar.height

        left += self.theme.getFrameBorderLeft()
        width -= (self.theme.getFrameBorderLeft() + self.theme.getFrameBorderRight())
        top += self.theme.getFrameBorderTop()
        height -= (self.theme.getFrameBorderBottom() + self.theme.getFrameBorderTop())

        self.innerRect = (left, top, width, height)
        
    def setMenuBar(self, menuBar):
        if self._menuBar:
            Base.removeChild(self, self._menuBar)
        self._menuBar = menuBar
        
        Base.addChild(self, self._menuBar)
        self._menuBar.setWindow(self)
        
        self._menuBar.moveto( self.theme.getFrameBorderLeft(), self.theme.getFrameBorderTop() )
        self._menuBar.resize( self.innerRect[2], self._menuBar.height)
        self.calcInnerRect()
        self.placeInnerObjects() 
        
    def setTitle(self, title):
        self.title = title

    def setBackImage(self, filename):
        self.backImage = filename
        
    def draw(self, renderer):
        """Draws to the actual frame if the renderer requires it.
        """
        if not self.show:
            return
        self.hitList = getTheme().drawFrame( (0,0,self.width, self.height), self.title, self.backImage)
        self._panel.draw(renderer)
        if self._menuBar:
            self._menuBar.draw(renderer)
        
    def replacePanel(self, panel):
        Window.replacePanel(self, panel)
        self.calcInnerRect()
        self.placeInnerObjects()

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
            self.frameMove( mouseX - self.startX, mouseY - self.startY)
            getRenderer().moveWindow(self.handle, self.posX, self.posY)
            return 1
        if self.resizing:
            mouseX = event.pos[0] - self.posX
            mouseY = event.pos[1] - self.posY
            if mouseX < 64:
                mouseX = 64
            if mouseY < 64:
                mouseY = 64
            self.frameResize( self.width + mouseX - self.startX, self.height + mouseY - self.startY)
            (self.startX, self.startY) = (mouseX, mouseY)
            return 1

        # set the proper cursor
        regionId = self.hitFrameRegion(event.pos)
        if regionId == pyui.locals.HIT_FRAME_RESIZE_BOTTOM_RIGHT:        
            self.resizingCursor=1
            self.theme.setResizeCursor()
        elif self.resizingCursor:
            self.resizingCursor=0
            self.theme.setArrowCursor()

        if regionId == pyui.locals.HIT_FRAME_MOVE:            
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
            return self.frameClose()
        
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
        self.calcInnerRect()
        self.placeInnerObjects()

    def _pyuiCloseButton(self):
        self.theme.setArrowCursor()        
        self.destroy()
        return 1            

    def handleEvent(self, event):
        """ do menu, then panel
        """
        if not self.show:
            return
        if self._menuBar:
            if self._menuBar.handleEvent(event):
                return 1
        if self._panel:
            if self._panel.handleEvent(event):
                return 1
        if self.eventMap.has_key(event.type):
            if self.eventMap[event.type](event):
                return 1
        return 0

    def frameResize(self, w, h):
        """Called when the resize corner is dragged.
        Override this to customize resizing behavior.
        """
        self.resize(w,h)

    def frameMove(self, x, y):
        """Called when the frame is dragged around.
        Override this to customize dragging behavior.
        """
        self.move(x, y)

    def frameClose(self):
        """Called when the frame close button is clicked
        Override this to customize the close button behavior.
        """
        return self._pyuiCloseButton()

class FrameMenuBar(Base):
    """Menu bar that fits at the top of the screen or the top of a window.
    """
    border = 1
    def __init__(self):
        Base.__init__(self)
        self.height = 20
        self.setShow(1)
        self.menus = []
        self.menuWidth = 0
        self.active = None
        self.highlight = None
        self.registerEvent(pyui.locals.LMOUSEBUTTONDOWN, self._pyuiMouseDown)
        self.registerEvent(pyui.locals.LMOUSEBUTTONUP, self._pyuiMouseUp)
        self.registerEvent(pyui.locals.MOUSEMOVE, self._pyuiMouseMotion)
        self.registerEvent(pyui.locals.MENU_EXIT, self._pyuiMenuExit)

    def draw(self, renderer):
        if self.show:
            getTheme().drawMenuBar(self.windowRect)
            h = self.height-4
            x = self.border+4
            y = self.windowRect[1] + 2
            for menu in self.menus:
                rect = getTheme().drawMenuBarItem( (x, y, menu.width, h),
                                     menu.menuTitle, menu == self.highlight)
                #menu.moveto(self.posX + rect[0] - self.border, self.posY + self.height)
                x += menu.width
            for m in self.menus:
                m.draw(renderer)
        
    def addMenu(self, menu):
        self.menus.append(menu)
        self.addChild(menu)

        menu.moveto(self.menuWidth, self.windowRect[1]+self.height)
        self.menuWidth += (menu.width)

    def setActiveMenu(self, menu):
        if self.active and menu != self.active:
            self.active.setShow(0)
            self.active = None
        if menu and len(menu.items) == 0:
            return
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
        x = pos[0] - self.window.rect[0]
        y = pos[1] - self.window.rect[1]
        for menu in self.menus:
            if pos[0] > menu.rect[0] and pos[0] < menu.rect[0] + menu.rect[2]:
                return menu
        else:
            return None

    def destroy(self):
        for menu in self.menus:
            menu.destroy()
            del menu
        self.menus = None


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

class FrameMenu(Base):
    """Menu attached to a menuBar.
    """
    iconWidth = 20  # fixme[pmf]: actually defined in theme
    minWidth = 20
    minHeight = 20
    border = 4
    def __init__(self, title):
        Base.__init__(self)
        self.menuTitle = "  " + title
        self.width = getRenderer().getTextSize(title)[0]+12
        
        self.height = self.minHeight
        self.items = []
        self.active = None
        self.subActive = None
        self.setShow(0)
        # no register events; we'll receive events from the menu bar (or other parent menu)

    def draw(self, renderer):
        if self.show:
            getTheme().drawMenu(self.windowRect)
            y = self.windowRect[1]
            for item in self.items:
                rect = getTheme().drawMenuItem( (self.posX+self.border+4, y+4, self.width - self.border*2, 0),
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
        if not self.show:
            return 0
        # give active submenu first chance
        if self.subActive and self.subActive._pyuiMouseMotion(event):
            return 1
        item = self.findItem(event.pos)
        if item and item != self.active:
            self.setActive(item)
        if item == None:
            self.setActive(None)
        return 1

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
        if item.handler:
            item.handler(item)
        #e = self.postEvent(item.eventType)
        #e.item = item
        self.postEvent(pyui.locals.MENU_EXIT)
        return 1

##    def activateSubmenu(self, item):
##        self.subActive = item.subMenu
##        (x,y) = (self.posX + item.rect[2], self.posY + item.rect[1] - self.border)
##        if x + item.subMenu.width > getDesktop().width:
##            # try moving to left of menu
##            x -= self.width + item.subMenu.width
##            if x < 0:
##                # the menu won't fit, nor to the left of the parent menu, nor to the right. What to do?
##                # Align the submenu to the right margin.
##                x = getDesktop().width - item.subMenu.width
##                item.subMenu.moveto(getDesktop().width - item.subMenu.width, self.posY + item.subMenu.height * getTheme().defaultTextHeight)
##        if y + item.subMenu.height > getDesktop().height:
##            y = getDesktop().height - item.subMenu.height
##            if y < 0:
##                raise "No room for submenu!"
##        item.subMenu.moveto(x, y)
##        item.subMenu.setShow(1)
        
    def addItem(self, title, handler = None, subMenu = None):
        """Add an item to the menu. NOTE: submenus dont work for now...
        """
        if subMenu:
            raise "Submenus not functioning yet..."
        
        newItem = FrameMenuItem(handler, title, subMenu)
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
        x = pos[0] - self.window.rect[0]
        y = pos[1] - self.window.rect[1]
        for item in self.items:
            if x >= item.rect[0] and y >= item.rect[1] and x < item.rect[0]+item.rect[2] and y < item.rect[1]+item.rect[3]:
                return item
        return None

