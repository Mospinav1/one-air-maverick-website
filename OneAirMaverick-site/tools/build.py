import json,math,os
S=1000.0
def X(lon): return (lon+180)/360*S
def Y(lat):
    lat=max(min(lat,85),-85); r=math.radians(lat)
    return (1-math.log(math.tan(math.pi/4+r/2))/math.pi)/2*S
def ring(coords,close=True):
    pts=[]; last=None
    for lon,lat in coords:
        p=(round(X(lon),2),round(Y(lat),2))
        if p!=last: pts.append(p); last=p
    if len(pts)<2: return ""
    d="M"+" ".join(f"{x:g} {y:g}" for x,y in pts[:1])+"L"+" ".join(f"{x:g} {y:g}" for x,y in pts[1:])
    return d+("Z" if close else "")
def geom_path(g,close=True):
    if not g: return ""
    t=g["type"]; c=g["coordinates"]
    if t=="Polygon": return "".join(ring(r) for r in c)
    if t=="MultiPolygon": return "".join(ring(r) for p in c for r in p)
    if t=="LineString": return ring(c,False)
    if t=="MultiLineString": return "".join(ring(l,False) for l in c)
    return ""
C=json.load(open("countries.geojson"))
countries=[]; labels=[]
for f in C["features"]:
    p=f["properties"]; d=geom_path(f["geometry"])
    if d: countries.append([p["ADM0_A3"],d])
    if p.get("LABEL_X") is not None:
        labels.append([p["NAME"],round(X(p["LABEL_X"]),2),round(Y(p["LABEL_Y"]),2),p.get("MIN_LABEL") or 5])
states="".join(geom_path(f["geometry"]) for f in json.load(open("states.geojson"))["features"])
lakes="".join(geom_path(f["geometry"]) for f in json.load(open("lakes.geojson"))["features"])
KEEP={"USA","CAN","MEX","CUB","BHS","TCA","CYM","JAM","HTI","DOM","PRI","VIR","VGB","AIA","SXM","MAF","BLM","ATG","KNA","GLP","DMA","MTQ","LCA","BRB","VCT","GRD","TTO","ABW","CUW","BES","BMU","MSR","BLZ","GTM","HND","NIC","CRI","PAN","COL","VEN","SLV"}
CARIB=KEEP-{"USA","CAN","MEX","BLZ","GTM","HND","NIC","CRI","PAN","COL","VEN","SLV"}
cities=[]
for f in json.load(open("ne_10m_populated_places_simple.geojson"))["features"]:
    p=f["properties"]; a=p["adm0_a3"]
    if a not in KEEP: continue
    lon,lat=p["longitude"],p["latitude"]
    if not (-180<=lon<=-50 and 5<=lat<=72): continue
    pop=p["pop_max"] or 0
    if a in ("USA",):
        if pop<60000 and p["scalerank"]>7: continue
    elif a in CARIB:
        if pop<8000 and not p["adm0cap"]: continue
    else:
        if pop<750000 and not p["adm0cap"]: continue
    # rank: lower = more important
    rank=p["scalerank"]
    cities.append([p["name"],p["adm1name"] if a=="USA" else p["adm0name"],a,round(X(lon),2),round(Y(lat),2),round(lat,4),round(lon,4),rank,int(pop)])
cities.sort(key=lambda c:(c[7],-c[8]))
data={"countries":countries,"countryLabels":labels,"states":states,"lakes":lakes,"cities":cities}
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","public","assets","data")
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"map-data.js"),"w").write(
 "/* One Air Maverick map data. Shapes and cities: Natural Earth (public domain). Pre-projected to Web Mercator, 0-1000 units. */\nwindow.OAM_MAP="+json.dumps(data,separators=(",",":"),ensure_ascii=False)+";\n")
A=json.load(open("airports_2500.json"))
A.sort(key=lambda a:(-a[7],a[0]))
open(os.path.join(OUT,"airports.js"),"w").write(
 "/* Public-use airports in the U.S. and the Caribbean with a paved runway of at least 2,500 ft (plus a few island strips charter aircraft use).\n   Source: OurAirports (public domain). Fields: name, city, state or country, code, ICAO, lat, lon, size (3 large, 2 medium, 1 small), search keywords. */\nwindow.OAM_AIRPORTS="+json.dumps(A,separators=(",",":"),ensure_ascii=False)+";\n")
print(len(countries),len(labels),len(cities),len(A))
