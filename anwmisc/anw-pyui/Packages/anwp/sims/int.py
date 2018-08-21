# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# INT.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Represents an Interceptor Starship in the simulator
# ---------------------------------------------------------------------------
from OpenGL import GL

centerX = 0
centerY = 0
numFrames = 1
h=17
w=14
points = ( (-h,-w), (h,-w), (h,w), (-h,w) )
primitives = [ (GL.GL_QUADS, (0,1,2,3)) ]
