# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# directapp.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main application, including client side panda code
# ---------------------------------------------------------------------------
import os
from anw.func import globals
from pandac.PandaModules import loadPrcFile, Filename, loadPrcFileData, WindowProperties
from threading import Event

loadPrcFile("data/config.prc")
windowtitle = 'Cosmica (version %s%s)' % (globals.currentVersion,globals.currentVersionTag)
loadPrcFileData('', 'window-title %s' % windowtitle)
from direct.interval.IntervalGlobal import Func
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Point2, Point3, Vec3, Vec4, BitMask32
from pandac.PandaModules import Shader, ColorBlendAttrib
from pandac.PandaModules import PandaNode, NodePath, Mat4
from direct.interval.SoundInterval import SoundInterval
from app import Application
    
class DirectApplication(Application, DirectObject):    
    """A Direct Application includes the Panda Engine Code"""
    def __init__(self, sound=1, server='', galaxy='', empire='', password='', shipBattle=None, glow=1):
        self.shutdownFlag = Event()
        props = WindowProperties()
        props.setTitle('%s (Game = %s)' % (windowtitle, galaxy)) 
        base.win.requestProperties(props)
        Application.__init__(self, server=server, galaxy=galaxy, empire=empire, password=password, shipBattle=shipBattle, glow=glow)
        self.pandapath = Filename.fromOsSpecific(self.path).getFullpath()
        self.imagePath = self.pandapath + '/images/'
        self.soundPath = self.pandapath + '/sounds/'
        self.modelPath = self.pandapath + '/models/'
        self.sound = sound
        self.finalcard = None
        self.glowCamera = None
        self.glowOn = True
        if glow:
            self.setupGlowFilter()
        self.gameLoopInterval = Func(self.gameLoop)
        self.gameLoopInterval.loop()
        self.createSounds()
        self.playMusic()
    
    def quit(self):
        self.stopMusic()
        self.shutdownFlag.set()
        #try:

            #exit()
        #except:
        #    os._exit(1)
    
    def playMusic(self):
        if self.sound:
            self.myMusic = base.loadMusic('%stopo.ogg' % self.soundPath)
            self.myMusic.setVolume(0.5)
            self.myMusic.setLoopCount(0)
            self.myMusic.play()
            
    def stopMusic(self):
        if self.sound:
            self.myMusic.stop()
    
    def createSounds(self):
        """Create all sounds objects to be called by mode"""
        for sound in ['beep01.ogg', 'beep02.ogg', 'beep03.ogg', 'bomb7.ogg', 
                  'grenade3.ogg', 'laser1.ogg', 'laser2.ogg', 'missile1.ogg',
                  'cannon6.ogg', 'photon1.ogg', 'warp.ogg', 'cancelwarp.ogg']:
            setattr(self, '%sSound' % sound[:-4], base.loadSfx("%s%s" % (self.soundPath, sound)))        
    
    def playSound(self, soundName):
        """Play the sound requested"""
        if self.sound:
            mySound = getattr(self, '%sSound' % soundName)
            mySound.setVolume(1)
            mySound.play()
    
    def enableMouseCamControl(self):
        """Enable Mouse Camera Control"""
        mat=Mat4(camera.getMat())
        mat.invertInPlace()
        base.mouseInterfaceNode.setMat(mat)
        base.enableMouse()
    
    def disableMouseCamControl(self):
        base.disableMouse()
        
    def gameLoop(self):
        """Run through this code every frame as an interval loop. update game every frame"""
        if self.shutdownFlag.is_set() or self.game.update(self.intervalValue) == 0:
            self.quit()
    
    def setupGlowFilter(self):
        #create the shader that will determime what parts of the scene will glow
        glowShader=Shader.load(self.pandapath + "/data/glowShader.sha")
        
        # create the glow buffer. This buffer renders like a normal scene,
        # except that only the glowing materials should show up nonblack.
        glowBuffer=base.win.makeTextureBuffer("Glow scene", 512, 512)
        glowBuffer.setSort(-3)
        glowBuffer.setClearColor(Vec4(0,0,0,1))

        # We have to attach a camera to the glow buffer. The glow camera
        # must have the same frustum as the main camera. As long as the aspect
        # ratios match, the rest will take care of itself.
        self.glowCamera=base.makeCamera(glowBuffer, lens=base.cam.node().getLens())

        # Tell the glow camera to use the glow shader
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(glowShader)
        self.glowCamera.node().setInitialState(tempnode.getState())

        # set up the pipeline: from glow scene to blur x to blur y to main window.
        blurXBuffer=self.makeFilterBuffer(glowBuffer,  "Blur X", -2, self.pandapath+"/data/XBlurShader.sha")
        blurYBuffer=self.makeFilterBuffer(blurXBuffer, "Blur Y", -1, self.pandapath+"/data/YBlurShader.sha")
        self.finalcard = blurYBuffer.getTextureCard()
        self.finalcard.reparentTo(render2d)
        self.finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        
        render.setShaderInput('glow', Vec4(0,0,0,0),0)
        
        render.analyze()
    
    def makeFilterBuffer(self, srcbuffer, name, sort, prog):
        blurBuffer=base.win.makeTextureBuffer(name, 512, 512)
        blurBuffer.setSort(sort)
        blurBuffer.setClearColor(Vec4(1,0,0,1))
        blurCamera=base.makeCamera2d(blurBuffer)
        blurScene=NodePath("new Scene")
        blurCamera.node().setScene(blurScene)
        shader = Shader.load(prog)
        card = srcbuffer.getTextureCard()
        card.reparentTo(blurScene)
        card.setShader(shader)
        return blurBuffer
