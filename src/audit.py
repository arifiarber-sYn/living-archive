"""audit.py — the memory-audit matrix for ONE unit, built from the files and git (no model call).

  python3 src/audit.py <unit-id>            e.g. vendim-d-070, pep-0008, shenim-nebius-video-1
  ARK_ARKIVA=arkiva-peps python3 src/audit.py pep-0008

Six questions a user should be able to answer about anything the agent "remembers":
  what      — the unit text (id, title/first line)
  source    — `burimi:` front-matter (where it came from)
  when      — `data:`/`krijuar:` front-matter + first git commit that added the file
  who       — git author of that commit (human or the agent's `remember`)
  revertible— the commit sha + the exact command that removes it (`git revert`/`git rm`), never executed here
  used      — is it in the local index (so it can be retrieved) and how many chars the model would see
Prints JSON; exit 1 if the unit does not exist. Fail-closed, read-only.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

RRENJA = pathlib.Path(__file__).resolve().parent.parent
ARKIVA = pathlib.Path(os.environ.get('ARK_ARKIVA') or (RRENJA / 'arkiva-peps'))
if not ARKIVA.is_absolute():
    ARKIVA = RRENJA / ARKIVA


def _git(*args: str) -> str:
    r = subprocess.run(['git', *args], cwd=RRENJA, capture_output=True, text=True, timeout=10)
    return r.stdout.strip()


def front_matter(teksti: str) -> dict:
    if not teksti.startswith('---'):
        return {}
    pj = teksti.split('---', 2)
    if len(pj) < 3:
        return {}
    d = {}
    for rr in pj[1].splitlines():
        if ':' in rr:
            k, v = rr.split(':', 1)
            d[k.strip()] = v.strip()
    return d


def audit(ident: str) -> dict:
    p = ARKIVA / (ident + '.md')
    if not p.exists():
        return {'id': ident, 'ekziston': False}
    teksti = p.read_text(encoding='utf-8', errors='replace')
    fm = front_matter(teksti)
    trupi = teksti.split('---', 2)[-1].strip() if teksti.startswith('---') else teksti
    rel = str(p.relative_to(RRENJA))
    log = _git('log', '--diff-filter=A', '--follow', '--date=iso-strict', '--format=%h%x09%ad%x09%an%x09%s', '--', rel)
    i_pari = log.splitlines()[-1].split('\t') if log else []
    ndryshime = _git('rev-list', '--count', 'HEAD', '--', rel)
    idx_meta = ARKIVA / 'embeddings.json'
    ne_indeks = None
    if idx_meta.exists():
        ne_indeks = ident in json.loads(idx_meta.read_text(encoding='utf-8')).get('id', [])
    return {
        'id': ident, 'ekziston': True, 'skedari': rel,
        'what': {'titulli': trupi.splitlines()[0][:160] if trupi else '', 'karaktere': len(teksti)},
        'source': fm.get('burimi', '(no burimi field)'),
        'licence': fm.get('licenca'),
        'when': {'front_matter': fm.get('data') or fm.get('krijuar'), 'commit_i_pare': i_pari[1] if len(i_pari) > 1 else None},
        'who': {'autori_git': i_pari[2] if len(i_pari) > 2 else None, 'commit': i_pari[0] if i_pari else None,
                'mesazhi': i_pari[3] if len(i_pari) > 3 else None,
                'nga_agjenti': bool(i_pari) and i_pari[3].startswith('remember:') if len(i_pari) > 3 else False},
        'revertible': {'ndryshime_gjithsej': int(ndryshime or 0),
                       'komanda_revert': ('git revert ' + i_pari[0]) if i_pari else None,
                       'komanda_forget': 'git rm ' + rel + ' && git commit -m "forget: ' + ident + '"'},
        'used': {'ne_indeks_semantik': ne_indeks, 'karaktere_qe_sheh_modeli': min(1400, len(teksti))},
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    d = audit(sys.argv[1])
    print(json.dumps(d, ensure_ascii=False, indent=2))
    raise SystemExit(0 if d['ekziston'] else 1)
