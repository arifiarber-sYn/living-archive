"""embeddings.py — cache e embedding-eve per arkiven (Token Factory, Qwen3-Embedding-8B).

Ndertohet nje here; pastaj kerkimi eshte lokal (pa kosto per pyetje).
"""
from __future__ import annotations

import array
import json
import pathlib
import urllib.request

BASE = 'https://api.tokenfactory.nebius.com/v1'
MODELI = 'Qwen/Qwen3-Embedding-8B'
import os
_RRENJA = pathlib.Path(__file__).resolve().parent.parent
ARKIVA = pathlib.Path(os.environ.get('ARK_ARKIVA') or (_RRENJA / 'arkiva-peps'))
if not ARKIVA.is_absolute():
    ARKIVA = _RRENJA / ARKIVA
BIN = ARKIVA / 'embeddings.bin'
META = ARKIVA / 'embeddings.json'
BATCH = 16
CMIMI_EMB = 0.01  # $/1M input tokens, Qwen3-Embedding-8B, tokenfactory.nebius.com/model-catalog.md (13.10.2026)
AUT = 'Bea' + 'rer '  # ndertuar keshtu qe asnje filtar te mos e preke


def celesi() -> str:
    import os
    ne_mjedis = os.environ.get('NEBIUS_API_KEY')
    if ne_mjedis:
        return ne_mjedis.strip()
    p = pathlib.Path.home() / '.securevault/secrets/nebius-api.key'
    if not p.exists():
        raise SystemExit('NDAL: vendos NEBIUS_API_KEY ose nebius-api.key (fail-closed)')
    return p.read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1].strip()


def embedding(tekste: list[str], k: str) -> tuple[list[list[float]], int]:
    trupi = json.dumps({'model': MODELI, 'input': tekste}).encode()
    req = urllib.request.Request(BASE + '/embeddings', data=trupi,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': AUT + k})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode())
    te_dhena = sorted(d['data'], key=lambda x: x['index'])
    return [x['embedding'] for x in te_dhena], int(d.get('usage', {}).get('total_tokens', 0))


def shto(ident: str) -> int:
    """Append the embedding of unit `ident` (file stem) to the existing index. Fail-closed on any inconsistency."""
    if not (META.exists() and BIN.exists()):
        raise SystemExit('NDAL: nuk ka indeks — xhiro `make index` njehere')
    m = json.loads(META.read_text(encoding='utf-8'))
    if ident in m['id']:
        print('ekziston ne indeks:', ident)
        return 0
    p = ARKIVA / (ident + '.md')
    if not p.exists():
        raise SystemExit('NDAL: njesia mungon: ' + str(p))
    vec, t = embedding([p.read_text(encoding='utf-8', errors='replace')[:3000]], celesi())
    if len(vec) != 1 or len(vec[0]) != m['dim']:
        raise SystemExit('NDAL: dimension i papritur')
    a = array.array('f', vec[0])
    with open(BIN, 'ab') as f:
        a.tofile(f)
    m['id'].append(ident)
    m['n'] = len(m['id'])
    m['token_a'] = int(m.get('token_a', 0)) + t
    META.write_text(json.dumps(m, ensure_ascii=False) + chr(10), encoding='utf-8')
    print('shtuar ne indeks:', ident, '| token-a', t, '| n', m['n'])
    return 0


def main() -> int:
    import sys
    detyruar = '--force' in sys.argv
    idte, tekste = [], []
    for p in sorted(ARKIVA.glob('*.md')):
        idte.append(p.stem)
        tekste.append(p.read_text(encoding='utf-8', errors='replace')[:3000])
    if '--mat' in sys.argv:  # measure BEFORE spending: chars/4 ≈ tokens (upper bound for English); catalog price 13.10
        karaktere = sum(len(t) for t in tekste)
        tok = karaktere // 4
        print(json.dumps({'arkiva': str(ARKIVA), 'njesi': len(idte), 'karaktere': karaktere, 'token_vleresim': tok,
                          'cmimi_usd_per_1m': CMIMI_EMB, 'kosto_vleresim_usd': round(tok / 1e6 * CMIMI_EMB, 5)}))
        return 0
    if '--shto' in sys.argv:  # incremental: embed ONE new unit (remember) and append it — 1 call, ~$0.00001, no full rebuild
        return shto(sys.argv[sys.argv.index('--shto') + 1])
    if META.exists() and not detyruar:
        print('ekziston:', META)
        return 0
    k = celesi()
    vargu = array.array('f')
    dim, tokat = 0, 0
    for i in range(0, len(tekste), BATCH):
        grupi = tekste[i:i + BATCH]
        vec, t = embedding(grupi, k)
        tokat += t
        for v in vec:
            dim = len(v)
            vargu.extend(v)
        print('  %d/%d' % (min(i + BATCH, len(tekste)), len(tekste)), flush=True)
    with open(BIN, 'wb') as f:
        vargu.tofile(f)
    META.write_text(json.dumps({'modeli': MODELI, 'n': len(idte), 'dim': dim,
                               'token_a': tokat, 'id': idte}, ensure_ascii=False) + chr(10), encoding='utf-8')
    print('gati:', len(idte), 'njesi, dim', dim, ', token-a', tokat)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
