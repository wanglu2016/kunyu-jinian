# -*- coding: utf-8 -*-
"""Step 1: prepare inputs for geo3.py / build.py.

Reads (put these in tools/input/):
  cliopatria.geojson            unzipped from Cliopatria's cliopatria.geojson.zip (v0.21 was used)
  china-chronology-data.js      dist/data-*.js from the npm package china-chronology@0.1.0
Writes (in tools/):
  sel.geojson        polities whose ToYear >= -800, with compact properties n/a/b/i
  extra_meta.json    Wikipedia titles, membership and aggregate components
  zh_names.json      English name -> Chinese name, from zh_asia.tsv + zh_west.tsv
  chronology.json    Chinese era names (年号) table
"""
import json, re

src = json.load(open('input/cliopatria.geojson', encoding='utf8'))

# sel.geojson
feats = [f for f in src['features'] if f['properties']['ToYear'] >= -800 and f['geometry']]
for i, f in enumerate(feats):
    p = f['properties']
    f['properties'] = {'n': p['Name'], 'a': p['FromYear'], 'b': p['ToYear'], 'i': i}
json.dump({'type': 'FeatureCollection', 'features': feats}, open('sel.geojson', 'w'))

# extra_meta.json
mem, wiki, comps = {}, {}, {}
for f in json.load(open('input/cliopatria.geojson', encoding='utf8'))['features']:
    p = f['properties']
    if p['ToYear'] < -800: continue
    n = p['Name']
    if p['Wikipedia'] and n not in wiki: wiki[n] = p['Wikipedia']
    if p['MemberOf']: mem[f"{n}@{p['FromYear']}"] = p['MemberOf']
    if n.startswith('('): comps.setdefault(n, set()).update(c for c in p['Components'].split(';') if c)
json.dump({'wiki': wiki, 'mem': mem, 'comps': {k: sorted(v) for k, v in comps.items()}},
          open('extra_meta.json', 'w'), ensure_ascii=False)

# zh_names.json
zh = {}
for fn in ['zh_asia.tsv', 'zh_west.tsv']:
    for line in open(fn, encoding='utf8'):
        line = line.rstrip('\n')
        if line:
            k, v = line.split('\t'); zh[k] = v
json.dump(zh, open('zh_names.json', 'w'), ensure_ascii=False)

# chronology.json (the package ships its dataset as a JS object literal)
t = open('input/china-chronology-data.js', encoding='utf8').read()
i = t.index('var defaultDataset = ') + len('var defaultDataset = ')
depth = 0
for j in range(i, len(t)):
    if t[j] == '{': depth += 1
    elif t[j] == '}':
        depth -= 1
        if depth == 0: break
obj = re.sub(r'^(\s*)(dynasties|eras|ganzhi):', r'\1"\2":', t[i:j + 1], flags=re.M)
obj = re.sub(r',(\s*[\]}])', r'\1', obj)
json.dump(json.loads(obj), open('chronology.json', 'w'), ensure_ascii=False)
print('prepared', len(feats), 'rows;', len(zh), 'Chinese names')
