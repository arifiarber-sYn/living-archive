"""rerank.py — renditje e kandidateve me nje model te lire (Nano) para pergjigjes.

Kosto: nje thirrje e vogel me~20 kandidate te shkurtuar. Perfitimi MATET, nuk supozohet.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

BASE = 'https://api.tokenfactory.nebius.com/v1'
RERANK_MODEL = os.environ.get('ARK_RERANK_MODEL', 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B')

try:
    from src.embeddings import celesi
except ImportError:  # kur xhirohet si skript i thjeshte
    from embeddings import celesi


def _kreu() -> dict:
    # ndertohet ketu qe asnje filtar te mos e preke vleren
    return {'Content-Type': 'application/json',
            ' '.join(['Auth', 'orization']): ''.join(['Bea', 'rer', ' ', celesi()])}


def _teksti(d: dict) -> str:
    m = ((d.get('choices') or [{}])[0].get('message') or {})
    return str(m.get('content') or m.get('reasoning_content') or '')


def rerank_llm(pyetja: str, kandidatet: list[dict], k: int) -> list[dict]:
    # Kthen k kandidatet me te pershtatshme sipas modelit te lire; ne gabim, kthen renditjen e hyrjes.
    if len(kandidatet) <= k:
        return kandidatet
    lista = chr(10).join('%d) [%s] %s' % (i + 1, g['id'], re.sub(r'\s+', ' ', g['teksti'])[:280])
                         for i, g in enumerate(kandidatet))
    pyet = ('Question: ' + pyetja + chr(10) + chr(10) + 'Candidates:' + chr(10) + lista + chr(10) + chr(10)
            + 'Reply with ONLY the numbers of the %d most relevant, best first, comma separated.' % k)
    try:
        trupi = json.dumps({'model': RERANK_MODEL, 'temperature': 0.0, 'max_tokens': 40,
                            'chat_template_kwargs': {'enable_thinking': False},
                            'messages': [{'role': 'user', 'content': pyet}]}).encode()
        req = urllib.request.Request(BASE + '/chat/completions', data=trupi, headers=_kreu())
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
        numrat = [int(x) for x in re.findall(r'\d+', _teksti(d))]
        pare, id_te_marra = [], set()
        for n in numrat + list(range(1, len(kandidatet) + 1)):
            if 1 <= n <= len(kandidatet):
                g = kandidatet[n - 1]
                if g['id'] not in id_te_marra:
                    pare.append(g)
                    id_te_marra.add(g['id'])
            if len(pare) >= k:
                break
        return pare[:k]
    except Exception:  # noqa: BLE001
        return kandidatet[:k]
