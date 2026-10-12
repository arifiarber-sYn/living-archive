#!/usr/bin/env python3
"""Harness i motorit REJA — mat, nuk hamend.

Pyetje te bazuara ne korpusin e repo-s (pergjigjet dihen) + pyetje pa baze.
Metrika: pergjigje me CITIM te verifikueshem, refuzime te sakta, kosto, kohe.
Shkruan: indeksi/harness-reja.json
"""
import json, pathlib, statistics, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reja  # noqa: E402

DALJA = pathlib.Path(__file__).resolve().parent.parent / 'indeksi' / 'harness-reja.json'

# 'duhet' = fjale qe pergjigja e sakte duhet t'i permbaje (nga korpusi, jo hamendje)
PYETJET = [
    {'id': 'b1', 'pyetja': 'Sa eshte buxheti total i miratuar per vitin 2027?', 'duhet': ['142']},
    {'id': 'b2', 'pyetja': 'Sa euro ndahen per arsim parauniversitar?', 'duhet': ['18.3', '18,3']},
    {'id': 'b3', 'pyetja': 'Kur fillon procedura e prokurimit per punimet rrugore?', 'duhet': ['2027']},
    {'id': 'b4', 'pyetja': 'Sa zgjat procedura e prokurimit per punimet rrugore?', 'duhet': ['90']},
    {'id': 'b5', 'pyetja': 'Kush e miratoi buxhetin dhe me cilin numer vendimi?', 'duhet': ['118']},
    {'id': 'j1', 'pyetja': 'Kush fitoi Kupen e Botes 2010?', 'refuzim': True},
    {'id': 'j2', 'pyetja': 'Sa kushton bileta e trenit ne Japoni?', 'refuzim': True},
    {'id': 'j3', 'pyetja': 'Kush e shkroi romanin Lumi i vdekur?', 'refuzim': True},
]


def main() -> int:
    rreshtat, kohet, kosto = [], [], 0.0
    sakte = 0
    for p in PYETJET:
        try:
            r = reja.pergjigju(p['pyetja'])
        except Exception as e:  # noqa: BLE001
            r = {'pergjigja': '', 'citime': [], 'refuzim': False, 'sekonda': 0.0, 'kosto_usd': 0.0, 'gabim': str(e)[:120]}
        kohet.append(r.get('sekonda', 0.0))
        kosto += r.get('kosto_usd', 0.0)
        if p.get('refuzim'):
            ok = bool(r.get('refuzim'))
            arsyeja = 'refuzoi' if ok else 'U PERGJIGJ pa baze'
        else:
            teksti = r.get('pergjigja', '').lower()
            ka_citim = bool(r.get('citime'))
            ka_fakte = any(d.lower() in teksti or d.lower().replace(',', '.') in teksti.replace(',', '.') for d in p['duhet'])
            ok = ka_citim and ka_fakte
            arsyeja = ('ok' if ok else ('pa citim' if not ka_citim else 'pa shifer/fakt'))
        sakte += 1 if ok else 0
        rreshtat.append({'id': p['id'], 'pyetja': p['pyetja'], 'ok': ok, 'arsyeja': arsyeja,
                         'citime': r.get('citime', []), 'kosto_usd': r.get('kosto_usd', 0.0),
                         'sekonda': r.get('sekonda', 0.0), 'pergjigja': (r.get('pergjigja') or '')[:300]})
        print(('OK ' if ok else 'XX ') + p['id'] + '  ' + arsyeja)
    n = len(rreshtat)
    dalja = {'koha': reja.ts(), 'motor': 'reja', 'modeli': reja.LLM, 'emb': reja.EMB,
             'pyetje': n, 'sakte': sakte, 'sakte_pct': round(100 * sakte / n, 1),
             'latence_p50_s': round(statistics.median(kohet), 3) if kohet else 0,
             'kosto_totale_usd': round(kosto, 8), 'kosto_mesatare_usd': round(kosto / n, 8),
             'rreshtat': rreshtat}
    DALJA.parent.mkdir(parents=True, exist_ok=True)
    DALJA.write_text(json.dumps(dalja, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({k: v for k, v in dalja.items() if k != 'rreshtat'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
