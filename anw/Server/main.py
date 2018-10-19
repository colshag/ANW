# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# main.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main Server: The Servers Job is to verify user
# requests, read the object database and ask those objects to 
# return values.  The Server then converts these values into
# XML for the client.
# ---------------------------------------------------------------------------
from anw.func import storedata, globals, funcs
from anw.mail.sending import SmtpEmail, Email
from anw.server import anwserver
from anw.util.Injection import Services
from twisted.internet import reactor, task
from twisted.web import xmlrpc, server
import ConfigParser
import datetime
import hashlib
import logging
import os
import random
import shutil
import signal
import string
import sys
import time
import types
import xmlrpclib

defaultprofilepath = os.path.expanduser(os.path.join("~", ".anw", "server.config")) 

def logHelp(profilepath=None):
    if profilepath == None:
        profilepath = defaultprofilepath 
    logging.error("Create or modify the file in " 
              + profilepath
              + " with contents like the following\n" 
              + "[CosmicaServer]\n"
              + "serveruser = yourusername\n" 
              + "serverpass = yourpassword\n\n"
              + "[Email]\n" 
              + "#email section is optional. leave out to disable end of round updates and empire to empire message sending\n"
              + "smtphost = your.smtp.hostname\n"
              + "smtpuser = your_smtp_username\n"
              + "smtppass = your_smtp_password\n"
              + "smtpport = 587\n"
              + "# Leave both tls and ssl as False if your smtp server has no encryption\n"
              + "# you can only have one of tls or ssl, not both\n"
              + "smtptls = True\n"
              + "smtpssl = False\n"
              + "fromname = your_game_server_name\n"
              + "fromaddress = your_server_email_address\n"
              )

def logVersion():
    logging.info("Server version: " + globals.currentVersion + globals.currentVersionTag)

def writeLocalAuthFile(port, database):
    """ this is currently only supported when running a single game on a server """
    path = os.path.join(os.path.expanduser("~"), ".anw", database + ".info")
    f = open(path, "wb")
    key = hashlib.sha1(str(random.random())).hexdigest()
    globals.adminaccess = key
    f.write("key=" + key + "\n")
    f.write("port=" + str(port) + "\n")
    f.write("pid=" + str(os.getpid()) + "\n")
    f.close()

def setupLogging():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def loadConfigFromProfile(profile="server", configSection="CosmicaServer"):
    """ 
    server profile name.  This will be in $HOME/.anw/server.config
    will work for both profile and /path/to/profile arguments
    returns (serverusername,serverpassword) tuple
    """

    if os.path.isfile(profile):
        print "found file", profile, "using it as config.  If you intended to use a profile make sure the name doesn't match a relative path"
        profilepath = profile
    else:
        if not profile.endswith(".config"):
            profile += ".config"
        profilepath = os.path.expanduser(os.path.join("~", ".anw", profile))

    # redudent if they passed the actual path to a config file, but check anyway since we expand the path if it was a profile name
    if not os.path.isfile(profilepath):
        print "Could not find profile", profile, "at path", profilepath
        logHelp(profilepath=profilepath)
        sys.exit()

    parser = ConfigParser.RawConfigParser()
    parser.read(profilepath)
    try:
        serveruser = parser.get(configSection, "serveruser")
        serverpassword = parser.get(configSection, "serverpass")
    except:
        logHelp(profilepath)
    
    retVal = {"serveruser" : serveruser, "serverpass" : serverpassword}
    
    
    retVal['email'] = loadEmailSettingsIntoDictionary({}, parser) 
    
    return retVal

def loadEmailSettingsIntoDictionary(dictionary, parser):
    """Fill dictionary with keys relating to email configuration.  returns an empty dictionary if an error occurs"""
    emailSection = "Email"
    if parser.has_section(emailSection):
        optionsAvailable = parser.options(emailSection)
        for option in ('smtphost', 'smtpport', 'smtptls', 'smtpssl', 'smtpuser', 'smtppass', 'fromname', 'fromaddress'):
            if option in optionsAvailable:
                dictionary[option] = parser.get(emailSection, option)
            else:
                logging.fatal("Missing email option: " + option + " DISABLING email support!")
                logHelp()
                sys.exit(0)

    return dictionary

def SIGINT_CustomEventHandler(num, frame):
    """Received a Interrupt signal. Shut down and exit.
    If the reactor is stopped, the database will be saved automatically
    """
    print "Recieved signal - INTERRUPT"
    print "Saving and shutting down ...."
    reactor.stop()
    
    
def SIGHUP_CustomEventHandler(num, frame):
    """Received a HUP signal. Save all galaxies."""
    print "Recieved signal - HUP"
    print "saving"
    reactor.callInThread(anwserver.saveAllGalaxies, app)

if __name__ == '__main__':

    setupLogging()
    logVersion()
    from optparse import OptionParser
    from optparse import Option
    parser = OptionParser(option_list=[Option("-p", dest="psyco", default=0),
                                       Option("-d", dest="database", default=None),
                                       Option("-o", dest="port", default=8000),
                                       Option("-e", dest="testemail", default=1),
                                       Option("-s", dest="singleplayer", default=0),
                                       Option("-c", dest="config", default="server")
                                       ])
    (options, args) = parser.parse_args()
    
    print"opts:", options.psyco, options.database, options.port, options.testemail, options.singleplayer

    psyco = int(options.psyco)
    database = options.database
    port = int(options.port)
    testemail = int(options.testemail)
    singleplayer = int(options.singleplayer)
    config = str(options.config)
         
    if psyco:
        try:
            import psyco
            psyco.full()
            print "psyco loaded"
        except ImportError:
            pass
    
    config = loadConfigFromProfile(profile=config)
    globals.serverMode = 1

    if singleplayer == 1:
        logging.info("Singleplayer mode activated")
        testemail = 0

    app = anwserver.ANWServer()
    app.runServer(port, database, singleplayer)
    if database != None:
        writeLocalAuthFile(port, database)
    
    signal.signal(signal.SIGINT, SIGINT_CustomEventHandler)
    try:
        signal.signal(signal.SIGHUP, SIGHUP_CustomEventHandler)
    except:
        pass
    signal.signal(signal.SIGTERM, SIGINT_CustomEventHandler)
    signal.signal(signal.SIGABRT, SIGINT_CustomEventHandler)
       
    # Make a XML-RPC Server listening to port
    reactor.listenTCP(port, server.Site(app))
    
    #Set up the loop to check the end of round every hour
    endRoundLoop = task.LoopingCall(anwserver.endRoundCounter, app)
    endRoundLoop.start(3600, 0)
    
    #add a shutdown trigger to save all galaxies
    reactor.addSystemEventTrigger('during', 'shutdown', anwserver.saveAllGalaxies, app)
    
    if testemail:
        emailResult = Services.inject(Email).sendTestEmail()
        if emailResult == False:
            logging.error("Email is enabled but is not working. Please check your configuration")
            logHelp()
            sys.exit(0)

    # Start reactor
    reactor.run()
    


