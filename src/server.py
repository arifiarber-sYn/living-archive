"""server.py — the real demo: ask the living archive, get a cited answer or a refusal — and browse the memory.

No external dependencies: http.server + know.py (Token Factory). Port 8077 (`ARK_PORT`), corpus `ARK_ARKIVA`.
Routes: /                 UI (English, `src/ui.html`): ask · memory audit trail · gated web layer · live metrics
        /pyet?q=          answer JSON (citations, refusal, latency, cost, retrieved ids)
        /web?q=&allow=1   the same cite-or-refuse contract over Tavily web sources PLUS the closest archive units
                          (memory first, web second — mixed [id]/[wN] citations; `memory=0` for web only); WITHOUT
                          allow=1 the privacy gate refuses and nothing leaves the machine (0 network) — `src/web_know.py`
        /njesi/<id>       one memory unit, raw markdown (the thing a citation points at)
        /historia         git log of the memory directory — the audit trail of `remember`
        /diff/<sha>       what one commit changed in the memory (git show --stat + patch, capped)
        /kosto            measured numbers (harness/report.json)   /health
"""
from __future__ import annotations

import http.server
import json
import os
import pathlib
import re
import socketserver
import subprocess
import sys
import threading
import time
import urllib.parse

RRENJA = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RRENJA))
from src.know import ARKIVA, MODEL, Arkiva, pergjigju  # noqa: E402
from src.web_know import pergjigju_web  # noqa: E402

PORT = int(os.environ.get('ARK_PORT', '8077'))
ARK = Arkiva()
REPORT = RRENJA / ('harness/report-peps.json' if ARKIVA.name == 'arkiva-peps' else 'harness/report.json')
MATJE = RRENJA / 'matje/prova-tani.json'
RX_ID = re.compile(r'^[a-z0-9-]{1,40}$')
RX_SHA = re.compile(r'^[0-9a-f]{7,40}$')
FAQJA = (pathlib.Path(__file__).with_name('ui.html')).read_text(encoding='utf-8')

# Example questions per corpus: one answerable, one that must be refused (the «failure beat» a judge should see).
SHEMBUJ = {
    'arkiva-peps': ['Which PEP added assignment expressions?', 'Which PEP introduced the match statement?',
                    'What does PEP 9999 propose?', 'Who won the 2026 World Cup?'],
}
SHEMBUJ_DEFAULT = ['Which decision grants unlimited autonomy?', 'What is the lesson about double submissions?',
                   'What is the capital of Australia?']


def _faqja() -> str:
    sh = SHEMBUJ.get(ARKIVA.name, SHEMBUJ_DEFAULT)
    uid = sorted(p.stem for p in ARKIVA.glob('*.md'))[:1] or ['']
    return (FAQJA.replace('__N__', str(ARK.N)).replace('__MODEL__', MODEL).replace('__Q__', sh[0])
            .replace('__UID__', uid[0])
            .replace('__EXAMPLES__', ' '.join('<a onclick="setq(this.textContent)">%s</a>' % s for s in sh)))


# Budget guard for a PUBLIC demo (off by default; both knobs are env vars, see README «Run it»):
#   ARK_RATE_PER_MIN — paid routes (/pyet, /web) per client IP per minute (0 = unlimited)
#   ARK_DAILY_CAP_USD — total measured spend per UTC day across all clients; above it the paid routes refuse with 429
# Client IP = X-Forwarded-For (tailscale funnel / reverse proxy) or the socket peer. State is in memory + a small JSON file
# so a restart does not reset the daily counter. Refusals cost $0 and are counted, never answered.
RATE_PER_MIN = int(os.environ.get('ARK_RATE_PER_MIN', '0'))
DAILY_CAP_USD = float(os.environ.get('ARK_DAILY_CAP_USD', '0'))
BUXHETI = RRENJA / 'matje' / ('.buxheti-%s.json' % ARKIVA.name)
_KYC = threading.Lock()
_GODITJET: dict[str, list[float]] = {}


def _buxheti_lexo() -> dict:
    sot = time.strftime('%Y-%m-%d', time.gmtime())
    try:
        d = json.loads(BUXHETI.read_text(encoding='utf-8'))
        if d.get('dita') == sot:
            return d
    except Exception:  # noqa: BLE001
        pass
    return {'dita': sot, 'kosto_usd': 0.0, 'thirrje': 0, 'refuzuar_429': 0}


def _buxheti_shto(kosto: float) -> None:
    with _KYC:
        d = _buxheti_lexo()
        d['kosto_usd'] = round(d['kosto_usd'] + max(kosto, 0.0), 6)
        d['thirrje'] += 1
        BUXHETI.parent.mkdir(parents=True, exist_ok=True)
        BUXHETI.write_text(json.dumps(d), encoding='utf-8')


def _roja(ip: str) -> str | None:
    """Returns a refusal reason or None. Sliding 60 s window per IP, then the daily cap."""
    tani = time.time()
    with _KYC:
        if RATE_PER_MIN:
            g = [t for t in _GODITJET.get(ip, []) if tani - t < 60]
            if len(g) >= RATE_PER_MIN:
                _GODITJET[ip] = g
                return 'rate limit: %d paid requests per minute per client' % RATE_PER_MIN
            g.append(tani)
            _GODITJET[ip] = g
            if len(_GODITJET) > 5000:   # never grow without bound on a public endpoint
                for k in list(_GODITJET)[:1000]:
                    _GODITJET.pop(k, None)
        if DAILY_CAP_USD:
            d = _buxheti_lexo()
            if d['kosto_usd'] >= DAILY_CAP_USD:
                d['refuzuar_429'] += 1
                BUXHETI.write_text(json.dumps(d), encoding='utf-8')
                return 'daily budget reached ($%.2f); the demo resumes at 00:00 UTC' % DAILY_CAP_USD
    return None


