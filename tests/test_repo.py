"""Repository-level checks: no secrets, consistent numbers, required tools visible, demo routes work.

All tests are network-free.
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

RRENJA = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RRENJA))


def _skedaret_e_ndjekur() -> list[pathlib.Path]:
    try:
        out = subprocess.run(['git', 'ls-files'], cwd=RRENJA, capture_output=True, text=True, check=True).stdout
        return [RRENJA / l for l in out.splitlines() if l]
    except Exception:  # noqa: BLE001  (no git → scan the tree)
        return [p for p in RRENJA.rglob('*') if p.is_file() and '.git' not in p.parts]


class TestPaSekrete(unittest.TestCase):
    SHABLLONE = [r'sk-[A-Za-z0-9_-]{20,}', r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}',
                 r'NEBIUS_API_KEY\s*=\s*["\']?[A-Za-z0-9]{20,}', r'TAVILY_API_KEY\s*=\s*["\']?tvly-']

    def test_asnje_celes_ne_skedaret_e_ndjekur(self):
        gjetje = []
        for p in _skedaret_e_ndjekur():
            if p.suffix in {'.bin', '.png', '.mp4', '.jpg'} or p.name.endswith('.key'):
                gjetje.append(str(p)) if p.name.endswith('.key') else None
                continue
            try:
                t = p.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            for rx in self.SHABLLONE:
                if re.search(rx, t):
                    gjetje.append(f'{p.relative_to(RRENJA)}: {rx}')
        self.assertEqual(gjetje, [], 'possible secret in tracked files')

    def test_gitignore_mbulon_env_dhe_indeksin(self):
        gi = (RRENJA / '.gitignore').read_text(encoding='utf-8')
        for rresht in ('.env', 'arkiva/embeddings.bin'):
            self.assertIn(rresht, gi)


class TestReadmeDheMakefile(unittest.TestCase):
    def setUp(self):
        self.readme = (RRENJA / 'README.md').read_text(encoding='utf-8')
        self.makefile = (RRENJA / 'Makefile').read_text(encoding='utf-8')

    def test_veglat_e_kerkuara_jane_te_padiskutueshme(self):
        for emri in ('Nebius Token Factory', 'Nemotron', 'Apache-2.0'):
            self.assertIn(emri, self.readme, emri + ' must be named in README')
        self.assertTrue((RRENJA / 'LICENSE').exists())
        self.assertIn('Apache License', (RRENJA / 'LICENSE').read_text(encoding='utf-8')[:200])

    def test_readme_pa_vende_bosh(self):
        self.assertNotIn('FILL', self.readme)

    def test_numrat_e_readme_perputhen_me_raportin(self):
        r = json.loads((RRENJA / 'harness/report.json').read_text(encoding='utf-8'))
        pritet = f"{r['sakte']}/{r['pyetje']}"
        self.assertIn(pritet, self.readme, f'README must quote the current harness result {pritet}')
        self.assertIn(f"{r['refuzime_sakte']}/{r['refuzime_totale']}", self.readme)
        tr = (RRENJA / 'demo/transcript.md').read_text(encoding='utf-8')
        rp = RRENJA / 'harness/report-peps.json'
        r_tr = json.loads(rp.read_text(encoding='utf-8')) if (rp.exists() and 'public corpus' in tr[:200]) else r
        self.assertIn(f'"sakte": {r_tr["sakte"]},', tr, 'demo/transcript.md must be re-recorded after `make eval` (jury 13.10 flagged 9/13 vs 12/13)')
        self.assertIn(f'"pyetje": {r_tr["pyetje"]},', tr)
        r100p = RRENJA / 'harness/report-peps-100.json'
        if r100p.exists():
            r100 = json.loads(r100p.read_text(encoding='utf-8'))
            self.assertIn(f"**{r100['sakte']}/{r100['pyetje']} ({r100['sakte_pct']}%)**", self.readme, 'README must quote the 100-set result')
        trp = RRENJA / 'demo/transcript-peps.md'
        if trp.exists() and rp.exists():
            r2 = json.loads(rp.read_text(encoding='utf-8'))
            self.assertIn(f'"sakte": {r2["sakte"]},', trp.read_text(encoding='utf-8'), 'demo/transcript-peps.md must match report-peps.json')
        if rp.exists():
            r2 = json.loads(rp.read_text(encoding='utf-8'))
            self.assertIn(f"**{r2['sakte']}/{r2['pyetje']} ({r2['sakte_pct']}%)**", self.readme, 'README must quote the PEP-corpus result')

    def test_makefile_ka_targetet(self):
        for t in ('run:', 'test:', 'eval:', 'demo:', 'index:'):
            self.assertIn(t, self.makefile)


class TestTavilyFailClosed(unittest.TestCase):
    def test_pa_celes_kthen_liste_bosh_pa_rrjet(self):
        from src import tavily_ndihmes
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.dict(os.environ, {}, clear=False), \
                mock.patch('pathlib.Path.home', return_value=pathlib.Path(d)), \
                mock.patch('urllib.request.urlopen', side_effect=AssertionError('network must not be used')):
            os.environ.pop('TAVILY_API_KEY', None)
            self.assertEqual(tavily_ndihmes.kerko('anything'), [])


class TestWebKnowFailClosed(unittest.TestCase):
    """The web layer (Tavily → Nemotron) must refuse without permission and never touch the network while refusing."""

    def test_pa_leje_refuzon_pa_rrjet(self):
        from src import web_know
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('network must not be used')):
            d = web_know.pergjigju_web('anything', lejo=False)
        self.assertTrue(d['refuzim'])
        self.assertIn('porta', d)
        self.assertEqual((d['kosto_usd'], d['hyr'], d['burime'], d['citime']), (0.0, 0, [], []))

    def test_me_leje_por_pa_celes_thote_qe_s_ka_celes(self):
        from src import web_know
        with tempfile.TemporaryDirectory() as t, \
                mock.patch.dict(os.environ, {}, clear=False), \
                mock.patch('pathlib.Path.home', return_value=pathlib.Path(t)), \
                mock.patch('urllib.request.urlopen', side_effect=AssertionError('network must not be used')):
            os.environ.pop('TAVILY_API_KEY', None)
            d = web_know.pergjigju_web('anything', lejo=True)
        self.assertTrue(d['refuzim'])
        self.assertEqual(d.get('gabim'), 'pa_celes')

    def test_citimet_web_numerohen_vetem_per_burimet_e_marra(self):
        from src.web_know import nxirr_citime_web
        self.assertEqual(nxirr_citime_web('Deadline is 30 Oct [w2]. Also 【w1】 and [w9].', {'w1', 'w2', 'w3'}), ['w1', 'w2'])
        self.assertEqual(nxirr_citime_web("I don't know.", {'w1'}), [])

    def test_me_leje_dhe_burime_modeli_citon_url_ne(self):
        from src import web_know
        burime = [{'url': 'https://example.org/a', 'title': 'A', 'content': 'The deadline is 30 October.'},
                  {'url': 'https://example.org/b', 'title': 'B', 'content': 'Unrelated.'}]
        pergj = {'choices': [{'message': {'content': 'The deadline is 30 October [w1].'}}],
                 'usage': {'prompt_tokens': 100, 'completion_tokens': 10}}
        with mock.patch.object(web_know.tavily_ndihmes, '_celesi', return_value='k'), \
                mock.patch.object(web_know.tavily_ndihmes, 'kerko', return_value=burime), \
                mock.patch.object(web_know, '_thirr', return_value=pergj):
            d = web_know.pergjigju_web('when?', lejo=True)
        self.assertFalse(d['refuzim'])
        self.assertEqual([c['url'] for c in d['citime']], ['https://example.org/a'])
        self.assertGreater(d['kosto_usd'], 0)

    def test_me_arkive_citimet_e_perziera_njesi_dhe_web(self):
        """Memory first, web second: one answer may cite an archive unit [pep-0572] and a web page [w1] side by side."""
        from src import web_know

        class ArkFals:
            def kerko(self, q, k=3):
                return [{'id': 'pep-0572', 'skor': 0.9, 'teksti': 'PEP 572 — assignment expressions (walrus).'}]
        burime = [{'url': 'https://example.org/a', 'title': 'A', 'content': 'Python 3.8 shipped in October 2019.'}]
        pergj = {'choices': [{'message': {'content': 'Assignment expressions came with PEP 572 [pep-0572], shipped in 3.8 in 2019 [w1].'}}],
                 'usage': {'prompt_tokens': 120, 'completion_tokens': 20}}
        with mock.patch.object(web_know.tavily_ndihmes, '_celesi', return_value='k'), \
                mock.patch.object(web_know.tavily_ndihmes, 'kerko', return_value=burime), \
                mock.patch.object(web_know, '_thirr', return_value=pergj) as th:
            d = web_know.pergjigju_web('when did walrus land?', lejo=True, ark=ArkFals())
        self.assertEqual(d['njesi'], ['pep-0572'])
        self.assertEqual([c['id'] for c in d['citime']], ['w1', 'pep-0572'])
        self.assertEqual(d['citime'][1]['njesi'], 'pep-0572')
        self.assertIn('[pep-0572]', th.call_args[0][0][0]['content'], 'the system prompt must show an archive id as the citation example')
        self.assertIn('Archive entries:', th.call_args[0][0][1]['content'])


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import socketserver
        from src import server
        socketserver.TCPServer.allow_reuse_address = True
        cls.srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), server.H)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def _get(self, path: str):
        c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        c.request('GET', path)
        r = c.getresponse()
        return r.status, r.read().decode()

    def test_health(self):
        st, b = self._get('/health')
        self.assertEqual((st, json.loads(b)), (200, {'status': 'pass'}))

    def test_kosto_kthen_numrat_e_matur(self):
        st, b = self._get('/kosto')
        d = json.loads(b)
        self.assertEqual(st, 200)
        for k in ('pyetje', 'sakte', 'kosto_mesatare_usd', 'latence_p50_s'):
            self.assertIn(k, d)

    def test_pyet_pa_q_kthen_gabim_pa_thirrje(self):
        st, b = self._get('/pyet?q=')
        self.assertEqual(st, 400)
        self.assertIn('gabim', json.loads(b))

    def test_faqja_eshte_anglisht_dhe_emerton_modelin(self):
        st, b = self._get('/')
        self.assertEqual(st, 200)
        self.assertIn('lang=en', b)
        self.assertIn('nvidia/nemotron', b)
        self.assertIn('Memory history', b)
        for pjesa in ('Nebius Token Factory', 'Tavily', 'OpenClaw', 'allow this query to leave this machine'):
            self.assertIn(pjesa, b, 'the UI must show the stack and the privacy gate: ' + pjesa)
        self.assertNotIn('__', b.split('<script>')[0], 'no unfilled placeholder in the page')

    def test_web_pa_leje_refuzon_pa_rrjet_dhe_pa_q_gabim(self):
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('network must not be used')):
            st, b = self._get('/web?q=anything')
        d = json.loads(b)
        self.assertEqual(st, 200)
        self.assertTrue(d['refuzim'])
        self.assertIn('porta', d)
        self.assertEqual(self._get('/web?q=')[0], 400)

    def test_roja_e_buxhetit_rate_limit_dhe_tavani_ditor_refuzojne_pa_thirrje(self):
        """Public-demo guard: the N+1-th paid request per minute → 429 before any model call; daily cap → 429; /buxheti is public."""
        from src import server
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(server, 'RATE_PER_MIN', 2), mock.patch.object(server, 'DAILY_CAP_USD', 0.0), \
                mock.patch.object(server, 'BUXHETI', pathlib.Path(td) / 'b.json'), mock.patch.dict(server._GODITJET, {}, clear=True), \
                mock.patch.object(server, 'pergjigju', return_value={'pergjigje': 'x', 'citime': [], 'refuzim': False, 'kosto_usd': 0.5}) as pg:
            self.assertEqual(self._get('/pyet?q=a')[0], 200)
            self.assertEqual(self._get('/pyet?q=a')[0], 200)
            st, b = self._get('/pyet?q=a')
            self.assertEqual(st, 429)
            self.assertTrue(json.loads(b)['refuzim'])
            self.assertEqual(pg.call_count, 2, 'the rate-limited request must not reach the model')
            st, b = self._get('/buxheti')
            d = json.loads(b)
            self.assertEqual((st, d['thirrje'], d['kosto_usd'], d['rate_per_min']), (200, 2, 1.0, 2))
            # daily cap: spent $1.0 so far, cap $0.9 → refuse, model not called, counter of refusals grows
            with mock.patch.object(server, 'DAILY_CAP_USD', 0.9), mock.patch.dict(server._GODITJET, {}, clear=True):
                st, b = self._get('/pyet?q=a')
                self.assertEqual(st, 429)
                self.assertIn('daily budget', json.loads(b)['gabim'])
                self.assertEqual(pg.call_count, 2)
                self.assertEqual(json.loads(self._get('/buxheti')[1])['refuzuar_429'], 1)
            # the privacy-gate refusal on /web is free and never rate-limited
            with mock.patch.object(server, 'RATE_PER_MIN', 1), mock.patch.dict(server._GODITJET, {}, clear=True):
                for _ in range(3):
                    st, b = self._get('/web?q=anything')
                    self.assertEqual((st, json.loads(b)['refuzim']), (200, True))

    def test_njesi_lexon_njesine_e_cituar_dhe_refuzon_id_te_keq(self):
        from src import server
        p = sorted(server.ARKIVA.glob('*.md'))[0]
        st, b = self._get('/njesi/' + p.stem)
        self.assertEqual(st, 200)
        self.assertIn('id: ', b)
        self.assertEqual(self._get('/njesi/../README.md')[0], 400)
        self.assertEqual(self._get('/njesi/nuk-ekziston-999')[0], 404)

    def test_historia_dhe_diff_japin_gjurmen_e_git(self):
        st, b = self._get('/historia')
        d = json.loads(b)
        self.assertEqual(st, 200)
        self.assertTrue(d['commits'], 'memory directory must have git history')
        sha = d['commits'][0]['sha']
        st2, b2 = self._get('/diff/' + sha)
        self.assertEqual(st2, 200)
        self.assertIn(sha, b2)
        self.assertEqual(self._get('/diff/not-a-sha')[0], 400)


if __name__ == '__main__':
    unittest.main()
