import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from xml.dom import minidom
from google.appengine.ext.webapp import template
import XRD
from XRD import Link

#
# Simple implementation of the XRD Provisioning Protocol (XRDP)
# http://xrdprovisioning.net/specs/1.0/wd01/xrd-provisioning-1.0-wd01.html
#
# TODO:
#  - auth
#  - xml:id support
#


class MainPage(webapp.RequestHandler):
    
    # HTTP GET handler, not defined by XRDS, returns resource descriptor
    def get(self):
        xrd = XRD.make_XRD(Link.gql(""), "acct:charlie@ecece.com")
#        self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)

application = webapp.WSGIApplication(
                                     [('/webfinger', MainPage)],
                                     debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()