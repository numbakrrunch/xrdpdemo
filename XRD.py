import os

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
def get_links(account):
    query = Link.all()
    query.filter("acct =", account)
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

# read a Link element from a string
def parse_link(str):
    try:
        dom = minidom.parseString(str)
    except:
        return
    if dom:
           el = dom.documentElement
    else:
        return
    if el == None or el.tagName != "Link" or el.hasChildNodes():  # validate single Link tag
        return
    attrs = el.attributes
    
    # build the link
    link = Link() 
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


# representation of an XRD link element.  links can have either an href OR a template value
class Link(db.Model):
    acct = db.StringProperty()
    rel = db.StringProperty()
    type = db.StringProperty()
    href = db.StringProperty()
    template = db.StringProperty()
    
    def toxml(self):
        doc = minidom.Document()
        el = doc.createElement("Link")
        el.setAttribute("rel", rel)
        el.setAttribute("type", type)
        if href:
            el.setAttribute("href", href)
        elif template:
            el.setAttribute("template", template)
        return el.toxml("UTF-8")
