# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# missile2_M.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a missile sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=5
w=5
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
