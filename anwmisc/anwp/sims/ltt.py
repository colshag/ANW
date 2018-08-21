# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# LTT.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Light Troop Transport Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=40
w=15
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
