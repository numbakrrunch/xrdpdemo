import xrdpclient
import httpclient

url="http://localhost:9090/xrdp"
#url="http://xrdpdemo.appspot.com/xrdp"
acct="charlie"
link={"rel": "http://oexchange.org/spec/0.8/rel/user-target",
      "type": "application/xrd+xml",
      "href": "http://oexchange.org/demo/linkeater/oexchange.xrd"}
newlink=link.copy();
newlink["rel"] = "newrel"

# get
print "--GET: fetching xrd"
print httpclient.get(url, params={"acct":"charlie"})

# POST/create
print "--POST: adding a new link"
#print xrdpclient.add(url, acct, link)
print xrdpclient.add(url, acct, newlink)

## PUT/update
#print "--PUT: updating the link"
#print xrdpclient.update(url, acct, link, newlink)
#
## DELETE/remove
#print "--DELETE: removing the link"
#print xrdpclient.delete(url, acct, newlink)
