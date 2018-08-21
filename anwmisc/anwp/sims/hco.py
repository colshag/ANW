# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# HCO.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Heavy Corvette Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=22
w=18
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
