import sha
import sys
import urllib
import urllib2
import os.path
import os
import gzip
from cStringIO import StringIO

installing = 0

class progress:
    def __init__(self):
        self.message = ""
        self.progress = 0
        self.bytes = 0
        self.error = []
        

    def updateProgress(self, message, progress, bytes):
        self.message = message
        self.progress = progress
        self.bytes = bytes
        print self.message, progress, bytes

    def getProgress(self):
        return self.progress

    def getMessage(self):
        return self.message

    def getByteCount(self):
        return self.bytes

    def addError(self, errorMsg):
        self.error.append(errorMsg)

    def isError(self):
        if len(self.error):
            return True
        return False
        
    def getNextError(self):
        return self.error.pop()

    
def checkfingerprint(filename, fingerprint):
    s = sha.new(open(filename,"rb").read())
    if fingerprint == s.hexdigest():
        return True
    else:
        #print filename + ":", "local file sha1:", s.hexdigest(), "does not match remote file", fingerprint
        #print fingerprint, s.hexdigest()
        return False

def downloadfile(url, localfile):
    f = open(localfile, "wb")
    data = urllib2.urlopen(url).read()
    size = len(data)
    f.write(data)
    f.close()
    return size

def gunzipfile(filename):
    data = gzip.open(filename).read()
    output = open(filename[:-3], "wb")
    output.write(data)
    output.close()
    os.remove(filename)
    

def doDownload(installdir, prog):

    global installing
    installing = 1
    downloadroot = "http://www.armadanetwars.com/downloads/"

    listing = downloadroot + "listing.txt.gz"
    
    installto = installdir
    
    if os.path.exists(installto) == False:
        prog.updateProgress("Making install directory...", 0, 0)
        #print "Making install directory:", installto
        os.makedirs(installto)
        
    prog.updateProgress("Downloading listing info...", 0, 0)

    blob = urllib2.urlopen(listing).read()
    listingdata = gzip.GzipFile('', 'rb',0, StringIO(blob))

    totalsize = len(blob)

    data = listingdata.readlines()
        
    numlines = len(data)
    curpos = 0
    for line in data:
        if not installing:
            break
        curpos = curpos + 1
        percent = int(100.0 * curpos / numlines)
        chunks = line.strip().split(",")

        if chunks[0] == "d":
            prog.updateProgress("Dir: " + chunks[1], percent, totalsize)
            if os.path.exists( installto + "/" + chunks[1] ):
                pass
            else:
                os.mkdir(installto + "/" + chunks[1])

        elif chunks[0] == "f":
            prog.updateProgress("File: " + chunks[1], percent, totalsize)
            p = installto + "/" + chunks[1]
            if os.path.exists( p[:-3] ):
                if checkfingerprint(p[:-3], chunks[2]) == False:
                    download = downloadroot + urllib.quote(chunks[1])
                    try:
                        totalsize += downloadfile(download, installto + "/" + chunks[1])
                        gunzipfile(p)
                    except:
                        prog.addError("Could not download: " + chunks[1])
                    if checkfingerprint(p[:-3], chunks[2]) == False:
                        prog.addError("Downloaded file " + chunks[1] + " doesn't match the fingerprint")
            else:
                download = downloadroot + urllib.quote(chunks[1])
                try:
                    totalsize += downloadfile(download, installto + "/" + chunks[1])
                    gunzipfile(p)
                except:
                    prog.addError("Could not download: " + chunks[1])
                if checkfingerprint(p[:-3], chunks[2]) == False:
                    prog.addError("Downloaded file " + chunks[1] + " doesn't match the fingerprint")
                
    return installing

def cancelDownload():
    global installing
    installing = 0
    

if __name__ == "__main__":

    prog = progress()
    doDownload("/tmp", prog)


    while(prog.isError()):
        print "Error: "*4 + prog.getNextError()

    print "Downloaded: " + str(prog.getByteCount()) + " bytes"

