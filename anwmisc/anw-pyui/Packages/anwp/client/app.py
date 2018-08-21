# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# app.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main application that runs ANW
# ---------------------------------------------------------------------------
import time
import pyui
import os
import logging
import pygame

import game
import anwp.sl.engine

class Application(object):
    """set the basic app parameters, startup a client game, maintain run loop"""
    def __init__(self, width, height, serverAddressList, sound, server='', galaxy='', empire='', password=''):
        self.server = str(server)
        self.sound = sound
        self.galaxy = str(galaxy)
        self.empire = str(empire)
        self.password = str(password)
        self.intervalValue = 0
        self.path = os.getcwd()
        self.genImagePath = '%s/images/' % self.path
        self.simImagePath = '%s/sims/images/' % self.path
        self.soundPath = '%s/sounds/' % self.path
        self.serverAddressList = serverAddressList # list of potential servers
        self.width = width # width of the app
        self.height = height # height of the app
        if width > 0 and height > 0:
            self.systemFont = pyui.desktop.getRenderer().createFont(pyui.themes.anw.myFontDetails, 14, 0)
            self.smallFont = pyui.desktop.getRenderer().createFont(pyui.themes.anw.myFontDetails, 12, 0)
            ##self.planetFont = pyui.desktop.getRenderer().createFont(pyui.themes.anw.myFontPlanets, 14, 0)
            self.planetFont = self.smallFont
            anwp.sl.engine.initialize(width, height) # start graphics engine

        # setup sound
        try:
            import pySonic
            self.sonic = 1
        except:
            self.sonic = 0
            print 'Warning: pySonic not installed trying low quality pyGame Sound...'
            
        if not pygame.mixer:
            print 'Warning: pyGame sound disabled, starting with no sound...'
            self.sound = 0
            
        if self.sound == 1:
            # initiate sound
            self.initSound()
            
        self.game = game.ANWGame(self, width, height) # load game
        self.desiredFPS = 60.0
        # level=INFO, DEBUG (python Logging)
        logging.basicConfig(level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s')
        self.log=logging.getLogger('client')
        self.log.info('desired FPS:',self.desiredFPS)
                    
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s')
        log=logging.getLogger('client')
        self.__dict__.update(dict)
        self.log=log
           
    def run(self):
        """Run the game through a loop"""
        running = 1
        frames = 0
        counter = 0
        lastFrame = time.time()
        endFrame = time.time()
        delaySec=0.0
        
        while running:
            pyui.draw()
            if pyui.update():
                if self.intervalValue == 0:
                    interval = time.time() - endFrame
                else:
                    interval = self.intervalValue
                endFrame = time.time()
                if self.game.update(interval) == 0:
                    running = 0
            else:
                running = 0
            time.sleep(delaySec)
            # track frames per second
            frames += 1
            counter += 1
            
            # calculate FPS
            if endFrame - lastFrame > 1.0:
                FPS = counter
                counter = 0
                lastFrame = endFrame
                self.log.info('FPS: %2d, INTERVAL: %s' % (FPS, interval ))
                if FPS > self.desiredFPS:
                    if delaySec == 0 or (FPS - self.desiredFPS) > 10:
                        delaySec = (1.0/self.desiredFPS - 1.0/FPS)
                    else:
                        delaySec *= 1.05
                        
                elif FPS < self.desiredFPS:
                    if delaySec > 0.001:
                        delaySec /= 2                    
                    else:
                        delaySec = 0
                                    
                #print "delaySec: ",delaySec
            
            if self.game.mode and running == 1:
                self.game.mode.onKey()
    
    def setIntervalValue(self, value):
        """Set the intervale Value to 0 for regular, or a value from 0 to 1 for set interval"""
        self.intervalValue = value
        
    def initSound(self):
        """Init the Sound system"""
        # initiate sound objects
        if self.sound == 1:
            if self.sonic == 1:
                # setup pySonic
                import pySonic
                self.sonicWorld = pySonic.World()
            else:
                # setup pygame
                pygame.mixer.pre_init(44100,-16,2, 1024 * 3)
                pygame.mixer.init()
                pygame.mixer.set_num_channels(15)
            
            # setup sound objects
            for path, subdirs, files in os.walk(self.soundPath):
                for file in files:
                    sound = file[:-4]
                    if self.sonic == 1:
                        # setup pySonic sound
                        setattr(self, sound, pySonic.Source())
                        mySound = getattr(self, sound)
                        if file[-3:] == 'wav':
                            mySound.Sound = pySonic.FileSample('%s%s.wav' % (self.soundPath, sound))
                        else:
                            mySound.Sound = pySonic.FileStream('%s%s.ogg' % (self.soundPath, sound))
                    else:
                        # setup pyGame sound
                        if file[-3:] == 'wav':
                            setattr(self, sound, pygame.mixer.Sound('%s%s.wav' % (self.soundPath, sound)))
                            mySound = getattr(self, sound)
                            mySound.set_volume(.5)
                break
    
    def continueMusic(self, sound):
        """Continue the Music"""
        if self.sound == 1:
            if self.sonic == 1:
                # pySonic music has to be contintued for some reason
                mySound = getattr(self, sound)
                if mySound.IsPlaying() == 0:
                    mySound.Play()
    
    def playMusic(self, sound):
        """Play the music"""
        if self.sound == 1:
            if self.sonic == 1:
                mySound = getattr(self,sound)
                mySound.Play()
            else:
                # play pyGame music
                pygame.mixer.music.load('%s%s.ogg' % (self.soundPath, sound))
                pygame.mixer.music.play(-1)
    
    def playSound(self, sound):
        """Play the Sound specified by sound name"""
        if self.sound == 1:
            mySound = getattr(self, sound)
            if mySound <> None:
                if self.sonic == 1:
                    mySound.Play()
                else:
                    # play pyGame
                    if mySound.get_num_channels():
                        mySound.fadeout(250)
                    mySound.play()
    
    def stopSound(self, sound):
        """Stop the Sound specified by sound name"""
        if self.sound == 1:
            try:
                mySound = getattr(self, sound)
                if mySound <> None:
                    if self.sonic == 1:
                        mySound.Stop()
                    else:
                        # stop pyGame
                        mySound.stop()
            except:
                pass
