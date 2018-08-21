# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# makeButtons.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This function will make button images
# ---------------------------------------------------------------------------
import Image, ImageDraw, ImageFont
guiPath = '../../../../anw/Packages/anw/gui/media/'

class CreateButtonImages(object):
    """Create the 4 Button Images Panda Requires:
    name_key_click, name_key_disabled, name_key_ready, name_key_rollover"""
    def __init__(self, path, name, key, action):
        self.path = path
        self.name = name
        self.key = key
        self.action = action
        self.blankImage = Image.open('blank.png')
        self.clickImage = Image.open('click.png')
        self.readyImage = Image.open('ready.png')
        self.backFont = ImageFont.truetype("star4.ttf", 105)
        self.backColor = (0,29,65)
        self.actionX = 5
        self.actionY = 40
        self.actionSize = 20
        self.backPosition = (5,13)

    def setActionParameters(self):
        """Set actionSize, actionX, based on number of characters in action"""
        numChar = len(self.action)
        if numChar >= 5:
            self.actionSize = 18
            self.actionX = 5
        elif numChar <= 2:
            self.actionSize = 35
            self.actionX = 25
            self.actionY = 30
        else:
            self.actionSize = 22
            self.actionX = 10
        if self.action in ('+','-'):
            self.actionSize = 70
            self.actionY = 10
            
    
    def createButtons(self):
        self.setActionParameters()
        self.createClickButton()
        self.createDisabledButton()
        self.createReadyButton()
        self.createRolloverButton()
    
    def createClickButton(self):
        im = self.clickImage.copy()
        self.createButton(im, 'click', (0,102,232), 10)
    
    def createDisabledButton(self):
        im = self.clickImage.copy()
        actionFont = ImageFont.truetype("star3.ttf", self.actionSize)
        type = 'disabled'
        actionColor = (140,140,140)
        imAction = self.blankImage.copy()
        draw = ImageDraw.Draw(imAction)
        draw.text((self.actionX, self.actionY), self.action, font=actionFont, fill=actionColor)
        im.paste(imAction,(0,0),imAction)
        self.saveImage(im, type)
    
    def createReadyButton(self):
        im = self.readyImage.copy()
        self.createButton(im, 'ready', (255,255,255), 0)
    
    def createRolloverButton(self):
        im = self.readyImage.copy()
        self.createButton(im, 'rollover', (235,232,12), -10)
    
    def createButton(self, im, type, actionColor, offsetY):
        actionFont = ImageFont.truetype("star3.ttf", self.actionSize)
        imBack = self.blankImage.copy()
        imAction = self.blankImage.copy()
        draw = ImageDraw.Draw(imBack)
        draw.text(self.backPosition, self.key, font=self.backFont, fill=self.backColor)
        im.paste(imBack,(0,0),imBack)
        
        draw = ImageDraw.Draw(imAction)
        draw.text((self.actionX, self.actionY+offsetY), self.action, font=actionFont, fill=actionColor)
        im.paste(imAction,(0,0),imAction)
        self.saveImage(im, type)
    
    def saveImage(self, image, type):
        imageFile = '%s%s_%s_%s.png' % (self.path,self.name, self.key, type)
        image.save(imageFile)
        print('image created:%s' % imageFile)

