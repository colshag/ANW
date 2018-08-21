# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# DST.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Destroyer Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=48
w=30
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
