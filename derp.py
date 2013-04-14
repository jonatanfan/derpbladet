# -*- coding: utf-8 -*-
import BeautifulSoup
import re
import urlparse


class DerpPage(BeautifulSoup.BeautifulSoup):
    def __init__(self, site, content):
        self.site = site
        self.site_url = "http://%s" % self.site
        self.derp_tags = ("h1", "h2", "h3", "p", "a", "strong", "span", "div", "em", "i", "option", "time", "title")
        self.derp_content_tags = (("meta", "keywords"), ("meta", "description"))
        self.derp_expression = u"[A-Za-z]+"
        self.derp_word = "DERP"
    
        super(BeautifulSoup.BeautifulSoup, self).__init__(content, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES)
        
    def derpify(self):
        """
        translate all navigable words inside derp_tags into derps
        """
        for tag in self.derp_tags:
            for element in self.findAll(tag):
                # todo: travel the structure more pythonically
                for i in range(len(element.contents)):
                    if type(element.contents[i]) == BeautifulSoup.NavigableString:
                        element.contents[i] = BeautifulSoup.NavigableString(re.sub(self.derp_expression, self.derp_word, element.contents[i]))
                        
        for tag, attr in self.derp_content_tags:
            for element in self.findAll(tag):
                if ('name', attr) in element.attrs:
                    contents = filter(lambda t: t[0]=="content", element.attrs)
                    for content in contents:
                        element.attrs.remove(content)
                        element.attrs.append(("content", re.sub(self.derp_expression, self.derp_word, content[1])))
                    
    
    def translate_relatives(self):
        """
        translates sites relative src and href attributes into absolute links
        """
        for tag in ("link", "script", "img"):
            for element in self.findAll(tag):
                hrefs = filter(lambda t: t[0]=="href", element.attrs)
                srcs = filter(lambda t: t[0]=="src", element.attrs)               
                for attr in hrefs+srcs:
                    url = urlparse.urlparse(attr[1])
                    if not url.netloc:
                        element.attrs.remove(attr)
                        element.attrs.append((attr[0], urlparse.urljoin(self.site_url, url.geturl())))             
                                    
    def translate_links(self):
        """
        translate all absolute links into relative local site links
        """
        for a in self.findAll("a"):
            hrefs=filter(lambda t: t[0]=="href", a.attrs)
            for href in hrefs:
                url = urlparse.urlparse(href[1])
                a.attrs.remove(href)
                a.attrs.append(("href", "/%s/%s" % (self.site, url.path[1:])))

    def translate(self):
        self.translate_relatives()
        self.translate_links()
        self.derpify()
        return self.prettify()