class CreateIndustryButtonImages(CreateButtonImages):
    """Similar to regular button images, no shortcut key image, 
    industry image on left, longer button with more text"""
    def __init__(self, path, name, key, action):
        CreateButtonImages.__init__(self, path, name, key, action)
        self.blankImage = Image.open('blank2.png')
        self.clickImage = Image.open('click2.png')
        self.readyImage = Image.open('ready2.png')
        self.actionX = 110
        self.actionY = 25
        self.actionSize = 45
        self.backPosition = (10,10)
    
    def setActionParameters(self):
        """Set actionSize, actionX, based on number of characters in action"""
        pass
    
    def createDisabledButton(self):
        im = self.readyImage.copy()
        self.createButton(im, 'disabled', (140,140,140), 0)
    
    def createButton(self, im, type, actionColor, offsetY):
        cityNum = 1
        if self.key in ('sy', 'mi','mf'):
            cityNum = 2
        
        imIndustryIcon = Image.open('%s.png' % self.key)
        im.paste(imIndustryIcon,(0,0),imIndustryIcon)
        
        actionFont = ImageFont.truetype("star3.ttf", self.actionSize)
        imAction = self.blankImage.copy()
        draw = ImageDraw.Draw(imAction)
        draw.text((self.actionX, self.actionY+offsetY), self.action, font=actionFont, fill=actionColor)
        im.paste(imAction,(0,0),imAction)
        
        cityIcon = Image.open('%dcity.png' % cityNum)
        im.paste(cityIcon,(725,20),cityIcon)
        
        self.saveImage(im, type)

class CreateTradeButtonImages(CreateIndustryButtonImages):
    """Similar to the IndustryButton Images without the cities needed image"""
    def __init__(self, path, name, key, action):
        CreateIndustryButtonImages.__init__(self, path, name, key, action)
    
    def createButton(self, im, type, actionColor, offsetY):
        myIcon = Image.open('%s.png' % self.key)
        im.paste(myIcon,(0,0),myIcon)
        
        actionFont = ImageFont.truetype("star3.ttf", self.actionSize)
        imAction = self.blankImage.copy()
        draw = ImageDraw.Draw(imAction)
        draw.text((self.actionX, self.actionY+offsetY), self.action, font=actionFont, fill=actionColor)
        im.paste(imAction,(0,0),imAction)
                
        self.saveImage(im, type)

class CreateDesignButtonImages(CreateIndustryButtonImages):
    """Similar to the IndustryButton Images without the cities needed image"""
    def __init__(self, path, name, key, action):
        CreateIndustryButtonImages.__init__(self, path, name, key, action)
    
    def createButton(self, im, type, actionColor, offsetY):
        myIcon = Image.open('rc.png')
        im.paste(myIcon,(0,0),myIcon)
        
        actionFont = ImageFont.truetype("star3.ttf", self.actionSize)
        imAction = self.blankImage.copy()
        draw = ImageDraw.Draw(imAction)
        draw.text((self.actionX, self.actionY+offsetY), self.action, font=actionFont, fill=actionColor)
        im.paste(imAction,(0,0),imAction)
                
        self.saveImage(im, type)
    

def run():
    #createMainButtons()
    #createScrollButtons()
    #createCityButtons()
    #createIndustryButtons()
    #createAgeButtons()
    #createSystemButtons()
    #createTradeButtons()
    #createDesignButtons()
    #createShipyardButtons()
    createMapMoveButtons()
    #createBVButtons()
    #createMIButtons()
    #createLeverageButtons()
    #createMapButtons()
    #createOrderButtons()
    #createDiplomacyButtons()
    #createMoveArmyButtons()
    #createMoveArmadaButtons()
    #createSystemMarketSellButtons()
    #createMarketButtons()
    #createSystemMarketBuyButtons()
    #createSendCreditButtons()
    #createMultiSimButtons()
    #createQuestionEndRound()
    #createQuestionSurrender()

def createMainButtons():
    myButtons = {'I':'CREDIT', 'E':'END', 'O':'MARKET', 'Q':'QUIT', 'R':'MAP',
                 'T':'TECH', 'U':'USER', 'I':'DESIGN', 'W':'WAR', 'Y':'MAIL'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'main', key, action)
        myCreate.createButtons()

