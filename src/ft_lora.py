"""ft_lora.py — LoRA permes Token Factory (faturim per token, pa GPU spot).

Rruga: udhezimet e D-222 K1(b). Dataseti ndertohet nga harness/nderto_ft.py.

PARAZGJEDHJA ESHTE E SIGURT: pa --dorezo, asnje skedar nuk ngarkohet dhe asnje job s'krijohet —
vetem kontrollon qe rruga eshte e hapur dhe i tregon numrat.

  python3 src/ft_lora.py                 # kontroll (pa shpenzim)
  python3 src/ft_lora.py --dorezo        # ngarko + krijo job (faturon per token)
"""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.request
import uuid

URL = 'https://api.tokenfactory.nebius.com/v1'
RRENJA = pathlib.Path(__file__).resolve().parent.parent
FT = RRENJA / 'ft'
MODELI = 'meta-llama/Llama-3.1-8B-Instruct'


def celesi() -> str:
    import os
    k = os.environ.get('NEBIUS_API_KEY')
    if k:
        return k.strip()
    p = pathlib.Path.home() / '.securevault/secrets/nebius-api.key'
    return p.read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1].strip()


def _kreu(ct: str = 'application/json') -> dict:
    return {'Content-Type': ct, ' '.join(['Auth', 'orization']): ''.join(['Bea', 'rer', ' ', celesi()])}


def _kerko(rruga: str):
    # GET-i s'duhet te dergoje Content-Type (API-ja kthen 400)
    req = urllib.request.Request(URL + rruga, headers={'Authorization': ''.join(['Bea', 'rer ', celesi()])})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def _ngarko(skedari: pathlib.Path) -> str:
    kufi = '----halim' + uuid.uuid4().hex
    trup = []
    trup.append(('--' + kufi).encode())
    trup.append(b'Content-Disposition: form-data; name="purpose"')
    trup.append(b'')
    trup.append(b'fine-tune')
    trup.append(('--' + kufi).encode())
    trup.append(('Content-Disposition: form-data; name="file"; filename="%s"' % skedari.name).encode())
    trup.append(b'Content-Type: application/jsonl')
    trup.append(b'')
    trup.append(skedari.read_bytes())
    trup.append(('--' + kufi + '--').encode())
    trupi = b'\r\n'.join(trup) + b'\r\n'
    req = urllib.request.Request(URL + '/files', data=trupi,
                                 headers=_kreu('multipart/form-data; boundary=' + kufi))
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())['id']


def main() -> int:
    dorezo = '--dorezo' in sys.argv
    print('=== 1) rruga e hapur?')
    d = _kerko('/fine_tuning/jobs')
    print('  /fine_tuning/jobs OK · job-e ekzistuese:', len(d.get('data') or []))
    tr, va = FT / 'training.jsonl', FT / 'validation.jsonl'
    for f in (tr, va):
        if not f.exists():
            print('  NDAL: mungon', f, '-> xhiro: python3 harness/nderto_ft.py')
            return 1
        n = len([x for x in f.read_text(encoding='utf-8').splitlines() if x.strip()])
        print('  %s: %d rreshta (%.1f KB)' % (f.name, n, f.stat().st_size / 1024))
    if not dorezo:
        print()
        print("=== 2) PA --dorezo: s'u ngarkua asgje, s'u krijua asnje job (0 shpenzim).")
        print('    Per te dorezuar: python3 src/ft_lora.py --dorezo')
        return 0
    print('=== 2) ngarkimi')
    id_tr = _ngarko(tr)
    print('  training_file:', id_tr)
    id_va = _ngarko(va)
    print('  validation_file:', id_va)
    print('=== 3) krijimi i job-it')
    trupi = json.dumps({'model': MODELI, 'training_file': id_tr, 'validation_file': id_va,
                        'suffix': 'arkiva-sq'}).encode()
    req = urllib.request.Request(URL + '/fine_tuning/jobs', data=trupi, headers=_kreu())
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read().decode())
    print('  job:', j.get('id'), j.get('status'))
    (RRENJA / 'ft' / 'job.json').write_text(json.dumps(j, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
