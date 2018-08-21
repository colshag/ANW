# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# lnd.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a drone sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=10
w=10
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