def createScrollButtons():
    myButtons = {'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'1', 'X':'5', 'C':'10'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'scroll', key, action)
        myCreate.createButtons()

def createAgeButtons():
    myButtons = {'A':'REMOVE', 'S':'SUBMIT', 'D':'ADD', 
                 'Z':'BASIC', 'X':'ADV', 'C':'INTEL'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'age', key, action)
        myCreate.createButtons()

def createCityButtons():
    myButtons = {'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'AL', 'X':'EC', 'C':'IA'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'city', key, action)
        myCreate.createButtons()

def createIndustryButtons():
    myButtons = {'af':'ALLOY FACTORY','cm':'CRYSTAL MINE','ss':'SYNTHETIC SYSTEM',
                 'rc':'RESEARCH CENTER','sc':'SIMULATION CENTER','dc':'DESIGN CENTER',
                 'rs':'RADAR STATION','js':'JAMMING STATION','mf':'MILITIA FORTRESS',
                 'fa':'FLEET ACADEMY','ma':'MARINE ACADEMY','sy':'SHIPYARD',
                 'mi':'MARINE INSTALLATION','wg':'WARP GATE'}
    for key, action in myButtons.iteritems():
        myCreate = CreateIndustryButtonImages(guiPath, 'industry', key, action)
        myCreate.createButtons()

def createSystemButtons():
    myButtons = {'1':'CITIES', '2':'INDUSTRY', '3':'TRADE', 
                 '4':'MARKET', '5':'SHIPS', '6':'MARINES'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'system', key, action)
        myCreate.createButtons()
        
def createTradeButtons():
    myButtons = {'onetime':'ADD ONE TIME TRADE', 'tradegen':'ADD TRADE GEN ROUTE',
                 'cancel':'CANCEL TRADE ROUTE'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'trade', key, action)
        myCreate.createButtons()
    
    myButtons = {'G':'AL', 'F':'EC', 'V':'IA',
                 'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'5', 'X':'100', 'C':'1000'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'trade', key, action)
        myCreate.createButtons()

def createLeverageButtons():
    myButtons = {'leveragemax':'LEVERAGE MAX RES'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'leverage', key, action)
        myCreate.createButtons()
    
    myButtons = {'G':'AL', 'F':'EC', 'V':'IA',
                 'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'1', 'X':'10', 'C':'100'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'leverage', key, action)
        myCreate.createButtons()
        
def createDesignButtons():
    myButtons = {'A':'REMOVE', 'S':'SUBMIT', 'D':'ADD', 
                 'Z':'FORE', 'X':'AFT', 'C':'PORT', 'V':'STAR',
                 '1':'FORE', '2':'AFT', '3':'PORT', '4':'STAR'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'design', key, action)
        myCreate.createButtons()
        
    myButtons = {'submitdesign':'SUBMIT DESIGN',
                 'simulatedesign':'SIMULATE DESIGN',
                 'removedesign':'REMOVE DESIGN',
                 'cancel':'CANCEL DESIGN',
                 'mytech':'USE CURRENT TECH', 'alltech':'USE ALL TECH',
                 'setupsim':'SETUP A SIMULATION'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'design', key, action)
        myCreate.createButtons()

def createMapMoveButtons():
    myButtons = {'warpships':'WARP SHIPS', 'warparmies':'WARP ARMIES',
                 'cancel':'CANCEL WARP', 'selectall':'SELECT ALL', 'selectdamaged':'SELECT DAMAGED'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'mapmove', key, action)
        myCreate.createButtons()
        
    myButtons = {'A':'OUT', 'S':' UP ', 'D':' IN ', 'F':'SELECT','G':'CLEAR', 
                 'Z':'LEFT ', 'X':'DOWN ', 'C':'RIGHT','V':'S-LEFT','B':'S-RIGHT'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'mapmove', key, action)
        myCreate.createButtons()

def createMapButtons():
    myButtons = {'swap':'SWAP SHIP CAPTAINS','sort':'SORT ALL CAPTAINS'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'map', key, action)
        myCreate.createButtons()
        
def createShipyardButtons():
    myButtons = {'buildships':'BUILD SHIPS', 
                 'repairships':'REPAIR SHIPS', 
                 'upgradeships':'UPGRADE SHIPS'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'shipyard', key, action)
        myCreate.createButtons()

def createMIButtons():
    myButtons = {'buildmarines':'BUILD MARINES', 
                 'refitmarines':'REFIT MARINES', 
                 'upgrademarines':'UPGRADE MARINES'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'mi', key, action)
        myCreate.createButtons()
        
def createBVButtons():
    myButtons = {'simulatedesign':'SIMULATE DESIGN'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'bv', key, action)
        myCreate.createButtons()
    
    myButtons = {'F':'MINE', 'V':'OTHER',
                 'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'1', 'X':'5', 'C':'10'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'bv', key, action)
        myCreate.createButtons()

def createOrderButtons():
    myButtons = {'submit':'SUBMIT ORDER',
                 'cancel':'CANCEL ORDER', 'selectall':'SELECT ALL'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'order', key, action)
        myCreate.createButtons()

def createDiplomacyButtons():
    myButtons = {'sendmail':'SEND MESSAGE',
                 'increase':'INCREASE DIPLOMACY', 'decrease':'DECREASE DIPLOMACY'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'diplomacy', key, action)
        myCreate.createButtons()

def createMoveArmyButtons():
    myButtons = {'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'Mech', 'X':'Art', 'C':'Inf'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'movearmies', key, action)
        myCreate.createButtons()

def createMoveArmadaButtons():
    myButtons = {'A':'-', 'S':'SUBMIT', 'D':'+', 
                 'Z':'Platform', 'X':'Assault', 'C':'Warship'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'movearmada', key, action)
        myCreate.createButtons()

def createSystemMarketSellButtons():  
    myButtons = {'F':'PRICE', 'G':'AMOUNT', 
                 'A':'-', 'S':'SELL', 'D':'+', 
                 'Z':'1', 'X':'10', 'C':'100','V':'1000'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'sys_sell', key, action)
        myCreate.createButtons()

def createSystemMarketBuyButtons():  
    myButtons = {'F':'PRICE', 'G':'AMOUNT', 
                 'A':'-', 'S':'BUY', 'D':'+', 
                 'Z':'1', 'X':'10', 'C':'100','V':'1000'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'sys_buy', key, action)
        myCreate.createButtons()
        
def createSendCreditButtons():  
    myButtons = {'F':'PRICE', 'G':'AMOUNT', 
                 'A':'-', 'S':'SEND', 'D':'+', 
                 'Z':'1', 'X':'10', 'C':'100','V':'1000'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'sendcredit', key, action)
        myCreate.createButtons()
        
def createMarketButtons():
    myButtons = {'buyal':'BUY AL', 
                 'buyec':'BUY EC', 
                 'buyia':'BUY IA',
                 'sellal':'SELL AL', 
                 'sellec':'SELL EC', 
                 'sellia':'SELL IA',
                 'selectall':'SELL ALL RESOURCES'}
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'market', key, action)
        myCreate.createButtons()

def createMultiSimButtons():  
    myButtons = {'A':'-', 'S':'ADD', 'D':'+', 
                 'Z':'TEAM 1', 'X':'TEAM 2'}
    for key, action in myButtons.iteritems():
        myCreate = CreateButtonImages(guiPath, 'multisim', key, action)
        myCreate.createButtons()        

def createQuestionEndRound():
    myButtons = {'blankyes':'YES AND WAIT', 
                 'blankno':'YES AND QUIT', 
                 'cancel':'CANCEL END TURN',
                 }
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'questionendround', key, action)
        myCreate.createButtons()
        
def createQuestionSurrender():
    myButtons = {'blankyes':'YES, I SURRENDER !', 
                 'blankno':'NO, I NEVER GIVE UP !', 
                 }
    for key, action in myButtons.iteritems():
        myCreate = CreateTradeButtonImages(guiPath, 'questionsurrender', key, action)
        myCreate.createButtons()
        
if __name__ == '__main__':
    run()
