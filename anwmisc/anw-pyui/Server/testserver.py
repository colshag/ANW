# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# testserver.py
# grabbed from: http://twistedmatrix.com/projects/web/documentation/howto/xmlrpc.html
# ---------------------------------------------------------------------------
# This is a example twisted server, Twisted 2.5
# ---------------------------------------------------------------------------
from twisted.web import xmlrpc, server

class Example(xmlrpc.XMLRPC):
    """An example object to be published."""

    def xmlrpc_echo(self, x):
        """Return all passed args."""
        return x

    ##xmlrpc_echo.signature = [['string', 'string'],
                             ##['int', 'int'],
                             ##['double', 'double'],
                             ##['array', 'array'],
                             ##['struct', 'struct']]

    def xmlrpc_add(self, a, b):
        """Return sum of arguments."""
        return a + b

    ##xmlrpc_add.signature = [['int', 'int', 'int'],
                            ##['double', 'double', 'double']]
    ##xmlrpc_add.help = "Add the arguments and return the sum."

if __name__ == '__main__':
    from twisted.internet import reactor
    r = Example()
    xmlrpc.addIntrospection(r)
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()