from pandac.PandaModules import * 
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task

class Minimap:
	def __init__(self, path='/models', scale = 0.0, posX = -0.9, posZ = -0.65, mapimageName = None):
		taskMgr.add(self.step,"MinimapTask")
		self.path = path
		self.posX = posX
		self.posZ = posZ
		b = 500
		pos = Vec3(self.posX,0,self.posZ)#Aspect2D coordinates for the location of the center of the minimap. 
		if mapimageName is None: mapimageName = '%s/battlemap.png' % self.path#mapimage is the image to place in the minimap
		
		self.scale = scale  #this value is the number of pixels wide the map will be.
		ratio = b/self.scale
		self.dotScale = (ratio) * b
		self.dotSize = 0.005 / ratio
		self.map = aspect2d.attachNewNode('Map')
		mapimage = self.getMapImage(mapimageName)
		
		props = base.win.getProperties( )
		self.Height = float(props.getYSize())
		self.Hscale = (1/self.Height)
		
		self.map.setScale(self.Hscale)  #Sets scale to the screen resolution.
		self.map.setPos(pos) #this is the location on aspect2d for the minimap. 
		self.dots = []
		self.dots.append([])
		self.targets = []
		self.targets.append([])
		self.teamImage = []  #a list of paths to the image that each team will use. 
		self.setNumTeams(9)
		self.mapimage = OnscreenImage(image = mapimage, scale = self.scale, parent = self.map)
		self.mousePosition = OnscreenImage(image = self.path + 'select3.png', scale = self.dotSize*10, pos = (0,0,0), parent = aspect2d)
		self.totaltargets = 0
	
	def destroy(self):
		"""Remove Minimap from game"""
		for team in range(len(self.dots)): #will cycle through each team
			for i in range(len(self.dots[team])): #will cycle through each member of the team
				dot = self.dots[team][i]
				dot.removeNode()
		self.mousePosition.removeNode()
		self.mapimage.removeNode()
		self.map.removeNode()
	
	def getMapImage(self, mapimageName):
		texImage=PNMImage() 
		texImage.read(Filename(mapimageName)) 
		tex=Texture()
		tex.load(texImage)
		return tex
	
	def setTargets(self, targets, team):
		for i in range(len(targets)):
			self.targets[team].append(targets[i])
		
		for i in range(len(self.targets[team])):
			self.dots[team].append(OnscreenImage(image = self.teamImage[team], scale = self.dotSize, pos = (0,0,0), parent = aspect2d))
		
	def setBezel(self, image = None, scale = None):
		
		if image is None: image = '%s/bezel.png' % self.path
		if scale is None: scale = 1
		
		self.bezel = OnscreenImage(image = image, scale = self.scale * scale, parent = self.map)
		self.bezel.setTransparency(TransparencyAttrib.MAlpha)
		
	def setScale(self, scale):
		self.scale = scale
		
	def setPos(self,num): #must be a Vec3
		self.pos = num
				
	def appendTarget(self, target = None, team = None): #target must be a nodepath, team must be an integer
		if target is not None:
			self.targets[team].append(target)
			x = len(self.targets[team])
			self.dots[team].append(OnscreenImage(image = self.teamImage[team], scale = self.dotSize, pos = (0,0,0), parent = aspect2d))
			
	def setNumTeams(self, num):  #Num must be an integer. Sets the number of different groups for the map to track. Each group may be tracked using a different graphic   
		newTargets = []
		for x in range(num):
			newTargets.append([])
			self.dots.append([])
			self.teamImage.append('%s/dot%d.png' % (self.path, x))
		self.targets = newTargets
		
	def removeTarget(self, target = None, team = None):
		for i in range(len(self.targets[team])):
			if self.targets[team][i] == target: #This means the object in question is the object to be removed
				self.dots[team][i].stash()
				
	def step(self, task):
		try:
			for team in range(len(self.targets)): #will cycle through each team
				for i in range(len(self.targets[team])): #will cycle through each member of the team
					target = self.targets[team][i]
					if target.isEmpty() == False:
						x = (target.getX()/self.dotScale) + self.posX
						z = (target.getZ()/self.dotScale) + self.posZ
						self.dots[team][i].setX(x)
						self.dots[team][i].setZ(z)
			
			self.mousePosition.setX((camera.getX()/self.dotScale + self.posX))
			self.mousePosition.setZ((camera.getZ()/self.dotScale + self.posZ))
						
			return Task.cont
		except:
			pass