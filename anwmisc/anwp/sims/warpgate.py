# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# warpgate.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a resource sim on the galactic map
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=25
w=10
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
