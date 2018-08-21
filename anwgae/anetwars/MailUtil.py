from google.appengine.api import mail

def sendMessage(sourceAddress="anw@armadanetwars.com", destinationAddress=None, subjectText=None, bodyText=None):
    message = mail.EmailMessage(sender=sourceAddress,
                                subject=subjectText)
    message.to = destinationAddress
    message.body = bodyText

    message.send()
    
    
def sendNewRoundEmailTo(userGameInfo, gameName, newRoundNum):
    """Not being used"""
    if True == False:
        user = userGameInfo.user
        emailAddr = user.email
        subject = gameName + " - Round " + str(newRoundNum) + " is starting"
        message = "Please login to play your next turn."
        if newRoundNum == 0:
            subject = gameName + " - Welcome to Armada Net Wars!"
            message = "Please login to play your turn."
        sendMessage("anw@armadanetwars.com", emailAddr, subject, message + "\n\nVisit http://www.armadanetwars.com/ for more information")

    
