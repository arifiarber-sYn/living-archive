#!/usr/bin/env python3
"""demo_reja.py — demo HTTP i motorit REJA: pyetje -> pergjigje me citim, ose refuzim."""
import http.server, json, pathlib, socketserver, sys, urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reja  # noqa: E402

PORT = int(__import__('os').environ.get('ARK_DEMO_PORT', '8078'))

FAQJA = '<!doctype html><meta charset=utf-8><title>Arkivi i Gjalle - demo</title>' + \
        '<body style="font-family:system-ui;max-width:44rem;margin:3rem auto">' + \
        '<h1>Arkivi i Gjalle</h1><p>pergjigja OSE citon, OSE refuzon</p>' + \
        '<input id=q size=60 value="Sa eshte buxheti total i miratuar per vitin 2027?">' + \
        '<button onclick=p()>Pyet</button><pre id=o></pre>' + \
        '<script>async function p(){const q=document.getElementById("q").value;' + \
        'const r=await fetch("/pyet?q="+encodeURIComponent(q));const d=await r.json();' + \
        'document.getElementById("o").textContent=d.pergjigja+"\\n\\ncitime: "+JSON.stringify(d.citime)' + \
        '+"\\nkohe: "+d.sekonda+"s  kosto: $"+d.kosto_usd;}</script>' + \
        '<p><a href=/kosto>kosto</a> | <a href=/health>health</a></p>'


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _d(self, b, ct='application/json'):
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        if u.path == '/health':
            return self._d(b'{"status":"pass"}')
        if u.path == '/kosto':
            return self._d(json.dumps(reja.kosto_totale(), ensure_ascii=False).encode())
        if u.path == '/pyet':
            q = urllib.parse.parse_qs(u.query).get('q', [''])[0]
            if not q.strip():
                return self._d(b'{"gabim":"mungon q"}')
            return self._d(json.dumps(reja.pergjigju(q), ensure_ascii=False).encode())
        self._d(FAQJA.encode(), 'text/html; charset=utf-8')


def main() -> int:
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), H) as s:
        print('demo reja ne http://127.0.0.1:%d' % PORT, flush=True)
        s.serve_forever()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
