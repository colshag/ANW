# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# FRG.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents a Frigate Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=40
w=20
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
