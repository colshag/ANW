# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# selector_big.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a selector sim in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=50
w=50
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]