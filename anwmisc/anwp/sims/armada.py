# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# armada.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an armada sim on the galactic map
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=12
w=12
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
