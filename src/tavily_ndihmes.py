"""tavily_ndihmes.py — skica e «know layer» per Token Factory (çmimi Best Use of Tavily $3k).

Përdorimi: TAVILY_API_KEY nga thesari; pa çelës → kthen [] (fail-closed, pa rrjeta).
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.request


def _celesi() -> str | None:
    p = pathlib.Path.home() / '.securevault/secrets/tavily-api.key'
    if p.exists():
        return p.read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1].strip()
    return os.environ.get('TAVILY_API_KEY')


def kerko(pyetja: str, max_rezultate: int = 3) -> list[dict]:
    """Kerkim Tavily; kthen [{title,url,content,score}]. 0 kosto pa celes."""
    k = _celesi()
    if not k:
        return []
    trupi = json.dumps({'query': pyetja, 'max_results': max_rezultate}).encode()
    req = urllib.request.Request('https://api.tavily.com/search', data=trupi,
                                 headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    return d.get('results', [])


if __name__ == '__main__':
    import sys
    for x in kerko(' '.join(sys.argv[1:]) or 'Nebius Token Factory'):
        print('-', x.get('title'), '->', x.get('url'))
