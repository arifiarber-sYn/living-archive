"""Tests for the knowledge layer — network-free (no Token Factory call is made here).

Run: make test   (python3 -m unittest discover -s tests -v)
"""
from __future__ import annotations

import pathlib
import re
import sys
import unittest

RRENJA = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RRENJA))

from src import know  # noqa: E402


def _arkiva_offline() -> know.Arkiva:
    """Archive with the semantic index switched off → BM25 path, zero network."""
    ark = know.Arkiva()
    ark.vec = None
    return ark


class TestArkiva(unittest.TestCase):
    def test_arkiva_ngarkon_njesi_me_id_dhe_burim(self):
        ark = know.Arkiva()
        self.assertGreater(ark.N, 0, 'arkiva/ must contain at least one unit')
        for n in ark.njesi:
            self.assertRegex(n['id'], r'^[a-z]+(-[a-z0-9]+)+$', n['id'])  # vendim-d-070 · mesim-d2-01 (remember) · pep-0008 · shenim-nebius-video-1
            fm_id = n['teksti'][:160]
            # private units: file `vendim-d-070` ↔ `id: d-070`; public units: file `pep-0008` ↔ `id: pep-0008`
            self.assertTrue('id: ' + n['id'] in fm_id or 'id: ' + n['id'].split('-', 1)[1] in fm_id,
                            'front-matter id must match the file name: ' + n['id'])
            self.assertIn('burimi:', n['teksti'][:200], 'every unit declares its source (burimi)')

    def test_bm25_gjen_njesine_nga_fjalet_e_saj(self):
        ark = _arkiva_offline()
        njesia = ark.njesi[len(ark.njesi) // 2]
        # take rare words of that unit (df == 1) as the query
        fjalet = [w for w in set(njesia['tokat']) if ark.df[w] == 1][:6]
        self.assertTrue(fjalet, 'unit should have at least one distinctive word')
        hit = ark.kerko_bm25(' '.join(fjalet), 1)
        self.assertEqual(hit[0]['id'], njesia['id'])

    def test_embeddings_meta_perputhet_me_arkiven(self):
        if not know.EMB_META.exists():
            self.skipTest('no local index (built with `make index`)')
        ark = know.Arkiva()
        # units written after the index (`remember`) are BM25-only until `make index --force`; the index may lag, never lead
        self.assertLessEqual(len(ark.id_emb), ark.N, 'index must not contain more units than the archive')
        self.assertTrue(set(ark.id_emb) <= {n['id'] for n in ark.njesi}, 'every indexed id must exist in the archive')
        self.assertEqual(len(ark.vec), len(ark.id_emb) * ark.dim)


class TestRefuzimi(unittest.TestCase):
    def test_refuzon_para_modelit_kur_deshmia_mungon(self):
        ark = _arkiva_offline()
        r = know.pergjigju(ark, 'classic recipe for spinach byrek', pragu=1e9)
        self.assertTrue(r['refuzim'])
        self.assertEqual(r['citime'], [])
        self.assertEqual((r['hyr'], r['dal'], r['kosto_usd']), (0, 0, 0.0), 'refusal must cost nothing')
        self.assertIn("I don't know", r['pergjigja'])

    def test_refuzon_kur_asgje_nuk_gjendet(self):
        ark = _arkiva_offline()
        r = know.pergjigju(ark, 'zzzzqqqq xxxxyyyy')  # no token exists in the archive
        self.assertTrue(r['refuzim'])
        self.assertEqual(r['gjetjet'], [])


class TestCitimet(unittest.TestCase):
    RX = r'\[(?:vendim-|mesim-)?(d-\d+|l-\d+)\]'

    def test_regex_nxjerr_id_te_cituara(self):
        t = 'Decision [d-070] grants autonomy; see also [vendim-d-077] and [mesim-l-216]. Not [x-1].'
        self.assertEqual(sorted(set(re.findall(self.RX, t.lower()))), ['d-070', 'd-077', 'l-216'])

    def test_nxirr_citime_normalizon_kllapat_cjk(self):
        self.assertEqual(know.nxirr_citime('… is **D‑070**【d-070】 and ［l-16］.'), ['d-070', 'l-16'])

    def test_atribuo_leksikore_ruan_citimet_ekzistuese(self):
        self.assertEqual(know.atribuo_leksikore('anything', [], ['d-070']), ['d-070'])

    def test_atribuo_leksikore_nuk_atribuon_refuzimin(self):
        gjetjet = [{'id': 'vendim-d-001', 'teksti': 'autonomy notification unlimited decision agent'}]
        self.assertEqual(know.atribuo_leksikore("I don't know — nothing here.", gjetjet, []), [])

    def test_atribuo_leksikore_gjen_njesine_qe_mbulon_pergjigjen(self):
        gjetjet = [{'id': 'vendim-d-001', 'teksti': 'The agent receives unlimited autonomy and notifies afterwards.'},
                   {'id': 'vendim-d-002', 'teksti': 'Containers for syn and avokatim must never be rebuilt.'}]
        cit = know.atribuo_leksikore('The agent receives unlimited autonomy and notifies afterwards.', gjetjet, [])
        self.assertEqual(cit, ['vendim-d-001'])


class TestKosto(unittest.TestCase):
    def test_cmimi_perputhet_me_modelin_default(self):
        self.assertEqual((know.CMIM_HYR, know.CMIM_DAL), know.CMIMET[know.MODEL],
                         'cost must be priced with the price of the model actually called')

    def test_cmimi_super_sipas_katalogut(self):
        self.assertEqual(know.CMIMET['nvidia/nemotron-3-super-120b-a12b'], (0.30, 0.90))

    def test_modeli_default_eshte_nemotron_ne_token_factory(self):
        self.assertTrue(know.MODEL.startswith('nvidia/'), know.MODEL)
        self.assertIn('nemotron', know.MODEL.lower())
        self.assertEqual(know.BASE, 'https://api.tokenfactory.nebius.com/v1')


if __name__ == '__main__':
    unittest.main()


class TestIndeksiInkremental(unittest.TestCase):
    def test_shto_njesi_ne_indeks_pa_rindertim(self):
        import array, json, tempfile
        from unittest import mock
        from src import embeddings as E
        with tempfile.TemporaryDirectory() as d:
            ark = pathlib.Path(d)
            (ark / 'vendim-d-1.md').write_text('---\nid: d-1\n---\nalpha', encoding='utf-8')
            (ark / 'mesim-x-2.md').write_text('---\nid: x-2\n---\nbeta', encoding='utf-8')
            array.array('f', [1.0, 0.0]).tofile(open(ark / 'embeddings.bin', 'wb'))
            (ark / 'embeddings.json').write_text(json.dumps({'modeli': 'm', 'n': 1, 'dim': 2, 'token_a': 5, 'id': ['vendim-d-1']}), encoding='utf-8')
            with mock.patch.object(E, 'ARKIVA', ark), mock.patch.object(E, 'BIN', ark / 'embeddings.bin'), \
                 mock.patch.object(E, 'META', ark / 'embeddings.json'), mock.patch.object(E, 'celesi', lambda: 'k'), \
                 mock.patch.object(E, 'embedding', lambda tekste, k: ([[0.0, 1.0]], 3)):
                self.assertEqual(E.shto('mesim-x-2'), 0)
                self.assertEqual(E.shto('mesim-x-2'), 0)  # idempotent
                with self.assertRaises(SystemExit):
                    E.shto('nuk-ekziston-9')
            m = json.loads((ark / 'embeddings.json').read_text(encoding='utf-8'))
            self.assertEqual(m['id'], ['vendim-d-1', 'mesim-x-2'])
            self.assertEqual((m['n'], m['token_a']), (2, 8))
            a = array.array('f'); a.fromfile(open(ark / 'embeddings.bin', 'rb'), 4)
            self.assertEqual(list(a), [1.0, 0.0, 0.0, 1.0])


class TestRenditjaEIndeksit(unittest.TestCase):
    def test_teksti_semantik_sipas_id_jo_pozicionit(self):
        """Index order (append) ≠ archive order (sorted): the text returned must belong to the id."""
        import array
        from unittest import mock
        ark = know.Arkiva()
        ark.njesi = [{'id': 'a-1', 'teksti': 'TEKST-A', 'tokat': []}, {'id': 'b-2', 'teksti': 'TEKST-B', 'tokat': []},
                     {'id': 'c-3', 'teksti': 'TEKST-C', 'tokat': []}]
        ark.N = 3
        ark.dim = 2
        ark.id_emb = ['a-1', 'c-3', 'b-2']                      # b-2 appended last by --shto
        ark.vec = array.array('f', [1, 0, 0, 1, 1, 1])        # a=(1,0) c=(0,1) b=(1,1)
        with mock.patch.object(know, '_embedding', lambda t, k: ([[0.0, 1.0]], 0)), mock.patch.object(know, 'celesi', lambda: 'k'):
            hit = ark.kerko_semantike('q', 1)[0]
        self.assertEqual((hit['id'], hit['teksti']), ('c-3', 'TEKST-C'))
