# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# modemarketstats.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the galactic market stats mode
# ---------------------------------------------------------------------------
import mode
from anw.gui import textonscreen, line
from anw.func import globals, funcs

class ModeMarketStats(mode.Mode):
    """This is the Galactic Stats Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.cameraPos = (0,-20, 0)
        self.enableMouseCamControl = 0
        self.resetCamera()
        self.name = 'MARKETSTATS'
        self.createMainMenu('O')
        self.xMin = -6.0
        self.xTotal = 12
        self.yPriceMin = 1
        self.yPriceTot = 5
        self.yVolMin = -6
        self.yVolTot = 5
        self.xPriceOffset = 0.4
        self.xVolOffset = 1.3
        self.prices = {'AL':[],'EC':[],'IA':[]}
        self.maxPrice = int(self.getMaxPrice()) + 1
        self.volume = {'AL':[],'EC':[],'IA':[]}
        self.maxVolume = self.getMaxVolume() + 2
        self.xAxis = range(self.game.currentRound+1)
        self.yPrice = range(0,self.maxPrice)
        self.yVolume = range(0,self.maxVolume)
        self.getMarketData()
        self.makePriceChart()
        self.makeVolumeChart()
    
    def getMarketData(self):
        """Get the market Data"""
        rounds = funcs.sortStringList(self.game.marketStats.keys())
        for round in rounds:
            marketStat = self.game.marketStats[round]
            self.prices['AL'].append(marketStat['avgSoldAL'])
            self.prices['EC'].append(marketStat['avgSoldEC'])
            self.prices['IA'].append(marketStat['avgSoldIA'])
            self.volume['AL'].append(marketStat['volSoldAL'])
            self.volume['EC'].append(marketStat['volSoldEC'])
            self.volume['IA'].append(marketStat['volSoldIA'])
        
    def getMaxPrice(self):
        """Get the highest price of all resources so far"""
        price = 0.0
        for res in ['AL','EC','IA']:
            maxPrice = self.getMax('avgSold%s' % res)
            if maxPrice > price:
                price = maxPrice
        return int(price)
    
    def getMaxVolume(self):
        """Get the highest volume of all resources so far"""
        volume = 0.0
        for res in ['AL','EC','IA']:
            maxVolume = self.getMax('volSold%s' % res)
            if maxVolume > volume:
                volume = maxVolume
        return int(volume/1000.0)
    
    def getMax(self, key):
        """Determine the maximum"""
        max = 0.0
        for id, marketStat in self.game.marketStats.iteritems():
            if marketStat[key] > max:
                max = marketStat[key]
        return max
    
    def makePriceChart(self):
        """Make the price chart"""
        self.printChartXAxis(0.5, self.xPriceOffset)
        self.printChartYAxis(self.yPrice, self.yPriceMin, self.yPriceTot, 1)
        self.plotPriceData()
        self.printTitle('Galactic Market Average Prices by Round', 6.2)
        
    def makeVolumeChart(self):
        """Make the volume chart"""
        self.printChartXAxis(-6.5, self.xVolOffset)
        self.printChartYAxis(self.yVolume, self.yVolMin, self.yVolTot, 1000.0)
        self.plotVolumeData()
        self.printTitle('Galactic Market Volumes Traded by Round', -0.8)
        
    def printTitle(self, title, y):
        """Print the chart title"""
        title = textonscreen.TextOnScreen(self.guiMediaPath, str(title), 0.4)
        title.writeTextToScreen(-5, 20, y, 60)
        title.setColor(globals.colors['guiwhite'])
        self.gui.append(title)
        
    def printChartXAxis(self, y, offset):
        """Print the X Chart Axis"""
        count = 0
        for roundnum in self.xAxis:
            count += 1
            if self.shouldIprint(len(self.xAxis), count):
                x = self.getX(roundnum, len(self.xAxis)) + offset
                xAxis = textonscreen.TextOnScreen(self.guiMediaPath, str(roundnum), 0.20)
                xAxis.writeTextToScreen(x, 20, y)
                xAxis.setColor(globals.colors['guiwhite'])
                self.gui.append(xAxis)
    
    def shouldIprint(self, total, count):
        if total > 20 and total < 60:
            if count%2 == 0:
                return 1
            else:
                return 0
        elif total >= 60:
            if count%4 == 0:
                return 1
            else:
                return 0
        else:
            return 1
                
    def getX(self, myPos, maxPos):
        """Get the location based on the position to max"""
        percent = float(myPos)/float(maxPos)
        pos = percent*self.xTotal
        return pos+self.xMin
    
    def plotPriceData(self):
        """Plot the Price Data"""
        for res in ['AL','EC','IA']:
            round = 0
            x1 = 0.0
            y1 = 0.0
            for price in self.prices[res]:
                y2 = self.getY(price, self.maxPrice, self.yPriceMin, self.yPriceTot)
                x2 = self.getX(round, len(self.xAxis)) + self.xPriceOffset
                if (x1,y1) != (0,0):
                    myLine = line.Line(self.guiMediaPath, (x1,y1), (x2, y2), texture='square_grey')
                    myLine.setColor(globals.colors[globals.resourceColors[res]])
                    self.gui.append(myLine)
                x1 = x2
                y1 = y2
                round += 1
                
    def printChartYAxis(self, yList, yMin, yTotal, factor):
        """Print the Y Axis"""
        count = 0
        lastprint = yMin - 1
        for val in yList:
            y = self.getY(val, max(yList), yMin, yTotal)
            if y - lastprint <= 0.2:
                continue
            lastprint = y
                
            yAxis = textonscreen.TextOnScreen(self.guiMediaPath, str(val*factor), 0.2)
            yAxis.writeTextToScreen(self.xMin, 20, y)
            yAxis.setColor(globals.colors['guiwhite'])
            self.gui.append(yAxis)
            count += 1

    def getY(self, myPos, maxPos, yMin, yTotal):
        """Get the location based on the position to max"""
        percent = float(myPos)/float(maxPos)
        pos = percent*yTotal
        return pos+yMin
    
    def plotVolumeData(self):
        """Plot the Volume Data"""
        for res in ['AL','EC','IA']:
            round = 0
            x1 = 0.0
            y1 = 0.0
            for vol in self.volume[res]:
                y2 = self.getY(vol/1000.0, self.maxVolume, self.yVolMin, self.yVolTot)
                x2 = self.getX(round, len(self.xAxis)) + self.xVolOffset
                if (x1,y1) != (0,0):
                    myLine = line.Line(self.guiMediaPath, (x1,y1), (x2, y2), texture='square_grey')
                    myLine.setColor(globals.colors[globals.resourceColors[res]])
                    self.gui.append(myLine)
                x1 = x2
                y1 = y2
                round += 1
    