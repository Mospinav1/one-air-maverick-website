import csv,re,json,collections,sys
MINLEN=int(sys.argv[1]) if len(sys.argv)>1 else 2500
CARIB={"BS","TC","KY","JM","DO","HT","PR","VI","VG","AI","SX","MF","BL","AG","KN","GP","DM","MQ","LC","BB","VC","GD","TT","AW","CW","BQ","BM","MS"}
US={"US"}
FORCE={"VIJ"}
PAVED=re.compile(r"^(ASP|ASPH|CON|CONC|PEM|BIT|TAR|PAVED|PAV|ASFALT|ASPHALT|CONCRETE|BITUMINOUS|MAC|TARMAC|A|C|ASP-|ASPH-|CON-|PEM-)",re.I)
def paved(s):
    s=(s or "").strip().upper()
    if not s: return None
    if any(k in s for k in ("TURF","GRASS","GRAVEL","DIRT","SAND","WATER","SNOW","ICE","CORAL","CLAY","GRE","GRV","GRS","TRF","SOIL","UNPAVED","U")) and not s.startswith(("ASP","CON","PEM","BIT")): return False
    return bool(PAVED.match(s))
best=collections.defaultdict(int); unknown=collections.defaultdict(int)
for r in csv.DictReader(open("runways.csv")):
    if r["closed"]=="1": continue
    try: L=int(r["length_ft"] or 0)
    except: L=0
    p=paved(r["surface"])
    if p: best[r["airport_ref"]]=max(best[r["airport_ref"]],L)
    elif p is None: unknown[r["airport_ref"]]=max(unknown[r["airport_ref"]],L)
MIL=re.compile(r"(Naval|Air Force|\bAFB\b|Naval Air|\bNAS\b|Army Air|Army Heliport|Marine Corps|Air Reserve Base|Joint Base|Coast Guard|Air National Guard Base|Naval Outlying|\bNOLF\b|Auxiliary Field|Air Force Auxiliary|\bAAF\b|Space Force|Test Range|Proving Ground)",re.I)
out=[];stats=collections.Counter()
for a in csv.DictReader(open("airports.csv")):
    c=a["iso_country"]
    if c not in US and c not in CARIB: continue
    if a["type"] not in ("small_airport","medium_airport","large_airport"): continue
    L=best.get(a["id"],0)
    if L<MINLEN:
        # Caribbean fields sometimes lack surface data; keep them if a long runway is listed and it has a code
        ok=c in CARIB and unknown.get(a["id"],0)>=MINLEN and (a["iata_code"] or a["icao_code"])
        # Island strips a little under the limit that charter turboprops routinely use (St. Barts, Negril, Union Island)
        ok=ok or (c in CARIB and a["iata_code"] and L>=2000)
        # Known data error: Virgin Gorda's runway is paved but listed as gravel
        ok=ok or a["iata_code"] in FORCE
        if not ok: stats["short/unpaved"]+=1; continue
    # Military bases are closed to charter; joint civil fields keep a civil word in their name (e.g. "Charleston AFB/International")
    if MIL.search(a["name"]) and not (re.search(r"International|Regional|Municipal|Civil",a["name"]) or ("/" in a["name"] and "Airport" in a["name"])): stats["military"]+=1; continue
    lc=a["local_code"] or ""
    if c=="US" and not (a["iata_code"] or a["icao_code"] or re.fullmatch(r"[A-Z0-9]{3}",lc)):
        stats["private-use"]+=1; continue   # US public-use fields have 3-character FAA codes; private strips use 4
    code=a["iata_code"] or (lc if c=="US" and lc else "") or a["icao_code"] or a["gps_code"] or a["ident"]
    reg=a["iso_region"].split("-",1)[1] if c=="US" else c
    out.append([a["name"],a["municipality"],reg,code,a["icao_code"] or a["gps_code"] or "",round(float(a["latitude_deg"]),4),round(float(a["longitude_deg"]),4),{"large_airport":3,"medium_airport":2,"small_airport":1}[a["type"]],
                ",".join(k.strip() for k in (a["keywords"] or "").split(",") if k.strip() and k.strip() not in (code,a["icao_code"]))[:60]])
    stats[c if c in CARIB else "US"]+=1
print(len(out)); print(stats.most_common())
json.dump(out,open(f"airports_{MINLEN}.json","w"),separators=(",",":"))
