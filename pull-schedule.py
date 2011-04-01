import sys
import os
import urllib
import time
import re
import yaml
import locale
from cStringIO import StringIO

URL = "http://www.urbs.curitiba.pr.gov.br/PORTAL/tabelahorario/tabela.php"

EXPR_TABLE_INFO = re.compile(
              r"<font class='textoValidade'>(?P<since>[^<]+)</font> - "\
              "<font class='textoCabecalho'>(?P<type>[^<]+)</font>")
EXPR_TABLE_STATION = re.compile(
                     r"<center> Ponto: </font><font class='textoPonto'"\
                      ">(?P<station>[^<]+)</font>")
EXPR_TABLE_ENTRY = re.compile(
                     r"<td><font class='textoHorario(Adaptador)?'>"\
                      "(?P<entry>[^<]+)</font></td>")

# <td><font class='textoHorarioAdaptador'>17:46</font></td>

SOURCE_ENCODING = "latin-1"

class UnexpectedContent(Exception):
    pass

def load_lines(path):
    raw = open(path).read()
    lines = yaml.load(raw)
    return lines

def parse_schedule_table(raw):
    # fetch table information
    found = EXPR_TABLE_STATION.search(raw)
    if found:
        rawstation = found.group("station").strip()
        station = rawstation.decode(SOURCE_ENCODING)
    else:
        raise UnexpectedContent
    found = EXPR_TABLE_INFO.search(raw)
    if found:
        since = found.group("since").strip()
        rawtype = found.group("type").strip()
        type = rawtype.decode(SOURCE_ENCODING)
    else:
        raise UnexpectedContent
    # fetch the time table
    entries = []
    for found in EXPR_TABLE_ENTRY.finditer(raw):
        entry = found.group("entry").strip()
        entries.append(entry)
    table = {"station": station, "since": since, "type": type, "entries": entries}
    return table

def parse_schedule_page(line, raw):
    # split each table describing one kind of schedule
    cur = None
    tables = []
    for line in StringIO(raw):
        if cur is None and "textoPonto" in line:
            cur = StringIO()
            cur.write(line)
        elif cur:
            if "</table>" in line:
                # finished hunk
                hunk = cur.getvalue()
                cur = None
                tables.append(parse_schedule_table(hunk))
            else:
                cur.write(line)
    return tables

def pull_schedule(lines):
    for line in lines:
        params = {"cboLinha": line["code"],
                  "cboTipoDia": "0",
                  "btnAcesso": "Consultar"}
        raw = urllib.urlopen(URL, urllib.urlencode(params)).read()
        yield {"line": line, "table": parse_schedule_page(line, raw)}
        sys.stderr.write("pulled %s\n" % (line["name"].encode(locale.getpreferredencoding())))
        #time.sleep(0.5)

def main():
    lines = load_lines("rotas-fixed.yaml")
    tables = list(pull_schedule(lines))
    print yaml.dump(tables, default_flow_style=False)

if __name__ == "__main__":
    main()
