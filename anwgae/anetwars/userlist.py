from QueryUtil import *
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from models import User
import os


class MainPage(webapp2.RequestHandler):
    def get(self):
        userId = self.request.get('user')
        if userId:
            self.displayActiveGames(userId)
        else:
            self.displayAllUsers()                    

    def displayActiveGames(self, userId):
        ugis = queryAllGamesForUser(userId)
        template_values = {'games' : []}
        for ugi in ugis:
            allUGI = getAllUserGameInfoInGame(ugi.game.name)
            # this will be a tuple of tuples.
            # ((UGI, round, turnComplete), (UGI, round, turnComplete))
            newAllUGI = []
            for ugi in allUGI:
                maxRound = 0
                maxRoundTurnComplete = False
                egr = ugi.empire_game_round.fetch(1000)
                for e in egr:
                    if e.gameRound.roundNum > maxRound:
                        maxRound = e.gameRound.roundNum
                        maxRoundTurnComplete = e.turnComplete
                newAllUGI.append((ugi, maxRound, maxRoundTurnComplete))
            template_values['games'].append(newAllUGI)
        print str(template_values)
        
        path = os.path.join(os.path.dirname(__file__), 'activegames.html')
        self.response.out.write(template.render(path, template_values))

    def displayAllUsers(self):
        player_query = User.all()
        # sort?
        player_query.filter('valid =', True)
        players = player_query.fetch(1000)
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        
        template_values = {'players': players}
        self.response.out.write(template.render(path, template_values))



app = webapp2.WSGIApplication(
                                     [('/', MainPage),
                                      ],
                                     debug=True)

