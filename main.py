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
	tomorrow = date_object + datetime.timedelta(hours=24)
	lines_query = ndb.gql("SELECT * FROM Line WHERE user = :1 AND date >= :2 AND date <= :3", user_object, date_object, tomorrow).order(Line.date)
	return lines_query.fetch()

class Line(ndb.Model):
	user = ndb.UserProperty()
	calories = ndb.IntegerProperty(indexed=False)
	protein = ndb.IntegerProperty(indexed=False)
	date = ndb.DateTimeProperty(indexed=True)

class HomePage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('getdate.html')
		self.response.write(template.render())
		

class DatePage(webapp2.RequestHandler):
	def get(self, year, month, day):

		today = datetime.datetime(int(year), int(month), int(day))

		current_user = users.get_current_user()
		lines = get_lines(current_user, today)

		template_values = {
			'lines': lines,
			'user': current_user,
			'year': year,
			'month': month,
			'day': day,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class LinePost(webapp2.RequestHandler):
	def post(self):
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		day = int(self.request.get('day'))
		hour =int(self.request.get('hour'))
		minute = int(self.request.get('minute'))
		second = int(self.request.get('second'))
		date = datetime.datetime(year, month, day, hour, minute, second)

		calories = int(self.request.get('calories'))
		protein = int(self.request.get('protein'))
		author = users.get_current_user()

		line = Line(parent=user_key(author), date=date, user=author, calories=calories, protein=protein)
		line.put()

		url = '/date/' + str(year) + '/' + str(month) + '/' + str(day)

		self.redirect(url)

app = webapp2.WSGIApplication([
	('/', HomePage),
	('/date/(\d+)/(\d+)/(\d+)', DatePage),
	('/linepost', LinePost),
], debug=True)