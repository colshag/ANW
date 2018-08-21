# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# explosion_small.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an explosion sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 16
h=8
w=8
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
