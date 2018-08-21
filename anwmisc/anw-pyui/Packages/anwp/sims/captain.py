# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# captain.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a captain sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=10
w=10
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
