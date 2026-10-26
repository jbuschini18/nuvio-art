"""Regenerate John's Nuvio collections from layout.json.

  python3 build.py                 # tag from TAG below; writes both variants + verify list
  python3 build.py --tag v3        # after you add/replace art and push tag v3
  python3 build.py --base raw      # use raw.githubusercontent instead of jsDelivr
  python3 build.py --genre-art alt # code-generated genre cards instead of rsa16's

Asset paths in layout.json start with "@" and are relative to the nuvio-art repo root.
Same collection/folder ids every time, so re-importing replaces in place."""
import argparse, json, os, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__))
USER, REPO, TAG = "jbuschini18", "nuvio-art", "v4"
# Live poster-wall backdrops (third-party, refreshed monthly by luckynumb3rs' GitHub Action). "lk:" paths in layout.json.
LIVE = {"raw": "https://raw.githubusercontent.com/luckynumb3rs/stremio-perfect-setup/main/",
        "jsdelivr": "https://cdn.jsdelivr.net/gh/luckynumb3rs/stremio-perfect-setup/"}   # = exact URLs in his original export
CURRENT_AIOM = "/workspace/nuvio/mine.json"            # his live AIOMetadata export
PROPOSED_AIOM = os.path.join(HERE, "aiometadata", "aiometadata_us.json")
NEEDS_AIOM_CHANGE = {"collections.discover.anticipated", "collections.discover.latest"}
SHAPES = {"POSTER", "LANDSCAPE", "SQUARE", "poster", "wide", "square"}

def base_url(kind, tag):
    return (f"https://cdn.jsdelivr.net/gh/{USER}/{REPO}@{tag}/" if kind == "jsdelivr"
            else f"https://raw.githubusercontent.com/{USER}/{REPO}/{tag}/")

def build(layout, base, genre_art, with_aiom_change, live="raw"):
    cols = copy.deepcopy(layout)
    for c in cols:
        if not with_aiom_change:
            c["folders"] = [f for f in c["folders"] if f["id"] not in NEEDS_AIOM_CHANGE]
        for f in c["folders"]:
            if c["id"] == "collections.genres":
                slug = f["id"].split(".")[-1]
                f["coverImageUrl"] = {"repo": f"@genres/cover/{slug}.png", "alt": f"@genres/alt/{slug}.png", "none": ""}[genre_art]
                if genre_art == "none": f["hideTitle"] = False
            for k, v in list(f.items()):
                if isinstance(v, str) and v.startswith("@"): f[k] = base + v[1:]
                elif isinstance(v, str) and v.startswith("lk:"): f[k] = LIVE[live] + v[3:]
        for k in ("backdropImageUrl",):
            if isinstance(c.get(k), str) and c[k].startswith("@"): c[k] = base + c[k][1:]
    return cols

def nuvio_validate(cols):
    """Port of NuvioTV CollectionsDataStore.validateCollectionsJson (1.1.0-beta.8)."""
    assert isinstance(cols, list) and cols, "expected non-empty array"
    n = 0
    for c in cols:
        assert isinstance(c.get("id"), str) and c["id"].strip(), "collection id"
        assert isinstance(c.get("title"), str), c["id"]
        assert isinstance(c.get("folders"), list), c["id"]
        for f in c["folders"]:
            assert isinstance(f, dict) and isinstance(f.get("id"), str) and f["id"].strip()
            assert isinstance(f.get("title"), str), f["id"]
            src = f.get("sources") if isinstance(f.get("sources"), list) else f.get("catalogSources")
            assert isinstance(src, list), f["id"] + " sources"
            assert f.get("tileShape") is None or f["tileShape"] in SHAPES, f["id"]
            for s in src:
                p = (s.get("provider") or "addon").lower()
                if p == "addon": assert all(isinstance(s.get(k), str) for k in ("addonId", "type", "catalogId")), f["id"]
                if p == "tmdb": assert isinstance(s.get("tmdbSourceType"), str)
                if p == "trakt": assert isinstance(s.get("traktListId"), (int, float))
            n += 1
    return n

def catalog_check(cols, aiom_path):
    cats = {(c["id"], c["type"]): c for c in json.load(open(aiom_path))["config"]["catalogs"]}
    errs, ids = [], set()
    for c in cols:
        for f in c["folders"]:
            if f["id"] in ids: errs.append("duplicate folder id " + f["id"])
            ids.add(f["id"])
            for key in ("sources", "catalogSources"):
                for s in f.get(key) or []:
                    if s.get("addonId") != "aio-metadata": errs.append(f"{f['id']}: addonId {s.get('addonId')}")
                    x = cats.get((s["catalogId"], s["type"]))
                    if not x: errs.append(f"{f['id']}: missing {s['catalogId']} ({s['type']})")
                    elif not x.get("enabled"): errs.append(f"{f['id']}: disabled {s['catalogId']} ({s['type']})")
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=TAG); ap.add_argument("--base", choices=["jsdelivr", "raw"], default="jsdelivr")
    ap.add_argument("--genre-art", choices=["repo", "alt", "none"], default="repo")
    ap.add_argument("--hero-host", choices=["raw", "jsdelivr"], default="raw",
                    help="host for the live backdrops; jsdelivr = his original URLs but that repo is >50 MB and jsDelivr intermittently 403s it")
    a = ap.parse_args()
    layout = json.load(open(os.path.join(HERE, "layout.json")))
    base = base_url(a.base, a.tag)
    outs = {"nuvio-collections.json": (False, CURRENT_AIOM),
            "nuvio-collections.with-anticipated-latest.json": (True, PROPOSED_AIOM)}
    urls, ext = set(), set()
    art = os.path.join(HERE, f"nuvio-art-{a.tag}")
    if not os.path.isdir(art): sys.exit(f"missing upload folder {art}")
    for name, (aiom_change, aiom) in outs.items():
        cols = build(layout, base, a.genre_art, aiom_change, a.hero_host)
        n = nuvio_validate(json.loads(json.dumps(cols)))
        errs = catalog_check(cols, aiom)
        if errs: print(name, "ERRORS", *errs, sep="\n  "); sys.exit(1)
        for c in cols:
            for f in c["folders"]:
                for k, v in f.items():
                    if isinstance(v, str) and v.startswith(LIVE[a.hero_host]):
                        ext.add(v); continue
                    if isinstance(v, str) and v.startswith("http"):
                        urls.add(v)
                        rel = v[len(base):] if v.startswith(base) else None
                        if rel is None or not os.path.exists(os.path.join(art, rel)):
                            print("NOT IN UPLOAD FOLDER:", v); sys.exit(1)
        urls.add(base + "collections/" + name)
        txt = json.dumps(cols, ensure_ascii=False, indent=2) + "\n"
        open(os.path.join(HERE, name), "w").write(txt)
        os.makedirs(os.path.join(art, "collections"), exist_ok=True)
        open(os.path.join(art, "collections", name), "w").write(txt)  # importable From URL
        print(f"OK {name}: {len(cols)} collections, {n} folders, all catalogs exist+enabled in {os.path.basename(aiom)}")
    open(os.path.join(HERE, "urls.txt"), "w").write("\n".join(sorted(urls)) + "\n")
    open(os.path.join(HERE, "urls_live.txt"), "w").write("\n".join(sorted(ext)) + "\n")
    print(f"{len(urls)} self-hosted URLs -> urls.txt (base {base}); {len(ext)} live backdrop URLs -> urls_live.txt")

if __name__ == "__main__":
    main()
