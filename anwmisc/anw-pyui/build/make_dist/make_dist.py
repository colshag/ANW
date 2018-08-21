#!/usr/bin/env python

import glob
import sys
import os
import shutil
import gzip

from buildlisting import buildlisting

root = "../../"

destination = "../../../../Web/trunk/downloads/anw/"
makedistdest = "../../../../Web/trunk/downloads/"
#os.system("rm -rf '" + destination + "'")
print "Clearing files in destination", destination
try:
    #shutil.rmtree(destination)
    for path, dirs, files  in os.walk(destination):
        for f in files:
            if f.endswith(".ttf") or f.endswith(".py") or f.endswith(".png"):
                os.remove(path + "/" + f)
except:
    print "Couldn't delete files... aborting"
    sys.exit()

try:
    os.makedirs(destination)
except:
    print "Couldn't make destination directory. Probably exists and this is OK."

neededdirs = [
              "Client/images",
              "Client/sounds",
              "Client/fonts",
              "Client/sims/images",
              "Packages/pyui/images",
              "Packages/pyui/renderers",
              "Packages/pyui/themes",
              "Packages/anwp/client",
              "Packages/anwp/func",
              "Packages/anwp/modes",
              "Packages/anwp/sims",
              "Packages/anwp/sl",
              "Packages/anwp/war",
              "Packages/anwp/gui",
              "Database"
              ]
neededfileglobs = [
                   "Client/images/*.png",
                   "Client/sounds/*.wav",
                   "Client/sounds/*.ogg",
                   "Packages/anwp/sims/*.py",
                   "Client/fonts/*.ttf",
                   "Client/sims/*.py",
                   "Packages/pyui/images/*.png",
                   "Packages/pyui/*.py",
                   "Packages/pyui/*/*.py",
                   "Packages/anwp/*.py",
                   "Packages/anwp/client/*.py",
                   "Packages/anwp/func/*.py",
                   "Packages/anwp/modes/*.py",
                   "Packages/anwp/sims/*.py",
                   "Packages/anwp/sl/*.py",
                   "Packages/anwp/war/*.py",
                   "Packages/anwp/gui/*.py",
                   "Client/run.py",
                   "Client/client.data",
                   "Client/connect.ini",
                   "Database/*.ship",
                   ]

for d in neededdirs:
    #print "Creating directory: ", destination + d
    try:
        os.makedirs(destination + d)
    except:
        pass
    
for filepath in neededfileglobs:
    for f in glob.glob(root + filepath):
        #print "Copying", f, "to", destination + f[len(root):]
        output = gzip.GzipFile(destination + f[len(root):] + ".gz", "wb")
        output.write(open(f, "rb").read())
        output.close()
        #shutil.copyfile(f, destination + f[len(root):])

shutil.copyfile("dist-utils/install/launcher.py", destination + "../launcher.py")


os.chdir(makedistdest)
buildlisting()


print "If any directories were removed for this version, they must be manually removed from the download directory and this script must be rerun"



