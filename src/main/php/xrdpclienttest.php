<?php 
require 'xrdpclient.php';

// account access params
$url = 'http://xrdpdemo.appspot.com/xrdp';
$acct = 'charlie';

// make a couple of links for testing
$rel = "http://oexchange.org/spec/0.8/rel/user-target";
$type = "application/xrd+xml";
$href = "http://oexchange.org/demo/linkeater/oexchange.xrd";
$newrel = "newrel";
$link = new Link($rel, $type, $href);
$newlink = new Link($newrel, $type, $href);

// add a link, update it and delete it
$client = new XRDPClient($url);
echo $client->get($acct);
/*
echo $client->add($acct, $link);
echo $client->update($acct, $link, $newlink);
echo $client->delete($acct, $newlink);
*/
//echo $client->delete($acct, $link);

?>