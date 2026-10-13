"""web_know.py — the same «cite or refuse» contract, applied to live web sources from Tavily.

Flow (behind the privacy gate — nothing leaves the machine unless `lejo=True`):
    question → Tavily search (top-k pages) → Nemotron on Nebius Token Factory reads ONLY those pages
             → an answer where every claim ends with [w1]/[w2]… (resolved to the URL), or exactly «I don't know».

Why a second knowledge layer: the archive answers from what the user already knows; the web layer answers
from what the user explicitly allowed to be looked up right now. Both refuse instead of guessing, and both
show the evidence. Fail-closed: no permission → refusal (0 network); no Tavily key → an explicit error, never a guess.
"""
from __future__ import annotations

import re
import time

from src import tavily_ndihmes
from src.know import CMIM_DAL, CMIM_HYR, KLLAPA, MODEL, _teksti, _thirr, nxirr_citime

MAKS_BURIME = 5
MAKS_NJESI = 3           # archive units offered next to the web pages when `ark` is given (memory first, web second)
SNIP_WEB = 1400          # chars of each page the model may read — the same budget as an archive unit
RX_W = re.compile(r'\[(w\d{1,2})\]')

REFUZIM_PORTA = ("Refused — the query did not leave this machine. The web layer needs an explicit permission "
                 "(allow=1 in the demo, --lejo in the agent skill) before anything is sent to Tavily.")


def nxirr_citime_web(teksti: str, idte: set[str]) -> list[str]:
    """[w1] … ids in the answer, normalised like the archive citations; only ids of retrieved pages count."""
    return [c for c in sorted(set(RX_W.findall(teksti.translate(KLLAPA).lower())), key=lambda s: int(s[1:])) if c in idte]


def pergjigju_web(pyetja: str, lejo: bool = False, max_burime: int = MAKS_BURIME, ark=None) -> dict:
    """With `ark` (an `Arkiva`), the model also sees the closest archive units and may cite them as [id] next to
    [wN] — memory first, web second, one answer with mixed citations. Without `ark`, web sources only."""
    t0 = time.perf_counter()
    baza = {'pyetja': pyetja, 'modeli': MODEL, 'burime': [], 'citime': [], 'njesi': [], 'hyr': 0, 'dal': 0, 'kosto_usd': 0.0}
    if not lejo:
        return {**baza, 'pergjigja': REFUZIM_PORTA, 'refuzim': True, 'porta': 'privacy gate: not allowed',
                'sekonda': round(time.perf_counter() - t0, 3)}
    if not tavily_ndihmes._celesi():
        return {**baza, 'pergjigja': "No Tavily key on this machine (TAVILY_API_KEY) — the web layer is off, nothing was guessed.",
                'refuzim': True, 'gabim': 'pa_celes', 'sekonda': round(time.perf_counter() - t0, 3)}
    rez = tavily_ndihmes.kerko(pyetja, max_burime)[:max_burime]
    burime = [{'id': 'w%d' % (i + 1), 'url': r.get('url', ''), 'titulli': (r.get('title') or '')[:160],
               'teksti': (r.get('content') or '')[:SNIP_WEB]} for i, r in enumerate(rez)]
    if not burime:
        return {**baza, 'pergjigja': "I don't know — the web search returned no sources.", 'refuzim': True,
                'sekonda': round(time.perf_counter() - t0, 3)}
    njesi = ark.kerko(pyetja, MAKS_NJESI) if ark is not None else []   # local, free — the memory the user already owns
    kontekst = chr(10).join('[%s] %s — %s%s%s' % (b['id'], b['titulli'], b['url'], chr(10), b['teksti']) for b in burime)
    if njesi:
        kontekst = (chr(10).join('[%s] %s' % (n['id'], n['teksti'][:SNIP_WEB]) for n in njesi)
                    + chr(10) + chr(10) + 'Web sources (fetched now, with the user\'s permission):' + chr(10) + kontekst)
    sistemi = ('You answer ONLY from the numbered sources below' + (' — the user\'s own archive entries first, then web pages' if njesi else '')
               + '. Answer in one or two sentences. Every claim ends with the source id in square brackets, like ['
               + (njesi[0]['id'] if njesi else 'w1') + '] or [w1] — never a bare id. '
               'If the sources do not contain the answer, reply exactly: I don\'t know.')
    d = _thirr([{'role': 'system', 'content': sistemi},
                {'role': 'user', 'content': ('Archive entries:' if njesi else 'Sources:') + chr(10) + kontekst + chr(10) + chr(10) + 'Question: ' + pyetja}], max_tokens=400)
    u = d.get('usage', {})
    hyr, dal = int(u.get('prompt_tokens', 0)), int(u.get('completion_tokens', 0))
    teksti = _teksti(d).strip()
    idte = {b['id'] for b in burime}
    cit = nxirr_citime_web(teksti, idte)
    cit_ark = nxirr_citime(teksti, njesi) if njesi else []          # only ids of retrieved units count (same rule as /pyet)
    sipas_id = {b['id']: b for b in burime}
    njesi_plota = {n['id']: n['id'] for n in njesi}
    return {**baza,
            'pergjigja': teksti,
            'refuzim': "i don't know" in teksti.lower()[:80],
            'citime': [{'id': c, 'url': sipas_id[c]['url'], 'titulli': sipas_id[c]['titulli']} for c in cit]
                      + [{'id': c, 'njesi': next((u for u in njesi_plota if u == c or u.endswith('-' + c)), c)} for c in cit_ark],
            'burime': [{k: b[k] for k in ('id', 'url', 'titulli')} for b in burime],
            'njesi': [n['id'] for n in njesi],
            'sekonda': round(time.perf_counter() - t0, 3), 'hyr': hyr, 'dal': dal,
            'kosto_usd': round(hyr / 1e6 * CMIM_HYR + dal / 1e6 * CMIM_DAL, 7)}


if __name__ == '__main__':
    import json
    import sys
    args = [a for a in sys.argv[1:] if a != '--lejo']
    print(json.dumps(pergjigju_web(' '.join(args) or 'When is the Nebius x NVIDIA Global AI Hackathon deadline?',
                                   lejo='--lejo' in sys.argv), ensure_ascii=False, indent=2))
