# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# mail.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an in game mail message to a player
# ---------------------------------------------------------------------------
from anw.func import root

class Mail(root.Root):
    """A Mail represents an in game mail message.  Mail messages are sent to players
    through their mail system, mail can come from other players or the server."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.fromEmpire = str() # empire ID
        self.messageType = str() # type of message (diplomacy, economic stats, etc)
        self.subject = str() # message subject
        self.body = str() # message body
        self.value = str() # special value that can be passed with the message
        self.round = int() # round message was created
        self.viewed = int() # has message been viewed (1=yes, 0=no)
        self.urgent = int() # message urgent, email notification (1=yes, 0=no)
        self.remove = int() # remove message from db (1=yes, 0=no)
        
        self.defaultAttributes = ('id', 'fromEmpire', 'messageType', 'subject', 'body',
                                  'value', 'round', 'viewed', 'urgent', 'remove')
        self.setAttributes(args)
        