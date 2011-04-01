#!/usr/bin/env python
import sys
import yaml

raw = open(sys.argv[1]).read()
sys.stderr.write("loading\n")
items = yaml.load(raw)
sys.stderr.write("fixing\n")
line = None
route = None
all = []
for item in items:
    if line is None:
        line = item
    else:
        route = item
        code, name = line
        all.append({"name": name, "code": code, "route": route})
        route = line = None
sys.stderr.write("serializing and dumping\n")
print yaml.dump(all, default_flow_style=False)
