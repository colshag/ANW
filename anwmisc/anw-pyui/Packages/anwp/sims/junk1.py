# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# junk1.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a peice of junk in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=2
w=2
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
