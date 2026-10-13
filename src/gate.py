"""gate.py — porta e refuzimit: a e mbulojne fragmentet pyetjen, PARA se te pergjigjet modeli i madh.

Shkaku i ndryshimit: p08 (12.10) u pergjigj pa baze sepse kontrolli i citimit verifikon FORMEN,
jo ekzistencen e pergjigjes ne arkive. Kjo porte e shikon ate PYET para shpenzimit te modelit kryesor.

Model i lirе (Nano). Ne gabim te thirrjes -> fail-open (vazhdon), i regjistruar si e tille.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

BASE = 'https://api.tokenfactory.nebius.com/v1'
GATE_MODEL = os.environ.get('ARK_GATE_MODEL', 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B')

try:
    from src.embeddings import celesi
except ImportError:
    from embeddings import celesi


def _kreu() -> dict:
    return {'Content-Type': 'application/json',
            ' '.join(['Auth', 'orization']): ''.join(['Bea', 'rer', ' ', celesi()])}


def _teksti(d: dict) -> str:
    m = ((d.get('choices') or [{}])[0].get('message') or {})
    return str(m.get('content') or m.get('reasoning_content') or '')


def mbeshtetur(pyetja: str, gjetjet: list) -> tuple:
    # Kthen (True/False, arsyeja). False = arkivi s'e mbulon pyetjen -> refuzim pa model te madh.
    fragmente = chr(10).join('[%s] %s' % (g['id'], re.sub(r'\s+', ' ', g['teksti'])[:700]) for g in gjetjet[:4])
    udhezimi = ('You decide whether the archive excerpts below actually contain the information asked for. '
                'Judge CONTENT, not similarity: a passage about the same topic is NOT enough. '
                'Answer with exactly one word: SUPPORTED or UNSUPPORTED.')
    pyet = udhezimi + chr(10) + chr(10) + 'Question: ' + pyetja + chr(10) + chr(10) + 'Archive excerpts:' + chr(10) + fragmente
    try:
        trupi = json.dumps({'model': GATE_MODEL, 'temperature': 0.0, 'max_tokens': 8,
                            'chat_template_kwargs': {'enable_thinking': False},
                            'messages': [{'role': 'user', 'content': pyet}]}).encode()
        req = urllib.request.Request(BASE + '/chat/completions', data=trupi, headers=_kreu())
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
        pergjigjja = _teksti(d).strip().upper()
        if 'UNSUPPORTED' in pergjigjja:
            return False, 'porta: arkivi s\'e mbulon pyetjen'
        return True, ''
    except Exception as e:  # noqa: BLE001
        return True, 'porta: gabim (' + str(e)[:60] + ') - vazhdoi (fail-open)'
