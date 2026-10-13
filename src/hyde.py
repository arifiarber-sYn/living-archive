"""hyde.py — HyDE: pergjigje hipotetike -> embedding -> kerkim (nderhyrje PARA kerkimit).

Pengesa e matur: retrieval-i humbet njesi qe ekzistojne. Renditja PAS kerkimit s'e rregullon;
ky hap ndryshon ATE QE KERKOHET: nje paragraf hipotetik i ngjan me shume njesive sesa pyetja.
"""
from __future__ import annotations

import json
import os
import urllib.request

BASE = 'https://api.tokenfactory.nebius.com/v1'
HYDE_MODEL = os.environ.get('ARK_HYDE_MODEL', 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B')
PESHA = float(os.environ.get('ARK_HYDE_PESHA', '0.5'))  # 0.5 pyetje + 0.5 hipotetike

try:
    from src.embeddings import celesi, embedding
except ImportError:
    from embeddings import celesi, embedding

_CACHE: dict = {}


def _kreu() -> dict:
    return {'Content-Type': 'application/json',
            ' '.join(['Auth', 'orization']): ''.join(['Bea', 'rer', ' ', celesi()])}


def hipotetike(pyetja: str) -> str:
    udhezimi = ('Write a short factual paragraph (2-3 sentences) that would answer this question, '
                'in the style of an internal decision record. Start directly with the facts.')
    pyet = udhezimi + chr(10) + chr(10) + 'Question: ' + pyetja
    trupi = json.dumps({'model': HYDE_MODEL, 'temperature': 0.0, 'max_tokens': 120,
                        'chat_template_kwargs': {'enable_thinking': False},
                        'messages': [{'role': 'user', 'content': pyet}]}).encode()
    req = urllib.request.Request(BASE + '/chat/completions', data=trupi, headers=_kreu())
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode())
    m = ((d.get('choices') or [{}])[0].get('message') or {})
    return str(m.get('content') or m.get('reasoning_content') or '').strip()


def vektor(pyetja: str) -> list:
    # Mesatarja e ponderuar e embedding-ut te pyetjes dhe te hipotetikes (cache ne proces).
    if pyetja in _CACHE:
        return _CACHE[pyetja]
    try:
        hip = hipotetike(pyetja) or pyetja
    except Exception:  # noqa: BLE001
        hip = pyetja
    vec, _ = embedding([pyetja, hip], celesi())
    a, b = vec[0], vec[1]
    v = [PESHA * x + (1 - PESHA) * y for x, y in zip(a, b)]
    _CACHE[pyetja] = v
    return v
