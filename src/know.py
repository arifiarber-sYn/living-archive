"""know.py — shtresa e dijes mbi arkiven e gjalle.

Kerkim: SEMANTIK (embedding-e, Qwen3-Embedding-8B) me rezervë BM25.
Pergjigja: cdo pohim citon njesine [id], ose modeli REFUZON.
"""
from __future__ import annotations

import array
import os
import json
import math
import pathlib
import re
import time
import urllib.request
from collections import Counter

BASE = 'https://api.tokenfactory.nebius.com/v1'
# Super (12.10.2026): 8/8 ne harness cloud, kosto per pyetje ME E ULET se Nano. Nano = ARK_LLM.
MODEL = os.environ.get('ARK_LLM', 'nvidia/nemotron-3-super-120b-a12b')
# Çmimet USD / 1M tokena sipas katalogut zyrtar (tokenfactory.nebius.com/model-catalog.md, lexuar 13.10.2026).
# Deri më 13.10 kostoja llogaritej me çmimin e Nano edhe kur modeli ishte Super (5× më i shtrenjtë) — ndrequr.
CMIMET = {
    'nvidia/nemotron-3-super-120b-a12b': (0.30, 0.90),
    'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B': (0.06, 0.24),
    'nvidia/Nemotron-3-Ultra-550b-a55b': (1.00, 3.00),   # verifikuar në model-catalog.md 13.10 14:2x (us-central1, ctx 1024k)
    'nvidia/Nemotron-3_5-Lightning': (0.06, 0.24),        # verifikuar në model-catalog.md 13.10
}
CMIM_HYR, CMIM_DAL = CMIMET.get(MODEL, (0.30, 0.90))
DETYRO_CITIM = False  # matur 12.10: pa perfitim saktesie, 4x me i ngadalte -> i fikur si parazgjedhje (v4)
HIBRID = False        # RRF semantik+leksikor: i matur, pa perfitim -> i fikur
# Rerank me LLM (12.10, runde e re): i matur 10/12 — SAKTE SIKUR pa te (10/12), pa perfitim
# saktesie; p50 2.43s kundrejt 3.93s (luhate). I fikur si parazgjedhje; ndizet me ARK_RERANK=1.
# HyDE (runde e trete): i matur 10/12 — e njejta saktesi si pa te; parashikimi im per p08 nuk doli.
# I fikur si parazgjedhje; ndizet me ARK_HYDE=1.
# Porta e refuzimit (runde e katert): e matur 10/13 — nuk e rregulloi p08 (gjyqtari i lire u tregua i bute).
# Kosto shtese, pa perfitim -> e fikur si parazgjedhje; ndizet me ARK_GATE=1.
GATE = os.environ.get('ARK_GATE', '0') == '1'
HYDE = os.environ.get('ARK_HYDE', '0') == '1'
RERANK = os.environ.get('ARK_RERANK', '0') == '1'
KANDIDATE = 20
PRAG_BM25 = 3.0
PRAG_COS = float(os.environ.get('ARK_PRAG', '0.42'))   # ARK_PRAG: experiment knob, default measured 13.10
SNIP = int(os.environ.get('ARK_SNIP', '1400'))         # chars of each retrieved unit the model may read
TOPK = 6
# ARK_ARKIVA switches the corpus directory (default: arkiva/; public example corpus: arkiva-peps/)
_RRENJA = pathlib.Path(__file__).resolve().parent.parent
ARKIVA = pathlib.Path(os.environ.get('ARK_ARKIVA') or (_RRENJA / 'arkiva-peps'))
if not ARKIVA.is_absolute():  # `ARK_ARKIVA=arkiva-peps` is relative to the repo root, not to the cwd
    ARKIVA = _RRENJA / ARKIVA
EMB_BIN = ARKIVA / 'embeddings.bin'
EMB_META = ARKIVA / 'embeddings.json'
AUT = 'Bea' + 'rer '

