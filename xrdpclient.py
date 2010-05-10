import httpclient
from xml.dom.minidom import Document

headers = {'Content-Type': 'application/xrd+xml'}

def add(url, acct, link):
    return httpclient.req(url, link_to_xml(link), {"acct": acct}, headers=headers)

def update(url, acct, link, newvalue):
    params = link.copy()
    params["acct"] = acct
    return httpclient.req(url, link_to_xml(newvalue), params, headers=headers, method="PUT")

def delete(url, acct, link):
    params = link.copy()
    params["acct"] = acct
    return httpclient.req(url, params=params, headers=headers, method="DELETE")

def link_to_xml(link):
    doc = Document()
    el = doc.createElement("Link")
    for name, val in link.iteritems():
        el.setAttribute(name, val)
    return el.toxml("UTF-8")

