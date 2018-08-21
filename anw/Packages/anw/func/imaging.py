# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# imaging.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Functions that create images using PIL
# ---------------------------------------------------------------------------
import Image
import ImageOps
import string

import globals

class ANWImager(object):
    """Creates ANW based images"""
    def __init__(self, filename, templatePath, imagePath):
        self.filename = filename
        self.templatePath = templatePath
        self.imagePath = imagePath
        self.colors = {'yellow':(252, 224, 0, 255),
                        'orange':(255, 92, 0, 255),
                        'green':(62, 249, 79, 255),
                        'cyan':(0, 194, 226, 255),
                        'red':(238, 21, 21, 255),
                        'pink':(254, 156, 176, 255),
                        'white':(254, 246, 248, 255),
                        'ltpurple':(239, 144, 250, 255),
                        'blue':(12, 93, 155, 255),
                        'brown':(180, 101, 49, 255),
                        
                        'blood':(156, 0, 0, 255),
                        'dkgrey':(60, 60, 60, 255),
                        'dkpurple':(110, 4, 122, 255),
                        'dkgreen':(6, 61, 11, 255),
                        'dkblue':(30, 13, 136, 255),
                        'black':(10, 10, 10, 255),
                        'dkyellow':(150,150,0,255)
                        }
        # create Image
        self.createImage()
    
    def createImage(self):
        """decipher the filename given and create the image"""
        pass
        
    def saveImage(self, image, filename):
        """Save Image to File"""
        try:
            image.save('%s%s.png' % (self.imagePath, filename), 'PNG')
        except IOError:
            print 'cannot save file: %s%s' % (self.imagePath, filename)
    
    def imageAttr(self, image):
        """Display image attributes to stdout"""
        print image.format, image.size, image.mode, image.info
    
    def changeColor(self, image, mask, color1, color2 = (0,0,0,0)):
        """Take an image and change its color, color is a tuple (R,G,B)"""
        print 'changing color of image to (%i, %i, %i, %i)' % color1
        self.imageAttr(image)
        image = ImageOps.colorize(image, color1, color2)
        xsize, ysize = image.size
        blank = Image.open('%s%i.png' % (self.templatePath, xsize))
        mask = Image.open(mask)
        image = Image.composite(image, blank, mask)
        return image
    
    def createObject(self, color1, color2, imageLName, imageBaseName):
        """Create an object using 2 colors and 2 images"""
        objectL = Image.open('%s%s' % (self.templatePath, imageLName))
        object = self.changeColor(objectL, '%s%s' % (self.templatePath, imageBaseName), color1, color2)
        return object

class CreateGenericImage(ANWImager):
    """take a filename and decipher it to build a generic Image"""
    def createImage(self):
        """decipher filename: abr_color1_color2"""
        (abr, empireID, color1, color2) = string.split(self.filename, '_')
        color1 = self.colors[color1]
        color2 = self.colors[color2]
        abr = string.lower(abr)
        imageLName = '%s_x.png' % abr
        imageName = '%s.png' % abr
        im = self.createObject(color1, color2, imageLName, imageName)
        self.saveImage(im, '%s_%s' % (abr, empireID))
        
class CreateSystemImage(ANWImager):
    """Take a filename and decipher it to build a System Image"""
    def createImage(self):
        """decipher system filename: sys_x_color1_color2"""
        (sys, starnum, color1, color2) = string.split(self.filename, '_')
        color1 = self.colors[color1]
        color2 = self.colors[color2]
        imageLName = 'star%s_x.png' % starnum
        imageName = 'star%s.png' % starnum
        im = self.createObject(color1, color2, imageLName, imageName)
        self.saveImage(im, self.filename)

class CreateEmpireImage(ANWImager):
    """Take a filename and decipher it to build an Empire Image"""
    def createImage(self):
        """decipher empire filename: emp_x_color1_color2"""
        (emp, empSymbol, color1, color2) = string.split(self.filename, '_')
        color1 = self.colors[color1]
        color2 = self.colors[color2]
        imageLName = 'empire%s_x.png' % empSymbol
        imageName = 'empire%s.png' % empSymbol
        im = self.createObject(color1, color2, imageLName, imageName)
        self.saveImage(im, self.filename)

class CreateTechImage(ANWImager):
    """Take a filename and decipher it to build a Tech Image"""
    def createImage(self):
        """decipher tech filename: tech_color"""
        (tech, color) = string.split(self.filename, '_')
        if color == 'red':
            color1 = 'red'
            color2 = 'black'
        elif color == 'yellow':
            color1 = 'yellow'
            color2 = 'white'
        elif color == 'green':
            color1 = 'green'
            color2 = 'white'
        color1 = self.colors[color1]
        color2 = self.colors[color2]
        imageLName = 'tech_x.png'
        imageName = 'tech.png'
        im = self.createObject(color1, color2, imageLName, imageName)
        self.saveImage(im, self.filename)

class CreateSelectorImage(ANWImager):
    """Take a filename and decipher it to build a Custom Selector Image"""
    def createImage(self):
        """decipher selector filename: selector_color1_color2"""
        (selector, color1, color2) = string.split(self.filename, '_')
        color1 = self.colors[color1]
        color2 = self.colors[color2]
        imageLName = 'selector1_x.png'
        imageName = 'selector1.png'
        im = self.createObject(color1, color2, imageLName, imageName)
        self.saveImage(im, self.filename)
