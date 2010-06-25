import os
import logging

from xml.dom import minidom
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# build a webfinger XRD document from a list of links and an acct 
def make_XRD(links, acct):
    template_params = {'links': links,
                       'acct': acct}
    path = os.path.join(os.path.dirname(__file__), 'xrd.tmpl')
    return template.render(path, template_params)

# query for the db for the links for the specified account 
def get_links(acct, filter=None):
    query = Link.all()
    query.filter("acct =", acct)
    if filter:
        for k, v in filter.iteritems():
            query.filter(k + " =", v)
    return query

# query the db for a link matching the specified criteria
def get_link(acct, rel, type, href, template):
    query = Link.all()
    query.filter("rel =", rel)
    query.filter("type =", type)
    if href:
        query.filter("href =", href)
    elif template:
        query.filter("template =", template)
    links = query.fetch(1)
    if len(links):
        return links[0]
    return

def get_link_by_key(key):
    try:
        return db.get(key)
    except:
        return None
    
# read a Link element from a string
def parse_link(content):
    try:
        dom = minidom.parseString(content)
    except Exception as e:
        logging.error("could not parse link: " + content + " exception: " + str(type(e)) + str(e.args))
        return
    if dom:
           el = dom.documentElement
    else:
        return
    logging.info("parsed link")
    if el == None or el.tagName != "Link":  # validate single Link tag
        return
    attrs = el.attributes
    
    # build the link
    link = Link()
    link.content = content
    if attrs.get("rel"):
        link.rel = attrs.get("rel").nodeValue
    else:
        return
    if attrs.get("type"):
        link.type = attrs.get("type").nodeValue
    else:
        return
    if attrs.get("href"):
        link.href = attrs.get("href").nodeValue
    elif attrs.get("template"):
        link.template = attrs.get("template").nodeValue
    else:  # href XOR template is required
        return
    return link

def new_link(attrs):
    link = Link()
    if attrs.get("rel"):
        link.rel = attrs.get("rel")
    else:  # rel required
        return
    if attrs.get("type"):
        link.type = attrs.get("type")
    else:  # type required
        return
    if attrs.get("href"):
        link.href = attrs.get("href")
    elif attrs.get("template"):
        link.template = attrs.get("template")
    else:  # href XOR template is required
        return
    link.content = link.makexml()
    return link

# representation of an XRD link element.  links can have either an href OR a template value
class Link(db.Model):
    acct = db.StringProperty()
    rel = db.StringProperty()
    type = db.StringProperty()
    href = db.StringProperty()
    template = db.StringProperty()
    content = db.StringProperty()  # original link text that was submitted
    
    # build new xml for this link from its attributes
    def makexml(self):
        doc = minidom.Document()
        el = doc.createElement("Link")
        el.setAttribute("rel", self.rel)
        el.setAttribute("type", self.type)
        if self.href:
            el.setAttribute("href", self.href)
        elif self.template:
            el.setAttribute("template", self.template)
        return el.toxml("UTF-8")

    # return content with xml:id set to key
    def toxml(self):
        try:
            dom = minidom.parseString(self.content)
        except:
            return
        if dom == None:
            return
        el = dom.documentElement
        if el == None or el.tagName != "Link":  # validate single Link tag
            return
        el.setAttribute("xml:id", str(self.key()))
        return el.toxml("UTF-8")
