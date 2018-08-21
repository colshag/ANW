# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# HCA.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Heavy Carrier Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=52
w=42
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
