#!/usr/bin/env python3
"""Arkivi i Gjalle - gelltitje, indeksim me embedime lokale, pergjigje me CITIME.
Vetem standard library + ollama lokal (pa API te jashtme)."""
import hashlib, html, http.server, json, math, os, pathlib, socketserver, subprocess, sys, threading, time, urllib.parse, urllib.request
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent.parent
KORPUS = BASE / 'korpus'
INDEKS = BASE / 'indeksi' / 'indeksi.json'
VLERESIMET = BASE / 'indeksi' / 'vleresimet.jsonl'
OLLAMA = 'http://127.0.0.1:11434/api/embeddings'
OLLAMA_GEN = 'http://127.0.0.1:11434/api/generate'
EMB = os.environ.get('ARK_EMB', 'nomic-embed-text')
LLM = os.environ.get('ARK_LLM', 'qwen3:4b')  # default PUBLIK (ollama pull qwen3:4b); ndrysho me ARK_LLM
PORT = int(os.environ.get('ARK_PORT', '8903'))
CHUNK = 700
TOPK = 5
PRAG = 0.45

def ts():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def embed(text):
    body = json.dumps({'model': EMB, 'prompt': text[:2000]}).encode('utf-8')
    req = urllib.request.Request(OLLAMA, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        v = json.loads(r.read().decode('utf-8')).get('embedding') or []
    if not v:
        raise RuntimeError('embed() ktheu vektor BOSH (modeli ' + EMB + ' mungon ose gaboi) — ' +
                           'verifiko: ollama list && ollama pull ' + EMB)
    return v

def gen(prompt, npred=300, model=None):
    body = json.dumps({'model': model or LLM, 'prompt': prompt, 'stream': False,
                       'options': {'temperature': 0, 'num_predict': npred}, 'think': False}).encode('utf-8')
    req = urllib.request.Request(OLLAMA_GEN, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode('utf-8'))
    return (d.get('response') or d.get('thinking') or '').strip()

def teksti_i_skedarit(p):
    if p.suffix.lower() == '.pdf':
        try:
            r = subprocess.run(['pdftotext', '-layout', str(p), '-'], capture_output=True, timeout=60)
            return r.stdout.decode('utf-8', errors='replace')
        except Exception:
            return ''
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''

def copto(t):
    t = ' '.join(t.split())
    if not t:
        return []
    out, i = [], 0
    while i < len(t):
        out.append(t[i:i + CHUNK])
        i += CHUNK - 120
    return out

def gelltit():
    INDEKS.parent.mkdir(parents=True, exist_ok=True)
    baza, raport = [], []
    skedaret = [p for p in sorted(KORPUS.rglob('*')) if p.is_file()]
    for n, p in enumerate(skedaret, 1):
        text = teksti_i_skedarit(p)
        c = copto(text)
        did = 'd' + str(n)
        for k, ch in enumerate(c):
            v = embed(ch)  # deshton me ze (raise) nese endpoint-i s'pergjigjet ose kthen bosh
            baza.append({'id': did + '-' + str(k), 'dok': did, 'file': str(p.relative_to(KORPUS)),
                         'tekst': ch, 'vec': v})
        raport.append({'dok': did, 'file': str(p.relative_to(KORPUS)), 'shkronja': len(text),
                       'copa': len(c), 'kuptova': ('po' if len(text.strip()) > 40 else 'JO')})
    if any(not c['vec'] for c in baza):
        raise RuntimeError('indeksi me vektor BOSH — gelltitja e dështoi, mos e ruaj')
    INDEKS.write_text(json.dumps({'krijuar': ts(), 'copa': baza, 'raport': raport}, ensure_ascii=False), encoding='utf-8')
    return raport, len(baza)

def cosine(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    da = math.sqrt(sum(x * x for x in a)) or 1.0
    db = math.sqrt(sum(x * x for x in b)) or 1.0
    return sum(x * y for x, y in zip(a, b)) / (da * db)

def lexo_inde():
    if not INDEKS.exists():
        return {'copa': [], 'raport': []}
    return json.loads(INDEKS.read_text(encoding='utf-8'))

def ruaj_vleresim(q, v, citimet):
    VLERESIMET.parent.mkdir(parents=True, exist_ok=True)
    with VLERESIMET.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'ts': ts(), 'pyetja': q, 'vleresimi': v, 'citime': citimet}, ensure_ascii=False) + chr(10))


def boosts():
    b = {}
    if not VLERESIMET.exists():
        return b
    madhesi = {'sakte': 0.04, 'gabim': -0.12}
    for ln in VLERESIMET.read_text(encoding='utf-8').splitlines():
        try:
            r = json.loads(ln)
        except Exception:
            continue
        d = madhesi.get(r.get('vleresimi'))
        if not d:
            continue
        for cid in (r.get('citime') or []):
            b[cid] = round(b.get(cid, 0.0) + d, 3)
    return b


def kerko(pyetja, k=TOPK):
    inx = lexo_inde()
    try:
        v = embed(pyetja)
    except Exception:
        return []
    bb = boosts()
    sh = sorted(((cosine(v, c['vec']) + bb.get(c['id'], 0.0), c) for c in inx['copa']), key=lambda x: -x[0])
    return [(s, c) for s, c in sh[:k]]

def pergjigju(pyetja, k=TOPK):
    top = kerko(pyetja, k)
    if not top or top[0][0] < PRAG:
        return {'pergjigja': 'S E DI', 'citime': [], 'siguria': round(top[0][0], 3) if top else 0.0, 'baza': 'pa baze ne korpus'}
    frag = chr(10).join('[' + c['id'] + '] (' + c['file'] + '): ' + c['tekst'][:600] for s, c in top)
    p = ('/no_think' + chr(10) + 'Je arkivist. Pergjigju VETEM nga fragmentet me poshte.' + chr(10)
         + 'Cdo fakt duhet te kete citimin [id-i] i fragmentit.' + chr(10)
         + 'Nese fragmentet nuk e mbulojne pyetjen, shkruaj SAKTESISHT: S E DI' + chr(10) + chr(10)
         + 'FRAGMENTET:' + chr(10) + frag + chr(10) + chr(10) + 'PYETJA: ' + pyetja + chr(10) + 'PERGJIGJA:')
    try:
        ans = gen(p, 400)
    except Exception as e:
        return {'pergjigja': 'GABIM: ' + type(e).__name__, 'citime': [], 'siguria': 0.0, 'baza': 'gabim'}
    if ans.strip().upper().startswith('S E DI'):
        return {'pergjigja': 'S E DI', 'citime': [], 'siguria': round(top[0][0], 3), 'baza': 'LLM: s e di'}
    cits = [c['id'] for s, c in top if c['id'] in ans]
    bb = boosts()
    if any(bb.get(c['id'], 0.0) > 0 for s, c in top):
        ans = ans + chr(10) + '[feedback: kjo pergjigje u ndikua nga vleresimet e meparshme]'
    return {'pergjigja': ans, 'citime': cits, 'siguria': round(top[0][0], 3), 'baza': 'korpusi'}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'ndihme'
    if cmd == 'gelltit':
        rap, n = gelltit()
        print(json.dumps({'copa': n, 'dokumente': len(rap)}, ensure_ascii=False))
    elif cmd == 'pyet':
        print(json.dumps(pergjigju(' '.join(sys.argv[2:])), ensure_ascii=False, indent=1)[:900])
    else:
        print('komandat: gelltit | pyet <pyetja>')
