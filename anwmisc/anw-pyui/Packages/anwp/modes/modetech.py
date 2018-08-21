# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modetech.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Technology Tree in ANW
# ---------------------------------------------------------------------------
import pygame
import string
import types

import pyui
import anwp.sl.entity
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.techmenu
import anwp.gui.techinfo
import anwp.func.globals


class TechEntity(anwp.sl.entity.Entity):
    """Represents a Tech Entity in the Technology Tree"""
    def __init__(self, mode, category, myTechDict):
        self.mode = mode
        self.myTechDict = myTechDict
        self.techID = myTechDict['id']
        self.techAge = myTechDict['techAge']
        (tech, color) = string.split(myTechDict['imageFile'], '_')
        self.color1 = anwp.func.globals.colors[color]
        if color == 'red':
            self.color2 = anwp.func.globals.colors['yellow']
            self.color3 = anwp.func.globals.colors['white']
        elif color == 'yellow':
            self.color2 = anwp.func.globals.colors['blue']
            self.color3 = anwp.func.globals.colors['black']
        else:
            self.color2 = anwp.func.globals.colors['black']
            self.color3 = self.color2
        anwp.sl.entity.Entity.__init__(self, category, None)

class ModeTech(mode.Mode):
    """This represents the Technology Tree parent Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'TECH'
        self.techAge = 0
        
        # create gui panels
        self.mainMenu = anwp.gui.techmenu.MainMenuTech(self, self.game.app)
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.techInfo = None
        
        # create the world
        self.worldWidth = 1600
        self.worldHeight = 4000
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)

    def createSims(self):
        """Create the Tech Tree, it contains:
           - Line Connections between techs
           - Tech Entities
           - Tech Descriptions
        """
        import anwp.sims
        # create tech sims
        for techID, techDict in self.game.myTech.iteritems():
            if techDict['techAge'] == self.techAge:
                imageFileName = '%s%s.png' % (self.game.app.simImagePath, techDict['imageFile'])
                    
                # create sim
                sim = TechEntity(self, anwp.sims.categories.ClickableCategory(imageFileName,'tech'), techDict)
                                
                # add sim to world
                self.sims.append(sim)
                x = techDict['x']
                y = techDict['y']
                facing = 0
                speed = 0
                sim.turnRate = 0
                self.world.addToWorld(sim, x, y, facing, speed)
    
    def getTechOrders(self):
        """Ask the Server for an updated Tech Orders list"""
        try:
            serverResult = self.game.server.getEmpireOrders(self.game.authKey, 'techOrders')
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.myEmpire['techOrders'] = serverResult
        except:
            self.modeMsgBox('getTechOrders->Connection to Server Lost')
    
    def cancelTechOrder(self, orderList, techID):
        """Send a Cancel Tech Order to Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelTechOrder(self.game.authKey, orderID)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshTechOrder(techID)
        except:
            self.modeMsgBox('cancelTechOrder->Connection to Server Lost, Login Again')
        
    
    def refreshTechOrder(self, techID):
        """Perform refresh to accomodate tech Order"""
        try:
            # get tech update
            self.getTechOrders()
            
            # get empire update
            self.getEmpireUpdate(['rpUsed', 'rpAvail'])
            
            # refresh gui panel if still hovering over it
            if self.techInfo.currentID == techID:
                self.techInfo.panel.populate(self.techInfo.panel.myTechDict)
        except:
            self.modeMsgBox('refreshTechOrder error ')
            
    def addTechOrder(self, amount, techID):
        """Send an Add Tech Request to the Server"""
        try:
            dOrder = {'type':techID, 'value':amount, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addTechOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshTechOrder(techID)
        except:
            self.modeMsgBox('addTechOrder->Connection to Server Lost, Login Again') 

    def updateSelector(self):
        """Update the x, y position of the selector to point to the selector"""
        self.simSelector.posX = self.selected.posX
        self.simSelector.posY = self.selected.posY-13
    
    def onMouseDown(self, event):
        """Allow dynamic picking of an object within world"""
        # determine where mouse is
        (worldX, worldY) = anwp.sl.engine.screenToWorld(event.pos[0], event.pos[1])
        sim = self.world.checkPoint(worldX, worldY)
        
        # if selecting nothing, remove panel and selector
        if sim == None:
            if self.techInfo <> None:
                self.techInfo.destroy()
                self.techInfo = None
            self.removeSelector()
        else:
            # create panel and selector if they do not exist
            if self.techInfo == None:
                self.techInfo = myPanel = anwp.gui.techinfo.TechInfoFrame(self, self.game.app)
            self.createSelector()
        
        # update observer
        if self.techInfo <> None and sim <> None:
            self.updateObserver(sim, 'techInfo')
    
    def draw(self):
        """Draw standard World information each frame"""
        self.bufferX = (self.appWidth/2) - self.viewX
        self.bufferY = (self.appHeight/2) - self.viewY
        anwp.sl.engine.clear()
        ##self.drawBorders()
        self.drawTechLines()
        
        # render engine
        anwp.sl.engine.render()
        self.drawTechInfo()
    
    def drawTechInfo(self):
        """Tech Info (Names and Numbers) are rendered outside system drawcallback due to 
        problems drawing in drawcallback of system"""
        for sim in self.sims:
            # for each tech sim
            nameList = string.split(sim.myTechDict['name'], ' ')
            i = 0
            (x,y) = anwp.sl.engine.worldToScreen(sim.myTechDict['x'], sim.myTechDict['y'])
            for name in nameList:
                # draw tech name under tech symbol
                pyui.desktop.getRenderer().drawText(name, (x-30,(y+40)+(i*15)),
                                                sim.color1, self.game.app.systemFont, 
                                                flipped = 1)
                i += 1
            
            # draw currentPoints and requiredPoints on top of tech symbol
            pyui.desktop.getRenderer().drawText(str(sim.myTechDict['currentPoints']), (x-20,y-3), sim.color2, 
                                                self.game.app.systemFont, flipped = 1)
            pyui.desktop.getRenderer().drawText(str(sim.myTechDict['requiredPoints']), (x-20,y+15), sim.color3, 
                                                self.game.app.systemFont, flipped = 1)
        
        # display current and used research points
        text = 'Research Points (Avail/Total): (%d/%d)' % (self.game.myEmpire['rpAvail'], self.game.myEmpire['rpAvail']+self.game.myEmpire['rpUsed'])
        pyui.desktop.getRenderer().drawText(text, (20, self.game.displayHeight - 40), anwp.func.globals.colors['white'], self.game.app.systemFont, flipped = 1)
            
                
    def drawTechLines(self):
        """Draw the Tech Lines"""
        # draw tech lines
        techLinesObj = getattr(self.game, 'techLines%d' % self.techAge)
        for item in techLinesObj:
            anwp.sl.engine.drawLine(item[0]+self.bufferX, item[1]+self.bufferY, item[2]+self.bufferX, item[3]+self.bufferY, pyui.colors.green)

class ModeTech1(ModeTech):
    """This is the 1st Age of Technology Tree Mode"""
    def __init__(self, game):
        ModeTech.__init__(self, game)
        self.name = 'TECH1'
        self.techAge = 1
        self.mainMenu.panel.disableButtons()
        
        # create the sims for the world
        self.createSims()

class ModeTech2(ModeTech):
    """This is the 2nd Age of Technology Tree Mode"""
    def __init__(self, game):
        ModeTech.__init__(self, game)
        self.name = 'TECH2'
        self.techAge = 2
        self.mainMenu.panel.disableButtons()
        
        # create the sims for the world
        self.createSims()
    
class ModeTech3(ModeTech):
    """This is the 3rd Age of Technology Tree Mode"""
    def __init__(self, game):
        ModeTech.__init__(self, game)
        self.name = 'TECH3'
        self.techAge = 3
        self.mainMenu.panel.disableButtons()
        
        # create the sims for the world
        self.createSims()