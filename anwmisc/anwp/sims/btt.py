# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# BTT.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Battle Troop Transport Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=50
w=17
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
