#!/usr/bin/env python3
"""Harness i vete-vleresimit: agjenti i nderton VETe pyetjet nga korpusi.
Mat: saktesine e citimeve, normen e "S E DI" te gabuar, dhe trillimin."""
import json, pathlib, random, re, time
import arkivi

DEL = arkivi.BASE / "indeksi" / "harness.json"
TIPI_PA_BAZE = [
    "Sa eshte temperatura mesatare ne Mars?",
    "Kush ishte presidenti i Shqiperise ne 1930?",
    "Sa kushton nje bilete treni Tirane-Berlin?",
    "Sa banore ka qyteti i Tokios?",
    "Cili eshte numri atomik i uraniumit?",
]


def _numra(t):
    return re.findall(r"\d[\d.,]{2,}", t)


def _pyetje_nga_llm(c):
    p = ("/no_think" + chr(10) + "Nga fragmenti me poshte, shkruaj NJE pyetje te cilen fragmenti e pergjigjet,"
         + chr(10) + "dhe pergjigjja e sakte ne pak fjale. Formati:" + chr(10)
         + "PYETJA: <pyetja>" + chr(10) + "PERGJIGJA: <pergjigjja e shkurter>" + chr(10) + chr(10)
         + "FRAGMENTI:" + chr(10) + c["tekst"][:800])
    try:
        r = arkivi.gen(p, 120)
    except Exception:
        return None
    q, a = "", ""
    for ln in r.splitlines():
        s = ln.strip()
        if s.upper().startswith("PYETJA:") and not q:
            q = s.split(":", 1)[1].strip()
        elif s.upper().startswith("PERGJIGJA:") and not a:
            a = s.split(":", 1)[1].strip()
    if len(q) > 12 and len(a) > 0:
        return q, a
    return None


def nderto(sa=15):
    inx = arkivi.lexo_inde()
    copat = [c for c in inx["copa"] if len(c.get("tekst", "")) > 120]
    random.seed(11)
    random.shuffle(copat)
    pyetje = []
    for c in copat:
        if len(pyetje) >= sa:
            break
        g = _pyetje_nga_llm(c)
        if g:
            pyetje.append({"pyetja": g[0], "pritet": g[1], "copa": c["id"], "tipi": "bazesueshme"})
        else:
            n = _numra(c["tekst"])
            if n:
                pyetje.append({"pyetja": "Cfare vlere permend dokumenti " + c["file"] + "?",
                               "pritet": n[0], "copa": c["id"], "tipi": "bazesueshme"})
    for q in TIPI_PA_BAZE:
        pyetje.append({"pyetja": q, "pritet": "", "copa": "", "tipi": "pa_baze"})
    return pyetje


def _pastro(t):
    return re.sub(r"[^0-9a-zA-Z]", "", str(t)).lower()


def xhiro(sa=15):
    pyetjet = nderto(sa)
    rreshta = []
    t0 = time.time()
    for p in pyetjet:
        t = time.time()
        try:
            r = arkivi.pergjigju(p["pyetja"])
        except Exception as e:
            r = {"pergjigja": "GABIM " + type(e).__name__, "citime": [], "siguria": 0}
        ans = str(r.get("pergjigja", ""))
        sd = ans.strip().upper().startswith("S E DI")
        if p["tipi"] == "bazesueshme":
            cit_ok = p["copa"] in (r.get("citime") or [])
            terma = [x for x in re.findall(r"\d[\d.,]{1,}", str(p["pritet"]))]
            if terma:
                ans_ok = all(_pastro(t) in _pastro(ans) for t in terma)
            else:
                fjalet = [w for w in _pastro(p["pritet"]).split() if len(w) > 5]
                ans_ok = bool(fjalet) and all(w in _pastro(ans) for w in fjalet)
            rreshta.append({"pyetja": p["pyetja"], "pritet": p["pritet"], "tipi": "bazesueshme",
                            "pergjigja": ans[:200], "citime": r.get("citime"), "sakte": bool(ans_ok or cit_ok) and not sd,
                            "sd_gabim": bool(sd), "sekonda": round(time.time() - t, 1)})
        else:
            rreshta.append({"pyetja": p["pyetja"], "pritet": "(pa baze)", "tipi": "pa_baze",
                            "pergjigja": ans[:200], "citime": r.get("citime"), "sakte": bool(sd),
                            "trillim": (not sd), "sekonda": round(time.time() - t, 1)})
    b = [x for x in rreshta if x["tipi"] == "bazesueshme"]
    pb = [x for x in rreshta if x["tipi"] == "pa_baze"]
    m = {
        "bazesueshme": len(b),
        "sakte": sum(1 for x in b if x["sakte"]),
        "sakte_pct": round(100.0 * sum(1 for x in b if x["sakte"]) / len(b), 1) if b else 0.0,
        "sd_gabim": sum(1 for x in b if x.get("sd_gabim")),
        "sd_gabim_pct": round(100.0 * sum(1 for x in b if x.get("sd_gabim")) / len(b), 1) if b else 0.0,
        "pa_baze": len(pb),
        "pa_baze_sakte": sum(1 for x in pb if x["sakte"]),
        "trillime": sum(1 for x in pb if x.get("trillim")),
        "trillim_pct": round(100.0 * sum(1 for x in pb if x.get("trillim")) / len(pb), 1) if pb else 0.0,
        "sekonda": round(time.time() - t0, 1),
        "koha": arkivi.ts(),
    }
    DEL.parent.mkdir(parents=True, exist_ok=True)
    DEL.write_text(json.dumps({"metrika": m, "rreshta": rreshta}, ensure_ascii=False, indent=1), encoding="utf-8")
    return m


if __name__ == "__main__":
    print(json.dumps(xhiro(), ensure_ascii=False))
