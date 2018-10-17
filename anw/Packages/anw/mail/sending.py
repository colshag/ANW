from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
import logging


class Email(object):
    smtpserver = "smtp.gmail.com"
    smtpport = 537
    username = "armadanetwars@gmail.com"
    password = "iloveanw"
    fromaddress = "armadanetwars@gmail.com"
    fromname = "Armada Net Wars Server"

    tls = True
    ssl = False
    
    def configure(self, configuration):
        #self.smtpserver = configuration['smtphost']
        #self.smtpport = int(configuration['smtpport'])
        #self.username = configuration['smtpuser']
        #self.password = configuration['smtppass']
        #self.fromaddress = configuration['fromaddress']
        #self.fromname = configuration['fromname']
        #self.tls = configuration['smtptls'] in ("True", "true", "1", "yes")
        #self.ssl = configuration['smtpssl'] in ("True", "true", "1", "yes")
        return True
    
    def send(self, toAddress, subject, text):
        if toAddress == "":
            return
        try:
            fromaddr = "armadanetwars@gmail.com"
            toaddr = toAddress
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = subject
        
            body = text
            msg.attach(MIMEText(body, 'plain'))
        
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            #server.login("armadanetwars", "iloveanw")
            server.login("armadanetwars","edyxjscrgbwqfvem")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            logging.info("Sent email successfully to " + toAddress)
        except:
            print 'Error: Could not send email to:%s' % toAddress    
    
    def sendTestEmail(self):
        return self.send(self.fromaddress, "Armada Net Wars Server [%s] starting..."%self.fromname, "This is a test message indicating the server has started and the email system is working")

class SmtpEmail(Email):
    def send(self, toAddress, subject, text):
        try:
            toaddr = toAddress
            msg = MIMEMultipart()
            msg['From'] = self.fromaddress
            msg['To'] = toaddr
            msg['Subject'] = subject
        
            body = text
            msg.attach(MIMEText(body, 'plain'))
            
            server = None
            if self.ssl:
                server = smtplib.SMTP_SSL(self.smtpserver, self.smtpport)
            else:
                server = smtplib.SMTP(self.smtpserver, self.smtpport)
            server.ehlo()
            
            if self.tls:
                server.starttls()
                server.ehlo()
                
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.fromaddress, toaddr, text)    
            logging.info("Sent email successfully to " + toAddress) 
            return True       
        except:
            print 'Error: Could not send email to: %s reason: %s' % (toAddress, str(sys.exc_info()[0]))
        return False
    
#class NullEmail(Email):
    #def send(self, toAddress, subject, text):
        #return True

    #def configure(self, configuration):
        #return True

    

        