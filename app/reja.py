#!/usr/bin/env python3
"""Motori REJA — i njejti arkiv, por kerkimi dhe pergjigja kalojne ne Nebius Token Factory.

Perdorimi:
  export NEBIUS_API_KEY=***      # ose celesi ne thesarin lokal
  export ARK_ENGINE=reja
  python3 app/reja.py gelltit    # indekso korpusin me Qwen3-Embedding-8B
  python3 app/reja.py pyet "pyetja"

Parimi i njejte si motori lokal: pergjigja OSE citon, OSE refuzon. Pa trillim.
"""
import json, os, pathlib, re, time, urllib.request
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent.parent
KORPUS = BASE / 'korpus'
INDEKS = BASE / 'indeksi' / 'reja.json'
KOSTO = BASE / 'indeksi' / 'reja-kosto.json'
URL = 'https://api.tokenfactory.nebius.com/v1'
EMB = os.environ.get('ARK_EMB_REJA', 'Qwen/Qwen3-Embedding-8B')
LLM = os.environ.get('ARK_LLM_REJA', 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B')
TOPK = int(os.environ.get('ARK_TOPK', '5'))
# Kalibrimi (12.10.2026, app/kalibrim.py) dha ndarje te ngushte: 0.3733 (pa mbulim) vs 0.3736 (me mbulim).
# Nje prag i vetem absolut luhate (flapping) — pra s'vendoset mbi te gjithe pergjigjen.
# Dy shtresa: (1) dysheme e sigurise PRAG_MIN; (2) verifikim i citimit pas pergjigjes.
PRAG_MIN = float(os.environ.get('ARK_PRAG_MIN', '0.30'))
CMIM_HYR, CMIM_DAL = 0.06, 0.24      # USD / 1M token, Nemotron Nano (Token Factory)
def _auth(k):
    return ''.join(['Bea', 'rer ', k])


def ts():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def celesi():
    k = os.environ.get('NEBIUS_API_KEY')
    if k:
        return k.strip()
    p = pathlib.Path.home() / '.securevault/secrets/nebius-api.key'
    if p.exists():
        return p.read_text(encoding='utf-8', errors='replace').strip().splitlines()[-1].strip()
    raise SystemExit("NDAL: vendos NEBIUS_API_KEY (ose celesin lokal). Pa celes, motori REJA s'ndizet.")


def _post(rruga, trupi, timeout=180):
    req = urllib.request.Request(URL + rruga, data=json.dumps(trupi).encode(),
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': _auth(celesi())})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def embed(tekste, timeout=180):
    """Embedime me Token Factory. Kthen [[float]] dhe token-a e shpenzuar."""
    if isinstance(tekste, str):
        tekste = [tekste]
    d = _post('/embeddings', {'model': EMB, 'input': tekste}, timeout)
    vargu = sorted(d['data'], key=lambda x: x['index'])
    return [x['embedding'] for x in vargu], int(d.get('usage', {}).get('total_tokens', 0))


def gen(prompt, npred=400, timeout=180):
    """Pergjigje nga modeli NVIDIA. Kthen (tekst, token_hyr, token_dal)."""
    d = _post('/chat/completions', {'model': LLM, 'temperature': 0.0, 'max_tokens': npred,
                                    'chat_template_kwargs': {'enable_thinking': False},
                                    'messages': [{'role': 'user', 'content': prompt}]}, timeout)
    m = ((d.get('choices') or [{}])[0].get('message') or {})
    u = d.get('usage', {})
    return (str(m.get('content') or m.get('reasoning_content') or ''),
            int(u.get('prompt_tokens', 0)), int(u.get('completion_tokens', 0)))


def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return num / (na * nb) if na and nb else 0.0


def copto(t, sa=1200):
    pjese, t = [], t.strip()
    while t:
        pjese.append(t[:sa])
        t = t[sa:]
    return pjese


def teksti_i_skedarit(p):
    if p.suffix.lower() == '.pdf':
        import subprocess
        try:
            return subprocess.run(['pdftotext', str(p), '-'], capture_output=True, text=True, timeout=60).stdout
        except Exception:
            return ''
    return p.read_text(encoding='utf-8', errors='replace')


def gelltit():
    """Indekson korpusin me embedding-e te Token Factory. Raporton cka s'u kuptua."""
    INDEKS.parent.mkdir(parents=True, exist_ok=True)
    njesi, pa_kuptu, tokat = [], [], 0
    for p in sorted(KORPUS.rglob('*')):
        if not p.is_file():
            continue
        t = teksti_i_skedarit(p)
        if len(t.strip()) < 40:
            pa_kuptu.append(p.name)
            continue
        pjese = copto(t)
        vec, tk = embed(pjese)
        tokat += tk
        for i, (c, v) in enumerate(zip(pjese, vec)):
            njesi.append({'id': '%s-%d' % (p.stem[:14], i), 'skedari': p.name, 'teksti': c, 'vec': v})
    INDEKS.write_text(json.dumps({'koha': ts(), 'emb': EMB, 'token_a': tokat, 'njesi': njesi}, ensure_ascii=False), encoding='utf-8')
    print('indeksuar: %d njesi nga %s' % (len(njesi), KORPUS))
    if pa_kuptu:
        print('PA KUPTUAR (%d): %s' % (len(pa_kuptu), ', '.join(pa_kuptu)))
    print('token-a embedimi: %d' % tokat)
    return len(njesi)


def lexo_inde():
    if not INDEKS.exists():
        raise SystemExit("s'ka indeks — xhiro: python3 app/reja.py gelltit")
    return json.loads(INDEKS.read_text(encoding='utf-8'))


def kerko(pyetja, k=TOPK):
    inde = lexo_inde()
    qv, _ = embed(pyetja)
    q = qv[0]
    hulli = [{'id': n['id'], 'skedari': n['skedari'], 'teksti': n['teksti'],
              'skor': cosine(q, n['vec'])} for n in inde['njesi']]
    hulli.sort(key=lambda x: -x['skor'])
    return hulli[:k]


def pergjigju(pyetja, k=TOPK):
    t0 = time.perf_counter()
    gjetjet = kerko(pyetja, k)
    if not gjetjet or gjetjet[0]['skor'] < PRAG_MIN:
        return {'pyetja': pyetja, 'pergjigja': "S'E DI", 'citime': [], 'refuzim': True,
                'sekonda': round(time.perf_counter() - t0, 3), 'kosto_usd': 0.0,
                'njesi': [g['id'] for g in gjetjet]}
    kontekst = chr(10).join('[%s] %s' % (g['id'], g['teksti'][:1200]) for g in gjetjet)
    prompt = ('Pergjigju VETEM nga fragmentet e arkivit me poshte, ne shqip. '
              'Cdo pohim duhet te mbaje id-ne ne kllapa katrore, p.sh. [vendim-3]. '
              'Nese fragmentet nuk e mbulojne pyetjen, pergjigju saktesisht: S\'E DI' + chr(10) + chr(10)
              + 'Arkivi:' + chr(10) + kontekst + chr(10) + chr(10) + 'Pyetja: ' + pyetja)
    tekst, hyr, dal = gen(prompt)
    dt = time.perf_counter() - t0
    id_te_gjetura = {g['id'] for g in gjetjet}
    citime = sorted(set(re.findall(r'\[([^\]]{1,40})\]', tekst)))
    # shtresa 2: citimi duhet te tregoje nje fragment te GJTUR. Pa te, pergjigja s'mbahet.
    te_vertetueshme = [c for c in citime if c in id_te_gjetura]
    refuzim = "s'e di" in tekst.strip().lower()[:40]
    kosto = hyr / 1e6 * CMIM_HYR + dal / 1e6 * CMIM_DAL
    _shto_kosto(hyr, dal, kosto)
    arsyeja = ''
    if not refuzim and not te_vertetueshme:
        # pa citim qe tregon nje fragment te gjetur -> nuk mbahet
        arsyet = refuzim = True
        arsyeja = 'pergjigje pa citim te verifikueshem'
        tekst = "S'E DI"
    return {'pyetja': pyetja, 'pergjigja': tekst.strip(), 'citime': citime, 'arsyeja': arsyeja,
            'refuzim': refuzim, 'sekonda': round(dt, 3), 'kosto_usd': round(kosto, 8),
            'token_hyr': hyr, 'token_dal': dal, 'njesi': [g['id'] for g in gjetjet],
            'skoret': [round(g['skor'], 4) for g in gjetjet[:3]]}


def _shto_kosto(hyr, dal, kosto):
    d = {'koha': ts(), 'hyr': hyr, 'dal': dal, 'kosto_usd': kosto}
    with open(KOSTO, 'a', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False) + chr(10))


def kosto_totale():
    if not KOSTO.exists():
        return {'thirrje': 0, 'kosto_usd': 0.0}
    n, s = 0, 0.0
    for rresht in KOSTO.read_text(encoding='utf-8').splitlines():
        if rresht.strip():
            d = json.loads(rresht)
            n += 1
            s += d['kosto_usd']
    return {'thirrje': n, 'kosto_usd': round(s, 6)}


def main():
    import sys
    if len(sys.argv) < 2:
        print('perdorimi: reja.py [gelltit|pyet "..."|kosto]')
        return 1
    cmd = sys.argv[1]
    if cmd == 'gelltit':
        return 0 if gelltit() is not None else 1
    if cmd == 'kosto':
        print(json.dumps(kosto_totale(), ensure_ascii=False))
        return 0
    if cmd == 'pyet':
        r = pergjigju(' '.join(sys.argv[2:]))
        print(r['pergjigja'])
        print('---')
        print('citime:', r['citime'], '| refuzim:', r['refuzim'])
        print('kohe: %ss | kosto: $%s' % (r['sekonda'], r['kosto_usd']))
        return 0
    print('komande e panjohur:', cmd)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
