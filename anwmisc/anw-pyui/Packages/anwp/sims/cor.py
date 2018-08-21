# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# COR.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an Corvette Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=20
w=16
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
