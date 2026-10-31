import json, sys, collections, time, gzip, math
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely import make_valid
from shapely.ops import polylabel
SIM=float(sys.argv[1]); TOL=float(sys.argv[2]); Q=float(sys.argv[3]); OUT=len(sys.argv)>4
d=json.load(open('sel.geojson'))
fs=[f for f in d['features'] if not f['properties']['n'].startswith('(')]
byname=collections.defaultdict(list)
for f in fs: byname[f['properties']['n']].append(f)
geoms=[]   # list of encoded bytes
rows=[]    # name, from, to, gidx
labels=[]  # per geom: lon, lat, areaKm2
def zz(v): return (v<<1) ^ (v>>31)
def varint(v, out):
    v=zz(v)
    while True:
        b=v&0x7f; v>>=7
        if v: out.append(b|0x80)
        else: out.append(b); break
def uvar(v,out):
    while True:
        b=v&0x7f; v>>=7
        if v: out.append(b|0x80)
        else: out.append(b); break
nv=0
for n,lst in byname.items():
    lst.sort(key=lambda f:f['properties']['a'])
    prev=None; prevIdx=None
    for f in lst:
        p=f['properties']
        g=shape(f['geometry'])
        if not g.is_valid: g=make_valid(g)
        if prev is not None:
            try:
                if g.symmetric_difference(prev).area < SIM*max(g.area,1e-9):
                    rows.append((n,p['a'],p['b'],prevIdx)); continue
            except Exception: pass
        gs=g.simplify(TOL, preserve_topology=True)
        polys=[pg for pg in getattr(gs,'geoms',[gs]) if pg.geom_type=='Polygon' and not pg.is_empty]
        tot=sum(pg.area for pg in polys)
        polys=[pg for pg in polys if pg.area>=0.004 or pg.area>=0.2*tot]
        if not polys:
            polys=[pg for pg in getattr(g,'geoms',[g]) if pg.geom_type=='Polygon']
        out=bytearray()
        uvar(len(polys),out)
        lx=ly=0
        for pg in polys:
            rings=[pg.exterior]+list(pg.interiors)
            enc=[]
            for r in rings:
                cs=[(round(x/Q),round(y/Q)) for x,y in r.coords]
                o=[cs[0]]
                for c in cs[1:]:
                    if c!=o[-1]: o.append(c)
                if o[0]==o[-1]: o=o[:-1]
                if len(o)>=3: enc.append(o)
            uvar(len(enc),out)
            for o in enc:
                uvar(len(o),out); nv+=len(o)
                for x,y in o:
                    varint(x-lx,out); varint(y-ly,out); lx,ly=x,y
        big=max(polys,key=lambda pg:pg.area)
        try: lp=polylabel(big, tolerance=0.05)
        except Exception: lp=big.representative_point()
        geoms.append(bytes(out)); labels.append((round(lp.x,2),round(lp.y,2)))
        prev=g; prevIdx=len(geoms)-1
        rows.append((n,p['a'],p['b'],prevIdx))
blob=b''.join(geoms)
print('SIM',SIM,'TOL',TOL,'Q',Q,'geoms',len(geoms),'rows',len(rows),'verts',nv,'bytes',len(blob),'gz',len(gzip.compress(blob,9)))
if OUT:
    offs=[];o=0
    for gb in geoms: offs.append(o); o+=len(gb)
    open('geoms.bin','wb').write(blob)
    json.dump({'Q':Q,'offs':offs,'labels':labels,'rows':rows},open('geoms_meta.json','w'),ensure_ascii=False)
