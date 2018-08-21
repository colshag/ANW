# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modedesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Design Mode in ANW
# ---------------------------------------------------------------------------
import pygame
import types
import string

import pyui
import anwp.sl.world
import mode
import anwp.func.globals
import anwp.gui.mainmenu
import anwp.gui.footer
import anwp.gui.quadinfo
import anwp.gui.shipdesigninfo

class ModeDesign(mode.Mode):
    """This is the StarShip Design Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'DESIGN'

        # load initial default design
        compDict = {'fore':[], 'aft':[], 'port':[], 'star':[]}
        weapDict = {}
        self.myShipDesign = self.getShipDesign('1', compDict, weapDict)
        
        # create gui panels
        self.mainMenu = anwp.gui.mainmenu.MainMenu(self, self.game.app)
        self.mainMenu.panel.btnDesign.disable()
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.mainDesign = anwp.gui.shipdesigninfo.ShipDesignInfoFrame(self, self.game.app, self.myShipDesign)
        
        top = self.mainMenu.height+10
        width = (self.appWidth/4)-20
        height = self.appHeight/3
        self.aftQuadInfo = anwp.gui.quadinfo.QuadInfoFrame(self, self.game.app, self.myShipDesign.quads['aft'], width+10, top+height+150, width, height)
        self.portQuadInfo = anwp.gui.quadinfo.QuadInfoFrame(self, self.game.app, self.myShipDesign.quads['port'], 0, height, width, height)
        self.foreQuadInfo = anwp.gui.quadinfo.QuadInfoFrame(self, self.game.app, self.myShipDesign.quads['fore'], width+10, top, width, height)
        self.starQuadInfo = anwp.gui.quadinfo.QuadInfoFrame(self, self.game.app, self.myShipDesign.quads['star'], width*2+20, height, width, height)
        
        # create the world
        self.worldWidth = 2000
        self.worldHeight = 2000
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight))
        self.renderer.setBackMethod(self.draw)

    def draw(self):
        """Draw Design World information each frame"""
        anwp.sl.engine.clear()
        anwp.sl.engine.drawImage(0, 0, self.appWidth, self.appHeight, self.backgroundImage)
        self.drawShipHull()
        self.drawDesignInfo()
        self.drawAngles()
        anwp.sl.engine.render()
    
    def drawAngles(self):
        """Draw Angles image"""
        x = 0
        width = self.portQuadInfo.width
        height = self.portQuadInfo.height*0.8
        y = self.appHeight - self.mainMenu.height - height
        anwp.sl.engine.drawImage(x,y,width,height,'%sangles.png' % self.game.app.genImagePath)
    
    def drawDesignInfo(self):
        """Draw the current design info"""
        i = 0
        shipMass = self.myShipDesign.mass
        for (item, value) in [['Battery:', self.myShipDesign.maxBattery], ['Max Power:', self.myShipDesign.maxPower],
                              ['Ship Mass:', shipMass], ['Ship Accel:', (self.myShipDesign.accel)], 
                              ['Rotation:', (self.myShipDesign.rotation)],
                              ['Radar:', self.myShipDesign.radar],
                              ['Jamming:', self.myShipDesign.jamming],
                              ['Transport:', self.myShipDesign.maxTransport],
                              ['Repair:', self.myShipDesign.repair]
                              ]:
            x = self.aftQuadInfo.posX+self.aftQuadInfo.width + 10
            y = self.mainMenu.height + 20 + i*20
            pyui.desktop.getRenderer().drawText('%s' % item, 
                                                (x,y),
                                                pyui.colors.white, self.game.app.systemFont, 
                                                flipped = 1)
            pyui.desktop.getRenderer().drawText('%d' % value, 
                                                (x+150,y),
                                                pyui.colors.yellow, self.game.app.systemFont, 
                                                flipped = 1)
            i += 1
        
        
        # draw total cost
        y = self.mainFooter.posY - 110
        pyui.desktop.getRenderer().drawText('TOTAL COST:', 
                                                (x,y),
                                                pyui.colors.white, self.game.app.systemFont, 
                                                flipped = 1)

        for (color, item) in [['green', 'CR'], ['blue', 'AL'],
                               ['yellow', 'EC'], ['red', 'IA']]:
            y = y + 20
            value = getattr(self.myShipDesign, 'cost%s' % item)
            pyui.desktop.getRenderer().drawText('COST (%s): %d' % (item, value), 
                                                (x,y),
                                                anwp.func.globals.colors[color], self.game.app.systemFont, 
                                                flipped = 1)
        
        # draw weapon fire rate information
        totalAMSPower = 0.0
        totalWeapPower = 0.0
        amsFireRate = 0.0
        weapFireRate = 0.0
        for position, myQuad in self.myShipDesign.quads.iteritems():
            for weaponID, myWeapon in myQuad.weapons.iteritems():
                if myWeapon.myWeaponData.AMS == 1:
                    totalAMSPower += myWeapon.myWeaponData.maxPower
                else:
                    totalWeapPower += myWeapon.myWeaponData.maxPower
        
        if self.myShipDesign.maxPower:
            amsFireRate = totalAMSPower/self.myShipDesign.maxPower
            weapFireRate = totalWeapPower/self.myShipDesign.maxPower

        x = 10
        y = self.mainFooter.posY - 110
        for (description, value, unit) in [['AMS Power:', '%d' % totalAMSPower, 'kw'],
                                     ['Weap Power:', '%d' % totalWeapPower, 'kw'],
                                     ['AMS Fire:', '%.2f' % amsFireRate, 'sec'],
                                     ['Weap Fire:', '%.2f' % weapFireRate, 'sec']]:
            y = y + 20
            pyui.desktop.getRenderer().drawText(description, 
                                                (x,y),
                                                pyui.colors.white, self.game.app.systemFont, 
                                                flipped = 1)
            pyui.desktop.getRenderer().drawText('%s %s' % (value,unit), 
                                                (x+150,y),
                                                pyui.colors.yellow, self.game.app.systemFont, 
                                                flipped = 1)
    
    def drawShipHull(self):
        """Draw the selected Ship Hull"""
        myShipHull = self.game.shiphulldata[self.myShipDesign.shipHullID]
        color1 = self.game.myEmpire['color1']
        color2 = self.game.myEmpire['color2']
        name = '%sb_%s_%s' % (string.lower(myShipHull.abr), color1, color2)
        filename = '%s%s.png' % (self.game.app.simImagePath, name)
        x = self.portQuadInfo.posX
        y = self.foreQuadInfo.posY
        width = self.starQuadInfo.posX + self.starQuadInfo.width - self.portQuadInfo.posX
        height = self.aftQuadInfo.posY + self.aftQuadInfo.height - self.foreQuadInfo.posY
        anwp.sl.engine.drawImage(x, y, width, height, filename)

    def refreshPanels(self, disable=0):
        """Refresh the Design panels to reflect the loading of a new design"""
        self.mainDesign.panel.populate(self.myShipDesign)
        self.aftQuadInfo.panel.populate(self.myShipDesign.quads['aft'])
        self.foreQuadInfo.panel.populate(self.myShipDesign.quads['fore'])
        self.portQuadInfo.panel.populate(self.myShipDesign.quads['port'])
        self.starQuadInfo.panel.populate(self.myShipDesign.quads['star'])
        
        if disable == 1:
            self.mainDesign.panel.getPanel(1).btnAdd.disable()
            self.mainDesign.panel.getPanel(1).lstQuad.clearSelection()
            self.mainDesign.panel.getPanel(2).btnAdd.disable()
            self.mainDesign.panel.getPanel(2).lstQuad.clearSelection()

    def resetDesign(self, hullID='1'):
        """Reset Design to a scout"""
        compDict = {'fore':[], 'aft':[], 'port':[], 'star':[]}
        weapDict = {}
        self.myShipDesign = self.getShipDesign(hullID, compDict, weapDict)
        self.refreshPanels(1)

    def removeShipDesign(self, ID):
        """Remove Ship Design"""
        try:
            serverResult = self.game.server.removeShipDesign(self.game.authKey, ID)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                # design removed from server, remove from client
                del self.game.shipDesigns[ID]
                self.resetDesign()
        except:
            self.modeMsgBox('removeShipDesign->Connection to Server Lost, Login Again')
    
    def updateDesign(self, disable=0):
        """Update the current design"""
        self.myShipDesign.setMyStatus()
        self.refreshPanels(disable)
        