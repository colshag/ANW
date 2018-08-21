#!/usr/bin/env python

import sha
import sys
import urllib
import urllib2
import os.path


homedir = None
try:
    homedir = os.environ['HOME']
except:
    pass

options = {}
options["-o"] = "1"
options["customargs"] = "passthru0"
options["passthru0"] = ""
options["installdir"] = "."


MENU = 0
#RUN = 1
SETRESOLUTION = 2
TOGGLEFULLSCREEN = 3
TOGGLESOUND = 4
SETINSTALLPATH = 5
SETCUSTOMARGS = 6

currentMenu = MENU

def runMenu():
    global currentMenu
    print "-"*80
    print "Armada Net Wars"
    while 1:
        print "-"*80
        print "Current config: "
        print "\tsound: [" + options['-o'] + "]"
        print "\tinstall dir: [" + options['installdir'] + "] (a directory called 'anw' will be created in that location)"
        
        if currentMenu == MENU:
            print "What would you like to do?"
            print "\tRun the application\t[1]"
            print "\tToggle sound\t[2]"
            print "\tChange install path\t[3]"
            print "\tUpdate/Install the game\t[4]"

            print "\tQuit [q]"
            print
    
            answer = getInput("Command: ")
            
            if answer == "1":
                doRun()
                return
            elif answer == "2":
                currentMenu = TOGGLESOUND
            elif answer == "3":
                currentMenu = SETINSTALLPATH
            elif answer == "4":
                doDownload(options["installdir"])
            elif answer == "q":
                return

        elif currentMenu == TOGGLESOUND:
           sound = getInput("Enter 1 for sound or 0 for no sound: ")
           if sound == "1" or sound == "0":
                options['-o'] = sound
                currentMenu = MENU
                
        elif currentMenu == SETINSTALLPATH:
            installpath = getInput("Enter a new install path or nothing to keep it the same: ")
            if installpath != "":
                options['installdir'] = installpath
            currentMenu = MENU
        else:
            currentMenu = MENU

def getInput(question):
    return raw_input(question)

def loadOptions():
    if os.path.exists(homedir + "/.armadanetwars") == False:
        return False

    for option in open(homedir + "/.armadanetwars", "rb").readlines():
        left,right = option.strip().split("=")
        options[left] = right

    return True

def writeOptions():
    output = open(homedir + "/.armadanetwars", "wb")
    for key in options.keys():
        output.write(key + "=" + options[key] + "\n")
    output.close()

def doRun():
    os.chdir(options['installdir'] + "/" + "anw/Client")
    command = "PYTHONPATH=../Packages/ python run.py -r " + options['-r'] + " -f " + options['-f'] + " " + options[options['customargs']]
    print command
    os.system(command)

def checkfingerprint(filename, fingerprint):
    s = sha.new(open(filename,"rb").read())
    if fingerprint == s.hexdigest():
        return True
    else:
        #print filename + ":", "local file sha1:", s.hexdigest(), "does not match remote file", fingerprint
        return False

def downloadfile(url, localfile):
    open(localfile, "wb").write(urllib2.urlopen(url).read())

