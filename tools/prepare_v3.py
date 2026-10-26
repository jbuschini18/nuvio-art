"""v3 layout: restore live poster-wall backdrops (heroBackdropUrl) and self-host the left-side
service/genre logos (titleLogoUrl) from John's ORIGINAL Nuvio export; point Discover at the new WebP tiles."""
import json, os, urllib.request
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "nuvio-art-v3")
ORIG = json.load(open("/workspace/nuvio/mycols.json"))
TREE = {x["path"] for x in json.load(open("/workspace/scratch/lk_tree.json"))["tree"]}
RAW = "https://raw.githubusercontent.com/luckynumb3rs/stremio-perfect-setup/main/"
JSD = "https://cdn.jsdelivr.net/gh/luckynumb3rs/stremio-perfect-setup/"
ALIAS = {"collections.genres.kids-family": "collections.genres.family",        # no original; closest upstream art
         "collections.genres.sci-fi-fantasy": "collections.genres.fantasy"}
orig = {f["id"]: f for c in ORIG for f in c["folders"]}
L = json.load(open(os.path.join(HERE, "layout_v2.json")))
report = []
def rel(u):
    for p in (JSD, RAW):
        if u.startswith(p): return u[len(p):]
for c in L:
    cid = c["id"].split(".")[-1]
    for f in c["folders"]:
        slug = f["id"].split(".")[-1]
        if cid == "discover" and f.get("focusGifUrl", "").endswith(".gif"):
            f["focusGifUrl"] = f["focusGifUrl"][:-4] + ".webp"
        src_id = f["id"] if f["id"] in orig else ALIAS.get(f["id"])
        o = orig.get(src_id) if src_id else None
        if not o and src_id:                        # alias not in his export: derive upstream path
            g, s = src_id.split(".")[1:]
            o = {"heroBackdropUrl": f"{JSD}collections/{g}/backdrop/{s}.webp", "titleLogoUrl": f"{JSD}collections/{g}/title/{s}.webp"}
        hero = logo = "-"
        if o:
            hb = rel(o.get("heroBackdropUrl") or "")
            if hb and hb in TREE: f["heroBackdropUrl"] = "lk:" + hb; hero = "live"
            elif hb: hero = "missing upstream"
            tl = rel(o.get("titleLogoUrl") or "")
            if tl and tl in TREE:
                dst = f"{cid}/title/{slug}.webp"; os.makedirs(os.path.join(ART, cid, "title"), exist_ok=True)
                req = urllib.request.Request(RAW + tl, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r: data = r.read()
                open(os.path.join(ART, dst), "wb").write(data); f["titleLogoUrl"] = "@" + dst; logo = "self-hosted"
            elif tl: logo = "missing upstream (404)"
        report.append(f"{f['id']}\tsource={src_id or '-'}{' (alias)' if f['id'] in ALIAS else ''}\theroBackdrop={hero}\ttitleLogo={logo}")
json.dump(L, open(os.path.join(HERE, "layout.json"), "w"), indent=2)
open(os.path.join(HERE, "v3_backdrop_logo_report.tsv"), "w").write("\n".join(report) + "\n")
print("\n".join(report))
