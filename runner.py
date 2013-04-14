# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, abort, render_template, g, Response
import requests
import ipdb
from functools import wraps
from derp import DerpPage
import pickle
import psycopg2
import os
import datetime


app = Flask(__name__)
allowed_sites = ("expressen.se",
                 "aftonbladet.se",
                 "svd.se",
                 "wsj.com",)


class MyDerpPage(DerpPage):
    def derpify(self, ):
        self.derp_expression = u"[A-Za-zåäöÅÄÖé]+"
        DerpPage.derpify(self) # TODO: something using super instead or whatever


@app.before_request
def before_request():
    conn_string = os.environ['DATABASE_URL']
    g.conn = psycopg2.connect(conn_string)


@app.teardown_request
def teardown_request(exception):
    g.conn.close()    


def page_cache(f):
    """
    Stupid cache using postgres table
    """
    @wraps(f)
    def inner(site, path):
        """
        CREATE TABLE cacher (
            site character varying(31), 
            page character varying(255), 
            content text,
            timestamp timestamp,
            PRIMARY KEY (site, page)
        )
        """
        now = datetime.datetime.now()
        cursor = g.conn.cursor()
        cursor.execute("SELECT content, timestamp FROM cacher WHERE site=%s AND page=%s", (site, path,))
        if cursor.rowcount > 0:
            row = cursor.fetchone()
            if row[1]+datetime.timedelta(seconds=60)>now:
                print("using cache")
                return row[0]
            else:
                cursor.execute("DELETE FROM cacher WHERE site=%s AND page=%s", (site, path,))
        
        content = f(site, path)
        cursor.execute("INSERT INTO cacher(site, page, content, timestamp) VALUES (%s, %s, %s, %s)", (site, path, content, now,))
        g.conn.commit()
        return content
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

@app.route('/robots.txt')
def robots():
    robot = "User-agent: *\n"
    for s in allowed_sites:
        robot += "Disallow: /%s/\n" % s
    return Response(robot, mimetype='text/txt')

    


    

if __name__ == '__main__':
    app.run(debug=True)