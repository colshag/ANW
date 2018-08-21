# PyUI
# Copyright (C) 2001-2002 Sean C. Riley
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""PyGame openGL renderer
"""
import os
import pyui
import pygame
from pyui.renderers import openglBase
from pygame import locals

from pyui.desktop import getDesktop, getTheme, getRenderer

from OpenGL.GL import *

class OpenGLPygame(openglBase.OpenGLBase):
    """ PyGame 3D wrapper for the GL renderer
    """

    name = "P3D"
    
    def __init__(self, w, h, fullscreen, title):
        openglBase.OpenGLBase.__init__(self, w, h, fullscreen, title)
        pygame.init()
        pygame.display.set_caption(title)
        if fullscreen:
            self.screen = pygame.display.set_mode((w, h), locals.OPENGL | locals.DOUBLEBUF | locals.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((w, h), locals.OPENGL | locals.DOUBLEBUF)

        pygame.key.set_mods(locals.KMOD_NONE)
        pygame.mouse.set_visible(0)
        self.imageSizes = {}

    def draw(self, windows):
        apply(self.drawBackMethod, self.drawBackArgs)        
        self.setup2D()                        
        for i in xrange(len(windows)-1, -1, -1):
            w = windows[i]
            self.setWindowOrigin(w.posX, w.posY)
            if w.dirty:
                ## use display lists for deferred rendering...
                if not hasattr(w, "displayList"):
                    w.displayList = 0
                if w.displayList:
                    glDeleteLists(w.displayList,1)
                w.displayList = glGenLists(1)
                glNewList(w.displayList, GL_COMPILE_AND_EXECUTE)
                w.drawWindow(self)                
                glEndList()
            else:
                glCallList(w.displayList)

        self.setWindowOrigin(0,0)
        self.drawMouseCursor()
        self.teardown2D()
        pygame.display.flip()

        self.mustFill = 0
        self.dirtyRects = []

    def readTimer(self):
        return pygame.time.get_ticks()/1000.0

    def update(self):
        """PyGame event handling.
        """
        desktop = getDesktop()
        ## process all pending system events.
        event = pygame.event.poll()
        while event.type != locals.NOEVENT:
            
            # special case to handle multiple mouse buttons!
            if event.type == locals.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    desktop.postUserEvent(pyui.locals.LMOUSEBUTTONDOWN, event.pos[0], event.pos[1])
                elif event.dict['button'] == 3:
                    desktop.postUserEvent(pyui.locals.RMOUSEBUTTONDOWN, event.pos[0], event.pos[1])
                    
            elif event.type == locals.MOUSEBUTTONUP:
                if event.dict['button'] == 1:
                    desktop.postUserEvent(pyui.locals.LMOUSEBUTTONUP, event.pos[0], event.pos[1])
                elif event.dict['button'] == 3:
                    desktop.postUserEvent(pyui.locals.RMOUSEBUTTONUP, event.pos[0], event.pos[1])
                    
            elif event.type == locals.MOUSEMOTION:
                self.mousePosition = event.pos
                desktop.postUserEvent(pyui.locals.MOUSEMOVE, event.pos[0], event.pos[1])

            elif event.type == locals.KEYDOWN:
                character = event.unicode
                code = 0
                if len(character) > 0:
                    code = ord(character)
                else:
                    code = event.key
                    #code = event.key, code                    
                desktop.postUserEvent(pyui.locals.KEYDOWN, 0, 0, code, pygame.key.get_mods())
                #if code >= 32 and code < 128:
                #    desktop.postUserEvent(pyui.locals.CHAR, 0, 0, character, pygame.key.get_mods())
            elif event.type == locals.KEYUP:
                code = event.key
                desktop.postUserEvent(pyui.locals.KEYUP, 0, 0, code, pygame.key.get_mods())
                
            else:
                try:
                    desktop.postUserEvent(event.type)
                except:
                    print "Error handling event %s" % repr(event)
            event = pygame.event.poll()

            self.mousePosition = pygame.mouse.get_pos()
            
    def quit(self):
        pygame.quit()          
        
    def loadTexture(self, filename, label = None):
        """This loads images without using P.I.L! Yay.
        """
        if label:
            if self.textures.has_key(label):
                return
        else:
            if self.textures.has_key(filename):
                return

        try:
            surface = pygame.image.load(filename)
        except:
            surface = pygame.image.load(  pyui.__path__[0] + "/images/" + filename )
        data = pygame.image.tostring(surface, "RGBA", 1)
        ix = surface.get_width()
        iy = surface.get_height()
        self.imageSizes[filename] = (ix,iy)
        
        # Create Texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

        if label:
            self.textures[label] = texture
        else:
            self.textures[filename] = texture

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)    
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def getImageSize(self, filename):
        self.loadTexture(filename)
        return self.imageSizes.get(filename, (0,0) )

    def createFont(self, face, size, flags):
        newFont = GLFont(face, size, flags)
        return newFont

    def drawText(self, text, pos, color, font = None, flipped = 0):
        """the flipped flag is for drawing text in the upside-down
        coordinate space of cartesian space, rather than UI space.
        It flips the Y axis before drawing.
        """
        if not font:
            font = getTheme().defaultFont
            
        if flipped:
            glMatrixMode(GL_PROJECTION)                        
            glPushMatrix()
            glLoadIdentity()
            glOrtho( 0, self.width, self.height, 0, -1, 1 )
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()            
            
        font.drawText(text, pos, color)

        if flipped:
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)                        
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)                        

    def getTextSize(self, text, font = None):
        if not font:
            font = getTheme().defaultFont
        return font.getTextSize(text)
    
class GLFont:
    def __init__(self, faceFile, size, flags):
        self.faceFile = faceFile
        self.size = size
        self.flags = flags
        print "Creating font:", fontRegistery[faceFile]
       	if fontRegistery.has_key(faceFile):
            faceFile = "fonts/" + fontRegistery[faceFile]
    
        self.font = pygame.font.Font(faceFile, size*1.3)

        self.charInfo = []  # tuples of (width, height, texture coordinates) for each character
        self.createGlyphs()

    def createGlyphs(self ):
        testSurface = self.font.render("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUTWXYZ", 1, (255,255,255,255))
        charWidth = testSurface.get_width()
        charHeight = testSurface.get_height()
        charSurfaces = []

        # create the character surfaces
        totalWidth = 0
        for i in range(0,128):
            try:
                charSurface = self.font.render( chr(i), 1, (255,255,255,255))
            except:
                charSurfaces.append( None )
            else:
                charSurfaces.append(charSurface)
                totalWidth += charSurface.get_width()

        # TODO: calculate this properly
        if totalWidth > 1300:
            SZ = 512
        else:
            SZ = 256
        totalWidth = SZ
        totalHeight = SZ
        
        # pack the surfaces into a single texture
        x = pygame.surface.Surface((totalWidth, totalHeight),
                                   flags=pygame.HWSURFACE |pygame.SRCALPHA,
                                   depth=32,
                                   masks=(0,0,0,0))
        self.packedSurface = x.convert_alpha()
        self.packedSurface.fill((0,0,0,0))
        positionX = 0
        positionY = 0
        c = 0
        for charSurf in charSurfaces:
            if not charSurf:
                self.charInfo.append( (0,0, (0,0,0,0)) )
                continue

            if positionX + charSurf.get_width() > SZ:
                positionX = 0
                positionY += charSurf.get_height()
            
            self.packedSurface.blit(charSurf, (positionX, positionY) )
            
            # calculate texture coords
            left = positionX/(float)(totalWidth)
            top = 1- positionY/(float)(totalHeight)            
            right = (positionX+charSurf.get_width()) / (float)(totalWidth)
            bottom = 1 - ((positionY+charSurf.get_height()) / (float)(totalHeight))
            texCoords = (left, top, right, bottom)

            self.charInfo.append( (charSurf.get_width(), charSurf.get_height(), texCoords) )
            positionX += charSurf.get_width()
            c += 1

        # create GL texture from surface
        self.texture = glGenTextures(1)
        data = pygame.image.tostring(self.packedSurface, "RGBA", 1)        
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, totalWidth, totalHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)    
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # create display lists for each of the characters
        top = 1
        bottom = 3
        self.displayLists = []
        for (width, height, coords) in self.charInfo:
            if not width and not height:
                self.displayLists.append(0)
                continue
            newList = glGenLists(1)
            glNewList(newList, GL_COMPILE)
            glBegin(GL_QUADS)
            glTexCoord2f(coords[0], coords[top])
            glVertex2i(0, 0)
            glTexCoord2f(coords[2], coords[top])
            glVertex2i(width, 0)
            glTexCoord2f(coords[2], coords[bottom])
            glVertex2i(width, height)
            glTexCoord2f(coords[0], coords[bottom])
            glVertex2i(0, height)
            glEnd()
            glEndList()
            self.displayLists.append(newList)

    def drawText(self, text, pos, color):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor4ub(color[0], color[1], color[2], color[3])
        xPos = pos[0]
        yPos = pos[1]-5
        glPushMatrix()
        glTranslate(xPos,yPos,0)
        for c in text:
            width = self.charInfo[ord(c)][0]
            glCallList( self.displayLists[ord(c)])
            glTranslate(width,0,0)
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)     

    def getTextSize(self, text):
        w = 0
        h = 0
        for c in text:
            (width, height, coords) = self.charInfo[ord(c)]
            w += width
            h = max(height,h)
        return (w,h/1.4)
        

fontRegistery = {
    "comic sans ms":"comic.ttf",
    "courier new":"cour.ttf",
    "courier":"cour.ttf",    
    "impact":"impact.ttf",
    "arial":"arial.ttf",
    "times new roman":"times.ttf",
    "times":"times.ttf",
    "alien6":"alien6.ttf",
    "tahoma":"tahoma.ttf",
    "star1":"star1.ttf",
    "star2":"star2.ttf",
    "star3":"star3.ttf",
    "star4":"star4.ttf",
    "star5":"star5.ttf",
    "star3PPC":"star3PPC.ttf"
    }
    
