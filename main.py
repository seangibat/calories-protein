#!/usr/bin/env python

"""
# Hey! Thanks for reading. I'd love any feedback on how I could
# organize or program this better. I'm still pretty new to Python 
# and programming in general. I figure I need to move all of the 
# connection stuff into it's own class and module. I'll do that when 
# I get a moment this week.
"""

import os
import urllib
import jinja2
import webapp2
import datetime
from pytz.gae import pytz
from pytz import timezone
from datetime import timedelta

from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

# Keys are based on the chatroom name and used by both connections and chatlines.
def user_key(user_object):
	return ndb.Key('User', user_object.user_id())

def get_lines(user_object, date_object):
	tomorrow = date_object - datetime.timedelta(days=1)
	lines_query = Line.query(Line.user==user_object, Line.time>=date_object, Line.time<=tomorrow).order(Line.time)
	lines_query = ndb.gql("SELECT * FROM Line WHERE user = :1 AND time <= :2 AND time >= :3", user_object, date_object, tomorrow)
	return lines_query.fetch()

class Line(ndb.Model):
	user = ndb.UserProperty()
	calories = ndb.IntegerProperty(indexed=False)
	protein = ndb.IntegerProperty(indexed=False)
	time = ndb.DateTimeProperty(indexed=True)

class HomePage(webapp2.RequestHandler):
	def get(self):
		current_user = users.get_current_user()
		lines = get_lines(current_user, datetime.datetime.today()+datetime.timedelta(hours=4))

		template_values = {
			'lines': lines,
			'user': current_user,
			'meow': datetime.datetime.now().isoformat(),
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class LinePost(webapp2.RequestHandler):
	def post(self):
		calories = int(self.request.get('calories'))
		protein = int(self.request.get('protein'))
		author = users.get_current_user()
		date = datetime.datetime.now()-datetime.timedelta(hours=4)

		line = Line(parent=user_key(author), time=date, user=author, calories=calories, protein=protein)
		line.put()

		self.redirect('/')

app = webapp2.WSGIApplication([
	('/', HomePage),
	('/linepost', LinePost),
], debug=True)