def _git(*args: str) -> str:
    try:
        return subprocess.run(['git', *args], cwd=RRENJA, capture_output=True, text=True, timeout=10).stdout
    except Exception as e:  # noqa: BLE001
        return 'git unavailable: ' + str(e)[:80]


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _dergo(self, b: bytes, ct: str, kodi: int = 200) -> None:
        self.send_response(kodi)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _ip(self) -> str:
        xf = self.headers.get('X-Forwarded-For', '')
        return (xf.split(',')[0].strip() if xf else self.client_address[0]) or '?'

    def _json(self, d, kodi: int = 200) -> None:
        self._dergo(json.dumps(d, ensure_ascii=False, indent=2).encode(), 'application/json', kodi)

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        if u.path == '/health':
            return self._dergo(b'{"status":"pass"}', 'application/json')
        if u.path == '/buxheti':   # public, read-only: what the guard has spent/refused today
            d = _buxheti_lexo()
            d.update({'rate_per_min': RATE_PER_MIN, 'daily_cap_usd': DAILY_CAP_USD})
            return self._json(d)
        if u.path == '/kosto':
            d = {}
            for skedari in (REPORT, MATJE):
                if skedari.exists():
                    j = json.loads(skedari.read_text(encoding='utf-8'))
                    d = {k: v for k, v in j.items() if k != 'rreshtat'}
                    break
            return self._json(d)
        if u.path == '/pyet':
            q = urllib.parse.parse_qs(u.query).get('q', [''])[0]
            if not q.strip():
                return self._json({'gabim': 'missing q'}, 400)
            arsye = _roja(self._ip())
            if arsye:
                return self._json({'gabim': arsye, 'refuzim': True, 'citime': [], 'kosto_usd': 0.0}, 429)
            r = pergjigju(ARK, q)
            r['njesi_arkive'] = ARK.N
            r['semantike'] = ARK.vec is not None
            _buxheti_shto(float(r.get('kosto_usd') or 0.0))
            return self._json(r)
        if u.path == '/web':
            qs = urllib.parse.parse_qs(u.query)
            q = qs.get('q', [''])[0]
            if not q.strip():
                return self._json({'gabim': 'missing q'}, 400)
            lejo = qs.get('allow', ['0'])[0] in ('1', 'true', 'yes')
            me_kujtese = qs.get('memory', ['1'])[0] not in ('0', 'false', 'no')   # archive units offered next to web pages
            arsye = _roja(self._ip()) if lejo else None   # the privacy-gate refusal is free and local; only paid calls count
            if arsye:
                return self._json({'gabim': arsye, 'refuzim': True, 'citime': [], 'burime': [], 'kosto_usd': 0.0}, 429)
            try:
                r = pergjigju_web(q, lejo=lejo, ark=ARK if me_kujtese else None)
                _buxheti_shto(float(r.get('kosto_usd') or 0.0))
                return self._json(r)
            except Exception as e:  # noqa: BLE001 — network/key errors are reported, never turned into an answer
                return self._json({'gabim': 'web layer failed: ' + str(e)[:120], 'refuzim': True, 'citime': [], 'burime': []}, 502)
        if u.path.startswith('/njesi/'):
            ident = u.path[len('/njesi/'):]
            if not RX_ID.match(ident):
                return self._json({'gabim': 'bad id'}, 400)
            p = ARKIVA / (ident + '.md')
            if not p.exists():
                return self._json({'gabim': 'no such unit', 'id': ident}, 404)
            return self._dergo(p.read_bytes(), 'text/markdown; charset=utf-8')
        if u.path == '/historia':
            log = _git('log', '--date=iso-strict', '--format=%h%x09%ad%x09%s', '-n', '50', '--', str(ARKIVA.relative_to(RRENJA)))
            commits = []
            for rr in log.splitlines():
                pj = rr.split('\t', 2)
                if len(pj) == 3:
                    commits.append({'sha': pj[0], 'data': pj[1], 'mesazhi': pj[2]})
            return self._json({'arkiva': ARKIVA.name, 'commits': commits})
        if u.path.startswith('/diff/'):
            sha = u.path[len('/diff/'):]
            if not RX_SHA.match(sha):
                return self._json({'gabim': 'bad sha'}, 400)
            out = _git('show', '--stat', '--patch', '--format=%h %ad %s%n', '--date=iso-strict', sha, '--', str(ARKIVA.relative_to(RRENJA)))
            return self._dergo(out[:20000].encode(), 'text/plain; charset=utf-8')
        self._dergo(_faqja().encode(), 'text/html; charset=utf-8')


def main() -> int:
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('0.0.0.0', PORT), H) as s:
        print('demo at http://127.0.0.1:%d  (%d units from %s, semantic=%s)' % (PORT, ARK.N, ARKIVA.name, ARK.vec is not None), flush=True)
        s.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
