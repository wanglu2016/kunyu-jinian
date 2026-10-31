import json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
W,H=4096,2048
IMG='input/three-globe-img/'
def xy(lon,lat): return ((lon+180)/360*W, (90-lat)/180*H)
# land mask (supersample 2x for AA)
SS=2
m=Image.new('L',(W*SS,H*SS),0); dr=ImageDraw.Draw(m)
land=json.load(open('input/natural-earth/ne_50m_land.geojson'))
for f in land['features']:
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for p in polys:
        ext=[(x*SS,y*SS) for x,y in (xy(*c) for c in p[0])]
        dr.polygon(ext,fill=255)
        for hole in p[1:]:
            dr.polygon([(x*SS,y*SS) for x,y in (xy(*c) for c in hole)],fill=0)
lakes=json.load(open('input/natural-earth/ne_50m_lakes.geojson'))
for f in lakes['features']:
    if f['properties'].get('scalerank',9)>3: continue
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    for p in polys:
        dr.polygon([(x*SS,y*SS) for x,y in (xy(*c) for c in p[0])],fill=0)
mask=np.asarray(m.resize((W,H),Image.LANCZOS)).astype(np.float32)/255.0
Image.fromarray((mask*255).astype(np.uint8)).save('out/land.png',optimize=True)
# blue marble
bm=np.asarray(Image.open(IMG+'earth-blue-marble.jpg').convert('RGB')).astype(np.float32)/255.0
lum=(0.30*bm[...,0]+0.59*bm[...,1]+0.11*bm[...,2])
# topology -> hillshade
topo=np.asarray(Image.open(IMG+'earth-topology.png').convert('L').resize((W,H),Image.BICUBIC)).astype(np.float32)/255.0
topo=ndimage.gaussian_filter(topo,1.2)
gy,gx=np.gradient(topo)
lat=np.linspace(90,-90,H)[:,None]
coslat=np.clip(np.cos(np.radians(lat)),0.15,1)
gx=gx/coslat
k=55.0
nx=-gx*k; ny=gy*k; nz=np.ones_like(nx)
nrm=np.sqrt(nx*nx+ny*ny+nz*nz)
L=np.array([-0.55,0.6,0.58]); L=L/np.linalg.norm(L)
shade=(nx*L[0]+ny*L[1]+nz*L[2])/nrm
shade=np.clip(shade,0,1)
# land color: desaturated blue marble + warm tone + elevation tint
sat=0.38
grey=lum[...,None]
col=grey+(bm-grey)*sat
warm=np.array([1.04,0.99,0.90])
col=col*warm
# elevation tint: higher -> lighter, sandier
elev=np.clip(topo,0,1)[...,None]
col=col*0.80+0.10*elev*np.array([0.95,0.88,0.75])
col=np.clip(col,0,1)
col=col*(0.55+0.62*shade[...,None])
col=np.clip(col*0.88+0.035,0,1)
hi=0.52
col=np.where(col>hi, hi+(col-hi)*0.38, col)
# ocean
lat2=np.abs(lat)/90.0
ocean=np.zeros((H,W,3),np.float32)
deep=np.array([0.035,0.085,0.115]); shelf=np.array([0.075,0.165,0.205])
dist=ndimage.distance_transform_edt(mask<0.5)
near=np.exp(-dist/9.0)[...,None]
ocean[:]=deep
ocean=ocean*(1-0.25*lat2[...,None])
ocean=ocean+(shelf-deep)*near
# subtle ocean texture from blue marble luminance (deep basins darker)

mk=mask[...,None]
out=ocean*(1-mk)+col*mk
# coastline glow
edge=np.clip(mask-ndimage.grey_erosion(mask,size=(3,3)),0,1)
out=out+edge[...,None]*np.array([0.10,0.12,0.11])*0.6
img=Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))
# rivers
dr=ImageDraw.Draw(img,'RGBA')
riv=json.load(open('input/natural-earth/ne_50m_rivers_lake_centerlines.geojson'))
for f in riv['features']:
    sr=f['properties'].get('scalerank',9)
    if sr>5: continue
    g=f['geometry']; lines=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
    w=2 if sr<=3 else 1
    a=150 if sr<=3 else 110
    for ln in lines:
        pts=[xy(*c) for c in ln]
        for i in range(len(pts)-1):
            if abs(pts[i][0]-pts[i+1][0])>W/2: continue
            dr.line([pts[i],pts[i+1]],fill=(70,120,140,a),width=w)
img.save('out/base.jpg',quality=86,optimize=True,progressive=True)
img.resize((1024,512),Image.LANCZOS).save('preview_base.jpg',quality=85)
print('ok')
