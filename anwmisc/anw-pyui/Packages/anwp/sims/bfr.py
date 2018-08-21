# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# BFR.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Battle Frigate Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=44
w=22
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
