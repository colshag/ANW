#!/usr/bin/env python

import sha
import os
import gzip

def buildlisting():
    print "Generating listing.txt"

    output = gzip.GzipFile("listing.txt.gz", "wb")
    for path, dirs, files  in os.walk("anw"):
        if path.find(".svn") != -1:
            continue
        output.write("d," + path.replace("\\", "/") + "\n")
        for d in dirs:
            if d.find(".svn") != -1:
                continue
            output.write("d," + path.replace("\\", "/") + "/" + d + "\n")
        for f in files:
            if f.find(".svn") != -1:
                continue
            sha1 = sha.new(gzip.open(path.replace("\\", "/")+"/"+f, "rb").read())
            output.write("f," + path.replace("\\", "/") + "/" + f + "," + sha1.hexdigest() + "\n")
    print "done...  Now check in 'anw', 'install.py' and 'listing.txt'.  The files will be deployed to the webserver automatically"
    output.close()
