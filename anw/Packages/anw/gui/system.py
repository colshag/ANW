# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# system.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The system represents one System object in map mode
# ---------------------------------------------------------------------------
from pandac.PandaModules import Vec3
import direct.directbase.DirectStart
from anw.gui import textonscreen, rootsim
from anw.func import globals, funcs
        
class System(rootsim.RootSim):
    """A System Gui for interacting with player Solar Systems in map mode"""
    def __init__(self, path, mode, systemDict):
        self.systemDict = systemDict
        self.id = systemDict['id']
        self.empireID = systemDict['myEmpireID']
        self.color1 = globals.empires[int(self.empireID)]['color1']
        self.color2 = globals.empires[int(self.empireID)]['color2']
        rootsim.RootSim.__init__(self, path, 'planet%s' % self.empireID, 
                                 'planet_sphere', 0)
        self.resourceSize = 0.25
        self.mode = mode
        self.game = mode.game
        self.simCity = None
        self.textName = None
        self.textCityNum = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        self.simAL = None
        self.simEC = None
        self.simIA = None
        
        self.simRS = None
        self.simJS = None
        self.simMF = None
        self.simFA = None
        self.simMA = None
        self.simSY = None
        self.simMI = None
        self.simWG = None
        
        self.simAF = None
        self.simCM = None
        self.simSS = None
        self.simSC = None
        self.simDC = None
        self.simRC = None
        
        self.scale = .5 + .5*(self.systemDict['cities']/40.0)
        self.x = systemDict['x']
        self.z = systemDict['y']
        self.y = 20
        self.createMySim()
        self.armadaPos = {}
        self.armyPos = {}
        self.warpedArmadaPos = {}
        self.warpedArmyPos = {}
        self.setPositions()
    
    def setPositions(self):
        self.armadaPos = {}
        self.armyPos = {}
        self.warpedArmadaPos = {}
        self.warpedArmyPos = {}
        self.setMyPositions()
        self.setWarpedPositions()
        
    def setMyPositions(self):
        """Setup Positions as a list of empireIDs"""
        count = 0
        if self.id in self.game.myArmadas.keys():
            self.armadaPos[self.game.myEmpireID] = count
            count += 1
        if self.id in self.game.myArmies.keys():
            self.armyPos[self.game.myEmpireID] = count
            count += 1
        if self.id in self.game.otherArmadas.keys():
            for empireID in self.game.otherArmadas[self.id]:
                self.armadaPos[empireID] = count
                count += 1
        if self.id in self.game.otherArmies.keys():
            for empireID in self.game.otherArmies[self.id]:
                self.armyPos[empireID] = count
                count += 1
    
    def setWarpedPositions(self):
        """Setup Positions as a list of empireIDs"""
        count = 0
        if self.id in self.game.warpedArmadas.keys():
            self.warpedArmadaPos[self.game.myEmpireID] = count
            count += 1
        if self.id in self.game.warpedArmies.keys():
            self.warpedArmyPos[self.game.myEmpireID] = count
            
    def getMyArmadaPosition(self, empireID):
        """Return the x,z positions System wants to place Armada"""
        self.setMyPositions()
        x = self.x+1.15 + self.armadaPos[empireID]*0.35
        z = self.z+0.75
        return (x,z)
    
    def getMyWarpedArmadaPosition(self, empireID):
        """Return the x,z positions System wants to place Warped Armada"""
        self.setWarpedPositions()
        x = self.x+1.3 + self.warpedArmadaPos[empireID]*0.35
        z = self.z-0.25
        return (x,z)
    
    def getMyArmyPosition(self, empireID):
        """Return the x,z positions System wants to place Army"""
        self.setMyPositions()
        x = self.x+1.15 + self.armyPos[empireID]*0.35
        z = self.z+0.75
        return (x,z)
    
    def getMyWarpedArmyPosition(self, empireID):
        """Return the x,z positions System wants to place Warped Army"""
        self.setWarpedPositions()
        x = self.x+1.3 + self.warpedArmyPos[empireID]*0.35
        z = self.z-0.25
        return (x,z)
        
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.setColor()
        self.setPos()
        self.writeName()
        self.writeCityNum()
        self.createExtras()
        self.rotateSim()
        
    def createExtras(self):
        """Display Extra System Information if applicable"""
        if self.empireID == self.mode.game.myEmpireID:
            self.writeResources()
            self.writeProdResources()
            self.createIndustrySims()
            self.writeCitiesUsed()
    
    def writeCitiesUsed(self):
        """Write the cities used to cities available"""
        text = '%s/%s' % (self.systemDict['citiesUsed'],self.systemDict['cities'])
        self.textCityNum.myText.setText(text)
            
    def destroy(self):
        """Remove the beaker from game"""
        self.removeMyWidgets()
        self.sim.removeNode()
        self.clearText(self.textName)
        self.clearText(self.textCityNum)
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
    
    def writeName(self):
        """Write the system name"""
        text = funcs.getSystemName(self.systemDict)
        self.clearText(self.textName)
        self.textName = textonscreen.TextOnScreen(self.path, text, 0.25, font=1)
        self.textName.writeTextToScreen(self.x-0.9, self.y, self.z+1, wordwrap=14)
        self.textName.setColor(globals.colors[self.color1])
    
    def writeCityNum(self):
        """Write City Number"""
        text = '%s' % self.systemDict['cities']
        self.createSimCity(globals.colors[self.color1])
        self.textCityNum = textonscreen.TextOnScreen(self.path, text, 0.20, font=1)
        self.textCityNum.writeTextToScreen(self.x-1.5, self.y-0.1, self.z+0.86, wordwrap=10)
        self.textCityNum.setColor(globals.colors[self.color1])
    
    def writeResources(self):
        """Display any available resources"""
        self.resourceCount = 0
        for resource in ['AL','EC','IA']:
            value = self.systemDict[resource]
            if value > 0:
                myMethod = getattr(self, 'write%s' % resource)
                myMethod(self.x, self.y+0.05, self.z-1.3-(0.3*self.resourceCount), value)
                self.resourceCount += 1
    
    def writeProdResources(self):
        """Display if Resources Currently being Produced"""
        self.resourceCount = 0
        for resource in ['AL','EC','IA']:
            value = self.systemDict['prod%s' % resource]
            if value > 0:
                myMethod = getattr(self, 'createSim%s' % resource)
                myMethod(self.x-0.25, self.y+0.05, self.z-1.25-(0.3*self.resourceCount))
                self.resourceCount += 1
    
    def createSimAL(self, x, y, z):
        """Create the AL Sim"""
        self.simAL = loader.loadModelCopy('%s/plane' % self.path)
        self.simAL.setScale(0.2)
        self.simAL.reparentTo(render)
        self.simAL.setTransparency(1)
        tex = loader.loadTexture('%s/resource.png' % self.path)
        self.simAL.setTexture(tex, 0)
        self.simAL.setPos(x, y, z)
        self.simAL.setColor(globals.colors['guiblue2'])
        self.myWidgets.append(self.simAL)
    
    def createSimEC(self, x, y, z):
        """Create the EC Sim"""
        self.simEC = loader.loadModelCopy('%s/plane' % self.path)
        self.simEC.setScale(0.2)
        self.simEC.reparentTo(render)
        self.simEC.setTransparency(1)
        tex = loader.loadTexture('%s/resource.png' % self.path)
        self.simEC.setTexture(tex, 0)
        self.simEC.setPos(x, y, z)
        self.simEC.setColor(globals.colors['guiyellow'])
        self.myWidgets.append(self.simEC)
       
    def createSimIA(self, x, y, z):
        """Create the IA Sim"""
        self.simIA = loader.loadModelCopy('%s/plane' % self.path)
        self.simIA.setScale(0.2)
        self.simIA.reparentTo(render)
        self.simIA.setTransparency(1)
        tex = loader.loadTexture('%s/resource.png' % self.path)
        self.simIA.setTexture(tex, 0)
        self.simIA.setPos(x, y, z)
        self.simIA.setColor(globals.colors['guired'])
        self.myWidgets.append(self.simIA)
    
    def createSimCity(self, color):
        """Create the City Sim"""
        self.simCity = loader.loadModelCopy('%s/plane' % self.path)
        self.simCity.setScale(0.4)
        self.simCity.reparentTo(render)
        self.simCity.setTransparency(1)
        tex = loader.loadTexture('%s/empire%s.png' % (self.path, self.empireID))
        self.simCity.setTexture(tex, 0)
        self.simCity.setPos(self.x-1.25, self.y+0.05, self.z+1.28)
        self.simCity.setColor(color)
        self.myWidgets.append(self.simCity)
    
    def clearIndustrySims(self):
        """Remove all Industry Indicator Sims"""
        for id in funcs.sortStringList(self.mode.game.industrydata.keys()):
            industryData = self.mode.game.industrydata[id]
            code = self.mode.game.industrydata[id].abr[1:]
            myAttr = getattr(self, 'sim%s' % code)
            if myAttr != None:
                myAttr.removeNode()
        
    def createIndustrySims(self):
        """Create all Industry Indicator Sims"""
        count = 0
        count2 = 0
        hasSY = 0
        for id in funcs.sortStringList(self.mode.game.industrydata.keys()):
            industryData = self.mode.game.industrydata[id]
            oldNum = self.systemDict['myOldIndustry'][id]
            newNum = self.systemDict['myIndustry'][id]
            if oldNum > 0 or newNum > 0:
                code = self.mode.game.industrydata[id].abr[1:]
                color = funcs.getFutureColor(newNum, oldNum)
                if code == 'SY':
                    hasSY = 1
                if code not in ['AF', 'CM', 'SS', 'SC', 'DC', 'RC']:
                    myMethod = getattr(self, 'createSim%s' % code)
                    myMethod(color, count)
                    count += 1
                else:
                    myMethod = getattr(self, 'createSim%s' % code)
                    myMethod(color, count2)
                    count2 += 1
        if hasSY == 0 and self.systemDict['availSYC'] > 0:
            self.createSimSY(globals.colors['guiwhite'], count)
    
    def getIndustryPosition2(self, count):
        """Get Industry Position based on number of industry"""
        if count <= 2:
            x = -1.1 -count*0.3
            z = -0.6
        else:
            num = count - 3
            x = -1.3 -num*0.3
            z = -0.2
        return (x,z)
    
    def createSimAF(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simAF = loader.loadModelCopy('%s/plane' % self.path)
        self.simAF.setScale(0.25)
        self.simAF.reparentTo(render)
        self.simAF.setTransparency(1)
        tex = loader.loadTexture('%s/af.png' % self.path)
        self.simAF.setTexture(tex, 0)
        self.simAF.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simAF.setColor(color)
        self.myWidgets.append(self.simAF)
    
    def createSimCM(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simCM = loader.loadModelCopy('%s/plane' % self.path)
        self.simCM.setScale(0.25)
        self.simCM.reparentTo(render)
        self.simCM.setTransparency(1)
        tex = loader.loadTexture('%s/cm.png' % self.path)
        self.simCM.setTexture(tex, 0)
        self.simCM.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simCM.setColor(color)
        self.myWidgets.append(self.simCM)
    
    def createSimSS(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simSS = loader.loadModelCopy('%s/plane' % self.path)
        self.simSS.setScale(0.25)
        self.simSS.reparentTo(render)
        self.simSS.setTransparency(1)
        tex = loader.loadTexture('%s/ss.png' % self.path)
        self.simSS.setTexture(tex, 0)
        self.simSS.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simSS.setColor(color)
        self.myWidgets.append(self.simSS)
    
    def createSimSC(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simSC = loader.loadModelCopy('%s/plane' % self.path)
        self.simSC.setScale(0.25)
        self.simSC.reparentTo(render)
        self.simSC.setTransparency(1)
        tex = loader.loadTexture('%s/sc.png' % self.path)
        self.simSC.setTexture(tex, 0)
        self.simSC.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simSC.setColor(color)
        self.myWidgets.append(self.simSC)
    
    def createSimDC(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simDC = loader.loadModelCopy('%s/plane' % self.path)
        self.simDC.setScale(0.25)
        self.simDC.reparentTo(render)
        self.simDC.setTransparency(1)
        tex = loader.loadTexture('%s/dc.png' % self.path)
        self.simDC.setTexture(tex, 0)
        self.simDC.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simDC.setColor(color)
        self.myWidgets.append(self.simDC)
    
    def createSimRC(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition2(count)
        self.simRC = loader.loadModelCopy('%s/plane' % self.path)
        self.simRC.setScale(0.25)
        self.simRC.reparentTo(render)
        self.simRC.setTransparency(1)
        tex = loader.loadTexture('%s/rc.png' % self.path)
        self.simRC.setTexture(tex, 0)
        self.simRC.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simRC.setColor(color)
        self.myWidgets.append(self.simRC)
                    
    def getIndustryPosition(self, count):
        """Get Industry Position based on number of industry"""
        if count <= 3:
            x = -1.1 -count*0.3
            z = 0.7
        else:
            num = count - 4
            x = -1.3 -num*0.3
            z = 0.3
        return (x,z)
    
    def createSimWG(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simWG = loader.loadModelCopy('%s/plane' % self.path)
        self.simWG.setScale(0.25)
        self.simWG.reparentTo(render)
        self.simWG.setTransparency(1)
        tex = loader.loadTexture('%s/wg.png' % self.path)
        self.simWG.setTexture(tex, 0)
        self.simWG.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simWG.setColor(color)
        self.myWidgets.append(self.simWG)
    
    def createSimMA(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simMA = loader.loadModelCopy('%s/plane' % self.path)
        self.simMA.setScale(0.25)
        self.simMA.reparentTo(render)
        self.simMA.setTransparency(1)
        tex = loader.loadTexture('%s/ma.png' % self.path)
        self.simMA.setTexture(tex, 0)
        self.simMA.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simMA.setColor(color)
        self.myWidgets.append(self.simMA)
    
    def createSimFA(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simFA = loader.loadModelCopy('%s/plane' % self.path)
        self.simFA.setScale(0.25)
        self.simFA.reparentTo(render)
        self.simFA.setTransparency(1)
        tex = loader.loadTexture('%s/fa.png' % self.path)
        self.simFA.setTexture(tex, 0)
        self.simFA.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simFA.setColor(color)
        self.myWidgets.append(self.simFA)
    
    def createSimMF(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simMF = loader.loadModelCopy('%s/plane' % self.path)
        self.simMF.setScale(0.25)
        self.simMF.reparentTo(render)
        self.simMF.setTransparency(1)
        tex = loader.loadTexture('%s/mf.png' % self.path)
        self.simMF.setTexture(tex, 0)
        self.simMF.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simMF.setColor(color)
        self.myWidgets.append(self.simMF)
    
    def createSimJS(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simJS = loader.loadModelCopy('%s/plane' % self.path)
        self.simJS.setScale(0.25)
        self.simJS.reparentTo(render)
        self.simJS.setTransparency(1)
        tex = loader.loadTexture('%s/js.png' % self.path)
        self.simJS.setTexture(tex, 0)
        self.simJS.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simJS.setColor(color)
        self.myWidgets.append(self.simJS)
    
    def createSimRS(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        self.simRS = loader.loadModelCopy('%s/plane' % self.path)
        self.simRS.setScale(0.25)
        self.simRS.reparentTo(render)
        self.simRS.setTransparency(1)
        tex = loader.loadTexture('%s/rs.png' % self.path)
        self.simRS.setTexture(tex, 0)
        self.simRS.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simRS.setColor(color)
        self.myWidgets.append(self.simRS)
    
    def createSimSY(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        color = self.getFunctionalColor(color, self.systemDict['usedSYC'])
        self.simSY = loader.loadModelCopy('%s/plane' % self.path)
        self.simSY.setScale(0.25)
        self.simSY.reparentTo(render)
        self.simSY.setTransparency(1)
        tex = loader.loadTexture('%s/sy.png' % self.path)
        self.simSY.setTexture(tex, 0)
        self.simSY.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simSY.setColor(color)
        self.myWidgets.append(self.simSY)
    
    def createSimMI(self, color, count):
        """Create the Sim"""
        (x,z) = self.getIndustryPosition(count)
        color = self.getFunctionalColor(color, self.systemDict['usedMIC'])
        self.simMI = loader.loadModelCopy('%s/plane' % self.path)
        self.simMI.setScale(0.2)
        self.simMI.reparentTo(render)
        self.simMI.setTransparency(1)
        tex = loader.loadTexture('%s/mi.png' % self.path)
        self.simMI.setTexture(tex, 0)
        self.simMI.setPos(self.x+x, self.y+0.05, self.z+z)
        self.simMI.setColor(color)
        self.myWidgets.append(self.simMI)
    
    def getFunctionalColor(self, color, capacityUsed):
        if color != globals.colors['guiwhite']:
            return color
        if capacityUsed > 0:
            return globals.colors['guiyellow']
        return globals.colors['guiwhite']
        
    def rotateSim(self):
        ival = self.sim.hprInterval((25.0), Vec3(360, 0, 0))
        ival.loop() # keep the rotation going
    
    def refreshResources(self):
        self.clearText(self.textAL)
        self.clearText(self.textEC)
        self.clearText(self.textIA)
        self.writeResources()
    
    def refreshIndustrySims(self):
        self.clearIndustrySims()
        self.createIndustrySims()
        
    def getGenResources(self):
        """Return future generation of resources as (AL,EC,IA)"""
        from anw.gui import systemindustry
        systemindustrygui = systemindustry.SystemIndustry(self.path, self.systemDict, self.mode.game.myEmpire,
                                                                       self.mode.game.industrydata, 0)
        systemindustrygui.setMyMode(self.mode)
        return systemindustrygui.getCurrentProduction()
    
    def refreshGenTradeRoute(self):
        """Refresh any GEN trade route coming from this system"""
        if self.game.mode.name == 'MAP':
            for tradeRouteID, tradeRouteDict in self.game.tradeRoutes.iteritems():
                if tradeRouteDict['fromSystem'] == self.id and tradeRouteDict['type'] == 'GEN':
                    self.game.mode.traderoutes[tradeRouteID].refreshResources()

class BackgroundSystem(System):
    """A Background System that is not clickable, just for viewing"""
    def __init__(self, path, mode, systemDict,glow=1):
        System.__init__(self, path, mode, systemDict)
        self.scale = 20
        self.y = 50
        self.x = 30
        self.z = 30
        
        self.createMyBackgroundSim(glow)
    
    def createMySim(self):
        pass
    
    def createMyBackgroundSim(self, glow=1):
        self.registerMySim()
        self.loadMyTexture()
        if glow == 1:
            self.setGlow()
        self.setColor()
        self.setPos()
        self.writeName()
        self.writeCityNum()
        self.rotateSim()
        
    def rotateSim(self):
        ival = self.sim.hprInterval((180.0), Vec3(360, 0, 0))
        ival.loop() # keep the rotation going
    
    def setPositions(self):
        pass
    
    def writeName(self):
        """Write the tech name"""
        if 'availWGC' in self.systemDict.keys():
            availWGC = self.systemDict['availWGC']
            if availWGC != 0:
                text = '%s -> (%d/%d)' % (self.systemDict['name'], self.systemDict['usedWGC'], availWGC)
            else:
                text = self.systemDict['name']
        else:
            text = self.systemDict['name']
        self.clearText(self.textName)
        self.textName = textonscreen.TextOnScreen(self.path, text, 8, font=1)
        self.textName.writeTextToScreen(self.x-20, self.y, self.z+20, wordwrap=14)
        self.textName.setColor(globals.colors[self.color1])
    
    def writeCityNum(self):
        """Write City Number"""
        text = '%s' % self.systemDict['cities']
        self.createSimCity(globals.colors[self.color1])
        self.textCityNum = textonscreen.TextOnScreen(self.path, text, 10, font=1)
        self.textCityNum.writeTextToScreen(self.x-29, self.y, self.z+13, wordwrap=10)
        self.textCityNum.setColor(globals.colors[self.color1])
        
if __name__ == "__main__":
    mediaPath = 'media'
    mySystemDict = {'id':'1', 'name':'Test System', 'x':0, 'y':0, 'myEmpireID':'1', 'cities':15}
    system1 = System(mediaPath, None, mySystemDict)
    run()