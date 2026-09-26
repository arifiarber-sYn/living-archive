#!/usr/bin/env python3
"""UI i Arkivit - pyet, pergjigje me citime te klikueshme, raporti i kuptimit.
Server i thjeshte stdlib; pyetja xhiron ne fill, faqja rifreskohet vetë."""
import html, http.server, json, socketserver, threading, urllib.parse
import arkivi, agjenti, harness

GJENDJA = {'pyetja': '', 'rez': None, 'duke': False, 'gabim': ''}

def puno(q):
    GJENDJA['duke'] = True
    GJENDJA['rez'] = None
    GJENDJA['gabim'] = ''
    try:
        GJENDJA['rez'] = arkivi.pergjigju(q)
    except Exception as e:
        GJENDJA['gabim'] = type(e).__name__ + ': ' + str(e)[:150]
    GJENDJA['duke'] = False

def faqja():
    r = GJENDJA['rez']
    pjese = []
    if GJENDJA['duke']:
        pjese.append('<p class="m">Po mendon&hellip; (modeli lokal, 10-40 sekonda)</p>')
    if GJENDJA['gabim']:
        pjese.append('<p class="err">' + html.escape(GJENDJA['gabim']) + '</p>')
    if r:
        if str(r.get('pergjigja', '')).strip().upper().startswith('S E DI'):
            pjese.append('<div class="sdi"><b>S&rsquo;E DI</b><br><span class="m">Nuk ka baze ne korpus. (siguria: ' + str(r.get('siguria')) + ')</span></div>')
        else:
            cits = ''.join('<a class="cit" href="/frag/' + html.escape(c) + '">[' + html.escape(c) + ']</a> ' for c in (r.get('citime') or []))
            pjese.append('<div class="ans">' + html.escape(str(r.get('pergjigja'))).replace(chr(10), '<br>') + '</div>')
            pjese.append('<p class="m">Citime (kliko per te verifikuar): ' + (cits or 'PA CITIME') + ' &middot; siguria: ' + str(r.get('siguria')) + ' &middot; burimi: ' + html.escape(str(r.get('baza'))) + '</p>')
            pjese.append('<form method="post" action="/vlereso"><input type="hidden" name="q" value="' + html.escape(GJENDJA['pyetja']) + '">'
                         + '<button name="v" value="sakte">Sakte</button> <button name="v" value="gabim" style="background:#6b7280">Gabim</button> <span class="m">(feedback-u ruhet dhe ndikon pyetjet e ngjashme)</span></form>')
    inx = arkivi.lexo_inde()
    rap = inx.get('raport', [])
    rreshta = ''.join('<tr><td>' + html.escape(str(x['dok'])) + '</td><td>' + html.escape(str(x['file']))[:60] + '</td><td>' + str(x['shkronja']) + '</td><td>' + str(x['copa']) + '</td><td>' + ('po' if x['kuptova'] == 'po' else '<b>JO</b>') + '</td></tr>' for x in rap)
    gj = agjenti.GJ
    rreshtaL = ''
    for x in gj.get('rreshta', []):
        rreshtaL += ('<tr><td>' + html.escape(str(x['dok'])) + '</td><td>' + html.escape(str(x['file']))[:34]
                     + '</td><td>' + html.escape(str(x['vendimi']))[:80] + '</td><td>' + str(x['shkronja'])
                     + '</td><td>' + str(x['copa']) + '</td><td>' + ('po' if x['kuptova'] == 'po' else ('<b>JO</b>' if x['kuptova'] == 'JO' else '?'))
                     + '</td><td>' + str(x['sekonda']) + 's</td></tr>')
    stato = ('<p class="m">Laku po xhiron&hellip; (' + str(len(gj.get('rreshta', []))) + ' deri tani)</p>' if gj.get('aktiv')
             else ('<p class="m">Perfundoi: ' + json.dumps(gj.get('permbledhje') or {}, ensure_ascii=False) + '</p>' if gj.get('mbaroi') else ''))
    blloku = ('<h2 style="font-size:16px">Laku agjentik i gelltitjes (vezhgo &rarr; vendos &rarr; indekso &rarr; raporto)</h2>'
              + '<form method="post" action="/gelltit"><button>Gelltit korpusin</button></form>' + stato
              + '<table><tr><th>#</th><th>Skedari</th><th>Vendimi i agjentit</th><th>Shkronja</th><th>Copa</th><th>Kuptova</th><th>Koha</th></tr>' + rreshtaL + '</table>')
    return ('<!doctype html><meta charset="utf-8"><title>Arkivi i Gjalle</title>'
            + ('<meta http-equiv="refresh" content="4">' if GJENDJA['duke'] else '')
            + '<style>body{font-family:system-ui;background:#0f1115;color:#e5e7eb;padding:16px;max-width:900px;margin:0 auto}'
            + 'input[type=text]{width:70%;padding:10px;border-radius:8px;border:1px solid #333;background:#161a22;color:#eee}'
            + 'button{background:#2563eb;color:#fff;border:0;padding:10px 14px;border-radius:8px;cursor:pointer}'
            + 'table{border-collapse:collapse;width:100%;margin-top:10px}td,th{border-bottom:1px solid #262b36;padding:6px;font-size:13px;text-align:left}'
            + '.ans{background:#161a22;padding:12px;border-radius:8px;margin:10px 0}.sdi{background:#3b2a12;padding:12px;border-radius:8px;margin:10px 0}'
            + '.m{color:#9ca3af;font-size:13px}.cit{color:#60a5fa;text-decoration:none;margin-right:4px}.err{color:#f87171}</style>'
            + '<h1>Arkivi i Gjalle &mdash; demo</h1><p class="m">LLM lokal (' + arkivi.LLM + ') &middot; embedime ' + arkivi.EMB + ' &middot; pa API te jashtme</p>'
            + '<form method="post" action="/pyet"><input type="text" name="q" placeholder="Pyet mbi korpusin..." value="' + html.escape(GJENDJA['pyetja']) + '"> <button>Pyet</button></form>'
            + ''.join(pjese)
            + blloku
            + paneli_harness()
            + '<h2 style="font-size:16px">Cka kuptova nga korpusi</h2><table><tr><th>#</th><th>Skedari</th><th>Shkronja</th><th>Copa</th><th>Kuptova</th></tr>' + rreshta + '</table>')

