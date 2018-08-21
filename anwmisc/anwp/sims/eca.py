# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# ECA.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an Escort Carrier Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=40
w=20
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
