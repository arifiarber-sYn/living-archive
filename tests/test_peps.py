"""Public example corpus (PEPs): ingest + citation ids. No network."""
import pathlib
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness.ndaj_korpusin import ndaj_pep, licenca_pep  # noqa: E402
from src.know import nxirr_citime  # noqa: E402

PEP_FIKTIV = """PEP: 8
Title: Style Guide for Python Code
Author: Guido van Rossum <guido@python.org>,
        Barry Warsaw <barry@python.org>
Status: Active
Type: Process
Created: 05-Jul-2001

Introduction
============

This document gives coding conventions.


Copyright
=========

This document has been placed in the public domain.
"""


class TestPeps(unittest.TestCase):
    def test_ndaj_pep_front_matter_me_burim_dhe_licence(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'pep-0008.rst'
            p.write_text(PEP_FIKTIV, encoding='utf-8')
            ident, trupi = ndaj_pep(p)
        self.assertEqual(ident, 'pep-0008')
        self.assertIn('burimi: https://peps.python.org/pep-0008/', trupi)
        self.assertIn('licenca: Public domain', trupi)
        self.assertIn('titulli: Style Guide for Python Code', trupi)
        self.assertIn('# PEP 8 — Style Guide for Python Code', trupi)
        self.assertNotIn('guido@python.org', trupi.split('---')[2].split('Introduction')[0])  # header emails not in the lead

    def test_skedare_jo_pep_injorohen(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'README.rst'
            p.write_text('x', encoding='utf-8')
            self.assertIsNone(ndaj_pep(p))

    def test_licenca_fallback_pep1(self):
        self.assertIn('PEP 1', licenca_pep('no copyright section here'))
        self.assertIn('CC0', licenca_pep('... CC0-1.0-Universal license ...'))

    def test_citimi_pep(self):
        self.assertEqual(nxirr_citime('See [pep-0008] and 【pep-0484】.'), ['pep-0008', 'pep-0484'])
        self.assertEqual(nxirr_citime('Answer is pep-0008.'), [])  # bare id is NOT a citation (strict by design)
        gj = [{'id': 'pep-0008'}, {'id': 'vendim-d-070'}]
        self.assertEqual(nxirr_citime('[utf-8] [pep-0008] [d-070] [pep-9999]', gj), ['d-070', 'pep-0008'])

    def test_korpusi_publik_nese_ekziston_ka_licence_per_njesi(self):
        d = pathlib.Path(__file__).resolve().parent.parent / 'arkiva-peps'
        if not d.exists():
            self.skipTest('arkiva-peps/ not built (make peps)')
        for p in list(d.glob('pep-*.md'))[:50]:
            s = p.read_text(encoding='utf-8')
            self.assertRegex(s, r'^licenca: ', msg=p.name) if False else self.assertIn('\nlicenca: ', s, p.name)
            self.assertIn('\nburimi: https://peps.python.org/', s, p.name)


if __name__ == '__main__':
    unittest.main()
