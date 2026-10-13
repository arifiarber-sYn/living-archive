#!/usr/bin/env python3
"""remember.py — veprim i auditueshëm: shton një njësi të re në arkivë + git commit.

  python3 src/remember.py --id l-99 --tekst "..." [--burimi "biseda 2026-10-13"] [--kategoria shenim] [--indeks]

Fail-closed: nëse skedari ekziston → REFUZON (exit 2). Kurrë s'fshin; vetëm shton."""
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

KETU = Path(__file__).resolve().parent.parent
import os
ARKIVA = Path(os.environ.get("ARK_ARKIVA") or (KETU / "arkiva-peps"))  # same switch as know.py/embeddings.py (public corpus: arkiva-peps)
if not ARKIVA.is_absolute():
    ARKIVA = KETU / ARKIVA

def tani() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--tekst", required=True)
    ap.add_argument("--burimi", default="agjent (remember)")
    ap.add_argument("--kategoria", default="shenim")
    ap.add_argument("--indeks", action="store_true")
    a = ap.parse_args()
    idd = a.id.strip()
    shteg = ARKIVA / (a.kategoria + "-" + idd + ".md")
    if shteg.exists():
        print(json.dumps({"ok": False, "arsyeja": "ekziston", "shteg": str(shteg)}, ensure_ascii=False)); return 2
    ARKIVA.mkdir(parents=True, exist_ok=True)
    shteg.write_text("---\nid: " + idd + "\nburimi: " + a.burimi + "\ndata: " + tani() + "\n---\n\n" + a.tekst.strip() + "\n", encoding="utf-8")
    subprocess.run(["git", "add", str(shteg)], cwd=KETU, check=True)
    c = subprocess.run(["git", "commit", "-m", "remember: " + idd, "--", str(shteg)], cwd=KETU, capture_output=True, text=True)
    if c.returncode != 0:
        print(json.dumps({"ok": False, "arsyeja": "commit_deshtoi", "detaj": (c.stderr or c.stdout)[-300:]}, ensure_ascii=False)); return 3
    log = subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=KETU, capture_output=True, text=True).stdout.strip()
    indeks = None
    if a.indeks:  # H8 (13.10): incremental — one embedding call appended to the index; `make index` said "ekziston" and did nothing
        r = subprocess.run(["python3", "src/embeddings.py", "--shto", shteg.stem], cwd=KETU, capture_output=True, text=True)
        indeks = {"ok": r.returncode == 0, "detaj": (r.stdout or r.stderr).strip()[-160:]}
    print(json.dumps({"ok": True, "shteg": str(shteg), "id": idd, "commit": log, "indeks": indeks}, ensure_ascii=False)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
