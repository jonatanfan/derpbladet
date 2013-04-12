from flask import Flask, request
import requests
import ipdb
import BeautifulSoup
import re
from urlparse import urlparse

app = Flask(__name__)

def translate(content):
    soup = BeautifulSoup.BeautifulSoup(content)
    
    for tag in ("h1", "h2", "h3", "p", "a", "strong", "span", "div", "em", "i", "option", "time", "title"):
        for paragraph in soup.findAll(tag):
            for i in range(len(paragraph.contents)):
                if type(paragraph.contents[i]) == BeautifulSoup.NavigableString:
                    paragraph.contents[i] = BeautifulSoup.NavigableString(re.sub("[A-Za-z\xe5\xe4\xf6\xc5\xc4\xd6\;]+", "DERP", paragraph.contents[i]))         
    
    for link in soup.findAll("link"):
        if link["href"][0] == "/":
            link["href"] = "http://www.aftonbladet.se%s" % link["href"]
            
    for a in soup.findAll("a"):
        href=filter(lambda t: t[0]=="href", a.attrs)[0]
        url = urlparse(href[1])
        if url.hostname == "www.aftonbladet.se":
            a.attrs.remove(href)
            a.attrs.append(("href", "%s%s" % (request.host_url, url.path[1:])))               
    return soup.prettify()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def page(path):
    r = requests.get('http://www.aftonbladet.se/%s' % path)
    return translate(r.content)


if __name__ == '__main__':
    app.run(debug=True)