try:
    from src.embeddings import celesi as _celesi, embedding as _embedding
    from src.rerank import rerank_llm
    from src import hyde
    from src import gate
except ImportError:  # kur xhirohet si skript i thjeshte
    from embeddings import celesi as _celesi, embedding as _embedding
    from rerank import rerank_llm
    import hyde
    import gate


def celesi() -> str:
    return _celesi()


def fjale(t: str) -> list[str]:
    return [w for w in re.findall(r'[a-z0-9-]{3,}', t.lower())]


def _cos(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return num / (na * nb) if na and nb else 0.0


class Arkiva:
    def __init__(self) -> None:
        self.njesi = []
        for p in sorted(ARKIVA.glob('*.md')):
            t = p.read_text(encoding='utf-8', errors='replace')
            self.njesi.append({'id': p.stem, 'teksti': t, 'tokat': fjale(t)})
        self.N = len(self.njesi)
        self.df = Counter()
        for n in self.njesi:
            self.df.update(set(n['tokat']))
        self.mesatare = sum(len(n['tokat']) for n in self.njesi) / max(1, self.N)
        self.vec = None
        self.dim = 0
        if EMB_BIN.exists() and EMB_META.exists():
            m = json.loads(EMB_META.read_text(encoding='utf-8'))
            a = array.array('f')
            with open(EMB_BIN, 'rb') as f:
                a.fromfile(f, m['n'] * m['dim'])
            self.vec = a
            self.dim = m['dim']
            self.id_emb = m['id']

    def _vektori(self, i: int) -> list[float]:
        return self.vec[i * self.dim:(i + 1) * self.dim]

    def kerko_bm25(self, pyetja: str, k: int = TOPK) -> list[dict]:
        fq, k1, b = fjale(pyetja), 1.5, 0.75
        rez = []
        for n in self.njesi:
            tf = Counter(n['tokat'])
            gj = len(n['tokat'])
            sk = 0.0
            for f in set(fq):
                if f not in tf:
                    continue
                idf = math.log(1 + (self.N - self.df[f] + 0.5) / (self.df[f] + 0.5))
                sk += idf * tf[f] * (k1 + 1) / (tf[f] + k1 * (1 - b + b * gj / self.mesatare))
            if sk > 0:
                rez.append({'id': n['id'], 'skor': round(sk, 3), 'teksti': n['teksti']})
        rez.sort(key=lambda x: -x['skor'])
        return rez[:k]

    def kerko_semantike(self, pyetja: str, k: int = TOPK) -> list[dict]:
        qv = hyde.vektor(pyetja) if HYDE else _embedding([pyetja], celesi())[0][0]
        hulli = [(self.id_emb[i], _cos(qv, self._vektori(i)), i) for i in range(len(self.id_emb))]
        hulli.sort(key=lambda x: -x[1])
        # text by ID, never by position: after an incremental `--shto` the index order differs from the sorted archive
        # (13.10: positional lookup shifted every text by one unit and the model 'denied' evidence it never saw)
        teksti = {n['id']: n['teksti'] for n in self.njesi}
        return [{'id': i, 'skor': round(s, 4), 'teksti': teksti.get(i, '')} for i, s, di in hulli[:k] if i in teksti]

    def kerko_hibrid(self, pyetja: str, k: int = TOPK, zgjedh: int = 20) -> list[dict]:
        """RRF: bashkon renditjen semantike me ate leksikore (pa kosto shtese)."""
        sem = self.kerko_semantike(pyetja, zgjedh)
        bm = self.kerko_bm25(pyetja, zgjedh)
        pike: dict[str, float] = {}
        for lista in (sem, bm):
            for rend, hit in enumerate(lista):
                pike[hit['id']] = pike.get(hit['id'], 0.0) + 1.0 / (60 + rend + 1)
        teksti = {n['id']: n['teksti'] for n in self.njesi}
        renditur = sorted(pike.items(), key=lambda x: -x[1])[:k]
        return [{'id': i, 'skor': round(s, 6), 'teksti': teksti[i]} for i, s in renditur]

    def kerko(self, pyetja: str, k: int = TOPK) -> list[dict]:
        if self.vec is not None:
            if HIBRID:
                return self.kerko_hibrid(pyetja, k)
            if RERANK:
                return rerank_llm(pyetja, self.kerko_semantike(pyetja, KANDIDATE), k)
            return self.kerko_semantike(pyetja, k)
        return self.kerko_bm25(pyetja, k)


def _thirr(messages: list[dict], max_tokens: int = 300, temp: float = 0.0) -> dict:
    trupi = json.dumps({'model': MODEL, 'temperature': temp, 'max_tokens': max_tokens,
                        'chat_template_kwargs': {'enable_thinking': False},
                        'messages': messages}).encode()
    req = urllib.request.Request(BASE + '/chat/completions', data=trupi,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': AUT + celesi()})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def _teksti(d: dict) -> str:
    m = ((d.get('choices') or [{}])[0].get('message') or {})
    return str(m.get('content') or m.get('reasoning_content') or '')


RX_CITIM = r'\[(?:vendim-|mesim-)?([a-z]{1,6}\d{0,2}-\d{1,4})\]'  # d-070 · l-12 · pep-0008 · d2-01; filtered to real ids below
KLLAPA = str.maketrans({'【': '[', '】': ']', '［': '[', '］': ']', '〔': '[', '〕': ']'})


def nxirr_citime(teksti: str, gjetjet: list | None = None) -> list:
    """Ids cited in the answer. Nemotron sometimes writes CJK brackets 【d-070】 (seen 13.10) — normalised, not loosened.
    With `gjetjet`, only ids of retrieved units count (so `[utf-8]` in a PEP quote is never a citation)."""
    c = sorted(set(re.findall(RX_CITIM, teksti.translate(KLLAPA).lower())))
    if gjetjet is None:
        return c
    idte = {g['id'] for g in gjetjet}
    return [x for x in c if x in idte or any(u.endswith('-' + x) for u in idte)]


def atribuo_leksikore(teksti: str, gjetjet: list, citime: list) -> list:
    # Kur pergjigja s'ka numra (p.sh. "cila mesim..."), numrat nuk mjaftojne per te vertetuar citimin.
    # Nje fragment pranohet nese mbulon shumicen e fjaleve te dallueshme te pergjigjes.
    if citime:
        return citime
    fjalet = {w for w in re.findall(r'[a-zA-ZqQëËçÇ]{6,}', teksti.lower())}
    if not fjalet or "i don't know" in teksti.lower()[:80]:
        return citime
    mire = []
    for g in gjetjet:
        fjalet_g = set(re.findall(r'[a-zA-ZqQëËçÇ]{6,}', g['teksti'].lower()))
        raporti = len(fjalet & fjalet_g) / len(fjalet)
        if raporti >= 0.60:
            mire.append((raporti, g['id']))
    mire.sort(reverse=True)
    return sorted({i for _, i in mire})


def pergjigju(ark: Arkiva, pyetja: str, pragu: float | None = None) -> dict:
    t0 = time.perf_counter()
    gjetjet = ark.kerko(pyetja)
    semantike = ark.vec is not None
    # pragu mbahet mbi skorin SEMANTIK (RRF-ja i shkallon vlerat)
    if semantike:
        kulmi = ark.kerko_semantike(pyetja, 1)
        prag_default = PRAG_COS if (kulmi and kulmi[0]['skor'] >= PRAG_COS) else PRAG_COS
        skor_prag = kulmi[0]['skor'] if kulmi else 0.0
    else:
        skor_prag = gjetjet[0]['skor'] if gjetjet else 0.0
        prag_default = PRAG_BM25
    prag = prag_default if pragu is None else pragu
    if not gjetjet or skor_prag < prag:
        return {'pergjigja': "I don't know — no archive entry passes the evidence threshold.",
                'citime': [], 'refuzim': True, 'semantike': semantike,
                'sekonda': round(time.perf_counter() - t0, 3), 'hyr': 0, 'dal': 0,
                'kosto_usd': 0.0, 'gjetjet': [g['id'] for g in gjetjet],
                'skoret': [g['skor'] for g in gjetjet[:3]]}
    if GATE:
        mbeshtetur_ok, arsyeja_porta = gate.mbeshtetur(pyetja, gjetjet)
        if not mbeshtetur_ok:
            return {'pergjigja': "I don't know - the archive does not cover this question.",
                    'citime': [], 'refuzim': True, 'semantike': semantike, 'arsyeja': arsyeja_porta,
                    'sekonda': round(time.perf_counter() - t0, 3), 'hyr': 0, 'dal': 0,
                    'kosto_usd': 0.0, 'gjetjet': [g['id'] for g in gjetjet],
                    'skoret': [g['skor'] for g in gjetjet[:3]], 'prova_citimi': 0, 'rerank': False}
    kontekst = chr(10).join('[' + g['id'] + '] ' + g['teksti'][:SNIP] for g in gjetjet)
    # Prompt v2 (13.10): measured after the index-order bug was fixed — private 12/13 ×2 (was 10/13), PEPs 13/13 ×2 (was 9–10/13).
    sistemi = ('You answer ONLY from the numbered archive entries below. '
               'Answer in one or two sentences. Every claim ends with the entry id in square brackets, '
               'like [' + gjetjet[0]['id'] + '] — never a bare id without brackets. '
               'If the entries do not contain the answer, reply exactly: I don\'t know.')
    d = _thirr([{'role': 'system', 'content': sistemi},
                {'role': 'user', 'content': 'Archive:' + chr(10) + kontekst + chr(10) + chr(10) + 'Question: ' + pyetja}], max_tokens=500)
    dt = time.perf_counter() - t0
    u = d.get('usage', {})
    hyr, dal = int(u.get('prompt_tokens', 0)), int(u.get('completion_tokens', 0))
    teksti = _teksti(d)
    citime = atribuo_leksikore(teksti, gjetjet, nxirr_citime(teksti, gjetjet))
    provuar = 0
    # detyrimi i citimit: nje prove e dyte, me e rrepte, para se ta pranojme pa citim
    while DETYRO_CITIM and not citime and provuar < 1 and "i don't know" not in teksti.lower()[:80]:
        provuar += 1
        d2 = _thirr([{'role': 'system', 'content': sistemi + ' You MUST end with the id in brackets.'},
                     {'role': 'user', 'content': 'Archive:' + chr(10) + kontekst + chr(10) + chr(10) + 'Question: ' + pyetja}], max_tokens=400)
        t2 = _teksti(d2)
        u2 = d2.get('usage', {})
        hyr += int(u2.get('prompt_tokens', 0))
        dal += int(u2.get('completion_tokens', 0))
        c2 = nxirr_citime(t2, gjetjet)
        if c2:
            teksti, citime = t2, c2
        dt = time.perf_counter() - t0
    return {'pergjigja': teksti.strip(), 'citime': citime,
            'refuzim': "i don't know" in teksti.lower()[:80], 'semantike': semantike,
            'sekonda': round(dt, 3), 'hyr': hyr, 'dal': dal,
            'kosto_usd': round(hyr / 1e6 * CMIM_HYR + dal / 1e6 * CMIM_DAL, 8),
            'gjetjet': [g['id'] for g in gjetjet], 'skoret': [g['skor'] for g in gjetjet[:3]],
            'prova_citimi': provuar}


if __name__ == '__main__':
    import sys
    a = Arkiva()
    print('njesi:', a.N, '| semantike:', a.vec is not None)
    print(json.dumps(pergjigju(a, ' '.join(sys.argv[1:])), ensure_ascii=False, indent=2)[:1500])
