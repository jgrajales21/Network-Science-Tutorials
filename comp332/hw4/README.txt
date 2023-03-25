Files:
web_client.py
web_proxy.py
http_util.py

web_client.py:
Sends url to web_proxy in the form of a GET request and waits for response from host name
server (deleivered by the web proxy)

web_proxy.py:
Recives GET request from web client and checks to see if the url
in GET request was recently visited (i.e is it in the cache). If the url is in
the cache then a CONDITIONAL GET request is sent to the host name server. Else,
a standard GET request is sent to the host name server.

Each HTTP response from a CONDITONAL GET is then parsed for the HTTP response code
to then infrom the web cleint.

http_util.py:
includes helpful functions to extract data from and format GET requests

WRITE-UP

This project only involved manipulation of the web_proxy.py file as this is the
location that the cache is implemented. Becuase caches require the efficient
storage and access of data I choose to implement it using a dictionary where
the keys were (hostname, pathname) tuples and the values were the http
responses from the host name servers. The main use cases of the cache is when
in need to check if a conditional GET request must be sent and when
interpreting the response code of a CONDITIONAL GET request. To this end we
interact with our cachce immediately after recieveing the message from the web
client and host name server.

Examples of functional links were provided at the bottom of the web_client.py
file where links that prompt the 304 HTTP response are commented beside links.
The code works for all of these links. I also used many links from this
website: http://www.testingmcafeesites.com all of which returned 304 response
codes.
