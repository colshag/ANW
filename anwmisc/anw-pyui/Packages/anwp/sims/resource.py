# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# resource.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a resource sim on the galactic map
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=15
w=15
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