def postinstallcheck():
    success = True
    print "*****************************************************************"
    print "Checking if you have the required modules and python version to play Armada Net Wars"

    if sys.version.split()[0].split('.') < ["2","4","0"]:
        print "You must have at least python 2.4.0 to play Armada Net Wars."
        print "You have version", sys.version.split()[0]
        ##if sys.platform == 'darwin':
            ##print "Ensure you install and use python from /Library/Frameworks/Python.framework"
        ##success = False
    try:
        import psyco
    except:
        print "WARNING: python-psyco module not detected: Although not required to play"
        print "        the psyco module can greatly speed up gameplay and is recommended"
    ##try:
        ##import Image
        ##import ImageOps
        ##import ImagePalette
        ##import BmpImagePlugin
        ##import GifImagePlugin
        ##import ImageFile
        ##import JpegImagePlugin
        ##import PngImagePlugin
        ##import PpmImagePlugin
        ##import TiffImagePlugin
    ##except:
        ##print "ERROR: It seems you are missing the python-imaging libraries."
        ##success = False
    ##try:
        ##import OpenGL
    ##except:
        ##print "ERROR: It seems you are missing the python-opengl libraries."
        ##success = False
    try:
        from pandac.PandaModules import Point2, Point3, Vec3, Vec4, BitMask32
    except:
        print "ERROR: It seems you are missing the panda3d libraries, please install panda3d from panda3d.org."
        success = False
   
    ##if sys.platform == 'darwin':
        ##try:
            ##import objc
        ##except:
            ##print "ERROR: It seems you are missing the python ObjC libraries."
            ##success = False
 
    return success

def doDownload(installdir):
    downloadroot = "http://www.armadanetwars.com/downloads/"
    
    listing = downloadroot + "listing.txt"
    
    installto = installdir
    
    if os.path.exists(installto) == False:
        print "Making install directory:", installto
        os.makedirs(installto)
        
    print "Downloading listing info..."
    listingdata = urllib2.urlopen(listing)
    print "Checking/Installing Armada Net Wars install in:", installto
    for line in listingdata.readlines():
        chunks = line.strip().split(",")
        if chunks[0] == "d":
            if os.path.exists( installto + "/" + chunks[1] ):
                pass
            else:
                print "Directory:", installto + "/" + chunks[1]
                os.mkdir(installto + "/" + chunks[1])
        elif chunks[0] == "f":
            if os.path.exists( installto + "/" + chunks[1] ):
                if checkfingerprint(installto + "/" + chunks[1], chunks[2]) == False:
                    download = downloadroot + urllib.quote(chunks[1])
                    print "fingerprint mismatch... downloading new file:", download
                    downloadfile(download, installto + "/" + chunks[1])
                    if checkfingerprint(installto + "/" + chunks[1], chunks[2]) == False:
                        print "Newly Downloaded file doesn't match the fingerprint. Aborting..."
                        sys.exit(1)
            else:
                download = downloadroot + urllib.quote(chunks[1])
                print "downloading file:", download
                downloadfile(download, installto + "/" + chunks[1])
                if checkfingerprint(installto + "/" + chunks[1], chunks[2]) == False:
                    print "Downloaded file doesn't match the fingerprint. Aborting..."
                    sys.exit(1)
    
    
    print """
    ******************************************************************
           Armada Net Wars - Install complete and up to date
    *******************************************************************
    """
    
    if postinstallcheck() == False:
        print "You will need to install the above libraries before you can play"
    else:
        print "You have all the required python libraries to play"
        
def printArgs():
    print "Usage:"
    print sys.argv[0] + " [-u] [-r] [-cNAME] [path/to/install]"
    print "Options are saved in $HOME/.armadanetwars the second time the command is run"
    print "-u: Performs an update"
    print "-r: Runs the application with the previous options"
    print "-c: loads the custom passthru options by name. Make sure there is no space between -c and the NAME"
    print "With no argument specified, a menu is presented with further options"        
    
if __name__ == "__main__":
    install = False
    run = False
    if loadOptions() == False:
        print "It appears you don't have the application downloaded"
        install = True

    
    for val in sys.argv[1:]:
        if val == '-?' or val == '--?' or val == '--help':
            printArgs()
            sys.exit()
        elif val == '-u':
            install = True
        elif val == '-r':
            run = True
        elif val[:2] == '-c':
            options['customargs'] = val[2:]
            run = True
        else:
            print "Setting install dir to", val
            options['installdir'] = val

    if install == True:
        print "downloading/updating application"
        doDownload(options['installdir'])
    if run == True:
        print "Running application"
        doRun()
    if install == False and run == False:
        runMenu()

    writeOptions()
