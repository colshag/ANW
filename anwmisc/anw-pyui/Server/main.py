# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# main.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This runs the main server
# ---------------------------------------------------------------------------
from twisted.internet import reactor
from twisted.web import xmlrpc, server
import server

def run(psyco, database, port, thread):
    if psyco:
        try:
            import psyco
            psyco.full()
            print "psyco loaded"
        except ImportError:
            pass
        
    # Initiliaze MyApp
    app = server.ANWServer(thread)
    app.runServer(port, database)

    # Make a XML-RPC Server listening to port
    server.reactor.listenTCP(port, server.server.Site(app))

    # Start both reactor parts (wx MainLoop and XML-RPC server)
    server.reactor.run()

if __name__ == '__main__':
    from optparse import OptionParser
    from optparse import Option
    parser = OptionParser(option_list=[Option("-p", dest="psyco", default=0),
                                       Option("-d", dest="database", default=None),
                                       Option("-o", dest="port", default=8000),
                                       Option("-t", dest="thread", default=0)])
    (options, args) = parser.parse_args()
    print"opts:", options.psyco, options.database, options.port, options.thread
    run(int(options.psyco), options.database, int(options.port), int(options.thread))
