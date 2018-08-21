#!/usr/bin/env python

import glob
import sys
import os
import shutil
import gzip

from buildlisting import buildlisting

root = "../../"

destination = "../../../anwweb/downloads/anw/"
makedistdest = "../../../anwweb/downloads/"
#os.system("rm -rf '" + destination + "'")
##print "Clearing files in destination", destination
##try:
    ###shutil.rmtree(destination)
    ##for path, dirs, files  in os.walk(destination):
        ##for f in files:
            ##if f.endswith(".ttf") or f.endswith(".py") or f.endswith(".png"):
                ##os.remove(path + "/" + f)
##except:
    ##print "Couldn't delete files... aborting"
    ##sys.exit()

try:
    os.makedirs(destination)
except:
    print "Couldn't make destination directory. Probably exists and this is OK."

neededdirs = [
              "Client/data",
              "Client/sounds",
              "Packages/anw",
              "Packages/anw/aw",
              "Packages/anw/client",
              "Packages/anw/func",
              "Packages/anw/gui",
              "Packages/anw/gui/media",
              "Packages/anw/modes",
              "Packages/anw/war",
              "Database"
              ]
neededfileglobs = [
                   "Client/data/*.prc",
                   "Client/data/*.sha",
                   "Client/sounds/*.ogg",
                   "Client/client.data",
                   "Client/connect.ini",
                   "Client/run.py",
                   "Client/run.sh",
                   "Client/runmac.sh",
                   "Client/run.bat",
                   "Client/*.txt",
                   "Packages/anw/*.py",
                   "Packages/anw/aw/industrydata.py",
                   "Packages/anw/aw/__init__.py",
                   "Packages/anw/client/*.py",
                   "Packages/anw/func/*.py",
                   "Packages/anw/gui/*.py",
                   "Packages/anw/gui/media/*.png",
                   "Packages/anw/gui/media/*.egg",
                   "Packages/anw/gui/media/*.pz",
                   "Packages/anw/gui/media/*.ttf",
                   "Packages/anw/gui/media/*.rgb",
                   "Packages/anw/modes/*.py",
                   "Packages/anw/war/*.py",
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
        output = open(destination + f[len(root):], "wb")
        #output = gzip.GzipFile(destination + f[len(root):] + ".gz", "wb")
        output.write(open(f, "rb").read())
        output.flush()
        output.close()
        #shutil.copyfile(f, destination + f[len(root):])

shutil.copyfile("dist-utils/install/launcher.py", destination + "../launcher.py")


os.chdir(makedistdest)
buildlisting()


print "If any directories were removed for this version, they must be manually removed from the download directory and this script must be rerun"



