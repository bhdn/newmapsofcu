#!/usr/bin/env python
import sys
import os
import re
import unicodedata
import shelve
import locale

MAIN_NAME = "index.html"
STATIONS_NAME = "estacao"
STREETS_NAME = "rua"

import yaml
from Cheetah.Template import Template

def load(path, cachepath):
    load = True
    if os.path.exists(cachepath):
        load = False
        modyaml = os.stat(path).st_mtime
        modcache = os.stat(cachepath).st_mtime
        if modyaml > modcache:
            load = True
    sh = shelve.open(cachepath)
    lines = None
    if load:
        raw = open(path).read()
        lines = yaml.load(raw) 
        sh["all"] = lines
    else:
        sh = shelve.open(cachepath)
        lines = sh["all"]
    sh.close()
    return lines

def file_name(name):
    if not isinstance(name, unicode):
        name = name.decode("utf8")
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore")
    name = name.lower()
    name = re.sub(r"[.,/ ?*]", "-", name)
    name = name + ".html"
    return name

def get_template(path):
    return open(path).read().decode(locale.getpreferredencoding())

def _dump_template(tmplpath, outpath, context):
    source = get_template(tmplpath)
    tmpl = Template(source=source, searchList=context)
    f = open(outpath, "w")
    f.write(tmpl.respond().encode(locale.getpreferredencoding()))
    f.close()

def dump_main(lines, basedir, mainpath):
    context = {"lines": lines, "file_name": file_name}
    path = os.path.join(basedir, MAIN_NAME)
    _dump_template(mainpath, path, context)

def dump_lines(lines, basedir, linepath):
    for line in lines:
        info = line["line"] # arg!
        lfname = file_name(info["name"])
        lfpath = os.path.join(basedir, lfname)
        context = {"line": line, "info": info,
                "file_name": file_name}
        _dump_template(linepath, lfpath, context)

def dump_stations(lines, basedir, stationspath, stationpath, streetspath,
        streetpath):
    stations = {} # name : lines
    streets = {}
    for line in lines:
        info = line["line"]
        routes = info["route"]
        for code, routename in routes:
            if code.endswith("|S") or code.endswith("|N"):
                stations.setdefault(routename, set()).add(info["name"])
            else:
                streets.setdefault(routename, set()).add(info["name"])
    ctxstations = {"stations": ((st, file_name(st))
                    for st in sorted(stations))}
    ctxstreets = {"streets": ((st, file_name(st))
                    for st in sorted(streets))}
    stationsdir = os.path.join(basedir, STATIONS_NAME)
    streetsdir = os.path.join(basedir, STREETS_NAME)
    if not os.path.exists(stationsdir):
        os.mkdir(stationsdir)
    if not os.path.exists(streetsdir):
        os.mkdir(streetsdir)
    path = os.path.join(stationsdir, "index.html")
    _dump_template(stationspath, path, ctxstations)
    path = os.path.join(streetsdir, "index.html")
    _dump_template(streetspath, path, ctxstreets)
    # now dump page for each street and station
    prefix = "../"
    for stationname, lines in sorted(stations.iteritems()):
        linesurl = ((line, prefix + file_name(line)) for line in lines)
        context = {"station": stationname, "lines": linesurl}
        path = os.path.join(stationsdir, file_name(stationname))
        _dump_template(stationpath, path, context)
    for streetname, lines in sorted(streets.iteritems()):
        linesurl = ((line, prefix + file_name(line)) for line in lines)
        context = {"street": streetname, "lines": linesurl}
        path = os.path.join(streetsdir, file_name(streetname))
        _dump_template(streetpath, path, context)

def dump(lines, basedir, mainpath, linepath, stationspath, stationpath,
        streetspath, streetpath):
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    dump_main(lines, basedir, mainpath)
    dump_lines(lines, basedir, linepath)
    dump_stations(lines, basedir, stationspath, stationpath, streetspath,
            streetpath)

if __name__ == "__main__":
    print "loading"
    lines = load("all.yaml", "all.shelve")
    print "dumping"
    dump(lines, sys.argv[1], "main.tmpl", "route.tmpl", "stations.tmpl",
            "station.tmpl", "streets.tmpl", "street.tmpl")
