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

class MainPage(webapp.RequestHandler):

    # HTTP GET handler, not defined by XRDS, returns resource descriptor
    def get(self):
        acct = self.request.get("acct")
        if acct == "":
            self.error(400)
            self.response.out.write("error: acct not provided")
            return
        key = self.request.get("xmlid")
        if key:
            link = XRD.get_link_by_key(key)
            if link == None:
                self.error(404)
                self.response.out.write("link not found for id: " + key)
                return
            else:
                links = [link]
        else:
            query = self.read_link_params()
            links = XRD.get_links(acct, query)
        logging.info(str(links))
        xrd = XRD.make_XRD(links, acct)
        if self.request.get("suppress_response_type"):
            self.response.headers['Content-Type'] = 'text/html'
        else:
            self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)

    # HTTP POST handler, add a link if there isn't already a link with the same properties
    def post(self):
        acct = self.request.get("acct")
        if acct == "":
            self.error(400)
            self.response.out.write("error: acct not provided")
            return
        type = self.request.headers['Content-Type']
        if type == "application/x-www-form-urlencoded":
            logging.info("formencoded")
            params = self.read_link_params(True);
            logging.info("link params: " + str(params))
            if params == None:  # error already sent by get_link()
                return
            link = XRD.new_link(params)
        else:
            link = XRD.parse_link(self.request.body)
            if link == None:
                self.error(400)
                self.response.out.write("error: could not parse a link from request body")
                return
            
        link.acct = acct
        existing = XRD.get_link(acct, link.rel, link.type, link.href, link.template)
        if existing:  # conflict
            self.error(409)
            self.response.out.write("error: a link with the same rel, type, href/template already exists")
            return
        link.put()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
        if self.request.get("suppress_response_type"):
            self.response.headers['Content-Type'] = 'text/html'
        else:
            self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)
    
    # HTTP PUT handler, update an existing link
    def put(self):
        acct = self.request.get("acct")
        if acct == "":
            self.error(400)
            self.response.out.write("error: acct not provided")
            return
        key = self.request.get("xmlid")
        if key:
            link = XRD.get_link_by_key(key)
            if link == None:
                self.error(404)
                self.response.out.write("link not found for id: " + key)
                return
        else:
            query = self.read_link_params()
            links = XRD.get_links(acct, query)
            if links == None or links.count() == 0:
                self.error(404)
                self.response.out.write("link not found")
                return
            elif links.count() > 1:
                self.error(400)
                self.response.out.write("more than one match found")
                return
            link = links[0]
        link.delete()
        newlink = XRD.parse_link(self.request.body)
        newlink.acct = acct
        newlink.put()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
        if self.request.get("suppress_response_type"):
            self.response.headers['Content-Type'] = 'text/html'
        else:
            self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)
    
    # HTTP DELETE handler, delete an existing link
    def delete(self):
        acct = self.request.get("acct")
        if acct == "":
            self.error(400)
            self.response.out.write("error: acct not provided")
            return
        key = self.request.get("xmlid")
        if key:
            link = XRD.get_link_by_key(key)
            if link == None:
                self.error(404)
                self.response.out.write("link not found for id: " + key)
                return
            else:
                links = [link]
        else:
            query = self.read_link_params()
            links = XRD.get_links(acct, query)        
            if links == None or links.count() == 0:
                self.error(404)
                self.response.out.write("error: link matching your params not found")
                return
        for link in links:
            link.delete()
        xrd = XRD.make_XRD(XRD.get_links(acct), acct)
        if self.request.get("suppress_response_type"):
            self.response.headers['Content-Type'] = 'text/html'
        else:
            self.response.headers['Content-Type'] = 'application/xrd+xml'
        self.response.out.write(xrd)

    # read a link from a request 
    def read_link_params(self, validate = False):
        attrs = self.request
        link = {}
        if attrs.get("rel"):
            link['rel'] = attrs.get("rel")
        elif validate:  # rel required
            self.error(400)
            self.response.out.write("error: missing rel attribute")
            return
        if attrs.get("type"):
            link['type'] = attrs.get("type")
        elif validate:  # type required
            self.error(400)
            self.response.out.write("error: missing type attribute")
            return
        if attrs.get("href"):
            link['href'] = attrs.get("href")
        elif attrs.get("template"):
            link['template'] = attrs.get("template")
        elif validate:  # href XOR template is required
            self.error(400)
            self.response.out.write("error: href or template attribute required but missing")
            return
        return link

application = webapp.WSGIApplication([('/xrdp', MainPage)],
                                     debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()