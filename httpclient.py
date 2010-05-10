import urllib
import urllib2
import httplib

# simple HTTP GET
# TODO timeouts
def get(url, params=None, headers={}):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    if params:
        url = url + "?" + urllib.urlencode(params)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

# build your own HTTP request
# TODO timeouts
def req(url, body=None, params=None, headers={}, method="POST"):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    if params:
        url = url + "?" + urllib.urlencode(params)
    request = urllib2.Request(url, body, headers)
    request.get_method = lambda: method
    response = urllib2.urlopen(request)
    return response.read()
