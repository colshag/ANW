# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# run.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# used to test gui
# ---------------------------------------------------------------------------
import os

import pyui
import anwp.client.app
import anwp.client.game

class TestApplication(anwp.client.app.Application):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.renderer = pyui.desktop.getRenderer()
        self.game = anwp.client.game.TestGame(self, width, height) # load game
    
    def addGui(self, gui):
        self.gui = gui
        
    def run(self):
        """Run the game through a loop"""
        running = 1
        frames = 0
        counter = 0
        lastFrame = pyui.readTimer()
        endFrame = pyui.readTimer()
        
        while running:
            pyui.draw()
            if pyui.update():
                interval = pyui.readTimer() - endFrame
                endFrame = pyui.readTimer()
            else:
                running = 0
            
            # track frames per second
            frames += 1
            counter += 1
            
            # calculate FPS
            if endFrame - lastFrame > 1.0:
                FPS = counter
                counter = 0
                lastFrame = endFrame
                print 'FPS: %2d' % (FPS )
    
    
    