def paneli_harness():
    p = arkivi.BASE / 'indeksi' / 'harness.json'
    b = ''
    if p.exists():
        try:
            dd = json.loads(p.read_text(encoding='utf-8'))
            m = dd['metrika']
            b = ('<p class="m">Bazesueshme: <b>' + str(m['sakte']) + '/' + str(m['bazesueshme']) + '</b> sakte (' + str(m['sakte_pct']) + '%) &middot; '
                 + '"S E DI" te gabuar: <b>' + str(m['sd_gabim']) + '</b> (' + str(m['sd_gabim_pct']) + '%) &middot; '
                 + 'pa baze: <b>' + str(m['pa_baze_sakte']) + '/' + str(m['pa_baze']) + '</b> sakte &middot; '
                 + 'trillime: <b>' + str(m['trillime']) + '</b> (' + str(m['trillim_pct']) + '%) &middot; kohë: ' + str(m['sekonda']) + 's</p>')
            b += ('<table><tr><th>Pyetja</th><th>Pritet</th><th>Pergjigja</th><th>Tipi</th><th>?</th></tr>'
                  + ''.join('<tr><td>' + html.escape(str(x['pyetja']))[:70] + '</td><td>' + html.escape(str(x['pritet']))[:26]
                            + '</td><td>' + html.escape(str(x['pergjigja']))[:70] + '</td><td>' + html.escape(str(x['tipi']))
                            + '</td><td>' + ('OK' if x.get('sakte') else 'X') + '</td></tr>' for x in dd.get('rreshta', [])) + '</table>')
        except Exception:
            b = '<p class="m">(harness-i nuk lexohet)</p>'
    elif GJENDJA.get('harness_duke'):
        b = '<p class="m">Harness-i po xhiron (i nderton vetë pyetjet, mandej i provon)&hellip;</p>'
    elif GJENDJA.get('harness_rez'):
        b = '<p class="m">' + html.escape(json.dumps(GJENDJA['harness_rez'], ensure_ascii=False)[:200]) + '</p>'
    else:
        b = '<p class="m">Nuk eshte xhiruar ende.</p>'
    return ('<h2 style="font-size:16px">Vetë-vlerësimi (harness i brendshem)</h2>'
            + '<form method="post" action="/harness"><button>Xhiro harness-in</button></form>' + b)


class H(http.server.BaseHTTPRequestHandler):
    def _d(self, b, ct):
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith('/frag/'):
            fid = urllib.parse.unquote(self.path.split('/frag/', 1)[1])
            inx = arkivi.lexo_inde()
            for c in inx['copa']:
                if c['id'] == fid:
                    self._d(('<html><meta charset="utf-8"><body style="font-family:system-ui;background:#0f1115;color:#eee;padding:16px">'
                             + '<h3>[' + html.escape(fid) + '] ' + html.escape(c['file']) + '</h3><pre style="white-space:pre-wrap">' + html.escape(c['tekst']) + '</pre>'
                             + '<p><a style="color:#60a5fa" href="/">kthehu</a></p></body></html>').encode('utf-8'), 'text/html; charset=utf-8')
                    return
            self._d(b'<html><body>fragmenti nuk u gjet</body></html>', 'text/html; charset=utf-8')
            return
        self._d(faqja().encode('utf-8'), 'text/html; charset=utf-8')

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        d = urllib.parse.parse_qs(self.rfile.read(n).decode('utf-8', errors='replace'))
        if self.path.startswith('/vlereso'):
            try:
                arkivi.ruaj_vleresim((d.get('q') or [''])[0], (d.get('v') or [''])[0], (GJENDJA.get('rez') or {}).get('citime') or [])
            except Exception:
                pass
        if self.path.startswith('/harness'):
            if not GJENDJA.get('harness_duke'):
                GJENDJA['harness_duke'] = True
                def _h():
                    try:
                        GJENDJA['harness_rez'] = harness.xhiro()
                    except Exception as e:
                        GJENDJA['harness_gabim'] = type(e).__name__ + ': ' + str(e)[:120]
                    GJENDJA['harness_duke'] = False
                threading.Thread(target=_h, daemon=True).start()
        if self.path.startswith('/gelltit'):
            if not agjenti.GJ.get('aktiv'):
                threading.Thread(target=agjenti.gelltit_lak, daemon=True).start()
        if self.path.startswith('/pyet'):
            q = (d.get('q') or [''])[0]
            GJENDJA['pyetja'] = q
            GJENDJA['rez'] = None
            if q.strip():
                threading.Thread(target=puno, args=(q,), daemon=True).start()
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

    def log_message(self, *a):
        pass

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', arkivi.PORT), H) as srv:
        print('Arkivi: http://127.0.0.1:' + str(arkivi.PORT))
        srv.serve_forever()
