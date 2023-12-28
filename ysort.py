#!/usr/bin/env python3

import sys
import yaml

lut = ""
lookup = dict()
sets = []
bigset = set()
missing_lut = False

def dict_representer(dumper, data):
  global bigset
  mapping = sorted(list(data.items()), key=lambda arg:lookup.get(arg[0].lower(), 9999))
  if missing_lut:
    curset = set(data.keys())
    if len(curset)>1:
      if not bigset >= curset:
        if not bigset & curset:
          sets.append(list(data.keys()))
        else:
          for i, aset in enumerate(sets):
            exc = curset & set(aset)
            if exc:
              sets[i].extend(filter(lambda x: x not in exc, data.keys()))
        bigset |= curset
    mapping = data.items()
  return dumper.represent_mapping('tag:yaml.org,2002:map', mapping)

document = False if sys.stdin.isatty() else sys.stdin.read()
if len(sys.argv)>1:
  try:
    with open(sys.argv[1], encoding="UTF-8") as f:
      document = f.read()
  except IOError:
    pass
if document is not False:
  try:
    with open("ysort.lut", encoding="UTF-8") as f:
      lut = f.read()
  except IOError:
    missing_lut = True
  lookup.update({item.strip().lower():id+len(lookup) for id, item in enumerate(lut.splitlines()) if item and not item.startswith('#')})
  yaml.add_representer(dict, dict_representer)
  docs = yaml.load_all(document, Loader=yaml.Loader)
  clean = '---\n'.join(yaml.dump(doc) for doc in docs)
  if missing_lut:
    if 0:
      while len(bigset) < sum([len(x) for x in sets]):
        bigset = set()
        for i, curset in enumerate(sets):
          if curset & bigset:
            sets[i] = set()
            for j, aset in enumerate(sets):
              if aset & curset:
                sets[j] |= curset
            sets.pop(i)
          bigset |= curset
    with open("ysort.lut", "wt", encoding="UTF-8") as f:
      f.write("""\
# ysort.lut - ysort lookup table
# All yaml mappings at all levels will be sorted according to the order of the keys in this document.
# Missing keys keep their relative order at the end of the mapping. Case does not matter.

""")
      f.write("\n".join(["".join([y+"\n" for y in x]) for x in sets]))
    print("ysort infile.yaml outfile.yaml --- created lookup table in file ysort.lut")
  else:
    if len(sys.argv)>2:
      with open(sys.argv[2], "wt", encoding="UTF-8") as fout:
        fout.write(clean)
    else:
      print(clean)
else:
  print("ysort infile.yaml outfile.yaml --- sort YAML mappings with attached lookup table (ysort.lut)")
