# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# engine.py
# Contains the graphics engine.  This engine connects to pyOpenGL
# ---------------------------------------------------------------------------
import sys
import copy

# library imports
from OpenGL.GL import *
from OpenGL.GLUT import *
import pygame

# application imports
import aabb
import anwp.func.funcs

gSources = {}  # imported source objects 
gTextures = {} # textures that have been loaded 
gTextureCoords = [[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]

class GraphicsException(Exception):
    pass

class GraphicsSource:
    def __init__(self, sourceDict):
        # set the attributes on this object
        self.__dict__.update(sourceDict)

        # calculate the aabb, width and height for this source
        self.aabb = aabb.AABB()
        for (x,y) in self.points:
            self.aabb.add(x,y)
        self.width = self.aabb.maxX - self.aabb.minX
        self.height = self.aabb.maxY - self.aabb.minY

        # calculate animation offset
        if self.numFrames:
            self.frameOffset = self.width / self.numFrames
        else:
            self.frameOffset = 0

        # calculate texture coordinates for this source
        self.coords = []
        frameOffset = 0
        frameWidth = 1.0 / self.numFrames
        for i in range(0, self.numFrames):
            frameCoords = []
            for x,y in self.points:
                tx = ( ( (x+(float)(self.width)/2.0) / self.width) / self.numFrames)
                ty = 1 - ((y+(float)(self.height)/2.0) / self.height)
                frameCoords.append( (tx+frameOffset,ty) )
            self.coords.append( frameCoords )
            frameOffset += frameWidth

def getSource(source):
    """Load or find a modules based on the source. 
     *** this is in internal method ***    
    """
    if gSources.has_key(source):
        return gSources[source]

    # load and store the module
    sourceDict = {}
    execfile(source, globals(), sourceDict)
    sourceObject = GraphicsSource(sourceDict)
    gSources[source] = sourceObject
    return sourceObject

def loadImage(filename):
    """load or lookup an image and return the OpenGL Handle to it.    
     *** this is in internal method ***
    """
    global gTextures
    if gTextures.has_key(filename):
        return gTextures[filename]

    # Load the texture into memory
    surface = pygame.image.load(filename)
    surface = pygame.transform.flip(surface,0,1)
    data = pygame.image.tostring(surface, "RGBA", 1)
    ix = surface.get_width()
    iy = surface.get_height()

    # Create the OpenGL Texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    # add the texture to global dictionary
    gTextures[filename] = texture
    return texture

class GraphicsObject:
    __slots__= ('posX','posY','facing','frame','mobile','sourceName','sourceObject','image','drawCallback')
    
    def __init__(self, source, mobile, image=None, drawCallback=None):
        """Create an object from a source of data.
        """
        self.posX = 0
        self.posY = 0
        self.facing = 0
        self.frame = 0
        self.color = None
        self.mobile = mobile
        self.sourceName = source
        # use copy.copy to allow for independant size changes per graphics object
        self.sourceObject = copy.copy(getSource(source))
        self.drawCallback = drawCallback        
        if image:
            self.image = image
        else:
            self.image = None##self.sourceObject.image

    def getSimData(self):
        """called by simulation to get data required to use
        this object in the simulation.
        returns (centerX, centerY, width, height)
        """
        return (self.sourceObject.centerX,
                self.sourceObject.centerY,
                self.sourceObject.width,
                self.sourceObject.height)
        
    def setState(self, x, y, facing):
        """updates the state of the object.
        """
        self.posX = x
        self.posY = y
        self.facing = facing

    def setFrame(self, frame):
        """Set the animation frame.
        """
        if frame < self.sourceObject.numFrames:
            self.frame = frame

    def setHeight(self, height):
        """set image height dynamically"""
        width = self.sourceObject.w
        self.setSize(width, height)
    
    def setWidth(self, width):
        """set image width dynamically"""
        height = self.sourceObject.h
        self.setSize(width, height)
    
    def setSize(self, width, height):
        """set the size of image dynamically"""
        self.sourceObject.points = ( (-height,-width), (height,-width), (height,width), (-height,width) )

    def nextFrame(self):
        """go to the next animation frame, implicitly cycle.
        """
        self.frame += 1
        if self.frame >= self.sourceObject.numFrames:
            self.frame = 0

    def destroy(self):
        """Destroy the object and release any resources.
        """
        self.sourceObject = None

    def render(self):
        """draw this object.
        *** this is in internal method ***        
        """
        glPushMatrix()
        if self.color:
            apply(glColor4ub, self.color)
        glTranslate( self.posX, self.posY, 0)
        glRotate(self.facing, 0, 0, 1)
        for prim, indicies in self.sourceObject.primitives:
            glBegin(prim)
            for i in indicies:
                apply(glTexCoord2f, self.sourceObject.coords[ self.frame ][i] )
                apply(glVertex, self.sourceObject.points[ i ])
            glEnd()
        glPopMatrix()
        if self.drawCallback:
            gEngine.drawCallbacks.append(self.drawCallback)

    def renderStatic(self):
        """draw this object.
        *** this is in internal method ***        
        """
        if self.color:
            apply(glColorub, self.color)
        for prim, indicies in self.sourceObject.primitives:
            for i in indicies:
                apply(glTexCoord2f, self.sourceObject.coords[ self.frame ][i] )
                points = self.sourceObject.points[ i ]
                apply(glVertex, (points[0] + self.posX, points[1] + self.posY))

class TextureBucket:
    """I am a container of objects with the same texture.
    I am responsible for rendering my objects.
    """
    def __init__(self, texture, dynamic):
        self.texture = texture
        self.objects = []
        self.dynamic = dynamic
        self.displayList = 0
        self.dirty = 1
        
    def addObject(self, object):
        self.objects.append(object)
        self.dirty = 1

    def removeObject(self, object):
        self.objects.remove(object)
        self.dirty = 1

    def render(self):
        """Draws the objects using display lists if enabled.
        """
        gEngine.drawCallbacks = []
        if self.dynamic:
            # render objects outside of display list
            self.renderObjects()
        else:
            # recreate display list if required
            if self.dirty:
                if self.displayList:
                    glDeleteLists(self.displayList, 1)
                self.displayList = glGenLists(1)
                glNewList(self.displayList, GL_COMPILE)
                self.renderObjectsStatic()
                glEndList()
                self.dirty = 0

            # always draw the display list
            glCallList(self.displayList)
        for drawCallback in gEngine.drawCallbacks:
            drawCallback()

    def renderObjects(self):
        """actually renders the objects.
        """
        texture = loadImage(self.texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4ub(255,255,255,255)
        for object in self.objects:
            object.render()

    def renderObjectsStatic(self):
        """actually renders the objects.
        """
        texture = loadImage(self.texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4ub(255,255,255,255)
        glBegin(GL_QUADS)
        for object in self.objects:
            object.renderStatic()
        glEnd()
        
class RenderBucket:
    """sorts objects by texture to minimize texture swapping.
    """
    def __init__(self, dynamic = 1 ):
        self.buckets = {}
        self.bucketList = []
        self.dynamic = dynamic

    def addObject(self, object):
        bucket = self.buckets.get(object.image, None)
        if not bucket:
            bucket = TextureBucket(object.image, self.dynamic)
            self.buckets[object.image] = bucket
        bucket.addObject(object)
        self.setBucketList()

    def removeObject(self, object):
        bucket = self.buckets.get(object.image, None)
        if not bucket:
            raise GraphicsException("Unable to find image: %s" % object.image)
        bucket.removeObject(object)
        self.setBucketList()
        
    def render(self):
        """Calls each texture bucket to render the objects.
        """
        for bucket in self.bucketList:
            bucket.render()
    
    def setBucketList(self):
        """set the bucket list in the right order"""
        self.bucketList = anwp.func.funcs.sortDictByChildObjValue(self.buckets, 'texture', True, {})

class Engine:
    def __init__(self, w, h):
        self.mobileObjects = RenderBucket()
        self.staticObjects = RenderBucket(dynamic = 0)
        self.width = w
        self.height = h
        self.posX = w/2
        self.posY = h/2
        self.facing = 0
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glOrtho( 0, w, 0, h, -1, 0)
    
    def add(self, obj, x, y, facing):
        """adds a graphics object to the engine.
        """
        obj.setState(x, y, facing)
        if obj.image <> None:
            if obj.mobile:
                self.mobileObjects.addObject(obj)
            else:
                self.staticObjects.addObject(obj)

    def remove(self, obj):
        """removes a graphics object from the engine.
        """
        if obj.image <> None:
            if obj.mobile:
                self.mobileObjects.removeObject(obj)
            else:
                self.staticObjects.removeObject(obj)

    def dirty(self, obj):
        """dirties an object and it's bucket.
        """
        if obj.image <> None:
            if obj.mobile:
                self.mobileObjects.dirtyObject(obj)
            else:
                self.staticObjects.dirtyObject(obj)
        
    def render(self):
        """Draw all of the objects.
        """
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)        
        glTranslate(self.width/2-self.posX, self.height/2-self.posY, 0)
        self.staticObjects.render()
        self.mobileObjects.render()
        glPopMatrix()

    def setView(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def worldToScreen(self, posX, posY):
        """transform position from world space into screen space.
        """
        screenX = (posX - self.posX) + self.width/2
        screenY = self.height - ((posY - self.posY) + self.height/2)
        return (screenX, screenY)

    def screenToWorld(self, posX, posY):
        """transform position from screen space into world space.
        """
        worldX = (posX - self.width/2) + self.posX
        worldY = ((self.height - posY) - self.height/2) + self.posY
        return (worldX, worldY)


def clear(color=None):
    if color:
        apply(glColor,color)
    else:
        glColor(0,0,0,255)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)    
    
def drawLine( x1, y1, x2, y2, color):
    """Draw a line from (x1,y1)(x2,y2)
    """
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    glDisable(GL_TEXTURE_2D)    
    glBegin(GL_LINES)
    glColor4ub( color[0], color[1], color[2], color[3] )
    glVertex2i(x1, y1)
    glVertex2i(x2, y2)
    glEnd()
    glEnable(GL_TEXTURE_2D)
             
def drawRect( x, y, width, height, color):
    """Draw a rectangle.
    """
    x = int(x)
    y = int(y)
    width = int(width)
    height = int(height)
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glColor4ub( color[0], color[1], color[2], color[3] )
    glVertex2i(x, y)
    glVertex2i(x+width, y)
    glVertex2i(x+width, y+height)
    glVertex2i(x, y+height)
    glEnd()
    glEnable(GL_TEXTURE_2D) 

def drawText(text, position, color):
    """Draw text at position.
    """
    glDisable(GL_TEXTURE_2D)    
    glColor4ub( color[0], color[1], color[2], color[3] )
    glRasterPos2f(position[0], position[1]+13)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    glEnable(GL_TEXTURE_2D)
    
def drawImage( x, y, width, height, image):
    """Draw a texture 
    """
    global gTextureCoords

    glColor4ub(255,255,255,255)
    texture = loadImage(image)
    glBindTexture( GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    
    glBegin(GL_QUADS)
    glTexCoord2f(gTextureCoords[0][0], gTextureCoords[0][1])
    glVertex2i( x, y)
    glTexCoord2f(gTextureCoords[1][0], gTextureCoords[1][1])
    glVertex2i( x+width, y) 
    glTexCoord2f(gTextureCoords[2][0], gTextureCoords[2][1])
    glVertex2i( x+width, y+height)
    glTexCoord2f(gTextureCoords[3][0], gTextureCoords[3][1])
    glVertex2i( x, y+height)
    glEnd()


gEngine = None  # graphics engine singleton

def initialize(width, height):
    """initialize the graphics engine.
    """
    global gEngine
    gEngine = Engine(width, height)

def addObject(object, x, y, facing):
    """Add a graphics object to the engine to be renderered.
    """
    if gEngine:
        gEngine.add(object, x, y, facing)

def removeObject(object):
    """remove a graphics object from the engine
    """
    if gEngine:
        gEngine.remove(object)

def render():
    """Draw all of the objects in the engine.
    """
    if gEngine:
        gEngine.render()

def setView(posX, posY):
    """set the origin of the viewpoints.
    """
    gEngine.setView(posX, posY)

def getWidth():
    return gEngine.width

def getHeight():
    return gEngine.height

def worldToScreen(posX, posY):
    return gEngine.worldToScreen(posX, posY)

def screenToWorld(posX, posY):
    return gEngine.screenToWorld(posX, posY)
    

def getSources():
    return gSources.keys()

def getTextures():
    return gTextures.keys()

def flushTextures():
    global gTextures
    if gTextures:
        # NOTE: Due to an issue with deleting OpenGL textures
        # with PyOpenGL 2.0.0.44, the line of code below is disabled.
        # On some machines, calling glDeleteTextures causes a crash,
        # so this line is disabled. Note that this means that texture
        # memory will NOT be released when this code is called.
        # (SR)
        #glDeleteTextures( gTextures.values() )
        #gTextures = {}
        pass

def flushSources():
    global gSources
    gSources = {}
