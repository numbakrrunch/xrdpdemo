import cgi
import os
import logging

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
        acct = self.request.get("acct")
        if acct == None:
            self.error(400)
            return
        links = XRD.get_links(acct)
        xrd = XRD.make_XRD(links, acct)
#        self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)

    # HTTP POST handler, add a link if there isn't already a link with the same properties
    def post(self):
        acct = self.request.get("acct")
        if acct == None:
            self.error(400)
            return
        logging.info(self.request.body)
        link = XRD.parse_link(self.request.body)
        if link == None:
            self.error(400)
            return
        link.acct = acct
        existing = XRD.get_link(acct, link.rel, link.type, link.href, link.template)
        if existing:  # conflict
            self.error(409)
            return            
        link.put()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
#        self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)
    
    # HTTP PUT handler, update an existing link
    def put(self):
        acct = self.request.get("acct")
        if acct == None:
            self.error(400)
            return            
        link = XRD.get_link(acct,
                            self.request.get("rel"),
                            self.request.get("type"),
                            self.request.get("href"),
                            self.request.get("template"))
        if link == None:
            self.error(400)
            return
        newlink = XRD.parse_link(self.request.body) 
        link.rel = newlink.rel;
        link.type = newlink.type;
        link.href = newlink.href;
        link.template = newlink.template;
        link.put()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
#        self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)
    
    # HTTP DELETE handler, delete an existing link
    def delete(self):
        acct = self.request.get("acct")
        if acct == None:
            self.error(400)
            return            
        link = XRD.get_link(acct,
                            self.request.get("rel"),
                            self.request.get("type"),
                            self.request.get("href"),
                            self.request.get("template"))
        if link == None:
            self.error(404)
            return            
        link.delete()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
#        self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)


application = webapp.WSGIApplication([('/xrdp', MainPage)],
                                     debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()