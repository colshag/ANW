from direct.particles.ParticleEffect import ParticleEffect
from pandac.PandaModules import Filename, Vec4, Vec3, Point3
import math

class SmokeTrail(object):
    def __init__(self, warsim):
        self.warsim = warsim
        self.initialize()
        
    def initialize(self):
        smokeEffect = self.warsim.path + "smoke.ptf"
        self.particle = ParticleEffect()
        self.particle.loadConfig(Filename(smokeEffect))
        self.litterMin = 1.0
        # rough estimate based on masses that are around 50000->120000.  gets the max litter down to 25 -> 60
        self.litterMax = self.warsim.myShip.mass / 2500.0
        self.litterSize = self.litterMin
        self.particleStarted = False
        
        
    def update(self, facing):
        
        if self.warsim.myShip.strength >= 99.0:
            return
        
        if not self.particleStarted:
            self.particle.start(parent=self.warsim.sim, renderParent=render)#, renderParent=self.sim)
            self.particleStarted = True

        p0 = self.particle.particlesDict['particles']

        # 90 degree offset from what you waht expect
        radians = math.radians(self.warsim.myShip.facing - 90)
        xvec = math.cos(radians)
        yvec = math.sin(radians)
        
        p0.emitter.setOffsetForce(Vec3(0.0, xvec, yvec))
        
        futureLitterSize = self.warsim.myShip.strength * self.litterMax / 100.0
        futureLitterSize = abs(self.litterMax - futureLitterSize)
        if self.litterSize != futureLitterSize:
            # want the inverse
            self.litterSize = futureLitterSize
            p0.setLitterSize(int(self.litterSize))

    def cleanup(self):
        self.particle.cleanup()