#!/usr/bin/env python3
"""Laku agjentik i gelltitjes: vezhgo -> vendos -> indekso -> raporto.
Cdo hap shkruhet ne gjendje te perbashket, qe UI ta shohe LIVE."""
import json, pathlib, threading, time
import arkivi

GJ = {"aktiv": False, "mbaroi": False, "rreshta": [], "filloi": "", "mbaroi_koha": "", "permbledhje": {}}
LOCK = threading.Lock()


def _shto(r):
    with LOCK:
        GJ["rreshta"].append(r)


def _vendos(p, text):
    """Vendimi i agjentit per nje dokument - i shprehur me nje fjali."""
    if p.suffix.lower() == ".pdf":
        if len(text.strip()) < 40:
            return "PDF pa tekst te nxjerreshem (i skanuar?) -> s'e indeksoj"
        return "PDF i lexueshem -> nxjerre tekstin me pdftotext dhe indekso"
    if len(text.strip()) < 40:
        return "skedar tekstual pothuajse bosh -> s'e indeksoj"
    return "skedar tekstual -> copto dhe indekso"


def gelltit_lak():
    with LOCK:
        GJ["aktiv"] = True
        GJ["mbaroi"] = False
        GJ["rreshta"] = []
        GJ["filloi"] = arkivi.ts()
    t0 = time.time()
    skedaret = [p for p in sorted(arkivi.KORPUS.rglob("*")) if p.is_file()]
    baza, raport = [], []
    for n, p in enumerate(skedaret, 1):
        t_dok = time.time()
        faza = "vezhgoj"
        try:
            text = arkivi.teksti_i_skedarit(p)
            faza = "vendos"
            vendimi = _vendos(p, text)
            c = arkivi.copto(text)
            did = "d" + str(n)
            faza = "indeksoj"
            for k, ch in enumerate(c):
                try:
                    v = arkivi.embed(ch)
                except Exception:
                    v = []
                baza.append({"id": did + "-" + str(k), "dok": did, "file": str(p.relative_to(arkivi.KORPUS)),
                             "tekst": ch, "vec": v})
            kuptova = "po" if len(text.strip()) > 40 else "JO"
            raport.append({"dok": did, "file": str(p.relative_to(arkivi.KORPUS)), "shkronja": len(text),
                           "copa": len(c), "kuptova": kuptova})
            faza = "raportoj"
            _shto({"dok": did, "file": str(p.relative_to(arkivi.KORPUS)), "vendimi": vendimi,
                   "shkronja": len(text), "copa": len(c), "kuptova": kuptova,
                   "sekonda": round(time.time() - t_dok, 2), "gabim": ""})
        except Exception as e:
            _shto({"dok": "d" + str(n), "file": str(p.relative_to(arkivi.KORPUS)), "vendimi": "gabim ne fazen: " + faza,
                   "shkronja": 0, "copa": 0, "kuptova": "?", "sekonda": round(time.time() - t_dok, 2),
                   "gabim": type(e).__name__ + ": " + str(e)[:120]})
    arkivi.INDEKS.parent.mkdir(parents=True, exist_ok=True)
    arkivi.INDEKS.write_text(json.dumps({"krijuar": arkivi.ts(), "copa": baza, "raport": raport}, ensure_ascii=False), encoding="utf-8")
    with LOCK:
        GJ["aktiv"] = False
        GJ["mbaroi"] = True
        GJ["mbaroi_koha"] = arkivi.ts()
        GJ["permbledhje"] = {"dokumente": len(skedaret), "copa": len(baza),
                             "kuptova_jo": sum(1 for r in raport if r["kuptova"] != "po"),
                             "sekonda": round(time.time() - t0, 2)}
