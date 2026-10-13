"""matje.py — korniza e matjeve per garane Nebius (kriteri 2 i jurise: numra te matur).

Mat: latence (p50/p95), token-a hyrese/dalese, kosto per thirrje. Shkruan matje/<etiketa>.json.
Çelesi lexohet NGA SKEDARI (kurre ne argv/log). Pa celes -> ndalon (fail-closed).
"""
from __future__ import annotations

import json
import pathlib
import statistics
import time
import urllib.request

BASE = 'https://api.tokenfactory.nebius.com/v1'
MODEL = 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B'
# çmimet per 1M token (USD) — Token Factory, NVIDIA Nemotron Nano; perditeso nese ndryshon
CMIM_HYR = 0.06
CMIM_DAL = 0.24


def celesi() -> str:
    p = pathlib.Path.home() / '.securevault/secrets/nebius-api.key'
    if not p.exists():
        raise SystemExit('NDAL: mungon nebius-api.key (fail-closed)')
    return p.read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1].strip()


def nje_thirrje(k: str, pyetja: str, max_tokens: int = 120) -> dict:
    trupi = json.dumps({'model': MODEL, 'messages': [{'role': 'user', 'content': pyetja}],
                        'temperature': 0.0, 'max_tokens': max_tokens}).encode()
    req = urllib.request.Request(BASE + '/chat/completions', data=trupi,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + k})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode())
    dt = time.perf_counter() - t0
    u = d.get('usage', {})
    hyr, dal = int(u.get('prompt_tokens', 0)), int(u.get('completion_tokens', 0))
    kosto = hyr / 1e6 * CMIM_HYR + dal / 1e6 * CMIM_DAL
    return {'sekonda': round(dt, 3), 'hyr': hyr, 'dal': dal, 'kosto_usd': round(kosto, 8),
            'permbajtja': str(((d.get('choices') or [{}])[0].get('message') or {}).get('content') or '')[:120]}


def main() -> int:
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    etiketa = sys.argv[2] if len(sys.argv) > 2 else 'dita1'
    k = celesi()
    rezultatet = []
    for i in range(n):
        try:
            rezultatet.append(nje_thirrje(k, 'Answer in one short sentence: what is 7*8? (run %d)' % i))
        except Exception as e:  # noqa: BLE001
            print('GABIM ne thirrjen %d: %s' % (i, str(e)[:120]))
    if not rezultatet:
        print('asnje thirrje e suksesshme')
        return 1
    lat = [r['sekonda'] for r in rezultatet]
    kosto = sum(r['kosto_usd'] for r in rezultatet)
    raport = {'modeli': MODEL, 'n': len(rezultatet), 'latence_p50_s': round(statistics.median(lat), 3),
              'latence_p95_s': round(sorted(lat)[max(0, int(len(lat) * 0.95) - 1)], 3),
              'kosto_totale_usd': round(kosto, 8), 'kosto_mesatare_per_thirrje_usd': round(kosto / len(rezultatet), 8),
              'token_hyr_total': sum(r['hyr'] for r in rezultatet),
              'token_dal_total': sum(r['dal'] for r in rezultatet), 'thirrjet': rezultatet}
    outd = pathlib.Path(__file__).resolve().parent.parent / 'matje'
    outd.mkdir(exist_ok=True)
    (outd / (etiketa + '.json')).write_text(json.dumps(raport, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({x: raport[x] for x in raport if x != 'thirrjet'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
