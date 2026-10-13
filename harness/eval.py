"""eval.py — matja mbi arkiven e gjalle (kriteri 3 i jurise: prova nga demoja).

Metrika: citim-i sakte (id i pritur), refuzim i sakte, latence, kosto. Shkruan harness/report.json.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src.know import MODEL, Arkiva, pergjigju  # noqa: E402

HARNESS = pathlib.Path(__file__).resolve().parent


def main() -> int:
    import os
    pyetjet_sk = HARNESS / os.environ.get('ARK_PYETJE', 'pyetjet.json')
    raport_sk = HARNESS / os.environ.get('ARK_RAPORT', 'report.json')
    pyetjet = json.loads(pyetjet_sk.read_text(encoding='utf-8'))['pyetjet']
    ark = Arkiva()
    rreshtat, koh = [], []
    kosto, cit_sakte, ref_sakte, ref_total = 0.0, 0, 0, 0
    for p in pyetjet:
        try:
            r = pergjigju(ark, p['pyetja'])
        except Exception as e:  # noqa: BLE001
            r = {'pergjigja': '', 'citime': [], 'refuzim': False, 'sekonda': 0.0, 'hyr': 0, 'dal': 0,
                 'kosto_usd': 0.0, 'gjetjet': [], 'gabim': str(e)[:120]}
        koh.append(r['sekonda'])
        kosto += r['kosto_usd']
        if r.get('gabim'):
            # a failed call is never a correct answer (13.10: an exception row used to count as OK — fail-open)
            ok = False
            if p.get('refuzim'):
                ref_total += 1
        elif p.get('refuzim'):
            ref_total += 1
            ok = bool(r['refuzim'])
            ref_sakte += 1 if ok else 0
        else:
            if p.get('pret'):
                ok = bool(set(p['pret']) & set(r['citime']))
            else:  # no expected id: a real, non-refused answer WITH at least one citation
                ok = (not r['refuzim']) and bool(r['pergjigja'].strip()) and bool(r['citime'])
            cit_sakte += 1 if ok else 0
        rangu = None  # evidence funnel: where did retrieval put the expected unit? (1 = top)
        if p.get('pret'):
            for i, g in enumerate(r['gjetjet'], 1):
                if any(g == e or g.endswith('-' + e) for e in p['pret']):
                    rangu = i
                    break
        rreshtat.append({'id': p['id'], 'pyetja': p['pyetja'], 'ok': ok, 'gabim': r.get('gabim'), 'rangu': rangu,
                         'citime': r['citime'], 'pret': p.get('pret'), 'refuzim': r['refuzim'],
                         'sekonda': r['sekonda'], 'kosto_usd': r['kosto_usd'],
                         'pergjigja': r['pergjigja'][:300], 'gjetjet': r['gjetjet']})
        print(('OK ' if ok else 'XX ') + p['id'] + '  ' + str(r['citime']) + '  ' + str(r['sekonda']) + 's')
    sakte = sum(1 for x in rreshtat if x['ok'])
    me_pret = [x for x in rreshtat if x['pret']]
    fjale_korpus = sum(len(n['teksti'].split()) for n in ark.njesi)
    fjale_kontekst = 6 * 1400 // 6  # ~1400 chars per retrieved unit → words (≈ chars/6)
    funnel = {'me_id_te_pritur': len(me_pret),
              'top1': sum(1 for x in me_pret if x['rangu'] == 1),
              'top3': sum(1 for x in me_pret if x['rangu'] and x['rangu'] <= 3),
              'gjetur': sum(1 for x in me_pret if x['rangu']),
              'fjale_korpus': fjale_korpus,
              'fjale_te_lexuara_nga_modeli_maks': fjale_kontekst * 6,
              'pjesa_e_korpusit_qe_sheh_modeli_pct': round(100 * fjale_kontekst * 6 / max(1, fjale_korpus), 2)}
    raport = {'shkalla': time.strftime('%Y-%m-%d'), 'modeli': MODEL, 'njesi_arkive': ark.N, 'pyetje': len(rreshtat),
              'sakte': sakte, 'sakte_pct': round(100 * sakte / max(1, len(rreshtat)), 1),
              'citim_sakte': cit_sakte, 'refuzime_sakte': ref_sakte, 'refuzime_totale': ref_total,
              'latence_p50_s': round(statistics.median(koh), 3) if koh else 0,
              'kosto_totale_usd': round(kosto, 8),
              'kosto_mesatare_usd': round(kosto / max(1, len(rreshtat)), 8), 'funnel': funnel, 'rreshtat': rreshtat}
    raport['arkiva'] = str(ark.N) + ' units from ' + pathlib.Path(__import__('src.know', fromlist=['ARKIVA']).ARKIVA).name
    raport_sk.write_text(json.dumps(raport, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({k: v for k, v in raport.items() if k != 'rreshtat'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
