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

""" GLUT renderer
"""

import sys
import time

import pyui

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


from pyui.desktop import getDesktop
from pyui.renderers import openglBase

try:
    from PIL.Image import *
except:
    print "Unable to find Python Imaging Library!"

class OpenGLGlut(openglBase.OpenGLBase):
    """ openGL renderer. Uses the PyOpenGL extensions.
    """

    name = "GLUT"
    
    def __init__(self, w, h, fullscreen, title):
        openglBase.OpenGLBase.__init__(self, w, h, fullscreen, title)
        
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)   #GLUT_ALPHA |        
        if self.fullscreen:
            glutGameModeString("%dx%d:32@70" % (w,h) )
            self.windowID = glutEnterGameMode()
        else:
            glutInitWindowSize(w,h)
            glutInitWindowPosition(0,0)
            self.windowID = glutCreateWindow(title)
        glutSetWindow(self.windowID)
        
        glutReshapeFunc(self.ReSizeGLScene)
        glutMouseFunc(self.onMouse)
        glutMotionFunc(self.onMotion)
        glutPassiveMotionFunc(self.onMotion)
        glutKeyboardFunc(self.onKeyDown)
        glutKeyboardUpFunc(self.onKeyUp)
        glutSpecialFunc(self.onSpecialDown)
        glutSpecialUpFunc(self.onSpecialUp)        
                
        
    def draw(self, windows):
        apply(self.drawBackMethod, self.drawBackArgs)                
        self.setup2D()

        for i in xrange(len(windows)-1, -1, -1):
            w = windows[i]
            self.setWindowOrigin(w.posX, w.posY)
            ## use display lists for deferred rendering...
            if w.dirty:
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
        glutSwapBuffers()    

        self.mustFill = 0
        self.dirtyRects = []


    def onMouse(self, button, state, x, y):
        if button==1:
            return
        if state==0:
            #mouse button down
            if button==0:
                getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONDOWN,x,y)
            else:
                getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONDOWN,x,y)
        else:
            #mouse button up
            if button==0:
                getDesktop().postUserEvent(pyui.locals.LMOUSEBUTTONUP  ,x,y)
            else:
                getDesktop().postUserEvent(pyui.locals.RMOUSEBUTTONUP  ,x,y)

    def onMotion(self, x, y):
        getDesktop().postUserEvent(pyui.locals.MOUSEMOVE, x,y)
        self.mousePosition = (x,y)

    def getModifiers(self):
        """NOTE: GLUT does not detect the CONTROL key!!!! BUG!!
        """
        mod = glutGetModifiers()
        realmod = 0
        if mod & GLUT_ACTIVE_SHIFT:
            realmod |= pyui.locals.MOD_SHIFT
        if mod & GLUT_ACTIVE_CTRL:
            realmod |= pyui.locals.MOD_CONTROL
        if mod & GLUT_ACTIVE_ALT:
            realmod |= pyui.locals.MOD_ALT
        return realmod
    
    def onSpecialDown(self, key, x, y):
        k = self.keyMap.get(key, key)
        print "down: ", k, key
        getDesktop().postUserEvent(pyui.locals.KEYDOWN, 0, 0, k, self.getModifiers() )
        
    def onSpecialUp(self, key, x, y):
        k = self.keyMap.get(key, key)        
        getDesktop().postUserEvent(pyui.locals.KEYUP, 0, 0, k, self.getModifiers() )
        
    def onKeyDown(self,key,x,y):
        if ord(key) < 128:
            getDesktop().postUserEvent(pyui.locals.CHAR, 0, 0, key, self.getModifiers() )
        
        getDesktop().postUserEvent(pyui.locals.KEYDOWN, 0, 0, ord(key), self.getModifiers() )

    def onKeyUp(self,key,x,y):
        getDesktop().postUserEvent(pyui.locals.KEYUP  , 0, 0, ord(key), self.getModifiers() )

    def quit(self):
        if self.fullscreen:
            glutLeaveGameMode()
        self.done = 1
        
    def runMe(self):
        if not getDesktop().running:
            sys.exit()
        pyui.update()
        pyui.draw()
        self.frame = self.frame + 1
        now = time.time()
        if now - self.last >= 1:
            self.last = now
            print "FPS: %d" % self.frame
            self.frame = 0
        #time.sleep(0.01)
        
    def run(self, callback=None):
        if callback:
            glutDisplayFunc(callback)
            glutIdleFunc(callback)
        else:
            glutDisplayFunc(self.runMe)
            glutIdleFunc(self.runMe)
            
        glutMainLoop()


    def loadTexture(self, filename, label = None):
        if label:
            if self.textures.has_key(label):
                return
        else:
            if self.textures.has_key(filename):
                return

        try:
            image = open(filename)
        except:
            image = open(  pyui.__path__[0] + "/images/" + filename )
            
        ix = image.size[0]
        iy = image.size[1]
        seq = 0
        for mode, seq in [('RGBA', 4), ('RGBX', 4), ('RGB', 3)]:
            try:
                image = image.tostring("raw", mode, 0, -1)
            except (IOError, SystemError):
                print "Unable to load %s with encoder %s" % (filename, mode)
                failed = 1
            else:
                failed = 0
                break
        if failed:
            raise IOError("All three encoders failed.")
        
        #Create Texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)   # 2d texture (x and y size)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, seq, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        print "Loaded: %s as %d" % ( filename, texture)
        if label:
            self.textures[label] = texture
        else:
            self.textures[filename] = texture

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)    
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def ReSizeGLScene(self, Width, Height):
        # Prevent A Divide By Zero If The Window Is Too Small     
        if Height == 0:	
            Height = 1

        # Reset The Current Viewport And Perspective Transformation
        glViewport(0, 0, Width, Height)		
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        self.width = Width
        self.height = Height

    def getTextSize(self, text, font = None):
        """This text method uses the old GLUT rendering instead of True Type fonts.
        """
        if font == 'fixed':
            return ( 8 * len( text ), 13 )        
        w = 0
        for c in text:
            w += glutBitmapWidth(GLUT_BITMAP_HELVETICA_12, ord(c))
        return (w, pyui.locals.TEXT_HEIGHT)


    def do_text_OLD(self, text, position, color, font ):
        """This text method uses the old GLUT rendering instead of True Type fonts.
        """
        glColor4ub( color[0], color[1], color[2], color[3] )
        glRasterPos2f(position[0], position[1]+13)
        if font == 'fixed':
            font = GLUT_BITMAP_8_BY_13
        else:
            font = GLUT_BITMAP_HELVETICA_12
        for char in text:
            glutBitmapCharacter(font, ord(char))
