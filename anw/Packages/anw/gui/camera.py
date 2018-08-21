"""
   camera.py -- A camera for Panda3D that can be rotated or moved around by
   setting values in a control map.
   
Copyright (c) 2007 Sean Hammond seanh@sdf.lonestar.org

    This file is part of PandaSteer.

    PandaSteer is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    PandaSteer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PandaSteer; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

from direct.task import Task
import direct.directbase.DirectStart

class Camera:
    """A camera with that can be rotated and moved around by setting values in
    a control map.
    """    
    
    def __init__(self,pos):
        """Initialise the camera. Pos should be a Point3, the initial position
        of the camera."""
        
        self.prevtime = 0

        # The camera's controls:
        # 0 = off, 1 = on
        self.controlMap = {"left":0, "right":0, "up":0, "down":0, "forward":0,
                           "backward":0, "strafe-left":0, "strafe-right":0}

        # Task that moves the camera according to the control map.
        taskMgr.add(self.move,"cameraMoveTask")

        base.disableMouse()
        base.camera.setPos(pos)
      
    def lookAt(self,point):
        """Wrapper method for base.camera.lookAt"""
        base.camera.lookAt(point)  
      
    def lookAt(self,x,y,z):
        """Wrapper method for base.camera.lookAt"""
        base.camera.lookAt(x,y,z)  
      
    def move(self,task):
        """Update the camera's position before rendering the next frame.
        
        This is a task function and is called each frame by Panda3D.
        
        Arguments:
        task -- A direct.task.Task object passed to this function by Panda3D.
        
        Return:
        Task.cont -- To tell Panda3D to call this task function again next
                     frame.
        
        """

        elapsed = task.time - self.prevtime

        # Rotate the camera according to which of it's controls are activated.
         
        speed = 60 
        if (self.controlMap["left"]!=0):
            base.camera.setH(base.camera.getH() + (elapsed*speed))
        if (self.controlMap["right"]!=0):
            base.camera.setH(base.camera.getH() - (elapsed*speed))
        if (self.controlMap["up"]!=0):
            base.camera.setP(base.camera.getP() - (elapsed*speed))
        if (self.controlMap["down"]!=0):
            base.camera.setP(base.camera.getP() + (elapsed*speed))
        if (self.controlMap["forward"]!=0 or self.controlMap["backward"]!=0):
            # This two-line Matrix trick is taken from the Roaming Ralph demo
            # that comes with Panda3D, see 
            # <http://panda3d.org/phpbb2/viewtopic.php?t=1446> for an
            # explanation.
            forward = base.camera.getNetTransform().getMat().getRow3(1)
            forward.normalize()
            if (self.controlMap["forward"]!=0):
                base.camera.setPos(base.camera.getPos() + forward*(elapsed*speed))
            if (self.controlMap["backward"]!=0):
                base.camera.setPos(base.camera.getPos() - forward*(elapsed*speed))
        if (self.controlMap["strafe-left"]!=0 or self.controlMap["strafe-right"]!=0):
            # Compute the camera's right direction in the same way we compute
            # the forward direction above, using the NodePath's transformation
            # matrix.
            right = base.camera.getNetTransform().getMat().getRow3(0)
            right.setZ(0)
            right.normalize()
            if (self.controlMap["strafe-left"]!=0): 
                base.camera.setPos(base.camera.getPos() - right*(elapsed*speed))
            if (self.controlMap["strafe-right"]!=0):
                base.camera.setPos(base.camera.getPos() + right*(elapsed*speed))
     
        # Store the task time and continue.
        self.prevtime = task.time
        return Task.cont

    def setControl(self, control, value):
        """Set the state of one of the camera's movement controls.
        
        Arguments:
        See self.controlMap in __init__.
        control -- The control to be set, must be a string matching one of
                   the strings in self.controlMap.
        value -- The value to set the control to.
        
        """
       
        self.controlMap[control] = value
