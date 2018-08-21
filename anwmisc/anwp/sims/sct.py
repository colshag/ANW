# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# SCT.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an Scout Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=16
w=13
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
