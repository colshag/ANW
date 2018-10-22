# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# server.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main ANW Server: The Servers Job is to verify user
# requests, read the object database and ask those objects to 
# return values.  The Server then converts these values into
# XML for the client.
# ---------------------------------------------------------------------------
from anw.func import storedata, globals, funcs
#from anw.gae.access import GAE, LocalGAE
from anw.mail.sending import SmtpEmail, Email #,NullEmail
from anw.server import anwserver
from anw.util.Injection import Services
from threading import Thread
from twisted.internet import reactor, task
from twisted.web import xmlrpc, server
import ConfigParser
import datetime
import hashlib
#import logging
import os
import errno
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
    #print("Create or modify the file in " 
              #+ profilepath
              #+ " with contents like the following\n" 
              #+ "[CosmicaServer]\n"
              #+ "serveruser = yourusername\n" 
              #+ "serverpass = yourpassword\n\n"
              #+ "[Email]\n" 
              #+ "#email section is optional. leave out to disable end of round updates and empire to empire message sending\n"
              #+ "smtphost = your.smtp.hostname\n"
              #+ "smtpuser = your_smtp_username\n"
              #+ "smtppass = your_smtp_password\n"
              #+ "smtpport = 587\n"
              #+ "# Leave both tls and ssl as False if your smtp server has no encryption\n"
              #+ "# you can only have one of tls or ssl, not both\n"
              #+ "smtptls = True\n"
              #+ "smtpssl = False\n"
              #+ "fromname = your_game_server_name\n"
              #+ "fromaddress = your_server_email_address\n"
              #)

#def logVersion():
    #logging.critical("Loading Server version: " + globals.currentVersion)

def writeLocalAuthFile(port, database):
    """ this is currently only supported when running a single game on a server """
    path = os.path.join(os.path.expanduser("~"), ".anw", database + ".info")
    
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
            
    f = open(path, "wb")
    key = hashlib.sha1(str(random.random())).hexdigest()
    globals.adminaccess = key
    f.write("key=" + key + "\n")
    f.write("port=" + str(port) + "\n")
    f.write("pid=" + str(os.getpid()) + "\n")
    f.close()
    
def setupDepenencyInjection(email={}):
    """ Register all object implementations up front """
    if email == {}:
        Services.register(Email)#, NullEmail)
    else:
        Services.register(Email, SmtpEmail)
    Services.inject(Email).configure(email)

def setupLogging():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def loadConfigFromProfile(profile="server", configSection="CServer"):
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
        # expand to full path, cross platform
        # from http://ubuntuforums.org/showthread.php?t=820043&page=2
        profilepath = os.path.expanduser(os.path.join("~", ".anw", profile))

    # redudent if they passed the actual path to a config file, but check anyway since we expand the path if it was a profile name
    #if not os.path.isfile(profilepath):
        #print "Could not find profile", profile, "at path", profilepath
        #logHelp(profilepath=profilepath)

    parser = ConfigParser.RawConfigParser()
    parser.read(profilepath)
    
    retVal = {}
    
    
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
                print("Missing email option: " + option + " DISABLING email support!")
                logHelp()

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

def shutdown_signal():
    reactor.stop()


def serverMain(queue=None, singleplayer=0, database='ANW1', port=8000, testemail=0, config="server", firsttime=0):
    #setupLogging()
    #logVersion()
    from optparse import OptionParser
    from optparse import Option

    config = loadConfigFromProfile(profile=config)
    
    # Initiliaze MyApp
    globals.serverMode = 1

    if singleplayer == 1:
        print("Singleplayer mode activated")
        testemail = 0
    else:
        setupDepenencyInjection(email=config['email'])

    app = anwserver.ANWServer()
    app.runServer(port, database, singleplayer)
    if database != None:
        writeLocalAuthFile(port, database)
    
    #Set up signal handling
    try:
        signal.signal(signal.SIGINT, SIGINT_CustomEventHandler)
    except:
        app._Log("Failed to install SIGINT handler")
    try:
        signal.signal(signal.SIGHUP, SIGHUP_CustomEventHandler)
    except:
        pass
        #logging.warning("Failed to install SIGHUP handler")
        # no signup in windows. just ignore any errors here
    try:
        signal.signal(signal.SIGTERM, SIGINT_CustomEventHandler)
    except:
        app._Log("Failed to install SIGTERM handler")

    try:
        signal.signal(signal.SIGABRT, SIGINT_CustomEventHandler)
    except:
        app._Log("Failed to install SIGABRT handler")

    # email all players if this is the first time game was created
    if firsttime != None and singleplayer == 0:
        app.emailFirstTimePlayers(firsttime)
        app._Log("First Time Database Generated, players emailed")

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
            app._Log("Email is enabled but is not working. Please check your configuration")
            logHelp()
            sys.exit(0)

    # Start reactor
    #reactorThread = Thread(target=reactor.run, args=(False,))
    #reactorThread.start()
    app._Log("Server Started - Version %s" % globals.currentVersion)
    shutdownwait = Thread(target=monitorThread, args=(queue,))
    shutdownwait.start()
    reactor.run()


def monitorThread(queue, sleeponstart=1):
    if queue:
        time.sleep(sleeponstart)
        queue.put("server ready")
        waitforsignal = queue.get()
        shutdown_signal()