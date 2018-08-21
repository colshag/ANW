# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# explosion.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is an explosion group of sims that fly out and then die
# ---------------------------------------------------------------------------
from direct.task import Task
from anw.func import funcs
from anw.gui import rootsim, textonscreen
from random import randint
from pandac.PandaModules import Filename, Vec3, Point3, Vec4
from direct.particles.ParticleEffect import ParticleEffect

class Explosion(rootsim.RootSim):
    """An explosion of small bits that fly out and then die"""
    def __init__(self, path, hullSize, x, z, empireID, texture='square', width=0.005, glow=1):
        rootsim.RootSim.__init__(self, path, texture, 'plane', transparent=1, scale=0.2)
        self.hullSize = hullSize
        self.empireID = empireID
        self.count = 200.0
        self.x = x
        self.y = 20
        self.z = z
        self.width = width
        self.glow = glow
        self.bits = {}
        self.particles = {}
        self.doParticle = 1
        self.createMyBits()

    def createMyParticle(self, size):
        particle = ParticleEffect()
        smokeEffect = self.path + "smoke.ptf"
        particle.loadConfig(Filename(smokeEffect))
        p0 = particle.particlesDict['particles']
        p0.emitter.setOffsetForce(Vec3(0.0, 0.0, 0.0))
        p0.factory.setLifespanBase(0.3 * size)
        p0.setPoolSize(200)
        return particle

    def createMyBits(self):
        """Create all the explosion bits"""
        if self.hullSize == 'tiny':
            sizeimage = [1,1,2,2,2]
            self.doParticle = 0
        elif self.hullSize == 'small':
            sizeimage = [1,1,1,1,1,1,2,2,2,3]
        else:
            sizeimage = [1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3]
        images = []
        for size in sizeimage:
            self.texture = '%sjunk%d_%s.png' % (self.path, size, self.empireID)
            mySim = self.createMySim()
            mySim.setPos(Vec3(self.x, self.y, self.z))
            if self.doParticle == 1:
                particle = self.createMyParticle(size)
                particle.start(parent=mySim, renderParent=render)

            self.bits[mySim] = [self.x, self.z, 0, randint(-100,100), randint(-100,100), randint(1,5)]
            if self.doParticle == 1:
                self.particles[mySim] = (particle, size)
    
    def createMySim(self):
        mySim = loader.loadModelCopy('%s/%s' % (self.path, self.type))
        mySim.setScale(self.scale)
        mySim.reparentTo(render)
        mySim.setTransparency(self.transparent)
        tex = loader.loadTexture(self.texture)
        mySim.setTexture(tex, 1)
        mySim.setShaderInput('glow',Vec4(self.glow,0,0,0),self.glow)
        return mySim
    
    def moveBits(self):
        """Make the bit move in a random direction"""
        for bit, (x,z,facing,dx,dz,dfacing) in self.bits.iteritems():
            if self.doParticle == 1:
                particle, size = self.particles[bit]
            newPos = bit.getPos()
            newX = x+dx*0.001
            newZ = z+dz*0.001
            newFacing = facing+dfacing
            newPos.setX(newX)
            newPos.setZ(newZ)
            bit.setPos(newPos)
            bit.setR(newFacing)
            
            if self.doParticle == 1:
                if self.count >= 0:
                    p0 = particle.particlesDict['particles']
                    p0.factory.setLifespanBase(0.3 * size * (float(self.count)/200.0))
                
            self.bits[bit] = (newX, newZ, newFacing, dx, dz, dfacing)
    
    def update(self):
        """Keep track of bits, destroy when count is over"""
        if self.count <= 0:
            self.destroy()
            return 0
        else:
            self.count -= 1
            self.moveBits()
            return 1
    
    def destroy(self):
        """remove all bits"""
        for bit in self.bits.keys():
            bit.removeNode()
            if self.doParticle == 1:
                self.particles[bit][0].cleanup()
            
        