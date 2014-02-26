"""A simple 'hello world' sample, which includes examples of start/stop
handlers, accesses the 'users' service, and shows how to get information about
the current instance.
"""

import logging
import os
import time

import jinja2
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import modules
from google.appengine.api import users
from google.appengine.ext import deferred

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


def get_url_for_instance(instance_id):
    """Return a full url of the current instance.
    Args:
        A string to represent an VM instance.
    Returns:
        URL string for the instance.
    """
    hostname = app_identity.get_default_version_hostname()
    return 'http://{}.{}.{}'.format(
        instance_id, modules.get_current_version_name(), hostname)


def get_signin_navigation(original_url):
    """Return a pair of a link text and a link for logging in/out.
    Args:
        An original URL.
    Returns:
        Two-value tuple; a url and a link text.
    """
    if users.get_current_user():
        url = users.create_logout_url(original_url)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(original_url)
        url_linktext = 'Login'
    return url, url_linktext


def do_heavy_task():
    time.sleep(30)
    return


class Hello(webapp2.RequestHandler):
    """Display a greeting, using user info if logged in, and display information
    about the instance.
    """
    def get(self):
        """Display a 'Hello' message"""
        instance_id = modules.get_current_instance_id()
        message = 'Hello'
        if users.get_current_user():
            nick = users.get_current_user().nickname()
            message += ', %s' % nick
        template = JINJA_ENVIRONMENT.get_template('index.html')
        url, url_linktext = get_signin_navigation(self.request.uri)
        self.response.out.write(
            template.render(
                instance_url=get_url_for_instance(instance_id),
                url=url,
                url_linktext=url_linktext,
                message=message))


class RunHeavyTask(webapp2.RequestHandler):
    """Just runs the heavy task with deferred."""
    def get(self):
        """Just runs the heavy task with deferred."""
        deferred.defer(do_heavy_task)
        self.response.write('Put a heavy task on the queue.')


APPLICATION = webapp2.WSGIApplication([
    ('/', Hello),
    ('/run_heavy_task', RunHeavyTask),
], debug=True)
