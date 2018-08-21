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

import sys
import time

import pyui

import soya, soya.soya3d as soya3d, soya.model as model, soya.cube as cube

from pyui.renderers import openglBase
from pygame import locals

from pyui.desktop import getDesktop, getTheme, getRenderer

from OpenGL.GL import *

class SoyaRenderer(openglBase.OpenGLBase):
    """ Soya 3D wrapper for the GL renderer
    """

    name = "Soya"
    
    def __init__(self, w, h, fullscreen, title):
        openglBase.OpenGLBase.__init__(self, w, h, fullscreen, title)
        soya.init()
        self.scene = soya3d.World()


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
    
        soya.display()
        

    def update(self):
        """PyGame event handling.
        """
        return 1
    
    def quit(self):
        return
        
    def drawImage(self, rect, filename, pieceRect = None):
        pass
