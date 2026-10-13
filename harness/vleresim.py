"""vleresim.py — zbaton rishikimin njerezor mbi nje raport ekzistues (pa kosto, pa ri-xhirim).

Kthen dy pikepamje: SAKTE_PYETJE (si me pare) dhe SAKTE_PERMBAJTJE (citimi nuk eshte kusht).
"""
from __future__ import annotations

import json
import pathlib

HARNESS = pathlib.Path(__file__).resolve().parent


def main() -> int:
    import sys
    burimi = HARNESS / (sys.argv[1] if len(sys.argv) > 1 else 'report-v3-semantik.json')
    raport = json.loads(burimi.read_text(encoding='utf-8'))
    rishikimi = {x['id']: x for x in json.loads((HARNESS / 'vleresim-njerezor.json').read_text(encoding='utf-8'))['rastet']}
    per, cek, te_dykuptueshme = 0, 0, 0
    for r in raport['rreshtat']:
        v = rishikimi.get(r['id'], {})
        r['permbajtja_ok'] = bool(r['ok'] or v.get('permbajtja_ok'))
        r['citimi_ok'] = bool(r['ok'] and r['citime'])
        if v.get('pyetja_e_dykuptueshme'):
            te_dykuptueshme += 1
        per += 1 if r['permbajtja_ok'] else 0
        cek += 1 if r['citimi_ok'] else 0
    n = len(raport['rreshtat'])
    dalja = {'burimi': burimi.name, 'pyetje': n,
             'sakte_pyetje': raport['sakte'], 'sakte_pyetje_pct': raport['sakte_pct'],
             'sakte_permbajtje': per, 'sakte_permbajtje_pct': round(100 * per / n, 1),
             'citime_te_sakta': cek, 'citime_pct': round(100 * cek / n, 1),
             'pyetje_te_dykuptueshme': te_dykuptueshme, 'rreshtat': raport['rreshtat']}
    (HARNESS / 'report-v5-vleresuar.json').write_text(json.dumps(dalja, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({k: v for k, v in dalja.items() if k != 'rreshtat'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
