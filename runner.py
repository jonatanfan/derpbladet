# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, abort, render_template
import requests
import ipdb
from functools import wraps
from derp import DerpPage


app = Flask(__name__)
allowed_sites = ("expressen.se",
                 "aftonbladet.se",
                 "svd.se",
                 "wsj.com",)


class MyDerpPage(DerpPage):
    def derpify(self, ):
        self.derp_expression = u"[A-Za-zåäöÅÄÖé]+"
        DerpPage.derpify(self) # TODO: something using super instead or whatever


def page_cache(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return f(*args, **kwargs)
    return inner


def site_allowed(site):
    if site in allowed_sites:
        return True
    else:
        return False

    
@app.route('/<site>/', defaults={'path': ''})
@app.route('/<site>/<path:path>')
@page_cache
def page(site, path):
    if site_allowed(site):
        r = requests.get('http://%s/%s' % (site, path))
        page = MyDerpPage(site, r.content)
        return page.translate()
    else:
        return abort(404)

@app.route('/')
def index():
    return render_template("index.html", allowed_sites=allowed_sites)
    

if __name__ == '__main__':
    app.run(debug=True)