# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# direct_M.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a medium direct fire sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=20
w=5
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
