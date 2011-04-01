#!/usr/bin/env python
import sys
import os
import random
import time
import shelve
import urllib
import socket

BASE = "http://urbs-web.curitiba.pr.gov.br/centro/j_urbs2.asp"
BASE_REF = "http://urbs-web.curitiba.pr.gov.br/centro/defmapalinhas.asp?l=n"
BASE_IMG = "http://urbs-web.curitiba.pr.gov.br/centro/mapa/tmp"
DELAY = 0.3

def split_box(boxdata):
    try:
        return [float(tok) for tok in boxdata.split(";") if tok]
    except ValueError, e:
        sys.stderr.write("invalid data: %s\n" % (repr(boxdata)))
        raise

def download_one(line, dest, cx="0", cy="0", radius="250", ref=BASE_REF,
        cookiebase="1337"):
    params = {"cx": str(cx), "cy": str(cy), "r": str(radius),
        "ll": str(cookiebase), "cl": str(line), "ref": ref}
    urlreq = BASE + "?" + urllib.urlencode(params)
    urlimg = BASE_IMG + str(cookiebase) + ".gif"
    while True:
        try:
            boxdata = urllib.urlopen(urlreq).read()
            imgdata = urllib.urlopen(urlimg).read()
        except (IOError, socket.error), e:
            delay = random.randint(1, 120)
            print "error: %s, sleeping for %d" % (e, delay)
            time.sleep(delay)
            continue
        if is_error(boxdata) or is_error(imgdata):
            print "retrying", repr(boxdata)[:10], repr(imgdata)[:10]
            time.sleep(DELAY * 5)
            continue
        imgpath = dest + ".gif"
        boxpath = dest + ".box"
        f = open(imgpath, "w")
        f.write(imgdata)
        f.close()
        f = open(boxpath, "w")
        f.write(boxdata)
        f.close()
        break
    return split_box(boxdata)

def is_error(data):
    return data.startswith("\r\n<") or data.startswith("<!")

def download(lines, basedir, seq=None):
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    for i, line in enumerate(lines):
        destbase = os.path.join(basedir, str(line))
        print "getting box for", line
        basebox = download_one(line, destbase, cx=0, cy=0, radius=50)
        minx, miny, maxx, maxy = basebox
        zoom = 400
        cx = minx
        stepx = 0
        while cx < maxx:
            cy = miny
            stepy = 0
            while cy < maxy:
                dest = destbase + ("-%02dx%02d" % (stepx, stepy))
                download_one(line, dest, cx=cx, cy=cy, radius=zoom)
                try:
                    #delay = abs(random.gauss(DELAY, 0.1) + 0.01)
                    delay = 0.0
                    time.sleep(delay)
                except IOError:
                    print "bogus delay:", delay
                    continue
                print "got", dest
                sys.stdout.flush()
                stepy += 1
                cy += zoom
            stepx += 1
            cx += zoom
        delay = random.randint(1, 60 * 6)
        print "sleeping for %d seconds" % (delay)
        time.sleep(delay)

print "loading"
lines = [str(line["line"]["code"])
        for line in shelve.open("all.shelve")["all"]]
if len(sys.argv) == 2:
    last = sys.argv[1]
    lines = lines[lines.index(last):]
#download([528], "./maps-2")
download(lines, "./maps-3")
