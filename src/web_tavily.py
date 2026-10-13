#!/usr/bin/env python3
"""web_tavily.py — kerko web via Tavily PAS portes se privatesise (D-196).
Pa --lejo => REFUZON (pyetja s'del jashte). Celesi: TAVILY_API_KEY ose ~/.securevault/secrets/tavily-api.key."""
import argparse, json, os, pathlib, urllib.request

def key():
    k = os.environ.get("TAVILY_API_KEY")
    if k: return k.strip()
    p = pathlib.Path.home()/".securevault/secrets/tavily-api.key"
    return p.read_text().strip() if p.exists() else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pyetja", required=True)
    ap.add_argument("--lejo", action="store_true")
    ap.add_argument("--max", type=int, default=3)
    a = ap.parse_args()
    if not a.lejo:
        print(json.dumps({"ok": False, "arsyeja": "porta e privatesise: pa --lejo pyetja NUK del jashte"}, ensure_ascii=False)); return 2
    k = key()
    if not k:
        print(json.dumps({"ok": False, "arsyeja": "pa_celes"})); return 3
    req = urllib.request.Request("https://api.tavily.com/search",
        data=json.dumps({"query": a.pyetja, "max_results": a.max}).encode(),
        headers={"Authorization": "Bearer "+k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.load(r)
    res = [{"url": x.get("url"), "title": x.get("title")} for x in d.get("results", [])]
    print(json.dumps({"ok": True, "pyetja": a.pyetja, "rezultate": res}, ensure_ascii=False)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
