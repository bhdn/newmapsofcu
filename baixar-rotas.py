#!/usr/bin/env python
import sys
import os
import urllib
import re
import time

URL_LINHAS = "http://urbs-web.curitiba.pr.gov.br/centro/conteudo_lista_linhas.asp?l=%27n%27"
URL_ROTA = "http://urbs-web.curitiba.pr.gov.br/centro/lista_ruas.asp"

EXPR_LINHAS = re.compile(r"<option value='(?P<code>\d+)'>(?P<nome>[^<]+)</option>")
EXPR_ROUTE = re.compile(r"<option .*? value='(?P<code>[^']+)'>(?P<name>[^<]+)</option>")

SOURCE_ENCODING = "latin-1"

def parse_lines(raw):
    for match in EXPR_LINHAS.finditer(raw):
        code = match.group("code")
        rawname = match.group("nome")
        name = rawname.decode(SOURCE_ENCODING)
        yield [code, name]

def fetch_route(code, line):
    params = {"l": code, "nl": line.encode(SOURCE_ENCODING)}
    url = URL_ROTA + "?" + urllib.urlencode(params)
    raw = urllib.urlopen(url).read()
    return raw

def parse_route(raw):
    for match in EXPR_ROUTE.finditer(raw):
        code = match.group("code")
        rawname = match.group("name")
        try:
            name = rawname.decode("ascii")
        except UnicodeError:
            name = rawname.decode(SOURCE_ENCODING)
        else:
            name = rawname
        yield [code, name]

def get_route(lines):
    print "# vim:ft=yaml"
    for code, name in lines:
        raw = fetch_route(code, name)
        route = parse_route(raw)
        yield [[code, name], list(route)]

def main():
    import yaml
    raw = urllib.urlopen(URL_LINHAS).read()
    for route in get_route(parse_lines(raw)):
        print yaml.dump(route, default_flow_style=False, encoding="utf-8")

if __name__ == "__main__":
    main()
