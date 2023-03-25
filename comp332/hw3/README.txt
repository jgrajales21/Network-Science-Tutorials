1. begin running the web_proxy.py file by typing the following into the
terminal: python web_proxy.py

2. In the main function of the web_client.py file type in the url youy would
like to issue a GET request to, assign this to the url variable. NOTE: you
should type in the url with 'http://' as my code cleaves this off the string.
Refer to examples in the main function for more detail.

3. Once you have put in your url into the web_client.py file run the file using
: python web_client.py

4. You should see the web proxy and the web client print a response from host
name server from both the proxy and client.

WRITE UP:

The program design is provided in detail in both files. I ordered my thought
process (as is indicated by the numbered steps). Generally, I recieved had the
web client take a url as input. Modified the url so that it fit GET request
format and then sent it into a socket to the web proxy. The web proxy then
parsed the GET request and opened a socket with the url specified in it. The
proxy then sent the get request to the host name server specified by the url
and waited for a response. Once the host name server responded it forwarded
this message to the web client upon which the code terminates

The code was tested using the links commented in the main function of the
web_client.py file.
