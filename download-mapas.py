#!/usr/bin/env python
import sys
import os
import random
import time
import shelve
import urllib

BASE = "http://urbs-web.curitiba.pr.gov.br/centro/j_urbs2.asp"
BASE_REF = "http://urbs-web.curitiba.pr.gov.br/centro/defmapalinhas.asp?l=n"
BASE_IMG = "http://urbs-web.curitiba.pr.gov.br/centro/mapa/tmp"

def download(lines, basedir, seq=None):
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    params = {"cx": "0", "cy": "0", "raio": "250", "ll": "", "cl": "528", "ref": BASE_REF}
    cookiebase = random.randint(0, 99999)
    for i, line in enumerate(lines):
        cookie = cookiebase + i
        code = str(line["line"]["code"])
        if seq and code not in seq:
            continue
        params["cl"] = code
        params["ll"] = str(cookie)
        urlreq = BASE + "?" + urllib.urlencode(params)
        box = urllib.urlopen(urlreq).read()
        urlimg = BASE_IMG + str(cookie) + ".gif"
        imgdata = urllib.urlopen(urlimg).read()
        imgpath = os.path.join(basedir, code + ".gif")
        boxpath = os.path.join(basedir, code + ".box")
        f = open(imgpath, "w")
        f.write(imgdata)
        f.close()
        f = open(boxpath, "w")
        f.write(box)
        f.close()
        time.sleep(0.5)
        print "wrote", imgpath, boxpath

lines = shelve.open("all.shelve")["all"]
download(lines, "./maps", sys.argv[1:])
