# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weaparc_2.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a weapon arc in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=200
w=40
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
