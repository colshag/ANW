# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# colorSims.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This function will make color all sims required
# ---------------------------------------------------------------------------
import os
from anw.func import imaging, globals
guiPath = '../../../../anw/Packages/anw/gui/media/'

def GetImageFileList(path):
    """Return list of image files in path directory"""        
    for root, dirs, files in os.walk(path):
        return files

def run():
    myImageList = GetImageFileList('.')
    for image in myImageList:
        if '_x' not in image:
            try:
                for empireDict in globals.empires:
                    name = image[:-4]
                    name = '%s_%s_%s_%s' % (name, empireDict['id'], empireDict['color1'], empireDict['color2'])
                    imaging.CreateGenericImage(name, '', guiPath)
            except:
                print 'cannot build image:%s' % name

if __name__ == '__main__':
    run()