# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testclient.py
# grabbed from: http://twistedmatrix.com/projects/web/documentation/howto/xmlrpc.html
# ---------------------------------------------------------------------------
# This is a example twisted server, Twisted 2.5
# ---------------------------------------------------------------------------

from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

def printValue(value):
    print repr(value)
    reactor.stop()

def printError(error):
    print 'error', error
    reactor.stop()

proxy = Proxy('http://localhost:7080')
proxy.callRemote('add', 3, 5).addCallbacks(printValue, printError)
reactor.run()